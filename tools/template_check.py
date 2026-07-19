# -*- coding: utf-8 -*-
"""模板驗證器——用法 A: probe（截圖 scale 判定）、用法 B: verify（模板品質交叉誤認）。

用途：在把截圖裁成模板前，先確認截圖是 PC 原生像素（scale=1.0 基準），
      並驗證新模板不會跟鄰近模板互相誤認。

用法（在 src-tauri 目錄下，用 backend venv）：

  # A：判斷截圖是否 scale=1.0 基準（可直接裁）
  backend\\.venv\\Scripts\\python.exe -X utf8 ..\\tools\\template_check.py probe <截圖.png>

  # B：驗證模板對多張截圖的匹配分數，並做交叉誤認檢查
  backend\\.venv\\Scripts\\python.exe -X utf8 ..\\tools\\template_check.py verify <模板.jpg> <截圖.png> [more.png...]
"""
import argparse
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, "src-tauri", "images")

# 用來 probe 的穩定錨點模板（純圖示類，無文字，scale 穩定）
# 挑選原則：圖案獨特、不受遊戲狀態影響、buttons/ 裡一定存在
PROBE_ANCHORS = [
    os.path.join(IMAGES, "buttons", "home_menu.jpg"),
    os.path.join(IMAGES, "buttons", "attack.jpg"),
    os.path.join(IMAGES, "buttons", "choose_a_summon.jpg"),
    os.path.join(IMAGES, "buttons", "home.jpg"),
]


