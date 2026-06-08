# 「不揪ㄛ」揪團平台——前後端 API 規格書 (V1.3)

本文件定義「不揪ㄛ」運動揪團平台前端與後端之資料傳輸介面。第 1.3 版 (V1.3) 納入了最新的防呆與業務邏輯限制，包含：**防止刪除使用中場地**、**回饋結案狀態精簡化 (is_handled)**、以及**防範重複檢舉機制**。同時也補齊了 V1.2 中原有的 SABC 程度系統與強制資料驗證。

**文件版本：** V1.3
**基礎網址 (Base URL)：** `/api`

---

## 一、 使用者認證與個人檔案模組 (Auth & Users)

### 1. 使用者註冊 (Register)
- **路由路徑：** `POST /api/auth/register`
- **說明：** 新使用者建立帳號。

| 參數 (JSON Body) | 必填 | 格式 | 說明 |
| :--- | :--- | :--- | :--- |
| name | 是 | String | 暱稱 |
| email | 是 | String | 電子信箱，做為登入帳號 |
| password | 是 | String | 登入密碼 |

### 2. 使用者登入 (Login)
- **路由路徑：** `POST /api/auth/login`
- **說明：** 使用電子信箱與密碼登入。

| 參數 (JSON Body) | 必填 | 格式 | 說明 |
| :--- | :--- | :--- | :--- |
| email | 是 | String | 電子信箱 |
| password | 是 | String | 登入密碼 |

### 3. 取得個人資料與信譽積分
- **路由路徑：** `GET /api/users/profile`

**回傳範例 (Response 200)：**
```json
{
  "user_id": 1,
  "name": "陳球友",
  "phone": "0912345678",
  "email": "test@example.com",
  "birthday": "2006-06-25",
  "gender": "男",
  "avatar_url": "https://example.com/avatars/user1.jpg",
  "line_id": "test_line",
  "instagram": "test_ig",
  "bio": "喜歡打什麼位置...",
  "age": 19,
  "credit_point": 100,
  "role": "user",
  "levels": {
    "籃球": "B",
    "排球": "A",
    "羽球": "S",
    "桌球": "C",
    "麻將": "B"
  }
}
```

### 4. 更新/完善個人資料
- **路由路徑：** `PUT /api/users/profile`
- **說明：** 用於註冊後的「建立個人檔案」流程，或是後續修改資料。`birthday` 與 `gender` 僅能在首次建立檔案時填寫，後續不可修改。

| 參數 (JSON Body) | 必填 | 說明 |
| :--- | :--- | :--- |
| name | 否 | 暱稱修改 |
| phone | 否 | 聯絡電話 (首次完善檔案時為必填) |
| birthday | 否 | 出生年月日 (首次完善檔案時為必填) |
| gender | 否 | 性別 (首次完善檔案時為必填) |
| bio | 否 | 個人簡介 |
| avatar | 否 | 預設頭貼 ID 或上傳之圖片檔 |
| levels | 否 | SABC 程度物件 (首次完善檔案時為必填) |
| line_id | 否 | LINE ID |
| instagram | 否 | Instagram 帳號 |

### 5. 能力程度定義 (SABC 系統)
所有運動項目均須填寫程度，參考標準如下：

#### 🏀 球類運動 (籃/排/羽/桌)
- **S (菁英)：** 大專公開一、甲組等級，具備強烈跳發、精準快攻與高強度攔網。
- **A (高手)：** 大專一般組或校隊，能跑 5-1 戰術陣型、具備背舉與看手型重扣。
- **B (熟練)：** 系隊主力或熱門 Play 咖，一接二傳穩定不持球。
- **C (新手)：** 剛入門，以發球過網為目標，容易噴球、歡樂運動為主。

#### 🀄 麻將
- **S (菁英)：** 職業賽事等級，精準讀牌、扣死絕張、利用捨牌誘導放槍。
- **A (高手)：** 長期牌桌常客，能依進牌機率迅速轉圈、果斷防守下車。
- **B (熟練)：** 週末固定牌咖，吃碰槓反應順暢不拖台錢，穩定組出基本台數。
- **C (新手)：** 剛入門，容易相公、常問「這張可以吃嗎」的歡樂麻將。

---

## 二、 球局房間模組 (Games/Matches CRUD)

### 1. 取得球局列表
- **路由路徑：** `GET /api/games`
- **Query 參數：** `region`, `sport_type`, `level`

| 回傳 JSON 欄位 | 說明 |
| :--- | :--- |
| duration | 預計時長，例如 "2 小時" |
| description | 揪團說明 / 備註 |
| facilities | 場地設施陣列（後端根據 `venue_id` 自動帶入） |
| gender_limit | 性別限制 ('不限', '限男', '限女') |

### 2. 主揪發起球局（開房）
- **路由路徑：** `POST /api/games`

**傳送參數範例 (Body)：**
```json
{
  "sport_id": 1,
  "venue_id": 5,
  "most_players": 6,
  "target_level": "B",
  "booking_date": "2026-05-25",
  "time_slot": "14:00-16:00",
  "duration": "2 小時",
  "total_price": 1200.00,
  "gender_limit": "不限", 
  "description": "歡迎大家來打球，請自備飲水。"
}
```
*\*註：`total_price` 限制 0 ~ 10,000 元。*

---

## 三、 參與與候補機制 (Match Participants)

