# 「不揪ㄛ」揪團平台——前後端 API 規格書

本文件定義「不揪ㄛ」運動揪團平台前端與後端之資料傳輸介面，欄位設計嚴格對齊系統 MySQL 資料表結構（包含 Users, GamesMatches, Match_Participants, favorite_games, favorite_venues, Reports, blacklist），並納入「生日年齡驗證」與「球局/場館收藏」等新進功能。

**文件版本：** V1.0  
**基礎網址 (Base URL)：** `/api`

---

## 一、 使用者認證與個人檔案模組 (Auth & Users)

主要連動 `users`、`user_sport_levels` 與 `blacklist` 資料表。用於處理球友註冊、登入、信用積分核算與運動能力級別之管理。

### 1. 使用者註冊與登入
- **路由路徑：** `POST /api/auth/login`
- **說明：** 使用者首次登入即自動註冊，前端需傳入生日以供後端進行年齡匹配驗證。

| 傳入參數 (JSON Body) | 欄位型態 | 欄位說明 |
| :--- | :--- | :--- |
| name | String | 球友姓名或暱稱 |
| phone | String | 聯絡電話（唯一識別） |
| birthday | Date (YYYY-MM-DD) | 出生年月日（前端用日曆選擇器） |

**後端回傳範例 (Response 200)：**
```json
{
  "token": "eyJhbGciOi...",
  "user_id": 1,
  "role": "user"
}
```

### 2. 取得個人資料與信譽積分
- **路由路徑：** `GET /api/users/profile`
- **說明：** 後端需根據 `birthday` 與當前日期，於資料庫動態計算出 `age` 欄位吐給前端。

**後端回傳範例 (Response 200)：**
```json
{
  "user_id": 1,
  "name": "陳球友",
  "phone": "0912345678",
  "birthday": "2006-06-25",
  "age": 19,
  "credit_point": 100,
  "role": "user"
}
```

### 3. 取得與更新個人的運動能力分級
- **取得能力值：** `GET /api/users/sport-levels`
- **更新能力值：** `PUT /api/users/sport-levels`

**更新時傳入參數 (Body)：**
```json
{
  "sport_id": 1,
  "level": "advanced"
}
```

### 4. 設定與取得使用者月曆可用時間與地點
- **說明：** 提供使用者在行事曆/月曆上標記多個有空的時間區段與所在地點，以供系統進行精準的推薦或匹配。
- **設定可用時間與地點：** `POST /api/users/availability`
- **取得目前可用設定：** `GET /api/users/availability`

**設定時傳入參數範例 (Body)：**
```json
{
  "available_dates": ["2026-05-25", "2026-05-26"],
  "time_slots": ["18:00-20:00", "20:00-22:00"],
  "preferred_city": "新北市",
  "preferred_district": "板橋區",
  "latitude": 25.0116,
  "longitude": 121.4617,
  "search_radius_km": 5
}
```

**後端回傳範例 (Response 200)：**
```json
{
  "status": "success",
  "message": "月曆可用時間與地點更新成功。"
}
```

---

## 二、 球局房間模組 (GamesMatches CRUD)

主要連動 `gamesmatches`、`sports`、`venues` 與 `address` 資料表。為系統核心列表與開房引擎。

### 1. 取得球局列表 (支援分類篩選與特殊排序)
- **路由路徑：** `GET /api/games`
- **前端篩選 Query 參數：** `?sport_id=1&target_level=casual&city=新北市&date=2026-05-25&time_slot=18:00-20:00&lat=25.0116&lng=121.4617&radius=5`
- **說明：** 支援傳統分類與基於月曆時間、地理位置（GPS 經緯度及半徑距離）的附近搜尋。後端需主動將球場、運動項目、地址進行 JOIN，並透過 Haversine 公式進行半徑篩選，同時連動氣象與環保署 OpenData 計算出 `weather_index`（不適合遊玩指數）直接吐給前端。

