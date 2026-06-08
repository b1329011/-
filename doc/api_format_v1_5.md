# 「不揪ㄛ」揪團平台——前後端 API 規格書 (V1.5)

本文件定義「不揪ㄛ」運動揪團平台前端與後端之資料傳輸介面。第 1.5 版 (V1.5) 根據目前後端實作進行整理，包含：**自動信用分扣減機制**、**防重複檢舉**、**候補轉正機制**、**氣象與 AQI 串接**、以及**管理員回饋處理與回覆**等核心邏輯。

**文件版本：** V1.5
**基礎網址 (Base URL)：** `/api`
**認證方式：** `Authorization: Token {your_token}`

---

## 一、 使用者認證與個人檔案 (Auth & Users)

### 1. 使用者註冊 (Register)
- **路徑：** `POST /api/auth/register`
- **權限：** 公開
- **參數 (JSON Body)：**
  | 參數 | 必填 | 格式 | 說明 |
  | :--- | :--- | :--- | :--- |
  | name | 是 | String | 暱稱 |
  | email | 是 | String | 電子信箱 (登入帳號) |
  | password | 是 | String | 密碼 |

### 2. 使用者登入 (Login)
- **路徑：** `POST /api/auth/login`
- **權限：** 公開
- **參數 (JSON Body)：**
  | 參數 | 必填 | 格式 | 說明 |
  | :--- | :--- | :--- | :--- |
  | email | 是 | String | 電子信箱 |
  | password | 是 | String | 密碼 |
- **回傳：** 包含 `token`, `user_id`, `role`。若信譽分數 <= 40 會回傳 403 被停權。

### 3. 個人資料管理 (Profile)
- **路徑：** `GET /api/users/profile` (取得), `PUT/PATCH /api/users/profile` (更新), `DELETE /api/users/profile` (註銷)
- **說明：** 
    - 首次完善資料時 `phone`, `birthday`, `gender`, `levels` 為必填。
    - `birthday` 與 `gender` 僅能在首次建立時填寫，後續不可修改。
    - 手機號碼格式須為 `09xxxxxxxx`。
- **更新參數範例：**
```json
{
  "name": "陳球友",
  "phone": "0912345678",
  "bio": "熱血排球人",
  "levels": {"排球": "A", "籃球": "B"},
  "line_id": "test_line",
  "instagram": "test_ig"
}
```

### 4. 運動程度設定 (Sport Levels)
- **路徑：** `GET /api/users/sport-levels`
- **路徑：** `PUT /api/users/sport-levels` (更新單項程度)
- **參數：** `{"sport_id": 1, "level": "A"}`

### 5. 管理員更新使用者信譽 (Admin Only)
- **路徑：** `PATCH /api/users/{id}/reputation`
- **參數：** `{"credit_point": 100}`

---

## 二、 運動與場地模組 (Sports & Venues)

### 1. 取得運動項目
- **路徑：** `GET /api/sports`

### 2. 取得場地列表
- **路徑：** `GET /api/venues`
- **Query 參數：** `city`, `district`
- **回傳：** 包含場地名稱、地址、設施清單、經緯度等。

### 3. 取得場地行政區分組 (Regions)
- **路徑：** `GET /api/venues/regions`
- **說明：** 用於前端篩選器，回傳以 縣市 -> 行政區 分組的場地清單。

### 4. 回報球場狀態
- **路徑：** `POST /api/venues/{venue_id}/courts/{court_id}/report-status`
- **參數：** `{"issue_type": "漏水", "description": "天花板在滴水"}`
- **說明：** 標記球場為佔用/異常，並推播警告給今日預約該球場的主揪。

### 5. 管理員功能 (Admin Only)
- **新增場地：** `POST /api/venues`
- **刪除場地：** `DELETE /api/venues/{id}` (若有進行中球局則回傳 409)
- **緊急關閉場地：** `POST /api/venues/{id}/emergency-close` (通知所有受影響球友)

---

## 三、 球局房間模組 (Games/Matches)

