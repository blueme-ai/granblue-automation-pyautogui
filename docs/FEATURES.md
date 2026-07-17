# 全功能與執行流程說明

> 本文件說明 Granblue Automation（custom_dev 分支）的完整執行流程、各模式現況，  
> 以及可供用戶決策的死碼／優化清單。

---

## 一、整體執行流程

```
用戶雙擊「啟動GUI.bat」
        │
        ▼
[GUI 層] gui/main.py（PySide6）
 ├─ 任務分頁：選模式 → 關卡 → 目標道具 → 腳本 → 次數 → 新增任務
 ├─ 設定分頁：各種執行選項（自動存檔 settings.json）
 └─ 「開始」按鈕
        │
        ▼
[任務佇列] GUI 內部 TaskRunner（QProcess）
 依序取出佇列中每個任務，組成 settings.json
        │
        ▼
[子行程啟動] python -X utf8 backend/main.py <settings.json>
 main.py → MainDriver.start_bot()
 → multiprocessing.Process( target=_run_bot )
        │
        ▼
[初始化] Game.__init__( set_path )
 ├─ Settings.update(set_path)  ── 讀取 settings.json，填入 Settings 類別變數
 └─ （重複 import 所有模式模組，Python 幾乎無成本，歷史遺留做法）
        │
        ▼
[視窗校準] Game.start_farming_mode() 開頭呼叫
 Game._calibrate_game_window()
 ├─ ImageUtils.determine_template_scale()
 │   用 home 按鈕模板在 0.5x～3.0x 多尺度掃描，找出最佳縮放比例
 │   → 存入 ImageUtils._template_scale（後續所有座標偏移都乘這個值）
 ├─ ImageUtils.find_button("home")      ── 以 Home 鍵為定位錨點
 └─ ImageUtils.find_button("home_back") ── 取得視窗邊界
        │
        ▼
[農場主迴圈] while item_amount_farmed < item_amount_to_farm
 ├─ 根據 Settings.farming_mode 分派到對應模式（見下節）
 ├─ 每次完成後計數、呼叫 Game._delay_between_runs()
 ├─ 計時進行隨機小休息（33–35 分鐘）/ 大休息（3–4 小時一次，1–2 小時）
 └─ 超過 40,000 秒（約 11 小時）後自動結束
        │
        ▼
[模式分派] game.py ~line 1185（farmingMode 字串對應類別）
 Quest / Special / Coop / Raid / Event / Event Quick / Rise of the Beasts /
 Guild Wars / Dread Barrage / Side Story / Proving Grounds / Xeno Clash /
 Exo / Arcarum / Arcarum Sandbox / Generic / Fate
        │
        ▼
[各模式 _navigate()]
 圖像導航：go_back_home → find_and_click_button(各頁面按鈕) → 確認頁面
        │
        ▼
[準備開戰] Game.select_summon() + Game.find_party_and_start_mission()
        │
        ▼
[CombatMode.start_combat_mode()]
 ├─ 快速召喚（enable_auto_quick_summon，全部路徑均觸發，5 秒防重複）
 ├─ Full Auto（腳本含 enablefullauto 指令）
 ├─ Semi Auto（enablesemiauto）
 ├─ 腳本模式（逐行解析 .txt，支援技能/召喚/治療/跳轉等指令）
 └─ 偵測：party wipe / 撤退 / 戰鬥超時 / 驗證碼（playsound 提示音）
        │
        ▼
[結算] Game.collect_loot()
 ├─ 截圖辨識道具掉落 → Settings.item_amount_farmed += n
 ├─ Nightmare 偵測（特殊/活動/四象/六道）→ 可選擇啟動 Nightmare 腳本
 └─ 按「Play Again」繼續下一輪，或回首頁準備下一輪導航
        │
        ▼
[結束或繼續] 達到次數上限 → 回報佇列完成，GUI 執行下一個任務
```

---

## 二、模式逐一盤點

以下「17 個模式鍵」對應 `gui/data/data_zhcn.json` 的頂層鍵名（括號內為 Settings.farming_mode 的實際字串值）。

---

