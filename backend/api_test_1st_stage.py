import urllib.request
import urllib.parse
import json
import sys
import os
import django
import datetime

# 強制使用 sqlite 測試，避免汙染主資料庫
os.environ['FORCE_SQLITE'] = 'True'

# Setup Django configuration
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from api_v1.models import Sport, Venue, Court, GameMatch, Report, Feedback

BASE_URL = "http://127.0.0.1:8088/api"

# Open log file for test logs
log_file = open("1st_stage_api_test.log", "w", encoding="utf-8")

def print_log(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(map(str, args)) + end
    log_file.write(text)
    log_file.flush()
    # Also print to stdout for visibility
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        try:
            sys.stdout.write(text.encode(sys.stdout.encoding or 'cp950', errors='replace').decode(sys.stdout.encoding or 'cp950'))
        except Exception:
            sys.stdout.write(text.encode('ascii', errors='replace').decode('ascii'))
    sys.stdout.flush()

def print_header(title):
    print_log("\n\n" + "=" * 60)
    print_log(f"🚀 {title}")
    print_log("=" * 60 + "\n")

def make_request(path, method="GET", data=None, token=None):
    quoted_path = urllib.parse.quote(path.lstrip('/'), safe='/?=&')
    url = f"{BASE_URL}/{quoted_path}"
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
            
            print_log(f"✅ [{method}] {url} -> Status: {status}")
            return status, parsed_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        print_log(f"❌ [{method}] {url} -> Status: {e.code}")
        print_log(f"   Response: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}")
        return e.code, parsed_body
    except Exception as e:
        print_log(f"💥 Connection failed: {e}")
        return None, None

def initialize_db():
    print_log("[Init] Cleaning SQLite Database for test run...")
    # Delete test users from database to prevent conflicts
    User.objects.all().delete()
    Report.objects.all().delete()
    Feedback.objects.all().delete()
    GameMatch.objects.all().delete()

    # Create admin user
    User.objects.create_superuser(email="admin@example.com", name="管理員", password="admin123")
    
    # Initialize basic schema seeding (Sports, Address, Venue, Courts)
    Address = django.apps.apps.get_model('api_v1', 'Address')
    addr, _ = Address.objects.get_or_create(id=1, defaults={"city": "台北市", "district": "大安區", "street_line": "建國南路二段"})
    
    venue, _ = Venue.objects.get_or_create(id=1, defaults={"name": "大安羽球館", "address": addr, "latitude": 25.0264, "longitude": 121.5364})
    badminton, _ = Sport.objects.get_or_create(id=2, defaults={"name": "羽毛球"})
    court, _ = Court.objects.get_or_create(id=1, defaults={"venue": venue, "base_price": 300})
    court.sports.add(badminton)
    print_log("[Init] Database seeded successfully.")

def run_tests():
    print_header("1st Stage API E2E Verification (FORCE_SQLITE)")
    
    initialize_db()

    # ========================================================
    # PART 1: 註冊A用正常輸入邏輯
    # ========================================================
    print_header("PART 1: 註冊A用正常輸入邏輯")

    # 1. 註冊
    print_log("\n--- [A.1] 註冊 A 帳號 ---")
    reg_data_a = {
        "name": "陳主揪",
        "email": "user_a@example.com",
        "password": "password123"
    }
    status, reg_res_a = make_request("/auth/register", "POST", data=reg_data_a)
    if status != 201:
        print_log("❌ A 註冊失敗！終止測試。")
        return
    token_a = reg_res_a["token"]
    user_id_a = reg_res_a["user_id"]
    print_log(f"🔑 註冊成功！Token A: {token_a}")

    # 2. 完善個人檔案
    print_log("\n--- [A.2] 完善個人檔案 A ---")
    setup_profile_a = {
        "phone": "0988111222",
        "birthday": "2000-05-20",
        "gender": "男",
        "bio": "我是主揪陳先生",
        "levels": {
            "羽球": "A"
        }
    }
    status, prof_res_a = make_request("/users/profile/", "PUT", data=setup_profile_a, token=token_a)
    if status == 200:
        print_log("👉 完善個人檔案成功！")
        print_log(f"   生日: {prof_res_a.get('birthday')}, 性別: {prof_res_a.get('gender')}")
    else:
        print_log("❌ 完善個人檔案 A 失敗！")

    # 3. 修改個人檔案 (驗證 birthday 與 gender 唯讀防改)
    print_log("\n--- [A.3] 修改個人檔案 A 並驗證唯讀防改 ---")
    modify_profile_a = {
        "name": "陳主揪改名",
        "birthday": "1990-01-01",  # 試圖修改生日
        "gender": "女"              # 試圖修改性別
    }
    status, mod_res_a = make_request("/users/profile/", "PUT", data=modify_profile_a, token=token_a)
    if status == 200:
        print_log(f"   修改後姓名: {mod_res_a.get('name')}")
        print_log(f"   生日原值 (應不變, 為 2000-05-20): {mod_res_a.get('birthday')}")
        print_log(f"   性別原值 (應不變, 為 男): {mod_res_a.get('gender')}")
        if mod_res_a.get('birthday') == "2000-05-20" and mod_res_a.get('gender') == "男":
            print_log("✅ 唯讀屬性防範邏輯運作正常！")
        else:
            print_log("❌ 唯讀屬性遭到非法修改！")
    else:
        print_log("❌ 修改個人檔案 A 失敗！")

    # 4. 正常發起球局
    print_log("\n--- [A.4] A 正常發起球局 ---")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    valid_game = {
        "game_name": "週五羽球熱血團",
        "sport_id": 2,  # 羽球
        "court_id": 1,
        "most_players": 4,
        "target_level": "A",
        "booking_date": tomorrow,
        "start_time": "18:00",
        "duration": "2 小時",
        "total_price": 600.0,
        "gender_limit": "不限",
        "game_note": "帶水跟球拍來即可。"
    }
    status, game_res = make_request("/games/", "POST", data=valid_game, token=token_a)
    if status == 201:
        game_id = game_res["id"]
        print_log(f"👉 建立成功！球局 ID: {game_id}")
    else:
        print_log("❌ A 發起球局失敗！")
        return

    # 5. 加入球局 (主揪重複加入自己發起的球局，預期會被防呆阻擋)
    print_log("\n--- [A.5] 主揪重複加入自己發起的球局 ---")
    status, join_a_res = make_request(f"/games/{game_id}/join/", "POST", token=token_a)
    if status == 400:
        print_log("✅ 阻擋主揪重複加入自己球局邏輯正確！")
    else:
        print_log("❌ 錯誤：主揪竟重複加入了自己球局！")

    # ========================================================
    # PART 2: 註冊B不正常使用
    # ========================================================
    print_header("PART 2: 註冊B不正常使用")

    # 1. 各種錯誤格式註冊
    print_log("\n--- [B.1] 錯誤格式註冊防呆 ---")
    
    # 1.1 信箱格式錯誤 (無 @)
    print_log("👉 測試：信箱格式無 @：")
    make_request("/auth/register", "POST", data={
        "name": "林隊員",
        "email": "user_b_invalid",
        "password": "password123"
    })
    
    # 1.2 缺失密碼
    print_log("\n👉 測試：缺失密碼欄位：")
    make_request("/auth/register", "POST", data={
        "name": "林隊員",
        "email": "user_b@example.com"
    })
    
    # 1.3 缺失姓名
    print_log("\n👉 測試：缺失姓名欄位：")
    make_request("/auth/register", "POST", data={
        "email": "user_b@example.com",
        "password": "password123"
    })
    
    # 1.4 重複註冊 A 的信箱
    print_log("\n👉 測試：重複註冊同一個信箱：")
    make_request("/auth/register", "POST", data={
        "name": "林二號",
        "email": "user_a@example.com",
        "password": "password123"
    })

    # 2. 註冊 B 正常註冊，但不修改個人檔案直接送出
    print_log("\n--- [B.2] 註冊 B 帳號並測試完善檔案防呆 ---")
    reg_data_b = {
        "name": "林隊員",
        "email": "user_b@example.com",
        "password": "password123"
    }
    status, reg_res_b = make_request("/auth/register", "POST", data=reg_data_b)
    token_b = reg_res_b["token"]
    
    # 2.1 完善檔案防呆：缺少必填欄位 (不修改直接送出空內容)
    print_log("\n👉 測試：完善檔案時傳送空內容（不修改送出）：")
    make_request("/users/profile/", "PUT", data={}, token=token_b)
    
    # 2.2 完善檔案防呆：缺少 levels
    print_log("\n👉 測試：完善檔案時缺少運動等級 levels：")
    make_request("/users/profile/", "PUT", data={
        "phone": "0911222333",
        "birthday": "1999-09-09",
        "gender": "男"
    }, token=token_b)

    # 2.3 完善檔案防呆：手機格式不正確
    print_log("\n👉 測試：手機格式不正確 (非09開頭或非10碼)：")
    make_request("/users/profile/", "PUT", data={
        "phone": "123456",
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)

    # 2.4 未完善檔案直接去加入球局
    print_log("\n👉 測試：未完善個人檔案前，直接去加入球局 A：")
    status, _ = make_request(f"/games/{game_id}/join/", "POST", token=token_b)
    if status == 400 or status == 403:
        print_log("✅ 阻擋未完善檔案加入球局邏輯正確！")
    else:
        print_log("❌ 錯誤：未完善檔案竟成功加入了球局！")

    # 2.5 正確完成完善檔案
    print_log("\n👉 正確完善 B 個人檔案：")
    make_request("/users/profile/", "PUT", data={
        "phone": "0911222333",
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)

    # 3. 資料亂填的發起球局
    print_log("\n--- [B.3] B 發起亂填資料的球局防呆 ---")

    # 3.1 時間日期填過去
    print_log("\n👉 測試：預約日期為過去 (昨天的日期)：")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    make_request("/games/", "POST", data={
        "game_name": "過去的球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": yesterday,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.2 價格亂填 (大於 10,000 元)
    print_log("\n👉 測試：價格過高 (12,000 元)：")
    make_request("/games/", "POST", data={
        "game_name": "土豪球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 12000.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.3 價格為負數
    print_log("\n👉 測試：價格為負數 (-100 元)：")
    make_request("/games/", "POST", data={
        "game_name": "負債球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": -100.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.4 持續時間格式不對 (無數字)
    print_log("\n👉 測試：持續時間格式錯誤 (無包含數字)：")
    make_request("/games/", "POST", data={
        "game_name": "無限球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "不限時間",
        "total_price": 500.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.5 持續時間數值不對 (大於 24 小時)
    print_log("\n👉 測試：持續時間過長 (25 小時)：")
    make_request("/games/", "POST", data={
        "game_name": "漫長球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "25 小時",
        "total_price": 500.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.6 最多人數少於最少人數
    print_log("\n👉 測試：最多人數少於最少人數：")
    make_request("/games/", "POST", data={
        "game_name": "奇特球局",
        "sport_id": 2,
        "court_id": 1,
        "least_players": 4,
        "most_players": 2,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "不限"
    }, token=token_b)

    # 3.7 性別限制亂填
    print_log("\n👉 測試：性別限制輸入無效值 (男女)：")
    make_request("/games/", "POST", data={
        "game_name": "性別混亂球局",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "B",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "男女"
    }, token=token_b)

    print_log("\n" + "=" * 60)
    print_log("🎉 1st Stage API 測試全數執行完畢！")
    print_log("=" * 60 + "\n")

if __name__ == "__main__":
    run_tests()
