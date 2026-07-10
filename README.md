# 碧藍幻想自動化工具（Granblue Automation）

基於圖像模板匹配（OpenCV + PyAutoGUI）的碧藍幻想（GBF）農場機器人。
本倉庫是 [steve1316/granblue-automation-pyautogui](https://github.com/steve1316/granblue-automation-pyautogui)
的改造版：重寫了 GUI（PySide6，中英文介面）、支援任意螢幕解析度／縮放、
移除對特定瀏覽器書籤與外部找房服務的依賴。

> 原版英文說明（戰鬥腳本語法等）見 [README_original_en.md](README_original_en.md)。

## 特色

- **任意解析度**：校準時自動偵測遊戲畫面相對模板的縮放比例（0.5x–3.0x），
  1080p／2K／4K、Windows DPI 縮放、mac Retina 都可直接用，換電腦不用改任何設定
- **內建任務佇列**：GUI 可排多個任務依序執行，支援拖曳排序、插入休息時段
- **免書籤、免外部服務**：全部用圖像辨識從遊戲首頁導航；多人 Raid 用遊戲內建的
  「釘選」介面，不需要 Twitter/找房網站
- **CAPTCHA 提醒**：偵測到驗證碼時播放音效等你手動處理（最多 10 分鐘），完成後自動繼續
- **遊戲語言**：英文版完整支援；日文版機制已就緒（見下方「日文版支援」）

## 環境需求

- Python 3.11+（Windows / mac 皆可）
- 瀏覽器開著碧藍幻想網頁版，遊戲視窗縮放 100%，畫面上要看得到底部的 Home 按鈕
- 建議把遊戲視窗放在主螢幕；執行中不要移動遊戲視窗（預設靜態視窗校準）

## 安裝

```bash
git clone <this repo>
cd granblue-automation-pyautogui
python -m venv src-tauri/backend/.venv
# Windows
src-tauri/backend/.venv/Scripts/pip install -r src-tauri/backend/requirements.txt
src-tauri/backend/.venv/Scripts/pip install PySide6
```

## 使用步驟

1. **啟動 GUI**：Windows 直接雙擊根目錄的「啟動GUI.bat」
   （或 `python -X utf8 gui/main.py`）
2. **開好遊戲**：瀏覽器登入 GBF，停在任何畫面都可以（機器人會自己回首頁），
   確認畫面底部的 Home 鍵沒被遮住
3. **建任務**：在 GUI 選「模式 → 關卡 → 目標道具 → 戰鬥腳本 → 次數」按「新增任務」；
   可以連續加多個任務、插入「休息」
4. **按「開始」**：機器人會先做視窗校準（自動偵測縮放比例），然後依序執行任務佇列
5. 執行 log 即時顯示在 GUI 下方；要中斷按「停止」，或隨時按全域快捷鍵
   **Ctrl+Alt+Q** 緊急停止（機器人執行中會搶滑鼠，用快捷鍵不需要搶回游標）

### 多人 Raid（釘選模式）使用方式

遊戲內建了 Raid 釘選功能（救援列表最多可釘選 4 個 Raid）：

1. 先在遊戲裡把想打的 Raid 釘選好（最多 4 個釘選位）
2. GUI 模式選「多人」，關卡選「釘選1」～「釘選4」（對應 1st～4th 釘選位）
3. 機器人流程：首頁 → Backup 捷徑（Quest 鈕上方）→ Finder 釘選列表 →
   點指定釘選位 → 檢查每場 HP 條（可設「HP 低於 % 時不進」）→ 加入 → 開打
4. 建議遊戲設定開「自動選擇召喚」，加入後會直接跳到隊伍確認、零點擊開打
5. 「Raid 選項」中可設定自動退出時間、HP 門檻等

### 戰鬥腳本

放在 `src-tauri/scripts/*.txt`，語法與原版相同（`full_auto.txt` 為全自動）。
詳細語法見原版說明 [README_original_en.md](README_original_en.md)。

## 模式支援狀態

| 模式 | 狀態 | 說明 |
|------|------|------|
| 任務（Quest） | ✅ | 世界地圖導航，26 個關卡 |
| 特殊（Special） | ✅ | 含次元光環偵測 |
| 共斗（Coop） | ✅ | 19 個關卡 |
| 多人（Raid） | ✅ | 遊戲內釘選介面，釘選 1–4；分頁切換模板待截圖補齊 |
| 兌換／戰貨活動（Event） | ✅ | 支援夢魘偵測 |
| 四象降臨 | ✅ | 含神仙、EX+ |
| 古戰場（Guild Wars） | ✅ | EX～NM200 |
| 公會戰（Dread Barrage） | ✅ | 1–5 星 |
| 勇氣之地（Proving Grounds） | ✅ | |
| 六道（Xeno Clash） | ✅ | |
| 轉世（Arcarum） | ✅ | |
| 轉世沙盒（Arcarum Sandbox） | ✅ | 69 個關卡，已實測 |
| 通常（Generic） | ✅ | 自己先手動進一場戰鬥，之後機器人用「再玩一次」重複刷 |
| 快速活動 / Side Story | ⚠️ 暫不可用 | 舊實作依賴瀏覽器書籤快捷鍵，待重做 |

## 日文版支援

機制已就緒：GUI 設定「遊戲語言 → 日本語」後，圖像比對會優先使用
`src-tauri/images/buttons_jp/`、`headers_jp/` 下的模板，缺圖自動退回英文版模板。

純圖示按鈕跨語言通用；**含文字的按鈕需要日文版截圖裁模板**，
製作方式見 [src-tauri/images/buttons_jp/README.md](src-tauri/images/buttons_jp/README.md)。

## 常見問題

- **校準失敗**：確認遊戲視窗縮放 100%、底部 Home 鍵與返回鍵可見
- **點擊位置偏移**：把該次執行的 log 保存下來回報（含偵測到的縮放比例）
- **一直回首頁重試**：通常是該模式導航路上的某個按鈕模板匹配失敗，回報 log
- **驗證碼**：聽到提示音後手動完成驗證，機器人會自動繼續

## 免責聲明

僅供圖像辨識自動化的教育研究用途。使用自動化工具違反遊戲服務條款，
帳號風險自負。建議在非主力機器或虛擬機上執行。

---

**維護注意**：功能有修改時請同步更新本文件（模式支援表、使用步驟）。