### 1. 轉世沙盒（Arcarum Sandbox）

- **Settings.farming_mode**：`"Arcarum Sandbox"`
- **對應檔案**：`bot/game_modes/_arcarum_sandbox.py`（live）；`arcarum_sandbox.py` 為死碼（Alt+4 書籤版，已棄用）
- **功能**：導航至 Replicard Sandbox 各 Zone，依照 _mission_data 座標字典定位節點，支援全 9 個 Zone、69 個關卡，含黃金寶箱偵測與 Mimic 自動戰鬥
- **導航方式**：原版圖像導航（`_arcarum_sandbox.py`）——由首頁 Extras 選單進入，座標字典算出節點偏移後點擊
- **模板風險**：九個 Zone 選區橫幅已補日文版模板；節點座標為像素偏移，會乘 `_template_scale`，多解析度適配
- **建議**：✅ 保留（live，已實測 69 個關卡）

---

### 2. 轉世（Arcarum）

- **Settings.farming_mode**：`"Arcarum"`
- **對應檔案**：`bot/game_modes/arcarum.py`（live）
- **功能**：帶隊跑轉世遠征圖（The Arcarum）各路線（Staves/Swords/Cups/Coins），支援 Extreme 難度、boss 偵測、遠征完結自動重開
- **導航方式**：原版圖像導航——從首頁 Extras 選單進入；舊版 arcarum_banner 圖已替換為 navigate_to_arcarum_extras()
- **模板風險**：`arcarum_extreme` 等按鈕模板為 2022 年舊圖，若遊戲改版 UI 可能需補截
- **建議**：✅ 保留

---

### 3. 任務（Quest）

- **Settings.farming_mode**：`"Quest"`
- **對應檔案**：`bot/game_modes/quest.py`（live）
- **功能**：世界地圖導航，支援 Phantagrande / Nalhegrande / Oarlyegrande 三個天空域，26 個關卡；含 Dimensional Halo 偵測（可選開啟 Nightmare 腳本）
- **導航方式**：圖像導航——go_back_home → Quest → 天空域圖像翻頁（world_left/right_arrow）→ 島嶼選擇按鈕
- **模板風險**：各島嶼按鈕為 2022 年舊圖，若新天空域關卡不在清單內無法選用
- **建議**：✅ 保留

---

### 4. 特殊（Special）

- **Settings.farming_mode**：`"Special"`
- **對應檔案**：`bot/game_modes/special.py`（live，已還原自 harjeb commit 6d1366a 的圖像導航版）
- **功能**：Quest → Special → 依章節/難度選關；支援 Angel Halo、碎片關卡、Dimensional Halo Nightmare 偵測
- **導航方式**：圖像導航（已還原原版，不再用 Alt 書籤）
- **模板風險**：Special 頁各章節按鈕均為 2022 年截圖，若官方重新排版可能失效
- **建議**：✅ 保留

---

### 5. 共鬥（Coop）

- **Settings.farming_mode**：`"Coop"`
- **對應檔案**：`bot/game_modes/coop.py`（live）
- **功能**：主持共鬥房、選難度（Normal/Hard/EX1~EX4/Final）、等待其他玩家加入或自動開戰，19 個關卡
- **導航方式**：圖像導航——home_menu → coop → scroll → host_quest 位置偏移
- **模板風險**：coop_host_quest 等按鈕為 2022 年模板，GBF 若改版共鬥 UI 需補截
- **建議**：✅ 保留

---

### 6. 多人（Raid）

- **Settings.farming_mode**：`"Raid"`
- **對應檔案**：`bot/game_modes/raid2.py`（live，import 成 `Raid`）；`raid.py` 為死碼（依賴 EririRoomFinder 外部找房服務）
- **功能**：遊戲內釘選介面（釘選 1–4），首頁 Backup 捷徑快速進入救援列表，點指定釘選位，HP 條門檻判定，加入後開打
- **導航方式**：圖像導航——掃 raid_backup*.jpg 多變體 → 釘選位角標 raid_pin_N → 釘選縮圖偏移點擊
- **模板風險**：Backup 捷徑圖示有多種外觀（紅菱形、黃緞帶等），已設計自動掃 glob 擴充；釘選分頁切換模板仍待補齊
- **建議**：✅ 保留

