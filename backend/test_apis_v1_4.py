import urllib.request
import urllib.parse
import json
import sys
import os
import django

# Setup Django to initialize password updates for test accounts
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from api_v1.models import Sport, Venue, Court, GameMatch, Report, Feedback

BASE_URL = "http://127.0.0.1:8000/api"

# Open log file for test logs
log_file = open("api_test_output_v1_4.log", "w", encoding="utf-8")

def print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(map(str, args)) + end
    log_file.write(text)
    log_file.flush()
    # Also print to stdout for modeling feedback visibility with encoding fallback
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        try:
            sys.stdout.write(text.encode(sys.stdout.encoding or 'cp950', errors='replace').decode(sys.stdout.encoding or 'cp950'))
        except Exception:
            sys.stdout.write(text.encode('ascii', errors='replace').decode('ascii'))
    sys.stdout.flush()

def print_header(title):
    print("\n\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60 + "\n")

def make_request(path, method="GET", data=None, token=None):
    # Quote the path and query string to support non-ASCII characters
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
            
            print(f"✅ [{method}] {url} -> Status: {status}\n")
            return status, parsed_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        print(f"❌ [{method}] {url} -> Status: {e.code}")
        print(f"   Response: {json.dumps(parsed_body, indent=2, ensure_ascii=False)}\n")
        return e.code, parsed_body
    except Exception as e:
        print(f"💥 Failed to connect to server: {e}\n")
        return None, None

def initialize_db():
    print("[Init] Initializing test accounts and passwords in DB...")
    # Set passwords for initial test users to allow credential testing
    admin_user = User.objects.filter(role='admin').first()
    if admin_user:
        admin_user.set_password("admin123")
        admin_user.save()
        print(f"[Init] Set admin user password. Email: {admin_user.email}")
    else:
        # Create a default admin user if none exists (needed for SQLite testing)
        admin_user = User.objects.create_superuser(email="admin@example.com", name="楊管理員", password="admin123")
        print(f"[Init] Created new admin user for testing. Email: {admin_user.email}")
        
    # Reset other tables for a clean test run
    Report.objects.all().delete()
    Feedback.objects.all().delete()
    # Delete users created during previous test runs to prevent conflict
    User.objects.exclude(email__in=['admin@example.com', 'admin1@example.com', 'yangxin@example.com', 'linminghe@example.com', 'chenhanlin@example.com', 'jianlu@example.com', 'lisiyu@example.com']).delete()

    # Seed essential Sport, Venue, Address, and Court objects
    Address = django.apps.apps.get_model('api_v1', 'Address')
    addr, _ = Address.objects.get_or_create(id=1, defaults={"city": "台北市", "district": "大安區", "street_line": "建國南路二段"})
    
    venue1, _ = Venue.objects.get_or_create(id=1, defaults={"name": "大安體育館", "address": addr, "latitude": 25.0264, "longitude": 121.5364})
    venue2, _ = Venue.objects.get_or_create(id=2, defaults={"name": "大安羽球館", "address": addr, "latitude": 25.0264, "longitude": 121.5364})
    
    basketball, _ = Sport.objects.get_or_create(id=1, defaults={"name": "籃球"})
    badminton, _ = Sport.objects.get_or_create(id=2, defaults={"name": "羽毛球"})
    
    court1, _ = Court.objects.get_or_create(id=1, defaults={"venue": venue1, "base_price": 300})
    court1.sports.add(basketball)
    court2, _ = Court.objects.get_or_create(id=2, defaults={"venue": venue2, "base_price": 300})
    court2.sports.add(badminton)

def run_tests():
    print("🔔 開始執行「不揪ㄛ」V1.4 API 流程與防呆邏輯端到端測試")
    print("🔔 測試端點目標: " + BASE_URL)
    
    initialize_db()
    
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
    print_header("2. 使用者註冊 (Register) 與信箱密碼登入 (Login)")
    
    # 註冊帳號 A
    print("\n[POST] 註冊新帳號 A：")
    register_data_a = {
        "name": "陳主揪",
        "email": "user_a@example.com",
        "password": "password123"
    }
    status, register_res = make_request("/auth/register", "POST", data=register_data_a)
    if status != 201:
        print("❌ 註冊帳號 A 失敗。")
        return
    token_a = register_res["token"]
    user_id_a = register_res["user_id"]
    print(f"🔑 註冊成功！Token A: {token_a} (ID: {user_id_a})")

    # 註冊帳號 B
    print("\n[POST] 註冊新帳號 B：")
    register_data_b = {
        "name": "林隊員",
        "email": "user_b@example.com",
        "password": "password123"
    }
    _, register_res_b = make_request("/auth/register", "POST", data=register_data_b)
    token_b = register_res_b["token"]
    user_id_b = register_res_b["user_id"]

    # 註冊帳號 C (女性帳號，測試性別限制用)
    print("\n[POST] 註冊新帳號 C (女性)：")
    register_data_c = {
        "name": "王正妹",
        "email": "user_c@example.com",
        "password": "password123"
    }
    _, register_res_c = make_request("/auth/register", "POST", data=register_data_c)
    token_c = register_res_c["token"]

    # 測試重複信箱註冊
    print("\n[POST] 測試重複註冊同一信箱（預期 400 失敗）：")
    make_request("/auth/register", "POST", data=register_data_a)

    # 測試信箱密碼登入
    print("\n[POST] 使用帳號 A 登入：")
    login_data_a = {
        "email": "user_a@example.com",
        "password": "password123"
    }
    status, login_res = make_request("/auth/login", "POST", data=login_data_a)
    if status == 200:
        print("✅ 登入驗證通過！")

    # ==========================================
    # 3. 完善個人資料 (首次與唯讀限制)
    # ==========================================
    print_header("3. 完善個人資料 (首次與唯讀欄位防改限制)")
    
    # 首次完善個人資料（必填 phone, birthday, gender, levels）
    print("\n[PUT] 帳號 A 首次完善個人檔案：")
    setup_profile_a = {
        "phone": "0988111222",
        "birthday": "2000-05-20",
        "gender": "男",
        "bio": "我是主揪陳先生",
        "levels": {
            "羽球": "A",
            "籃球": "B"
        }
    }
    status, profile_res = make_request("/users/profile/", "PUT", data=setup_profile_a, token=token_a)
    if profile_res:
        print(json.dumps(profile_res, indent=2, ensure_ascii=False))

    # 首次完善個人資料（B 帳號）
    print("\n[PUT] 帳號 B 首次完善個人檔案：")
    setup_profile_b = {
        "phone": "0988333444",
        "birthday": "1999-10-10",
        "gender": "男",
        "levels": {"羽球": "B", "籃球": "B"}
    }
    make_request("/users/profile/", "PUT", data=setup_profile_b, token=token_b)

    # 首次完善個人資料（C 帳號，女性）
    print("\n[PUT] 帳號 C 首次完善個人檔案：")
    setup_profile_c = {
        "phone": "0988555666",
        "birthday": "2002-02-02",
        "gender": "女",
        "levels": {"羽球": "C"}
    }
    make_request("/users/profile/", "PUT", data=setup_profile_c, token=token_c)

    # 再次修改個人檔案，驗證 birthday 與 gender 唯讀（不予修改）
    print("\n[PUT] 帳號 A 嘗試變更生日與性別（預期原值不變）：")
    change_profile = {
        "name": "陳主揪改名",
        "birthday": "1990-12-12",
        "gender": "女"
    }
    status, change_res = make_request("/users/profile/", "PUT", data=change_profile, token=token_a)
    if change_res:
        print(f"👉 暱稱變更為: {change_res.get('name')}")
        print(f"👉 生日原值 (應為 2000-05-20): {change_res.get('birthday')}")
        print(f"👉 性別原值 (應為 男): {change_res.get('gender')}")

    # ==========================================
    # 4. 主揪發起球局 (價格限制與自動計算)
    # ==========================================
    print_header("4. 主揪發起球局 (價格限制與自動計算 split_price)")
    
    # 測試費用超過 10,000 元
    print("\n[POST] 發起價格 15,000 元的球局（預期 400 驗證錯誤）：")
    invalid_game = {
        "game_name": "無效球局",
        "sport_id": 1,
        "court_id": 1,
        "most_players": 2,
        "target_level": "B",
        "booking_date": "2026-06-20",
        "start_time": "18:00",
        "duration": "2 小時",
        "total_price": 15000.0,
        "gender_limit": "不限"
    }
    make_request("/games/", "POST", data=invalid_game, token=token_a)

    # 發起正常球局，性別限制：限男
    print("\n[POST] 發起費用 1000 元球局，上限 2 人，限男（預期成功）：")
    valid_game = {
        "game_name": "週末歡樂羽球局",
        "sport_id": 2, # 羽球
        "court_id": 2,
        "most_players": 2,
        "target_level": "B",
        "booking_date": "2026-06-25",
        "start_time": "20:00",
        "duration": "2 小時",
        "total_price": 1000.0,
        "gender_limit": "限男",
        "game_note": "羽球雙打，限男性，大安羽球館。"
    }
    status, game_res = make_request("/games/", "POST", data=valid_game, token=token_a)
    if status != 201:
        print("❌ 建立球局失敗。")
        return
    game_id = game_res["id"]
    print(f"👉 球局 ID: {game_id}")
    print(f"👉 自動計算分攤價格 split_price (應為 500): {game_res.get('split_price')}")

    # ==========================================
    # 5. 報名與性別限制 / 候補防呆
    # ==========================================
    print_header("5. 報名與性別限制 / 候補防呆機制")
    
    # 測試性別不符報名（帳號 C 女性報名限男球局）
    print("\n[POST] 帳號 C (女) 報名此限男球局（預期 400 拒絕）：")
    make_request(f"/games/{game_id}/join/", "POST", token=token_c)

    # 帳號 B (男) 報名（成功加入，使球局滿員）
    print("\n[POST] 帳號 B (男) 報名此球局（預期成功加入）：")
    make_request(f"/games/{game_id}/join/", "POST", token=token_b)

    # 註冊新帳號 D 報名（應自動進入候補）
    print("\n[POST] 註冊新帳號 D 並報名（預期自動進入候補第一順位）：")
    _, reg_d = make_request("/auth/register", "POST", data={"name": "林候補", "email": "user_d@example.com", "password": "password123"})
    token_d = reg_d["token"]
    make_request("/users/profile/", "PUT", data={"phone": "0988777888", "birthday": "1998-01-01", "gender": "男", "levels": {"羽球": "B"}}, token=token_d)
    
    status, join_d_res = make_request(f"/games/{game_id}/join/", "POST", token=token_d)
    if join_d_res:
        print(f"👉 返回狀態: {join_d_res.get('status')}")
        print(f"👉 候補順位: {join_d_res.get('position')}")

    # ==========================================
    # 6. 防重複檢舉限制
    # ==========================================
    print_header("6. 防重複檢舉限制 (重複檢舉同人同球局)")
    
    report_data = {
        "game_id": game_id,
        "reported_user_id": user_id_b,
        "reason": "言行不當",
        "detail": "他在球局中口出惡言"
    }
    print("\n[POST] 帳號 A 第一次檢舉帳號 B：")
    status, rep_res1 = make_request("/reports/", "POST", data=report_data, token=token_a)
    
    print("\n[POST] 帳號 A 第二次重複檢舉帳號 B（預期 409 Conflict 錯誤）：")
    status, rep_res2 = make_request("/reports/", "POST", data=report_data, token=token_a)
    if status == 409:
        print("✅ 重複檢舉防範機制運作正常！")

    # ==========================================
    # 7. 防止刪除使用中場地
    # ==========================================
    print_header("7. 防止刪除使用中場地 (409 Conflict)")
    
    # 取得管理員的 Token
    admin_user = User.objects.filter(role='admin').first()
    _, login_admin = make_request("/auth/login", "POST", data={"email": admin_user.email, "password": "admin123"})
    admin_token = login_admin["token"]
    
    # 嘗試刪除有進行中球局使用的場館 (大安羽球館)
    venue_id_in_use = GameMatch.objects.get(id=game_id).court.venue.id
    print(f"\n[DELETE] 管理員刪除使用中場館 ID {venue_id_in_use}（預期 409 Conflict 拒絕）：")
    status, del_venue_res = make_request(f"/admin/venues/{venue_id_in_use}/", "DELETE", token=admin_token)
    if status == 409:
        print("✅ 防止刪除使用中場地機制運作正常！")

    # ==========================================
    # 8. 回饋結案狀態處理
    # ==========================================
    print_header("8. 回饋結案狀態處理 (不刪除並標記 is_handled)")
    
    # 提交回饋
    print("\n[POST] 帳號 A 提交回饋：")
    fb_data = {
        "type": "建議",
        "content": "希望增加多一點排球場"
    }
    _, fb_res = make_request("/feedback/", "POST", data=fb_data, token=token_a)
    fb_id = fb_res["id"]
    
    # 管理員取得未處理回饋
    print("\n[GET] 管理員讀取未處理回饋：")
    status, fb_list = make_request("/admin/feedbacks?is_handled=false", "GET", token=admin_token)
    print(f"👉 未處理回饋筆數: {len(fb_list)}")
    
    # 標記為已處理
    print(f"\n[PUT] 管理員處理回饋 ID {fb_id}：")
    status, handled_res = make_request(f"/admin/feedbacks/{fb_id}/handle", "PUT", data={"is_handled": True}, token=admin_token)
    if handled_res:
        print(f"👉 狀態更新為 is_handled: {handled_res.get('is_handled')}")
        
    # 再次取得未處理回饋
    print("\n[GET] 管理員再次讀取未處理回饋：")
    _, fb_list_after = make_request("/admin/feedbacks?is_handled=false", "GET", token=admin_token)
    print(f"👉 未處理回饋筆數 (應減少 1): {len(fb_list_after)}")

    # ==========================================
    # 9. 主揪佈告欄歷史紀錄與發佈公告
    # ==========================================
    print_header("9. 主揪佈告欄公告與發佈權限")
    
    # 非主揪 B 發佈公告
    print("\n[POST] 非主揪帳號 B 試圖在球局發公告（預期 403 Forbidden 拒絕）：")
    make_request(f"/games/{game_id}/announcements/", "POST", data={"text": "今天我要遲到 5 分鐘。"}, token=token_b)

    # 主揪 A 發佈公告
    print("\n[POST] 主揪帳號 A 發佈佈告欄公告（預期成功）：")
    make_request(f"/games/{game_id}/announcements/", "POST", data={"text": "大家記得帶紅色球拍。"}, token=token_a)

    # 取得佈告欄公告
    print("\n[GET] 取得該球局的公告清單：")
    status, ann_list = make_request(f"/games/{game_id}/announcements/", "GET", token=token_b)
    if ann_list:
        print(json.dumps(ann_list, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("🎉 所有 V1.4 API 及業務防呆測試全部執行完畢！")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_tests()
