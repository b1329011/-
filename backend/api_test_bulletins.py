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

# 使用 MySQL 進行測試
os.environ['FORCE_SQLITE'] = 'False'

# Setup Django configuration
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from api_v1.models import Sport, Venue, Court, GameMatch, Notification, GameBulletin

BASE_URL = "http://127.0.0.1:8088/api"

# Open log file for test logs
log_file = open("bulletin_api_test.log", "w", encoding="utf-8")

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
            print_log(f"   Response Body: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}", stdout=False)
            return status, parsed_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        print_log(f"❌ [{method}] {url} -> Status: {e.code}")
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
    print_log("[Init] Cleaning test users for bulletins test run...")
    test_emails = [
        "user_bulletin_a@example.com",
        "user_bulletin_b@example.com",
        "user_bulletin_c@example.com"
    ]
    # Delete cascade test data
    User.objects.filter(email__in=test_emails).delete()
    print_log("[Init] Database cleaned.")

def cleanup_db():
    print_log("[Cleanup] Cleaning up test data from Database...")
    try:
        test_emails = [
            "user_bulletin_a@example.com",
            "user_bulletin_b@example.com",
            "user_bulletin_c@example.com"
        ]
        deleted_count, details = User.objects.filter(email__in=test_emails).delete()
        print_log(f"[Cleanup] Deleted test users and cascaded objects: {deleted_count} ({details})")
    except Exception as e:
        print_log(f"[Cleanup] Error during cleanup: {e}")

def run_tests():
    print_header("Game Bulletin & Notification E2E Verification (MySQL Mode)")
    
    initialize_db()

    # 1. 註冊 A (主揪)、B (球友)、C (旁觀者)
    print_log("\n--- [1] 註冊 A, B, C 帳號 ---")
    reg_data_a = {"name": "公告主揪A", "email": "user_bulletin_a@example.com", "password": "password123"}
    status, reg_res_a = make_request("/auth/register", "POST", data=reg_data_a)
    token_a = reg_res_a["token"]

    reg_data_b = {"name": "球友B", "email": "user_bulletin_b@example.com", "password": "password123"}
    status, reg_res_b = make_request("/auth/register", "POST", data=reg_data_b)
    token_b = reg_res_b["token"]

    reg_data_c = {"name": "旁觀者C", "email": "user_bulletin_c@example.com", "password": "password123"}
    status, reg_res_c = make_request("/auth/register", "POST", data=reg_data_c)
    token_c = reg_res_c["token"]

    # 2. 完善 A 與 B 個人檔案
    print_log("\n--- [2] 完善 A 與 B 的個人檔案 ---")
    make_request("/users/profile/", "PUT", data={
        "phone": "0900111111",
        "birthday": "2000-01-01",
        "gender": "男",
        "levels": {"羽球": "A"}
    }, token=token_a)

    make_request("/users/profile/", "PUT", data={
        "phone": "0900222222",
        "birthday": "2000-01-02",
        "gender": "女",
        "levels": {"羽球": "B"}
    }, token=token_b)

    # 3. A 發起球局
    print_log("\n--- [3] A 發起新球局 ---")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    game_data = {
        "game_name": "公告測試羽球局",
        "sport_id": 2,  # 羽球 (已預先載入)
        "court_id": 1,
        "most_players": 4,
        "target_level": "A",
        "booking_date": tomorrow,
        "start_time": "19:00",
        "duration": "2 小時",
        "total_price": 600.0,
        "gender_limit": "不限",
        "game_note": "測試公告推播功能。"
    }
    status, game_res = make_request("/games/", "POST", data=game_data, token=token_a)
    game_id = game_res["id"]
    print_log(f"✅ 球局建立成功，ID = {game_id}")

    # 4. B 加入球局
    print_log("\n--- [4] B 加入該球局 ---")
    status, join_res = make_request(f"/games/{game_id}/join/", "POST", token=token_b)
    if status == 200:
        print_log("✅ B 成功加入球局")
    else:
        print_log(f"❌ B 加入球局失敗：Status {status}")
        return

    # 5. A 發布公告
    print_log("\n--- [5] 主揪 A 發布新公告 ---")
    bulletin_payload = {
        "title": "更換場地通知",
        "content": "請大家直接到 3 號場地集合，謝謝！"
    }
    status, bulletin_res = make_request(f"/games/{game_id}/announcements/", "POST", data=bulletin_payload, token=token_a)
    if status == 201:
        print_log(f"✅ 公告發布成功！公告 ID: {bulletin_res['id']}，日期: {bulletin_res.get('date')}")
    else:
        print_log(f"❌ 公告發布失敗：Status {status}")
        return

    # 6. B 讀取公告列表
    print_log("\n--- [6] 球友 B 讀取公告列表 ---")
    status, bulletins_list = make_request(f"/games/{game_id}/announcements/", "GET", token=token_b)
    bulletin_found = False
    for b in bulletins_list:
        if b["content"] == bulletin_payload["content"]:
            bulletin_found = True
            print_log(f"✅ 成功在公告列表中找到公告：【{b['title']}】{b['content']}，日期：{b.get('date')}")
            break
    if not bulletin_found:
        print_log("❌ 錯誤：公告列表中未找到剛發布的公告！")

    # 7. B (參賽者) 檢查通知中心
    print_log("\n--- [7] 球友 B 檢查通知中心 ---")
    status, notifs_b = make_request("/notifications/", "GET", token=token_b)
    notif_found = False
    for n in notifs_b:
        if "更換場地通知" in n["message"] or "3 號場地" in n["message"]:
            notif_found = True
            print_log(f"✅ B 的通知中心收到公告通知：{n['message']}")
            break
    if not notif_found:
        print_log("❌ 錯誤：B 的通知中心沒有收到任何新公告通知！")

    # 8. A (主揪/發布者) 檢查通知中心
    print_log("\n--- [8] 主揪 A 檢查通知中心 ---")
    status, notifs_a = make_request("/notifications/", "GET", token=token_a)
    notif_found_a = False
    for n in notifs_a:
        if "更換場地通知" in n["message"] or "3 號場地" in n["message"]:
            notif_found_a = True
            break
    if not notif_found_a:
        print_log("✅ A 沒有收到自己發布的公告通知，隱私過濾正常。")
    else:
        print_log("❌ 錯誤：A（發布者）居然在通知中心收到了自己發布的公告通知！")

    # 9. C (未參賽者) 檢查通知中心
    print_log("\n--- [9] 未參賽者 C 檢查通知中心 ---")
    status, notifs_c = make_request("/notifications/", "GET", token=token_c)
    notif_found_c = False
    for n in notifs_c:
        if "更換場地通知" in n["message"] or "3 號場地" in n["message"]:
            notif_found_c = True
            break
    if not notif_found_c:
        print_log("✅ C 沒有收到任何該球局公告通知，權限過濾正常。")
    else:
        print_log("❌ 錯誤：未參賽的 C 居然在通知中心收到了該球局的公告通知！")

    print_log("\n" + "=" * 60)
    print_log("🎉 Game Bulletin & Notification 測試全部執行完畢！")
    print_log("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        run_tests()
    finally:
        cleanup_db()