| 回傳 JSON 欄位 | 欄位型態 | 欄位說明 |
| :--- | :--- | :--- |
| game_id | Int | 球局活動唯一識別碼 |
| sport_name | String | 運動項目名稱（羽毛球、排球、籃球、麻將） |
| venue_name | String | 球館/場館名稱 |
| split_price | Decimal | 分攤後一人需付金額（總價/上限人數） |
| most_players | Int | 所需總人數 |
| current_players | Int | 目前已加入人數（剩餘名額由前端兩者相減計算） |
| weather_index | Decimal | 不適合遊玩指數 (5*降雨機率 + AQI/50) |
| match_status | Enum | 匹配狀態 ('recruiting', 'full', 'closed') |
| distance_km | Decimal | 距離目前位置公里數（僅在傳入 lat, lng 時回傳） |

> **💡 前端 UI 特別處理邏輯：**
> 1. 若 `sport_name` 為「麻將」，前端應直接隱藏時間篩選，改以極大字體視覺化突顯「缺 1 人」、「缺 2 人」之即時狀態。
> 2. 若 `weather_index` 指數偏高且場地類型為 outdoor，前端卡片需亮起紅色降雨警告標籤。

### 2. 主揪發起球局（開房）
- **路由路徑：** `POST /api/games`

**前端傳送範例 (Body)：**
```json
{
  "sport_id": 1,
  "court_id": 5,
  "least_players": 4,
  "most_players": 6,
  "target_level": "casual",
  "booking_date": "2026-05-25",
  "time_slot": "14:00-16:00",
  "total_price": 600.00,
  "deposit_required": 1,
  "cancel_deadline": "2026-05-24T14:00:00Z"
}
```

### 3. 智慧隨機匹配與推薦隊伍
- **路由路徑：** `POST /api/games/quick-match`
- **說明：** 使用者傳入運動項目與期望篩選條件（年齡區間、休閒/專業、能力級別）。後端會自動在現有開放的房間中進行相似度權重排序，**絕不自動幫使用者加入房間**，而是回傳列表讓使用者自行選擇：
  1. 若有完全符合條件的球局，回傳最多 3 個精確匹配的球局 (`exact_matches`)。
  2. 若無完全符合條件的球局，則回傳最多 3 個相似/相關的球局 (`alternative_matches`)。

**前端傳送範例 (Body)：**
```json
{
  "sport_id": 1,
  "target_level": "casual",
  "age_preference": "same_generation", 
  "play_style": "leisure"
}
```

**後端回傳範例 (Response 200 - 有完全符合條件之球局)：**
```json
{
  "matched_type": "exact",
  "matches": [
    {
      "game_id": 105,
      "sport_name": "羽毛球",
      "venue_name": "板橋國民運動中心",
      "match_score": 100,
      "reason": "時間、年齡與能力要求完全相符"
    },
    {
      "game_id": 106,
      "sport_name": "羽毛球",
      "venue_name": "板橋體育館",
      "match_score": 98,
      "reason": "同年代球友，等級與您高度吻合"
    }
  ]
}
```

**後端回傳範例 (Response 200 - 無完全符合，回傳推薦/相關列表)：**
```json
{
  "matched_type": "alternative",
  "matches": [
    {
      "game_id": 108,
      "sport_name": "羽毛球",
      "venue_name": "樹林羽球館",
      "match_score": 85,
      "reason": "能力相符，但時間稍有落差"
    },
    {
      "game_id": 112,
      "sport_name": "羽毛球",
      "venue_name": "板橋體育館",
      "match_score": 80,
      "reason": "年齡相仿，但等級要求稍高"
    }
  ]
}
```

### 4. 主揪修改球局房間資訊
- **路由路徑：** `PUT /api/games/{game_id}`
- **說明：** 主揪在取消截止時間前（`cancel_deadline`），可修改該球局的資訊（如：活動日期、時間段、備註、所需總人數上限、能力限制等）。修改完成後，後端會自動向所有已加入的成員發送「球局資訊修改通知」。

