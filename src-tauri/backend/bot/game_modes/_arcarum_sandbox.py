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

    @staticmethod
    def _mundus_scan(handle_selected) -> bool:
        """通用的 Zone Mundus 節點掃描。

        可挑戰的節點上有「劍氣泡」標記（arcarum_sandbox_node_battle）。先翻到
        最左、依 start_pan 起始位置（用已完成次數輪替以覆蓋全地圖），逐視角、
        逐節點嘗試選中（多候選偏移；成功＝底部出現關卡「>」箭頭 且 不是中央
        The World，避免誤打世界）。選中後把該節點的箭頭清單交給 handle_selected
        處理，回傳 True 代表已處理完成（結束掃描）。整圈都沒處理成功回傳 False。
        """
        from bot.game import Game
        _s = ImageUtils._template_scale

        def _clear_popups():
            Game.find_and_click_button("close", tries = 1, suppress_error = True)
            Game.find_and_click_button("cancel", tries = 1, suppress_error = True)

        def _select_node(bx, by):
            # 回傳選中節點後底部的關卡箭頭清單；沒選中回傳 None。
            for (dx, dy) in ((-40, 30), (0, 38), (-45, 20), (30, 35)):
                MouseUtils.move_and_click_point(bx + int(dx * _s), by + int(dy * _s), "arcarum_mundus_node")
                Game.wait(2.0)
                is_world = ImageUtils.find_button("arcarum_sandbox_the_world", tries = 1, suppress_error = True) is not None
                arrows = ImageUtils.find_all("arcarum_sandbox_mission_go", custom_confidence = 0.72)
                if len(arrows) > 0 and not is_world:
                    return arrows
            return None

        _clear_popups()
        for _ in range(8):
            if Game.find_and_click_button("arcarum_sandbox_left_arrow", tries = 1, suppress_error = True):
                Game.wait(0.7)
            else:
                break

        start_pan = Settings.item_amount_farmed % 6
        for _ in range(start_pan):
            if Game.find_and_click_button("arcarum_sandbox_right_arrow", tries = 1, suppress_error = True):
                Game.wait(0.7)
            else:
                break

        for _view in range(10):
            _clear_popups()
            bubbles = ImageUtils.find_all("arcarum_sandbox_node_battle", custom_confidence = 0.70)
            bubbles.sort(key = lambda p: (p[1], p[0]))
            if len(bubbles) > 0:
                MessageLog.print_message(f"[ARCARUM.SANDBOX] 本視角發現 {len(bubbles)} 個可挑戰節點（起始翻頁 {start_pan}）...")
            for (bx, by) in bubbles:
                arrows = _select_node(bx, by)
                if arrows is not None and handle_selected(arrows):
                    return True
            # 本視角處理不成 → 往右翻頁換視角；到最右繞回最左。
            if Game.find_and_click_button("arcarum_sandbox_right_arrow", tries = 1, suppress_error = True):
                Game.wait(1.0)
            else:
                for _ in range(8):
                    if Game.find_and_click_button("arcarum_sandbox_left_arrow", tries = 1, suppress_error = True):
                        Game.wait(0.7)
                    else:
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
            if ImageUtils.find_button("arcarum_sandbox_attempts_left", tries = 1, suppress_error = True) is None:
                MessageLog.print_message("[ARCARUM.SANDBOX] 此節點每日關卡已打完（只剩無限 Defender），跳過。")
                return False
            ImageUtils.save_debug_screenshot("mundus_after_node_click")
            # 每日關卡在最上（Herald→每日 Militis），無限 Defender 在下。
            arrows.sort(key = lambda p: p[1])
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
            name_loc = ImageUtils.find_button(tmpl, tries = 1, suppress_error = True)
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
