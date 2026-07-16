# macOS 安裝說明

> 本文件說明如何在 macOS 上安裝並啟動碧藍幻想自動化工具。
> Windows 使用者直接看 [README.md](../README.md) 即可。

---

## 前置作業

### 1. 安裝 Homebrew

若尚未安裝 Homebrew，在 Terminal 執行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Apple Silicon（M 系列晶片）安裝完後，依照終端提示把 `/opt/homebrew/bin` 加進 `PATH`：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. 安裝 Python 3.11

```bash
brew install python@3.11
```

安裝後確認版本：

```bash
python3.11 --version
```

> **注意**：Windows 的 `.venv` 是 Windows 二進位，**不能複製到 Mac 用**。
> 在 Mac 上要重新建立 venv（見下方步驟）。

### 3. Clone 專案

```bash
git clone <this repo>
cd granblue-automation-pyautogui
```

---

## 建立虛擬環境並安裝套件

### 建立 venv

```bash
python3.11 -m venv src-tauri/backend/.venv
```

### 安裝相依套件

```bash
src-tauri/backend/.venv/bin/pip install --upgrade pip
src-tauri/backend/.venv/bin/pip install -r src-tauri/backend/requirements.txt
```

#### PyTorch 版本說明

`requirements.txt` 已依平台自動選版：

| 機型 | 自動安裝版本 |
|------|-------------|
| Apple Silicon（M1/M2/M3/M4，arm64） | PyTorch 2.1+，支援 MPS（Metal Performance Shaders）加速 |
| Intel Mac（x86_64） | PyTorch 2.1–2.2.x（PyTorch 2.3 起停止提供 Intel macOS 版本） |

pip 會依照系統自動選正確版本，**不需要手動指定**。

若想在 Apple Silicon 啟用 MPS 加速（目前圖像辨識主要用 CPU，MPS 的效益有限），
不需要額外設定，PyTorch 在 M 系列晶片上預設可用 `.to("mps")`。

---

## macOS 必要系統權限

pyautogui 需要截圖與控制滑鼠／鍵盤，macOS 預設封鎖這類操作。
**沒有授權會導致截圖全黑、滑鼠無法移動。**

### 開放方式（需重複授權兩項）

1. 打開「系統設定」→「隱私權與安全性」
2. 左側清單選「**輔助使用**」，右側找 **Terminal**（或你用的終端 App，例如 iTerm2）
   → 打開開關
3. 左側清單選「**螢幕錄製**」，同樣找 **Terminal** → 打開開關

> 若是透過雙擊 `啟動GUI.command` 啟動，macOS 打開的是「Terminal」App，
> 要授權給「Terminal」；若改用 iTerm2 等第三方終端，改授權給對應 App。

授權後需要重啟 Terminal 才會生效。

---

## 啟動 GUI

在 macOS 有兩種啟動方式：

### 方式一：雙擊（Finder 點兩下）

在 Finder 找到專案根目錄的 **`啟動GUI.command`**，雙擊即可。

首次執行 macOS 可能顯示「無法驗證開發者」：
「系統設定」→「隱私權與安全性」→ 最下方找到該檔案 → 按「強制執行」。

### 方式二：Terminal 手動執行

```bash
cd /path/to/granblue-automation-pyautogui
src-tauri/backend/.venv/bin/python -X utf8 gui/main.py
```

---

## Retina / 高 DPI 螢幕

本程式已內建多尺度模板匹配與 Retina 比例偵測（0.5x–3.0x）。
建議：

- 遊戲瀏覽器視窗放在**主螢幕**
- 瀏覽器縮放維持 **100%**（Safari／Chrome 的「顯示比例」不要調）
- 若使用外接螢幕混合 DPI，遊戲視窗一定要放主螢幕（HiDPI 最高的那個）

---

## 已知限制與 macOS 特有注意事項

### ESC 緊急停止

`keyboard` 套件（全域快捷鍵）在 macOS 上需要輔助使用權限。
本程式已做容錯：若授權不足，啟動時靜默略過，**不會崩潰**，
但 ESC 全域停止鍵**不會有反應**。

要讓 ESC 正常動作，需確認 Terminal（或啟動用的 App）已取得「輔助使用」授權
（見上方「macOS 必要系統權限」）。

若仍無效，替代停法：按 GUI 視窗的「**停止**」按鈕，或在 Terminal 按 `Ctrl+C`。

### CAPTCHA 音效提醒

偵測到驗證碼時程式會播放音效等待手動處理。macOS 上音效播放依賴 `playsound3`，
需確認系統音量未靜音、且 Terminal 有「麥克風」以外的聲音輸出權限（通常預設可用）。

### `pywin32` 套件

`requirements.txt` 中 `pywin32` 限定 `sys_platform == "win32"`，Mac 不會安裝，
無需擔心。

### 螢幕休眠

macOS 預設閒置一段時間後螢幕進入休眠，休眠後截圖會失敗。
跑長時間佇列前請至「系統設定」→「螢幕保護程式」→「電源」，
將「顯示器關閉」設定為「永不」。

---

## 常見問題

**Q：pip install 途中出現 `error: externally-managed-environment`？**
A：確認你是在 venv 裡安裝（用 `src-tauri/backend/.venv/bin/pip`），不要用系統的 pip。

**Q：截圖全黑 / 滑鼠不動？**
A：缺少螢幕錄製或輔助使用授權，參閱上方「macOS 必要系統權限」重新授權並重啟 Terminal。

**Q：校準失敗？**
A：確認遊戲瀏覽器縮放 100%、底部 Home 鍵與返回鍵完整顯示在主螢幕。

**Q：雙擊 `啟動GUI.command` 沒反應？**
A：在 Terminal 手動執行看錯誤訊息；也可能需要先執行一次
`chmod +x 啟動GUI.command` 賦予執行權限。