**前端傳送範例 (Body)：**
```json
{
  "least_players": 4,
  "most_players": 8,
  "target_level": "casual",
  "booking_date": "2026-05-26",
  "time_slot": "15:00-17:00"
}
```

**後端回傳範例 (Response 200)：**
```json
{
  "status": "success",
  "message": "球局資訊修改成功，已向所有成員發送變更通知。"
}
```

---

## 三、 球友參與與房間互動模組 (Match Participants)

主要連動 `match_participants`（參與表）、`waitlists`（候補表）與 `gamesmatches` 資料表。控制房間內人員異動、取消截止期限、到場確認與候補處理。

### 1. 球友加入球局（我要加一）
- **路由路徑：** `POST /api/games/{game_id}/join`
- **後端檢驗安全機制：** 後端會校驗使用者目前是否被列入黑名單（`blacklist`）、信用積分是否足夠，以及其能力值（`level`）是否達到房間要求的 `target_level`。

### 2. 球友退出球局
- **路由路徑：** `DELETE /api/games/{game_id}/leave`
- **說明：** 前端點擊退出。若當前時間已超過 `cancel_deadline` 且該球局 `deposit_required=1`，後端將執行扣除訂金流程或跳出不可免費取消警告。

### 3. 免費場地：主揪到場站位確認與補救機制
- **路由路徑：** `PATCH /api/games/{game_id}/confirm-presence`
- **前端傳送 (Body)：** `{ "is_confirmed": 1 }`
- **說明與補救機制：**
  - **開局前 30 ~ 15 分鐘（補救與預警期）：** 若主揪尚未按下到場確認，系統將自動向該球局全體成員發送「主揪尚未回報到場」之**預警通知**。主揪在此期間內仍可點擊確認到場，完成補救且**免於處罰**。
  - **開局前 15 分鐘內（逾時解散與處罰期）：** 若主揪於開局前 15 分鐘仍未進行到場確認，該球局將被系統**強制自動解散**。系統會向所有成員發送**解散通知**，並對主揪執行信譽點數扣除懲罰（扣除信用分數 10 分，情節嚴重者寫入黑名單）。

### 4. 加入球局候補名單
- **路由路徑：** `POST /api/games/{game_id}/waitlist`
- **說明：** 當球局房間人數已滿（`match_status='full'`）時，球友可選擇排入該球局之候補名單，後端會記錄於 `waitlists` 資料表。

**後端回傳範例 (Response 200)：**
```json
{
  "waitlist_id": 45,
  "position": 2,
  "status": "waiting",
  "message": "已成功加入候補名單，您目前順位為第 2 位。"
}
```

### 5. 取消候補名單
- **路由路徑：** `DELETE /api/games/{game_id}/waitlist`
- **說明：** 使用者主動取消候補狀態，釋放順位，後端自動更新後續候補球友之順位值 (`position`)。

### 6. 候補轉正與自動遞補規則
- **說明：**
  1. **自動遞補：** 當有正式成員退出（呼叫 `DELETE /api/games/{game_id}/leave`）時，系統將自動查詢 `waitlists` 中 `position=1` 的球友，直接將其轉為正式加入 (`match_participants` 寫入)，並寄送成團/轉正通知。
  2. **手動轉正 API (限主揪或管理員)：** `POST /api/games/{game_id}/waitlist/promote`
     - 傳入 Body: `{"user_id": 12}`
     - 說明：主揪可手動將指定候補球友強行轉正（若球友被扣信用分或特殊需求時使用）。

---

## 四、 關注與收藏模組

連動全新建立之 `favorite_games` 與 `favorite_venues` 關聯表。用於實現球友收藏愛心功能。

### 1. 收藏與取消收藏「球局」
- **新增收藏：** `POST /api/favorites/games` → 傳入 Body: `{"game_id": 101}`
- **移除收藏：** `DELETE /api/favorites/games/101`
- **取得收藏球局列表：** `GET /api/favorites/games`

