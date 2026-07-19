# 素材截圖 SOP（抓新模板用）

模板必須是 PC 原生像素（scale=1.0 基準），否則比對分數會掉、裁出來不能用。

## 一、PC 原生截圖的三種來源

### 來源 1：capture_helper 熱鍵（推薦）

```
cd src-tauri
backend\.venv\Scripts\python.exe -X utf8 ..\tools\capture_helper.py
```

啟動後：
- **F8** — 截遊戲視窗（優先讀 `jp_capture/window.json`，沒有就全螢幕）
- **F9** — 截全螢幕
- **ESC** — 結束

截圖存到倉庫根目錄的 `captures/cap_時間戳.png`，PNG 無損。

工作流：打開工具，在遊戲裡走到要收的畫面，按 F8，繼續走下一個畫面。
最後把整個 `captures/` 資料夾壓縮後傳給 Claude（或直接在本機跑驗證工具）。

### 來源 2：Win+PrtSc 自動存檔

Windows 預設：Win+PrtSc 截全螢幕，自動存到 `C:\Users\你\Pictures\Screenshots\`。
PNG 格式，原生像素，可直接用。

### 來源 3：bot 執行時的 debug 截圖

bot 跑起來後，失敗時會把當下截圖存到 `src-tauri/backend/log/debug_*.png`（依設定而定）。
這些都是原生像素，遇到模板抓不到時可直接從這裡裁補。

---

## 二、為什麼 Telegram 傳來的照片不能用

Telegram 手機 App 傳圖會自動壓縮並降採樣（實測 scale 約 0.67），
匹配錨點模板的分數會掉到 0.75 以下，裁出來的尺寸比原始模板小，
放入 `images/buttons/` 後比對時需要不同縮放、不穩定。

**結論：不要用 Telegram「傳送照片」功能傳截圖。**

如果非要用 Telegram 傳檔，選「傳送為檔案」（File / Document 選項）——
這樣不壓縮，原始 PNG 保留。或直接上傳整個 `captures/` 資料夾壓縮包。

---

## 三、傳圖給 Claude 的規則

1. **傳整個視窗**，不要預先裁圖——讓 Claude 看到周圍脈絡，裁準位置
2. **PNG 格式**，不要轉 JPG（JPG 有損壓縮，邊緣模糊）
3. **不要縮放**——原始尺寸直接傳
4. 一次可以傳多張（把 `captures/` 整包壓縮後傳）

---

## 四、截到截圖之後——驗證流程

用 `template_check.py` 確認截圖是原生像素、新模板不會誤認：

```
cd src-tauri
# 步驟 1：確認截圖是原生像素（scale=1.0）
backend\.venv\Scripts\python.exe -X utf8 ..\tools\template_check.py probe ..\captures\cap_xxx.png

# 步驟 2：驗證裁出來的新模板，對截圖命中且不誤認
backend\.venv\Scripts\python.exe -X utf8 ..\tools\template_check.py verify ..\src-tauri\images\buttons\新模板.jpg ..\captures\cap_xxx.png ..\captures\cap_yyy.png
```

- probe 分數 ≥ 0.90 → 截圖為原生像素，可裁
- verify 自身分數 ≥ 0.95、交叉模板分數 < 0.85 → 模板品質合格

---

## 五、模板入庫

驗證通過後，將裁好的 `.jpg` 放入：
- `src-tauri/images/buttons/` — 英文版通用按鈕
- `src-tauri/images/buttons_jp/` — 日文版獨有（同名時覆蓋英文版）
- `src-tauri/images/headers/` 或 `headers_jp/` — 頁面標頭模板

JPG 存檔品質建議 95（`cv2.IMWRITE_JPEG_QUALITY, 95`）。
