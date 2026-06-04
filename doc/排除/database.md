# 「不揪ㄛ」揪團平台——資料庫設計文件 (Database Design)

本文件詳細定義「不揪喔」運動與麻將揪團平台的資料庫結構設計，對齊專案最新版本之 [nojo528.sql](file:///c:/Users/cyhs1/OneDrive/桌面/明和/cgu/資料庫/database_project/db/nojo528.sql)。包含完整實體關係圖 (ERD)、各資料表架構 (Schema) 詳解、索引約束與外鍵級聯規則。

---

## 一、 實體關係圖 (Entity-Relationship Diagram)

以下為本平台 17 張資料表的關聯網絡圖，使用 Mermaid 語法繪製：

```mermaid
erDiagram
    users {
        int user_id PK "AUTO_INCREMENT"
        enum role "角色: 'user', 'admin'"
        varchar name "姓名/暱稱"
        int credit_point "信譽點數 (預設100)"
        varchar phone UK "電話號碼 (唯一鍵)"
        date birth_date "生日"
    }
    user_sport_levels {
        int user_id PK, FK "使用者ID"
        int sport_id PK, FK "項目ID"
        enum level "程度: 'C(beginner)', 'B(advanced)', 'A(Veteran)', 'S(Elite)'"
        timestamp updated_at "最後更新時間"
    }
    sports {
        int sport_id PK "AUTO_INCREMENT"
        varchar sport_name UK "運動名稱 (唯一鍵)"
    }
    address {
        int address_id PK "AUTO_INCREMENT"
        varchar city "城市"
        varchar district "行政區"
        varchar street_line "道路與門牌"
    }
    venues {
        int venue_id PK "AUTO_INCREMENT"
        int address_id FK "地址ID"
        varchar name "場館名稱"
        json opening_hours "營業時間 (JSON)"
        enum types "場地類型: 'indoor', 'outdoor', 'semi-outdoor'"
    }
    facilities {
        int facility_id PK "AUTO_INCREMENT"
        varchar name UK "設施名稱 (唯一鍵)"
    }
    venue_facilities {
        int venue_id PK, FK "場館ID"
        int facility_id PK, FK "設施ID"
    }
    court {
        int court_id PK "AUTO_INCREMENT"
        int venue_id FK "場館ID"
        tinyint occupied "是否佔用"
        int base_price "球場基本租借費用"
    }
    court_conflicts {
        int conflict_id PK "AUTO_INCREMENT"
        int court_id_1 FK "互斥球場1"
        int court_id_2 FK "互斥球場2"
    }
    court_sports {
        int court_id PK, FK "場地ID"
        int sport_id PK, FK "支援運動項目ID"
    }
    gamesmatches {
        int game_id PK "AUTO_INCREMENT"
        int user_id FK "主揪/房主ID"
        int court_id FK "球場ID"
        int sport_id FK "運動項目ID"
        int least_players "最少成團人數"
        int most_players "最大人數上限"
        enum target_level "要求程度: 'beginner', 'casual', 'advanced'"
        json weather "天氣資訊 (JSON)"
        int air_index "AQI 空氣品質指數"
        enum match_status "狀態: 'recruiting', 'full', 'closed'"
        date booking_date "活動日期"
        varchar time_slot "活動時段"
        decimal total_price "場地總價"
        tinyint deposit_required "是否需要訂金"
        timestamp cancel_deadline "免費取消期限"
        tinyint is_confirmed "主揪到場確認狀態"
        enum booking_status "預約狀態: 'pending', 'booked', 'cancelled'"
    }
    keep {
        int user_id PK, FK "收藏者ID"
        int game_id PK, FK "球局ID"
    }
    match_participants {
        int list_id PK "AUTO_INCREMENT"
        int game_id FK "球局ID"
        int user_id FK "參戰球友ID"
        timestamp joined_at "加入時間"
    }
    notification {
        int notification_id PK "AUTO_INCREMENT"
        int game_id FK "球局ID"
        text message "通知內容"
        timestamp created_at "建立時間"
        tinyint is_read "是否已讀"
    }
    reports {
        int report_id PK "AUTO_INCREMENT"
        int game_id FK "關聯球局ID"
        int reporter_id FK "檢舉人ID"
        int offender_id FK "被檢舉人ID"
        int rule_id FK "對應規則ID"
        text admin_note "管理員審核備註"
        timestamp reviewed_at "審核時間"
        int reviewed_by FK "審核管理員ID"
        enum status "審核狀態: 'pending', 'deducted', 'rejected'"
    }
    penalty_rules {
        int rule_id PK "AUTO_INCREMENT"
        varchar reason UK "違規原因 (唯一鍵)"
        int points_deducted "扣除信譽分數值"
    }
    blacklist {
        int blacklist_id PK "AUTO_INCREMENT"
        int user_id FK "使用者ID"
        timestamp added_at "封鎖時間"
        timestamp removed_at "解封時間 (可為空)"
    }

    users ||--o{ user_sport_levels : "設定運動能力"
    sports ||--o{ user_sport_levels : "定義分級項目"
    address ||--o{ venues : "擁有物理地址"
    venues ||--o{ venue_facilities : "具備設施"
    facilities ||--o{ venue_facilities : "關聯設施表"
    venues ||--o{ court : "劃分獨立球場"
    court ||--o{ court_conflicts : "涉及衝突1"
    court ||--o{ court_conflicts : "涉及衝突2"
    court ||--o{ court_sports : "具備支援項目"
    sports ||--o{ court_sports : "關聯運動項目"
    users ||--o{ gamesmatches : "發起揪團活動"
    court ||--o{ gamesmatches : "佔用實體場地"
    sports ||--o{ gamesmatches : "屬於指定活動"
    users ||--o{ keep : "收藏球局"
    gamesmatches ||--o{ keep : "被收藏"
    gamesmatches ||--o{ match_participants : "招募正式隊員"
    users ||--o{ match_participants : "正式參戰"
    gamesmatches ||--o{ notification : "發送通知"
    gamesmatches ||--o{ reports : "產生糾紛背景"
    users ||--o{ reports : "發起檢舉"
    users ||--o{ reports : "被指控違規"
    users ||--o{ reports : "指派審理管理員"
    penalty_rules ||--o{ reports : "適用處罰條款"
    users ||--o{ blacklist : "被寫入封鎖名單"
```

---

## 二、 資料表 Schema 詳解

### 1. `users` (使用者與管理員帳號表)
- **說明**: 儲存平台所有使用者與管理員的基本資料、聯絡電話、生日及累計信譽積分。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `role` | `enum('user','admin')` | 否 | `'user'` | 權限身分 |
| `name` | `varchar(100)` | 否 | | 姓名或暱稱 |
| `credit_point` | `int(11)` | 否 | `100` | 信用積分，可用於信譽停權評估 |
| `phone` | `varchar(20)` | 是 | `NULL` | 手機號碼，唯一限制鍵 (Unique Key) |
| `birth_date` | `date` | 是 | `NULL` | 用戶生日，供年齡計算與驗證 |

---

### 2. `user_sport_levels` (使用者運動等級分級表)
- **說明**: 紀錄使用者在不同運動項目下的程度分級，用以媒合實力相近的球友。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `int(11)` | 否 | | 複合主鍵之一 & 外部鍵 (FK) 連接 `users.user_id` |
| `sport_id` | `int(11)` | 否 | | 複合主鍵之二 & 外部鍵 (FK) 連接 `sports.sport_id` |
| `level` | `enum('C(beginner)','B(advanced)','A(Veteran)','S(Elite)')` | 否 | | 運動能力級別 (新手 / 進階 / 資深 / 精英) |
| `updated_at` | `timestamp` | 否 | *CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP* | 自動更新修改時間 |

---

### 3. `sports` (支援運動項目表)
- **說明**: 平台支援之核心活動類別定義（如籃球、羽球、排球等）。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `sport_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `sport_name` | `varchar(50)` | 否 | | 運動名稱，唯一限制鍵 (Unique Key) |

---

### 4. `address` (場館物理地址表)
- **說明**: 場館的定位與物理地址解析，將行政區細分利於地理檢索。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `address_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `city` | `varchar(50)` | 否 | | 縣市 (如：台北市、新北市) |
| `district` | `varchar(50)` | 否 | | 行政區 (如：板橋區、大安區) |
| `street_line` | `varchar(255)` | 否 | | 道路與門牌詳細資訊 |

---

### 5. `venues` (場館與球館表)
- **說明**: 儲存各大型運動場館（如國民運動中心、球館）的基本資訊與營業時間。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `venue_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `address_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `address.address_id` |
| `name` | `varchar(100)` | 否 | | 場館或球館名稱 |
| `opening_hours` | `json` | 是 | `NULL` | 營業時間範圍 JSON |
| `types` | `enum('indoor','outdoor','semi-outdoor')` | 是 | `NULL` | 場地環境類型，供天氣篩選邏輯使用 |

---

### 6. `facilities` (公共設施定義表)
- **說明**: 平台支援之場地硬體設施主檔（如：淋浴間、停車場、冷氣等）。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `name` | `varchar(50)` | 否 | | 設施名稱，唯一限制鍵 (Unique Key) |

---

### 7. `venue_facilities` (場館設施關聯多對多表)
- **說明**: 連接 `venues` 與 `facilities` 表，標記各場館擁有之設施。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `venue_id` | `int(11)` | 否 | | 複合主鍵之一 & 外部鍵 (FK) 連接 `venues.venue_id` |
| `facility_id` | `int(11)` | 否 | | 複合主鍵之二 & 外部鍵 (FK) 連接 `facilities.facility_id` |

---

### 8. `court` (場館內實體場地/桌次表)
- **說明**: 代表一個場館內複數的實體球場（如 A 面場、B 面場）或桌次，並記錄其基本費用。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `court_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `venue_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `venues.venue_id` |
| `occupied` | `tinyint(1)` | 否 | `0` | 是否有實體佔用中 (布林標記) |
| `base_price` | `int(5)` | 否 | | 該球場的基本預約租借價格 |

---

### 9. `court_conflicts` (場地衝突與共用互斥表)
- **說明**: 解決實體球場邊界交疊或「半場/全場」租借互斥的邏輯。如全場佔用時，相應的兩個半場應自動互斥關閉預約。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `conflict_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `court_id_1` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `court.court_id` |
| `court_id_2` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `court.court_id`，且與 `court_id_1` 構成聯合唯一約束 |

---

### 10. `court_sports` (場地支援項目表)
- **說明**: 定義特定場地所能提供的運動類型。例如同一個多功能羽網球場，同時可支援羽毛球與網球。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `court_id` | `int(11)` | 否 | | 複合主鍵之一 & 外部鍵 (FK) 連接 `court.court_id` |
| `sport_id` | `int(11)` | 否 | | 複合主鍵之二 & 外部鍵 (FK) 連接 `sports.sport_id` |

---

### 11. `gamesmatches` (揪團房間表)
- **說明**: 揪團核心商務主表，記錄發起球局（或活動局）、時間段、所需人數、費用、取消期限、是否支付訂金與氣象環境參數。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `game_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `user_id` | `int(11)` | 否 | | 主揪用戶，外部鍵 (FK) 連接 `users.user_id` |
| `court_id` | `int(20)` | 否 | | 實體預約場地，外部鍵 (FK) 連接 `court.court_id` |
| `sport_id` | `int(11)` | 否 | | 運動類型，外部鍵 (FK) 連接 `sports.sport_id` |
| `least_players`| `int(11)` | 否 | | 最少成團人數門檻，未達則不成團 |
| `most_players` | `int(11)` | 否 | | 房間上限人數 |
| `target_level` | `enum('beginner','casual','advanced')`| 是 | `NULL`| 開房限制程度需求 |
| `weather` | `json` | 是 | `NULL`| 記錄當前天氣狀況與遊玩指數 (JSON) |
| `air_index` | `int(11)` | 是 | `NULL`| 空氣品質 AQI 指數 |
| `match_status` | `enum('recruiting','full','closed')`| 否 | `'recruiting'`| 成團媒合狀態 |
| `booking_date` | `date` | 是 | `NULL`| 球局預訂日期 |
| `time_slot` | `varchar(50)` | 是 | `NULL`| 活動時段 (如：'18:00-20:00') |
| `total_price` | `decimal(10,2)`| 是 | `NULL`| 場地總價（後端依此計算分攤金額） |
| `deposit_required`| `tinyint(1)`| 否 | `0` | 臨時取消是否需要扣收訂金 |
| `cancel_deadline`| `timestamp` | 是 | `NULL`| 免費取消與退款的截止時間點 |
| `is_confirmed` | `tinyint(1)` | 否 | `0` | 主揪到場實體站位確認狀態 |
| `booking_status`| `enum('pending','booked','cancelled')`| 否 | `'pending'`| 訂場與交易狀態記錄 |

---

### 12. `keep` (球友收藏球局表)
- **說明**: 多對多關係表，儲存使用者對特定進行中揪團活動的收藏與關注。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `int(11)` | 否 | | 複合主鍵之一 & 外部鍵 (FK) 連接 `users.user_id` |
| `game_id` | `int(11)` | 否 | | 複合主鍵之二 & 外部鍵 (FK) 連接 `gamesmatches.game_id` |

---

### 13. `match_participants` (球局正式參與成員表)
- **說明**: 紀錄每一局已成功「加一」並被分配為正式隊員的球友清單。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `list_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `game_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `gamesmatches.game_id` |
| `user_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `users.user_id` |
| `joined_at` | `timestamp` | 否 | *CURRENT_TIMESTAMP* | 加入此球局的精確時間戳 |

*註：`game_id` 與 `user_id` 設有聯合唯一索引 (Unique Index)，嚴禁同一使用者在同一球局中重複報名。*

---

### 14. `notification` (通知紀錄表)
- **說明**: 儲存發送給各球局的系統通知訊息，包含預約狀態更新、成團提醒等。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `notification_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `game_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `gamesmatches.game_id` |
| `message` | `text` | 否 | | 通知內容文字 |
| `created_at` | `timestamp` | 否 | *CURRENT_TIMESTAMP* | 通知建立時間戳 |
| `is_read` | `tinyint(1)` | 是 | `0` | 是否已讀 (0: 未讀, 1: 已讀) |

---

### 15. `reports` (賽後使用者檢舉審查表)
- **說明**: 提供賽後檢舉機制，處理放鳥、未付分攤費用或惡意行為，由管理員在後台審查裁決。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `report_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `game_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `gamesmatches.game_id` |
| `reporter_id` | `int(11)` | 否 | | 檢舉發起人，外部鍵 (FK) 連接 `users.user_id` |
| `offender_id` | `int(11)` | 否 | | 被檢舉人，外部鍵 (FK) 連接 `users.user_id` |
| `rule_id` | `int(11)` | 是 | `NULL` | 適用之處罰規章，外部鍵 (FK) 連接 `penalty_rules.rule_id` |
| `admin_note` | `text` | 是 | `NULL` | 管理員審查裁決備註 |
| `reviewed_at` | `timestamp` | 是 | `NULL` | 審核時間戳 |
| `reviewed_by` | `int(11)` | 是 | `NULL` | 承辦管理員，外部鍵 (FK) 連接 `users.user_id` |
| `status` | `enum('pending','deducted','rejected')`| 否 | `'pending'`| 檢舉狀態 (待審/已扣分/駁回) |

*註：`game_id`、`reporter_id` 與 `offender_id` 構成三元聯合唯一索引，每人在同一球局對同一違規者限檢舉一次。*

---

### 16. `penalty_rules` (信譽扣分懲處規章表)
- **說明**: 系統制定的信譽扣分基準與懲處規則。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `rule_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `reason` | `varchar(50)` | 否 | | 違規類型說明，唯一限制鍵 (Unique Key) |
| `points_deducted`| `int(11)` | 否 | | 該項違規所扣減的信譽分數值 (如：放鳥扣 20 分) |

*系統預設懲處規章包括：*
1. `no_show` (放鳥未到場): 扣 20 分
2. `not_paid` (未付分攤費): 扣 15 分
3. `bad_behavior` (不當行為): 扣 10 分
4. `verbal_abuse` (言語辱罵): 扣 10 分
5. `poor_attitude` (態度惡劣): 扣 10 分
6. `rank_mismatch` (實力不符): 扣 10 分
7. `harassment` (惡意騷擾): 扣 30 分
8. `physical_violence` (肢體衝突): 扣 60 分
9. `MLM` (推銷直銷): 扣 15 分

---

### 17. `blacklist` (黑名單封鎖紀錄表)
- **說明**: 紀錄被停權封鎖的使用者清單。
- **欄位結構**:

| 欄位名稱 | 資料型態 | 允許空值 | 預設值 | 備註 / 約束 |
| :--- | :--- | :--- | :--- | :--- |
| `blacklist_id` | `int(11)` | 否 | *AUTO_INCREMENT* | 主鍵 (PK) |
| `user_id` | `int(11)` | 否 | | 外部鍵 (FK) 連接 `users.user_id` |
| `added_at` | `timestamp` | 否 | *CURRENT_TIMESTAMP* | 寫入黑名單的停權時間 |
| `removed_at` | `timestamp` | 是 | `NULL` | 解封恢復正常使用的時間 (手動或自動) |

---

## 三、 約束與級聯傳遞規則 (Constraints & Cascade Rules)

最新資料庫版本引入了嚴格的資料完整性外鍵約束 (Foreign Key Constraints) 及級聯操作：

1. **使用者被動移除影響 (Cascade Delete User)**:
   - `blacklist` 設有外鍵 `blacklist_ibfk_1` 指向 `users`。當刪除使用者時，其對應的黑名單封鎖紀錄將**級聯刪除** (`ON DELETE CASCADE`)。
   - `user_sport_levels` 設有外鍵 `user_sport_levels_ibfk_1` 指向 `users`。當刪除使用者時，其所屬之所有運動等級紀錄將**級聯刪除** (`ON DELETE CASCADE`)。
   - `match_participants` 同理：使用者刪除時，其參戰登記亦同步**級聯刪除**。

2. **球局解散與刪除影響 (Cascade Delete Game)**:
   - `match_participants` 設有外鍵 `match_participants_ibfk_1` 指向 `gamesmatches`。球局解散或刪除時，全體已加入成員的對應明細將**自動清理** (`ON DELETE CASCADE`)。
   - `notification` 設有外鍵 `fk_notification_game` 指向 `gamesmatches`。當球局被實體刪除時，相關通知訊息將**級聯刪除** (`ON DELETE CASCADE`)。
   - `reports` 外鍵 `reports_ibfk_1`：若該球局被實體刪除，其衍生的賽後檢舉單將**級聯清除** (`ON DELETE CASCADE`)。
   - `keep` 外鍵 `keep_ibfk_2`：球局一旦消失，收藏該球局的明細也自動**級聯刪除**。

3. **場館與實體球場異動**:
   - `court` 指向 `venues`。當刪除場館時，該場館包含的所有實體球場將**級聯刪除**。
   - `gamesmatches` 指向 `court` 設有外鍵 `gamesmatches_ibfk_4`。若該實體球場資料遭到刪除，為保全現存揪團歷史，球局房的 `court_id` 欄位會維持。

4. **安全更新傳遞 (On Update Cascade)**:
   - 所有關聯的對外鍵皆配置 `ON UPDATE CASCADE` 約束。若管理員後台異動了主鍵值（如更改 `sport_id` 或 `user_id`），關聯資料表中所有涉及的欄位值將**自動完成同步更新**，絕不產生資料孤兒。
