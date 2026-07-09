# 碧藍幻想自動化工具 — 新版 GUI

以 PySide6 重寫的簡潔介面，取代舊的 `qt_gui/`（PyQt5）與 `src-tauri/controller.py`。

## 啟動

- Windows：雙擊 repo 根目錄的 `啟動GUI.bat`
- macOS / Linux：`./start_gui.sh`
- 手動：`python gui/main.py`（需先安裝 `src-tauri/backend/requirements.txt`）

## 架構

| 檔案 | 職責 |
|------|------|
| `main.py` | 入口，建立 QApplication |
| `main_window.py` | 主視窗：任務分頁（佇列＋日誌）與設定分頁 |
| `runner.py` | 任務調度器：依序執行任務、休息倒數、串流後端日誌 |
| `settings_schema.py` | 產生後端 settings JSON（schema 與 backend/utils/settings.py 對應）|
| `i18n.py` | 中英文切換（中文原文當 key，偏好存 `data/ui_config.json`）|
| `data/` | 遊戲模式、召喚石、模式名稱翻譯資料 |

## 執行流程

1. GUI 把每個任務組成完整設定 dict（`build_settings`）
2. `TaskRunner` 逐一寫到 `src-tauri/backend/farm_queue/settingsN.json`
3. 以 `python -X utf8 backend/main.py <file>` 執行（工作目錄 = `src-tauri/`，
   模板圖路徑 `images/` 以此為基準）
4. 「休息」任務用 QTimer 倒數，不會卡住介面

## 新增功能時

- 新選項：`main_window.py` 加控件 → `collect_options()` 加欄位 →
  `settings_schema.py` 對應到後端欄位 → `i18n.py` 補英文翻譯
- 新遊戲模式：編輯 `data/data_zhcn.json` 與 `data/translate.json`