def _match(gray_img: np.ndarray, gray_tmpl: np.ndarray):
    """回傳 (最高分, 左上座標)。"""
    if gray_tmpl.shape[0] >= gray_img.shape[0] or gray_tmpl.shape[1] >= gray_img.shape[1]:
        return 0.0, (0, 0)
    res = cv2.matchTemplate(gray_img, gray_tmpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return float(max_val), max_loc


def _load_gray(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[錯誤] 讀不到檔案：{path}")
        sys.exit(1)
    return img


def cmd_probe(args):
    """用穩定錨點模板對截圖測分數，判斷是否為 scale=1.0 原生像素。"""
    shot_path = args.screenshot
    if not os.path.exists(shot_path):
        print(f"[錯誤] 找不到截圖：{shot_path}")
        sys.exit(1)

    gray_shot = _load_gray(shot_path)
    h, w = gray_shot.shape
    print(f"\n截圖：{shot_path}  ({w}x{h})")
    print()
    print(f"{'錨點模板':<36}  {'最高分':>7}  {'位置':>14}  判定")
    print("-" * 75)

    scores = []
    for tmpl_path in PROBE_ANCHORS:
        name = os.path.basename(tmpl_path)
        if not os.path.exists(tmpl_path):
            print(f"  {name:<34}  {'(缺檔)':>7}")
            continue
        gray_tmpl = _load_gray(tmpl_path)
        score, loc = _match(gray_shot, gray_tmpl)
        scores.append(score)
        if score >= 0.90:
            verdict = "OK（原生像素，可裁）"
        elif score >= 0.75:
            verdict = "尚可（輕微壓縮，謹慎裁）"
        else:
            verdict = "警告：可能壓縮/縮放，不建議裁模板"
        print(f"  {name:<34}  {score:>7.3f}  {str(loc):>14}  {verdict}")

    print()
    if scores:
        hit = [s for s in scores if s >= 0.90]
        if not hit:
            # 所有錨點分數都低，很可能這張截圖根本找不到這些元件（不是主畫面）
            any_ok = [s for s in scores if s >= 0.75]
            if any_ok:
                print("[結論] 有錨點找到但分數偏低。截圖可能是壓縮/縮放圖，")
                print("       請用 PC 原生截圖（Win+Shift+S 或 capture_helper F8）。")
            else:
                print("[結論] 所有錨點都沒有在截圖中出現（分數 <0.75）。")
                print("       截圖可能不含首頁/戰鬥元件，或解析度/縮放差異過大。")
                print("       換一張含有底部選單列或攻擊按鈕的截圖來 probe。")
        else:
            print(f"[結論] {len(hit)}/{len(scores)} 個錨點命中（≥0.90）。")
            print("       截圖為 PC 原生像素（scale=1.0 基準），可直接裁模板。")
    print()


def _siblings(tmpl_path: str):
    """找同目錄下所有 .jpg/.png，排除自己。"""
    d = os.path.dirname(os.path.abspath(tmpl_path))
    name = os.path.basename(tmpl_path)
    result = []
    for f in sorted(os.listdir(d)):
        if f != name and f.lower().endswith((".jpg", ".png")):
            result.append(os.path.join(d, f))
    return result


def cmd_verify(args):
    """印出模板對各截圖的最高分，並對同目錄鄰近模板做交叉誤認檢查。"""
    tmpl_path = args.template
    shot_paths = args.screenshots

    if not os.path.exists(tmpl_path):
        print(f"[錯誤] 找不到模板：{tmpl_path}")
        sys.exit(1)
    for p in shot_paths:
        if not os.path.exists(p):
            print(f"[錯誤] 找不到截圖：{p}")
            sys.exit(1)

    gray_tmpl = _load_gray(tmpl_path)
    tmpl_name = os.path.basename(tmpl_path)
    th, tw = gray_tmpl.shape
    print(f"\n模板：{tmpl_path}  ({tw}x{th})")
    print()

    # --- 自我匹配分數 ---
    print("【模板 vs 截圖  最高分表】")
    print(f"  {'截圖':<40}  {'最高分':>7}  {'位置':>14}  判定")
    print("-" * 80)

    self_scores = []
    for sp in shot_paths:
        gray_shot = _load_gray(sp)
        score, loc = _match(gray_shot, gray_tmpl)
        self_scores.append((sp, score, loc))
        if score >= 0.95:
            verdict = "命中（建議門檻 0.95）"
        elif score >= 0.80:
            verdict = "偏低（調整 threshold？）"
        else:
            verdict = "未命中"
        sname = os.path.relpath(sp)
        print(f"  {sname:<40}  {score:>7.3f}  {str(loc):>14}  {verdict}")

    print()

    # --- 交叉誤認檢查 ---
    siblings = _siblings(tmpl_path)
    # 最多挑 10 個同目錄模板做交叉測試（全測太慢）
    if len(siblings) > 10:
        # 取名字字母最接近的 10 個（排序後取前後各 5）
        idx = sorted(range(len(siblings)),
                     key=lambda i: abs(ord(os.path.basename(siblings[i])[0]) -
                                       ord(tmpl_name[0])))
        siblings = [siblings[i] for i in idx[:10]]
        siblings.sort()

    if not siblings:
        print("[交叉誤認] 同目錄無其他模板，跳過交叉測試。")
    else:
        print(f"【交叉誤認檢查】（同目錄鄰近模板，共測 {len(siblings)} 個）")
        print(f"  {'鄰近模板':<36}  " + "  ".join(
            f"{os.path.basename(sp)[:12]:>12}" for _, sp, _ in
            [(0, s, 0) for s in shot_paths[:4]]
        ))
        shot_labels = [os.path.basename(sp)[:12] for sp in shot_paths[:4]]
        header2 = f"  {'鄰近模板':<36}  " + "  ".join(f"{l:>12}" for l in shot_labels)
        print(header2)
        print("-" * (40 + 15 * min(len(shot_paths), 4)))

        for sib_path in siblings:
            gray_sib = _load_gray(sib_path)
            sib_name = os.path.basename(sib_path)
            row = f"  {sib_name:<36}"
            for sp in shot_paths[:4]:
                gray_shot = _load_gray(sp)
                score, _ = _match(gray_shot, gray_sib)
                marker = " *" if score >= 0.85 else "  "
                row += f"  {score:>10.3f}{marker}"
            print(row)

        print()
        # 和自我分數相比
        if self_scores:
            min_self = min(s for _, s, _ in self_scores)
            print(f"  模板自身最低命中分數：{min_self:.3f}")
            print("  交叉誤認警告標準：分數 ≥ 0.85（以 * 標記）")
            high_cross = []
            for sib_path in siblings:
                gray_sib = _load_gray(sib_path)
                for sp in shot_paths[:4]:
                    gray_shot = _load_gray(sp)
                    score, _ = _match(gray_shot, gray_sib)
                    if score >= 0.85:
                        high_cross.append((os.path.basename(sib_path), os.path.basename(sp), score))
            if high_cross:
                print()
                print("  [警告] 以下鄰近模板在截圖上得分 ≥ 0.85，可能發生誤認：")
                for sname, shotname, sc in high_cross:
                    print(f"    {sname} vs {shotname}: {sc:.3f}")
            else:
                print("  [OK] 無鄰近模板得分 ≥ 0.85，交叉誤認風險低。")
    print()


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("probe", help="判斷截圖是否為 scale=1.0 原生像素")
    pa.add_argument("screenshot", help="要 probe 的截圖 .png 路徑")

    pv = sub.add_parser("verify", help="驗證模板對截圖的匹配分數＋交叉誤認")
    pv.add_argument("template", help="要驗證的模板（.jpg/.png）")
    pv.add_argument("screenshots", nargs="+", help="一或多張截圖 .png")

    args = p.parse_args()
    {"probe": cmd_probe, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    main()
