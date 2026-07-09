# -*- coding: utf-8 -*-
"""GUI 多語言支援。

以中文原文作為 key：
- 語言為 zh 時直接回傳原文
- 語言為 en 時查表，查不到就回退中文（保證不會顯示空白）

語言偏好儲存在 gui/data/ui_config.json，重開程式後保留。
"""
import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ui_config.json")

current_language = "zh"

_EN = {
    # ---- 視窗與分頁 ----
    "碧藍幻想自動化工具": "Granblue Automation",
    "任務": "Tasks",
    "設定": "Settings",
    "日誌": "Log",
    "語言": "Language",

    # ---- 任務分頁 ----
    "遊戲模式": "Game Mode",
    "戰鬥腳本": "Combat Script",
    "次數": "Runs",
    "新增任務": "Add Task",
    "新增休息": "Add Break",
    "刪除選中": "Remove Selected",
    "清空列表": "Clear All",
    "開始": "Start",
    "停止": "Stop",
    "拖曳任務可重新排序": "Drag tasks to reorder",
    "休息": "Break",
    "分鐘": "min",
    "執行中": "Running",
    "無可用腳本": "No scripts available",
    "次": "runs",

    # ---- 設定分頁 ----
    "執行選項": "Run Options",
    "模擬人類滑鼠移動": "Human-like mouse movement",
    "滑鼠移動速度（秒）": "Mouse speed (sec)",
    "啟用執行間隔（秒）": "Delay between runs (sec)",
    "啟用隨機執行間隔": "Random delay between runs",
    "最短": "Min",
    "最長": "Max",
    "戰鬥選項": "Combat Options",
    "戰鬥中刷新（auto/FA 攻擊後刷新頁面）": "Refresh during combat (reload after attacking in auto/FA)",
    "自動施放快速召喚石": "Auto quick summon",
    "找不到召喚石時自動選第一個": "Pick first summon if target not found",
    "Raid 選項": "Raid Options",
    "自動退出 Raid": "Auto-leave raid",
    "最長時間（分鐘）": "Max time (min)",
    "不超時模式": "No-timeout mode",
    "HP 低於（%）時撤退": "Retreat below HP (%)",
    "視窗與安全": "Window & Safety",
    "靜態視窗校準（執行中不可移動遊戲視窗）": "Static window calibration (don't move the game window while running)",
    "防偵測（每輪結束把滑鼠移出視窗）": "Anti-detection (move mouse out of window between runs)",
    "開場先休息": "Rest at start",
    "ROTB 首選": "ROTB First",
    "ROTB 方式": "ROTB Method",
    "1=朱雀 2=玄武 3=白虎 4=青龍": "1=Zhuque 2=Xuanwu 3=Baihu 4=Qinglong",

    # ---- 對話框 ----
    "錯誤": "Error",
    "提示": "Info",
    "確認停止": "Confirm Stop",
    "確定要停止目前執行中的任務嗎？": "Are you sure you want to stop the running tasks?",
    "任務列表是空的，請先新增任務。": "The task list is empty. Add a task first.",
    "請先選擇戰鬥腳本。": "Please choose a combat script first.",
    "腳本檔不存在或無法讀取：": "Script file missing or unreadable: ",
    "任務已全部完成": "All tasks completed",
    "任務已停止": "Tasks stopped",
    "開始執行任務佇列，共 {n} 個任務": "Starting task queue with {n} task(s)",
    "找不到後端程式（backend/main.py），請確認安裝完整。": "Backend not found (backend/main.py). Please check the installation.",
    "第 {i} 個任務開始：{name}": "Task {i} started: {name}",
    "第 {i} 個任務結束（代碼 {code}）": "Task {i} finished (exit code {code})",
    "休息 {m} 分鐘…": "Taking a break for {m} minute(s)...",
}


def tr(text: str, **fmt) -> str:
    """翻譯字串；zh 直接回傳原文，en 查表、查不到回退原文。支援 {name} 格式化參數。"""
    out = _EN.get(text, text) if current_language == "en" else text
    if fmt:
        try:
            out = out.format(**fmt)
        except (KeyError, IndexError):
            pass
    return out


def set_language(lang: str):
    global current_language
    current_language = "en" if lang == "en" else "zh"
    _save_config({"language": current_language})


def load_language() -> str:
    global current_language
    current_language = _load_config().get("language", "zh")
    return current_language


def _load_config() -> dict:
    try:
        with open(_CONFIG_FILE, encoding = "utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_config(update: dict):
    cfg = _load_config()
    cfg.update(update)
    try:
        os.makedirs(os.path.dirname(_CONFIG_FILE), exist_ok = True)
        with open(_CONFIG_FILE, "w", encoding = "utf-8") as f:
            json.dump(cfg, f, ensure_ascii = False, indent = 2)
    except OSError:
        pass
