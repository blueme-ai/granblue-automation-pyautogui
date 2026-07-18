from typing import Tuple, List

from utils.message_log import MessageLog
from utils.settings import Settings
from utils.image_utils import ImageUtils
from utils.mouse_utils import MouseUtils
from bot.combat_mode import CombatMode


class ArcarumSandboxException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ArcarumSandbox:
    """
    Provides the navigation and any necessary utility functions to handle the Arcarum Replicard Sandbox game mode.
    """

    _first_run: bool = True

    # The x and y coordinates are the difference between the center of the Menu button at the top-right and the center of the node itself.
    # The section refers to the left most page that the node is located in starting at page 0.
    _mission_data = {
        ##########
        # Zone Eletio
        "Slithering Seductress": {
            "section": 0,
            "x": 335,
            "y": 210
        },
        "Living Lightning Rod": {
            "section": 0,
            "x": 60,
            "y": 200
        },
        "Eletion Drake": {
            "section": 0,
            "x": 105,
            "y": 340
        },
        "Paradoxical Gate": {
            "section": 1,
            "x": 305,
            "y": 205
        },
        "Blazing Everwing": {
            "section": 1,
            "x": 180,
            "y": 190
        },
        "Death Seer": {
            "section": 1,
            "x": 55,
            "y": 270
        },
        "Hundred-Armed Hulk": {
            "section": 2,
            "x": 305,
            "y": 185
        },
        "Terror Trifecta": {
            "section": 2,
            "x": 210,
            "y": 260
        },
        "Rageborn One": {
            "section": 2,
            "x": 285,
            "y": 295
        },
        "Eletion Glider": {
            "section": 2,
            "x": 70,
            "y": 260
        },

        ##########
        # Zone Faym
        "Trident Grandmaster": {
            "section": 0,
            "x": 350,
            "y": 210
        },
        "Hoarfrost Icequeen": {
            "section": 0,
            "x": 210,
            "y": 270
        },
        "Oceanic Archon": {
            "section": 0,
            "x": 95,
            "y": 340
        },
        "Farsea Predator": {
            "section": 1,
            "x": 350,
            "y": 210
        },
        "Faymian Fortress": {
            "section": 1,
            "x": 205,
            "y": 270
        },
        "Draconic Simulacrum": {
            "section": 1,
            "x": 70,
            "y": 210
        },
        "Azureflame Dragon": {
            "section": 2,
            "x": 340,
            "y": 215
        },
        "Eyes of Sorrow": {
            "section": 2,
            "x": 315,
            "y": 345
        },
        "Mad Shearwielder": {
            "section": 2,
            "x": 60,
            "y": 215
        },
        "Faymian Gun": {
            "section": 2,
            "x": 200,
            "y": 285
        },

        ##########
        # Zone Goliath
        "Avatar of Avarice": {
            "section": 0,
            "x": 285,
            "y": 345
        },
        "Temptation's Guide": {
            "section": 0,
            "x": 215,
            "y": 170
        },
        "World's Veil": {
            "section": 0,
            "x": 170,
            "y": 270
        },
        "Goliath Keeper": {
            "section": 1,
            "x": 355,
            "y": 335
        },
        "Bloodstained Barbarian": {
            "section": 1,
            "x": 260,
            "y": 205
        },
        "Frenzied Howler": {
            "section": 1,
            "x": 50,
            "y": 190
        },
        "Goliath Vanguard": {
            "section": 1,
            "x": 65,
            "y": 360
        },
        "Vestige of Truth": {
            "section": 2,
            "x": 375,
            "y": 210
        },
        "Writhing Despair": {
            "section": 2,
            "x": 250,
            "y": 260
        },
        "Goliath Triune": {
            "section": 2,
            "x": 50,
            "y": 300
        },

        ##########
        # Zone Harbinger
        "Vengeful Demigod": {
            "section": 0,
            "x": 235,
            "y": 185
        },
        "Dirgesinger": {
            "section": 0,
            "x": 345,
            "y": 235
        },
        "Wildwind Conjurer/Fullthunder Conjurer": {
            "section": 0,
            "x": 215,
            "y": 310
        },
        "Harbinger Simurgh": {
            "section": 0,
            "x": 120,
            "y": 260
        },
        "Harbinger Hardwood": {
            "section": 1,
            "x": 365,
            "y": 320
        },
        "Demanding Stormgod": {
            "section": 1,
            "x": 275,
            "y": 250
        },
        "Harbinger Stormer": {
            "section": 1,
            "x": 180,
            "y": 150
        },
        "Harbinger Tyrant": {
            "section": 2,
            "x": 370,
            "y": 200
        },
        "Phantasmagoric Aberration": {
            "section": 2,
            "x": 230,
            "y": 315
        },
        "Dimensional Riftwalker": {
            "section": 2,
            "x": 115,
            "y": 245
        },

        # 510, 135

        ##########
        # Zone Invidia
        "Infernal Hellbeast": {
            "section": 0,
            "x": 350,
            "y": 215
        },
        "Spikeball": {
            "section": 0,
            "x": 115,
            "y": 260
        },
        "Blushing Groom": {
            "section": 0,
            "x": 45,
            "y": 185
        },
        "Unworldly Guardian": {
            "section": 1,
            "x": 290,
            "y": 260
        },
        "Deva of Wisdom": {
            "section": 1,
            "x": 185,
            "y": 130
        },
        "Sword of Aberration": {
            "section": 1,
            "x": 170,
            "y": 220
        },
        "Athena Militis": {
            "section": 1,
            "x": 185,
            "y": 350
        },

        ##########
        # Zone Joculator
        "Glacial Hellbeast": {
            "section": 0,
            "x": 50,
            "y": 180
        },
        "Giant Sea Plant": {
            "section": 0,
            "x": 375,
            "y": 280
        },
        "Maiden of the Depths": {
            "section": 0,
            "x": 145,
            "y": 340
        },
        "Bloody Soothsayer": {
            "section": 1,
            "x": 260,
            "y": 340
        },
        "Nebulous One": {
            "section": 1,
            "x": 30,
            "y": 280
        },
        "Dreadful Scourge": {
            "section": 1,
            "x": 240,
            "y": 140
        },
        "Grani Militis": {
            "section": 1,
            "x": 200,
            "y": 230
        },

        ##########
        # Zone Kalendae
        "Bedeviled Plague": {
            "section": 1,
            "x": 300,
            "y": 180
        },
        "Xeno Vohu Manah Militis": {
            "section": 1,
            "x": 350,
            "y": 240
        },

        "Tainted Hellmaiden": {
            "section": 1,
            "x": 100,
            "y": 340
        },
        "Watcher from Above": {
            "section": 1,
            "x": 20,
            "y": 215
        },
        "Scintillant Matter": {
            "section": 0,
            "x": 365,
            "y": 245
        },
        "Ebony Executioner": {
            "section": 0,
            "x": 250,
            "y": 145
        },
        "Hellbeast of Doom": {
            "section": 0,
            "x": 125,
            "y": 345
        },
        "Baal Militis": {
            "section": 0,
            "x": 220,
            "y": 245
        },

        ##########
        # Zone Liber
        "Mounted Toxophilite": {
            "section": 0,
            "x": 225,
            "y": 145
        },
        "Beetle of Damnation": {
            "section": 0,
            "x": 230,
            "y": 345
        },
        "Ageless Guardian Beast": {
            "section": 0,
            "x": 120,
            "y": 250
        },
        "Solar Princess": {
            "section": 1,
            "x": 330,
            "y": 265
        },
        "Drifting Blade Demon": {
            "section": 1,
            "x": 225,
            "y": 150
        },
        "Simpering Beast": {
            "section": 1,
            "x": 220,
            "y": 335
        },
        "Garuda Militis": {
            "section": 1,
            "x": 50,
            "y": 225
        },
    }

    @staticmethod
    def _navigate_to_mission(skip_to_action: bool = False):
        """Navigates to the specified Arcarum Replicard Sandbox mission inside the current Zone.

        Args:
            skip_to_action (bool, optional): True if the mission is already selected. Defaults to False.

        Returns:
            None
        """
        from bot.game import Game

        MessageLog.print_message(f"[ARCARUM.SANDBOX] Now beginning navigation to {Settings.mission_name} inside {Settings.map_name}...")

        if skip_to_action is False:
            section: int = ArcarumSandbox._mission_data[Settings.mission_name]["section"]
            x: int = ArcarumSandbox._mission_data[Settings.mission_name]["x"]
            y: int = ArcarumSandbox._mission_data[Settings.mission_name]["y"]

            # Shift the Zone over to the right based on the section that the mission is located at.
            if section == 1:
                Game.find_and_click_button("arcarum_sandbox_right_arrow")
            elif section == 2:
                Game.find_and_click_button("arcarum_sandbox_right_arrow")
                Game.wait(1.0)
                Game.find_and_click_button("arcarum_sandbox_right_arrow")

            Game.wait(1.0)

            # Now click on the specified node that has the mission offset by the coordinates associated with it based off of the Home Menu button location.
            # 節點偏移座標是 1 倍縮放時量的，要乘上偵測到的螢幕縮放比例
            scale = ImageUtils._template_scale
            home_location: Tuple[int, int] = ImageUtils.find_button("home_menu", tries = 10)
            if home_location is None:
                raise ArcarumSandboxException("Failed to find the Home Menu anchor for node navigation (zone map may not have loaded).")
            MouseUtils.move_and_click_point(home_location[0] - int(x * scale), home_location[1] + int(y * scale), "arcarum_node")

        Game.wait(1.0)
        # if gold chest exists, the mission may be invisible
        if Game.find_and_click_button("gold_chest"):
            ArcarumSandbox._open_gold_chest()
            return None

        if Game.find_and_click_button("mimic", suppress_error = True):
            Game.wait(3.0)
            if Game.check_for_captcha():
                Game.wait(3.0)
            if Game.find_party_and_start_mission(Settings.group_number, Settings.party_number):
                if CombatMode.start_combat_mode():
                    Game.collect_loot(is_completed = True)
            Game.find_and_click_button("expedition")
            return None
        
        if ImageUtils.find_button("boost"):
            # 有bonus怪
            MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Found Boost and fighting it...")
            action_locations: List[Tuple[int, ...]] = ImageUtils.find_all("arcarum_sandbox_action")
            MouseUtils.move_and_click_point(action_locations[0][0], action_locations[0][1], "arcarum_sandbox_action")
            return None

        # If there is no Defender, then the first action is the mission itself. Else, it is the second action.
        action_locations: List[Tuple[int, ...]] = ImageUtils.find_all("arcarum_sandbox_action")
        if len(action_locations) == 1:
            MouseUtils.move_and_click_point(action_locations[0][0], action_locations[0][1], "arcarum_sandbox_action")
        elif Settings.enable_defender and Settings.number_of_defeated_defenders < Settings.number_of_defenders:
            MouseUtils.move_and_click_point(action_locations[-2][0], action_locations[-2][1], "arcarum_sandbox_action")
            MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Found Defender and fighting it...")
            Settings.engaged_defender_battle = True
        else:
            # If there is Defender,the mission should be latest
            MouseUtils.move_and_click_point(action_locations[-1][0], action_locations[-1][1], "arcarum_sandbox_action")

        return None

    @staticmethod
    def _reset_position():
        """Resets the position of the bot to be at the left-most edge of the map.

        Returns:
            None
        """
        from bot.game import Game

        MessageLog.print_message(f"[ARCARUM.SANDBOX] Now determining if bot is starting all the way at the left edge of the Zone...")
        count = 0
        while Game.find_and_click_button("arcarum_sandbox_left_arrow", tries = 1, suppress_error = True):
            Game.wait(1.0)
            count += 1
            if count > 30:
                break

        MessageLog.print_message(f"[ARCARUM.SANDBOX] Left edge of the Zone has been reached.")

        return None

    @staticmethod
    def _navigate_to_zone():
        """Navigates to the specified Arcarum Replicard Sandbox Zone.

        Returns:
            None
        """
        from bot.game import Game

        if ArcarumSandbox._first_run:
            MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Now beginning navigation to {Settings.map_name}...")

            # 轉世入口已搬到首頁的 Extras 展開選單（舊版的 arcarum_banner 已不存在）。
            if Game.navigate_to_arcarum_extras() is False:
                raise ArcarumSandboxException("Failed to navigate to Arcarum from the Home screen.")

            ArcarumSandbox._first_run = False
        else:
            Game.wait(4.0)

        # 不在沙盒大廳的話（例如剛被錯誤處理送回首頁），重新走首頁 Extras 導航。
        # 舊版是點 arcarum_sandbox_banner，該模板已過時（實測 0.31）會亂點，不可用。
        if ImageUtils.confirm_location("arcarum_sandbox") is False:
            MessageLog.print_message("[ARCARUM.SANDBOX] 不在沙盒大廳，重新從首頁 Extras 導航...")
            if Game.navigate_to_arcarum_extras() is False:
                raise ArcarumSandboxException("Failed to navigate back to Replicard Sandbox.")

        Game.wait(3.0)

        zone_buttons = {
            "Zone Eletio": "arcarum_sandbox_zone_eletio",
            "Zone Faym": "arcarum_sandbox_zone_faym",
            "Zone Goliath": "arcarum_sandbox_zone_goliath",
            "Zone Harbinger": "arcarum_sandbox_zone_harbinger",
            "Zone Invidia": "arcarum_sandbox_zone_invidia",
            "Zone Joculator": "arcarum_sandbox_zone_joculator",
            "Zone Kalendae": "arcarum_sandbox_zone_kalendae",
            "Zone Liber": "arcarum_sandbox_zone_liber",
            "Zone Mundus": "arcarum_sandbox_zone_mundus",
        }
        if Settings.map_name not in zone_buttons:
            raise ArcarumSandboxException("Invalid map name provided for Arcarum Replicard Sandbox navigation.")

        # 先直接找圖磚點擊（大螢幕上八個區域一次全顯示，不需捲動）；
        # 找不到才往下捲一點再找——舊版對下半部區域無條件先捲 -400，
        # 在高解析度視窗上會把圖磚捲出點擊位置導致點空（下半部區域全失敗）。
        button_name = zone_buttons[Settings.map_name]
        navigation_check = Game.find_and_click_button(button_name, tries = 3, suppress_error = True)
        if navigation_check is False:
            MouseUtils.scroll_screen_from_home_button(-400)
            Game.wait(1.0)
            navigation_check = Game.find_and_click_button(button_name, tries = 3, suppress_error = True)

        if navigation_check is False:
            raise ArcarumSandboxException("Failed to navigate into the Sandbox Zone.")

        # 等待區域地圖載入完成（以 home_menu 錨點出現為準），
        # 否則後續的節點座標計算會拿不到錨點而失敗。
        Game.wait(2.0)
        if ImageUtils.find_button("home_menu", tries = 10, suppress_error = True) is None:
            raise ArcarumSandboxException("Zone map did not finish loading.")

        # Zone Mundus 是輻射狀地圖，結構與其他 8 區不同（元素選擇器＋中央
        # The World＋六個元素王節點）。兩種目標：
        #  - The World（中央）：底部常駐選項列，直接點「>」開打。
        #  - 元素王掃描（Mundus Element Sweep）：掃描地圖上可挑戰的節點，
        #    打第一個的第一關（Herald 增益王），用來刷 The World 的門票。
        if Settings.map_name == "Zone Mundus":
            _s = ImageUtils._template_scale
            if "The World" in Settings.mission_name:
                # 進場預設選中中央 The World，底部列會顯示它；直接找該列。
                world_location = ImageUtils.find_button("arcarum_sandbox_the_world", tries = 3, suppress_error = True)
                if world_location is None:
                    # 底部沒顯示 The World（遊戲可能記住了上次選的其他節點）→
                    # 點地圖中央的 The World 球選中它再試。中央球相對 home_menu 的
                    # 偏移是 1 倍縮放量測 (-204, +207)，乘縮放比例。
                    MessageLog.print_message("[ARCARUM.SANDBOX] 底部未顯示 The World，點中央球重新選中...")
                    home_location = ImageUtils.find_button("home_menu", tries = 5)
                    if home_location is not None:
                        MouseUtils.move_and_click_point(home_location[0] - int(204 * _s), home_location[1] + int(207 * _s), "arcarum_the_world_orb")
                        Game.wait(2.0)
                    world_location = ImageUtils.find_button("arcarum_sandbox_the_world", tries = 5)
                if world_location is None:
                    raise ArcarumSandboxException("Failed to find The World mission row in Zone Mundus.")
                # 從「The World」文字中心往右到「>」箭頭的偏移（1 倍縮放量測，乘縮放比例）
                MouseUtils.move_and_click_point(world_location[0] + int(235 * _s), world_location[1] + int(15 * _s), "arcarum_sandbox_the_world")
                Game.wait(3.0)
                return None
            elif Settings.mission_name == "Mundus Element Sweep":
                ArcarumSandbox._navigate_mundus_element()
                return None
            else:
                # 指定單刷某一隻元素王（關卡名即該怪名，例如 "Herald of Water"）。
                ArcarumSandbox._navigate_mundus_target(Settings.mission_name)
                return None

        # Now that the Zone is on screen, have the bot move all the way to the left side of the map.
        ArcarumSandbox._reset_position()

        # Finally, select the mission.
        ArcarumSandbox._navigate_to_mission()

        return None

    # 每次掃描交替起點方向：pass 1 由左往右、pass 2 由右往左…
    # 單輪掃描會被 stale 檢查提早收工（省時），遠端的 pan 只靠單向掃永遠
    # 到不了（run-0912 實測 4 輪全從左端起步，右端節點一次都沒被檢查）。
    _scan_from_left: bool = True

    @staticmethod
    def _mundus_scan(handle_selected) -> bool:
        """通用的 Zone Mundus 節點掃描。

        可挑戰的節點上有「劍氣泡」標記（arcarum_sandbox_node_battle）。逐節點
        嘗試選中（多候選偏移；成功＝底部出現關卡「>」箭頭 且 不是中央
        The World，避免誤打世界）。選中後把該節點的箭頭清單交給 handle_selected
        處理，回傳 True 代表已處理完成（結束掃描）。整圖都沒處理成功回傳 False。

        關鍵行為（實測得知）：
        - 底部面板會殘留上一個選中節點的內容，必須比對點擊前後面板有沒有變，
          否則沒點中也會被誤判成功。
        - 選中偏離視角中央的節點時，遊戲會把地圖平移置中該節點、面板延遲
          1~4 秒才更新——所以要輪詢等待面板變化，且每次成功選中後氣泡座標
          全部失效，必須重新偵測。
        - 平移優先點左右翻頁箭頭（固定平移量、視角可重現，原版做法；用戶
          指正拖曳每次位移不同），箭頭失效才用滑鼠水平拖曳當備援。
        """
        from bot.game import Game
        import cv2
        _s = ImageUtils._template_scale

        # 這一輪的起點端與前進方向（輪替）。
        from_left = ArcarumSandbox._scan_from_left
        ArcarumSandbox._scan_from_left = not from_left
        start_side = "left" if from_left else "right"
        forward = "right" if from_left else "left"

        def _clear_popups():
            Game.find_and_click_button("close", tries = 1, suppress_error = True)
            Game.find_and_click_button("cancel", tries = 1, suppress_error = True)

        def _panel_band():
            # 底部關卡面板所在的畫面帶（避開會動畫的地圖區），用來比對點擊前後
            # 面板是否真的換了內容。
            image = ImageUtils._grab_screen()
            height, width = image.shape
            return image[int(height * 0.48):int(height * 0.70), 0:int(width * 0.78)]

        def _band_same(a, b) -> bool:
            return a.shape == b.shape and float((cv2.absdiff(a, b) > 12).mean()) < 0.01

        # 這一次掃描已經檢查過（handle_selected 回傳 False）的節點面板，
        # 用面板影像當指紋，重複選中時直接跳過不再交給 handle。
        seen_bands: list = []

        def _band_seen(band) -> bool:
            return any(_band_same(band, s) for s in seen_bands)

        def _find_bubbles():
            # 可挑戰節點的標記有兩種：平常的「劍氣泡」；活動期間（如 2026-07
            # Tales of Arcarum）部分節點的氣泡會換成「活動獎章氣泡」（該節點
            # 掉活動素材）——只認劍氣泡會把大半節點當空氣（run-20260715-205226
            # 實測：18 輪全圖掃描找不到 Tide Caller，就是它的氣泡被換成獎章）。
            # 兩種氣泡對節點中心的幾何位置相同，共用同一組點擊偏移。
            bubbles = ImageUtils.find_all("arcarum_sandbox_node_battle", custom_confidence = 0.70)
            bubbles += ImageUtils.find_all("arcarum_sandbox_node_event", custom_confidence = 0.70)
            return bubbles

        def _refresh_bubble(bx, by):
            # 地圖會自己平移（選中節點的置中動畫、彈窗收掉後的回彈——
            # run-174938 實測回彈約 78px），偵測到的氣泡座標很快就過期，
            # 點下去全落在背景上。每次點擊前重新找「原座標附近」的氣泡；
            # 找不到＝地圖已經移走，這顆氣泡的座標作廢。
            candidates = _find_bubbles()
            best = None
            for (cx, cy) in candidates:
                d = abs(cx - bx) + abs(cy - by)
                if d <= 55 * _s and (best is None or d < best[0]):
                    best = (d, cx, cy)
            return (best[1], best[2]) if best is not None else None

        def _select_node(bx, by):
            # 回傳 (箭頭清單, 面板影像)；沒點中回傳 None；地圖移動導致座標
            # 過期回傳 "moved"（外層要立刻重新偵測氣泡，不是換下一顆）。
            # 偏移全部緊貼節點實際位置（氣泡左下約 -50,+30）——偏到氣泡上
            # 會打開任務資訊彈窗，把後面的點擊全部吃掉。
            for offset_index, (dx, dy) in enumerate(((-40, 30), (-52, 28), (-26, 36))):
                fresh = _refresh_bubble(bx, by)
                if fresh is None:
                    return "moved"
                bx, by = fresh
                before = _panel_band()
                MouseUtils.move_and_click_point(bx + int(dx * _s), by + int(dy * _s), "arcarum_mundus_node")
                # 選中偏離中央的節點會觸發地圖置中動畫，面板最慢 4 秒左右才換，
                # 用輪詢等待；一變就提早跳出。第一個偏移是量測過的幾何位置，
                # 等好等滿；後備偏移命中率低，短輪詢就好（已選中節點自己的
                # 氣泡怎麼點面板都不會變，別在它身上耗時間）。
                polls = 6 if offset_index == 0 else 2
                after = before
                for _ in range(polls):
                    Game.wait(0.8)
                    after = _panel_band()
                    if not _band_same(before, after):
                        break
                if _band_same(before, after):
                    # 面板沒變＝沒點中新節點（殘留面板）。可能誤開了任務資訊
                    # 彈窗（點到氣泡/資訊圖示會跳出來吃掉點擊），先清掉再試。
                    _clear_popups()
                    continue
                Game.wait(0.7)  # 等置中動畫收尾，讓箭頭位置穩定
                is_world = ImageUtils.find_button("arcarum_sandbox_the_world", tries = 1, suppress_error = True) is not None
                arrows = ImageUtils.find_all("arcarum_sandbox_mission_go", custom_confidence = 0.72)
                if len(arrows) > 0 and not is_world:
                    return arrows, _panel_band()
                # 面板變了卻沒有箭頭＝多半是任務資訊彈窗蓋住畫面，清掉再試。
                _clear_popups()
            # 所有偏移都沒選中：存地圖截圖（檔名帶氣泡座標）供校準點擊偏移。
            ImageUtils.save_debug_screenshot(f"mundus_node_miss_{int(bx)}x{int(by)}")
            return None

        _clear_popups()

        # 遊戲可能記住上次選中的節點（面板已經顯示它）。點已選中的節點面板
        # 不會變、會被面板變化檢查略過，所以先把「目前已選中的面板」交給
        # handle_selected 檢查一次。
        if ImageUtils.find_button("arcarum_sandbox_the_world", tries = 1, suppress_error = True) is None:
            arrows = ImageUtils.find_all("arcarum_sandbox_mission_go", custom_confidence = 0.72)
            if len(arrows) > 0:
                seen_bands.append(_panel_band())
                if handle_selected(arrows):
                    return True

        # 地圖移動不能靠左右箭頭（實測點了不會動——之前「翻頁」其實都是
        # 選中節點觸發的重新置中）。實測地圖可以用滑鼠「水平拖曳」平移
        # （手機式操作），而且拖過去之後原本被裁在視窗邊緣、點不中的節點
        # 會變成完整可點。走法：先一路拖到最左端（不點任何東西），再由左
        # 往右單向掃過去＝確定性的全圖覆蓋（選中節點會讓遊戲把地圖置中回
        # 該節點，雙向走法會被這個置中拉扯來回抵消，單向掃不會）。

        def _bubbles_moved(a, b) -> bool:
            if len(a) != len(b):
                return True
            a = sorted(a)
            b = sorted(b)
            return any(abs(pa[0] - pb[0]) > 25 or abs(pa[1] - pb[1]) > 25 for pa, pb in zip(a, b))

        def _drag_map(direction) -> bool:
            # 平移地圖視窗。優先點左右翻頁箭頭——原版做法，固定平移量、
            # 每次出來的畫面一致（用戶指正：拖曳每次位移都不同，視角不可
            # 重現，覆蓋與定位都不穩）。箭頭沒認到或點了沒位移（例如到端點
            # 箭頭消失/變灰）才退回滑鼠拖曳。回傳氣泡有沒有移動。
            arrow = ImageUtils.find_button(f"arcarum_sandbox_{direction}_arrow", tries = 1, suppress_error = True)
            if arrow is not None:
                before = _find_bubbles()
                MouseUtils.move_and_click_point(arrow[0], arrow[1], f"arcarum_sandbox_{direction}_arrow")
                Game.wait(1.5)
                after = _find_bubbles()
                if len(before) > 0 and len(after) > 0 and _bubbles_moved(before, after):
                    return True
                # 箭頭點了沒位移 → 往下掉回拖曳再確認一次。
            # 在地圖空白處水平拖曳平移視窗（拖曳不會觸發點擊選節點）。
            # 要看左邊＝把地圖往右拖，反之亦然。
            # 拖曳起點若剛好按在節點上會拖不動，所以準備多個起點輪流試；
            # 全部起點都拖不動＝地圖已到這個方向的盡頭。
            import pyautogui
            win_left, win_top, win_width, win_height = ImageUtils.get_window_dimensions()
            for (fx1, fx2, fy) in ((0.18, 0.72, 0.29), (0.24, 0.72, 0.325), (0.30, 0.70, 0.205)):
                before = _find_bubbles()
                y = win_top + int(win_height * fy)
                x1 = win_left + int(win_width * fx1)
                x2 = win_left + int(win_width * fx2)
                start, end = (x1, x2) if direction == "left" else (x2, x1)
                # 遊戲會把地圖吸附回欄位位置，單次拖曳實際只前進一小段；
                # 連拖兩次確保邊緣被裁切的節點完整進到視窗內（否則點不中）。
                for _ in range(2):
                    pyautogui.moveTo(start, y, duration = 0.2)
                    pyautogui.dragTo(end, y, duration = 0.5, button = "left")
                    Game.wait(1.2)
                after = _find_bubbles()
                if len(before) > 0 and len(after) > 0 and _bubbles_moved(before, after):
                    return True
            return False

        # 第一階段：不點任何節點，一路平移到起點端（氣泡位置不再變＝到端）。
        for _ in range(8):
            if not _drag_map(start_side):
                break
        MessageLog.print_message(f"[ARCARUM.SANDBOX] 已移到地圖最{'左' if from_left else '右'}端，開始{'由左往右' if from_left else '由右往左'}掃描...")

        # 本視角內點了沒反應的座標（幻影氣泡或已選中節點自己），rescan 直接跳過；
        # 地圖一移動（拖曳/置中）座標基準就變，隨即清空。
        dead_points: list = []

        def _point_dead(bx, by) -> bool:
            return any(abs(bx - dx) + abs(by - dy) <= 45 * _s for (dx, dy) in dead_points)

        # 連續「重選到已檢查節點」的次數——每撞一次，往右逃離的拖曳步數就加一
        # （上限 +2：拖太多步會跳過還沒掃的視角，run-0040 五隻失敗的主因之一）。
        seen_streak = 0

        # 連續「沒有選中任何新節點」的視角數。地圖最右端 snap-back 會讓
        # 「拖不動＝掃完」永遠不觸發（run-0040 實測卡同一視角 19 分鐘），
        # 用這個計數器兜底：連 3 個視角沒新節點＝這一輪掃完了，讓外層
        # 重試重新導航再掃一輪（每輪起點不同，覆蓋互補）。
        stale_views = 0

        # 第二階段：由左往右單向掃。
        for _view in range(20):
            _clear_popups()
            # 先開這個視角看得到的寶箱（免費獎勵）。一般寶箱點 OK/Close 收下；
            # mimic 寶箱怪會進戰鬥——存除錯截圖供之後完善（目前先盡量收）。
            chest = ImageUtils.find_button("arcarum_mundus_chest", tries = 1, suppress_error = True)
            if chest is not None:
                MessageLog.print_message("[ARCARUM.SANDBOX] 發現寶箱，開啟收獎...")
                MouseUtils.move_and_click_point(chest[0], chest[1], "arcarum_mundus_chest")
                Game.wait(2.0)
                ImageUtils.save_debug_screenshot("mundus_chest_opened")
                if Game.find_and_click_button("mimic", tries = 1, suppress_error = True):
                    # mimic 寶箱怪 → 交給既有選節點/戰鬥流程處理。
                    Game.wait(2.0)
                    arrows = ImageUtils.find_all("arcarum_sandbox_mission_go", custom_confidence = 0.72)
                    if len(arrows) > 0 and handle_selected(arrows):
                        return True
                else:
                    Game.find_and_click_button("ok", tries = 2, suppress_error = True)
                    Game.find_and_click_button("close", tries = 2, suppress_error = True)
                    Game.wait(1.0)

            # 每次成功選中節點地圖都會重新置中（座標全變），所以選中一個就
            # 重新偵測氣泡。已檢查過的節點用面板指紋跳過，避免無窮迴圈。
            hit_seen = False
            new_band_this_view = False
            for _rescan in range(6):
                bubbles = _find_bubbles()
                # 靠近起點端的先點，確保節點在被視窗甩出邊界之前一定被檢查過。
                bubbles.sort(key = lambda p: (p[0], p[1]), reverse = not from_left)
                if _rescan == 0 and len(bubbles) > 0:
                    MessageLog.print_message(f"[ARCARUM.SANDBOX] 本視窗發現 {len(bubbles)} 個可挑戰節點...")
                progressed = False  # 選中新節點或地圖移動＝氣泡清單要重偵測。
                for (bx, by) in bubbles:
                    if _point_dead(bx, by):
                        continue  # 本視角已證實點不出東西（幻影氣泡/已選中節點），別再耗時間。
                    result = _select_node(bx, by)
                    if result == "moved":
                        # 地圖移走了（置中/回彈），這批座標全部過期——
                        # 立刻重新偵測，別再拿舊座標點空氣。
                        dead_points.clear()
                        progressed = True
                        break
                    if result is None:
                        # 三個偏移都點不出面板變化＝幻影氣泡（道路交叉紋被誤認，
                        # run-2353 實測 (298,372) 每視角固定誤中）或已選中節點自己。
                        # 記進黑名單，同一視角的 rescan 不再點它。
                        dead_points.append((bx, by))
                        continue
                    arrows, band = result
                    if _band_seen(band):
                        # 重選到已檢查過的節點：選中動作已經把地圖拉回置中它，
                        # 視窗又彈回掃過的區域。不能當一般「沒進展」只拖一步——
                        # 下一輪最左的氣泡又是它、又被拉回來，會永遠困在原地
                        # （jp 佇列 boss1/2 各 25 分鐘死循環的主因）。跳出去
                        # 用遞增步數拖曳逃離。
                        hit_seen = True
                        break
                    seen_bands.append(band)
                    seen_streak = 0
                    new_band_this_view = True
                    # 存下每個選中節點的面板（供收集怪名模板／診斷用）。
                    ImageUtils.save_debug_screenshot("mundus_panel")
                    if handle_selected(arrows):
                        return True
                    progressed = True
                    break  # 地圖已因選中而移動，重新偵測氣泡再繼續。
                if hit_seen or not progressed:
                    break  # 本視窗沒有新節點可選了，拖曳地圖移動視窗。
            # 這個視角一個新節點都沒選到就累計；連 4 個視角沒新東西＝
            # 本輪掃完（端點 snap-back 讓拖曳永遠「成功」，不能只靠拖不動判終點；
            # 之前設 3 太急，右端 pan 沒掃到就收工）。
            if new_band_this_view:
                stale_views = 0
            else:
                stale_views += 1
                if stale_views >= 4:
                    MessageLog.print_message("[ARCARUM.SANDBOX] 連續 4 個視角沒有新節點，本輪掃描結束。")
                    break
            # 視窗內沒有新節點 → 往前進方向平移地圖。若是重選到舊節點被拉
            # 回來的，連續撞到幾次就多移幾步（上限 +2，移太多會跳過沒掃的
            # 視角），逃出已掃描的區域。移不動＝到端點。
            if hit_seen:
                seen_streak += 1
            drags = 1 + (min(seen_streak, 2) if hit_seen else 0)
            moved_any = False
            for _ in range(drags):
                if _drag_map(forward):
                    moved_any = True
                else:
                    break
            dead_points.clear()  # 視角變了，黑名單座標基準失效。
            if not moved_any:
                MessageLog.print_message(f"[ARCARUM.SANDBOX] 已掃到地圖最{'右' if from_left else '左'}端，全圖掃描完成。")
                break
        return False

    @staticmethod
    def _navigate_mundus_element():
        """Zone Mundus 元素王掃描：只打「有每日次數（Attempts Left）」的關卡
        （Herald 增益王＋每日 Militis，門票/素材來源），跳過只剩無限 Defender
        的節點，用來刷 The World 的門票。"""
        from bot.game import Game

        MessageLog.print_message("\n[ARCARUM.SANDBOX] Mundus 元素掃描：尋找有每日次數的節點...")

        def handle(arrows):
            attempts = ImageUtils.find_button("arcarum_sandbox_attempts_left", tries = 1, suppress_error = True)
            if attempts is None:
                MessageLog.print_message("[ARCARUM.SANDBOX] 此節點每日關卡已打完（只剩無限 Defender），跳過。")
                return False
            ImageUtils.save_debug_screenshot("mundus_after_node_click")
            # 點「挑戦可能回数/Attempts Left 同一列」的箭頭（每日關卡）。
            # 不能點最上面的箭頭：ミッション/導本按鈕列的鍍金邊在發光動畫幀
            # 會被誤認成箭頭（0.8+），排在最上面（jp sweep 實測誤點進任務頁）。
            arrows.sort(key = lambda p: abs(p[1] - attempts[1]))
            MouseUtils.move_and_click_point(arrows[0][0], arrows[0][1], "arcarum_mission_go")
            Game.wait(2.0)
            return True

        if not ArcarumSandbox._mundus_scan(handle):
            ImageUtils.save_debug_screenshot("mundus_no_node")
            raise ArcarumSandboxException("Mundus: 找不到有每日次數的元素節點（可能今日已全部打完）。")

    @staticmethod
    def _navigate_mundus_target(target_name: str):
        """Zone Mundus 指定單刷某一隻怪：掃遍地圖，找到底部關卡列出現該怪
        名字（模板 arcarum_mundus_<名字>）的節點就打那一關。名字模板需事先
        從遊戲截圖裁好（檔名：小寫、空格與 ' - 轉底線）。"""
        from bot.game import Game

        tmpl = "arcarum_mundus_" + target_name.lower().replace(" ", "_").replace("'", "").replace("-", "_")
        MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Mundus 指定單刷「{target_name}」...")

        def handle(arrows):
            # 0.85：Herald 系名字共用「Herald of」前綴，彼此交叉匹配可達 0.80，
            # 0.75 會把別的 Herald 誤認成目標；正確匹配實測 0.99+。
            name_loc = ImageUtils.find_button(tmpl, custom_confidence = 0.85, tries = 1, suppress_error = True)
            if name_loc is None:
                return False  # 這個節點的關卡列沒有目標怪 → 換下一個。
            ImageUtils.save_debug_screenshot("mundus_target_found")
            # 點與目標名字同一列（y 最接近）的那個箭頭。
            arrows.sort(key = lambda p: abs(p[1] - name_loc[1]))
            MouseUtils.move_and_click_point(arrows[0][0], arrows[0][1], "arcarum_mission_go")
            Game.wait(2.0)
            return True

        if not ArcarumSandbox._mundus_scan(handle):
            raise ArcarumSandboxException(f"Mundus: 掃遍地圖找不到「{target_name}」（今日已打完、名稱模板缺失、或名稱不符）。")

    @staticmethod
    def _refill_aap():
        """Refills AAP if necessary.

        Returns:
            None
        """
        if ImageUtils.confirm_location("aap", tries = 10):
            from bot.game import Game

            MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Bot ran out of AAP. Refilling now...")
            use_locations = ImageUtils.find_all("use")
            MouseUtils.move_and_click_point(use_locations[1][0], use_locations[1][1], "use")

            Game.wait(1.0)
            Game.find_and_click_button("ok")
            Game.wait(1.0)

            MessageLog.print_message(f"[ARCARUM.SANDBOX] AAP is now refilled.")

        return None
    
    @staticmethod
    def _play_zone_boss():
        """Clicks on Play if you are fighting a zone boss.

        Returns:
            None
        """
        play_button = ImageUtils.find_button("play")
        if play_button:
            MessageLog.print_message(f"\n[ARCARUM.SANDBOX] Now fighting zone boss...")
            MouseUtils.move_and_click_point(play_button[0], play_button[1], "play")

        return None

    @staticmethod
    def _open_gold_chest():
        """Clicks on a gold chest.
        If it is a mimic, fight it, if not, click ok.

        Returns:
            None
        """
        from bot.game import Game

        #MouseUtils.move_and_click_point(action_locations[0][0], action_locations[0][1], "arcarum_sandbox_action")
        Game.find_and_click_button("ok")
        Game.wait(5.0)
        if Game.find_and_click_button("ok", suppress_error = True) is False:
            MessageLog.print_message("\n[ARCARUM.SANDBOX] Click first...")
            action_locations: List[Tuple[int, ...]] = ImageUtils.find_all("arcarum_sandbox_action")
            MouseUtils.move_and_click_point(action_locations[0][0], action_locations[0][1], "arcarum_sandbox_action")
            Game.wait(3.0)
            if Game.find_party_and_start_mission(Settings.group_number, Settings.party_number):
                if CombatMode.start_combat_mode():
                    Game.collect_loot(is_completed = True)
            Game.find_and_click_button("expedition")
                 
        Game.wait(2.0)
        ArcarumSandbox._reset_position()
        ArcarumSandbox._navigate_to_mission()

    @staticmethod
    def start():
        """Starts the process of completing Arcarum Replicard Sandbox missions.

        Returns:
            None
        """
        from bot.game import Game

        # Start the navigation process.
        if ArcarumSandbox._first_run:
            ArcarumSandbox._navigate_to_zone()
        elif Game.find_and_click_button("alert_ok"):
            MessageLog.print_message("\n[INFO] Chrome alert pops...")
            Game.find_and_click_button("alert_ok")
            Game.find_and_click_button("home")
            Game.wait(5)
        elif Game.find_and_click_button("alert_ok_cn"):
            MessageLog.print_message("\n[INFO] Chrome alert pops2...")
            Game.find_and_click_button("alert_ok_cn")
            Game.find_and_click_button("home")
            Game.wait(5)   
        elif Game.find_and_click_button("play_again") is False:
            if Game.find_and_click_button("expedition"):
                # Wait out the animations that play, whether it be Treasure or Defender spawning.
                Game.wait(5.0)
                # Click away the Treasure popup if it shows up.
                Game.find_and_click_button("ok", suppress_error = True)
                if Settings.enable_gold_chest and Game.find_and_click_button("gold_chest") is True:
                    ArcarumSandbox._open_gold_chest()
                else:
                    # Start the mission again.
                    Game.wait(3.0)
                    # navigate to mission again.
                    ArcarumSandbox._navigate_to_mission(skip_to_action = True)
            elif Game.check_for_pending():
                ArcarumSandbox._first_run = True
                ArcarumSandbox._navigate_to_zone()
            elif ImageUtils.find_button("home_news") is not None:
                Game.go_back_home(confirm_location_check = True)
                ArcarumSandbox._first_run = True
                ArcarumSandbox._navigate_to_zone()
            else:
                if Game.find_and_click_button("mimic", suppress_error = True):
                    Game.wait(3.0)
                    if Game.find_party_and_start_mission(Settings.group_number, Settings.party_number):
                        if CombatMode.start_combat_mode():
                            Game.collect_loot(is_completed = True)
                    Game.find_and_click_button("expedition")

                if ImageUtils.find_button("attack"):
                    if CombatMode.start_combat_mode():
                        Game.collect_loot(is_completed = True)

                # If the bot find the "close" button, click.
                Game.find_and_click_button("close")

                # If the bot find the "ok" button, click.
                Game.find_and_click_button("ok")

                # If the bot cannot find the "Play Again" button, click the Expedition button.
                Game.find_and_click_button("expedition")

                # Wait out the animations that play, whether it be Treasure or Defender spawning.
                Game.wait(5.0)

                # Click away the Treasure popup if it shows up.
                Game.find_and_click_button("ok", suppress_error = True)
                if Settings.enable_gold_chest and Game.find_and_click_button("gold_chest") is True:
                    ArcarumSandbox._open_gold_chest()
                else:
                    # Start the mission again.
                    Game.wait(3.0)
                    # navigate to mission again.
                    ArcarumSandbox._first_run = True
                    ArcarumSandbox._navigate_to_zone()
                    #ArcarumSandbox._navigate_to_mission(skip_to_action = True)

        if Game.check_for_captcha():
            Game.wait(3.0)

        # Refill AAP if needed.
        ArcarumSandbox._play_zone_boss()
        #ArcarumSandbox._refill_aap()

        Game.wait(3.0)

        if Settings.engaged_defender_battle:
            if Game.find_party_and_start_mission(Settings.defender_group_number, Settings.defender_party_number, bypass_first_run = True):
                if CombatMode.start_combat_mode(is_defender = Settings.engaged_defender_battle):
                    Game.collect_loot(is_completed = True, is_defender = Settings.engaged_defender_battle)
        else:
            if Game.find_party_and_start_mission(Settings.group_number, Settings.party_number):
                if CombatMode.start_combat_mode():
                    Game.collect_loot(is_completed = True)

        return None
