from utils.settings import Settings
from utils.message_log import MessageLog
from utils.image_utils import ImageUtils
from utils.mouse_utils import MouseUtils
from bot.combat_mode import CombatMode
import pyautogui

class RaidException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Raid:
    """
    Provides the navigation and any necessary utility functions to handle the Raid game mode.
    """

    _raids_joined = 0


    @staticmethod
    def go_to_finder():
        """圖像導航到救援列表頁（首頁 → 任務 → Raid），取代舊版的 Alt+2 書籤快捷鍵。"""
        from bot.game import Game

        Game.go_back_home(confirm_location_check = True)
        Game.find_and_click_button("quest")
        Game.wait(2.0)

        # 檢查「你已從 Raid 撤退」彈窗與待處理戰鬥。
        if ImageUtils.confirm_location("you_retreated_from_the_raid_battle", tries = 2):
            Game.find_and_click_button("ok")
        if Game.check_for_pending():
            Game.find_and_click_button("quest")
            Game.wait(2.0)

        Game.find_and_click_button("raid")
        Game.wait(2.0)
        Raid._select_pinned_raid()

    @staticmethod
    def _select_pinned_raid():
        """切換到指定的釘選分頁（關卡名「釘選1」～「釘選4」）。

        需要 images/buttons/raid_tab_1.jpg ~ raid_tab_4.jpg 模板；
        還沒截圖做模板前，找不到就沿用目前顯示的分頁。
        """
        from bot.game import Game

        if not Settings.mission_name.startswith("釘選"):
            return

        n = Settings.mission_name[-1]
        if Game.find_and_click_button(f"raid_tab_{n}", tries = 3, suppress_error = True):
            Game.wait(1.5)
        else:
            MessageLog.print_message(f"[RAID] 找不到釘選分頁模板 raid_tab_{n}，沿用目前選中的分頁...")

    @staticmethod
    def _check_for_joined_raids():
        """Check and update the number of raids currently joined.

        Returns:
            None
        """
        # Find out the number of currently joined raids.
        joined_locations = ImageUtils.find_all("joined")

        if joined_locations is not None:
            Raid._raids_joined = len(joined_locations)
            MessageLog.print_message(f"\n[RAID] There are currently {Raid._raids_joined} raids joined.")

        return None

    @staticmethod
    def _clear_joined_raids():
        """Begin process to wait out the joined raids if there are 3 or more currently active.

        Returns:
            None
        """
        from bot.game import Game

        # If the maximum number of raids has been joined, collect any pending rewards with a interval of 30 seconds in between until the number of joined raids is below 3.
        while Raid._raids_joined >= 3:
            MessageLog.print_message(f"\n[RAID] Maximum raids of 3 has been joined. Waiting 30 seconds to see if any finish.")
            Game.wait(30)

            Game.go_back_home(confirm_location_check = True)
            Game.find_and_click_button("quest")

            if Game.check_for_pending():
                Game.find_and_click_button("quest")
                Game.wait(3.0)

            Game.find_and_click_button("raid")
            Game.wait(3.0)
            Game.find_and_click_button("recent")
            Raid._check_for_joined_raids()

        return None

    @staticmethod
    def _join_raid() -> bool:
        """Start the process to fetch a valid room code and join it.

        Returns:
            (bool): True if the bot arrived at the Summon Selection screen.
        """
        from bot.game import Game

        recovery_time = 1.5

        #Game.wait(2.0)
        if not ImageUtils.find_button("pending_battle_sidebar", tries = 5):
            return False

        # Now click on the first Room.
        room_locations = ImageUtils.find_all("pending_battle_sidebar")
        c = 0
        if len(room_locations) < 4:
            c += 1
            MouseUtils.scroll_screen_from_home_button(-480)
            Game.wait(1.0)
            room_locations = ImageUtils.find_all("pending_battle_sidebar")
            if len(room_locations) == 0:
                MouseUtils.scroll_screen_from_home_button(480)
                Game.wait(2.0)
                Game.find_and_click_button("reload_room")
                Game.wait(2.0)
                room_locations = ImageUtils.find_all("pending_battle_sidebar")

        
        Game.wait(1.0)
        hp_list = ImageUtils.find_all("hp")
        # 沿 HP 條往右偏移 hp_remain 像素（1 倍縮放時 20~89 對應 HP 百分比），
        # 取該點顏色判斷 HP 是否高於門檻；偏移要乘上螢幕縮放比例
        hp_offset = int(Settings.hp_remain * ImageUtils._template_scale)
        offset_points = [(x + hp_offset, y) for (x, y) in hp_list]

        # 步骤 2: 获取 RGB 颜色值
        def get_rgb_value(x, y):
            # 在这里定义如何根据坐标返回 RGB 颜色值
            rgb_value = pyautogui.pixel(x, y)
            return rgb_value

        find = False
        # 输出偏移后的坐标及其 RGB 颜色值
        for point in offset_points:
            rgb = get_rgb_value(point[0], point[1])
            MessageLog.print_message(f"Offset Point: {point}, RGB Color: {rgb}")
            if rgb[0] > 100:
                # hp > 50%
                MessageLog.print_message(f"found hp ok")
                MouseUtils.move_and_click_point(point[0], point[1], "pending_battle_sidebar")
                find = True
                break
        if not find:
            return False
        
        #MouseUtils.move_and_click_point(room_locations[0][0], room_locations[0][1], "pending_battle_sidebar")
        #Game.wait(1)

        # If the room code is valid and the raid is able to be joined, break out and head to the Summon Selection screen.
        #Game.find_and_click_button("ok", suppress_error = True)
        if Game.check_for_pending() is False:
            MessageLog.print_message(f"[WARNING] already ended or invalid.")

        #Game.wait(recovery_time)
        return True

    @staticmethod
    def _navigate():
        """Navigates to the specified Raid.

        Returns:
            None
        """
        from bot.game import Game

        MessageLog.print_message(f"\n[RAID] Beginning process to navigate to the raid: {Settings.mission_name}...")

        # Head to the Home screen.
        #Game.go_back_home(confirm_location_check = True)

        # Then navigate to the Quest screen.
        #Game.find_and_click_button("quest")

        #Game.wait(3.0)

        # Check for the "You retreated from the raid battle" popup.
        #if ImageUtils.confirm_location("you_retreated_from_the_raid_battle", tries = 3):
        #    Game.find_and_click_button("ok")

        # Check for any Pending Battles popup.
        #if Game.check_for_pending():
        #    Game.find_and_click_button("quest")

        #Game.wait(3.0)
        # Now navigate to the Raid screen.
        Raid.go_to_finder()
        for i in range(10):
            success = Raid._join_raid()
            if success:
                break
            # 頁內重整救援列表；沒有按鈕就 F5 重載頁面後重新選分頁
            if Game.find_and_click_button("reload_room", tries = 2, suppress_error = True):
                Game.wait(2)
            else:
                pyautogui.press('f5')
                Game.wait(3)
                Raid._select_pinned_raid()


    @staticmethod
    def start(first_run: bool):
        """Starts the process to complete a run for Raid Farming Mode and returns the number of items detected.

        Args:
            first_run (bool): Flag that determines whether or not to run the navigation process again. Should be False if the Farming Mode supports the "Play Again" feature for repeated runs.

        Returns:
            None
        """
        from bot.game import Game

        # Start the navigation process.
        if first_run:
            Raid._navigate()
        else:
            # Check for Pending Battles and then perform navigation again.
            Game.check_for_pending()
            Raid._navigate()
        # No Check.
        # Game.check_for_ep()

        # Check if the bot is at the Summon Selection screen.
        if Game.check_for_captcha():
            return None
        # Select the Party.
        if Game.quick_start_mission():
            MessageLog.print_message("\n[RAID] raid 次数+1")
            Settings.item_amount_farmed += 1
                    # Handle the rare case where joining the Raid after selecting the Summon and Party led the bot to the Quest Results screen with no loot to collect.
            if ImageUtils.confirm_location("no_loot", disable_adjustment = True):
                MessageLog.print_message("\n[RAID] Seems that the Raid just ended. Moving back to the Home screen and joining another Raid...")
            elif CombatMode.start_combat_mode():
                Game.collect_loot(is_completed = True, direct_battle=True)
                Settings.amount_of_runs_finished += 1
                        # go back to the Home screen.
                        #Game.find_and_click_button("home")
                        # Close the Skyscope mission popup.
                        #Game.check_for_skyscope()
        return None
