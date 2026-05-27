# 「不揪ㄛ」揪團平台——前後端 API 規格書 (V1.1 修訂版)

本文件定義「不揪ㄛ」運動揪團平台前端與後端之資料傳輸介面。本版本納入了 **SABC 程度系統**、**強制性個人資料驗證**、**大頭貼功能**、**精確費用/時長設定**及**管理員回饋系統**。

**文件版本：** V1.1  
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

## 二、 球局房間模組 (GamesMatches CRUD)

### 1. 取得球局列表
- **路由路徑：** `GET /api/games`

| 回傳 JSON 欄位 | 說明 |
| :--- | :--- |
| split_price | **自動計算：** `ceil(total_price / most_players)`。若 `is_free=true` 則為 0 |
| duration | 預計時長，例如 "2 小時" |
| description | 揪團說明 / 備註 |
| facilities | 場地設施陣列（後端根據 `venue_id` 自動帶入） |

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
  "description": "歡迎大家來打球，請自備飲水。"
}
```
*\*註：`total_price` 限制 0 ~ 10,000 元。*

---

## 三、 管理員與 Demo 支援模組 (Admin & Feedback)

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

### 3. 管理員發佈系統公告 (Announcements)
- **發佈公告：** `POST /api/admin/announcements`
- **取得公告 (公開)：** `GET /api/announcements`

### 4. 管理員數據分析 (Dashboard)
- **路由路徑：** `GET /api/admin/analytics`
- **回傳內容：** 今日活躍人數、進行中球局數、各類運動占比、近日活動熱度趨勢。

### 5. Demo 工具 (模擬環境)
- **調整房間狀態：** `PATCH /api/admin/demo/games/{game_id}/status`
- **模擬氣象適合度：** `PATCH /api/admin/demo/weather` (傳入 0-100 之數值)

---

## 四、 參與與候補機制 (Match Participants)

- **自動遞補：** 成員退出時，系統自動將候補第一順位轉為正式，並重新計算所有成員的 `split_price`（若為總額分攤模式）。
- **到場確認：** 主揪需於開局前 15 分鐘完成確認，否則系統自動解散並扣除信譽積分。
