# -*- coding: utf-8 -*-
"""日文版 UI 模板擷取工具。

原理：碧藍幻想的英文/日文版「版面完全相同、只有文字不同」。所以：
1. 英文版走訪各關鍵畫面 → 每個畫面存一張視窗截圖（en/）
2. 遊戲切日文 → 走訪「同樣的畫面、同樣的捲動位置」→ 再存一批（jp/）
3. extract：把每個英文模板在 en 截圖上定位 → 從 jp 截圖裁「同一個位置」
   → 跟英文模板比對相似度：
   - 相似度高 ＝ 這個按鈕沒有文字差異（圖示類），日文版直接用英文模板，跳過
   - 相似度低 ＝ 文字不同，把裁下來的日文版存到 staging 供人工過目後入庫

用法（都在 src-tauri 目錄下執行，用 backend/.venv 的 python）：
  python ../tools/jp_ui_capture.py window                     # 偵測遊戲視窗（英文版停首頁時做一次）
  python ../tools/jp_ui_capture.py shot --lang en --label home
  python ../tools/jp_ui_capture.py shot --lang jp --label home
  python ../tools/jp_ui_capture.py click --at 320,1250        # 視窗內座標點擊（供盲操作日文版）
  python ../tools/jp_ui_capture.py extract                    # 離線比對產出 staging + 報告

輸出：jp_capture/staging/buttons_jp/*.jpg、headers_jp/*.jpg、report.md。
人工確認 staging 沒裁壞後，複製進 images/buttons_jp、images/headers_jp 即可
（後端 gameLanguage=jp 時會優先讀這兩個資料夾，缺檔自動退回英文版）。
"""
import argparse
import json
import os
import sys
import time

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_TAURI = os.path.join(ROOT, "src-tauri")
IMAGES = os.path.join(SRC_TAURI, "images")
CAPTURE_DIR = os.path.join(ROOT, "jp_capture")
WINDOW_FILE = os.path.join(CAPTURE_DIR, "window.json")

# 兩邊截圖若對不齊（頁面捲動位置不同），裁出來的日文模板會整個歪掉。
# 用這些「純圖示、無文字」的模板當對齊哨兵：在 en/jp 圖上都找得到而且
# 位置差超過容忍值就發警告。
ALIGN_SENTINELS = ["home_menu", "attack", "arcarum_sandbox_node_battle"]


def _grab(region):
    import pyautogui
    shot = pyautogui.screenshot(region = tuple(region))
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)