### 2. 收藏與取消收藏「場館球館」
- **新增收藏：** `POST /api/favorites/venues` → 傳入 Body: `{"venue_id": 5}`
- **移除收藏：** `DELETE /api/favorites/venues/5`
- **取得收藏場館列表：** `GET /api/favorites/venues`
- **說明：** 當使用者將某運動場館加入收藏後，一旦有其他主揪在該場館發起/創建新球局房間時，系統會自動對收藏該場館的使用者推播「新開團通知」，方便球友第一時間報名參戰。

---

## 五、 檢舉與管理員後台模組 (Reports & Admin Panel)

主要連動 `reports`、`penalty_rules`、`blacklist` 及 `gamesmatches` 資料表。提供檢舉裁決、黑名單封鎖，以及管理員後台對球局房間之管理。

### 1. 使用者發起賽後檢舉
- **路由路徑：** `POST /api/reports`

**前端傳送範例 (Body)：**
```json
{
  "game_id": 101,
  "offender_id": 3,
  "reason": "no_show" 
}
```
*\*註：reason 可選值包含放鳥 'no_show'、未付錢 'not_paid'、惡劣行為 'bad_behavior'。*

### 2. 管理員審核檢舉案 (限 Admin 權限)
- **路由路徑：** `PATCH /api/admin/reports/{report_id}/review`
- **前端傳送 (Body)：** `{ "status": "deducted", "admin_note": "審核通過，放鳥扣分" }`
- **說明：** 審核狀態改為 `deducted` 後，後端依 `penalty_rules` 自動扣減該 user 的 `credit_point`。當低於特定積分，後端應自動寫入 `blacklist`（黑名單表）強制封鎖其開房與加一權限。

### 3. 查詢已成團房間與進行中球局 (限 Admin 權限)
- **路由路徑：** `GET /api/admin/games`
- **前端篩選 Query 參數：** `?status=full`

### 4. 新增場館審核 (限 Admin 權限)
- **路由路徑：** `PATCH /api/admin/venues/{venue_id}/approve`
- **說明：** 審核由合作商或大眾提報的新運動場館，核准後方可在前台地圖與開房列表中顯示。
- **前端傳送 (Body)：** `{ "is_approved": 1, "remarks": "場地安全設施與地板規格審核通過" }`

### 5. 天氣/場地臨時關閉與不可抗力流程 (Force Majeure)
- **路由路徑：** `POST /api/admin/venues/{venue_id}/emergency-close`
- **說明：** 當遇強烈颱風、暴雨或場地大修等不可抗力事件時，管理員登記該場館特定時段關閉/警告。系統會自動查詢受影響時段在該場館進行的所有球局，並自動發布不可抗力警報通知，**強烈建議房主（主揪）主動取消或修改球局時間**，而不是強制直接取消球局。

**前端傳送範例 (Body)：**
```json
{
  "close_date": "2026-05-28",
  "time_slots": ["14:00-16:00", "16:00-18:00"],
  "reason": "強烈颱風配合停班停課臨時關閉"
}
```

### 6. 管理者發布即時公告與統籌人溝通
- **路由路徑：** `POST /api/admin/broadcast`
- **說明：** 管理員向所有球局發起人（主揪）或全體球友發送緊急通知或政策宣導。
- **前端傳送範例 (Body)：**
```json
{
  "target_group": "organizers",
  "title": "梅雨季節戶外球場退款政策公告",
  "content": "若因降雨導致戶外場地無法使用，請於球局開始前10分鐘於系統上傳雨勢照片以利退款..."
}
```

---

## 六、 球館與場地基礎資訊模組 (Venues & Courts)

主要連動 `venues`（場館表）、`court`（場地/桌次表）、`sports`（運動項目表）與 `court_sports`（場地支持項目表）。提供前端渲染場館地圖、列表篩選，以及主揪發起活動時選擇場地。

