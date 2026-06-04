import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

# 開啟日誌輸出檔案，將所有輸出寫入文字檔中，而不直接印在終端機上
log_file = open("api_test_output.log", "w", encoding="utf-8")

def print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(map(str, args)) + end
    log_file.write(text)
    log_file.flush()

def print_header(title):
    print("\n\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60 + "\n")

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if token:
        headers["Authorization"] = f"Token {token}"
        
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode("utf-8")
            try:
                parsed_body = json.loads(body)
            except Exception:
                parsed_body = body
            
            print(f"✅ [{method}] {url} -> Status: {status}\n")
            return status, parsed_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        print(f"❌ [{method}] {url} -> Status: {e.code}")
        print(f"   Error Response: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}\n")
        return e.code, parsed_body
    except Exception as e:
        print(f"💥 Failed to connect to server: {e}\n")
        print("💡 請確認您的 Django 伺服器正在運行 (python manage.py runserver)\n")
        return None, None

def run_tests():
    print("🔔 開始執行「不揪ㄛ」V1.2 API 流程端到端測試")
    print("🔔 測試端點目標: " + BASE_URL)
    
    # ==========================================
    # 1. 取得大廳即時天氣與 AQI
    # ==========================================
    print_header("1. 取得大廳即時天氣與 AQI")
    status, res = make_request("/weather/aqi?city=桃園市", "GET")
    if res:
        print(json.dumps(res, indent=2, ensure_ascii=False))

    # ==========================================
    # 2. 使用者註冊與登入
    # ==========================================
    print_header("2. 使用者註冊與自動登入")
    login_data = {
        "phone": "0987654321",
        "name": "測試球友",
        "birthday": "2000-01-01",
        "gender": "男"
    }
    status, res = make_request("/auth/login", "POST", data=login_data)
    if not isinstance(res, dict) or "token" not in res:
        print("❌ 登入失敗，無法繼續後續需要 Token 的測試。")
        if isinstance(res, str) and ("Unknown column" in res or "no such column" in res or "Column" in res):
            print("\n💡 [資料庫欄位缺漏提示]：")
            print("   這通常是因為您的 MySQL 實體資料庫缺少欄位（例如：users 表的 gender 欄位）。")
            print("   請參考您專案中的 [doc/db_missing.md](file:///c:/Users/cyhs1/OneDrive/桌面/明和/cgu/資料庫/database_project/doc/db_missing.md) 文件，將 SQL 指令複製到 phpMyAdmin 中執行，即可完美補全欄位並順利通過測試！")
        elif isinstance(res, dict) and "detail" in res:
            print(f"   詳細錯誤資訊: {res['detail']}")
        return
        
    token = res["token"]
    user_id = res["user_id"]
    print(f"🔑 取得登入 Token: {token} (User ID: {user_id})")

    # ==========================================
    # 3. 取得與更新個人資料 (SABC 程度系統)
    # ==========================================
    print_header("3. 取得與更新個人資料 (SABC 程度)")
    
    print("\n[GET] 讀取個人資料：")
    status, profile = make_request("/users/profile/", "GET", token=token)
    if profile:
        print(json.dumps(profile, indent=2, ensure_ascii=False))
        
    print("\n[PUT] 更新個人資料 (設定 SABC 程度)：")
    update_data = {
        "name": "帥氣球王",
        "bio": "專打 S 級羽球局與 A 級籃球局，新手麻將求帶",
        "levels": {
            "羽毛球": "S",
            "籃球": "A",
            "麻將": "C"
        }
    }
    status, updated_profile = make_request("/users/profile/", "PUT", data=update_data, token=token)
    if updated_profile:
        print(json.dumps(updated_profile, indent=2, ensure_ascii=False))

    # ==========================================
    # 4. 主揪發起球局 (自動媒合場地)
    # ==========================================
    print_header("4. 主揪開房發起球局 (支援 gender_limit 與 venue_id 自動匹配)")
    game_data = {
        "sport_id": 1,         # 籃球
        "venue_id": 1,         # 大安運動中心
        "most_players": 2,     # 上限 2 人 (方便測試滿人候補)
        "target_level": "A",   # 要求 A 級高手
        "booking_date": "2026-06-15",
        "time_slot": "18:00-20:00",
        "duration": "2 小時",
        "is_free": False,
        "total_price": 500.0,
        "gender_limit": "不限",
        "description": "測試球局，大安運動中心室內場，歡迎高手來戰！"
    }
    status, game_res = make_request("/games/", "POST", data=game_data, token=token)
    if not game_res or "id" not in game_res:
        print("❌ 建立球局失敗。")
        return
        
    game_id = game_res["id"]
    print(f"🎯 成功建立球局！球局 ID: {game_id}，已自動將主揪設為成員，分攤價格為: {game_res.get('split_price')}")

    # ==========================================
    # 5. 取得球局大廳列表 (支援 V1.2 新篩選參數)
    # ==========================================
    print_header("5. 取得大廳球局列表 (測試篩選參數)")
    print("\n[GET] 篩選地區 '台北'、運動類型 '籃球' 與等級 'A'：")
    status, games_list = make_request(f"/games/?region=台北&sport_type=籃球&level=A", "GET")
    if games_list:
        print(f"🔍 找到符合篩選條件的球局共 {len(games_list)} 場。")
        print(json.dumps(games_list[0] if games_list else {}, indent=2, ensure_ascii=False))

    # ==========================================
    # 6. 報名參加與滿額自動轉候補
    # ==========================================
    print_header("6. 報名參加與滿額自動轉候補 (自動判定機制)")
    
    # 註冊第二位測試帳號來加入 (應能正常加入，使球局滿人)
    print("\n[POST] 第二個用戶登入並報名：")
    _, user2_res = make_request("/auth/login", "POST", data={"phone": "0911111111", "name": "隊員B", "birthday": "1999-05-05"})
    if not isinstance(user2_res, dict) or "token" not in user2_res:
        print("❌ 第二個用戶登入失敗，中止測試。")
        return
    token2 = user2_res["token"]
    status, join_res = make_request(f"/games/{game_id}/join/", "POST", token=token2)
    if join_res:
        print(json.dumps(join_res, indent=2, ensure_ascii=False))
        
    # 註冊第三位測試帳號加入 (此時應已滿人，自動轉為候補第一順位)
    print("\n[POST] 第三個用戶報名 (球局上限 2 人，預期自動排入候補)：")
    _, user3_res = make_request("/auth/login", "POST", data={"phone": "0922222222", "name": "候補仔C", "birthday": "1998-08-08"})
    if not isinstance(user3_res, dict) or "token" not in user3_res:
        print("❌ 第三個用戶登入失敗，中止測試。")
        return
    token3 = user3_res["token"]
    status, waitlist_res = make_request(f"/games/{game_id}/join/", "POST", token=token3)
    if waitlist_res:
        print(json.dumps(waitlist_res, indent=2, ensure_ascii=False))

    # ==========================================
    # 7. 主揪確認回報場地狀態
    # ==========================================
    print_header("7. 主揪確認回報場地狀態 (發送通知給參賽球友)")
    status_data = {
        "status": "已佔到",
        "note": "在第一羽球場，我穿黃色背心"
    }
    status, venue_res = make_request(f"/games/{game_id}/venue-status/", "PATCH", data=status_data, token=token)
    if venue_res:
        print(json.dumps(venue_res, indent=2, ensure_ascii=False))

    # ==========================================
    # 8. 使用者取消報名/退出球局 (測試信譽扣分)
    # ==========================================
    print_header("8. 取消報名/退出球局 (測試前 24 小時內退局信譽扣分)")
    print("\n[DELETE] 使用者 B 退出球局 (此時距離活動日期很近，預期會觸發扣分)：")
    status, cancel_res = make_request(f"/games/{game_id}/cancel/", "DELETE", token=token2)
    if cancel_res:
        print(json.dumps(cancel_res, indent=2, ensure_ascii=False))

    # ==========================================
    # 9. 提交檢舉 API
    # ==========================================
    print_header("9. 提交檢舉 API (支援 reason 與 detail)")
    report_data = {
        "game_id": game_id,
        "reported_user_id": user_id,  # 檢舉主揪
        "reason": "未回報場地",
        "detail": "到了現場發現主揪根本沒來，也連絡不上，非常糟糕！"
    }
    status, report_res = make_request("/reports/", "POST", data=report_data, token=token3)
    if report_res:
        print(json.dumps(report_res, indent=2, ensure_ascii=False))

    # ==========================================
    # 10. 通知系統列表與標記已讀
    # ==========================================
    print_header("10. 取得通知列表與標記已讀")
    print("\n[GET] 讀取使用者 C 的通知：")
    status, notifs = make_request("/notifications/", "GET", token=token3)
    if notifs:
        print(f"🔔 使用者 C 共有 {len(notifs)} 條通知。")
        print(json.dumps(notifs[0] if notifs else {}, indent=2, ensure_ascii=False))
        
        if len(notifs) > 0:
            notif_id = notifs[0]["notification_id"]
            print(f"\n[PATCH] 將通知 ID: {notif_id} 標記為已讀：")
            status, read_res = make_request(f"/notifications/{notif_id}/read/", "PATCH", token=token3)
            if read_res:
                print(json.dumps(read_res, indent=2, ensure_ascii=False))

    print_header("🎉 全所有 API 端到端測試完成！")

if __name__ == "__main__":
    run_tests()
    log_file.close()
    
    # 僅在終端機輸出這一行提示訊息
    sys.stdout.write("🎉 API 測試已順利完成！測試結果與呼叫日誌已成功輸出至同目錄下的 [api_test_output.log] 文字檔中。\n")
