# 「不揪ㄛ」揪團平台——資料庫缺漏欄位分析文件 (Database Gap Analysis)

本文件詳細彙整了**現有資料庫結構**（基於 [nojo528.sql](file:///c:/Users/cyhs1/OneDrive/桌面/明和/cgu/資料庫/database_project/db/nojo528.sql)）與**最新 API 規格書 (V1.2 更新草案)** 之間的落差。本文提供完整的欄位缺漏說明，並附上供後續手動於 MySQL/MariaDB 執行的 SQL 升級指令（DDL）。

---

## 📌 缺漏概要

最新 API 規格書 (V1.2) 引入了以下核心功能：
1. **SABC 程度系統**（將球局程度要求由 `beginner`, `casual`, `advanced` 對齊至 `S`, `A`, `B`, `C` 等級）。
2. **精確費用/時長與性別限制設定**（需要 `duration`, `is_free`, `description`, `gender_limit` 等欄位）。
3. **主揪場地確認與回報狀態**（需要 `venue_status` 與 `venue_note`）。
4. **檢舉系統強化**（需要支援自訂的檢舉原因 `reason` 與詳細內容 `detail`）。

目前實體資料庫中缺少了這些相對應的欄位或屬性限制。

---

## 🔍 詳細缺漏清單與分析

### 1. `gamesmatches` 資料表 (球局房間表)

| 缺漏欄位/屬性 | 資料型態 | 預設值 | 規格說明 / V1.2 用途 |
| :--- | :--- | :--- | :--- |
| `gender_limit` | `varchar(10)` | `'不限'` | 性別限制：`'不限'`, `'限男'`, `'限女'`。 |
| `venue_status` | `varchar(20)` | `'未確認'` | 主揪回報之場地確認狀態：如 `'已佔到'`, `'未佔到'`, `'未確認'`。 |
| `venue_note` | `text` | `NULL` | 主揪佔場時填寫的具體說明（例如：在第三球場，我穿黃色衣服）。 |
| `duration` | `varchar(50)` | `'2 小時'` | 球局預估時長（如 `'1.5 小時'`, `'2 小時'`）。現有 SQL 表無此欄位。 |
| `is_free` | `tinyint(1)` | `0` | 是否免費球局。現有 SQL 表無此欄位。 |
| `description` | `text` | `NULL` | 球局說明或備註。現有 SQL 表無此欄位。 |
| `target_level` | `enum / varchar` | — | **屬性限制缺漏：** 現有 SQL 限制為 `enum('beginner','casual','advanced')`，不支援 SABC 等級（如 `'S'`, `'A'`, `'B'`, `'C'`）。建議轉為 `varchar(20)` 以完美相容所有格式。 |

---

### 2. `reports` 資料表 (賽後使用者檢舉表)

| 缺漏欄位/屬性 | 資料型態 | 預設值 | 規格說明 / V1.2 用途 |
| :--- | :--- | :--- | :--- |
| `reason` | `varchar(100)` | `NULL` | 檢舉原因字串。現有表僅能關聯 `penalty_rules` 的 `rule_id`，無法儲存前端直接傳遞的自訂原因（如 `'未回報場地'`）。 |
| `detail` | `text` | `NULL` | 檢舉詳細內容說明（如 `'到了現場發現主揪根本沒訂場地...'`）。 |

---

### 3. `users` 資料表 (使用者與管理員帳號表)

| 缺漏欄位/屬性 | 資料型態 | 預設值 | 規格說明 / 用途 |
| :--- | :--- | :--- | :--- |
| `gender` | `varchar(10)` | `NULL` | 使用者性別：`'男'` 或 `'女'` (V1.2 欄位，Django 已使用)。 |
| `avatar_url` | `varchar(255)` | `NULL` | 大頭貼圖片連結網址。 |
| `bio` | `text` | `NULL` | 個人簡介。 |
| `password` | `varchar(128)` | — | **Django 認證系統欄位 (必填)：** 儲存雜湊後的密碼。現有 MySQL 實體表缺少此欄位，會導致登入/查詢時發生 `OperationalError: Unknown column 'users.password'` 錯誤。 |
| `last_login` | `datetime(6)` | `NULL` | **Django 認證系統欄位：** 記錄最後登入時間。 |
| `is_superuser` | `tinyint(1)` | `0` | **Django 認證系統欄位：** 標記是否為超級使用者。 |
| `is_staff` | `tinyint(1)` | `0` | **Django 認證系統欄位：** 標記是否具備工作人員權限。 |
| `is_active` | `tinyint(1)` | `1` | **Django 認證系統欄位：** 標記帳號是否有效。 |
| `date_joined` | `datetime(6)` | — | **Django 認證系統欄位：** 帳號創立日期。 |

---

## 🛠️ MySQL/MariaDB 升級 SQL 指令 (DDL)

若您之後準備手動更新 MySQL 資料庫，可以直接執行以下 SQL 指令以補全所有缺漏的欄位，而不破壞現有的任何資料：

```sql
-- ==========================================
-- 1. 更新 `gamesmatches` 資料表
-- ==========================================

-- 新增性別限制、佔場回報狀態、佔場備註
ALTER TABLE `gamesmatches` 
  ADD COLUMN `gender_limit` varchar(10) NOT NULL DEFAULT '不限' COMMENT '性別限制 (不限/限男/限女)',
  ADD COLUMN `venue_status` varchar(20) NOT NULL DEFAULT '未確認' COMMENT '佔場確認狀態',
  ADD COLUMN `venue_note` text NULL COMMENT '佔場位置或衣服說明備註';

-- 新增時長、是否免費、備註說明 (解決與 Django Model 對齊缺漏)
ALTER TABLE `gamesmatches`
  ADD COLUMN `duration` varchar(50) NOT NULL DEFAULT '2 小時' COMMENT '預計時長',
  ADD COLUMN `is_free` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否免費',
  ADD COLUMN `description` text NULL COMMENT '揪團說明備註';

-- 調整 `target_level` 欄位以支援 SABC 等級系統 (避免 Enum 限制報錯)
ALTER TABLE `gamesmatches` 
  MODIFY COLUMN `target_level` varchar(20) DEFAULT NULL COMMENT '要求程度 (SABC或傳統級別)';


-- ==========================================
-- 2. 更新 `reports` 資料表
-- ==========================================

-- 新增檢舉原因與詳細內容說明
ALTER TABLE `reports`
  ADD COLUMN `reason` varchar(100) NULL COMMENT '前端檢舉原因',
  ADD COLUMN `detail` text NULL COMMENT '檢舉詳細內容說明';


-- ==========================================
-- 3. 更新 `users` 資料表 (包含 Django 系統必要欄位)
-- ==========================================

-- 新增性別、頭貼連結、個人簡介 (解決 V1.2 對齊)
ALTER TABLE `users`
  ADD COLUMN `gender` varchar(10) NULL COMMENT '性別 (男/女)',
  ADD COLUMN `avatar_url` varchar(255) NULL COMMENT '頭貼網址',
  ADD COLUMN `bio` text NULL COMMENT '個人簡介';

-- 新增 Django 使用者與權限管理核心系統欄位 (解決 1054 Unknown column 'users.password' 等錯誤)
ALTER TABLE `users`
  ADD COLUMN `password` varchar(128) NOT NULL DEFAULT 'pbkdf2_sha256$870000$default_placeholder_hash$' COMMENT 'Django密碼雜湊',
  ADD COLUMN `last_login` datetime(6) NULL COMMENT '最後登入時間',
  ADD COLUMN `is_superuser` tinyint(1) NOT NULL DEFAULT 0 COMMENT '超級用戶標記',
  ADD COLUMN `is_staff` tinyint(1) NOT NULL DEFAULT 0 COMMENT '管理後台權限標記',
  ADD COLUMN `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '帳號啟用狀態',
  ADD COLUMN `date_joined` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '帳號創立日期';
```

---

## 💡 Django 後端相容處理方案 (Fake Migrations)

為了讓後端 Django 專案能正常啟動並識別這些新欄位，我們在後端程式碼中已進行如下設定：
1. 在 `api_v1/models.py` 中宣告這些新欄位（如此 Python 程式碼能支援欄位讀寫）。
2. 執行 `makemigrations` 產生新版遷移檔 (`0006_...`)。
3. **不直接對 MySQL 進行 migrate**（防止資料庫名稱不符報錯），而是使用 `--fake` 來略過實體資料庫修改，僅在 Django 遷移歷史中標記完成。
   ```powershell
   env\Scripts\python manage.py migrate api_v1 0006 --fake
   ```
4. 如果是在 SQLite 本機開發環境，則可以直接執行 `migrate` 建立完整環境。