### 1. 取得場館列表 (支援條件與票價篩選)
- **路由路徑：** `GET /api/venues`
- **前端篩選 Query 參數：** `?sport_type=羽毛球&city=新北市&min_price=100&max_price=500`

**後端回傳範例 (Response 200)：**
```json
[
  {
    "venue_id": 5,
    "name": "板橋體育館",
    "address": "新北市板橋區中正路8號",
    "sport_types": ["羽毛球", "籃球"],
    "base_price": 300.00,
    "opening_hours": "06:00-22:00",
    "rating": 4.5
  }
]
```

### 2. 取得特定場館詳細資訊
- **路由路徑：** `GET /api/venues/{venue_id}`

**後端回傳範例 (Response 200)：**
```json
{
  "venue_id": 5,
  "name": "板橋體育館",
  "address": "新北市板橋區中正路8號",
  "sport_types": ["羽毛球", "籃球"],
  "base_price": 300.00,
  "opening_hours": "06:00-22:00",
  "phone": "02-29683668",
  "facilities": ["免費車位", "熱水淋浴間", "自動販賣機"],
  "rating": 4.5
}
```

### 3. 取得特定場館內之場地/桌次狀態
- **路由路徑：** `GET /api/venues/{venue_id}/courts`

**後端回傳範例 (Response 200)：**
```json
[
  { "court_id": 1, "court_name": "A 羽球場", "occupied": 0, "status": "normal" },
  { "court_id": 2, "court_name": "B 羽球場", "occupied": 1, "status": "under_renovation" }
]
```

### 4. 回報場地與設備異常狀態 (使用者/主揪回報)
- **路由路徑：** `POST /api/venues/{venue_id}/courts/{court_id}/report-status`
- **說明：** 供使用者、主揪回報場地的異常狀況（如：場館正在整修、設施損壞無法使用、場地已不存在等）。後端接收後會標記該場地狀態，並發送審核通知給管理員，同時主動通知目前預約/使用該場地的所有球局房主。

**前端傳送範例 (Body)：**
```json
{
  "issue_type": "broken_equipment",
  "description": "羽球網斷裂損壞，且現場無備品更換",
  "photo_url": "https://example.com/photos/issue_123.jpg"
}
```

**後端回傳範例 (Response 200)：**
```json
{
  "status": "success",
  "message": "感謝您的回報！系統已建立場地修繕案並通知管理員，同時將警告推播給今日預計使用此場地的球友房主。"
}
```

### 5. 管理者新增運動場館 (限 Admin 權限)
- **路由路徑：** `POST /api/admin/venues`
- **說明：** 管理員可在後台直接新增平台核可的優質運動場館與所屬場地。

**前端傳送範例 (Body)：**
```json
{
  "name": "新莊國民運動中心",
  "address": "新北市新莊區公園路11號",
  "sport_types": ["羽毛球", "游泳", "籃球"],
  "base_price": 500.00,
  "opening_hours": "06:00-22:00",
  "phone": "02-77288888",
  "facilities": ["淋浴間", "付費停車場"]
}
```

**後端回傳範例 (Response 200)：**
```json
{
  "status": "success",
  "venue_id": 12,
  "message": "新運動場館新增成功。"
}
```

---

## 七、 系統通知與成團確認模組 (Notifications)

主要處理系統即時通知的發送（包含：不成團通知、解散通知、不可抗力因素建議取消通知）以及免費場地超時確認的背景檢測。

### 1. 取得使用者個人通知列表
- **路由路徑：** `GET /api/notifications`
- **說明：** 前端鈴鐺圖示點開時呼叫，回傳所有未讀與已讀的即時通知。

**後端回傳範例 (Response 200)：**
```json
[
  {
    "notification_id": 101,
    "title": "候補成功轉正通知 🏸",
    "content": "恭喜！您候補的「今晚下班羽球局」已成功轉為正式隊員，請準時出席！",
    "is_read": 0,
    "created_at": "2026-05-25T12:00:00Z"
  }
]
```

