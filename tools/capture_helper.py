# -*- coding: utf-8 -*-
"""遊戲畫面熱鍵連拍器。

用途：在遊戲裡到處走，看到要收的畫面按一下 F8，截圖自動存到 captures/。
截出來的都是 PC 原生像素 PNG，可直接用 template_check.py 驗證後裁成模板。

用法（在 src-tauri 目錄下，用 backend venv）：
  backend\\.venv\\Scripts\\python.exe -X utf8 ..\\tools\\capture_helper.py

熱鍵：
  F8  — 截遊戲視窗（從 jp_capture/window.json 讀 region）
  F9  — 截全螢幕
  ESC — 結束

輸出：captures/cap_<時間戳>.png（放在倉庫根目錄）

注意：熱鍵功能依賴 keyboard 套件，需在非虛擬機的 Windows 桌面環境執行。
螢幕鎖定中無法實測熱鍵，待實測。
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(ROOT, "captures")
WINDOW_FILE = os.path.join(ROOT, "jp_capture", "window.json")


def _grab_region(region):
    """截指定區域，回傳 BGR ndarray（PC 原生像素）。"""
    import cv2
    import numpy as np
    import pyautogui
    shot = pyautogui.screenshot(region=tuple(region))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _grab_fullscreen():
    """截全螢幕，回傳 BGR ndarray。"""
    import cv2
    import numpy as np
    import pyautogui
    shot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _load_window():
    """讀 jp_capture/window.json；不存在就回傳 None。"""
    if not os.path.exists(WINDOW_FILE):
        return None
    with open(WINDOW_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(img, label="cap"):
    """存成 PNG，回傳檔名與尺寸字串。"""
    import cv2
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    # 避免同一秒連按多張重名
    suffix = 0
    while True:
        suf = f"_{suffix:02d}" if suffix > 0 else ""
        path = os.path.join(CAPTURE_DIR, f"{label}_{ts}{suf}.png")
        if not os.path.exists(path):
            break
        suffix += 1
    cv2.imwrite(path, img)
    h, w = img.shape[:2]
    return path, f"{w}x{h}"


def main():
    try:
        import keyboard
    except ImportError:
        print("[錯誤] 找不到 keyboard 套件。請在 venv 內執行：pip install keyboard")
        sys.exit(1)

    win = _load_window()
    if win is None:
        print("[提示] 找不到 jp_capture/window.json，F8 會退回全螢幕截圖。")
        print("       如需只截遊戲視窗，先跑：python ../tools/jp_ui_capture.py window")
    else:
        r = win["region"]
        print(f"[OK] 遊戲視窗 region={r}（scale={win.get('scale', '?')}）")

    print()
    print("=" * 50)
    print("  碧藍幻想截圖連拍器  — 操作說明")
    print("=" * 50)
    print("  F8  — 截遊戲視窗（存 captures/cap_時間戳.png）")
    print("  F9  — 截全螢幕（存 captures/full_時間戳.png）")
    print("  ESC — 結束程式")
    print("=" * 50)
    print(f"  輸出目錄：{CAPTURE_DIR}")
    print("  格式：PNG 無損，PC 原生像素")
    print("  （Telegram 傳圖請直接傳整個 captures/ 資料夾，")
    print("   切勿用手機相機拍螢幕——Telegram 會壓縮降採樣，")
    print("   模板比對分數會掉，無法直接裁成模板。）")
    print("=" * 50)
    print()
    print("[待機中] 在遊戲視窗停好畫面後按 F8 截圖...")

    stop_flag = {"stop": False}

    def on_f8():
        nonlocal win
        if win is not None:
            img = _grab_region(win["region"])
            label = "cap"
        else:
            img = _grab_fullscreen()
            label = "full"
        path, size = _save(img, label)
        rel = os.path.relpath(path, ROOT)
        print(f"[F8] 已存：{rel}  ({size})")

    def on_f9():
        img = _grab_fullscreen()
        path, size = _save(img, "full")
        rel = os.path.relpath(path, ROOT)
        print(f"[F9] 全螢幕已存：{rel}  ({size})")

    def on_esc():
        stop_flag["stop"] = True

    keyboard.add_hotkey("f8", on_f8, suppress=True)
    keyboard.add_hotkey("f9", on_f9, suppress=True)
    keyboard.add_hotkey("esc", on_esc, suppress=False)

    while not stop_flag["stop"]:
        time.sleep(0.1)

    keyboard.unhook_all_hotkeys()
    print("[結束] 截圖連拍器已關閉。")


if __name__ == "__main__":
    main()
