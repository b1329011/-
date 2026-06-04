# 「不揪ㄛ」揪團平台——前後端 API 規格書 (V1.2 更新草案)

本文件定義「不揪ㄛ」運動揪團平台前端與後端之資料傳輸介面。本版本納入了 **SABC 程度系統**、**強制性個人資料驗證**、**大頭貼功能**、**精確費用/時長設定**及**管理員回饋系統**，並根據最新前端實作（檢舉、通知、AQI、報名流程等）補齊缺失的 API。

**文件版本：** V1.2 (草案)  
**基礎網址 (Base URL)：** `/api`

---

## 一、 使用者認證與個人檔案模組 (Auth & Users)

### 1. 使用者註冊與登入
- **路由路徑：** `POST /api/auth/login`
- **說明：** 使用者首次登入即自動註冊。手機號碼為唯一識別。

| 參數 (JSON Body) | 必填 | 格式 | 說明 |
| :--- | :--- | :--- | :--- |
| name | 是 | String | 球友姓名或暱稱 |
| phone | 是 | String | 聯絡電話，格式需為 `09xxxxxxxx` |
| birthday | 是 | Date | 出生年月日 (YYYY-MM-DD)。**註冊後不得修改** |
| gender | 是 | String | 性別 ('男' 或 '女') |

### 2. 取得個人資料與信譽積分
- **路由路徑：** `GET /api/users/profile`

**回傳範例 (Response 200)：**
```json
{
  "user_id": 1,
  "name": "陳球友",
  "phone": "0912345678",
  "birthday": "2006-06-25",
  "gender": "男",
  "avatar_url": "https://example.com/avatars/user1.jpg",
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

### 3. 更新個人資料
- **路由路徑：** `PUT /api/users/profile`
- **限制：** `birthday` 欄位不接受修改，若傳入將被忽略。

| 參數 (JSON Body) | 必填 | 說明 |
| :--- | :--- | :--- |
| name | 否 | 暱稱修改 |
| phone | 否 | 需符合 09xxxxxxxx 格式 |
| bio | 否 | 個人簡介 |
| avatar | 否 | Base64 字串或圖片檔案 (用於上傳頭貼) |
| levels | 否 | 整體 SABC 程度物件修改 |

### 4. 能力程度定義 (SABC 系統)
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
| split_price | **自動計算：** `ceil(total_price / most_players)`。若 `is_free=true` 則為 0 |
| duration | 預計時長，例如 "2 小時" |
| description | 揪團說明 / 備註 |
| facilities | 場地設施陣列（後端根據 `venue_id` 自動帶入） |
| gender_limit | 性別限制 ('不限', '限男', '限女') **[新增]** |

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
  "is_free": false,
  "total_price": 1200.00,
  "gender_limit": "不限", 
  "description": "歡迎大家來打球，請自備飲水。"
}
```
*\*註：`total_price` 限制 0 ~ 10,000 元。*

---

## 三、 參與與候補機制 (Match Participants) **[V1.2 新增]**

### 1. 報名參加/排候補
- **路由路徑：** `POST /api/games/{game_id}/join`
- **說明：** 根據目前人數自動判斷為正取或候補。

### 2. 取消報名/退出球局
- **路由路徑：** `DELETE /api/games/{game_id}/cancel`
- **說明：** 若超過免費取消期限（如活動開始前 24 小時），後端將自動執行扣除信譽分數（credit_point）的邏輯。

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

## 四、 檢舉與信譽模組 (Reports) **[V1.2 新增]**

### 1. 提交檢舉
- **路由路徑：** `POST /api/reports`
- **說明：** 針對球局中的不良行為進行檢舉。支援主揪專屬原因。

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

## 五、 通知系統 (Notifications) **[V1.2 新增]**

### 1. 取得通知列表
- **路由路徑：** `GET /api/notifications`
- **說明：** 包含活動開始前一天、前一小時的自動排程提醒，以及主揪狀態更新。

### 2. 標記通知為已讀
- **路由路徑：** `PATCH /api/notifications/{notification_id}/read`

---

## 六、 氣象與環境 API (Weather & AQI) **[V1.2 新增]**

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

## 七、 管理員與 Demo 支援模組 (Admin & Feedback)

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

### 3. 管理員發佈系統公告
- **發佈公告：** `POST /api/admin/announcements`
- **取得公告 (公開)：** `GET /api/announcements`

### 4. 管理員數據分析 (Dashboard)
- **路由路徑：** `GET /api/admin/analytics`
- **回傳內容：** 今日活躍人數、進行中球局數、各類運動占比、近日活動熱度趨勢。

### 5. Demo 工具 (模擬環境)
- **調整房間狀態：** `PATCH /api/admin/demo/games/{game_id}/status`
- **模擬氣象適合度：** `PATCH /api/admin/demo/weather`
