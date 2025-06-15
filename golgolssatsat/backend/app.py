import json
import os
import csv
import random
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, send_from_directory

app = Flask(__name__)
app.secret_key = "golgolssatsat123!"


DATA_DIR = "data"
UPLOADS_DIR = "uploads" 
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True) 

def load_json_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json_data(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------- 전체 지역 불러오기 --------------------
def load_all_regions_from_csv(path="regions.csv"):
    regions = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            city, district = row
            regions.append(f"{city} {district}")
    return regions

all_korea_regions = load_all_regions_from_csv()

# -------------------- 클래스 정의 --------------------
class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.registered_at = datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "registered_at": self.registered_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Photo:
    def __init__(self, photo_id, region_name, user_email, path):
        self.id = photo_id
        self.region_name = region_name
        self.user_email = user_email
        self.path = path
        self.uploaded_at = datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "region_name": self.region_name,
            "user_email": self.user_email,
            "path": self.path,
            "uploaded_at": self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Memo:
    def __init__(self, region_name, user_email, content):
        self.region_name = region_name
        self.user_email = user_email
        self.content = content
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "region_name": self.region_name,
            "user_email": self.user_email,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class VisitHistory:
    def __init__(self, region_name, user_email, visit_date):
        self.region_name = region_name
        self.user_email = user_email
        self.visit_date = visit_date

    def to_dict(self):
        return {
            "region_name": self.region_name,
            "user_email": self.user_email,
            "visit_date": self.visit_date
        }

class Tag:
    def __init__(self, photo_id, keyword):
        self.photo_id = photo_id
        self.keyword = keyword
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "photo_id": self.photo_id,
            "keyword": self.keyword,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Direction:
    def __init__(self, origin_coord, dest_coord):
        self.origin = origin_coord
        self.dest = dest_coord

    def get_route(self):
        return f"https://map.kakao.com/link/to/{self.dest}"

# -------------------- 전역 저장소 --------------------
users = {}
photos = []
memos = []
visit_histories = []
tags = []
user_settings = {}

# -------------------- 기능 함수 --------------------
def spin_roulette():
    if not all_korea_regions:
        return {"name": "추천할 지역이 없습니다"}
    return {"name": random.choice(all_korea_regions)}

def calculate_statistics():
    unique_regions = {p.region_name for p in photos}
    return {
        "visited_regions": len(unique_regions),
        "completion_rate": round((len(unique_regions) / len(all_korea_regions)) * 100, 2)
    }

# -------------------- 페이지 --------------------
@app.route("/")
def home():
    email = session.get("user_email")
    settings = user_settings.get(email, {}) if email else {}
    return render_template("index.html", user_settings=settings)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = request.json
    if data["email"] in users:
        return jsonify({"message": "이미 등록된 이메일입니다."}), 400
    users[data["email"]] = User(data["name"], data["email"], data["password"])
    return jsonify({"message": "회원가입 성공"})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    data = request.json
    user = users.get(data["email"])
    if user and user.password == data["password"]:
        session["user_email"] = data["email"]
        return jsonify({"message": "로그인 성공", "user": user.to_dict()})
    return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return jsonify({"message": "로그아웃 완료"})

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/record.html")
def record_page():
    return render_template("record.html")

@app.route("/roulette")
def roulette_page():
    return render_template("roulette.html")

@app.route("/statistics")
def statistics_page():
    return render_template("stats.html")


@app.route("/api/statistics")
def get_stats_data():
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    user_photos = [p for p in photos if p.user_email == email]
    user_visits = [v for v in visit_histories if v.user_email == email]

    total_regions_count = len(all_korea_regions)
    visited_regions_count = len({p.region_name for p in user_photos})
    completion_rate = 0
    if total_regions_count > 0:
        completion_rate = round((visited_regions_count / total_regions_count) * 100, 2)

    visits_by_province = {}
    visited_regions = {p.region_name for p in user_photos}
    for region in visited_regions:
        province = region.split(' ')[0]
        visits_by_province[province] = visits_by_province.get(province, 0) + 1
    
    province_labels = list(visits_by_province.keys())
    province_data = list(visits_by_province.values())

    visits_by_month = [0] * 12
    for visit in user_visits:
        try:
            month = int(visit.visit_date.split('-')[1])
            if 1 <= month <= 12:
                visits_by_month[month - 1] += 1
        except (ValueError, IndexError):
            continue
    
    month_labels = [f"{i}월" for i in range(1, 13)]

    return jsonify({
        "total_regions_count": total_regions_count,
        "visited_regions_count": visited_regions_count,
        "completion_rate": completion_rate,
        "visits_by_province": {
            "labels": province_labels,
            "data": province_data
        },
        "visits_by_month": {
            "labels": month_labels,
            "data": visits_by_month
        }
    })

@app.route("/setting")
def setting_page():
    return render_template("setting.html")

# -------------------- 데이터 API --------------------

# /upload 라우트를 파일과 모든 데이터를 함께 처리하도록 수정합니다.
@app.route("/upload", methods=["POST"])
def upload():
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    region_name = request.form.get("region_name")
    visit_date = request.form.get("visit_date")
    memo_content = request.form.get("memo")
    tag_keyword = request.form.get("tag")

    # 사진 파일이 있는 경우 (신규 등록 또는 사진 교체)
    if 'photo' in request.files:
        photo_file = request.files['photo']
        filename = photo_file.filename
        file_path = os.path.join(UPLOADS_DIR, filename)
        photo_file.save(file_path)
        db_path = f"/{UPLOADS_DIR}/{filename}"

        # 기존에 이 지역에 대한 사진이 있었는지 확인
        existing_photo = next((p for p in photos if p.user_email == email and p.region_name == region_name), None)

        if existing_photo:
            # 사진 업데이트
            existing_photo.path = db_path
            existing_photo.uploaded_at = datetime.now()
            photo_id = existing_photo.id
        else:
            # 새 사진 등록
            photo_id = len(photos) + 1
            photo = Photo(photo_id, region_name, email, db_path)
            photos.append(photo)
    else:
        # 사진 파일이 없는 경우 (기존 기록 내용만 수정)
        existing_photo = next((p for p in photos if p.user_email == email and p.region_name == region_name), None)
        if not existing_photo:
            return jsonify({"message": "수정할 기존 기록이 없습니다. 먼저 사진을 등록해주세요."}), 400
        photo_id = existing_photo.id

    # 방문 기록 업데이트 또는 추가
    existing_visit = next((v for v in visit_histories if v.user_email == email and v.region_name == region_name), None)
    if existing_visit:
        existing_visit.visit_date = visit_date
    else:
        visit = VisitHistory(region_name, email, visit_date)
        visit_histories.append(visit)

    # 메모 업데이트 또는 추가
    existing_memo = next((m for m in memos if m.user_email == email and m.region_name == region_name), None)
    if existing_memo:
        existing_memo.content = memo_content
        existing_memo.created_at = datetime.now()
    else:
        memo = Memo(region_name, email, memo_content)
        memos.append(memo)

    # 태그 업데이트 또는 추가 (사진 ID 기준)
    existing_tag = next((t for t in tags if t.photo_id == photo_id), None)
    if existing_tag:
        existing_tag.keyword = tag_keyword
        existing_tag.created_at = datetime.now()
    else:
        tag = Tag(photo_id, tag_keyword)
        tags.append(tag)
    
    return jsonify({"message": "성공적으로 저장되었습니다."})

# --- 업로드된 파일 서빙을 위한 라우트를 추가합니다 ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


# 아래 API들은 현재 record.html에서는 사용되지 않지만, 다른 기능에서 사용할 수 있으므로 남겨둡니다.
@app.route("/memo", methods=["POST"])
def add_memo():
    data = request.json
    email = session.get("user_email")
    memo = Memo(data["region_name"], email, data["content"])
    memos.append(memo)
    return jsonify({"message": "메모 저장 완료", "memo": memo.to_dict()})

@app.route("/visit", methods=["POST"])
def save_visit():
    data = request.json
    email = session.get("user_email")
    visit = VisitHistory(data["region_name"], email, data["visit_date"])
    visit_histories.append(visit)
    return jsonify({"message": "방문 기록 저장 완료", "visit": visit.to_dict()})

@app.route("/tag", methods=["POST"])
def add_tag():
    data = request.json
    tag = Tag(data["photo_id"], data["keyword"])
    tags.append(tag)
    return jsonify({"message": "태그 저장 완료", "tag": tag.to_dict()})

@app.route("/record/<region_name>")
def get_region_record(region_name):
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    user_photos = [p for p in photos if p.region_name == region_name and p.user_email == email]
    photo = user_photos[-1].to_dict() if user_photos else None
    tag = next((t.to_dict() for t in tags if photo and t.photo_id == photo["id"]), None)

    result = {
        "photo": photo,
        "memo": next((m.to_dict() for m in memos if m.region_name == region_name and m.user_email == email), None),
        "visit": next((v.to_dict() for v in visit_histories if v.region_name == region_name and v.user_email == email), None),
        "tag": tag
    }
    return jsonify(result)

@app.route("/statistics", methods=["GET"])
def stats():
    return jsonify(calculate_statistics())

@app.route("/roulette-api")
def roulette_api():
    return jsonify(spin_roulette())

@app.route("/my-settings")
def get_user_settings():
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401
    return jsonify(user_settings.get(email, {}))

@app.route("/settings", methods=["POST"])
def change_settings():
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401
    data = request.json
    user_settings[email] = {
        "dark_mode": data.get("dark_mode"), # .get()으로 안전하게 접근
        "nav_app": data.get("nav_app")    # map_style -> nav_app 으로 변경
    }
    return jsonify({"message": "설정 저장 완료"})

@app.route("/directions", methods=["POST"])
def get_direction():
    data = request.json
    d = Direction(data["origin_coord"], data["dest_coord"])
    return jsonify({"route_url": d.get_route()})

@app.route("/my-map-data")
def get_my_map_data():
    email = session.get("user_email")
    if not email:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    # 현재 사용자의 모든 사진 기록을 찾습니다.
    user_photos = [p for p in photos if p.user_email == email]
    
    # (같은 지역에 여러 사진을 올렸을 경우, 가장 마지막에 올린 사진으로 지도에 표시)
    latest_photos = {}
    for photo in user_photos:
        latest_photos[photo.region_name] = photo.path

    return jsonify(latest_photos)

# -------------------- 실행 --------------------
if __name__ == "__main__":
    app.run(debug=True)