### 2. 標記通知為已讀
- **路由路徑：** `PATCH /api/notifications/{notification_id}/read`

### 3. 三大核心通知流程說明與規格
- **A. 不成團通知 (Unsuccessful Group Notification)：**
  - **觸發時機：** 球局達到開局取消截止時間 (`cancel_deadline`)，但已加入人數 (`current_players`) 未達開局人數下限 (`least_players`)。
  - **系統動作：** 系統自動將 `match_status` 設為 `failed_to_start` 並解散該團。對所有已加入成員發送：「很抱歉，您報名的球局【球局名稱】因人數不足未達到開團下限，已自動不成團取消。」
- **B. 解散通知 (Dissolution Notification)：**
  - **觸發時機：** 主揪在取消截止時間前手動取消/解散球局，或因免費場地主揪於 15 分鐘前未確認到場導致系統強行解散。
  - **系統動作：** 對所有已加入成員（非主揪）發送：「您參與的球局【球局名稱】已由主揪（或因主揪逾時未回報到場）手動解散，造成不便敬請見諒。」
- **C. 不可抗力建議取消通知 (Force Majeure Alert)：**
  - **觸發時機：** 管理員發布某場館的臨時天災關閉、整修警報時。
  - **系統動作：** 系統**不強制解散**，而是向該時段在該場館有開團的所有主揪（房主）發送強烈建議通知：「【場館警報】您預訂的場館【場館名稱】因不可抗力因素（如颱風/整修）臨時關閉/警告，系統強烈建議您主動取消或修改您的球局，以保障球友權益與安全。」

### 4. 免費場地：30 分鐘預警與 15 分鐘超時解散檢測 (Background Worker)
- **運作機制說明：**
  - **背景排程：** 後端排程每分鐘掃描即將於 30 分鐘後開始的「免費場地球局」。
  - **30 分鐘未確認預警：** 若主揪仍未點擊到場確認 (`is_confirmed=0`)，系統自動對該球局全體成員（包括主揪）推播「主揪尚未回報到場」之**預警通知**。
  - **15 分鐘未確認懲處：** 若在開局前 15 分鐘，主揪依然未進行到場確認，系統將自動：
    1. 將球局狀態 `match_status` 變更為 `failed_to_start` (解散)。
    2. 自動觸發發送**解散通知**給全體成員。
    3. 自動扣除主揪的 `credit_point` 10 分作為信譽懲罰，並將其寫入管理員觀察名單。

---

## 八、 OpenData 同步與第三方資訊模組 (OpenData Integration)

此模組設計用於串接政府 OpenData（全國運動場館、天氣預報、空氣品質）並進行本地資料庫快取，避免前端因頻繁請求外部 API 而導致效能低落。

### 1. 場館資料 OpenData 同步與匯入 (限 Admin 權限)
- **路由路徑：** `POST /api/admin/opendata/sync-venues`
- **說明：** 手動或排程觸發從體育署全國運動場館 API 拉取最新數據，自動寫入或更新本地 `venues` 與 `courts` 資料庫。

### 2. 查詢或同步氣象與 AQI 資料
- **路由路徑：** `GET /api/opendata/weather`
- **前端 Query 參數：** `?city=新北市&district=板橋區`

**後端回傳範例 (Response 200)：**
```json
{
  "city": "新北市",
  "district": "板橋區",
  "temperature": 28.5,
  "rain_probability": 80,
  "aqi": 45,
  "weather_index": 4.9,
  "warning_message": "午後雷陣雨機率高，不建議進行戶外球局。"
}
```

### 3. 快取與更新策略
- **策略：** 後端排程每 30 分鐘呼叫一次中央氣象局與環境部 API，將最新的各行政區 `rain_probability` 與 `aqi` 快取至 Redis。當呼叫 `GET /api/games` 時，後端利用快取數據快速計算 `weather_index = (5 * 降雨機率 + AQI/50)` 併入列表回傳。