### 1. 報名參加/排候補
- **路由路徑：** `POST /api/games/{game_id}/join`
- **說明：** 根據目前人數自動判斷為正取或候補。主揪發起球局時自動加入，無法重複點擊報名。

### 2. 取消報名/退出球局
- **路由路徑：** `DELETE /api/games/{game_id}/cancel`
- **說明：** 若超過免費取消期限，後端將自動執行扣除信譽分數（credit_point）的邏輯。

### 3. 主揪回報場地狀態
- **路由路徑：** `PATCH /api/games/{game_id}/venue-status`
- **說明：** 活動開始前 30 分鐘，主揪確認是否佔到場地。
**傳入參數：**
```json
{
  "status": "已佔到", 
  "note": "在第三球場，我穿黃色球衣"
}
```

---

## 四、 主揪佈告欄模組 (Host Announcements)

### 1. 取得球局佈告欄歷史紀錄
- **路由路徑：** `GET /api/games/{game_id}/announcements`
- **說明：** 參與者或主揪進入揪團詳情頁時，點擊浮動按鈕取得該球局的佈告欄訊息。

**回傳範例 (Response 200)：**
```json
[
  {
    "id": 1,
    "text": "大家記得帶自己的球具跟水壺喔！",
    "time": "10:00 AM"
  }
]
```

### 2. 主揪發佈新公告
- **路由路徑：** `POST /api/games/{game_id}/announcements`
- **說明：** 僅限該球局的主揪 (Host) 呼叫。用於發佈單向通知給所有參與者。
- **權限限制：** 若非主揪呼叫，應回傳 `403 Forbidden`。

**傳入參數：**
```json
{
  "text": "因場地問題，時間延後 10 分鐘，請見諒。"
}
```

---

## 五、 檢舉與信譽模組 (Reports)

### 1. 提交檢舉
- **路由路徑：** `POST /api/reports`
- **說明：** 針對球局中的不良行為進行檢舉。支援主揪專屬原因。
- **[V1.3 新增限制]**：**防重複檢舉機制**。同一使用者 (reporting_user_id) 針對同一球局 (game_id) 的同一對象 (reported_user_id) 僅能檢舉一次。若重複檢舉將回傳 `409 Conflict`。

**傳入參數：**
```json
{
  "game_id": 152,
  "reported_user_id": 8,
  "reason": "未回報場地",
  "detail": "到了現場發現主揪根本沒訂場地，浪費大家時間"
}
```

---

## 六、 通知系統 (Notifications)

### 1. 取得通知列表
- **路由路徑：** `GET /api/notifications`
- **說明：** 包含活動開始前一天、前一小時的自動排程提醒，以及主揪狀態更新。

### 2. 標記通知為已讀
- **路由路徑：** `PATCH /api/notifications/{notification_id}/read`

---

## 七、 氣象與環境 API (Weather & AQI)

### 1. 取得大廳即時天氣與 AQI
- **路由路徑：** `GET /api/weather/aqi`
- **說明：** 回傳今日天氣狀況、氣溫與空氣品質指標 (AQI) 供大廳 Widget 顯示。
**回傳範例：**
```json
{
  "location": "桃園市",
  "temperature": 26,
  "condition": "多雲時晴",
  "aqi": 45
}
```

---

## 八、 管理員與 Demo 支援模組 (Admin & Feedback)

### 1. 使用者發送回饋
- **路由路徑：** `POST /api/feedback`

**傳入參數：**
```json
{
  "type": "建議", 
  "content": "希望增加羽球場地..."
}
```
*\*類型：建議、錯誤、場地、其他。*

### 2. 管理員取得回饋清單 (限 Admin)
- **路由路徑：** `GET /api/admin/feedbacks`
- **Query 參數：** `?is_handled=false` (可篩選出尚未處理的回饋)

### 3. 標記回饋已完成 (結案/忽略) **[V1.3 更新]**
- **路由路徑：** `PUT /api/admin/feedbacks/{feedback_id}/handle`
- **說明：** 取消原有的直接刪除機制，改採單一布林值 `is_handled` 紀錄。只要管理員標記完成（包含採納建議或略過），後端即將該欄位設為 `true`，以供保留歷史紀錄並簡化狀態流轉。
**傳入參數：**
```json
{
  "is_handled": true
}
```

### 4. 場地管理與刪除 **[V1.3 新增限制]**
- **路由路徑：** `DELETE /api/admin/venues/{venue_id}`
- **說明：** 刪除系統內建的運動場地。
- **[防呆限制]**：執行刪除前，後端必須檢查 `Games` 資料表中，是否有狀態為「未結束（招募中、進行中）」的球局正在使用該 `venue_id`。若有，必須阻擋刪除動作並回傳 `409 Conflict` 錯誤。

### 5. 管理員發佈系統公告
- **發佈公告：** `POST /api/admin/announcements`
- **取得公告 (公開)：** `GET /api/announcements`

### 6. 管理員數據分析 (Dashboard)
- **路由路徑：** `GET /api/admin/analytics`
- **回傳內容：** 今日活躍人數、進行中球局數、各類運動占比、近日活動熱度趨勢。

### 7. Demo 工具 (模擬環境)
- **調整房間狀態：** `PATCH /api/admin/demo/games/{game_id}/status`
- **模擬氣象適合度：** `PATCH /api/admin/demo/weather`
