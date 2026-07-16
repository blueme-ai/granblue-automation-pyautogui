# -*- coding: utf-8 -*-
"""Mundus 12 隻定點怪單刷佇列驅動器（跑在 src-tauri 目錄下）。

用法：backend/.venv/Scripts/python.exe -X utf8 backend/run_mundus_queue.py [--rounds 2] [--lang jp] [--bosses "A,B,C"]
每隻怪各跑一個 main.py 行程（itemAmount=rounds，一個行程內連刷 N 場），
單隻失敗不中斷佇列，最後印出總結表。
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))          # backend/
SRC_TAURI = os.path.dirname(HERE)                           # src-tauri/
PYTHON = os.path.join(HERE, ".venv", "Scripts", "python.exe")
BASE_SETTINGS = os.path.join(HERE, "jp_sweep_test.json")

DEFAULT_BOSSES = [
    "Tide Caller", "Parasite Steve", "Earth-Shattering Fire Demon",
    "Elephant Stomping Ground", "High-Voltage Rock", "Goddess of the Wild Hunt",
    "Love Meeee", "Hotheaded Pincers", "Princess of the Horde",
    "Proud War Princess of Dragons", "Dragon in Glittering Green", "Winged Demon Cat",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type = int, default = 2)
    ap.add_argument("--lang", default = "jp")
    ap.add_argument("--bosses", default = None, help = "逗號分隔；預設 12 隻定點怪")
    ap.add_argument("--timeout", type = int, default = 25, help = "單隻逾時（分鐘），逾時 taskkill 整棵樹")
    args = ap.parse_args()

    bosses = [b.strip() for b in args.bosses.split(",")] if args.bosses else DEFAULT_BOSSES
    base = json.load(open(BASE_SETTINGS, encoding = "utf-8"))
    results = []

    for i, boss in enumerate(bosses, 1):
        cfg = json.loads(json.dumps(base))
        cfg["game"]["mission"] = boss
        cfg["game"]["map"] = "Zone Mundus"
        cfg["game"]["itemAmount"] = args.rounds
        cfg["game"]["gameLanguage"] = args.lang
        cfg_path = os.path.join(HERE, "queue_current.json")
        json.dump(cfg, open(cfg_path, "w", encoding = "utf-8"), indent = 2)

        print(f"\n===== [{i}/{len(bosses)}] {boss} x{args.rounds} =====", flush = True)
        t0 = time.time()
        # 逾時保護：單隻超時就 taskkill 整棵樹（multiprocessing 子行程握滑鼠），
        # 避免像 jp sweep 首測那樣「掃不到→無限重試」空轉整晚。
        popen = subprocess.Popen([PYTHON, "-X", "utf8", os.path.join(HERE, "main.py"), cfg_path],
                                 cwd = SRC_TAURI, stdout = subprocess.PIPE, stderr = subprocess.STDOUT,
                                 text = True, encoding = "utf-8", errors = "replace")
        try:
            stdout, _ = popen.communicate(timeout = args.timeout * 60)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/PID", str(popen.pid), "/T", "/F"], capture_output = True)
            try:
                stdout, _ = popen.communicate(timeout = 15)
            except Exception:
                stdout = ""
            stdout = (stdout or "") + f"\n[QUEUE] TIMEOUT {args.timeout}min，已 taskkill 整棵樹。"
        class _P:  # 統一介面
            returncode = popen.returncode if popen.returncode is not None else 124
        proc = _P()
        proc.stdout, proc.stderr = stdout, ""
        dt = int(time.time() - t0)
        out = (proc.stdout or "") + (proc.stderr or "")
        farmed = out.count("Amount of items farmed") or None
        ok = proc.returncode == 0
        # 從輸出找戰鬥完成跡象
        wins = out.count("Loot Collected") + out.count("EXP Gained")
        status = "OK" if ok else f"EXIT {proc.returncode}"
        err = ""
        if "RuntimeError" in out or "Exception" in out:
            for line in out.splitlines():
                if "RuntimeError" in line or "ArcarumSandboxException" in line:
                    err = line.strip()[:160]
                    break
        results.append((boss, status, dt, err))
        print(f"  -> {status}  {dt}s  {err}", flush = True)

    print("\n===== 佇列總結 =====", flush = True)
    for boss, status, dt, err in results:
        print(f"{status:8s} {dt:5d}s  {boss}  {err}", flush = True)
    fails = [r for r in results if r[1] != "OK"]
    print(f"\n{len(results) - len(fails)}/{len(results)} 成功", flush = True)


if __name__ == "__main__":
    main()
