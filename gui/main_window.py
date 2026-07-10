# -*- coding: utf-8 -*-
"""主視窗：任務佇列 + 全域設定，支援中英文即時切換。"""
import json
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

# 全域停止快捷鍵（機器人會搶滑鼠，需要不用滑鼠就能停的方式）。
# keyboard 套件在 Windows 免額外權限；mac 需輔助使用權限，失敗時靜默略過。
# 用 ESC（Ctrl+Alt+Q 與用戶其他軟體衝突）；只在任務執行中才有作用。
try:
    import keyboard as _keyboard
except ImportError:
    _keyboard = None

STOP_HOTKEY = "esc"
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import i18n
from i18n import tr
from runner import TaskRunner, BREAK_MODE
from settings_schema import build_settings

_GUI_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_GUI_DIR)
_TAURI_DIR = os.path.join(_REPO_ROOT, "src-tauri")
_SCRIPTS_DIR = os.path.join(_TAURI_DIR, "scripts")
_DATA_DIR = os.path.join(_GUI_DIR, "data")

# 這些模式的後端仍依賴 harjeb 的瀏覽器書籤快捷鍵，尚未改回原版導航
BROKEN_MODES = {"快速活动", "Side Story"}


def _load_json(name: str) -> dict:
    with open(os.path.join(_DATA_DIR, name), encoding = "utf-8") as f:
        return json.load(f)


