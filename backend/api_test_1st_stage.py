import urllib.request
import urllib.parse
import json
import sys
import os
import django
import datetime

# 解決 Windows 終端機 Unicode 輸出編碼錯誤問題
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 測試 mysql 資料庫，避免強制使用 sqlite
os.environ['FORCE_SQLITE'] = 'False'

# Setup Django configuration
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from api_v1.models import Sport, Venue, Court, GameMatch, Report
from django.utils import timezone

BASE_URL = "http://127.0.0.1:8088/api"

# Open log file for test logs
log_file = open("1st_stage_api_test.log", "w", encoding="utf-8")

def print_log(*args, **kwargs):
    stdout = kwargs.pop('stdout', True)
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(map(str, args)) + end
    log_file.write(text)
    log_file.flush()
    if stdout:
        sys.stdout.write(text)
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
        
    print_log(f"📤 Request: [{method}] {url}")
    print_log(f"   Request Headers: {json.dumps(headers, ensure_ascii=False)}", stdout=False)
    if data:
        print_log(f"   Request Body: {json.dumps(data, indent=2, ensure_ascii=False)}", stdout=False)
        
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
            if hasattr(response, 'info'):
                resp_headers = dict(response.info())
                print_log(f"   Response Headers: {json.dumps(resp_headers, ensure_ascii=False)}", stdout=False)
            print_log(f"   Response Body: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}", stdout=False)
            return status, parsed_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        print_log(f"❌ [{method}] {url} -> Status: {e.code}")
        resp_headers = dict(e.headers) if hasattr(e, 'headers') else {}
        print_log(f"   Response Headers: {json.dumps(resp_headers, ensure_ascii=False)}", stdout=False)
        print_log(f"   Response Body: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}", stdout=False)
        return e.code, parsed_body
    except Exception as e:
        print_log(f"💥 Connection failed: {e}")
        return None, None

