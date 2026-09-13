import csv
import random
import io
import json
import re
import os
from gtts import gTTS
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# --- CẤU HÌNH CƠ BẢN & MODEL (GEMINI 3.6 FLASH) ---
MODEL_NAME = "gemini-3.6-flash"

st.set_page_config(
    page_title="Wordland - Chạm tay vào thế giới ngôn ngữ 🚀", 
    page_icon="🎨", 
    layout="wide"
)

# Khởi tạo Gemini Client tự động
client = genai.Client()

# --- HÀM TẠO HIỆU ỨNG PHÁO HOA ---
def trigger_confetti():
    confetti_html = """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
            confetti({
                particleCount: 120,
                spread: 100,
                origin: { y: 0.6 }
            });
        </script>
    """
    components.html(confetti_html, height=0, width=0)

# --- HÀM DỌN DẸP CHUỖI JSON CHỐNG LỖI ---
def clean_json_text(text):
    if not text:
        return ""
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    return text.strip()

# --- HÀM TẠO NỘI DUNG AI ÉP CHUẨN JSON VÀ LƯU CACHE ---
@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_content_cached(prompt: str):
    try:
        # Ép Gemini trả về định dạng application/json thuần túy
        config = types.GenerateContentConfig(response_mime_type="application/json")
        res = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config=config
        )
        return res.text if res and hasattr(res, 'text') else ""
    except Exception as e:
        return ""

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main-title {
        color: #FFFFFF;
        text-align: center;
        font-weight: 900;
        font-size: 2.8rem;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #F8EFBA;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 20px;
        text-shadow: 1px 2px 5px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        padding: 8px 12px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 12px;
        padding: 0px 16px;
        color: #ffffff !important;
        font-weight: 600;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        color: #ffeaa7 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffffff 0%, #f0f3f7 100%) !important;
        color: #6c5ce7 !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        transform: scale(1.03);
    }
    .stTabs [data-baseweb="tab-panel"] {
        animation: fadeInSlideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeInSlideUp {
        0% { opacity: 0; transform: translateY(15px) scale(0.99); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 260px;
        perspective: 1000px;
        margin-bottom: 15px;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        border-radius: 20px;
    }
    .flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 20px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .flip-card-front {
        background: linear-gradient(135deg, #ffffff 0%, #f0f3f7 100%);
        border: 3px solid #FF7675;
        color: #2D3436;
    }
    .flip-card-back {
        background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
        border: 3px solid #a29bfe;
        color: white;
        transform: rotateY(180deg);
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6) !important;
    }
    .reading-box, .grammar-lesson-box, .analytics-box, .admin-card, .group-card, .mail-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 18px;
        padding: 20px;
        border-left: 6px solid #6C5CE7;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        color: #2d3436;
    }
    .group-card { border-left-color: #00b894; }
    .mail-card { border-left-color: #fdcb6e; }
    .admin-card { border-left-color: #d63031; }
</style>
""", unsafe_allow_html=True)

english_topics = [
    "Daily Life (Đời sống hàng ngày)", "Work & Career (Nghề nghiệp)", 
    "Travel & Tourism (Du lịch)", "Food & Dining (Ẩm thực)",
    "Shopping (Mua sắm)", "Education & School (Trường học)", 
    "Health & Fitness (Sức khỏe)", "Technology & Science (Công nghệ)", 
    "Entertainment & Media (Giải trí)", "Family & Relationships (Gia đình)"
]

english_tenses = [
    "Simple Present (Hiện tại đơn)", "Present Continuous (Hiện tại tiếp diễn)", 
    "Present Perfect (Hiện tại hoàn thành)", "Present Perfect Continuous (HTHT tiếp diễn)",
    "Simple Past (Quá khứ đơn)", "Past Continuous (Quá khứ tiếp diễn)", 
    "Past Perfect (Quá khứ hoàn thành)", "Past Perfect Continuous (QKHT tiếp diễn)",
    "Simple Future (Tương lai đơn)", "Future Continuous (Tương lai tiếp diễn)", 
    "Future Perfect (Tương lai hoàn thành)", "Future Perfect Continuous (TLHT tiếp diễn)"
]

education_levels = [
    "🏫 Cấp 1 (Tiểu học)",
    "🏫 Cấp 2 (THCS)",
    "🏫 Cấp 3 (THPT)",
    "🎓 Đại học / Cao đẳng",
    "🏆 🎯 Ôn thi Chứng chỉ (TOEFL / IELTS / TOEIC)",
    "🏅 💻 Thi Học sinh giỏi / Tin học trẻ"
]

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- HÀM XỬ LÝ CSV & TÀI KHOẢN ---
def get_all_users_from_csv():
    rows = []
    try:
        with open("list.csv", mode="r", encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r]
    except FileNotFoundError:
        pass
    return rows

def check_login(user, pwd):
    users = get_all_users_from_csv()
    for row in users:
        if row and row[0].strip() == user and len(row) > 1 and row[1].strip() == pwd:
            is_admin = (user == "lephuchieuadmin")
            xp = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else (999999 if is_admin else 0)
            fullname = row[3].strip() if len(row) > 3 else ("Lê Phúc Hiếu (Quản Trị Viên)" if is_admin else "Học viên")
            user_class = row[4].strip() if len(row) > 4 else ("Admin Root" if is_admin else "Chưa nhập")
            user_school = row[5].strip() if len(row) > 5 else ("Wordland System" if is_admin else "Chưa nhập")
            user_level = row[6].strip() if len(row) > 6 else ("🛠️ Admin Control" if is_admin else "Chưa nhập")
            return True, {
                "is_admin": is_admin,
                "xp": xp, "fullname": fullname,
                "class": user_class, "school": user_school, "level": user_level
            }

    if user == "lephuchieuadmin" and pwd == "hieutinhoctre":
        return True, {
            "is_admin": True,
            "xp": 999999,
            "fullname": "Lê Phúc Hiếu (Quản Trị Viên)",
            "class": "Admin Root",
            "school": "Wordland System",
            "level": "🛠️ Admin Control"
        }

    return False, {}

def register_user(user, pwd, fullname, user_class, school, level, xp=0):
    if user.lower() == "lephuchieuadmin":
        return False, "Không thể tạo trùng với tài khoản Admin!"
    
    existing_users = [row[0].strip().lower() for row in get_all_users_from_csv()]
    if user.lower() in existing_users:
        return False, "Tên đăng nhập đã tồn tại!"
    
    with open("list.csv", mode="a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([user, pwd, xp, fullname, user_class, school, level])
    return True, "Thành công!"

def admin_delete_student(user):
    try:
        rows = get_all_users_from_csv()
        new_rows = [r for r in rows if r and r[0].strip().lower() != user.lower()]
        
        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(new_rows)
            
        groups = load_groups_data()
        updated = False
        for g_name, g_info in groups.items():
            if user in g_info.get("members", []):
                g_info["members"].remove(user)
                updated = True
        if updated:
            save_groups_data(groups)

        return True
    except Exception:
        return False

def update_user_profile_full(user, new_pwd, fullname, user_class, school, level):
    try:
        rows = get_all_users_from_csv()
        found = False
        
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == user.lower():
                # Giữ lại mật khẩu cũ nếu người dùng để trống
                pwd = new_pwd.strip() if new_pwd.strip() else (row[1] if len(row) > 1 else "")
                xp = row[2] if len(row) > 2 else (999999 if user == "lephuchieuadmin" else 0)
                
                # Cập nhật đầy đủ 7 cột thông tin
                rows[i] = [user, pwd, xp, fullname, user_class, school, level]
                found = True
                break

        if not found and user == "lephuchieuadmin":
            pwd = new_pwd.strip() if new_pwd.strip() else "hieutinhoctre"
            rows.append([user, pwd, 999999, fullname, user_class, school, level])

        # Ghi đè lại toàn bộ tệp list.csv
        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
            
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu vào CSV: {e}")
        return False

def admin_update_student(user, new_fullname, new_pwd):
    try:
        rows = get_all_users_from_csv()
        updated = False
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == user.lower():
                pwd = new_pwd.strip() if new_pwd.strip() else (row[1] if len(row) > 1 else "")
                fname = new_fullname.strip() if new_fullname.strip() else (row[3] if len(row) > 3 else "")
                xp = row[2] if len(row) > 2 else 0
                u_class = row[4] if len(row) > 4 else ""
                u_school = row[5] if len(row) > 5 else ""
                u_level = row[6] if len(row) > 6 else ""
                rows[i] = [user, pwd, xp, fname, u_class, u_school, u_level]
                updated = True
                break

        if updated:
            with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
                csv.writer(f).writerows(rows)
            return True
        return False
    except Exception:
        return False

def save_xp_to_csv(user, new_xp):
    if user == "lephuchieuadmin":
        return
    try:
        rows = get_all_users_from_csv()
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == user.lower():
                pwd = row[1] if len(row) > 1 else ""
                fullname = row[3] if len(row) > 3 else ""
                user_class = row[4] if len(row) > 4 else ""
                school = row[5] if len(row) > 5 else ""
                level = row[6] if len(row) > 6 else ""
                rows[i] = [user, pwd, new_xp, fullname, user_class, school, level]
                break

        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
    except Exception:
        pass

def admin_modify_user_xp(target_user, points_change, action_type="add"):
    rows = get_all_users_from_csv()
    updated = False
    for i, row in enumerate(rows):
        if row and row[0].strip().lower() == target_user.lower():
            current_xp = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else 0
            if action_type == "add":
                new_xp = current_xp + points_change
            else:
                new_xp = max(0, current_xp - points_change)
            
            rows[i][2] = new_xp
            updated = True
            break
            
    if updated:
        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
        return True, new_xp
    return False, 0

def add_xp(points):
    if st.session_state.get("is_admin", False):
        return
    st.session_state.xp += points
    save_xp_to_csv(st.session_state.user, st.session_state.xp)

# --- HÀM XỬ LÝ DỮ LIỆU NHÓM (GROUPS JSON) ---
GROUPS_FILE = "groups.json"

def load_groups_data():
    if not os.path.exists(GROUPS_FILE):
        return {}
    try:
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_groups_data(data):
    try:
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

# --- HÀM XỬ LÝ LỜI MỜI / HỘP THƯ (INVITES JSON) ---
INVITES_FILE = "invites.json"

def load_invites_data():
    if not os.path.exists(INVITES_FILE):
        return []
    try:
        with open(INVITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_invites_data(data):
    try:
        with open(INVITES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def send_group_invite(sender, recipient, group_name, invite_type="join_request"):
    invites = load_invites_data()
    for inv in invites:
        if inv.get("sender") == sender and inv.get("recipient") == recipient and inv.get("group_name") == group_name and inv.get("status") == "pending":
            return False, "Lời mời/Yêu cầu này đã được gửi trước đó và đang chờ xử lý!"
            
    invites.append({
        "id": random.randint(100000, 999999),
        "sender": sender,
        "recipient": recipient,
        "group_name": group_name,
        "type": invite_type,
        "status": "pending"
    })
    save_invites_data(invites)
    return True, "Đã gửi lời mời thành công!"

def admin_send_ai_homework(admin_user, target_student, skill_type, topic, level):
    try:
        if skill_type == "Trắc nghiệm Ngữ pháp":
            prompt = f"Tạo 3 câu hỏi trắc nghiệm ngữ pháp tiếng Anh về chủ đề '{topic}' cho trình độ '{level}'. Trả về JSON dạng danh sách: [{{\"id\": 1, \"question\": \"...\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], \"answer\": \"A\"}}]"
        elif skill_type == "Đọc hiểu (Reading)":
            prompt = f"Tạo 1 bài đọc ngắn khoảng 60 từ về chủ đề '{topic}' và 2 câu hỏi trắc nghiệm cho trình độ '{level}'. Trả về JSON dạng: {{\"passage\": \"...\", \"questions\": [{{\"id\": 1, \"question\": \"...\", \"options\": [\"A...\", \"B...\", \"C...\", \"D...\"], \"answer\": \"B\"}}]}}"
        elif skill_type == "Nghe (Listening)":
            prompt = f"Tạo 1 đoạn hội thoại ngắn tiếng Anh khoảng 40 từ về chủ đề '{topic}' và 2 câu hỏi trắc nghiệm cho trình độ '{level}'. Trả về JSON dạng: {{\"audio_script\": \"...\", \"questions\": [{{\"id\": 1, \"question\": \"...\", \"options\": [\"A...\", \"B...\", \"C...\", \"D...\"], \"answer\": \"A\"}}]}}"
        else: # Viết (Writing)
            prompt = f"Tạo 1 đề bài tập kỹ năng Viết về chủ đề '{topic}' cho trình độ '{level}'. Trả về JSON dạng: {{\"prompt\": \"Nội dung yêu cầu viết đoạn văn...\"}}"

        raw_text = generate_ai_content_cached(prompt)
        cleaned = clean_json_text(raw_text)
        if not cleaned:
            return False, "⚠️ Không thể kết nối với Gemini API hoặc quá hạn mức!"
            
        ai_content_json = json.loads(cleaned)

        invites = load_invites_data()
        invites.append({
            "id": random.randint(100000, 999999),
            "sender": admin_user,
            "recipient": target_student,
            "group_name": f"Bài tập: {skill_type} ({topic})",
            "type": "homework_task",
            "skill": skill_type,
            "level": level,
            "content": ai_content_json,
            "status": "pending",
            "score": 0,
            "max_score": 0,
            "teacher_feedback": "",
            "student_submission": None
        })
        save_invites_data(invites)
        return True, "Đã giao bài tập AI thành công vào hộp thư học sinh!"
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return False, "⚠️ Đã vượt quá hạn mức miễn phí (Rate Limit) của Gemini API. Vui lòng thử lại sau ít phút!"
        return False, f"Lỗi tạo bài tập từ AI: {err_msg}"

# Initialize States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "fullname" not in st.session_state:
    st.session_state.fullname = ""
if "user_class" not in st.session_state:
    st.session_state.user_class = ""
if "school" not in st.session_state:
    st.session_state.school = ""
if "level" not in st.session_state:
    st.session_state.level = ""
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>🎒 Wordland - Chạm tay vào thế giới ngôn ngữ 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Học Tiếng Anh Thông Minh Cùng AI Gemini 3.6 Flash</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2.2, 1])
    with col_b:
        tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký mới"])
        
        with tab1:
            user_input = st.text_input("Tên đăng nhập", key="login_user")
            pwd_input = st.text_input("Mật khẩu", type="password", key="login_pwd")
            if st.button("🚀 Vào học ngay", use_container_width=True):
                success, info = check_login(user_input.strip(), pwd_input.strip())
                if success:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = info["is_admin"]
                    st.session_state.user = user_input.strip()
                    st.session_state.xp = info["xp"]
                    st.session_state.fullname = info["fullname"]
                    st.session_state.user_class = info["class"]
                    st.session_state.school = info["school"]
                    st.session_state.level = info["level"]
                    trigger_confetti()
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu!")
                    
        with tab2:
            st.markdown("##### 👤 **Thông tin tài khoản**")
            reg_user = st.text_input("Tên đăng nhập *", key="reg_user")
            reg_pwd = st.text_input("Mật khẩu *", type="password", key="reg_pwd")
            
            st.markdown("##### 🎓 **Thông tin cá nhân & Trình độ học tập**")
            reg_fullname = st.text_input("Họ và Tên học sinh *", placeholder="Ví dụ: Lê Phúc Hiếu", key="reg_fullname")
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                reg_class = st.text_input("Lớp *", placeholder="Ví dụ: 8A1 hoặc Lớp 11", key="reg_class")
            with col_r2:
                reg_school = st.text_input("Trường học *", placeholder="Ví dụ: THCS Nguyễn Du", key="reg_school")
                
            reg_level = st.selectbox(
                "🎯 Bạn đang học / ôn thi Tiếng Anh theo cấp độ nào? *",
                education_levels, key="reg_level"
            )
            
            if st.button("✨ Tạo tài khoản mới", use_container_width=True):
                if not reg_user or not reg_pwd or not reg_fullname or not reg_class or not reg_school:
                    st.warning("Vui lòng điền đầy đủ các thông tin bắt buộc (*)! ")
                else:
                    ok, msg = register_user(
                        reg_user.strip(), reg_pwd.strip(), reg_fullname.strip(), 
                        reg_class.strip(), reg_school.strip(), reg_level
                    )
                    if ok:
                        st.success(msg)
                        trigger_confetti()
                    else:
                        st.error(msg)
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown(f"### 🌟 **{st.session_state.fullname}**")
st.sidebar.markdown(f"🆔 **Tài khoản:** `{st.session_state.user}`")
st.sidebar.markdown(f"🏫 **Lớp / Trường:** `{st.session_state.user_class}` - `{st.session_state.school}`")
st.sidebar.markdown(f"🎯 **Cấp độ học:**\n`{st.session_state.level}`")
st.sidebar.divider()

all_invites = load_invites_data()
my_pending_invites = [inv for inv in all_invites if inv.get("recipient") == st.session_state.user and inv.get("status") == "pending"]

if not st.session_state.is_admin:
    st.sidebar.markdown(f"⭐ **Điểm kinh nghiệm (XP):** `{st.session_state.xp}`")
    st.sidebar.markdown(f"❤️ **Từ vựng đã lưu:** `{len(st.session_state.favorites)}` từ")
    st.sidebar.markdown(f"📬 **Hộp thư thông báo:** `{len(my_pending_invites)}` tin mới")
else:
    st.sidebar.markdown("👑 **Quyền hạn:** `Quản trị hệ thống (Admin)`")
    admin_pending = [inv for inv in all_invites if inv.get("status") == "pending"]
    st.sidebar.markdown(f"📬 **Hộp thư Admin:** `{len(admin_pending)}` yêu cầu mới")

with st.sidebar.expander("✏️ **Đổi thông tin & Mật khẩu**"):
    new_fullname = st.text_input("Họ và Tên / Tên hiển thị:", value=st.session_state.fullname, key="edit_fullname")
    new_pass_input = st.text_input("Mật khẩu mới (Để trống nếu giữ nguyên):", type="password", key="edit_pass")
    new_class = st.text_input("Lớp:", value=st.session_state.user_class, key="edit_class")
    new_school = st.text_input("Trường:", value=st.session_state.school, key="edit_school")
    
    current_level_idx = 0
    if st.session_state.level in education_levels:
        current_level_idx = education_levels.index(st.session_state.level)
        
    new_level = st.selectbox("Cấp độ học / Ôn thi:", education_levels, index=current_level_idx, key="edit_level")
    
    if st.button("💾 Lưu thay đổi", use_container_width=True, key="btn_save_user_info"):
        if not new_fullname.strip() or not new_class.strip() or not new_school.strip():
            st.warning("Vui lòng không để trống các trường bắt buộc!")
        else:
            # 1. Lưu vào file CSV
            if update_user_profile_full(st.session_state.user, new_pass_input, new_fullname.strip(), new_class.strip(), new_school.strip(), new_level):
                # 2. Cập nhật ngay lập tức vào session_state để lưu giữ thông tin hiển thị
                st.session_state.fullname = new_fullname.strip()
                st.session_state.user_class = new_class.strip()
                st.session_state.school = new_school.strip()
                st.session_state.level = new_level
                
                trigger_confetti()
                st.success("🎉 Cập nhật và lưu thông tin học viên thành công!")
                st.rerun()

st.sidebar.write("")
if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.rerun()

# ==============================================================================
# MÀN HÌNH BẢNG ĐIỀU KHIỂN DÀNH RIÊNG CHO ADMIN
# ==============================================================================
if st.session_state.is_admin:
    st.markdown("<h1 class='main-title'>🛠️ TRANG QUẢN TRỊ ADMIN - WORDLAND 🛠️</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Hệ thống quản lý điểm số, tài khoản, nhóm và giao bài tập AI toàn diện</p>", unsafe_allow_html=True)
    
    users_data = [u for u in get_all_users_from_csv() if u and u[0] != "lephuchieuadmin"]
    groups_data = load_groups_data()

    st.markdown("### 📊 **Thống Kê Tổng Quan**")
    col_adm1, col_adm2, col_adm3, col_adm4 = st.columns(4)
    with col_adm1:
        st.metric("👥 Tổng Học Sinh Đăng Ký", f"{len(users_data)} tài khoản")
    with col_adm2:
        total_system_xp = sum(int(u[2]) for u in users_data if len(u) > 2 and u[2].isdigit())
        st.metric("⭐ Tổng Điểm XP Toàn Hệ Thống", f"{total_system_xp} XP")
    with col_adm3:
        top_user = max(users_data, key=lambda x: int(x[2]) if len(x)>2 and x[2].isdigit() else 0) if users_data else None
        top_name = top_user[3] if top_user and len(top_user)>3 else "Chưa có"
        top_xp = top_user[2] if top_user and len(top_user)>2 else 0
        st.metric("🏆 Học Sinh Dẫn Đầu", f"{top_name} ({top_xp} XP)")
    with col_adm4:
        st.metric("👥 Tổng Nhóm Học Tập", f"{len(groups_data)} nhóm")

    st.divider()

    tab_adm_list, tab_adm_edit_xp, tab_adm_users_mgr, tab_adm_groups_mgr, tab_adm_mailbox, tab_adm_hw, tab_adm_grading = st.tabs([
        "📋 Danh Sách Điểm Học Sinh", 
        "➕/➖ Cộng / Trừ Điểm XP", 
        "👤 Quản Lý Học Sinh (Thêm / Xóa / Sửa)", 
        "👥 Quản Lý Nhóm (Tạo / Sửa / Xóa / Thêm TV)",
        "📬 Hộp Thư & Duyệt Yêu Cầu Gia Nhập",
        "📚 Giao Bài Tập AI Cho Học Sinh",
        "💯 Xem Điểm & Chấm Lại Bài Tự Luận/Trắc Nghiệm"
    ])

    with tab_adm_list:
        st.subheader("📋 Danh Sách Chi Tiết Tất Cả Học Sinh")
        if users_data:
            table_data = []
            for u in users_data:
                table_data.append({
                    "Tài khoản": u[0] if len(u)>0 else "",
                    "Mật khẩu": u[1] if len(u)>1 else "",
                    "Họ và Tên": u[3] if len(u)>3 else "",
                    "Lớp": u[4] if len(u)>4 else "",
                    "Trường": u[5] if len(u)>5 else "",
                    "Cấp độ học": u[6] if len(u)>6 else "",
                    "Điểm XP": int(u[2]) if len(u)>2 and u[2].isdigit() else 0
                })
            st.dataframe(table_data, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu học sinh trong tệp list.csv!")

    with tab_adm_edit_xp:
        st.subheader("⚡ Điều Chỉnh Điểm XP Cho Học Sinh")
        if users_data:
            user_options = [f"{u[0]} - {u[3]} (Hiện có: {u[2]} XP)" for u in users_data]
            selected_user_str = st.selectbox("🎯 Chọn tài khoản học sinh:", user_options, key="adm_xp_sel")
            target_username = selected_user_str.split(" - ")[0].strip()

            col_xp1, col_xp2 = st.columns(2)
            with col_xp1:
                action = st.radio("Thao tác điểm:", ["➕ Cộng Điểm XP", "➖ Trừ Điểm XP"], key="adm_xp_radio")
            with col_xp2:
                points_input = st.number_input("Số điểm XP điều chỉnh:", min_value=1, max_value=10000, value=50, step=10, key="adm_xp_val")

            if st.button("🚀 XÁC NHẬN THAY ĐỔI ĐIỂM", type="primary", use_container_width=True, key="btn_adm_xp"):
                act_type = "add" if "Cộng" in action else "sub"
                success, new_xp = admin_modify_user_xp(target_username, points_input, act_type)
                if success:
                    trigger_confetti()
                    st.success(f"🎉 Đã cập nhật thành công! Tài khoản `{target_username}` hiện có **{new_xp} XP**!")
                    st.rerun()
                else:
                    st.error("Không thể cập nhật điểm!")
        else:
            st.warning("Hiện chưa có học sinh nào!")

    with tab_adm_users_mgr:
        st.subheader("👤 Quản Lý Tài Khoản Học Sinh")
        adm_u_tab1, adm_u_tab2, adm_u_tab3 = st.tabs(["➕ Thêm Học Sinh Mới", "✏️ Sửa Tên & Mật Khẩu", "❌ Xóa Học Sinh"])
        
        with adm_u_tab1:
            st.markdown("##### ➕ **Tạo Tài Khoản Học Sinh Mới Trực Tiếp**")
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                new_s_user = st.text_input("Tên đăng nhập học sinh *:", key="adm_add_u_user")
                new_s_pass = st.text_input("Mật khẩu *:", type="password", key="adm_add_u_pass")
                new_s_fullname = st.text_input("Họ và Tên học sinh *:", key="adm_add_u_fname")
            with col_add2:
                new_s_class = st.text_input("Lớp học *:", value="8A1", key="adm_add_u_class")
                new_s_school = st.text_input("Trường học *:", value="THCS Nguyễn Du", key="adm_add_u_school")
                new_s_level = st.selectbox("Cấp độ học *:", education_levels, key="adm_add_u_lvl")
            
            if st.button("🚀 XÁC NHẬN THÊM HỌC SINH", type="primary", use_container_width=True, key="btn_adm_add_student"):
                if not new_s_user.strip() or not new_s_pass.strip() or not new_s_fullname.strip():
                    st.warning("Vui lòng nhập đầy đủ Tên đăng nhập, Mật khẩu và Họ tên!")
                else:
                    ok, msg = register_user(new_s_user.strip(), new_s_pass.strip(), new_s_fullname.strip(), new_s_class.strip(), new_s_school.strip(), new_s_level)
                    if ok:
                        trigger_confetti()
                        st.success(f"🎉 Đã khởi tạo học sinh `{new_s_user.strip()}` thành công!")
                        st.rerun()
                    else:
                        st.error(msg)

        with adm_u_tab2:
            st.markdown("##### ✏️ **Chỉnh Sửa Thông Tin Học Sinh**")
            if users_data:
                user_opt_list = [f"{u[0]} ({u[3]})" for u in users_data]
                selected_student_raw = st.selectbox("Chọn học sinh cần sửa:", user_opt_list, key="adm_u_sel_edit")
                target_stu_user = selected_student_raw.split(" (")[0].strip()

                stu_info = next((u for u in users_data if u[0] == target_stu_user), None)
                if stu_info:
                    st.info(f"🆔 **Tài khoản đang chọn:** `{target_stu_user}` | Mật khẩu hiện tại: `{stu_info[1]}`")
                    col_su1, col_su2 = st.columns(2)
                    with col_su1:
                        adm_edit_name = st.text_input("Họ và Tên mới:", value=stu_info[3] if len(stu_info)>3 else "", key="adm_edit_fname")
                    with col_su2:
                        adm_edit_pwd = st.text_input("Mật khẩu mới (Để trống nếu giữ nguyên):", placeholder="Nhập MK mới...", type="password", key="adm_edit_pw")

                    if st.button("💾 CẬP NHẬT THÔNG TIN HỌC SINH", type="primary", use_container_width=True, key="btn_adm_update_stu"):
                        if admin_update_student(target_stu_user, adm_edit_name, adm_edit_pwd):
                            trigger_confetti()
                            st.success(f"Đã cập nhật thông tin thành công cho học sinh `{target_stu_user}`!")
                            st.rerun()
                        else:
                            st.error("Lỗi cập nhật dữ liệu học sinh!")
            else:
                st.warning("Chưa có học sinh nào!")

        with adm_u_tab3:
            st.markdown("##### ❌ **Xóa Hoàn Toàn Học Sinh Khỏi Hệ Thống**")
            if users_data:
                del_user_opt = [f"{u[0]} ({u[3]})" for u in users_data]
                selected_del_student = st.selectbox("Chọn học sinh muốn xóa:", del_user_opt, key="adm_del_u_sel")
                target_del_user = selected_del_student.split(" (")[0].strip()

                st.error(f"⚠️ Cảnh báo: Thao tác này sẽ xóa vĩnh viễn tài khoản `{target_del_user}` khỏi `list.csv` và các nhóm học tập!")
                if st.button("🔥 XÁC NHẬN XÓA HỌC SINH NÀY", type="primary", use_container_width=True, key="btn_adm_del_stu"):
                    if admin_delete_student(target_del_user):
                        st.success(f"Đã xóa thành công tài khoản học sinh `{target_del_user}`!")
                        st.rerun()
                    else:
                        st.error("Lỗi khi xóa học sinh!")
            else:
                st.warning("Chưa có học sinh nào!")

    with tab_adm_groups_mgr:
        st.subheader("👥 Quản Lý Nhóm Học Tập Toàn Diện")
        adm_g_tab1, adm_g_tab2, adm_g_tab3, adm_g_tab4 = st.tabs([
            "✨ Tạo Nhóm Mới", 
            "➕ Thêm Học Sinh Vào Nhóm Direct", 
            "✏️ Sửa Thông Tin Nhóm", 
            "🗑️ Xóa Nhóm"
        ])

        with adm_g_tab1:
            st.markdown("##### ✨ **Admin Tạo Nhóm Học Tập Mới**")
            adm_g_name = st.text_input("Tên nhóm mới *:", key="adm_g_name_create")
            adm_g_pass = st.text_input("Mã mật khẩu nhóm *:", type="password", key="adm_g_pass_create")
            
            if st.button("🚀 Khởi Tạo Nhóm", type="primary", use_container_width=True, key="btn_adm_create_g"):
                if not adm_g_name.strip() or not adm_g_pass.strip():
                    st.warning("Vui lòng nhập Tên nhóm và Mật khẩu nhóm!")
                elif adm_g_name.strip() in groups_data:
                    st.error("Nhóm này đã tồn tại trên hệ thống!")
                else:
                    groups_data[adm_g_name.strip()] = {
                        "leader": "lephuchieuadmin",
                        "passcode": adm_g_pass.strip(),
                        "members": ["lephuchieuadmin"]
                    }
                    save_groups_data(groups_data)
                    trigger_confetti()
                    st.success(f"Tạo nhóm **{adm_g_name.strip()}** thành công!")
                    st.rerun()

        with adm_g_tab2:
            st.markdown("##### ➕ **Thêm Học Sinh Trực Tiếp Vào Nhóm (Bỏ Qua Chờ Duyệt)**")
            if groups_data and users_data:
                target_g_sel = st.selectbox("Chọn nhóm học tập:", list(groups_data.keys()), key="adm_target_g_add")
                target_u_sel = st.selectbox("Chọn học sinh muốn thêm:", [u[0] for u in users_data], key="adm_target_u_add")

                if st.button("🤝 Thêm Vào Nhóm", type="primary", use_container_width=True, key="btn_adm_add_u_to_g"):
                    curr_g = groups_data[target_g_sel]
                    if target_u_sel not in curr_g["members"]:
                        curr_g["members"].append(target_u_sel)
                        groups_data[target_g_sel] = curr_g
                        save_groups_data(groups_data)
                        trigger_confetti()
                        st.success(f"Đã thêm học sinh `{target_u_sel}` vào nhóm **{target_g_sel}**!")
                        st.rerun()
                    else:
                        st.info(f"Học sinh `{target_u_sel}` đã có trong nhóm **{target_g_sel}** rồi!")
            else:
                st.warning("Cần có ít nhất 1 nhóm và 1 học sinh!")

        with adm_g_tab3:
            st.markdown("##### ✏️ **Chỉnh Sửa Tên Nhóm & Mật Khẩu Nhóm**")
            if groups_data:
                sel_edit_g = st.selectbox("Chọn nhóm cần sửa:", list(groups_data.keys()), key="adm_sel_g_edit")
                curr_g_info = groups_data[sel_edit_g]
                
                st.info(f"👥 **Nhóm đang chọn:** `{sel_edit_g}` | Mật khẩu hiện tại: `{curr_g_info.get('passcode')}`")
                col_eg1, col_eg2 = st.columns(2)
                with col_eg1:
                    new_group_name_input = st.text_input("Tên nhóm mới:", value=sel_edit_g, key="adm_new_gname_inp")
                with col_eg2:
                    new_group_pass_input = st.text_input("Mật khẩu nhóm mới:", value=curr_g_info.get("passcode"), key="adm_new_gpass_inp")

                if st.button("💾 CẬP NHẬT THÔNG TIN NHÓM", type="primary", use_container_width=True, key="btn_adm_update_group"):
                    updated_g = False
                    new_g_name_str = new_group_name_input.strip()
                    new_g_pass_str = new_group_pass_input.strip()

                    if new_g_name_str and new_g_name_str != sel_edit_g:
                        if new_g_name_str in groups_data:
                            st.error("Tên nhóm mới đã trùng với nhóm khác!")
                        else:
                            groups_data[new_g_name_str] = groups_data.pop(sel_edit_g)
                            sel_edit_g = new_g_name_str
                            updated_g = True

                    if new_g_pass_str and new_g_pass_str != groups_data[sel_edit_g].get("passcode"):
                        groups_data[sel_edit_g]["passcode"] = new_g_pass_str
                        updated_g = True

                    if updated_g:
                        save_groups_data(groups_data)
                        trigger_confetti()
                        st.success(f"Đã cập nhật thông tin cho nhóm **{sel_edit_g}** thành công!")
                        st.rerun()
            else:
                st.warning("Hiện chưa có nhóm nào!")

        with adm_g_tab4:
            st.markdown("##### 🗑️ **Giải Tán / Xóa Nhóm Hoàn Toàn**")
            if groups_data:
                sel_del_g = st.selectbox("Chọn nhóm muốn xóa:", list(groups_data.keys()), key="adm_sel_g_del")
                st.error(f"⚠️ Cảnh báo: Thao tác này sẽ xóa vĩnh viễn nhóm **{sel_del_g}** khỏi hệ thống!")
                
                if st.button("🔥 XÁC NHẬN XÓA NHÓM NÀY", type="primary", use_container_width=True, key="btn_adm_del_group"):
                    del groups_data[sel_del_g]
                    save_groups_data(groups_data)
                    st.success(f"Đã xóa nhóm **{sel_del_g}** thành công!")
                    st.rerun()
            else:
                st.warning("Hiện chưa có nhóm nào để xóa!")

    with tab_adm_mailbox:
        st.subheader("📬 Hộp Thư Admin & Duyệt Lời Mời / Yêu Cầu Gia Nhập Nhóm")
        
        all_inv_list = load_invites_data()
        pending_invs = [i for i in all_inv_list if i.get("status") == "pending"]

        if pending_invs:
            for inv in pending_invs:
                st.markdown(f"""
                <div class="mail-card">
                    📌 <b>Người gửi:</b> <code>{inv.get('sender')}</code> &nbsp;|&nbsp; 
                    🎯 <b>Gửi đến:</b> <code>{inv.get('recipient')}</code> &nbsp;|&nbsp; 
                    👥 <b>Nhóm yêu cầu:</b> <b>{inv.get('group_name')}</b>
                </div>
                """, unsafe_allow_html=True)

                col_mb1, col_mb2 = st.columns(2)
                with col_mb1:
                    if st.button(f"✅ Duyệt & Thêm Vào Nhóm ({inv['id']})", key=f"btn_adm_acc_{inv['id']}"):
                        target_gname = inv.get("group_name")
                        target_username = inv.get("sender") if inv.get("type") == "join_request" else inv.get("recipient")
                        
                        if target_gname in groups_data:
                            if target_username not in groups_data[target_gname]["members"]:
                                groups_data[target_gname]["members"].append(target_username)
                                save_groups_data(groups_data)
                        
                        inv["status"] = "accepted"
                        save_invites_data(all_inv_list)
                        trigger_confetti()
                        st.success("Đã chấp nhận thành công!")
                        st.rerun()

                with col_mb2:
                    if st.button(f"❌ Từ Chối ({inv['id']})", key=f"btn_adm_rej_{inv['id']}"):
                        inv["status"] = "rejected"
                        save_invites_data(all_inv_list)
                        st.info("Đã từ chối yêu cầu!")
                        st.rerun()
                st.divider()
        else:
            st.info("📬 Hộp thư hiện tại không có yêu cầu hay lời mời nào đang chờ duyệt!")

    with tab_adm_hw:
        st.subheader("📚 Hệ Thống Admin Giao Bài Tập Tự Động Bằng AI")
        st.caption("💡 *Chọn kỹ năng (Nghe, Đọc, Viết, Trắc nghiệm), chủ đề và cấp độ để AI tự sinh bài tập rồi gửi thẳng vào Hộp thư của học sinh.*")

        if users_data:
            col_hw1, col_hw2 = st.columns(2)
            with col_hw1:
                sel_student_target = st.selectbox("🎯 Chọn học sinh nhận bài tập:", ["-- Gửi tất cả học sinh --"] + [u[0] for u in users_data], key="adm_hw_stu")
                sel_skill = st.selectbox("⚙️ Chọn kỹ năng / Dạng bài tập:", ["Trắc nghiệm Ngữ pháp", "Đọc hiểu (Reading)", "Nghe (Listening)", "Viết (Writing)"], key="adm_hw_skill")
            with col_hw2:
                sel_hw_topic = st.selectbox("🎯 Chọn chủ đề bài tập:", english_topics, key="adm_hw_top")
                sel_hw_level = st.selectbox("🎓 Chọn cấp độ phù hợp:", education_levels, key="adm_hw_lvl")

            if st.button("✨ AI Tạo & Gửi Bài Tập Vào Hộp Thư", type="primary", use_container_width=True, key="btn_send_hw_ai"):
                with st.spinner("AI Gemini 3.6 đang biên soạn nội dung bài tập..."):
                    if sel_student_target == "-- Gửi tất cả học sinh --":
                        success_count = 0
                        for u in users_data:
                            ok, msg = admin_send_ai_homework("lephuchieuadmin", u[0], sel_skill, sel_hw_topic, sel_hw_level)
                            if ok: 
                                success_count += 1
                            else:
                                st.error(f"Không thể giao cho tài khoản `{u[0]}`: {msg}")
                                break
                        if success_count > 0:
                            trigger_confetti()
                            st.success(f"🎉 Đã giao bài tập thành công cho tổng số **{success_count}** học sinh trong hệ thống!")
                    else:
                        ok, msg = admin_send_ai_homework("lephuchieuadmin", sel_student_target, sel_skill, sel_hw_topic, sel_hw_level)
                        if ok:
                            trigger_confetti()
                            st.success(f"🎉 Đã gửi bài tập thành công vào hộp thư của học sinh `{sel_student_target}`!")
                        else:
                            st.error(msg)
        else:
            st.warning("⚠️ Hiện chưa có học sinh nào trong hệ thống để giao bài tập!")

    with tab_adm_grading:
        st.subheader("💯 Xem Điểm Bài Tập & Chấm Lại Bài Tự Luận / Trắc Nghiệm")
        st.caption("💡 *Giáo viên có thể xem đề bài, kiểm tra đáp án/bài làm tự luận của học sinh, nhập lại điểm số và ghi lại nhận xét.*")
        
        all_inv_list = load_invites_data()
        submitted_hw = [inv for inv in all_inv_list if inv.get("type") == "homework_task" and inv.get("status") in ["completed", "graded"]]

        if submitted_hw:
            hw_display_list = []
            for inv in submitted_hw:
                status_str = "✅ Đã chấm lại" if inv.get("status") == "graded" else "⚡ Tự động chấm"
                hw_display_list.append({
                    "Mã bài": inv.get("id"),
                    "Học sinh": inv.get("recipient"),
                    "Tên bài tập": inv.get("group_name"),
                    "Kỹ năng": inv.get("skill"),
                    "Trạng thái": status_str,
                    "Điểm số": f"{inv.get('score', 0)} / {inv.get('max_score', 0)} XP"
                })
            
            st.markdown("##### 📊 **Danh Sách Bài Tập Học Sinh Đã Nộp:**")
            st.dataframe(hw_display_list, use_container_width=True)
            st.divider()

            st.markdown("##### ✏️ **Xem Đề Bài, Bài Làm & Chấm Điểm Lại:**")
            selected_hw_id = st.selectbox(
                "🎯 Chọn bài tập của học sinh cần xem/chấm lại:", 
                [inv["id"] for inv in submitted_hw],
                format_func=lambda x: f"Mã {x} - {next(i['recipient'] for i in submitted_hw if i['id']==x)} ({next(i['group_name'] for i in submitted_hw if i['id']==x)})",
                key="sel_hw_to_grade"
            )

            target_inv = next(i for i in submitted_hw if i["id"] == selected_hw_id)
            
            st.info(f"👤 **Học sinh:** `{target_inv.get('recipient')}` | 📝 **Dạng bài:** `{target_inv.get('skill')}` | 📌 **Tên bài:** {target_inv.get('group_name')}")
            
            # --- HIỂN THỊ ĐỀ BÀI DẠNG WEB THÂN THIỆN ---
            st.markdown("### 📖 **Chi Tiết Đề Bài & Đáp Án Chuẩn:**")
            hw_content = target_inv.get("content", [])
            student_submission = target_inv.get("student_submission") or {}

            if isinstance(hw_content, list):
                for q in hw_content:
                    q_id = str(q.get("id"))
                    st_ans = student_submission.get(q.get("id")) or student_submission.get(q_id) or "Chưa làm / Chưa chọn"
                    correct_ans = q.get("answer", "")

                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 18px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #6C5CE7; box-shadow: 0 4px 12px rgba(0,0,0,0.08); color: #2d3436;">
                        <h5 style="color: #2d3436 !important; margin-bottom: 8px; font-weight: 700;"><b>Câu {q.get('id')}:</b> {q.get('question')}</h5>
                        <div style="margin-left: 10px; color: #4a5568; font-weight: 500;">
                            {"<br>".join([f"• {opt}" for opt in q.get('options', [])])}
                        </div>
                        <hr style="margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0; font-size: 1rem; color: #2d3436 !important;">
                            <b style="color: #2d3436;">✍️ Học sinh chọn:</b> 
                            <span style="background-color: #ffeaa7; color: #d63031; padding: 3px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #fdcb6e;">{st_ans}</span> 
                            &nbsp;&nbsp;|&nbsp;&nbsp; 
                            <b style="color: #2d3436;">✅ Đáp án chuẩn:</b> 
                            <span style="background-color: #e6fffa; color: #00b894; padding: 3px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #55efc4;">{correct_ans}</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            elif isinstance(hw_content, dict):
                passage = hw_content.get("passage") or hw_content.get("audio_script") or hw_content.get("prompt")
                if passage:
                    st.markdown(f"**📖 Nội dung bài đọc / kịch bản / Đề bài:**\n> {passage}")
                
                questions = hw_content.get("questions", [])
                if questions:
                    for q in questions:
                        q_id = str(q.get("id"))
                        st_ans = student_submission.get(q.get("id")) or student_submission.get(q_id) or "Chưa làm / Chưa chọn"
                        correct_ans = q.get("answer", "")

                        st.markdown(f"""
                        <div style="background: #ffffff; padding: 18px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #6C5CE7; box-shadow: 0 4px 12px rgba(0,0,0,0.08); color: #2d3436;">
                            <h5 style="color: #2d3436 !important; margin-bottom: 8px; font-weight: 700;"><b>Câu {q.get('id')}:</b> {q.get('question')}</h5>
                            <div style="margin-left: 10px; color: #4a5568; font-weight: 500;">
                                {"<br>".join([f"• {opt}" for opt in q.get('options', [])])}
                            </div>
                            <hr style="margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; font-size: 1rem; color: #2d3436 !important;">
                                <b>✍️ Học sinh chọn:</b> 
                                <span style="background-color: #ffeaa7; color: #d63031; padding: 3px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #fdcb6e;">{st_ans}</span> 
                                &nbsp;&nbsp;|&nbsp;&nbsp; 
                                <b>✅ Đáp án chuẩn:</b> 
                                <span style="background-color: #e6fffa; color: #00b894; padding: 3px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #55efc4;">{correct_ans}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"**✍️ Bài làm tự luận của học sinh:**")
                    st.info(f"{student_submission}")

            st.write("")
            col_re1, col_re2 = st.columns(2)
            with col_re1:
                new_score = st.number_input("💯 Điểm XP mới cấp cho học sinh:", min_value=0, max_value=500, value=int(target_inv.get("score", 0)), key=f"score_inp_{target_inv['id']}")
            with col_re2:
                teacher_remark = st.text_input("💬 Lời nhận xét của Giáo viên:", value=target_inv.get("teacher_feedback", "Bài làm tốt, cần phát huy!"), key=f"fb_inp_{target_inv['id']}")

            if st.button("💾 CẬP NHẬT ĐIỂM & GỬI NHẬN XÉT", type="primary", use_container_width=True, key=f"btn_save_grade_{target_inv['id']}"):
                old_score = int(target_inv.get("score", 0))
                diff = new_score - old_score
                
                # Cập nhật thông tin bài tập
                target_inv["score"] = new_score
                target_inv["teacher_feedback"] = teacher_remark
                target_inv["status"] = "graded"
                save_invites_data(all_inv_list)

                # Điều chỉnh điểm XP của học sinh trong CSV
                target_student = target_inv.get("recipient")
                if diff != 0:
                    act_type = "add" if diff > 0 else "sub"
                    admin_modify_user_xp(target_student, abs(diff), act_type)

                trigger_confetti()
                st.success(f"🎉 Đã cập nhật lại điểm cho học sinh `{target_student}` thành **{new_score} XP**!")
                st.rerun()
        else:
            st.info("📭 Chưa có học sinh nào hoàn thành bài tập được giao!")

    st.stop()

# ==============================================================================
# MÀN HÌNH DÀNH CHO HỌC SINH THƯỜNG
# ==============================================================================
st.markdown("<h1 class='main-title'>🎈 Wordland - Thế Giới Ngôn Ngữ AI 🎈</h1>", unsafe_allow_html=True)
st.write("")

c1, c2 = st.columns(2)
with c1:
    selected_topic = st.selectbox("🎯 Chọn chủ đề bài học:", ["🎲 [Ngẫu nhiên]"] + english_topics)
    if "Ngẫu nhiên" in selected_topic:
        selected_topic = random.choice(english_topics)

with c2:
    selected_tense = st.selectbox("⏳ Chọn thì ngữ pháp:", ["🎲 [Ngẫu nhiên]"] + english_tenses)
    if "Ngẫu nhiên" in selected_tense:
        selected_tense = random.choice(english_tenses)

st.divider()

tab_cards, tab_speaking, tab_grammar_learn, tab_tense_game, tab_grammar_check, tab_reading, tab_dialogue, tab_writing, tab_dict, tab_fav, tab_mock_exam, tab_maze_game, tab_analytics, tab_groups, tab_all_groups_overview, tab_user_mailbox = st.tabs([
    "🃏 Flashcards", "🎙️ Luyện Phát Âm", "📚 Học Ngữ Pháp AI", "⚙️ Đấu Trường Ngữ Pháp", 
    "📝 Sửa Lỗi Ngữ Pháp", "📖 Đọc Hiểu", "🎧 Hội Thoại", "✍️ Thử Thách Viết Văn", 
    "📚 Từ Điển & Dịch", "❤️ Từ Vựng Yêu Thích", "📝 Đề Thi Thử 4 Kỹ Năng", "🎮 Mê Cung Quái Vật", "📊 Thống Kê & Tiến Độ", "👥 Nhóm Học Tập", "👁️ Quản Lý & Xem Các Nhóm", "📬 Hộp Thư Nhận Lời Mời & Bài Tập"
])

# 1. FLASHCARDS
with tab_cards:
    st.subheader(f"📌 Thẻ từ vựng sinh động ({st.session_state.level}) - Chủ đề: {selected_topic}")
    if st.button("✨ Tạo bộ Flashcards mới", key="btn_fc"):
        trigger_confetti()
        with st.spinner(f"AI đang tạo Flashcards..."):
            prompt = f"Tạo 5 từ vựng tiếng Anh chủ đề '{selected_topic}' phù hợp trình độ '{st.session_state.level}'. Trả về JSON: [{{\"icon\": \"🍎\", \"word\": \"Apple\", \"ipa\": \"/ˈæp.əl/\", \"meaning\": \"Quả táo\", \"example\": \"I eat an apple.\"}}]"
            try:
                raw_text = generate_ai_content_cached(prompt)
                cleaned = clean_json_text(raw_text)
                if cleaned:
                    st.session_state.flashcards = json.loads(cleaned)
                else:
                    st.error("⚠️ Phản hồi từ AI rỗng. Vui lòng thử lại!")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if "flashcards" in st.session_state and st.session_state.flashcards:
        cols = st.columns(len(st.session_state.flashcards))
        for idx, card in enumerate(st.session_state.flashcards):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="flip-card">
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <div style="font-size: 3rem;">{card.get('icon', '📌')}</div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: #2D3436;">{card.get('word', '')}</div>
                            <div style="font-size: 1.1rem; color: #0984E3; font-style: italic;">{card.get('ipa', '')}</div>
                        </div>
                        <div class="flip-card-back">
                            <div style="font-size: 1.4rem; font-weight: bold; color: #FFEAA7;">{card.get('meaning', '')}</div>
                            <p style="font-size: 0.9rem;">"{card.get('example', '')}"</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# 2. LUYỆN PHÁT ÂM
with tab_speaking:
    st.subheader("🎙️ Phòng Luyện Phát Âm & Chấm Điểm AI")
    target_word = st.text_input("🎯 Nhập từ/câu luyện phát âm:", "Opportunity", key="sp_target_input")
    if target_word.strip():
        st.audio(text_to_speech(target_word.strip()), format="audio/mp3")
        
    rec_audio = st.audio_input("Ghi âm giọng đọc của bạn:", key="sp_mic_input")
    if rec_audio and st.button("🔍 AI Chấm Điểm", type="primary"):
        with st.spinner("AI đang lắng nghe..."):
            try:
                audio_part = types.Part.from_bytes(data=rec_audio.read(), mime_type="audio/wav")
                prompt_speak = f"Phân tích phát âm từ/câu '{target_word}' cho trình độ {st.session_state.level}. Trả về: Điểm X/10, Đánh giá chi tiết, Lời khuyên."
                res = client.models.generate_content(model=MODEL_NAME, contents=[audio_part, prompt_speak])
                st.success("🎯 Kết quả:")
                st.markdown(res.text)
                add_xp(15)
                trigger_confetti()
            except Exception as e:
                st.error(f"Lỗi: {e}")

# 3. HỌC NGỮ PHÁP AI
with tab_grammar_learn:
    st.subheader(f"📚 Học Lý Thuyết Ngữ Pháp AI: **{selected_tense}**")
    if st.button("📖 AI Soạn Bài Giảng Ngữ Pháp", type="primary", key="btn_learn_grammar"):
        with st.spinner(f"AI Gemini 3.6 đang tổng hợp bài học về {selected_tense}..."):
            prompt_learn = f"Soạn bài giảng về {selected_tense} cho trình độ {st.session_state.level} dạng Markdown."
            try:
                raw_text = generate_ai_content_cached(prompt_learn)
                if raw_text:
                    st.session_state.grammar_lesson = raw_text
                    add_xp(5)
                else:
                    st.error("⚠️ Phản hồi từ AI rỗng. Vui lòng thử lại!")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if "grammar_lesson" in st.session_state:
        st.markdown(f"<div class='grammar-lesson-box'>{st.session_state.grammar_lesson}</div>", unsafe_allow_html=True)

# 4. ĐẤU TRƯỜNG NGỮ PHÁP
with tab_tense_game:
    st.subheader(f"⚙️ Đấu Trường Ngữ Pháp: Thì **{selected_tense}**")
    if st.button("⚡ Bắt Đầu Thử Thách Chia Động Từ", type="primary"):
        with st.spinner("AI đang tạo bài tập..."):
            try:
                raw_text = generate_ai_content_cached(f"Tạo 5 câu trắc nghiệm chia động từ {selected_tense} dạng JSON.")
                cleaned = clean_json_text(raw_text)
                if cleaned:
                    st.session_state.tense_quiz_data = json.loads(cleaned)
                else:
                    st.error("⚠️ Phản hồi từ AI rỗng. Vui lòng thử lại!")
            except Exception as e:
                st.error(f"Lỗi tải câu hỏi từ AI: {e}")
            
    if "tense_quiz_data" in st.session_state and st.session_state.tense_quiz_data:
        t_ans = {}
        for item in st.session_state.tense_quiz_data:
            t_ans[item['id']] = st.radio(f"Câu {item['id']}: {item['question']}", item['options'], key=f"tq_{item['id']}")
        if st.button("🚀 Nộp Bài Ngữ Pháp"):
            score = sum(1 for item in st.session_state.tense_quiz_data if t_ans[item['id']][0] == item['answer'].strip().upper())
            add_xp(score * 10)
            trigger_confetti()
            st.success(f"🎉 Bạn đúng {score}/5 câu! Nhận +{score*10} XP!")

# 5. SỬA LỖI NGỮ PHÁP
with tab_grammar_check:
    st.subheader("📝 Bác Sĩ Ngữ Pháp - Soi & Sửa Lỗi Câu")
    user_text = st.text_area("Nhập văn bản tiếng Anh:", height=120)
    if st.button("🔍 Kiểm Tra Lỗi", type="primary"):
        if user_text.strip():
            try:
                raw_text = generate_ai_content_cached(f"Sửa lỗi ngữ pháp: '{user_text}'")
                st.markdown(raw_text)
            except Exception as e:
                st.error(f"Lỗi: {e}")

# 6. ĐỌC HIỂU (ĐÃ FIX CHỐNG LỖI JSON)
with tab_reading:
    st.subheader(f"📖 Luyện Đọc Hiểu - {selected_topic}")
    if st.button("✨ Tạo Bài Đọc Mới", type="primary", key="btn_create_reading_tab"):
        with st.spinner("AI Gemini đang biên soạn bài đọc hiểu..."):
            prompt_reading = f"""
            Tạo 1 bài đọc hiểu tiếng Anh ngắn khoảng 80 từ về chủ đề '{selected_topic}' cho trình độ '{st.session_state.level}'.
            Trả về dạng JSON có hai trường: "title" (tiêu đề) và "passage" (nội dung đoạn văn).
            """
            try:
                raw_text = generate_ai_content_cached(prompt_reading)
                cleaned = clean_json_text(raw_text)
                
                if cleaned:
                    st.session_state.reading_data = json.loads(cleaned)
                    trigger_confetti()
                    st.rerun()
                else:
                    st.error("⚠️ Hệ thống tạm thời không nhận được dữ liệu từ AI. Bạn hãy bấm nút 'Tạo Bài Đọc Mới' để thử lại!")
            except json.JSONDecodeError:
                st.error("⚠️ Phản hồi chưa chuẩn định dạng. Vui lòng nhấn nút thử lại một lần nữa!")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if "reading_data" in st.session_state and st.session_state.reading_data:
        data = st.session_state.reading_data
        st.markdown(f"""
        <div class="reading-box" style="background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 15px; margin-top: 15px; color: #2d3436;">
            <h3 style="color: #6C5CE7; margin-bottom: 10px;">📖 {data.get('title', 'Bài Đọc Hiểu')}</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #2d3436;">{data.get('passage', '')}</p>
        </div>
        """, unsafe_allow_html=True)
# 7. HỘI THOẠI
with tab_dialogue:
    st.subheader(f"🎧 Hội Thoại AI - {selected_topic}")
    if st.button("💬 Tạo Hội Thoại Mới"):
        try:
            raw_text = generate_ai_content_cached(f"Tạo hội thoại 2 người về {selected_topic} dạng JSON.")
            cleaned = clean_json_text(raw_text)
            if cleaned:
                st.session_state.dialogue_data = json.loads(cleaned)
            else:
                st.error("⚠️ Phản hồi từ AI rỗng!")
        except Exception as e:
            st.error(f"Lỗi: {e}")
    if "dialogue_data" in st.session_state and st.session_state.dialogue_data:
        for line in st.session_state.dialogue_data.get("dialogue", []):
            st.write(f"**{line.get('speaker')}:** {line.get('text')}")

# 8. VIẾT ĐOẠN VĂN
with tab_writing:
    st.subheader("✍️ Thử Thách Viết Đoạn Văn")
    min_words = st.number_input("🎯 Yêu cầu số từ tối thiểu:", 7, 300, 20)
    if st.button("🎲 Bốc Chủ Đề"):
        try:
            raw_text = generate_ai_content_cached(f"Tạo 1 chủ đề viết tiếng Anh dạng JSON.")
            cleaned = clean_json_text(raw_text)
            if cleaned:
                st.session_state.write_topic_data = json.loads(cleaned)
            else:
                st.error("⚠️ Phản hồi rỗng!")
        except Exception as e:
            st.error(f"Lỗi: {e}")
    if "write_topic_data" in st.session_state and st.session_state.write_topic_data:
        wt = st.session_state.write_topic_data
        st.info(f"📌 **Chủ đề:** {wt.get('topic_en')} ({wt.get('topic_vi')})")

# 9. TỪ ĐIỂN
with tab_dict:
    st.subheader("📚 Từ Điển & Dịch Thuật AI")
    dict_input = st.text_area("Nhập từ hoặc đoạn văn cần tra:")
    if st.button("🔍 Tra Cứu") and dict_input.strip():
        try:
            raw_text = generate_ai_content_cached(f"Tra từ/Dịch: '{dict_input}'")
            st.markdown(raw_text)
        except Exception as e:
            st.error(f"Lỗi: {e}")

# 10. TỪ VỰNG YÊU THÍCH
with tab_fav:
    st.subheader("❤️ Từ Vựng Đã Lưu")
    for fav in st.session_state.favorites:
        st.write(f"📌 **{fav['word']}**: {fav['meaning']}")

# 11. ĐỀ THI THỬ 4 KỸ NĂNG
with tab_mock_exam:
    st.subheader(f"📝 Đề Thi Thử AI 4 Kỹ Năng - Trình độ: **{st.session_state.level}**")
    st.caption("💡 *Đề thi thử tổng hợp gồm 4 phần (Nghe, Nói, Đọc, Viết) được AI biên soạn riêng theo cấp độ của bạn.*")
    
    if st.button("🚀 Khởi Tạo Đề Thi Thử 4 Kỹ Năng Mới", type="primary", key="btn_gen_mock_exam"):
        with st.spinner("AI Gemini đang biên soạn bộ đề thi 4 kỹ năng..."):
            prompt_mock = f"""
            Tạo 1 đề thi thử Tiếng Anh tổng hợp 4 kỹ năng cho trình độ '{st.session_state.level}'.
            Trả về duy nhất JSON chuẩn theo cấu trúc:
            {{
                "listening": {{\"script\": \"Small conversation script...\", \"question\": \"What is the main idea?\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], \"answer\": \"A\"}},
                "reading": {{\"passage\": \"Short passage...\", \"question\": \"According to passage...\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], \"answer\": \"B\"}},
                "speaking": {{\"topic\": \"Describe your favorite hobby and why you like it.\"}},
                "writing": {{\"prompt\": \"Write a paragraph (60-80 words) about your hometown.\"}}
            }}
            """
            try:
                raw_text = generate_ai_content_cached(prompt_mock)
                cleaned = clean_json_text(raw_text)
                if cleaned:
                    st.session_state.mock_exam_data = json.loads(cleaned)
                else:
                    st.error("⚠️ API rỗng!")
            except Exception as e:
                st.error(f"Lỗi khởi tạo đề thi từ AI: {e}")

    if "mock_exam_data" in st.session_state and st.session_state.mock_exam_data:
        exam = st.session_state.mock_exam_data
        
        # Listening
        st.markdown("#### 🎧 **Phần 1: Kỹ Năng Nghe (Listening)**")
        l_script = exam.get("listening", {}).get("script", "")
        if l_script:
            st.audio(text_to_speech(l_script), format="audio/mp3")
            with st.expander("👁️ Xem kịch bản bài nghe (Audio Script)"):
                st.write(l_script)
        l_q = exam.get("listening", {})
        ans_listening = st.radio(f"**Câu hỏi:** {l_q.get('question')}", l_q.get('options', []), key="mock_ans_lis")
        
        st.divider()
        
        # Reading
        st.markdown("#### 📖 **Phần 2: Kỹ Năng Đọc Hiểu (Reading)**")
        r_q = exam.get("reading", {})
        st.info(f"**Bài đọc:** {r_q.get('passage')}")
        ans_reading = st.radio(f"**Câu hỏi:** {r_q.get('question')}", r_q.get('options', []), key="mock_ans_read")
        
        st.divider()

        # Speaking
        st.markdown("#### 🎙️ **Phần 3: Kỹ Năng Nói (Speaking)**")
        s_q = exam.get("speaking", {})
        st.warning(f"🎯 **Đề bài nói:** {s_q.get('topic')}")
        mock_rec_audio = st.audio_input("Ghi âm bài nói của bạn:", key="mock_speak_mic")

        st.divider()

        # Writing
        st.markdown("#### ✍️ **Phần 4: Kỹ Năng Viết (Writing)**")
        w_q = exam.get("writing", {})
        st.success(f"📌 **Đề bài viết:** {w_q.get('prompt')}")
        mock_write_ans = st.text_area("Nhập bài làm đoạn văn của bạn tại đây:", height=100, key="mock_write_inp")

        st.write("")
        if st.button("🏆 NỘP BÀI THI THỬ & CHẤM ĐIỂM", type="primary", use_container_width=True, key="btn_sub_mock_exam"):
            score = 0
            if ans_listening and ans_listening[0] == l_q.get("answer", "").strip().upper():
                score += 25
            if ans_reading and ans_reading[0] == r_q.get("answer", "").strip().upper():
                score += 25
            if mock_rec_audio:
                score += 25
            if mock_write_ans.strip():
                score += 25
                
            add_xp(score)
            trigger_confetti()
            st.balloons()
            st.success(f"🎉 Bạn đã hoàn thành bài thi thử 4 kỹ năng! Điểm đạt được: **{score}/100 điểm** (+{score} XP)!")

# 12. TRÒ CHƠI MÊ CUNG QUÁI VẬT
with tab_maze_game:
    st.subheader("🎮 Trò Chơi: Mê Cung Quái Vật Nâng Cấp")
    st.caption("💡 *Giải đáp các câu hỏi tiếng Anh của Quái vật để nhận chìa khóa vượt qua 3 tầng mê cung!*")

    if "maze_level" not in st.session_state:
        st.session_state.maze_level = 1

    if st.button("🔄 Chơi Lại Từ Tầng 1", key="btn_reset_maze"):
        st.session_state.maze_level = 1
        if "maze_quiz" in st.session_state:
            del st.session_state.maze_quiz
        st.rerun()

    st.markdown(f"### 🏰 **Vị Trí Hiện Tại: Tầng {st.session_state.maze_level} / 3**")
    
    if st.session_state.maze_level > 3:
        trigger_confetti()
        st.balloons()
        st.success("🏆 CHÚC MỪNG BẠN ĐÃ THẮNG TRÒ CHƠI & THOÁT KHỎI MÊ CUNG QUÁI VẬT!")
        if st.button("🎮 Chơi Ải Mới"):
            st.session_state.maze_level = 1
            st.rerun()
    else:
        if "maze_quiz" not in st.session_state:
            with st.spinner("Quái vật đang chuẩn bị câu hỏi thử thách..."):
                prompt_maze = f"Tạo 1 câu hỏi trắc nghiệm tiếng Anh dạng đố vui để vượt ải mê cung cho trình độ '{st.session_state.level}'. Trả về JSON: {{\"monster\": \"👹 Quái Vật Lửa\", \"question\": \"...\", \"options\": [\"A...\", \"B...\", \"C...\", \"D...\"], \"answer\": \"A\"}}"
                try:
                    raw_text = generate_ai_content_cached(prompt_maze)
                    cleaned = clean_json_text(raw_text)
                    if cleaned:
                        st.session_state.maze_quiz = json.loads(cleaned)
                    else:
                        st.error("⚠️ API rỗng!")
                except Exception as e:
                    st.error(f"Lỗi trò chơi: {e}")

        if "maze_quiz" in st.session_state and st.session_state.maze_quiz:
            mq = st.session_state.maze_quiz
            st.markdown(f"""
            <div class="reading-box" style="border-left-color: #d63031;">
                <h4>{mq.get('monster', '👹 Quái Vật Mê Cung')} đang ngáng đường!</h4>
                <p style="font-size: 1.1rem; font-weight: bold;">"{mq.get('question')}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_maze_ans = st.radio("Chọn câu trả lời để tấn công quái vật:", mq.get("options", []), key=f"maze_ans_{st.session_state.maze_level}")
            
            if st.button("⚔️ TẤN CÔNG QUÁI VẬT", type="primary", key="btn_attack_monster"):
                if user_maze_ans and user_maze_ans[0] == mq.get("answer", "").strip().upper():
                    trigger_confetti()
                    st.success("💥 Chính xác! Quái vật đã bị hạ gục! Bạn nhận được Chìa khóa lên tầng tiếp theo (+20 XP)!")
                    add_xp(20)
                    st.session_state.maze_level += 1
                    del st.session_state.maze_quiz
                    st.rerun()
                else:
                    st.error("❌ Rất tiếc! Câu trả lời chưa chính xác. Quái vật đã phản công, hãy thử lại!")

# 13. PHÂN TÍCH TIẾN ĐỘ
with tab_analytics:
    st.subheader(f"📊 Phân Tích Tiến Độ Học Tập - **{st.session_state.fullname}**")
    
    all_invites_data = load_invites_data()
    user_invites = [i for i in all_invites_data if i.get("recipient") == st.session_state.user]
    completed_invites = [i for i in user_invites if i.get("status") in ["completed", "graded"]]
    
    col_an1, col_an2, col_an3, col_an4 = st.columns(4)
    with col_an1:
        st.metric("⭐ Tổng Điểm XP", f"{st.session_state.xp} XP")
    with col_an2:
        st.metric("📚 Bài Tập Được Giao", f"{len(user_invites)} bài")
    with col_an3:
        st.metric("✅ Bài Tập Đã Nộp", f"{len(completed_invites)} bài")
    with col_an4:
        rate = round((len(completed_invites) / len(user_invites) * 100), 1) if user_invites else 0.0
        st.metric("🎯 Tỷ Lệ Hoàn Thành", f"{rate}%")

    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("##### 📈 **Phân Phối Điểm XP Theo Kỹ Năng (Ước tính):**")
        skill_stats = {
            "Trắc nghiệm": sum(i.get("score", 0) for i in completed_invites if "Trắc nghiệm" in i.get("skill", "")),
            "Đọc hiểu": sum(i.get("score", 0) for i in completed_invites if "Đọc" in i.get("skill", "")),
            "Nghe": sum(i.get("score", 0) for i in completed_invites if "Nghe" in i.get("skill", "")),
            "Viết": sum(i.get("score", 0) for i in completed_invites if "Viết" in i.get("skill", ""))
        }
        st.bar_chart(skill_stats)

    with col_chart2:
        st.markdown("##### 🏆 **Đánh Giá Tiến Độ Học Tập:**")
        if st.session_state.xp >= 500:
            st.success("🌟 Trình độ: **Học Viên Xuất Sắc (Master)**! Tiếp tục duy trì phong độ nhé!")
        elif st.session_state.xp >= 200:
            st.info("👍 Trình độ: **Học Viên Chăm Chỉ (Advanced)**! Hãy chăm chỉ làm thêm bài tập AI!")
        else:
            st.warning("🌱 Trình độ: **Tân Binh Học Tập (Beginner)**! Hãy tích cực luyện tập để tăng điểm XP!")
            
        st.write("📋 **Lịch sử làm bài mới nhất:**")
        if completed_invites:
            recent_data = [{"Bài tập": i.get("group_name"), "Kỹ năng": i.get("skill"), "Điểm": f"{i.get('score')} XP"} for i in completed_invites[-5:]]
            st.table(recent_data)
        else:
            st.caption("Chưa có dữ liệu làm bài tập nào.")

# 14. TẠO NHÓM & MỜI BẠN BÈ VÀO NHÓM
with tab_groups:
    st.subheader("👥 Nhóm Học Tập & Bảng Xếp Hạng Đội Nhóm")
    
    groups = load_groups_data()
    user_curr = st.session_state.user

    my_group_name = None
    for g_name, g_info in groups.items():
        if user_curr == g_info.get("leader") or user_curr in g_info.get("members", []):
            my_group_name = g_name
            break

    sub_g1, sub_g2 = st.tabs(["🚀 Khung Nhóm Của Tôi", "➕ Xin Vào Nhóm / Tạo Nhóm Mới"])

    with sub_g1:
        if my_group_name:
            g_data = groups[my_group_name]
            is_leader = (user_curr == g_data.get("leader"))
            
            st.markdown(f"""
            <div class="group-card">
                <h3>👥 Nhóm: <b>{my_group_name}</b> {"👑 (Bạn là Trưởng nhóm)" if is_leader else ""}</h3>
                <p>🔑 <b>Mã bảo mật nhóm:</b> <code>{g_data.get('passcode')}</code> | 👑 <b>Trưởng nhóm:</b> <code>{g_data.get('leader')}</code></p>
            </div>
            """, unsafe_allow_html=True)

            all_csv_users = get_all_users_from_csv()
            user_xp_dict = {u[0]: (int(u[2]) if len(u)>2 and u[2].isdigit() else 0, u[3] if len(u)>3 else u[0]) for u in all_csv_users}

            members_list = g_data.get("members", [])
            group_members_info = []
            total_group_xp = 0

            for m_user in members_list:
                m_xp, m_name = user_xp_dict.get(m_user, (0, m_user))
                total_group_xp += m_xp
                group_members_info.append({
                    "Tài khoản": m_user,
                    "Họ và Tên": m_name,
                    "Vai trò": "👑 Trưởng Nhóm" if m_user == g_data.get("leader") else "👤 Thành Viên",
                    "Điểm XP": m_xp
                })

            group_members_info = sorted(group_members_info, key=lambda x: x["Điểm XP"], reverse=True)

            col_gm1, col_gm2 = st.columns(2)
            with col_gm1:
                st.metric("👥 Tổng Thành Viên", f"{len(members_list)} bạn")
            with col_gm2:
                st.metric("⭐ Tổng Điểm XP Nhóm", f"{total_group_xp} XP")

            st.markdown("##### 🏆 **Bảng Xếp Hạng Nội Bộ Nhóm:**")
            st.dataframe(group_members_info, use_container_width=True)

            st.divider()
            st.markdown("##### 📩 **Gửi Lời Mời Bạn Bè Gia Nhập Nhóm:**")
            
            non_member_students = [u[0] for u in all_csv_users if u[0] not in members_list and u[0] != "lephuchieuadmin"]
            
            if non_member_students:
                col_inv1, col_inv2 = st.columns([2, 1])
                with col_inv1:
                    target_friend = st.selectbox("Chọn bạn học sinh muốn mời vào nhóm:", non_member_students, key="sel_friend_invite")
                with col_inv2:
                    st.write("")
                    st.write("")
                    if st.button("📩 Gửi Lời Mời", type="primary", use_container_width=True, key="btn_send_friend_inv"):
                        ok, msg = send_group_invite(sender=user_curr, recipient=target_friend, group_name=my_group_name, invite_type="invite_user")
                        if ok:
                            trigger_confetti()
                            st.success(f"🎉 Đã gửi lời mời tham gia nhóm **{my_group_name}** tới Hộp thư của `{target_friend}`!")
                        else:
                            st.warning(msg)
            else:
                st.info("Tất cả học sinh trong hệ thống đều đã gia nhập nhóm của bạn!")

            if is_leader:
                st.divider()
                st.markdown("##### 🛠️ **Khung Quản Lý Nhóm (Quyền Trưởng Nhóm):**")
                removable_members = [m for m in members_list if m != user_curr]
                
                if removable_members:
                    user_to_remove = st.selectbox("Chọn thành viên muốn mời ra khỏi nhóm:", removable_members, key="sel_rem_mem")
                    if st.button("❌ Mời Ra Khỏi Nhóm", type="primary", key="btn_rem_mem"):
                        g_data["members"].remove(user_to_remove)
                        groups[my_group_name] = g_data
                        save_groups_data(groups)
                        st.success(f"Đã xóa tài khoản `{user_to_remove}` khỏi nhóm!")
                        st.rerun()
            
            st.write("")
            if st.button("🚪 Rời Khỏi Nhóm Này", key="btn_leave_group"):
                if is_leader:
                    del groups[my_group_name]
                    st.warning("Trưởng nhóm rời đi! Nhóm đã được giải tán.")
                else:
                    groups[my_group_name]["members"].remove(user_curr)
                    st.info("Bạn đã rời khỏi nhóm.")
                save_groups_data(groups)
                st.rerun()

        else:
            st.info("👋 Bạn chưa tham gia nhóm nào. Hãy chuyển sang Tab **'➕ Xin Vào Nhóm / Tạo Nhóm Mới'** để gửi yêu cầu!")

    with sub_g2:
        if my_group_name:
            st.warning(f"⚠️ Bạn đang tham gia nhóm **{my_group_name}**. Hãy rời nhóm hiện tại nếu muốn gia nhập hoặc tạo nhóm mới!")
        else:
            c_g1, c_g2 = st.columns(2)
            
            with c_g1:
                st.markdown("##### ✨ **Tạo Nhóm Học Tập Mới**")
                create_g_name = st.text_input("Tên nhóm mới *:", key="c_g_name")
                create_g_pass = st.text_input("Mã mật khẩu nhóm *:", type="password", key="c_g_pass")
                
                if st.button("🚀 Khởi Tạo Nhóm", type="primary", key="btn_create_g"):
                    if not create_g_name.strip() or not create_g_pass.strip():
                        st.warning("Vui lòng nhập đầy đủ Tên nhóm và Mã mật khẩu!")
                    elif create_g_name.strip() in groups:
                        st.error("Tên nhóm này đã tồn tại! Vui lòng chọn tên khác.")
                    else:
                        groups[create_g_name.strip()] = {
                            "leader": user_curr,
                            "passcode": create_g_pass.strip(),
                            "members": [user_curr]
                        }
                        save_groups_data(groups)
                        trigger_confetti()
                        st.success(f"Tạo nhóm **{create_g_name.strip()}** thành công!")
                        st.rerun()

            with c_g2:
                st.markdown("##### 🔑 **Gửi Yêu Cầu Tham Gia Nhóm (Chờ Duyệt)**")
                join_g_name = st.selectbox("Chọn nhóm muốn gia nhập:", ["-- Chọn nhóm --"] + list(groups.keys()), key="j_g_name")
                join_g_pass = st.text_input("Nhập mã mật khẩu của nhóm *:", type="password", key="j_g_pass")
                
                if st.button("📩 Gửi Yêu Cầu Vào Nhóm", key="btn_join_g"):
                    if join_g_name == "-- Chọn nhóm --" or not join_g_pass.strip():
                        st.warning("Vui lòng chọn nhóm và nhập mã mật khẩu!")
                    elif join_g_name in groups:
                        target_g = groups[join_g_name]
                        if join_g_pass.strip() == target_g.get("passcode"):
                            group_leader = target_g.get("leader")
                            ok, msg = send_group_invite(sender=user_curr, recipient=group_leader, group_name=join_g_name, invite_type="join_request")
                            if ok:
                                trigger_confetti()
                                st.success(f"🎉 Mã chính xác! Yêu cầu tham gia nhóm **{join_g_name}** đã được gửi tới Trưởng nhóm `{group_leader}`!")
                            else:
                                st.warning(msg)
                        else:
                            st.error("Mã mật khẩu nhóm không chính xác!")

# 15. QUẢN LÝ & XEM TẤT CẢ CÁC NHÓM TRÊN HỆ THỐNG
with tab_all_groups_overview:
    st.subheader("👁️ Quản Lý & Tra Cứu Thông Tin Toàn Bộ Các Nhóm")
    st.caption("💡 *Xem danh sách toàn bộ các nhóm học tập hiện có, kiểm tra nhóm đó bao gồm những ai và thuộc thể loại nhóm nào.*")

    all_groups = load_groups_data()
    all_csv_users = get_all_users_from_csv()
    user_fullname_dict = {u[0]: u[3] if len(u)>3 else u[0] for u in all_csv_users}
    user_fullname_dict["lephuchieuadmin"] = "Lê Phúc Hiếu (Quản Trị Viên)"

    if all_groups:
        for g_name, g_info in all_groups.items():
            leader_username = g_info.get("leader", "Không rõ")
            leader_fullname = user_fullname_dict.get(leader_username, leader_username)
            members = g_info.get("members", [])
            
            member_names = [f"{m} ({user_fullname_dict.get(m, m)})" for m in members]
            
            st.markdown(f"""
            <div class="group-card">
                <h3>📁 Tên Nhóm: <b>{g_name}</b></h3>
                <p>👑 <b>Trưởng nhóm / Người quản lý:</b> <code>{leader_fullname}</code> (Tài khoản: <code>{leader_username}</code>)</p>
                <p>👥 <b>Tổng số thành viên:</b> <b>{len(members)}</b> thành viên</p>
                <p>📋 <b>Danh sách thành viên chi tiết:</b> {', '.join(member_names) if member_names else 'Chưa có thành viên'}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 Hiện tại hệ thống chưa có nhóm học tập nào được tạo!")

# 16. HỘP THƯ HỌC SINH (BAO GỒM CẢ XEM ĐIỂM VÀ LÀM BÀI TẬP AI GIAO)
with tab_user_mailbox:
    st.subheader(f"📬 Hộp Thư Cá Nhân & Kết Quả Bài Tập - **{st.session_state.fullname}**")
    st.caption("💡 *Nơi tiếp nhận bài tập từ Giáo viên, làm bài và coi lại điểm số các bài tập đã hoàn thành.*")
    
    all_invites = load_invites_data()
    
    # 1. DANH SÁCH BÀI TẬP CHỜ LÀM & LỜI MỜI
    my_invites = [inv for inv in all_invites if inv.get("recipient") == st.session_state.user and inv.get("status") == "pending"]

    if my_invites:
        st.markdown("### 📥 **Bài Tập & Thông Báo Đang Chờ Xử Lý:**")
        for inv in my_invites:
            if inv.get("type") == "homework_task":
                st.markdown(f"""
                <div class="mail-card">
                    📚 <b>Bài tập mới từ Giáo viên / Admin:</b> <b>{inv.get('group_name')}</b><br>
                    🎓 <b>Cấp độ:</b> <code>{inv.get('level')}</code>
                </div>
                """, unsafe_allow_html=True)
                
                hw_content = inv.get("content")
                
                if inv.get("skill") == "Trắc nghiệm Ngữ pháp" and isinstance(hw_content, list):
                    hw_ans = {}
                    for q in hw_content:
                        hw_ans[q['id']] = st.radio(f"Câu {q['id']}: {q['question']}", q['options'], key=f"hw_q_{inv['id']}_{q['id']}")
                    
                    if st.button(f"🚀 Nộp Bài Tập Này ({inv['id']})", key=f"btn_sub_hw_{inv['id']}"):
                        score = sum(1 for q in hw_content if hw_ans[q['id']][0] == q['answer'].strip().upper())
                        max_s = len(hw_content) * 10
                        earned_xp = score * 10
                        add_xp(earned_xp)
                        inv["status"] = "completed"
                        inv["score"] = earned_xp
                        inv["max_score"] = max_s
                        inv["student_submission"] = hw_ans
                        save_invites_data(all_invites)
                        trigger_confetti()
                        st.success(f"🎉 Nộp bài thành công! Bạn đạt {score}/{len(hw_content)} câu và nhận +{earned_xp} XP!")
                        st.rerun()

                elif inv.get("skill") == "Đọc hiểu (Reading)" and isinstance(hw_content, dict):
                    st.markdown(f"**📖 Bài đọc:** {hw_content.get('passage')}")
                    hw_r_ans = {}
                    for q in hw_content.get("questions", []):
                        hw_r_ans[q['id']] = st.radio(f"Câu {q['id']}: {q['question']}", q['options'], key=f"hw_rq_{inv['id']}_{q['id']}")
                    
                    if st.button(f"🚀 Nộp Bài Đọc Hiểu ({inv['id']})", key=f"btn_sub_r_hw_{inv['id']}"):
                        score = sum(1 for q in hw_content.get("questions", []) if hw_r_ans[q['id']][0] == q['answer'].strip().upper())
                        max_s = len(hw_content.get("questions", [])) * 15
                        earned_xp = score * 15
                        add_xp(earned_xp)
                        inv["status"] = "completed"
                        inv["score"] = earned_xp
                        inv["max_score"] = max_s
                        inv["student_submission"] = hw_r_ans
                        save_invites_data(all_invites)
                        trigger_confetti()
                        st.success(f"🎉 Nộp bài đọc thành công! Nhận +{earned_xp} XP!")
                        st.rerun()

                elif inv.get("skill") == "Nghe (Listening)" and isinstance(hw_content, dict):
                    audio_text = hw_content.get('audio_script', '')
                    st.audio(text_to_speech(audio_text), format="audio/mp3")
                    st.info(f"🎧 (Hoặc đọc kịch bản hội thoại để làm bài): {audio_text}")
                    
                    hw_l_ans = {}
                    for q in hw_content.get("questions", []):
                        hw_l_ans[q['id']] = st.radio(f"Câu {q['id']}: {q['question']}", q['options'], key=f"hw_lq_{inv['id']}_{q['id']}")
                    
                    if st.button(f"🚀 Nộp Bài Nghe ({inv['id']})", key=f"btn_sub_l_hw_{inv['id']}"):
                        score = sum(1 for q in hw_content.get("questions", []) if hw_l_ans[q['id']][0] == q['answer'].strip().upper())
                        max_s = len(hw_content.get("questions", [])) * 15
                        earned_xp = score * 15
                        add_xp(earned_xp)
                        inv["status"] = "completed"
                        inv["score"] = earned_xp
                        inv["max_score"] = max_s
                        inv["student_submission"] = hw_l_ans
                        save_invites_data(all_invites)
                        trigger_confetti()
                        st.success(f"🎉 Nộp bài nghe thành công! Nhận +{earned_xp} XP!")
                        st.rerun()

                else: 
                    st.info(f"📌 **Yêu cầu đề bài:** {hw_content.get('prompt', 'Viết đoạn văn theo yêu cầu.')}")
                    student_hw_input = st.text_area("Nhập bài làm của bạn:", key=f"hw_text_{inv['id']}")
                    if st.button(f"🚀 Gửi Bài Làm Tự Luận ({inv['id']})", key=f"btn_sub_w_hw_{inv['id']}") and student_hw_input.strip():
                        add_xp(25)
                        inv["status"] = "completed"
                        inv["score"] = 25
                        inv["max_score"] = 50
                        inv["student_submission"] = student_hw_input.strip()
                        save_invites_data(all_invites)
                        trigger_confetti()
                        st.success("🎉 Đã gửi bài làm cho giáo viên! Nhận +25 XP!")
                        st.rerun()
                st.divider()

            else:
                invite_type_str = "🤝 Yêu cầu xin vào nhóm" if inv.get("type") == "join_request" else "📩 Lời mời bạn vào nhóm"
                st.markdown(f"""
                <div class="mail-card">
                    📌 <b>Loại thông báo:</b> {invite_type_str}<br>
                    📩 <b>Từ tài khoản:</b> <code>{inv.get('sender')}</code><br>
                    👥 <b>Nhóm học tập:</b> <b>{inv.get('group_name')}</b>
                </div>
                """, unsafe_allow_html=True)
                
                c_m1, c_m2 = st.columns(2)
                with c_m1:
                    if st.button(f"✅ Đồng Ý / Duyệt", key=f"btn_acc_usr_inv_{inv['id']}"):
                        target_gname = inv.get("group_name")
                        target_username = inv.get("sender") if inv.get("type") == "join_request" else st.session_state.user
                        
                        groups = load_groups_data()
                        if target_gname in groups:
                            if target_username not in groups[target_gname]["members"]:
                                groups[target_gname]["members"].append(target_username)
                                save_groups_data(groups)
                        
                        inv["status"] = "accepted"
                        save_invites_data(all_invites)
                        trigger_confetti()
                        st.success("Đã đồng ý thành công!")
                        st.rerun()

                with c_m2:
                    if st.button(f"❌ Từ Chối", key=f"btn_rej_usr_inv_{inv['id']}"):
                        inv["status"] = "rejected"
                        save_invites_data(all_invites)
                        st.info("Đã từ chối lời mời!")
                        st.rerun()
                st.divider()

    # 2. XEM ĐIỂM VÀ LỊCH SỬ BÀI TẬP ĐÃ LÀM
    st.markdown("### 🏆 **Lịch Sử Bài Tập Đã Nộp & Điểm Số:**")
    my_history = [inv for inv in all_invites if inv.get("recipient") == st.session_state.user and inv.get("status") in ["completed", "graded"]]

    if my_history:
        history_table = []
        for inv in my_history:
            status_text = "✅ Giáo viên đã chấm lại" if inv.get("status") == "graded" else "⚡ Hệ thống chấm tự động"
            history_table.append({
                "Tên bài tập": inv.get("group_name"),
                "Dạng bài": inv.get("skill"),
                "Điểm XP Đạt Được": f"{inv.get('score', 0)} / {inv.get('max_score', 0)} XP",
                "Trạng thái chấm": status_text,
                "Nhận xét của Giáo viên": inv.get("teacher_feedback", "Chưa có nhận xét")
            })
        st.dataframe(history_table, use_container_width=True)
    else:
        st.info("📭 Bạn chưa có lịch sử bài tập nào đã nộp!")
