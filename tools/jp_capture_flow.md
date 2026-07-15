# 日文版 UI 模板擷取流程

英文/日文版的版面**逐像素相同、只有文字不同**，所以不用人工一張張裁：
把「同一個畫面」在兩種語言下各截一張，工具會自動找出每個英文模板的位置、
從日文截圖裁同一塊、再判斷「這個元件有沒有文字差異」——有差異才產出日文模板，
純圖示（劍氣泡、箭頭、寶箱…）自動判定通用、跳過。

工具：`tools/jp_ui_capture.py`（用 `src-tauri\backend\.venv\Scripts\python.exe` 執行）。

## 事前條件

- 瀏覽器視窗**全程不能移動、不能改大小**（en/jp 兩輪截圖要逐像素對齊）
- 頁面縮放固定（跟平常跑 bot 一樣）
- 擷取期間每個畫面**捲動位置要一致**（首頁都停最上方、地圖都停進場預設視角）

## 步驟

1. **定視窗**（英文版、停首頁）：
   `python tools\jp_ui_capture.py window`
   → 全螢幕找 home 按鈕，把遊戲視窗 region 存進 `jp_capture/window.json`。

2. **英文輪**：走訪下列畫面，每到一個畫面截一張：
   `python tools\jp_ui_capture.py shot --lang en --label <畫面名>`

   | label | 畫面 | 主要收穫 |
   |---|---|---|
   | home | 首頁（停最上方） | home/menu/news/quest 底欄、Backup 捷徑 |
   | extras | 首頁 Extras 列展開 | extras、extras_arcarum |
   | mundus | 沙盒 Zone Mundus 地圖（進場預設視角） | attempts_left、The World 列 |
   | summon | 召喚石選擇頁 | choose_a_summon、auto pick、ok |
   | party | 隊伍確認頁 | party_selection_ok、set A/B |
   | battle | 戰鬥中 | attack、full/semi auto、跳過(skip) |
   | results | 結算畫面 | play_again、ok、close、pending battles |
   | backup | 救援列表（釘選頁） | reload_room、raid_list、釘選角標 |
   | settings | 遊戲設定頁（語言選項那頁） | 語言切換按鈕位置（給下一步用） |

   走訪可以人工點、也可以讓 bot 跑一場順便截（畫面出現時截即可，不影響 bot）。

3. **切日文**：遊戲內 Menu → Set Language → 日本語。
   （settings 截圖裡量好按鈕座標後，也可以用
   `python tools\jp_ui_capture.py click --at x,y` 盲點——日文版同位置。）

4. **日文輪**：走訪**同樣的畫面、同樣捲動位置**，
   `... shot --lang jp --label <同名>`。
   日文版看不懂沒關係：版面相同，照英文輪的位置點就行（可用 `click --at`）。

5. **比對產出**：
   `python tools\jp_ui_capture.py extract`
   → `jp_capture/staging/buttons_jp/`、`headers_jp/` ＋ `jp_capture/report.md`。
   工具會用圖示類哨兵（home_menu、attack、劍氣泡）檢查兩輪截圖有沒有對齊，
   歪了會警告（通常是捲動位置不同，重截那一張即可）。

6. **入庫**：過目 staging 的裁圖沒破圖後，複製到
   `src-tauri\images\buttons_jp\`、`src-tauri\images\headers_jp\`。
   後端 `gameLanguage=jp` 時自動優先讀這兩個資料夾，缺檔退回英文模板。

7. 遊戲切回英文（或直接在 GUI 設定「遊戲語言＝日文」開始用）。

## 注意

- **戰鬥/結算畫面**每次內容不同（敵人、掉落物），但按鈕位置固定——en/jp 兩輪
  不需要同一場戰鬥，只要都是「戰鬥中」「結算」畫面即可；對齊哨兵會把關。
- 之後遊戲改版換 UI，重跑同一套流程就能重抓。
- 沒截到的畫面模板不會產出（report 會少那幾條）；之後補截再跑 extract 即可，
  已入庫的不受影響。
