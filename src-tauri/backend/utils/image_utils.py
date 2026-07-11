import datetime
import os
import sys
import codecs
from datetime import date
from typing import List, Tuple

import PIL
import cv2
# import easyocr
import numpy
import pyautogui
from PIL import Image as Image

# playsound3 為新版套件（支援 Python 3.10+），舊版 playsound 作為備援
try:
    from playsound3 import playsound
except ImportError:
    from playsound import playsound

from utils.settings import Settings
from utils.message_log import MessageLog

# Windows 高 DPI 感知：讓截圖與滑鼠座標對應實體像素，避免 125%/150% 縮放時座標錯位
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

class ImageUtils:
    """
    Provides the utility functions needed to perform image-related actions.
    """

    # Initialize the following for saving screenshots.
    _image_number: int = 0
    _new_folder_name: str = None

    # Used for skipping selecting the Summon Element every time on repeated runs.
    _summon_selection_first_run = True
    _summon_selection_same_element = False

    _match_method: int = cv2.TM_CCOEFF_NORMED
    _match_location: Tuple[int, int] = None

    # 模板縮放比例：模板圖是 1080p 遊戲視窗截的，2K/4K 螢幕上遊戲元件更大，
    # 校準時由 determine_template_scale() 自動測出，之後所有匹配都套用。
    _template_scale: float = 1.0
    # 截圖像素 / 邏輯座標比例：mac Retina 截圖是 2 倍大，滑鼠座標要除回來。
    _screenshot_ratio: float = 1.0

    # Check if the temp folder is created in the images folder.
    _current_dir: str = os.getcwd()
    _temp_dir: str = _current_dir + "/temp/"
    if not os.path.exists(_temp_dir):
        os.makedirs(_temp_dir)

    # 缺模板檔的警告每個檔案只印一次，避免戰鬥迴圈重複刷版面
    _missing_template_warned: set = set()

    @staticmethod
    def save_debug_screenshot(tag: str) -> None:
        """存目前遊戲視窗截圖到 logs/，供事後診斷模板匹配失敗的原因。"""
        try:
            logs_dir = os.path.abspath(os.path.join(ImageUtils._current_dir, "..", "logs"))
            os.makedirs(logs_dir, exist_ok = True)
            if Settings.window_left is not None:
                image = pyautogui.screenshot(region = (Settings.window_left, Settings.window_top, Settings.window_width, Settings.window_height))
            else:
                image = pyautogui.screenshot()
            path = os.path.join(logs_dir, f"debug_{tag}_{datetime.datetime.now().strftime('%H%M%S')}.png")
            image.save(path)
            MessageLog.print_message(f"[DEBUG] 已存除錯截圖：{path}")
        except Exception:
            pass

    @staticmethod
    def _read_template(folder: str, filename: str):
        """讀取模板圖；檔案不存在回傳 None（警告每檔僅一次，且不觸發 cv2 錯誤輸出）。"""
        path = ImageUtils._template_path(folder, filename)
        if not os.path.exists(path):
            if filename not in ImageUtils._missing_template_warned:
                ImageUtils._missing_template_warned.add(filename)
                MessageLog.print_message(f"[WARNING] 模板圖檔 {filename} 不存在，跳過搜尋（每個檔案只提示一次）。")
            return None
        return cv2.imread(path, 0)

    @staticmethod
    def _template_path(folder: str, filename: str) -> str:
        """依遊戲語言解析模板路徑。

        gameLanguage 不是 en 時優先找 images/<folder>_<lang>/（例如 buttons_jp/），
        沒有對應語言的模板就退回預設英文版模板。圖示類按鈕跨語言通用，
        只有含文字的按鈕/標頭需要提供在地化模板。
        """
        lang = getattr(Settings, "game_language", "en")
        if lang and lang != "en":
            localized = f"{ImageUtils._current_dir}/images/{folder}_{lang}/{filename}"
            if os.path.exists(localized):
                return localized
        return f"{ImageUtils._current_dir}/images/{folder}/{filename}"

    # _reader: easyocr.Reader = None

    @staticmethod
    def update_window_dimensions(window_left: int, window_top: int, window_width: int, window_height: int, additional_calibration_required: bool = False):
        """Updates the window dimensions for PyAutoGUI to perform faster operations in.

        Args:
            window_left (int): The x-coordinate of the left edge of the region for image matching.
            window_top (int): The y-coordinate of the top edge of the region for image matching.
            window_width (int): The width of the region for image matching.
            window_height (int): The height of the region for image matching.
            additional_calibration_required (bool, optional): Flag that allows for compensation of x-coordinates of all matches to fit the right hand side of the computer screen.

        Returns:
            None
        """
        Settings.window_left = window_left
        Settings.window_top = window_top
        Settings.window_width = window_width
        Settings.window_height = window_height
        Settings.calibration_complete = True
        Settings.additional_calibration_required = additional_calibration_required
        return None

    @staticmethod
    def get_window_dimensions():
        """Get the window dimensions as a Tuple of 4 integers.

        Returns:
            (Tuple[int, int, int, int]): A Tuple of 4 integers consisting of (window_left, window_top, window_width, window_height).
        """
        return Settings.window_left, Settings.window_top, Settings.window_width, Settings.window_height

    @staticmethod
    def _grab_screen() -> numpy.ndarray:
        """截取遊戲視窗區域，回傳灰階影像，並更新截圖像素/邏輯座標比例。

        注意：不可命名為 _take_screenshot，該名稱已被戰利品截圖功能使用。

        Returns:
            (numpy.ndarray): 灰階截圖。
        """
        if Settings.window_left is not None and Settings.window_top is not None and Settings.window_width is not None and Settings.window_height is not None:
            region_width = Settings.window_width
            image: PIL.Image.Image = pyautogui.screenshot(region = (Settings.window_left, Settings.window_top, Settings.window_width, Settings.window_height))
        else:
            region_width = pyautogui.size()[0]
            image: PIL.Image.Image = pyautogui.screenshot()

        # mac Retina 螢幕的截圖尺寸是邏輯解析度的 2 倍，記下比例供座標換算
        ImageUtils._screenshot_ratio = image.width / region_width if region_width else 1.0

        image.save(f"temp/source.png")
        return cv2.imread(f"temp/source.png", 0)

    @staticmethod
    def _scaled_template(template: numpy.ndarray) -> numpy.ndarray:
        """依偵測到的縮放比例調整模板尺寸。"""
        scale = ImageUtils._template_scale * ImageUtils._screenshot_ratio
        if abs(scale - 1.0) < 0.01:
            return template
        h, w = template.shape
        return cv2.resize(template, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC)

    @staticmethod
    def _to_logical(value: float) -> int:
        """把截圖像素座標換算回滑鼠可用的邏輯座標。"""
        return int(value / ImageUtils._screenshot_ratio)

    @staticmethod
    def determine_template_scale() -> float:
        """自動偵測螢幕縮放比例：用「home」按鈕模板在 0.5～3.0 倍間掃描，
        找出匹配度最高的縮放值。供 2K/4K 或非 100% DPI 縮放的螢幕使用。

        Returns:
            (float): 偵測到的最佳縮放比例。
        """
        template: numpy.ndarray = cv2.imread(ImageUtils._template_path("buttons", "home.jpg"), 0)
        if template is None:
            MessageLog.print_message("[WARNING] 找不到 home 按鈕模板圖，略過縮放偵測。")
            return ImageUtils._template_scale

        src = ImageUtils._grab_screen()
        h, w = template.shape

        best_scale = 1.0
        best_val = -1.0
        # 粗掃 + 細掃兩階段，避免逐一掃描太慢
        for scale in [round(0.5 + 0.1 * i, 2) for i in range(26)]:  # 0.5 ~ 3.0，步進 0.1
            new_w, new_h = int(w * scale), int(h * scale)
            if new_w < 5 or new_h < 5 or new_w >= src.shape[1] or new_h >= src.shape[0]:
                continue
            resized = cv2.resize(template, (new_w, new_h), interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC)
            result = cv2.matchTemplate(src, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > best_val:
                best_val = max_val
                best_scale = scale

        # 在最佳值附近細掃一輪（±0.08，步進 0.02）
        for offset in [-0.08, -0.06, -0.04, -0.02, 0.02, 0.04, 0.06, 0.08]:
            scale = round(best_scale + offset, 2)
            new_w, new_h = int(w * scale), int(h * scale)
            if scale <= 0 or new_w < 5 or new_h < 5 or new_w >= src.shape[1] or new_h >= src.shape[0]:
                continue
            resized = cv2.resize(template, (new_w, new_h), interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC)
            result = cv2.matchTemplate(src, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > best_val:
                best_val = max_val
                best_scale = scale

        if best_val >= 0.7:
            # _scaled_template 會另外乘上 _screenshot_ratio，這裡先除掉避免重複計算
            ImageUtils._template_scale = best_scale / ImageUtils._screenshot_ratio if ImageUtils._screenshot_ratio else best_scale
            MessageLog.print_message(f"[INFO] 偵測到螢幕縮放比例：{best_scale}（匹配度 {best_val:.3f}），模板將自動縮放。")
        else:
            MessageLog.print_message(f"[WARNING] 縮放偵測沒有找到可靠的匹配（最高 {best_val:.3f}），維持原始比例。請確認遊戲畫面已開啟且首頁可見。")

        return ImageUtils._template_scale

    @staticmethod
    def _match(template: numpy.ndarray, confidence: float = 0.8) -> bool:
        """Updates the window dimensions for PyAutoGUI to perform faster operations in.

        Args:
            template (numpy.ndarray): The template image array to match against in a source image.
            confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.

        Returns:
            (bool): True if the template was found inside the source image and False otherwise.
        """
        match_check = False
        src: numpy.ndarray = ImageUtils._grab_screen()
        template = ImageUtils._scaled_template(template)
        height, width = template.shape

        result: numpy.ndarray = cv2.matchTemplate(src, template, ImageUtils._match_method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if (ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED) and min_val <= 1.0 - confidence:
            ImageUtils._match_location = min_loc
            match_check = True
        elif ImageUtils._match_method != cv2.TM_SQDIFF and ImageUtils._match_method != cv2.TM_SQDIFF_NORMED and max_val >= confidence:
            ImageUtils._match_location = max_loc
            match_check = True
        elif Settings.debug_mode:
            if ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED:
                MessageLog.print_message(f"[WARNING] Match not found with {min_val} not <= {1.0 - confidence} at Point {min_loc}.")
            else:
                MessageLog.print_message(f"[WARNING] Match not found with {max_val} not >= {confidence} at Point {max_loc}.")

        if match_check:
            region = (ImageUtils._match_location[0] + width, ImageUtils._match_location[1] + height)
            cv2.rectangle(src, ImageUtils._match_location, region, 255, 5)
            cv2.imwrite(f"temp/match.png", src)

            # 換算回邏輯座標（Retina 截圖是 2 倍像素，滑鼠座標要除回來）
            temp_location = [
                ImageUtils._to_logical(ImageUtils._match_location[0] + width / 2),
                ImageUtils._to_logical(ImageUtils._match_location[1] + height / 2),
            ]

            if Settings.additional_calibration_required:
                temp_location[0] += Settings.window_left
                temp_location[1] += Settings.window_top

            ImageUtils._match_location = tuple(temp_location)

            if ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED:
                if Settings.debug_mode:
                    MessageLog.print_message(f"[DEBUG] Match found with {min_val} <= {confidence} at Point {ImageUtils._match_location}")
            else:
                if Settings.debug_mode:
                    MessageLog.print_message(f"[DEBUG] Match found with {max_val} >= {confidence} at Point {ImageUtils._match_location}")

        return match_check

    @staticmethod
    def _match_all(template: numpy.ndarray, confidence: float = 0.8) -> List[Tuple[int, ...]]:
        """Updates the window dimensions for PyAutoGUI to perform faster operations in.

        Args:
            template (numpy.ndarray): The template image array to match against in a source image.
            confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.

        Returns:
            (List[Tuple[int, ...]]): List of Tuples containing match locations.
        """
        src: numpy.ndarray = ImageUtils._grab_screen()
        template = ImageUtils._scaled_template(template)
        height, width = template.shape

        match_check = True
        match_locations = []

        while match_check:
            result: numpy.ndarray = cv2.matchTemplate(src, template, ImageUtils._match_method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if (ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED) and min_val <= 1.0 - confidence:
                ImageUtils._match_location = min_loc
                match_check = True
            elif ImageUtils._match_method != cv2.TM_SQDIFF and ImageUtils._match_method != cv2.TM_SQDIFF_NORMED and max_val >= confidence:
                ImageUtils._match_location = max_loc
                match_check = True
            else:
                if Settings.debug_mode:
                    if ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED:
                        MessageLog.print_message(f"[WARNING] Match not found with {min_val} not <= {1.0 - confidence} at Point {min_loc}.")
                    else:
                        MessageLog.print_message(f"[WARNING] Match not found with {max_val} not >= {confidence} at Point {max_loc}.")

                match_check = False

            if match_check:
                region = (ImageUtils._match_location[0] + width, ImageUtils._match_location[1] + height)
                cv2.rectangle(src, ImageUtils._match_location, region, 255, 5)

                if Settings.debug_mode:
                    cv2.imwrite(f"temp/matchAll.png", src)

                # 換算回邏輯座標（Retina 截圖是 2 倍像素，滑鼠座標要除回來）
                temp_location = [
                    ImageUtils._to_logical(ImageUtils._match_location[0] + width / 2),
                    ImageUtils._to_logical(ImageUtils._match_location[1] + height / 2),
                ]

                if Settings.additional_calibration_required:
                    temp_location[0] += Settings.window_left
                    temp_location[1] += Settings.window_top

                ImageUtils._match_location = tuple(temp_location)
                match_locations.append(ImageUtils._match_location)

                if ImageUtils._match_method == cv2.TM_SQDIFF or ImageUtils._match_method == cv2.TM_SQDIFF_NORMED:
                    if Settings.debug_mode:
                        MessageLog.print_message(f"[DEBUG] Match found with {min_val} <= {confidence} at Point {ImageUtils._match_location}")
                else:
                    if Settings.debug_mode:
                        MessageLog.print_message(f"[DEBUG] Match found with {max_val} >= {confidence} at Point {ImageUtils._match_location}")

        return match_locations

    @staticmethod
    def _determine_adjustment(image_name: str) -> int:
        """Verify whether the template name is able to be adjusted and return its adjustment.

        Args:
            image_name (str): The specific adjustment to the specified template or 0 to use the default number of tries.

        Returns:
            (int): The adjustment specific to the template name.
        """
        calibration_list = ["home"]
        pending_battles_list = ["check_your_pending_battles", "pending_battles", "quest_results_pending_battles"]
        captcha_list = ["captcha"]
        support_summon_selection_list = ["select_a_summon", "coop_without_support_summon", "proving_grounds_summon_selection"]
        dialog_list = ["dialog_lyria", "dialog_vyrn"]
        skill_usage_list = ["use_skill", "skill_unusable"]
        summon_usage_list = ["summon_details", "quick_summon1", "quick_summon2", "quick_summon_not_ready"]
        arcarum_list = ["arcarum_party_selection", "arcarum_treasure", "arcarum_node", "arcarum_mob", "arcarum_red_mob", "arcarum_silver_chest", "arcarum_gold_chest", "arcarum_boss", "arcarum_boss2"]
        arcarum_stage_effect_list = ["arcarum_stage_effect_active"]
        no_loot_screen_list = ["no_loot"]
        battle_concluded_popup_list = ["battle_concluded"]
        exp_gained_popup_list = ["exp_gained"]
        loot_collection_screen_list = ["loot_collected"]

        if Settings.enable_calibration_adjustment and calibration_list.__contains__(image_name):
            return Settings.adjust_calibration
        elif Settings.enable_pending_battles_adjustment and pending_battles_list.__contains__(image_name):
            return Settings.adjust_pending_battle
        elif Settings.enable_captcha_adjustment and captcha_list.__contains__(image_name):
            return Settings.adjust_captcha
        elif Settings.enable_support_summon_selection_screen_adjustment and support_summon_selection_list.__contains__(image_name):
            return Settings.adjust_support_summon_selection_screen
        elif Settings.enable_combat_mode_adjustment and dialog_list.__contains__(image_name):
            return Settings.adjust_dialog
        elif Settings.enable_combat_mode_adjustment and skill_usage_list.__contains__(image_name):
            return Settings.adjust_skill_usage
        elif Settings.enable_combat_mode_adjustment and summon_usage_list.__contains__(image_name):
            return Settings.adjust_summon_usage
        elif Settings.enable_combat_mode_adjustment and no_loot_screen_list.__contains__(image_name):
            return Settings.adjust_check_for_no_loot_screen
        elif Settings.enable_combat_mode_adjustment and battle_concluded_popup_list.__contains__(image_name):
            return Settings.adjust_check_for_battle_concluded_popup
        elif Settings.enable_combat_mode_adjustment and exp_gained_popup_list.__contains__(image_name):
            return Settings.adjust_check_for_exp_gained_popup
        elif Settings.enable_combat_mode_adjustment and loot_collection_screen_list.__contains__(image_name):
            return Settings.adjust_check_for_loot_collection_screen
        elif Settings.enable_arcarum_adjustment and arcarum_list.__contains__(image_name):
            return Settings.adjust_arcarum_action
        elif Settings.enable_arcarum_adjustment and arcarum_stage_effect_list.__contains__(image_name):
            return Settings.adjust_arcarum_stage_effect
        else:
            return 0

    @staticmethod
    def find_button(image_name: str, custom_confidence: float = 0.83, tries: int = 5, suppress_error: bool = False, disable_adjustment: bool = False, bypass_general_adjustment: bool = False):
        """Find the location of the specified button.

        Args:
            image_name (str): Name of the button image file in the /images/buttons/ folder.
            custom_confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.
            tries (int, optional): Number of tries before failing. Note that this gets overridden if the image_name is one of the adjustments. Defaults to 5.
            suppress_error (bool, optional): Suppresses template matching error if True. Defaults to False.
            disable_adjustment (bool, optional): Disable the usage of adjustment to tries. Defaults to False.
            bypass_general_adjustment (bool, optional): Bypass using the general adjustment for the number of tries. Defaults to False.

        Returns:
            (Tuple[int, int]): Tuple of coordinates of where the center of the button is located if image matching was successful. Otherwise, return None.
        """
        if image_name == "extreme_p":
            custom_confidence = 0.95

        if Settings.debug_mode:
            MessageLog.print_message(f"\n[DEBUG] Starting process to find the {image_name.upper()} button image...")

        template: numpy.ndarray = ImageUtils._read_template("buttons", f"{image_name.lower()}.jpg")
        if template is None:
            return None

        new_tries = ImageUtils._determine_adjustment(image_name)
        if new_tries == 0 and disable_adjustment is False:
            if Settings.enable_general_adjustment and bypass_general_adjustment is False and tries == 5:
                new_tries = Settings.adjust_button_search_general
            else:
                new_tries = tries
        else:
            new_tries = tries

        while new_tries > 0:
            result_flag: bool = ImageUtils._match(template, custom_confidence)

            if result_flag is False:
                new_tries -= 1
                if new_tries <= 0:
                    if not suppress_error:
                        MessageLog.print_message(f"[WARNING] Failed to find the {image_name.upper()} button.")
                    return None
            else:
                return ImageUtils._match_location

        return None

    @staticmethod
    def confirm_location(image_name: str, custom_confidence: float = 0.8, tries: int = 5, suppress_error: bool = False, disable_adjustment: bool = False, bypass_general_adjustment: bool = False):
        """Confirm the position of the bot by searching for the header image.

        Args:
            image_name (str): Name of the header image file in the /images/headers/ folder.
            custom_confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.
            tries (int, optional): Number of tries before failing. Note that this gets overridden if the image_name is one of the adjustments. Defaults to 5.
            suppress_error (bool, optional): Suppresses template matching error if True. Defaults to False.
            disable_adjustment (bool, optional): Disable the usage of adjustment to tries. Defaults to False.
            bypass_general_adjustment (bool, optional): Bypass using the general adjustment for the number of tries. Defaults to False.

        Returns:
            (bool): True if current location is confirmed. Otherwise, False.
        """
        if Settings.debug_mode:
            MessageLog.print_message(f"\n[DEBUG] Starting process to find the {image_name.upper()} button image...")

        # if image_name == "select_a_summon":
        #     MessageLog.print_message("Find resume image")
            # 可能在resume game界面，需要重新进战斗

        template: numpy.ndarray = ImageUtils._read_template("headers", f"{image_name.lower()}_header.jpg")
        if template is None:
            return False

        new_tries = ImageUtils._determine_adjustment(image_name)
        if new_tries == 0 and disable_adjustment is False:
            if Settings.enable_general_adjustment and bypass_general_adjustment is False and tries == 5:
                new_tries = Settings.adjust_header_search_general
            else:
                new_tries = tries
        else:
            new_tries = tries

        if (image_name == "coop_without_support_summon" or image_name == "select_a_summon" or image_name == "proving_grounds_summon_selection") and \
                Settings.enable_support_summon_selection_screen_adjustment:
            new_tries = Settings.adjust_support_summon_selection_screen

        while new_tries > 0:
            result_flag: bool = ImageUtils._match(template, custom_confidence)

            if result_flag is False:
                new_tries -= 1
                if new_tries <= 0:
                    if not suppress_error:
                        MessageLog.print_message(f"[WARNING] Failed to confirm the bot's location at {image_name.upper()}.")
                    return False
            else:
                return True

        return False

    @staticmethod
    def find_summon(summon_list: List[str], summon_element_list: List[str], custom_confidence: float = 0.8, suppress_error: bool = False):
        """Find the location of the specified Summon. Will attempt to scroll the screen down to see more Summons if the initial screen position yielded no matches.

        Args:
            summon_list (List[str]): List of names of the Summon image's file name in /images/summons/ folder.
            summon_element_list (List[str]): List of names of the Summon element image file in the /images/buttons/ folder.
            custom_confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.
            suppress_error (bool, optional): Suppresses template matching error if True. Defaults to False.

        Returns:
            (Tuple[int, int]): Tuple of coordinates of where the center of the Summon is located if image matching was successful. Otherwise, return None.
        """
        from bot.game import Game

        if Settings.debug_mode:
            MessageLog.print_message(f"[DEBUG] Received the following list of Summons to search for: {str(summon_list)}")
            MessageLog.print_message(f"[DEBUG] Received the following list of Elements: {str(summon_element_list)}")

        last_summon_element = ""
        summon_element_index = 0

        # Find the home button.
        home_button = ImageUtils.find_button("home", bypass_general_adjustment = True)
        if home_button is None:
            raise Exception("Unable to start Summon Selection process by not finding the Home button.")

        # Make sure that the bot is at the Summon Selection screen.
        tries = 10
        while not ImageUtils.confirm_location("select_a_summon"):
            Game.find_and_click_button('reload')
            tries -= 1
            if tries <= 0 and ImageUtils.confirm_location("select_a_summon", tries = 1) is False:
                raise Exception("Could not reach the Summon Selection screen.")

        # Determine if all the summon elements are the same or not. This will influence whether the bot needs to change elements in repeated runs.
        ImageUtils._summon_selection_same_element = all(element == summon_element_list[0] for element in summon_element_list)

        # Make the first summon element category active for first run.
        if ImageUtils._summon_selection_first_run:
            current_summon_element: str = summon_element_list[summon_element_index]
            Game.find_and_click_button(f"summon_{current_summon_element}")
            last_summon_element = current_summon_element
            ImageUtils._summon_selection_first_run = False

        tries = 30
        while True:
            # Reset the summon index.
            summon_index = 0
            while summon_index < len(summon_list):
                # Switch over to a different element for this summon index if it is different.
                if ImageUtils._summon_selection_same_element is False:
                    current_summon_element: str = summon_element_list[summon_element_index]
                    if current_summon_element != last_summon_element:
                        if Game.find_and_click_button(f"summon_{current_summon_element}") is False:
                            raise Exception(f"Unable to switch summon element categories from {last_summon_element.upper()} to {current_summon_element.upper()}.")
                        last_summon_element = current_summon_element

                # Now try and find the Summon at the current index.
                template: numpy.ndarray = cv2.imread(f"{ImageUtils._current_dir}/images/summons/{summon_list[summon_index]}.jpg", 0)

                # Crop the summon template image so that plus marks would not potentially obscure any match.
                height, width = template.shape
                template = template[0:height, 0:width - 40]

                result_flag: bool = ImageUtils._match(template, custom_confidence)

                if result_flag:
                    if Settings.debug_mode:
                        MessageLog.print_message(f"[SUCCESS] Found {summon_list[summon_index].upper()} Summon at {ImageUtils._match_location}.")

                    return ImageUtils._match_location
                else:
                    if suppress_error is False:
                        MessageLog.print_message(f"[WARNING] Could not locate {summon_list[summon_index].upper()} Summon.")

                    if ImageUtils._summon_selection_same_element:
                        summon_index += 1
                    else:
                        # Keep searching for the same summon until the bot reaches the bottom of the page. Then reset the page and move to the next summon's element.
                        if ImageUtils.find_button("bottom_of_summon_selection", tries = 1) is not None:
                            summon_index += 1
                            summon_element_index += 1

                            # If the bot cycled through the list of summon elements without finding a match, reset Summons.
                            if ImageUtils._summon_selection_same_element is False and summon_element_index >= len(summon_element_list):
                                MessageLog.print_message(f"[WARNING] Bot has gone through the entire summon list without finding a match. Resetting Summons now...")
                                return None

                            MessageLog.print_message(f"[INFO] Bot has reached the bottom of the page. Moving on to the next summon's element...")
                            if Game.find_and_click_button("reload") is False:
                                from utils.mouse_utils import MouseUtils
                                MouseUtils.scroll_screen(home_button[0], home_button[1] - 50, 10000)

                            Game.wait(1.0)
                        else:
                            # If matching failed and the bottom of the page has not been reached, scroll the screen down to see more Summons and try again.
                            from utils.mouse_utils import MouseUtils
                            MouseUtils.scroll_screen(home_button[0], home_button[1] - 50, -700)

                    tries -= 1

            # Perform check here to prevent infinite loop for rare cases.
            if tries <= 0:
                MessageLog.print_message(f"[WARNING] Summon Selection process was not able to find any valid summons. Resetting Summons now...")
                return None

            # If the bot reached the bottom of the page, reset Summons.
            if ImageUtils.find_button("bottom_of_summon_selection", tries = 1) is not None:
                MessageLog.print_message(f"[WARNING] Bot has reached the bottom of the page and found no suitable Summons. Resetting Summons now...")
                return None

            # If matching failed and the bottom of the page has not been reached, scroll the screen down to see more Summons and try again.
            from utils.mouse_utils import MouseUtils
            MouseUtils.scroll_screen(home_button[0], home_button[1] - 50, -700)
            Game.wait(1.0)

    @staticmethod
    def find_all(image_name: str, is_item: bool = False, custom_confidence: float = 0.8, hide_info: bool = False) -> List[Tuple[int, ...]]:
        """Find the specified image file by locating all occurrences on the screen.

        Args:
            image_name (str): Name of the image file in the /images/buttons folder.
            is_item (bool, optional): Determines whether to search for the image file in the /images/buttons/ or /images/items/ folder. Defaults to False.
            custom_confidence (float, optional): Accuracy threshold for matching. Defaults to 0.8.
            hide_info (bool, optional): Whether or not to print the matches' locations. Defaults to False.

        Returns:
            (List[Tuple[int, ...]): List of occurrences found on the screen. If no occurrence was found, return a empty list.
        """
        if is_item:
            folder_name = "items"
        else:
            folder_name = "buttons"

        template: numpy.ndarray = ImageUtils._read_template(folder_name, f"{image_name}.jpg")
        if template is None:
            return []

        locations = ImageUtils._match_all(template, custom_confidence)
        filtered_locations: List[Tuple[int, ...]] = []
        same_y: int = 0
        sort_flag: bool = False

        if len(locations) != 0:
            for (index, location) in enumerate(locations):
                if index > 0:
                    # Filter out duplicate locations where they are 1 pixel away from each other.
                    if location[0] != (locations[index - 1][0] + 1) and location[1] != (locations[index - 1][1] + 1):
                        filtered_locations.append(location)
                        if same_y != location[1]:
                            same_y = location[1]
                            sort_flag = False
                        else:
                            sort_flag = True
                else:
                    filtered_locations.append(location)
                    same_y = location[1]
                    sort_flag = False

            # Sort the matched locations.
            def first(point):
                return point[0]

            def second(point):
                return point[1]

            if sort_flag:
                if Settings.debug_mode:
                    MessageLog.print_message(f"[DEBUG] Sorting array using first key")
                filtered_locations.sort(key = first)
            else:
                if Settings.debug_mode:
                    MessageLog.print_message(f"[DEBUG] Sorting array using second key")
                filtered_locations.sort(key = second)

            if not hide_info:
                MessageLog.print_message(f"[INFO] Occurrence for {image_name.upper()} found at: {filtered_locations}")
        else:
            if Settings.debug_mode:
                MessageLog.print_message(f"[DEBUG] Failed to detect any occurrences of {image_name.upper()} images.")

        return filtered_locations

    @staticmethod
    def find_farmed_items(item_name: str, take_screenshot: bool = True) -> int:
        """Detect amounts of items gained according to the desired items specified.

        Args:
            item_name (str): Item to be found.
            take_screenshot (bool, optional): Takes a screenshot whenever matches were detected. Defaults to True.

        Returns:
            (int): Amount gained for the item.
        """
        try:
            if not os.path.exists(ImageUtils._current_dir + "/backend/model/"):
                os.makedirs(ImageUtils._current_dir + "/backend/model/")

            MessageLog.print_message(f"\n[INFO] Initializing EasyOCR reader. This may take a few seconds...")
            # ImageUtils._reader = easyocr.Reader(["en"], model_storage_directory = ImageUtils._current_dir + "/backend/model/", gpu = True)
            MessageLog.print_message(f"[INFO] EasyOCR reader initialized.")
        except UnicodeEncodeError:
            # Tauri spawns the Python process using encoding cp1252 and not utf-8. Need to do this hacky way to force stdout to be utf-8 to get through
            # EasyOCR initialization as it uses Unicode characters. This process is not needed after EasyOCR downloads the models to the /model/ folder.
            MessageLog.print_message(f"\n[INFO] Seems that the models for EasyOCR has not been downloaded yet. Downloading them now after setting stdout encoding from cp1252 to utf-8...\n\n")
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            # ImageUtils._reader = easyocr.Reader(["en"], model_storage_directory = ImageUtils._current_dir + "/backend/model/", gpu = True)
            MessageLog.print_message(f"\n[INFO] Models for EasyOCR has been downloaded successfully.\n\n")

        # List of items blacklisted from using the standard confidence and instead need a custom confidence to detect them.
        blacklisted_items = ["Fire Orb", "Water Orb", "Earth Orb", "Wind Orb", "Light Orb", "Dark Orb",
                             "Red Tome", "Blue Tome", "Brown Tome", "Green Tome", "White Tome", "Black Tome",
                             "Hellfire Scroll", "Flood Scroll", "Thunder Scroll", "Gale Scroll", "Skylight Scroll", "Chasm Scroll",
                             "Jasper Scale", "Crystal Spirit", "Luminous Judgment", "Sagittarius Rune", "Sunlight Quartz", "Shadow Silver",
                             "Ifrit Anima", "Cocytus Anima", "Vohu Manah Anima", "Sagittarius Anima", "Corow Anima", "Diablo Anima",
                             "Ifrit Omega Anima", "Cocytus Omega Anima", "Vohu Manah Omega Anima", "Sagittarius Omega Anima", "Corow Omega Anima", "Diablo Omega Anima",
                             "Ancient Ecke Sachs", "Ancient Auberon", "Ancient Perseus", "Ancient Nalakuvara", "Ancient Bow of Artemis", "Ancient Cortana",
                             "Ecke Sachs", "Auberon", "Perseus", "Nalakuvara", "Bow of Artemis", "Cortana"]

        lite_blacklisted_items = ["Infernal Garnet", "Frozen Hell Prism", "Evil Judge Crystal", "Horseman's Plate", "Halo Light Quartz", "Phantom Demon Jewel",
                                  "Tiamat Anima", "Colossus Anima", "Leviathan Anima", "Yggdrasil Anima", "Luminiera Anima", "Celeste Anima",
                                  "Tiamat Omega Anima", "Colossus Omega Anima", "Leviathan Omega Anima", "Yggdrasil Omega Anima", "Luminiera Omega Anima", "Celeste Omega Anima",
                                  "Shiva Anima", "Europa Anima", "Alexiel Anima", "Grimnir Anima", "Metatron Anima", "Avatar Anima",
                                  "Shiva Omega Anima", "Europa Omega Anima", "Alexiel Omega Anima", "Grimnir Omega Anima", "Metatron Omega Anima", "Avatar Omega Anima",
                                  "Twin Elements Anima", "Macula Marius Anima", "Medusa Anima", "Nezha Anima", "Apollo Anima", "Dark Angel Olivia Anima",
                                  "Twin Elements Omega Anima", "Macula Marius Omega Anima", "Medusa Omega Anima", "Nezha Omega Anima", "Apollo Omega Anima", "Dark Angel Olivia Omega Anima",
                                  "Athena Anima", "Grani Anima", "Baal Anima", "Garuda Anima", "Odin Anima", "Lich Anima",
                                  "Athena Omega Anima", "Grani Omega Anima", "Baal Omega Anima", "Garuda Omega Anima", "Odin Omega Anima", "Lich Omega Anima",
                                  "Prometheus Anima", "Ca Ong Anima", "Gilgamesh Anima", "Morrigna Anima", "Hector Anima", "Anubis Anima",
                                  "Prometheus Omega Anima", "Ca Ong Omega Anima", "Gilgamesh Omega Anima", "Morrigna Omega Anima", "Hector Omega Anima", "Anubis Omega Anima",
                                  "Huanglong Anima", "Huanglong Omega Anima", "Qilin Anima", "Qilin Omega Anima"]

        MessageLog.print_message(f"[INFO] Now detecting item rewards...")

        total_amount_farmed = 0

        # Detect amounts gained from each item on the Loot Collected screen. If the item is on the blacklist, use my method instead.
        if item_name in blacklisted_items:
            locations = ImageUtils.find_all(item_name, is_item = True, custom_confidence = 0.99)
        elif item_name in lite_blacklisted_items:
            locations = ImageUtils.find_all(item_name, is_item = True, custom_confidence = 0.85)
        else:
            locations = ImageUtils.find_all(item_name, is_item = True, custom_confidence = 0.80)

        for index, location in enumerate(locations):
            check = False

            # Filter out any duplicate locations that are 1 pixels from each other when the item is in either of the blacklists.
            if item_name in blacklisted_items or item_name in lite_blacklisted_items:
                for x in range(index):
                    if (abs(location[0] - locations[x][0]) <= 1 and location[1] == locations[x][1]) or (abs(location[1] - locations[x][1]) and location[0] == locations[x][0]) or (
                            abs(location[0] - locations[x][0]) and abs(location[1] - locations[x][1])):
                        check = True

            if not check:
                # Create a screenshot in the specified region named "test" and save it in the /temp/ folder. Then use EasyOCR to extract text from it into a list.
                # Adjust the width and height variables if EasyOCR cannot detect the numbers correctly.
                left = location[0] + 10
                top = location[1] - 5
                width = 30
                height = 25
                test_image = pyautogui.screenshot(f"temp/test.png", region = (left, top, width, height))
                # test_image.show() # Uncomment this line of code to see what the bot captured for the region of the detected text.
                #result = ImageUtils._reader.readtext(f"temp/test.png", detail = 0)
                result = []
                # Split any unnecessary characters in the extracted text until only the number remains.
                result_cleaned = 0
                if len(result) != 0:
                    result_split = [char for char in result[0]]
                    for char in result_split:
                        try:
                            if int(char):
                                result_cleaned = int(char)
                        except ValueError:
                            continue
                else:
                    result_cleaned = 1

                total_amount_farmed += result_cleaned
            else:
                MessageLog.print_message(f"[INFO] Duplicate location detected. Removing it...")

        # If items were detected on the Quest Results screen, take a screenshot and save in the /results/ folder.    
        if take_screenshot and total_amount_farmed != 0:
            ImageUtils._take_screenshot()

        MessageLog.print_message(f"[INFO] Detection of item rewards finished.")
        return total_amount_farmed

    @staticmethod
    def wait_vanish(image_name: str, timeout: int = 10, suppress_error: bool = False) -> bool:
        """Check if the provided image vanishes from the screen after a certain amount of time.

        Args:
            image_name (str): Name of the image file in the /images/buttons/ folder.
            timeout (int, optional): Timeout in tries. Defaults to 10.
            suppress_error (bool, optional): Suppresses template matching error if True. Defaults to False.

        Returns:
            (bool): True if the image vanishes from the screen within the allotted time or False if timeout was reached.
        """
        MessageLog.print_message(f"\n[INFO] Now waiting for {image_name} to vanish from screen...")

        template: numpy.ndarray = ImageUtils._read_template("buttons", f"{image_name.lower()}.jpg")
        if template is None:
            return False

        for _ in range(timeout):
            if ImageUtils._match(template) is False:
                MessageLog.print_message(f"[SUCCESS] Image successfully vanished from screen...")
                return True

        if suppress_error is False:
            MessageLog.print_message(f"[WARNING] Image did not vanish from screen...")

        return False

    @staticmethod
    def get_button_dimensions(image_name: str) -> Tuple[int, int]:
        """Get the dimensions of a image in /images/buttons/ folder.

        Args:
            image_name (str): File name of the image in /images/buttons/ folder.

        Returns:
            (Tuple[int, int]): Tuple of the width and the height of the image.
        """
        # 有些點擊目標是算出來的座標、沒有對應模板檔（例如 Mundus 節點、
        # The World 中央球）。找不到檔案時回傳一個小預設框，讓點擊隨機化
        # 照常運作、不因缺檔崩潰。
        path = ImageUtils._template_path("buttons", f"{image_name}.jpg")
        if not os.path.exists(path):
            return 20, 20
        image = Image.open(path)
        width, height = image.size
        image.close()
        return width, height

    @staticmethod
    def _take_screenshot():
        """Takes a screenshot of the Quest Results screen when called in find_farmed_items().

        Returns:
            None
        """
        MessageLog.print_message(f"[INFO] Taking a screenshot of the Quest Results screen...")

        # Construct the image file and folder name from the current date, time, and image number.
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        current_date = date.today()
        new_file_name = f"{current_date} {current_time} #{ImageUtils._image_number}"
        ImageUtils._image_number += 1
        if ImageUtils._new_folder_name is None:
            ImageUtils._new_folder_name = f"{current_date} {current_time}"

        # Take a screenshot using the calibrated window dimensions.
        new_image: PIL.Image.Image = pyautogui.screenshot(region = (Settings.window_left, Settings.window_top, Settings.window_width, Settings.window_height))

        # Create the /results/ directory if it does not already exist.
        current_dir = os.getcwd()
        results_dir = os.path.join(current_dir, r"results")
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # Then create a new folder to hold this session's screenshots in.
        new_dir = os.path.join(current_dir, r"results", ImageUtils._new_folder_name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        # Finally, save the new image into the results directory with its new file name.
        new_image.save(f"{ImageUtils._current_dir}/results/{ImageUtils._new_folder_name}/{new_file_name}.jpg")
        MessageLog.print_message(f"[INFO] Results image saved as \"{new_file_name}.jpg\" in \"{ImageUtils._new_folder_name}\" folder...")
        return None

    @staticmethod
    def _play_captcha_sound():
        """Plays the CAPTCHA.mp3 music file.

        Returns:
            None
        """
        playsound(f"{ImageUtils._current_dir}/backend/CAPTCHA.mp3", block = False)
        return None

    @staticmethod
    def generate_alert_for_captcha():
        """Displays a alert that will inform users that a CAPTCHA was detected.

        Returns:
            None
        """
        ImageUtils._play_captcha_sound()
        pyautogui.alert(
            text = "Stopping bot. Please enter the CAPTCHA yourself and play this mission manually to its completion. \n\nIt is now highly recommended that you take a break of several hours and "
                   "in the future, please reduce the amount of hours that you use this program consecutively without breaks in between.",
            title = "CAPTCHA Detected!", button = "OK")
        return None

    @staticmethod
    def generate_alert(message: str):
        """Displays a alert that will inform users about various user errors that may occur.

        Args:
            message (str): The message to be displayed.

        Returns:
            None
        """
        ImageUtils._play_captcha_sound()
        pyautogui.alert(text = message, title = "Exception Encountered", button = "OK")
        return None