class MainWindow(QWidget):
    _hotkey_stop = Signal()

    def __init__(self):
        super().__init__()
        i18n.load_language()

        self.gamemode_dict = _load_json("data_zhcn.json")
        self.translate_dict = _load_json("translate.json")
        # 英文關卡名 → 日文名（顯示用，內部值仍是英文）
        self.names_ja = _load_json("names_ja.json")

        # 任務佇列：[{"mode": 中文模式名, "script": 檔名, "count": int}]，休息任務 script 為 None
        self.tasks: list[dict] = []

        self.runner = TaskRunner(_TAURI_DIR, self)
        self.runner.log_line.connect(self._append_log)
        self.runner.task_started.connect(self._highlight_task)
        self.runner.all_finished.connect(self._on_all_finished)

        self._build_ui()
        self._retranslate()
        self.resize(980, 620)

        # 快捷鍵回呼在背景執行緒觸發，經 Signal 轉回 Qt 主執行緒處理
        self._hotkey_stop.connect(self._on_hotkey_stop)
        if _keyboard is not None:
            try:
                _keyboard.add_hotkey(STOP_HOTKEY, self._hotkey_stop.emit)
            except Exception:
                pass

    def _on_hotkey_stop(self):
        """全域停止快捷鍵：不經確認立即停止（緊急用，滑鼠被搶時的逃生口）。"""
        if self.runner.is_running():
            self.runner.stop()
            self._append_log(tr("已透過快捷鍵 {k} 緊急停止。", k = STOP_HOTKEY.upper()))

    # ---------- UI 組裝 ----------

    def _build_ui(self):
        root = QVBoxLayout(self)

        # 右上角語言切換
        top_bar = QHBoxLayout()
        self.help_button = QPushButton()
        self.help_button.clicked.connect(self._show_help)
        top_bar.addWidget(self.help_button)
        top_bar.addStretch()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(1 if i18n.current_language == "en" else 0)
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        top_bar.addWidget(self.lang_label)
        top_bar.addWidget(self.lang_combo)
        root.addLayout(top_bar)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # ===== 任務分頁 =====
        task_page = QWidget()
        task_layout = QVBoxLayout(task_page)

        form_row = QHBoxLayout()
        self.mode_label = QLabel()
        self.mode_combo = QComboBox()
        for zh_name in self.gamemode_dict.keys():
            self.mode_combo.addItem(zh_name, zh_name)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.mission_label = QLabel()
        self.mission_combo = QComboBox()
        self.mission_combo.currentIndexChanged.connect(self._on_mission_changed)
        self.item_label = QLabel()
        self.item_combo = QComboBox()
        form_row.addWidget(self.mode_label)
        form_row.addWidget(self.mode_combo, 1)
        form_row.addWidget(self.mission_label)
        form_row.addWidget(self.mission_combo, 2)
        form_row.addWidget(self.item_label)
        form_row.addWidget(self.item_combo, 1)
        task_layout.addLayout(form_row)

        form_row2 = QHBoxLayout()
        self.script_label = QLabel()
        self.script_combo = QComboBox()
        self._populate_scripts()
        self.count_label = QLabel()
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 9999)
        form_row2.addWidget(self.script_label)
        form_row2.addWidget(self.script_combo, 2)
        form_row2.addWidget(self.count_label)
        form_row2.addWidget(self.count_spin)
        form_row2.addStretch()
        task_layout.addLayout(form_row2)
        self._on_mode_changed()

        button_row = QHBoxLayout()
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self._add_task)
        self.break_button = QPushButton()
        self.break_button.clicked.connect(self._add_break)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 720)
        self.break_spin.setValue(30)
        self.break_unit_label = QLabel()
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button = QPushButton()
        self.clear_button.clicked.connect(self._clear_tasks)
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.break_button)
        button_row.addWidget(self.break_spin)
        button_row.addWidget(self.break_unit_label)
        button_row.addStretch()
        button_row.addWidget(self.remove_button)
        button_row.addWidget(self.clear_button)
        task_layout.addLayout(button_row)

        self.task_list = QListWidget()
        self.task_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_list.model().rowsMoved.connect(self._on_rows_moved)
        self.task_list.setMaximumHeight(170)
        task_layout.addWidget(self.task_list)

        self.start_button = QPushButton()
        self.start_button.setMinimumHeight(36)
        self.start_button.clicked.connect(self._toggle_run)
        task_layout.addWidget(self.start_button)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(5000)
        task_layout.addWidget(self.log_view, 1)

        self.tabs.addTab(task_page, "")

        # ===== 設定分頁 =====
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)

        self.run_group = QGroupBox()
        run_grid = QVBoxLayout(self.run_group)
        self.bezier_check = QCheckBox()
        row = QHBoxLayout()
        row.addWidget(self.bezier_check)
        self.mouse_speed_label = QLabel()
        self.mouse_speed_spin = QDoubleSpinBox()
        self.mouse_speed_spin.setDecimals(1)
        self.mouse_speed_spin.setSingleStep(0.1)
        self.mouse_speed_spin.setValue(0.2)
        row.addWidget(self.mouse_speed_label)
        row.addWidget(self.mouse_speed_spin)
        row.addStretch()
        run_grid.addLayout(row)
        row = QHBoxLayout()
        self.delay_check = QCheckBox()
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 3600)
        self.delay_spin.setValue(15)
        self.random_delay_check = QCheckBox()
        self.delay_min_label = QLabel()
        self.delay_lower_spin = QSpinBox()
        self.delay_lower_spin.setRange(1, 3600)
        self.delay_lower_spin.setValue(15)
        self.delay_max_label = QLabel()
        self.delay_upper_spin = QSpinBox()
        self.delay_upper_spin.setRange(1, 3600)
        self.delay_upper_spin.setValue(60)
        row.addWidget(self.delay_check)
        row.addWidget(self.delay_spin)
        row.addWidget(self.random_delay_check)
        row.addWidget(self.delay_min_label)
        row.addWidget(self.delay_lower_spin)
        row.addWidget(self.delay_max_label)
        row.addWidget(self.delay_upper_spin)
        row.addStretch()
        run_grid.addLayout(row)
        row = QHBoxLayout()
        self.rest_check = QCheckBox()
        self.rest_check.setChecked(False)
        row.addWidget(self.rest_check)
        self.game_lang_label = QLabel()
        self.game_lang_combo = QComboBox()
        self.game_lang_combo.addItem("English", "en")
        self.game_lang_combo.addItem("日本語", "jp")
        row.addWidget(self.game_lang_label)
        row.addWidget(self.game_lang_combo)
        row.addStretch()
        run_grid.addLayout(row)
        settings_layout.addWidget(self.run_group)

        self.combat_group = QGroupBox()
        combat_grid = QVBoxLayout(self.combat_group)
        self.refresh_check = QCheckBox()
        self.refresh_check.setChecked(True)
        self.quick_summon_check = QCheckBox()
        self.bypass_summon_check = QCheckBox()
        combat_grid.addWidget(self.refresh_check)
        combat_grid.addWidget(self.quick_summon_check)
        combat_grid.addWidget(self.bypass_summon_check)
        settings_layout.addWidget(self.combat_group)

        self.raid_group = QGroupBox()
        raid_grid = QVBoxLayout(self.raid_group)
        row = QHBoxLayout()
        self.auto_exit_check = QCheckBox()
        self.auto_exit_label = QLabel()
        self.auto_exit_spin = QSpinBox()
        self.auto_exit_spin.setRange(1, 600)
        self.auto_exit_spin.setValue(10)
        row.addWidget(self.auto_exit_check)
        row.addWidget(self.auto_exit_label)
        row.addWidget(self.auto_exit_spin)
        row.addStretch()
        raid_grid.addLayout(row)
        row = QHBoxLayout()
        self.no_timeout_check = QCheckBox()
        self.hp_label = QLabel()
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 100)
        self.hp_spin.setValue(1)
        row.addWidget(self.no_timeout_check)
        row.addWidget(self.hp_label)
        row.addWidget(self.hp_spin)
        row.addStretch()
        raid_grid.addLayout(row)
        settings_layout.addWidget(self.raid_group)

        self.window_group = QGroupBox()
        window_grid = QVBoxLayout(self.window_group)
        self.static_window_check = QCheckBox()
        self.static_window_check.setChecked(True)
        self.anti_detect_check = QCheckBox()
        window_grid.addWidget(self.static_window_check)
        window_grid.addWidget(self.anti_detect_check)
        settings_layout.addWidget(self.window_group)
        settings_layout.addStretch()

        self.tabs.addTab(settings_page, "")

    # ---------- 語言 ----------

    def _on_language_changed(self):
        i18n.set_language(self.lang_combo.currentData())
        self._retranslate()

    def _retranslate(self):
        self.setWindowTitle(tr("碧藍幻想自動化工具"))
        self.lang_label.setText(tr("語言"))
        self.tabs.setTabText(0, tr("任務"))
        self.tabs.setTabText(1, tr("設定"))

        self.mode_label.setText(tr("遊戲模式"))
        self.mission_label.setText(tr("關卡"))
        self.item_label.setText(tr("目標道具"))
        self.script_label.setText(tr("戰鬥腳本"))
        self.count_label.setText(tr("次數"))
        self.help_button.setText(tr("使用說明"))
        self.add_button.setText(tr("新增任務"))
        self.break_button.setText(tr("新增休息"))
        self.break_unit_label.setText(tr("分鐘"))
        self.remove_button.setText(tr("刪除選中"))
        self.clear_button.setText(tr("清空列表"))
        self.task_list.setToolTip(tr("拖曳任務可重新排序"))
        self.start_button.setText(tr("停止") if self.runner.is_running() else tr("開始"))
        self.start_button.setToolTip(tr("執行中可隨時按 {k} 緊急停止（不需切回本視窗）", k = STOP_HOTKEY.upper()))

        # 模式下拉選單依語言顯示（內部值不變）
        for i in range(self.mode_combo.count()):
            zh_name = self.mode_combo.itemData(i)
            if i18n.current_language == "en":
                text = self.translate_dict.get(zh_name, zh_name)
            else:
                text = zh_name
            if zh_name in BROKEN_MODES:
                text += " (unavailable)" if i18n.current_language == "en" else "（待重做，暫不可用）"
            self.mode_combo.setItemText(i, text)

        self.run_group.setTitle(tr("執行選項"))
        self.bezier_check.setText(tr("模擬人類滑鼠移動"))
        self.mouse_speed_label.setText(tr("滑鼠移動速度（秒）"))
        self.delay_check.setText(tr("啟用執行間隔（秒）"))
        self.random_delay_check.setText(tr("啟用隨機執行間隔"))
        self.delay_min_label.setText(tr("最短"))
        self.delay_max_label.setText(tr("最長"))
        self.rest_check.setText(tr("開場先休息"))
        self.game_lang_label.setText(tr("遊戲語言"))
        self.game_lang_combo.setToolTip(tr("日本語需要 images/buttons_jp 的模板圖，缺圖時自動退回英文模板"))

        self.combat_group.setTitle(tr("戰鬥選項"))
        self.refresh_check.setText(tr("戰鬥中刷新（auto/FA 攻擊後刷新頁面）"))
        self.quick_summon_check.setText(tr("自動施放快速召喚石"))
        self.bypass_summon_check.setText(tr("找不到召喚石時自動選第一個"))

        self.raid_group.setTitle(tr("Raid 選項"))
        self.auto_exit_check.setText(tr("自動退出 Raid"))
        self.auto_exit_label.setText(tr("最長時間（分鐘）"))
        self.no_timeout_check.setText(tr("不超時模式"))
        self.hp_label.setText(tr("HP 低於（%）時撤退"))

        self.window_group.setTitle(tr("視窗與安全"))
        self.static_window_check.setText(tr("靜態視窗校準（執行中不可移動遊戲視窗）"))
        self.anti_detect_check.setText(tr("防偵測（每輪結束把滑鼠移出視窗）"))

        self._refresh_task_list()

    # ---------- 任務管理 ----------

    def _mission_display(self, mission: str) -> str:
        """關卡顯示名：有日文名時顯示「英文｜日文」，難度前綴自動剝除後查詢。"""
        ja = self.names_ja.get(mission)
        if ja is None:
            for prefix in ("N ", "H ", "VH ", "EX+ ", "EX "):
                if mission.startswith(prefix):
                    ja = self.names_ja.get(mission[len(prefix):])
                    break
        return f"{mission}｜{ja}" if ja else mission

    def _on_mode_changed(self):
        """依所選模式重新填入關卡清單。"""
        self.mission_combo.blockSignals(True)
        self.mission_combo.clear()
        mode = self.mode_combo.currentData()
        for mission_name in self.gamemode_dict.get(mode, {}).keys():
            self.mission_combo.addItem(self._mission_display(mission_name), mission_name)
        self.mission_combo.blockSignals(False)
        self._on_mission_changed()

    def _on_mission_changed(self):
        """依所選關卡重新填入目標道具清單。"""
        self.item_combo.clear()
        mode = self.mode_combo.currentData()
        mission = self.mission_combo.currentData()
        info = self.gamemode_dict.get(mode, {}).get(mission, {})
        for item in info.get("items", ["Repeated Runs"]):
            self.item_combo.addItem(item, item)

    def _populate_scripts(self):
        self.script_combo.clear()
        if os.path.isdir(_SCRIPTS_DIR):
            for name in sorted(os.listdir(_SCRIPTS_DIR)):
                if name.endswith(".txt"):
                    self.script_combo.addItem(name[:-4], name)
        if self.script_combo.count() == 0:
            self.script_combo.addItem(tr("無可用腳本"), "")

    def _task_display(self, task: dict) -> str:
        if task["mode"] == BREAK_MODE:
            return f"{tr('休息')} | {task['count']} {tr('分鐘')}"
        mode = task["mode"]
        if i18n.current_language == "en":
            mode = self.translate_dict.get(mode, mode)
        mission = task.get("mission", "")
        script = (task["script"] or "").replace(".txt", "")
        parts = [mode]
        if mission:
            parts.append(mission)
        parts.append(script)
        parts.append(f"{task['count']} {tr('次')}")
        return " | ".join(parts)

    def _refresh_task_list(self):
        self.task_list.clear()
        for task in self.tasks:
            self.task_list.addItem(self._task_display(task))

    def _add_task(self):
        script = self.script_combo.currentData()
        if not script:
            QMessageBox.warning(self, tr("錯誤"), tr("請先選擇戰鬥腳本。"))
            return
        script_path = os.path.join(_SCRIPTS_DIR, script)
        if not os.path.isfile(script_path):
            QMessageBox.warning(self, tr("錯誤"), tr("腳本檔不存在或無法讀取：") + script)
            return
        mode = self.mode_combo.currentData()
        mission = self.mission_combo.currentData() or ""
        info = self.gamemode_dict.get(mode, {}).get(mission, {})
        self.tasks.append({
            "mode": mode,
            "mission": mission,
            "map": info.get("map", ""),
            "item": self.item_combo.currentData() or "Repeated Runs",
            "script": script,
            "count": self.count_spin.value(),
        })
        self._refresh_task_list()

    def _add_break(self):
        self.tasks.append({"mode": BREAK_MODE, "script": None, "count": self.break_spin.value()})
        self._refresh_task_list()

    def _remove_selected(self):
        row = self.task_list.currentRow()
        if 0 <= row < len(self.tasks):
            self.tasks.pop(row)
            self._refresh_task_list()

    def _clear_tasks(self):
        self.tasks.clear()
        self._refresh_task_list()

    def _on_rows_moved(self, _parent, start, _end, _dest, row):
        task = self.tasks.pop(start)
        insert_at = row - 1 if row > start else row
        insert_at = max(0, min(insert_at, len(self.tasks)))
        self.tasks.insert(insert_at, task)

    # ---------- 執行 ----------

    def collect_options(self) -> dict:
        return {
            "bezier_mouse": self.bezier_check.isChecked(),
            "mouse_speed": self.mouse_speed_spin.value(),
            "delay_enabled": self.delay_check.isChecked(),
            "delay_seconds": self.delay_spin.value(),
            "random_delay_enabled": self.random_delay_check.isChecked(),
            "delay_lower": self.delay_lower_spin.value(),
            "delay_upper": self.delay_upper_spin.value(),
            "refresh_during_combat": self.refresh_check.isChecked(),
            "auto_quick_summon": self.quick_summon_check.isChecked(),
            "bypass_reset_summon": self.bypass_summon_check.isChecked(),
            "static_window": self.static_window_check.isChecked(),
            "anti_detection": self.anti_detect_check.isChecked(),
            "rest_at_start": self.rest_check.isChecked(),
            "auto_exit_raid": self.auto_exit_check.isChecked(),
            "auto_exit_minutes": self.auto_exit_spin.value(),
            "no_timeout": self.no_timeout_check.isChecked(),
            "hp_remain": self.hp_spin.value(),
            "game_language": self.game_lang_combo.currentData(),
        }

    def _toggle_run(self):
        if self.runner.is_running():
            answer = QMessageBox.question(
                self, tr("確認停止"), tr("確定要停止目前執行中的任務嗎？"),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.runner.stop()
            return

        if not self.tasks:
            QMessageBox.warning(self, tr("錯誤"), tr("任務列表是空的，請先新增任務。"))
            return

        options = self.collect_options()
        settings_list = []
        for task in self.tasks:
            if task["mode"] == BREAK_MODE:
                settings_list.append(build_settings(BREAK_MODE, task["count"], "", [], options))
                continue
            script_path = os.path.join(_SCRIPTS_DIR, task["script"])
            try:
                with open(script_path, encoding = "utf-8") as f:
                    script_lines = [line.strip() for line in f.readlines()]
            except OSError:
                QMessageBox.warning(self, tr("錯誤"), tr("腳本檔不存在或無法讀取：") + task["script"])
                return
            farming_mode = self.translate_dict.get(task["mode"], task["mode"])
            mission = self.translate_dict.get(task.get("mission", ""), task.get("mission", ""))
            settings_list.append(build_settings(
                farming_mode, task["count"], task["script"], script_lines, options,
                mission = mission, map_name = task.get("map", ""), item = task.get("item", "Repeated Runs")))

        self.start_button.setText(tr("停止"))
        self.runner.start(settings_list)

    def _show_help(self):
        QMessageBox.information(self, tr("使用說明"), tr(
            "【使用前準備】\n"
            "1. 用瀏覽器開啟碧藍幻想，視窗保持可見（不要縮小）\n"
            "2. 遊戲畫面停在「首頁」（看得到底部的 Home 按鈕）\n"
            "3. 遊戲內開啟兩個 Auto Restore 設定\n"
            "\n"
            "【操作步驟】\n"
            "1. 選遊戲模式 → 關卡 → 目標道具\n"
            "2. 選戰鬥腳本（full_auto 適合大多數情況）\n"
            "3. 設定次數，按「新增任務」\n"
            "4. 可以加多個任務、拖曳排序、插入休息時段\n"
            "5. 按「開始」，機器人會自動校準螢幕並依序執行\n"
            "\n"
            "【注意事項】\n"
            "• 執行中不要動滑鼠鍵盤（靜態視窗模式下不能移動遊戲視窗）\n"
            "• 出現驗證碼會播音效提醒，請手動輸入，完成後自動繼續\n"
            "• 長時間掛機有封號風險，建議搭配休息時段\n"
            "• 設定分頁可調整滑鼠模擬、執行間隔等進階選項"))

    def _append_log(self, line: str):
        self.log_view.appendPlainText(line)

    def _highlight_task(self, index: int):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            base = self._task_display(self.tasks[i]) if i < len(self.tasks) else item.text()
            if i == index:
                item.setBackground(QColor(200, 255, 200))
                item.setText(f"{base}  [{tr('執行中')}]")
            else:
                item.setBackground(QColor(255, 255, 255))
                item.setText(base)

    def _on_all_finished(self):
        self.start_button.setText(tr("開始"))
        self._append_log(tr("任務已全部完成"))
        self._refresh_task_list()
