#!/usr/bin/env bash
# 啟動碧藍幻想自動化工具 GUI（macOS 雙擊版）
# 授權：chmod +x 啟動GUI.command（git 已設為可執行）

# 切換到本 script 所在目錄（即專案根目錄）
cd "$(dirname "$0")"

if [ -f "src-tauri/backend/.venv/bin/python" ]; then
    "src-tauri/backend/.venv/bin/python" -X utf8 gui/main.py
else
    echo "找不到虛擬環境，請先執行："
    echo "  python3.11 -m venv src-tauri/backend/.venv"
    echo "  src-tauri/backend/.venv/bin/pip install -r src-tauri/backend/requirements.txt"
    read -p "按 Enter 關閉..."
fi