### 1. 取得球局列表
- **路徑：** `GET /api/games`
- **Query 參數：** `sport_id`, `target_level`, `city`, `date`, `region`, `lat`, `lng`, `radius`
- **特色：** 自動計算距離 (`distance_km`) 與氣象適合度 (`weather`)。

### 2. 建立球局
- **路徑：** `POST /api/games`
- **說明：** 信譽分數低於 60 分者無法創房。
- **主要參數：**
```json
{
  "game_name": "歡樂羽球團",
  "sport_id": 1,
  "venue_id": 5,
  "most_players": 6,
  "least_players": 4,
  "target_level": "業餘",
  "booking_date": "2026-06-25",
  "start_time": "14:00",
  "duration": "2 小時",
  "total_price": 600,
  "gender_limit": "不限",
  "game_note": "帶球來"
}
```

### 3. 加入與退出球局
- **報名/排候補：** `POST /api/games/{id}/join`
    - 自動判斷正取或候補 (順位)。
    - 若程度不符會回傳 `LEVEL_MISMATCH` 錯誤，需傳入 `{"force": true}` 強制加入。
- **取消報名/退出：** `DELETE /api/games/{id}/cancel`
    - 若在活動前 24 小時內取消，**自動扣除信譽分數 10 分**。

### 4. 主揪管理功能
- **回報場地狀態：** `PATCH /api/games/{id}/venue-status`
    - `{"status": "已佔到/已預約"}` 或 `{"status": "未佔到/未預約"}`。
    - 若未佔到，球局將自動取消並通知所有成員。
- **發佈公告：** `POST /api/games/{id}/announcements`
- **取得公告歷史：** `GET /api/games/{id}/announcements`

### 5. 快速配對 (Quick Match)
- **路徑：** `POST /api/games/quick-match`
- **參數：** `sport_id`, `target_level`, `age_preference`
- **說明：** 根據年齡段與等級計算匹配分數。

---

## 四、 收藏、檢舉與通知 (Social & Reports)

### 1. 收藏球局 (Favorites)
- `GET /api/favorites/games`
- `POST /api/favorites/games` (Body: `{"game_id": 123}`)
- `DELETE /api/favorites/games/{game_id}`

### 2. 提交檢舉 (Reports)
- **路徑：** `POST /api/reports`
- **說明：** **系統自動審查並扣分**。檢舉後會根據原因扣除被檢舉人 10~60 分。
- **防重複：** 同一使用者對同一球局的同一對象僅能檢舉一次。
- **參數：** `{"game_id": 1, "reported_user_id": 5, "reason": "未出現", "detail": "放鳥不來"}`

### 3. 通知系統 (Notifications)
- **取得列表：** `GET /api/notifications` (包含活動提醒、公告通知、回饋回覆)
- **標記已讀：** `PATCH /api/notifications/{id}/read`

---

## 五、 氣象、數據與回饋 (Utility & Admin)

### 1. 天氣與環境 API
- **即時天氣與 AQI：** `GET /api/weather/aqi` (Query: `city`, `district`)
- **說明：** 串接 CWA 與 MOENV 公開資料。

### 2. 回饋系統 (Feedback)
- **提交回饋：** `POST /api/feedback` (`{"type": "建議", "content": "..."}`)
- **管理員處理：** `PUT /api/admin/feedbacks/{id}/handle` (Body: `{"admin_reply": "感謝回報"}`)
    - 處理後會自動推播通知給提交的使用者。

### 3. 數據分析與公告 (Admin Only)
- **數據儀表板：** `GET /api/admin/analytics`
- **發佈系統公告：** `POST /api/admin/announcements`
- **同步場地 OpenData：** `POST /api/admin/opendata/sync-venues`

---

## 六、 信譽分數等級說明 (Credit Points)

- **100 分：** 初始分數，完美紀錄。
- **80-99 分：** 一般使用者。
- **60-79 分：** **限制創房功能**，僅能參加他人球局。
- **41-59 分：** **列入黑名單**，無法加入任何球局。
- **<= 40 分：** **永久停權**，帳號無法登入。
- **恢復機制：** 信用分每 2 天自動恢復 1 分 (最高恢復至 100 分)。