---

### 7. 兌換活動（Event）

- **Settings.farming_mode**：`"Event"` 或 `"Event (Token Drawboxes)"`
- **對應檔案**：`bot/game_modes/event.py`（live）
- **功能**：home_menu → 第一個（或第二個）Event Banner → 選難度，支援 Normal/Hard/VH/Extreme/EX2 各關卡；含 Event Nightmare 偵測（可選跳過或打）
- **導航方式**：圖像導航——event_banner / event_banner_blue 辨識，依 `Settings.first_event` 決定點第幾個 Banner
- **模板風險**：event_banner 為泛用樣板，信心值 0.7 降低誤判，實際上每次活動 Banner 外觀不同，模板匹配仍有失敗風險
- **建議**：✅ 保留（但 Event Banner 匹配是長期高風險點，可考慮改用位置固定點擊）

---

### 8. 戰貨活動（Event Token Drawboxes）

- 共用 `Event` 類別，`farming_mode` 字串為 `"Event (Token Drawboxes)"`，導航邏輯相同，只是關卡清單不同。見上條。
- **建議**：✅ 保留（與 Event 合體，無獨立檔案）

---

### 9. 快速活動（Event Quick）

- **Settings.farming_mode**：`"Event Quick"`
- **對應檔案**：`bot/game_modes/event_quick.py`（live import，但邏輯為死碼）
- **功能**（原設計）：快速跳到活動頁面重複刷
- **導航方式**：`pyautogui.keyDown('alt') + press('5')` / `press('1')`——依賴 harjeb 自製的瀏覽器書籤快捷鍵
- **現況**：在任何標準環境都不可用；GUI 已標注「待重做，暫不可用」；start() 僅發出 Alt+1 就結束，完全無法到達戰鬥頁面
- **建議**：❌ 可刪（或改寫成圖像導航版 Event Quick，目前對用戶零價值）

---

### 10. 四象降臨（Rise of the Beasts）

- **Settings.farming_mode**：`"Rise of the Beasts"`
- **對應檔案**：`bot/game_modes/_rotb.py`（live）；`rotb.py` 為死碼（Alt+N 書籤版）
- **功能**：home_menu → 活動 Banner → 四象關卡選擇；支援 Nightmare（Extreme+）偵測，也有 default fight 路徑（點 play_round_button 第 4 個）
- **導航方式**：圖像導航（`_rotb.py` 版本）——活動 Banner 辨識進入，然後翻找難度按鈕
- **模板風險**：`_rotb.py` 與 `rotb.py` 程式碼幾乎完全相同（唯一差異是 `_rotb.py` 無 import pyautogui Alt 鍵操作），四象活動限期開放，模板仍適用
- **建議**：✅ 保留（`_rotb.py`）；`rotb.py` 死碼建議刪除

---

### 11. 古戰場（Guild Wars）

- **Settings.farming_mode**：`"Guild Wars"`
- **對應檔案**：`bot/game_modes/guild_wars.py`（live）
- **功能**：home_menu → 活動 Banner → 古戰場頁面；Extreme/Extreme+ 打肉（meat）；NM90/NM95/NM100/NM150/NM200 打 Nightmare；含 Token 兌換邏輯
- **導航方式**：圖像導航——event_banner 辨識，scroll 後找 event_raid_battle 位置，依 Index 決定點擊目標
- **模板風險**：event_raid_battle 索引計數法（第 1、2 或 3 個按鈕）容易因活動頁版面變動而點錯位置
- **建議**：✅ 保留（核心活動功能）

---

### 12. 公會戰（Dread Barrage）

- **Settings.farming_mode**：`"Dread Barrage"`
- **對應檔案**：`bot/game_modes/dread_barrage.py`（live）
- **功能**：首頁 scroll 找 dread_barrage Banner → 進入；支援 1–5 星難度；含已開房「Resume」偵測直接繼續；使用 Full Auto
- **導航方式**：圖像導航——scroll + find_button("dread_barrage") 最多重試 30 次
- **模板風險**：dread_barrage Banner 外觀每次活動期間固定，但限時活動，非活動期間無法使用
- **建議**：✅ 保留