def _match(gray_img, gray_tmpl):
    """回傳 (最高分, 左上座標)。"""
    res = cv2.matchTemplate(gray_img, gray_tmpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return float(max_val), max_loc


def cmd_window(_args):
    """英文版停在首頁時執行：全螢幕找 home 按鈕定出遊戲視窗，存 window.json。
    視窗定義沿用後端的假設：瀏覽器視窗固定不動，之後 en/jp 兩輪都用同一個
    region 截圖，位置才會逐像素對齊。"""
    import pyautogui
    screen = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    tmpl = cv2.imread(os.path.join(IMAGES, "buttons", "home.jpg"), cv2.IMREAD_GRAYSCALE)

    best = (0.0, None, 1.0)
    for scale in np.arange(0.70, 1.35, 0.025):
        t = cv2.resize(tmpl, None, fx = scale, fy = scale, interpolation = cv2.INTER_AREA)
        val, loc = _match(gray, t)
        if val > best[0]:
            best = (val, loc, float(scale))
    val, loc, scale = best
    if val < 0.80 or loc is None:
        print(f"[FAIL] 全螢幕找不到 home 按鈕（最高 {val:.3f}）。遊戲要開英文版並停在首頁。")
        sys.exit(1)

    # 遊戲視窗：以 home 按鈕為錨，比照後端的寬度假設往上取整個直向畫面。
    tw = int(tmpl.shape[1] * scale)
    cx = loc[0] + tw // 2
    width = int(650 * scale)
    left = max(0, cx - width // 2)
    region = [left, 0, width, screen.shape[0]]
    os.makedirs(CAPTURE_DIR, exist_ok = True)
    with open(WINDOW_FILE, "w", encoding = "utf-8") as f:
        json.dump({"region": region, "scale": scale, "home_confidence": round(val, 3)}, f, indent = 2)
    print(f"[OK] 視窗 region={region} scale={scale:.3f}（home {val:.3f}），已存 {WINDOW_FILE}")


def _load_window():
    if not os.path.exists(WINDOW_FILE):
        print("[FAIL] 還沒偵測視窗，先跑：jp_ui_capture.py window（英文版停首頁）")
        sys.exit(1)
    with open(WINDOW_FILE, encoding = "utf-8") as f:
        return json.load(f)


def cmd_shot(args):
    win = _load_window()
    img = _grab(win["region"])
    out_dir = os.path.join(CAPTURE_DIR, args.lang)
    os.makedirs(out_dir, exist_ok = True)
    out = os.path.join(out_dir, f"{args.label}.png")
    cv2.imwrite(out, img)
    print(f"[OK] {out}")


def cmd_click(args):
    """視窗內座標點擊：日文版導航用（座標從英文版同畫面量好，版面相同）。"""
    import pyautogui
    win = _load_window()
    x, y = (int(v) for v in args.at.split(","))
    pyautogui.moveTo(win["region"][0] + x, win["region"][1] + y, duration = 0.2)
    pyautogui.click()
    time.sleep(float(args.wait))
    print(f"[OK] click 視窗內 ({x},{y})")


def _iter_templates():
    for folder in ("buttons", "headers"):
        d = os.path.join(IMAGES, folder)
        for name in sorted(os.listdir(d)):
            if name.lower().endswith(".jpg"):
                yield folder, name


def cmd_extract(args):
    en_dir = os.path.join(CAPTURE_DIR, "en")
    jp_dir = os.path.join(CAPTURE_DIR, "jp")
    staging = os.path.join(CAPTURE_DIR, "staging")
    labels = sorted(
        f[:-4] for f in os.listdir(en_dir) if f.endswith(".png")
        and os.path.exists(os.path.join(jp_dir, f)))
    if not labels:
        print("[FAIL] en/ 與 jp/ 沒有同名截圖可比對。")
        sys.exit(1)
    print(f"配對到 {len(labels)} 個畫面：{', '.join(labels)}")

    pairs = []
    for label in labels:
        en = cv2.imread(os.path.join(en_dir, label + ".png"), cv2.IMREAD_GRAYSCALE)
        jp = cv2.imread(os.path.join(jp_dir, label + ".png"), cv2.IMREAD_GRAYSCALE)
        if en.shape != jp.shape:
            print(f"[WARN] {label}: en/jp 尺寸不同，跳過。")
            continue
        # 對齊檢查：圖示類哨兵在兩張圖的位置要一致（頁面捲動不同就會歪）。
        for s in ALIGN_SENTINELS:
            t = cv2.imread(os.path.join(IMAGES, "buttons", s + ".jpg"), cv2.IMREAD_GRAYSCALE)
            ev, el = _match(en, t)
            jv, jl = _match(jp, t)
            if ev >= 0.85 and jv >= 0.85 and (abs(el[0] - jl[0]) > 4 or abs(el[1] - jl[1]) > 4):
                print(f"[WARN] {label}: 哨兵 {s} 位置 en{el} vs jp{jl}——兩張截圖沒對齊，結果不可信！")
        pairs.append((label, en, jp))

    found_threshold = float(args.found_threshold)
    same_threshold = float(args.same_threshold)
    report = ["# 日文模板擷取報告", "",
              f"門檻：英文定位 ≥ {found_threshold}，en/jp 相似 ≥ {same_threshold} 視為通用不裁。", ""]
    n_saved = n_common = 0
    for folder, name in _iter_templates():
        tmpl = cv2.imread(os.path.join(IMAGES, folder, name), cv2.IMREAD_GRAYSCALE)
        best = (0.0, None, None)  # (分數, label, 左上)
        for label, en, _ in pairs:
            if tmpl.shape[0] >= en.shape[0] or tmpl.shape[1] >= en.shape[1]:
                continue
            val, loc = _match(en, tmpl)
            if val > best[0]:
                best = (val, label, loc)
        val, label, loc = best
        if val < found_threshold or label is None:
            continue  # 這批畫面裡沒有這個元件，之後補畫面再跑。
        en, jp = next((e, j) for (l, e, j) in pairs if l == label)
        h, w = tmpl.shape
        x, y = loc
        crop = jp[y:y + h, x:x + w]
        # 相似度要跟「英文截圖同位置的裁片」比（不是跟模板比）：直接量測
        # 這塊區域在兩種語言下有沒有變，定位分數高低不會干擾判斷。
        en_crop = en[y:y + h, x:x + w]
        sim = 1.0 - float((cv2.absdiff(crop, en_crop) > 16).mean())
        if sim >= same_threshold:
            n_common += 1
            continue  # 圖示相同＝語言通用，日文版直接沿用英文模板。
        out_dir = os.path.join(staging, folder + "_jp")
        os.makedirs(out_dir, exist_ok = True)
        cv2.imwrite(os.path.join(out_dir, name), crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
        n_saved += 1
        report.append(f"- `{folder}/{name}` ← {label} @({x},{y}) 英文定位 {val:.3f}、en/jp 相似 {sim:.3f} → **已裁**")

    report += ["", f"共裁出 {n_saved} 個日文模板（另 {n_common} 個判定通用免裁）。",
               "過目 staging 內容沒裁壞後，複製進 images/buttons_jp、images/headers_jp。"]
    os.makedirs(staging, exist_ok = True)
    with open(os.path.join(CAPTURE_DIR, "report.md"), "w", encoding = "utf-8") as f:
        f.write("\n".join(report))
    print(f"[OK] 裁出 {n_saved} 個、通用 {n_common} 個。報告：jp_capture/report.md")


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest = "cmd", required = True)
    sub.add_parser("window")
    s = sub.add_parser("shot")
    s.add_argument("--lang", choices = ("en", "jp"), required = True)
    s.add_argument("--label", required = True)
    c = sub.add_parser("click")
    c.add_argument("--at", required = True, help = "視窗內座標 x,y")
    c.add_argument("--wait", default = "1.5")
    e = sub.add_parser("extract")
    e.add_argument("--found-threshold", default = "0.82")
    e.add_argument("--same-threshold", default = "0.90")
    args = p.parse_args()
    {"window": cmd_window, "shot": cmd_shot, "click": cmd_click, "extract": cmd_extract}[args.cmd](args)


if __name__ == "__main__":
    main()
