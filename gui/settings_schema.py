# -*- coding: utf-8 -*-
"""產生後端 settings JSON。

schema 必須與 backend/utils/settings.py 讀取的欄位一致。
GUI 沒提供的欄位一律填後端預設值，維持與舊版 qt_gui 相同的行為。
"""
from typing import List


def build_settings(
    farming_mode: str,
    item_amount: int,
    combat_script_name: str,
    combat_script: List[str],
    app_options: dict,
    mission: str = "",
    map_name: str = "",
    item: str = "",
) -> dict:
    """組出一個任務的完整後端設定。

    Args:
        farming_mode: 後端英文模式名（例如 "Raid"、"Take a break"）。
        item_amount: 執行次數（休息模式時為分鐘數）。
        combat_script_name: 戰鬥腳本檔名。
        combat_script: 戰鬥腳本內容（逐行）。
        app_options: 設定分頁的全域選項（見 main_window.collect_options()）。
        mission: 關卡名稱（例如 "Slithering Seductress"）。
        map_name: 地圖名稱（例如 "Zone Eletio"）。
        item: 目標道具名稱（例如 "Repeated Runs"）。
    """
    opt = app_options
    return {
        "game": {
            "combatScriptName": combat_script_name,
            "combatScript": combat_script,
            "farmingMode": farming_mode,
            "item": item,
            "mission": mission,
            "map": map_name,
            "itemAmount": item_amount,
            "summons": [],
            "summonDefault": False,
            "summonElements": [],
            "groupNumber": 0,
            "partyNumber": 0,
            "debugMode": False,
            "gameLanguage": opt.get("game_language", "en"),
        },
        "twitter": {
            "twitterUseVersion2": False,
            "twitterAPIKey": "",
            "twitterAPIKeySecret": "",
            "twitterAccessToken": "",
            "twitterAccessTokenSecret": "",
            "twitterBearerToken": "",
        },
        "discord": {
            "enableDiscordNotifications": False,
            "discordToken": "",
            "discordUserID": "",
        },
        "api": {
            "enableOptInAPI": opt.get("rest_at_start", True),
            "username": "",
            "password": "",
        },
        "configuration": {
            "enableBezierCurveMouseMovement": opt.get("bezier_mouse", False),
            "mouseSpeed": opt.get("mouse_speed", 0.1),
            "enableDelayBetweenRuns": opt.get("delay_enabled", False),
            "delayBetweenRuns": opt.get("delay_seconds", 15),
            "enableRandomizedDelayBetweenRuns": opt.get("random_delay_enabled", False),
            "delayBetweenRunsLowerBound": opt.get("delay_lower", 15),
            "delayBetweenRunsUpperBound": opt.get("delay_upper", 60),
            "enableRefreshDuringCombat": opt.get("refresh_during_combat", True),
            "enableAutoQuickSummon": opt.get("auto_quick_summon", True),
            "enableBypassResetSummon": opt.get("bypass_reset_summon", False),
            "staticWindow": opt.get("static_window", True),
            "enableMouseSecurityAttemptBypass": opt.get("anti_detection", False),
        },
        "misc": {
            "guiLowPerformanceMode": opt.get("rest_at_start", True),
            "alternativeCombatScriptSelector": False,
        },
        "nightmare": {
            "enableNightmare": False,
            "enableCustomNightmareSettings": True,
            "nightmareCombatScriptName": "",
            "nightmareCombatScript": [],
            "nightmareSummons": [],
            "nightmareSummonElements": [],
            "nightmareGroupNumber": 0,
            "nightmarePartyNumber": 1,
        },
        "event": {
            "enableLocationIncrementByOne": False,
            "selectBottomCategory": False,
            "first": True,
        },
        "raid": {
            "enableAutoExitRaid": opt.get("auto_exit_raid", False),
            "timeAllowedUntilAutoExitRaid": opt.get("auto_exit_minutes", 10),
            "enableNoTimeout": opt.get("no_timeout", False),
            "hpRemain": opt.get("hp_remain", 1),
        },
        "arcarum": {
            "enableStopOnArcarumBoss": True,
        },
        "generic": {
            "enableForceReload": False,
        },
        "xenoClash": {
            "selectTopOption": True,
        },
        "adjustment": {
            "enableCalibrationAdjustment": False,
            "adjustCalibration": 5,
            "enableGeneralAdjustment": False,
            "adjustButtonSearchGeneral": 5,
            "adjustHeaderSearchGeneral": 5,
            "enablePendingBattleAdjustment": False,
            "adjustBeforePendingBattle": 1,
            "adjustPendingBattle": 2,
            "enableCaptchaAdjustment": False,
            "adjustCaptcha": 5,
            "enableSupportSummonSelectionScreenAdjustment": False,
            "adjustSupportSummonSelectionScreen": 30,
            "enableCombatModeAdjustment": False,
            "adjustCombatStart": 50,
            "adjustDialog": 2,
            "adjustSkillUsage": 5,
            "adjustSummonUsage": 5,
            "adjustWaitingForReload": 3,
            "adjustWaitingForAttack": 100,
            "adjustCheckForNoLootScreen": 1,
            "adjustCheckForBattleConcludedPopup": 1,
            "adjustCheckForExpGainedPopup": 1,
            "adjustCheckForLootCollectionScreen": 1,
            "enableArcarumAdjustment": False,
            "adjustArcarumAction": 3,
            "adjustArcarumStageEffect": 10,
        },
        "sandbox": {
            "enableDefender": False,
            "enableGoldChest": opt.get("sandbox_gold_chest", True),
            "enableCustomDefenderSettings": False,
            "numberOfDefenders": 0,
            "defenderCombatScriptName": combat_script_name,
            "defenderCombatScript": combat_script,
            "defenderGroupNumber": 0,
            "defenderPartyNumber": 0,
        },
        "rotb": {
            "first": opt.get("rotb_first", 1),
            "method": opt.get("rotb_method", 1),
        },
    }
