@echo off
rem 啟動碧藍幻想自動化工具 GUI（Windows）
cd /d %~dp0
if exist "src-tauri\backend\.venv\Scripts\python.exe" (
    "src-tauri\backend\.venv\Scripts\python.exe" -X utf8 gui\main.py
) else (
    python -X utf8 gui\main.py
)
pause