---

### 13. 勇氣之地（Proving Grounds）

- **Settings.farming_mode**：`"Proving Grounds"`
- **對應檔案**：`bot/game_modes/proving_grounds.py`（live）
- **功能**：home_menu → 活動 Banner（依 first_event 選第幾個）→ 勇氣之地任務頁 → Extreme/Extreme+ 難度選擇 → Play Round Button 連戰流程
- **導航方式**：圖像導航——banner 辨識 + proving_grounds_missions 按鈕 + play_round_button 陣列
- **模板風險**：proving_grounds 頁面模板為 2022 年截圖；若官方改版 UI 需補截
- **建議**：✅ 保留

---

### 14. 六道（Xeno Clash）

- **Settings.farming_mode**：`"Xeno Clash"`
- **對應檔案**：`bot/game_modes/xeno_clash.py`（live）
- **功能**：go_back_home → Quest → Special → 六道關卡；含 Resume 偵測；包含 Nightmare 偵測
- **導航方式**：圖像導航——Quest 頁 → Special 頁 → 六道入口
- **模板風險**：六道為限期活動，模板與 Special 頁按鈕共用，適用性尚可
- **建議**：✅ 保留

---

### 15. Side Story（通稱 Side Story，GUI 標記「暫不可用」）

- **Settings.farming_mode**：`"Side Story"`
- **對應檔案**：`bot/game_modes/sidestory.py`（live import，但邏輯為死碼）
- **功能**（原設計）：使用 Alt+8 書籤跳至 Side Story 頁面，然後執行 treasure_trade（兌換）迴圈
- **導航方式**：`pyautogui.keyDown('alt') + press('8')`——依賴 harjeb 自製的瀏覽器書籤快捷鍵，在標準環境完全無效
- **現況**：_navigate() 發出 Alt+8 後若找到 draw 按鈕就開始兌換，否則直接 return False；完全無法到達正確頁面
- **建議**：❌ 可刪（整個模式邏輯依賴書籤快捷鍵，在用戶環境永遠失效）

---

### 16. 通常（Generic）

- **Settings.farming_mode**：`"Generic"`
- **對應檔案**：`bot/game_modes/generic.py`（live，import 成 `_Generic as Generic`）；`generic2.py` 為死碼（Alt+1 書籤版）
- **功能**：「通用再玩一次」模式——不做導航，假設用戶已手動進入某場戰鬥，機器人從 Attack 按鈕或 Play Again 按鈕開始，靠「再玩一次」迴圈持續刷
- **導航方式**：無導航（從當前畫面狀態判斷：Attack / Coop Start / Play Again / Select Summon）
- **模板風險**：依賴通用按鈕（attack/play_again），穩定性高
- **建議**：✅ 保留（使用場景廣，任何支援 Play Again 的關卡都可用）

---

### 17. 暫停休息

- **Settings.farming_mode**：GUI 佇列中的「休息」項目
- **功能**：在佇列中插入固定分鐘數的暫停，模擬真人行為
- **對應程式**：GUI 層直接 sleep，不呼叫 backend；與 game.py 主迴圈的內建小/大休息（33–35 分鐘 / 3–4 小時）分離
- **建議**：✅ 保留

---

### 附加模式（不在 data_zhcn.json 17 鍵但 game.py 有分派）

| farming_mode 值 | 對應類別 | 說明 |
|---|---|---|
| `"Fate"` | `Fate`（fate.py） | 命運劇情特殊關卡（fate_episode 圖像導航），非標準刷圖模式 |
| `"Exo"` | `Exo`（exo.py） | 另一個 Event 類變體，導航邏輯類似 event.py，支援 Solo/Extreme；GUI 中可能尚未配置關卡清單 |

---

## 三、共用基礎設施

### ImageUtils（`utils/image_utils.py`）

