# 「不揪ㄛ」揪團平台——系統文件庫 (Documentation Index)

歡迎閱讀「不揪喔」運動與麻將揪團平台的技術設計文檔庫。本文件庫包含以下核心設計說明，供前後端開發人員與系統管理員閱讀：

---

## 📄 核心文件目錄

### 1. 📂 [系統設計文件 (System Design)](system_design.md)
- 介紹系統概述、Django 技術架構與快取規劃。
- 詳細解析 9 大業務功能模組的核心實作邏輯。
- 詳細說明 Haversine 地理篩選、天氣指數、免費場地超時確認與自動候補轉正等核心演算法。

### 2. 🗄️ [資料庫設計文件 (Database Design)](database.md)
- 對齊專案最新版之 [nojo528.sql](file:///c:/Users/cyhs1/OneDrive/桌面/明和/cgu/資料庫/database_project/db/nojo528.sql) 結構。
- 提供完整系統的 Entity-Relationship Diagram (ERD) 關係圖。
- 詳細說明 17 張資料表的完整欄位屬性、資料型態、索引與外鍵級聯操作約束。

### 3. 🔌 [前後端 API 規格書 (API Specification)](api_format.md)
- 定義系統 Base URL 為 `/api`。
- 提供所有核心模組（使用者、球局房間、候補、收藏、檢舉管理、場館場地、通知與 OpenData 同步）之路由、參數、JSON 回傳格式與邏輯。

---

## 🛠️ 其他輔助文件
- [API 修改意見與需求追加明細](api_修改意見.md)
- 專案根目錄 [README.md](../README.md)