def check_and_create_tables():
    from django.db import connection
    with connection.cursor() as cursor:
        # Check if game_bulletins table exists
        cursor.execute("SHOW TABLES LIKE 'game_bulletins'")
        if not cursor.fetchone():
            print_log("[Init] Creating missing game_bulletins table in MySQL...")
            cursor.execute("""
                CREATE TABLE `game_bulletins` (
                  `bulletin_id` int(11) NOT NULL AUTO_INCREMENT,
                  `game_id` int(11) NOT NULL,
                  `title` varchar(200) NOT NULL DEFAULT '公告',
                  `content` text NOT NULL,
                  `created_at` datetime(6) NOT NULL,
                  PRIMARY KEY (`bulletin_id`),
                  KEY `game_bulletins_game_id_fk` (`game_id`),
                  CONSTRAINT `game_bulletins_game_id_fk` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

def initialize_db():
    check_and_create_tables()

    print_log("[Init] Cleaning test users from database for test run...")
    # 僅刪除測試用的帳號，避免汙染與誤刪其他資料
    test_emails = ["admin@example.com", "user_a@example.com", "user_b@example.com"]
    User.objects.filter(email__in=test_emails).delete()

    # Create admin user
    User.objects.create_superuser(email="admin@example.com", name="管理員", password="admin123")
    
    # Initialize basic schema seeding (Sports, Address, Venue, Courts)
    Address = django.apps.apps.get_model('api_v1', 'Address')
    addr, _ = Address.objects.get_or_create(id=1, defaults={"city": "台北市", "district": "大安區", "street_line": "建國南路二段"})
    
    venue, _ = Venue.objects.get_or_create(id=1, defaults={"name": "大安羽球館", "address": addr, "latitude": 25.0264, "longitude": 121.5364})
    badminton, _ = Sport.objects.get_or_create(id=2, defaults={"name": "羽毛球"})
    court, _ = Court.objects.get_or_create(id=1, defaults={"venue": venue, "base_price": 300})
    court.sports.add(badminton)

    # Create a past match for testing joining started games
    import datetime
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    GameMatch = django.apps.apps.get_model('api_v1', 'GameMatch')
    GameMatch.objects.create(
        id=999,
        game_name="已結束球局",
        creator=User.objects.get(email="admin@example.com"),
        sport=badminton,
        court=court,
        least_players=1,
        most_players=4,
        target_level="休閒",
        booking_date=yesterday,
        time_slot="10:00-12:00",
        total_price=500.0,
        cancel_deadline=timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(10, 0)))
    )

    print_log("[Init] Database seeded successfully.")

def run_tests():
    print_header("1st Stage API E2E Verification (MySQL Mode)")
    
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

    # Seed User A as a participant of past game 999
    try:
        from django.contrib.auth import get_user_model as get_auth_user_model
        UserModel = get_auth_user_model()
        user_a = UserModel.objects.get(id=user_id_a)
        from api_v1.models import MatchParticipant
        MatchParticipant.objects.get_or_create(match_id=999, user=user_a)
        print_log("👉 已成功將 User A 加入已結束球局 999 作為參與者")
    except Exception as e:
        print_log(f"❌ 初始化 User A 參與球局 999 失敗: {e}")

    # 2. 完善個人檔案
    print_log("\n--- [A.2] 完善個人檔案 A ---")
    setup_profile_a = {
        "phone": "0988111222",
        "birthday": "2000-05-20",
        "gender": "男",
        "bio": "我是主揪陳先生",
        "instagram": "instagram_a",
        "line_id": "line_a",
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
        "target_level": "高手",
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
    print_log("\n👉 測試：首次修改時，手機與 A 重複：")
    status, res = make_request("/users/profile/", "PUT", data={
        "phone": "0988111222",  # 重複 A
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)
    if status == 400 and "duplicates" in res and "phone" in res["duplicates"]:
        print_log("✅ 成功阻擋重複的手機號碼！")
    else:
        print_log("❌ 錯誤：未成功阻擋重複的手機號碼！")

    print_log("\n👉 測試：首次修改時，IG 與 A 重複：")
    status, res = make_request("/users/profile/", "PUT", data={
        "phone": "0911222333",
        "instagram": "instagram_a",  # 重複 A
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)
    if status == 400 and "duplicates" in res and "instagram" in res["duplicates"]:
        print_log("✅ 成功阻擋重複的 Instagram 帳號！")
    else:
        print_log("❌ 錯誤：未成功阻擋重複的 Instagram 帳號！")

    print_log("\n👉 測試：首次修改時，LINE 與 A 重複：")
    status, res = make_request("/users/profile/", "PUT", data={
        "phone": "0911222333",
        "line_id": "line_a",  # 重複 A
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)
    if status == 400 and "duplicates" in res and "line_id" in res["duplicates"]:
        print_log("✅ 成功阻擋重複的 LINE ID！")
    else:
        print_log("❌ 錯誤：未成功阻擋重複的 LINE ID！")

    # 2.5 正確完成完善檔案
    print_log("\n👉 正確完善 B 個人檔案（使用不重複的值）：")
    make_request("/users/profile/", "PUT", data={
        "phone": "0911222333",
        "instagram": "instagram_b",
        "line_id": "line_b",
        "birthday": "1999-09-09",
        "gender": "男",
        "levels": {"羽球": "B"}
    }, token=token_b)

    # 2.6 測試加入已開始的球局
    print_log("\n👉 測試：加入已開始的球局：")
    status, res = make_request("/games/999/join/", "POST", token=token_b)
    if status == 400:
        print_log("✅ 成功阻擋加入已開始的球局！")
    else:
        print_log(f"❌ 錯誤：加入已開始的球局竟回傳了 status: {status}")

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
        "target_level": "業餘",
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
        "target_level": "業餘",
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
        "target_level": "業餘",
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
        "target_level": "業餘",
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
        "target_level": "業餘",
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
        "target_level": "業餘",
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
        "target_level": "業餘",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "男女"
    }, token=token_b)

    # 3.8 發起與加入限性別球局防呆測試 (限男、限女限制)
    print_log("\n👉 [性別限制測試] 註冊女生帳號 C 並完善個人檔案：")
    status, reg_res_c = make_request("/auth/register/", "POST", data={
        "email": "user_c@example.com",
        "password": "Password123!",
        "name": "陳女生"
    })
    token_c = reg_res_c["token"]
    
    # 完善 C 檔案，性別設為 "女"
    status, _ = make_request("/users/profile/", "PUT", data={
        "name": "陳女生",
        "phone": "0933444555",
        "birthday": "2002-08-15",
        "gender": "女",
        "levels": {
            "羽球": "A",
            "籃球": "B"
        }
    }, token=token_c)

    print_log("\n👉 測試：男生 (User B) 嘗試發起限女球局 (應失敗)：")
    status, res = make_request("/games/", "POST", data={
        "game_name": "男生發起限女團",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "業餘",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "限女"
    }, token=token_b)
    if status == 400:
        print_log("✅ 成功阻擋：男生發起限女球局失敗！")
    else:
        print_log(f"❌ 錯誤：男生發起限女球局回傳狀態為 {status}")
        sys.exit(1)

    print_log("\n👉 測試：女生 (User C) 嘗試發起限男球局 (應失敗)：")
    status, res = make_request("/games/", "POST", data={
        "game_name": "女生發起限男團",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "業餘",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "限男"
    }, token=token_c)
    if status == 400:
        print_log("✅ 成功阻擋：女生發起限男球局失敗！")
    else:
        print_log(f"❌ 錯誤：女生發起限男球局回傳狀態為 {status}")
        sys.exit(1)

    print_log("\n👉 測試：男生 (User B) 成功發起限男球局：")
    status, game_male = make_request("/games/", "POST", data={
        "game_name": "男生發起限男團",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "業餘",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "限男"
    }, token=token_b)
    if status == 201:
        print_log("✅ 成功：男生成功發起限男球局！")
        male_game_id = game_male["id"]
    else:
        print_log(f"❌ 錯誤：男生發起限男球局失敗 {status}")
        sys.exit(1)

    print_log("\n👉 測試：女生 (User C) 嘗試加入限男球局 (應失敗)：")
    status, res = make_request(f"/games/{male_game_id}/join/", "POST", token=token_c)
    if status == 400:
        print_log("✅ 成功阻擋：女生加入限男球局失敗！")
    else:
        print_log(f"❌ 錯誤：女生加入限男球局回傳狀態為 {status}")
        sys.exit(1)

    print_log("\n👉 測試：女生 (User C) 成功發起限女球局：")
    status, game_female = make_request("/games/", "POST", data={
        "game_name": "女生發起限女團",
        "sport_id": 2,
        "court_id": 1,
        "most_players": 4,
        "target_level": "業餘",
        "booking_date": tomorrow,
        "start_time": "10:00",
        "duration": "2 小時",
        "total_price": 500.0,
        "gender_limit": "限女"
    }, token=token_c)
    if status == 201:
        print_log("✅ 成功：女生成功發起限女球局！")
        female_game_id = game_female["id"]
    else:
        print_log(f"❌ 錯誤：女生發起限女球局失敗 {status}")
        sys.exit(1)

    print_log("\n👉 測試：男生 (User B) 嘗試加入限女球局 (應失敗)：")
    status, res = make_request(f"/games/{female_game_id}/join/", "POST", token=token_b)
    if status == 400:
        print_log("✅ 成功阻擋：男生加入限女球局失敗！")
    else:
        print_log(f"❌ 錯誤：男生加入限女球局回傳狀態為 {status}")
        sys.exit(1)

    # ========================================================
    # PART 4: 測試 GET /api/games/ 隱私與時間過濾邏輯
    # ========================================================
    print_header("PART 4: 測試 GET /api/games/ 隱私與時間過濾邏輯")

    from django.contrib.auth import get_user_model as get_auth_user_model
    UserModel = get_auth_user_model()
    user_a = UserModel.objects.get(email="user_a@example.com")
    badminton = Sport.objects.get(id=2)
    court = Court.objects.get(id=1)
    
    # 建立一個正在進行中 (已開始但未結束) 且 A 參與的球局 (id=998)
    test_now = timezone.localtime(timezone.now())
    start_started = test_now - datetime.timedelta(hours=1)
    end_started = test_now + datetime.timedelta(hours=1)
    time_slot_started = f"{start_started.strftime('%H:%M')}-{end_started.strftime('%H:%M')}"
    
    from api_v1.models import GameMatch, MatchParticipant
    match_active_started, _ = GameMatch.objects.get_or_create(
        id=998,
        defaults={
            "game_name": "正在進行中且參賽球局",
            "creator": user_a,
            "sport": badminton,
            "court": court,
            "least_players": 1,
            "most_players": 4,
            "target_level": "休閒",
            "booking_date": start_started.date(),
            "time_slot": time_slot_started,
            "total_price": 500.0,
            "cancel_deadline": start_started - datetime.timedelta(hours=24)
        }
    )
    MatchParticipant.objects.get_or_create(match=match_active_started, user=user_a)

    # 1. 未登入狀態下，不應該在列表看到已結束球局 (id=999) 且不應該看到進行中但未參與的球局 (id=998)
    print_log("\n--- [GET /games/ 未登入過濾] ---")
    status, games_anon = make_request("/games/")
    if status == 200:
        found_past_game = any(g["id"] == 999 for g in games_anon)
        found_active_started = any(g["id"] == 998 for g in games_anon)
        if not found_past_game and not found_active_started:
            print_log("✅ 成功：未登入者無法在列表看到已結束球局，也看不到進行中但未參賽的球局")
        else:
            print_log(f"❌ 錯誤：未登入者看到了不該看的球局！已結束球局在列表: {found_past_game}, 進行中球局在列表: {found_active_started}")
    else:
        print_log(f"❌ 錯誤：未登入 GET /games/ 回傳狀態碼 {status}")

    # 2. 登入 B (非參與者) 狀態下，不應該在列表看到已結束球局 (id=999) 且不應該看到進行中但未參與的球局 (id=998)
    print_log("\n--- [GET /games/ 登入非參與者過濾] ---")
    status, games_b = make_request("/games/", token=token_b)
    if status == 200:
        found_past_game = any(g["id"] == 999 for g in games_b)
        found_active_started = any(g["id"] == 998 for g in games_b)
        if not found_past_game and not found_active_started:
            print_log("✅ 成功：未參與該球局的使用者 B 無法在列表看到已結束球局，也看不到進行中但未參賽的球局")
        else:
            print_log(f"❌ 錯誤：使用者 B 看到了不該看的球局！已結束球局在列表: {found_past_game}, 進行中球局在列表: {found_active_started}")
    else:
        print_log(f"❌ 錯誤：使用者 B GET /games/ 回傳狀態碼 {status}")

    # 3. 登入 A (參與者) 狀態下，不應該看到已結束球局 (id=999)，但應該要看到進行中且已參賽的球局 (id=998)
    print_log("\n--- [GET /games/ 登入參與者過濾與保留] ---")
    status, games_a = make_request("/games/", token=token_a)
    if status == 200:
        found_past_game = any(g["id"] == 999 for g in games_a)
        found_active_started = any(g["id"] == 998 for g in games_a)
        if not found_past_game and found_active_started:
            print_log("✅ 成功：參賽使用者 A 成功過濾掉已結束球局，且能在列表看到進行中且已參賽的球局")
        else:
            print_log(f"❌ 錯誤：使用者 A 列表過濾不正確！已結束球局在列表: {found_past_game} (預期 False), 進行中已參賽球局在列表: {found_active_started} (預期 True)")
    else:
        print_log(f"❌ 錯誤：使用者 A GET /games/ 回傳狀態碼 {status}")

    # ========================================================
    # PART 5: 測試球局狀態機狀態與通知
    # ========================================================
    print_header("PART 5: 測試球局狀態機狀態與通知")

    from django.core.management import call_command
    from api_v1.models import Notification, MatchParticipant
    
    # 取得基礎模型物件
    from django.contrib.auth import get_user_model as get_auth_user_model
    UserModel = get_auth_user_model()
    user_a = UserModel.objects.get(email="user_a@example.com")
    badminton = Sport.objects.get(id=2)
    court = Court.objects.get(id=1)
    
    # 使用台北當地時間，確保 time_slot 格式化後的字串代表當地時間
    now = timezone.localtime(timezone.now())

    # 1. 建立 24 小時內即將開始的球局 (預計觸發 24h 通知)
    start_24h = now + datetime.timedelta(hours=2)
    end_24h = now + datetime.timedelta(hours=4)
    time_slot_24h = f"{start_24h.strftime('%H:%M')}-{end_24h.strftime('%H:%M')}"
    
    match_24h = GameMatch.objects.create(
        game_name="24h內熱血球局",
        creator=user_a,
        sport=badminton,
        court=court,
        least_players=1,
        most_players=4,
        target_level="休閒",
        booking_date=start_24h.date(),
        time_slot=time_slot_24h,
        total_price=500.0,
        cancel_deadline=start_24h - datetime.timedelta(hours=24)
    )
    MatchParticipant.objects.create(match=match_24h, user=user_a)

    # 2. 建立已開始但尚未結束且人數足夠的球局 (預計觸發 開始通知)
    start_started = now - datetime.timedelta(hours=1)
    end_started = now + datetime.timedelta(hours=1)
    time_slot_started = f"{start_started.strftime('%H:%M')}-{end_started.strftime('%H:%M')}"
    
    match_started = GameMatch.objects.create(
        game_name="已開始成團球局",
        creator=user_a,
        sport=badminton,
        court=court,
        least_players=1,
        most_players=4,
        target_level="休閒",
        booking_date=start_started.date(),
        time_slot=time_slot_started,
        total_price=500.0,
        cancel_deadline=start_started - datetime.timedelta(hours=24)
    )
    MatchParticipant.objects.create(match=match_started, user=user_a)

    # 3. 建立已開始但人數不足的球局 (預計觸發 流局)
    match_failed = GameMatch.objects.create(
        game_name="人數不足流局球局",
        creator=user_a,
        sport=badminton,
        court=court,
        least_players=3,
        most_players=4,
        target_level="休閒",
        booking_date=start_started.date(),
        time_slot=time_slot_started,
        total_price=500.0,
        cancel_deadline=start_started - datetime.timedelta(hours=24)
    )
    MatchParticipant.objects.create(match=match_failed, user=user_a)

    # 4. 建立已結束的球局 (預計觸發 自動關閉)
    start_ended = now - datetime.timedelta(hours=3)
    end_ended = now - datetime.timedelta(hours=1)
    time_slot_ended = f"{start_ended.strftime('%H:%M')}-{end_ended.strftime('%H:%M')}"
    
    match_ended = GameMatch.objects.create(
        game_name="已結束自動關閉球局",
        creator=user_a,
        sport=badminton,
        court=court,
        least_players=1,
        most_players=4,
        target_level="休閒",
        booking_date=start_ended.date(),
        time_slot=time_slot_ended,
        total_price=500.0,
        cancel_deadline=start_ended - datetime.timedelta(hours=24)
    )
    MatchParticipant.objects.create(match=match_ended, user=user_a)

    print_log("\n👉 執行 Django Management Command 更新狀態機...")
    call_command('update_match_states')
    
    # 重新載入球局狀態
    match_24h.refresh_from_db()
    match_started.refresh_from_db()
    match_ended.refresh_from_db()
    
    match_failed_id = match_failed.id
    match_failed_exists = GameMatch.objects.filter(id=match_failed_id).exists()

    print_log(f"   24h球局狀態 (預期 recruiting/full): {match_24h.match_status}")
    print_log(f"   已開始成團球局狀態 (預期 started): {match_started.match_status}")
    print_log(f"   人數不足流局球局 (預期已刪除): {'存在' if match_failed_exists else '已物理刪除'}")
    print_log(f"   已結束自動關閉球局狀態 (預期 closed): {match_ended.match_status}")

    # 驗證狀態值
    if not match_failed_exists and match_ended.match_status == 'closed' and match_started.match_status == 'started':
        print_log("✅ 成功：球局狀態機狀態移轉與物理刪除正確！")
    else:
        print_log("❌ 錯誤：球局狀態機狀態移轉或刪除不正確！")

    # 驗證通知發送 (對已刪除球局，我們不帶 match 條件查，改查 message)
    notif_24h = Notification.objects.filter(user=user_a, match=match_24h, message__contains="將在 24 小時內開始").exists()
    notif_started = Notification.objects.filter(user=user_a, match=match_started, message__contains="已經開始").exists()
    # match_failed 已刪除，故 match 外鍵應為 None (SET_NULL)
    notif_failed = Notification.objects.filter(user=user_a, match__isnull=True, message__contains="因人數未達下限").exists()
    notif_ended = Notification.objects.filter(user=user_a, match=match_ended, message__contains="已順利結束").exists()

    print_log(f"   24h球局通知發送情況 (預期 True): {notif_24h}")
    print_log(f"   已開始成團球局通知發送情況 (預期 True): {notif_started}")
    print_log(f"   人數不足流局通知發送情況 (預期 True): {notif_failed}")
    print_log(f"   已結束球局通知發送情況 (預期 True): {notif_ended}")

    if notif_24h and notif_started and notif_failed and notif_ended:
        print_log("✅ 成功：球局狀態機通知發送全部正確！")
    else:
        print_log("❌ 錯誤：球局狀態機通知發送不正確！")

    # 測試個人歷史球局 API
    print_log("\n👉 測試：GET /api/games/history/ (個人歷史成團球局)：")
    status, history = make_request("/games/history/", token=token_a)
    if status == 200:
        has_ended = any(h["id"] == match_ended.id for h in history)
        has_failed = any(h["id"] == match_failed_id for h in history)
        if has_ended and not has_failed:
            print_log("✅ 成功：歷史球局 API 僅回傳成功結束之球局，不包含流局。")
        else:
            print_log(f"❌ 錯誤：歷史球局回傳結果不正確！包含流局: {has_failed}, 漏掉結束球局: {not has_ended}")
    else:
        print_log(f"❌ 錯誤：歷史球局 API 回傳狀態碼 {status}")
        
    # 重複呼叫狀態機，驗證防重複通知邏輯
    count_before = Notification.objects.filter(user=user_a, match=match_24h).count()
    call_command('update_match_states')
    count_after = Notification.objects.filter(user=user_a, match=match_24h).count()
    if count_before == count_after:
        print_log("✅ 成功：重複觸發狀態機未產生重複通知！")
    else:
        print_log("❌ 錯誤：重複觸發狀態機產生了重複通知！")

    print_log("\n" + "=" * 60)
    print_log("🎉 1st Stage API 測試全數執行完畢！")
    print_log("=" * 60 + "\n")

def cleanup_db():
    print_log("[Cleanup] Cleaning up test data from Database...")
    try:
        test_emails = ["admin@example.com", "user_a@example.com", "user_b@example.com", "user_c@example.com"]
        deleted_count, details = User.objects.filter(email__in=test_emails).delete()
        print_log(f"[Cleanup] Deleted test users and cascaded objects: {deleted_count} ({details})")
    except Exception as e:
        print_log(f"[Cleanup] Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        run_tests()
    finally:
        cleanup_db()