| 功能 | 說明 |
|---|---|
| `determine_template_scale()` | 開機時掃 0.5x–3.0x 找最佳縮放比例，存入 `_template_scale`；2K/4K/Retina/DPI 縮放全部自動適配 |
| `_template_path()` | 依 `game_language` 解析模板路徑；非 en 時優先找 `images/<folder>_<lang>/`，缺檔退回英文版（日文版 fallback 機制） |
| `_scaled_template()` | 套用 `_template_scale * _screenshot_ratio` 調整模板尺寸後再做 cv2 模板匹配 |
| `find_all()` | 全螢幕掃出所有匹配位置（用於 host_quest、coop_hard 等多重按鈕偵測） |
| `save_debug_screenshot()` | 匹配失敗時存截圖至 `logs/debug_*.png`，供事後診斷 |
| `_grab_screen()` | 截取遊戲區域並更新 `_screenshot_ratio`（支援 mac Retina） |

### MouseUtils（`utils/mouse_utils.py`）

貝茲曲線滑鼠移動（`enable_bezier_curve_mouse_movement`）、`scroll_screen_from_home_button()`——以 Home 鍵為基準捲動，適配任意解析度。

### CombatMode（`bot/combat_mode.py`）

- **腳本語言**：逐行解析 `src-tauri/scripts/*.txt`；關鍵指令：`enablefullauto`、`enablesemiauto`、`skill.n`、`summon.n`、`turn:N`、`usegreenpotion`…等
- **快速召喚**：`enable_auto_quick_summon`（預設開），所有戰鬥路徑均觸發，5 秒防重複
- **自動刷新**：`enable_refresh_during_combat`（預設開），攻擊後 F5 刷新防止頁面卡住
- **Wipe 偵測**：偵測 party_wipe_indicator 或 salute_participants，自動撤退或退出 Raid

### Settings（`utils/settings.py`）

從 `settings.json` 讀取所有設定填入類別變數（無實例化）；`Settings.update(path)` 可在 farming_mode 啟動時重新載入（支援佇列多任務不同設定）。

### Twitter/Discord 通知

- **TwitterRoomFinder**（`utils/twitter_room_finder.py`）：使用 tweepy 的 Twitter Stream API v2，監聽推文中的 Raid 房號；程式碼完整但 game.py 已在 Raid 分派前加注解 `# use eriri instead`，實際**不再啟用**（`TwitterRoomFinder.connect()` 已被注解）；僅在 `except` / 結束時呼叫 `disconnect()`（空操作）。
- **DiscordUtils**（`utils/discord_utils.py`）：透過 Discord Bot DM 通知狀態；`Game.start_discord_process()` 在 farming_mode 中已被注解（`#Game.start_discord_process()`）；`enable_discord` 設定為 False 時完全不啟動。

### CAPTCHA 音效

`playsound3`（fallback：`playsound`）在 `CombatMode` 偵測到驗證碼時播放音效，最多等待 10 分鐘讓用戶手動處理，完成後自動繼續。

### ESC 緊急停止

GUI 層全域快捷鍵（僅在佇列執行中有效），按 ESC 呼叫 TaskRunner 停止，終止 backend 子行程（含其子行程，避免滑鼠繼續移動）。

### Debug 截圖機制

`ImageUtils.save_debug_screenshot(tag)` 在匹配失敗的關鍵路徑自動截圖存至 `logs/debug_<tag>_<時間>.png`，方便補截新模板。

---

## 四、死碼 / 優化清單

以下每項格式：**檔案 / 功能｜現況｜建議｜影響**

