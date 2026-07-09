# -*- coding: utf-8 -*-
"""任務調度器：依序執行任務佇列（取代舊版 controller.py）。

- 每個任務寫出一份 settings JSON，交給 `python backend/main.py <file>` 執行
- 休息任務用 QTimer 倒數，不阻塞介面
- 後端輸出以 UTF-8 逐行讀取，透過 signal 丟給日誌視窗
"""
import json
import os
import sys

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from i18n import tr

BREAK_MODE = "Take a break"


class TaskRunner(QObject):
    log_line = Signal(str)          # 一行日誌
    task_started = Signal(int)      # 任務 index（0-based）
    task_finished = Signal(int, int)  # 任務 index、exit code
    all_finished = Signal()         # 佇列跑完（或被停止）

    def __init__(self, work_dir: str, parent = None):
        """
        Args:
            work_dir: src-tauri 目錄。後端的模板圖路徑（images/）與
                      settings 路徑都以這個目錄為工作目錄。
        """
        super().__init__(parent)
        self.work_dir = work_dir
        self.queue_dir = os.path.join(work_dir, "backend", "farm_queue")
        self._tasks: list[dict] = []
        self._index = -1
        self._process: QProcess | None = None
        self._break_timer: QTimer | None = None
        self._stopped = False

    def is_running(self) -> bool:
        return self._index >= 0

    def start(self, task_settings: list[dict]):
        """開始執行任務佇列。

        Args:
            task_settings: 每個元素是完整的後端設定 dict（build_settings 的輸出）。
        """
        backend_main = os.path.join(self.work_dir, "backend", "main.py")
        if not os.path.exists(backend_main):
            self.log_line.emit(tr("找不到後端程式（backend/main.py），請確認安裝完整。"))
            self.all_finished.emit()
            return

        os.makedirs(self.queue_dir, exist_ok = True)
        self._tasks = task_settings
        self._index = -1
        self._stopped = False
        self.log_line.emit(tr("開始執行任務佇列，共 {n} 個任務", n = len(task_settings)))
        self._next()

    def stop(self):
        """停止目前任務並清空佇列。"""
        self._stopped = True
        if self._break_timer is not None:
            self._break_timer.stop()
            self._break_timer = None
        if self._process is not None:
            self._process.kill()
        else:
            self._finish_all()

    def _next(self):
        self._index += 1
        if self._stopped or self._index >= len(self._tasks):
            self._finish_all()
            return

        settings = self._tasks[self._index]
        mode = settings["game"]["farmingMode"]
        self.task_started.emit(self._index)

        if mode == BREAK_MODE:
            minutes = int(settings["game"]["itemAmount"])
            self.log_line.emit(tr("休息 {m} 分鐘…", m = minutes))
            self._break_timer = QTimer(self)
            self._break_timer.setSingleShot(True)
            self._break_timer.timeout.connect(self._on_break_done)
            self._break_timer.start(minutes * 60 * 1000)
            return

        settings_file = os.path.join(self.queue_dir, f"settings{self._index + 1}.json")
        with open(settings_file, "w", encoding = "utf-8") as f:
            json.dump(settings, f, ensure_ascii = False, indent = 4)

        self.log_line.emit(tr("第 {i} 個任務開始：{name}", i = self._index + 1, name = mode))

        self._process = QProcess(self)
        self._process.setWorkingDirectory(self.work_dir)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_output)
        self._process.finished.connect(self._on_process_finished)
        self._process.start(sys.executable, ["-X", "utf8", os.path.join("backend", "main.py"), settings_file])

    def _on_break_done(self):
        self._break_timer = None
        self.task_finished.emit(self._index, 0)
        self._next()

    def _on_output(self):
        if self._process is None:
            return
        data = bytes(self._process.readAllStandardOutput())
        text = data.decode("utf-8", errors = "replace")
        for line in text.splitlines():
            if line.strip():
                self.log_line.emit(line.rstrip())

    def _on_process_finished(self, exit_code: int, _status):
        self._process = None
        self.log_line.emit(tr("第 {i} 個任務結束（代碼 {code}）", i = self._index + 1, code = exit_code))
        self.task_finished.emit(self._index, exit_code)
        self._next()

    def _finish_all(self):
        self._index = -1
        self._tasks = []
        self._process = None
        self.all_finished.emit()
