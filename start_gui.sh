#!/bin/sh
# 啟動碧藍幻想自動化工具 GUI（macOS / Linux）
cd "$(dirname "$0")"
if [ -x "src-tauri/backend/.venv/bin/python" ]; then
    exec src-tauri/backend/.venv/bin/python -X utf8 gui/main.py
else
    exec python3 -X utf8 gui/main.py
fi