| # | 檔案 / 功能 | 現況 | 建議 | 影響 |
|---|---|---|---|---|
| 1 | `bot/game_modes/event_quick.py` | import 存在但 start() 僅發出 Alt+1 就結束，GUI 已標「待重做」 | ❌ 刪除或完整重寫為圖像導航版 | 低：無用戶可用功能 |
| 2 | `bot/game_modes/sidestory.py` | _navigate() 使用 Alt+8，在標準環境永遠失效；GUI 已標「待重做，暫不可用」 | ❌ 刪除（或保留殼、改寫導航邏輯） | 低：無用戶可用功能 |
| 3 | `bot/game_modes/arcarum_sandbox.py`（無底線版） | 使用 Alt+4 書籤快捷鍵，已被 `_arcarum_sandbox.py` 取代，game.py 不 import | ❌ 刪除 | 零：不被引用 |
| 4 | `bot/game_modes/rotb.py`（無底線版） | 使用 Alt+N 書籤快捷鍵，已被 `_rotb.py` 取代，game.py 不 import | ❌ 刪除 | 零：不被引用 |
| 5 | `bot/game_modes/generic2.py` | Generic 類別使用 Alt+1 書籤快捷鍵，game.py import 的是 `generic.py`（_Generic） | ❌ 刪除 | 零：不被引用 |
| 6 | `bot/game_modes/raid.py`（原版） | 依賴 `EririRoomFinder` 外部找房服務，game.py 已注解並改用 `raid2.py` | ❌ 刪除 | 零：不被引用 |
| 7 | `utils/twitter_room_finder.py` | tweepy Stream API 已設定，但 game.py Raid 分派前呼叫已注解（`# use eriri instead`）；exception / finally 的 disconnect() 是空操作 | 🔧 可刪（若確定永不用 Twitter 找房）；否則保留但不做任何事 | 低：每次 import 仍載入 tweepy |
| 8 | `utils/discord_utils.py` | 功能完整，但 `start_discord_process()` 已注解；只有 exception 時 put 到 queue（queue 從不被消費） | 🔧 若不需要 Discord 通知可刪；否則解注解啟用 | 低：無副作用，只是死存 queue |
| 9 | `Game.__init__` 中重複 import | `__init__` 中逐一重複頂部 import（`from bot.game_modes.arcarum import Arcarum` 等），Python 不重複載入，但程式碼冗餘 | 🔧 刪除 `__init__` 中的重複 import | 低：可讀性、維護成本 |
| 10 | `main.py` 中 `update_settings` / `get_status` 方法 | 有 `json` import 但 import 不在頂部；`current_settings` 屬性從未定義；兩個方法從未被呼叫 | 🔧 刪除未完成的遠端控制殘留程式碼 | 低：隱藏潛在 NameError |
| 11 | `Settings` 類別初始化時直接載入 settings.json | 模組頂層（類別定義時）就嘗試 open settings.json，若執行時 cwd 不對會在 import 時崩潰 | 🔧 改為 lazy loading（僅 update() 時讀檔） | 中：偶爾導致難以診斷的 import 錯誤 |
| 12 | `game.py` 主迴圈 unchanged_count 邏輯 | `unchanged_count` 在迴圈外初始化、迴圈內每輪重置為 0，永遠不會達到 3 次門檻；邏輯錯誤 | 🔧 修正（初始化移到 try 外，或整段刪除） | 低：防呆邏輯失效，但不影響正常農場 |
| 13 | `bot/game_modes/exo.py` | 功能類似 event.py，但 GUI 的 data_zhcn.json 內無 "Exo" 鍵；game.py 有分派（`elif Settings.farming_mode == "Exo"`）；用戶無法從 GUI 選到 | 🔧 補 GUI 資料或確認是實驗性功能後決定保留或刪除 | 低：目前對 GUI 用戶不可見 |
| 14 | `bot/game_modes/fate.py` | game.py 有分派但 GUI data 中無 "Fate" 鍵；fate_episode 導航為特殊劇情關卡 | 🔧 同上——補 GUI 或移除 | 低：同上 |

---

> **最值得優先刪除的前 5 名**（對用戶零價值、零副作用）：
>
> 1. `bot/game_modes/arcarum_sandbox.py`（無底線版）—— 完全死碼，Alt+4 版本
> 2. `bot/game_modes/rotb.py`（無底線版）—— 完全死碼，Alt+N 版本
> 3. `bot/game_modes/generic2.py` —— 完全死碼，Alt+1 版本
> 4. `bot/game_modes/raid.py`（原版）—— 依賴已廢棄的 EririRoomFinder
> 5. `bot/game_modes/event_quick.py` / `sidestory.py` —— 已宣告不可用，佔 GUI 選項但永遠失敗
