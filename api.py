import csv
import random
import io
import json
import re
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

# --- HÀM DỌN DẸP CHUỖI JSON ---
def clean_json_text(text):
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    return text.strip()

# --- CUSTOM CSS NÂNG CẤP GIAO DIỆN & HIỆU ỨNG CHUYỂN TAB MƯỢT MÀ ---
st.markdown("""
<style>
    /* Background Gradient Chuyển Động Mượt */
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

    /* HIỆU ỨNG CHUYỂN TAB MƯỢT MÀ & HIỆN ĐẠI (TABS TRANSITION) */
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
        0% {
            opacity: 0;
            transform: translateY(15px) scale(0.99);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Styles Khác */
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
    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }
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
    .reading-box {
        background: rgba(255, 255, 255, 0.92);
        border-radius: 18px;
        padding: 25px;
        border-left: 6px solid #6C5CE7;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .grammar-lesson-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 18px;
        padding: 25px;
        border-left: 6px solid #00CEC9;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: #2d3436;
    }
    .analytics-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 18px;
        padding: 25px;
        border-left: 6px solid #FF7675;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: #2d3436;
    }
    .maze-container {
        background: white;
        padding: 15px;
        border-radius: 15px;
        display: inline-block;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .maze-row { display: flex; }
    .maze-cell {
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; border: 1px solid #dfe6e9;
    }
    .cell-wall { background-color: #2d3436; }
    .cell-path { background-color: #f5f6fa; }
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
def check_login(user, pwd):
    try:
        with open("list.csv", mode="r", encoding="utf-8") as f:
            users = list(csv.reader(f))
            for row in users:
                if row and row[0].strip() == user and len(row) > 1 and row[1].strip() == pwd:
                    xp = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else 0
                    fullname = row[3].strip() if len(row) > 3 else "Học viên"
                    user_class = row[4].strip() if len(row) > 4 else "Chưa nhập"
                    user_school = row[5].strip() if len(row) > 5 else "Chưa nhập"
                    user_level = row[6].strip() if len(row) > 6 else "Chưa nhập"
                    return True, {
                        "xp": xp, "fullname": fullname,
                        "class": user_class, "school": user_school, "level": user_level
                    }
            return False, {}
    except FileNotFoundError:
        return False, {}

def register_user(user, pwd, fullname, user_class, school, level):
    existing_users = []
    try:
        with open("list.csv", mode="r", encoding="utf-8") as f:
            existing_users = [row[0].strip().lower() for row in csv.reader(f) if row]
    except FileNotFoundError:
        pass

    if user.lower() in existing_users:
        return False, "Tên đăng nhập đã tồn tại!"
    
    with open("list.csv", mode="a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([user, pwd, 0, fullname, user_class, school, level])
    return True, "Đăng ký tài khoản thành công!"

def update_user_info_in_csv(user, fullname, user_class, school, level):
    try:
        rows = []
        with open("list.csv", mode="r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == user.lower():
                pwd = row[1] if len(row) > 1 else ""
                xp = row[2] if len(row) > 2 else 0
                rows[i] = [user, pwd, xp, fullname, user_class, school, level]
                break

        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return True
    except Exception:
        return False

def save_xp_to_csv(user, new_xp):
    try:
        rows = []
        with open("list.csv", mode="r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        
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
            writer = csv.writer(f)
            writer.writerows(rows)
    except Exception:
        pass

def add_xp(points):
    st.session_state.xp += points
    save_xp_to_csv(st.session_state.user, st.session_state.xp)

# --- TỪ VỰNG YÊU THÍCH ---
def save_favorite_word(word, meaning, ipa, example):
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    for item in st.session_state.favorites:
        if item['word'].lower() == word.lower():
            return False
            
    st.session_state.favorites.append({
        "word": word, "meaning": meaning, "ipa": ipa, "example": example
    })
    return True

# Initialize States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
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
st.sidebar.markdown(f"⭐ **Điểm kinh nghiệm (XP):** `{st.session_state.xp}`")
st.sidebar.markdown(f"❤️ **Từ vựng đã lưu:** `{len(st.session_state.favorites)}` từ")

with st.sidebar.expander("✏️ **Thay đổi thông tin cá nhân**"):
    new_fullname = st.text_input("Họ và Tên:", value=st.session_state.fullname, key="edit_fullname")
    new_class = st.text_input("Lớp:", value=st.session_state.user_class, key="edit_class")
    new_school = st.text_input("Trường:", value=st.session_state.school, key="edit_school")
    
    current_level_idx = 0
    if st.session_state.level in education_levels:
        current_level_idx = education_levels.index(st.session_state.level)
        
    new_level = st.selectbox("Cấp độ học / Ôn thi:", education_levels, index=current_level_idx, key="edit_level")
    
    if st.button("💾 Lưu thay đổi", use_container_width=True, key="btn_save_user_info"):
        if not new_fullname.strip() or not new_class.strip() or not new_school.strip():
            st.warning("Vui lòng không để trống thông tin!")
        else:
            if update_user_info_in_csv(st.session_state.user, new_fullname.strip(), new_class.strip(), new_school.strip(), new_level):
                st.session_state.fullname = new_fullname.strip()
                st.session_state.user_class = new_class.strip()
                st.session_state.school = new_school.strip()
                st.session_state.level = new_level
                st.success("Cập nhật thành công!")
                st.rerun()

st.sidebar.write("")
if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

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

# TABS TÍNH NĂNG
tab_cards, tab_speaking, tab_grammar_learn, tab_tense_game, tab_grammar_check, tab_reading, tab_dialogue, tab_writing, tab_dict, tab_fav, tab_mock_exam, tab_maze_game, tab_analytics = st.tabs([
    "🃏 Flashcards", "🎙️ Luyện Phát Âm", "📚 Học Ngữ Pháp AI", "⚙️ Đấu Trường Ngữ Pháp", 
    "📝 Sửa Lỗi Ngữ Pháp", "📖 Đọc Hiểu", "🎧 Hội Thoại", "✍️ Thử Thách Viết Văn", 
    "📚 Từ Điển & Dịch", "❤️ Từ Vựng Yêu Thích", "📝 Đề Thi Thử 4 Kỹ Năng", "🎮 Mê Cung Quái Vật", "📊 Thống Kê & Tiến Độ"
])

# 1. FLASHCARDS
with tab_cards:
    st.subheader(f"📌 Thẻ từ vựng sinh động ({st.session_state.level}) - Chủ đề: {selected_topic}")
    if st.button("✨ Tạo bộ Flashcards mới", key="btn_fc"):
        trigger_confetti()
        with st.spinner(f"AI đang tạo Flashcards..."):
            prompt = f"Tạo 5 từ vựng tiếng Anh chủ đề '{selected_topic}' phù hợp trình độ '{st.session_state.level}'. Trả về JSON: [{{\"icon\": \"🍎\", \"word\": \"Apple\", \"ipa\": \"/ˈæp.əl/\", \"meaning\": \"Quả táo\", \"example\": \"I eat an apple.\"}}]"
            try:
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                st.session_state.flashcards = json.loads(clean_json_text(res.text))
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if "flashcards" in st.session_state:
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
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.audio(text_to_speech(card.get('word', '')), format="audio/mp3")
                with col_btn2:
                    if st.button(f"❤️ Lưu", key=f"fav_fc_{idx}"):
                        save_favorite_word(card.get('word'), card.get('meaning'), card.get('ipa'), card.get('example'))

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
    st.caption("💡 *Ôn tập toàn bộ công thức, dấu hiệu nhận biết và câu ví dụ sinh động trước khi làm bài tập thử thách nhé!*")
    
    if st.button("📖 AI Soạn Bài Giảng Ngữ Pháp", type="primary", key="btn_learn_grammar"):
        with st.spinner(f"AI Gemini 3.6 đang tổng hợp bài học về {selected_tense}..."):
            prompt_learn = f"""
            Hãy soạn 1 bài giảng lý thuyết ngữ pháp chi tiết và dễ hiểu nhất về thì '{selected_tense}' phù hợp trình độ học sinh '{st.session_state.level}'.
            
            Bài giảng trình bày theo cấu trúc Markdown gồm:
            1. 🎯 **Khái niệm & Cách dùng (Usage)**: [Trình bày 2-3 cách dùng phổ biến nhất]
            2. 📐 **Công thức chuẩn (Structure)**: 
               - Khẳng định (+)
               - Phủ định (-)
               - Nghi vấn (?)
            3. 🔑 **Dấu hiệu nhận biết (Signal Words)**: [Các từ nhận biết quen thuộc]
            4. 💡 **Ví dụ minh họa & Dịch nghĩa**: [Đưa ra 3 ví dụ tiếng Anh kèm dịch tiếng Việt]
            5. ⚠️ **Lỗi thường gặp cần tránh**: [1-2 lỗi hay sai của học sinh]
            """
            try:
                res_learn = client.models.generate_content(model=MODEL_NAME, contents=prompt_learn)
                st.session_state.grammar_lesson = res_learn.text
                add_xp(5)
                st.toast("Bạn nhận +5 XP vì đã chăm chỉ đọc bài giảng!", icon="📖")
            except Exception as e:
                st.error(f"Lỗi tải bài giảng: {e}")

    if "grammar_lesson" in st.session_state:
        st.markdown(f"""
        <div class="grammar-lesson-box">
            {st.session_state.grammar_lesson}
        </div>
        """, unsafe_allow_html=True)

# 4. ĐẤU TRƯỜNG NGỮ PHÁP
with tab_tense_game:
    st.subheader(f"⚙️ Đấu Trường Ngữ Pháp: Thì **{selected_tense}**")
    if st.button("⚡ Bắt Đầu Thử Thách Chia Động Từ", type="primary"):
        with st.spinner("AI đang tạo bài tập..."):
            res = client.models.generate_content(model=MODEL_NAME, contents=f"Tạo 5 câu trắc nghiệm chia động từ {selected_tense} dạng JSON.")
            st.session_state.tense_quiz_data = json.loads(clean_json_text(res.text))
            
    if "tense_quiz_data" in st.session_state:
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
            res = client.models.generate_content(model=MODEL_NAME, contents=f"Sửa lỗi ngữ pháp cho học sinh trình độ {st.session_state.level}: '{user_text}'")
            st.info("🎯 Kết quả:")
            st.markdown(res.text)

# 6. ĐỌC HIỂU
with tab_reading:
    st.subheader(f"📖 Luyện Đọc Hiểu - {selected_topic}")
    if st.button("✨ Tạo Bài Đọc Mới", type="primary"):
        prompt_reading = f"Tạo bài đọc 100-150 từ về '{selected_topic}' trình độ {st.session_state.level} kèm 5 câu hỏi trắc nghiệm. Trả về JSON."
        try:
            res = client.models.generate_content(model=MODEL_NAME, contents=prompt_reading)
            st.session_state.reading_data = json.loads(clean_json_text(res.text))
        except Exception as e:
            st.error(f"Lỗi: {e}")

    if "reading_data" in st.session_state:
        data = st.session_state.reading_data
        st.markdown(f"### 📖 {data.get('title')}\n{data.get('passage')}")
        user_ans = {}
        for q in data.get('questions', []):
            user_ans[q['id']] = st.radio(f"Câu {q['id']}: {q['question']}", q['options'], key=f"rq_{q['id']}")
        if st.button("🚀 Nộp Bài Đọc"):
            score = sum(1 for q in data.get('questions', []) if user_ans[q['id']][0] == q['answer'].strip().upper())
            add_xp(score * 5)
            trigger_confetti()
            st.success(f"Điểm số: {score}/5! Nhận +{score*5} XP!")

# 7. HỘI THOẠI
with tab_dialogue:
    st.subheader(f"🎧 Hội Thoại AI - {selected_topic}")
    if st.button("💬 Tạo Hội Thoại Mới"):
        res = client.models.generate_content(model=MODEL_NAME, contents=f"Tạo hội thoại 2 người về {selected_topic} dạng JSON.")
        st.session_state.dialogue_data = json.loads(clean_json_text(res.text))
    if "dialogue_data" in st.session_state:
        for line in st.session_state.dialogue_data.get("dialogue", []):
            st.write(f"**{line.get('speaker')}:** {line.get('text')}")

# 8. VIẾT ĐOẠN VĂN
with tab_writing:
    st.subheader("✍️ Thử Thách Viết Đoạn Văn")
    min_words = st.number_input("🎯 Yêu cầu số từ tối thiểu:", 7, 300, 20)
    if st.button("🎲 Bốc Chủ Đề"):
        res = client.models.generate_content(model=MODEL_NAME, contents=f"Tạo 1 chủ đề viết tiếng Anh dạng JSON.")
        st.session_state.write_topic_data = json.loads(clean_json_text(res.text))
    if "write_topic_data" in st.session_state:
        wt = st.session_state.write_topic_data
        st.info(f"📌 **Chủ đề:** {wt.get('topic_en')} ({wt.get('topic_vi')})")
        student_paragraph = st.text_area("Đoạn văn của bạn:", height=150)
        word_count = len(re.findall(r'\b\w+\b', student_paragraph))
        st.caption(f"Số từ hiện tại: {word_count}/{min_words}")
        if st.button("🚀 Chấm Bài") and word_count >= min_words:
            res = client.models.generate_content(model=MODEL_NAME, contents=f"Chấm bài viết: '{student_paragraph}'")
            st.markdown(res.text)
            add_xp(20)
            trigger_confetti()

# 9. TỪ ĐIỂN
with tab_dict:
    st.subheader("📚 Từ Điển & Dịch Thuật AI")
    dict_input = st.text_area("Nhập từ hoặc đoạn văn cần tra:")
    if st.button("🔍 Tra Cứu") and dict_input.strip():
        res = client.models.generate_content(model=MODEL_NAME, contents=f"Tra từ/Dịch: '{dict_input}'")
        st.markdown(res.text)

# 10. TỪ VỰNG YÊU THÍCH
with tab_fav:
    st.subheader("❤️ Từ Vựng Đã Lưu")
    for idx, fav in enumerate(st.session_state.favorites):
        st.write(f"📌 **{fav['word']}**: {fav['meaning']}")

# 11. ĐỀ THI THỬ AI 4 KỸ NĂNG (NGHE - NÓI - ĐỌC - VIẾT)
with tab_mock_exam:
    st.subheader(f"📝 Đề Thi Thử AI 4 Kỹ Năng - Trình độ: **{st.session_state.level}**")
    st.caption("💡 *Bài thi kiểm tra toàn diện 4 kỹ năng: 🎧 Nghe, 📖 Đọc, ✍️ Viết và 🎙️ Nói (Ghi âm).*")
    
    if st.button("✨ AI Tạo Đề Thi Thử 4 Kỹ Năng Mới", type="primary", key="btn_gen_full_exam"):
        with st.spinner(f"AI Gemini 3.6 đang thiết kế bộ đề thi 4 kỹ năng..."):
            prompt_full_exam = f"""
            Tạo 1 đề thi Tiếng Anh 4 kỹ năng chuẩn cho học sinh trình độ '{st.session_state.level}'.
            Trả về định dạng JSON thuần túy như sau:
            {{
                "listening": {{
                    "passage": "Nội dung bài hội thoại tiếng Anh ngắn 50-80 từ...",
                    "questions": [
                        {{"id": 1, "question": "Câu hỏi nghe hiểu 1?", "options": ["A..", "B..", "C..", "D.."], "answer": "A"}},
                        {{"id": 2, "question": "Câu hỏi nghe hiểu 2?", "options": ["A..", "B..", "C..", "D.."], "answer": "B"}}
                    ]
                }},
                "reading": {{
                    "passage": "Nội dung bài đọc ngắn 80-100 từ...",
                    "questions": [
                        {{"id": 3, "question": "Câu hỏi đọc hiểu 1?", "options": ["A..", "B..", "C..", "D.."], "answer": "C"}},
                        {{"id": 4, "question": "Câu hỏi đọc hiểu 2?", "options": ["A..", "B..", "C..", "D.."], "answer": "D"}}
                    ]
                }},
                "writing": {{
                    "prompt": "Yêu cầu bài viết tiếng Anh (viết 15-30 từ)..."
                }},
                "speaking": {{
                    "prompt": "Yêu cầu ghi âm trả lời 1 câu hỏi phát âm tiếng Anh..."
                }}
            }}
            """
            try:
                res_exam = client.models.generate_content(model=MODEL_NAME, contents=prompt_full_exam)
                st.session_state.full_exam_data = json.loads(clean_json_text(res_exam.text))
            except Exception as e:
                st.error(f"Lỗi khởi tạo bài thi: {e}")

    if "full_exam_data" in st.session_state:
        exam = st.session_state.full_exam_data
        
        # PHẦN 1: NGHE
        st.markdown("### 🎧 **Phần 1: Kỹ Năng Nghe (Listening)**")
        lis_passage = exam["listening"].get("passage", "")
        st.write("🔊 **Nhấn để nghe đoạn ghi âm:**")
        st.audio(text_to_speech(lis_passage), format="audio/mp3")
        
        lis_answers = {}
        for q in exam["listening"].get("questions", []):
            st.write(f"**Câu {q['id']}: {q['question']}**")
            lis_answers[q['id']] = st.radio(f"Chọn đáp án câu {q['id']}:", q['options'], key=f"fe_l_{q['id']}")
        
        st.divider()

        # PHẦN 2: ĐỌC
        st.markdown("### 📖 **Phần 2: Kỹ Năng Đọc (Reading)**")
        st.markdown(f"<div class='reading-box'>{exam['reading'].get('passage', '')}</div>", unsafe_allow_html=True)
        
        read_answers = {}
        for q in exam["reading"].get("questions", []):
            st.write(f"**Câu {q['id']}: {q['question']}**")
            read_answers[q['id']] = st.radio(f"Chọn đáp án câu {q['id']}:", q['options'], key=f"fe_r_{q['id']}")
            
        st.divider()

        # PHẦN 3: VIẾT
        st.markdown("### ✍️ **Phần 3: Kỹ Năng Viết (Writing)**")
        st.info(f"📌 **Đề bài viết:** {exam['writing'].get('prompt', '')}")
        user_write_text = st.text_area("Nhập bài viết của bạn tại đây:", height=100, key="fe_write_input")
        
        st.divider()

        # PHẦN 4: NÓI
        st.markdown("### 🎙️ **Phần 4: Kỹ Năng Nói & Ghi Âm (Speaking)**")
        st.info(f"🎯 **Yêu cầu phát âm / trả lời:** {exam['speaking'].get('prompt', '')}")
        fe_audio = st.audio_input("Ghi âm câu trả lời của bạn tại đây:", key="fe_speak_input")

        st.divider()

        if st.button("🚀 Nộp Bài Thi 4 Kỹ Năng", type="primary", key="btn_submit_full_exam"):
            with st.spinner("AI Gemini 3.6 đang tổng hợp và chấm điểm bài thi 4 kỹ năng..."):
                lis_score = sum(1 for q in exam["listening"]["questions"] if lis_answers[q['id']][0] == q['answer'].strip().upper())
                read_score = sum(1 for q in exam["reading"]["questions"] if read_answers[q['id']][0] == q['answer'].strip().upper())
                mcq_score = lis_score + read_score
                
                st.success(f"📊 **Kết quả Trắc nghiệm (Nghe & Đọc):** Đúng {mcq_score} / 4 câu.")

                if user_write_text.strip():
                    prompt_eval_write = f"Đóng vai giáo viên chấm bài viết tiếng Anh ngắn này cho trình độ {st.session_state.level}: Đề bài: '{exam['writing']['prompt']}', Bài làm: '{user_write_text}'. Đánh giá ngắn gọn ưu/nhược điểm và cho điểm X/10."
                    res_w_eval = client.models.generate_content(model=MODEL_NAME, contents=prompt_eval_write)
                    st.markdown("##### ✍️ **Đánh giá Kỹ năng Viết:**")
                    st.info(res_w_eval.text)
                else:
                    st.warning("⚠️ Bạn chưa hoàn thành phần thi Viết.")

                if fe_audio:
                    try:
                        audio_part = types.Part.from_bytes(data=fe_audio.read(), mime_type="audio/wav")
                        prompt_eval_speak = f"Phân tích âm thanh ghi âm phần thi Nói tiếng Anh theo yêu cầu: '{exam['speaking']['prompt']}'. Cho điểm phát âm X/10 và nhận xét ngắn."
                        res_s_eval = client.models.generate_content(model=MODEL_NAME, contents=[audio_part, prompt_eval_speak])
                        st.markdown("##### 🎙️ **Đánh giá Kỹ năng Nói:**")
                        st.success(res_s_eval.text)
                    except Exception as e:
                        st.error(f"Lỗi phân tích file ghi âm: {e}")
                else:
                    st.warning("⚠️ Bạn chưa thực hiện phần thi Ghi âm (Nói).")

                earned_xp = (mcq_score * 10) + 20
                add_xp(earned_xp)
                trigger_confetti()
                st.toast(f"🎉 Bạn hoàn thành bài thi 4 kỹ năng và nhận +{earned_xp} XP!", icon="🏆")

# 12. TRÒ CHƠI MÊ CUNG QUÁI VẬT NÂNG CẤP (ENHANCED MAZE GAME - CHẾ ĐỘ & VẬT PHẨM)
with tab_maze_game:
    st.subheader("🎮 Trò Chơi: Mê Cung Quái Vật Nâng Cấp (Enhanced Maze Game)")
    st.caption("💡 *Chọn chế độ chơi, tận dụng Vật phẩm Hỗ trợ (Thuốc Bỏ Qua, Khiên) để đánh bại quái vật và chinh phục Đích 🏁!*")

    col_set1, col_set2 = st.columns([1, 1])
    with col_set1:
        maze_difficulty = st.selectbox("🎯 Chọn Cấp Độ Mê Cung:", ["🟢 Dễ (Bản đồ 7x7 - 3 Quái)", "🔴 Khó (Bản đồ 9x9 - 5 Quái)"], key="maze_diff")
    
    # Khởi tạo bản đồ 7x7 hoặc 9x9
    def init_custom_maze(diff_mode):
        if "Khó" in diff_mode:
            return [
                [0, 0, 1, 0, 0, 0, 1, 0, 0],
                [1, 0, 1, 0, 1, 0, 1, 0, 1],
                [0, 0, 2, 0, 1, 2, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 1, 1, 0],
                [0, 2, 0, 1, 2, 1, 0, 2, 0],
                [1, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 2, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1, 0],
                [1, 1, 1, 1, 0, 0, 0, 1, 3]
            ]
        else:
            return [
                [0, 0, 1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1],
                [0, 0, 2, 0, 1, 2, 0],
                [0, 1, 1, 0, 0, 0, 0],
                [0, 2, 0, 1, 1, 1, 0],
                [1, 0, 0, 0, 2, 0, 0],
                [1, 1, 1, 0, 0, 1, 3]
            ]

    if "maze" not in st.session_state or st.button("🔄 Tạo Mê Cung Mới", key="btn_reset_maze"):
        st.session_state.maze = init_custom_maze(maze_difficulty)
        st.session_state.player_pos = [0, 0]
        st.session_state.active_monster_q = None
        st.session_state.monster_pos = None
        st.session_state.maze_defeated_monsters = 0
        # Khởi tạo kho vật phẩm
        st.session_state.item_skip = 1   # 1 Thuốc bỏ qua
        st.session_state.item_shield = 1 # 1 Khiên bảo vệ

    maze = st.session_state.maze
    px, py = st.session_state.player_pos

    # Hiển thị Kho vật phẩm
    st.markdown(f"🎒 **Kho Vật Phẩm Hỗ Trợ:** 🧪 Thuốc Bỏ Qua: **{st.session_state.item_skip}** | 🛡️ Khiên Bảo Vệ: **{st.session_state.item_shield}**")

    col_m1, col_m2 = st.columns([1.2, 1])

    with col_m1:
        st.markdown("##### 🗺️ **Bản Đồ Mê Cung:**")
        maze_html = "<div class='maze-container'>"
        for r in range(len(maze)):
            maze_html += "<div class='maze-row'>"
            for c in range(len(maze[r])):
                cell_val = maze[r][c]
                icon = ""
                cell_class = "cell-path"
                
                if [r, c] == [px, py]:
                    icon = "🏃"
                elif cell_val == 1:
                    cell_class = "cell-wall"
                    icon = "🧱"
                elif cell_val == 2:
                    icon = "👾"
                elif cell_val == 3:
                    icon = "🏁"
                    
                maze_html += f"<div class='maze-cell {cell_class}'>{icon}</div>"
            maze_html += "</div>"
        maze_html += "</div>"
        st.markdown(maze_html, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("##### 🎮 **Điều Khiển Nhân Vật:**")
        
        move_dir = None
        
        b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
        with b_col2:
            if st.button("⬆️ Lên", use_container_width=True, key="m_up"): move_dir = (-1, 0)
        
        b_c1, b_c2, b_c3 = st.columns([1, 1, 1])
        with b_c1:
            if st.button("⬅️ Trái", use_container_width=True, key="m_left"): move_dir = (0, -1)
        with b_c3:
            if st.button("➡️ Phải", use_container_width=True, key="m_right"): move_dir = (0, 1)
            
        b_cc1, b_cc2, b_cc3 = st.columns([1, 1, 1])
        with b_cc2:
            if st.button("⬇️ Xuống", use_container_width=True, key="m_down"): move_dir = (1, 0)

        if move_dir and st.session_state.active_monster_q is None:
            nx, ny = px + move_dir[0], py + move_dir[1]
            
            if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and maze[nx][ny] != 1:
                if maze[nx][ny] == 2:
                    st.session_state.monster_pos = [nx, ny]
                    with st.spinner("👾 Quái vật cản đường! Đang tải câu hỏi..."):
                        p_q = f"Tạo 1 câu hỏi trắc nghiệm tiếng Anh ngắn cho trình độ '{st.session_state.level}'. Trả về JSON: {{\"question\": \"\", \"options\": [\"A..\", \"B..\", \"C..\", \"D..\"], \"answer\": \"A\"}}"
                        try:
                            res_monster = client.models.generate_content(model=MODEL_NAME, contents=p_q)
                            st.session_state.active_monster_q = json.loads(clean_json_text(res_monster.text))
                        except Exception as e:
                            st.error(f"Lỗi quái vật: {e}")
                
                elif maze[nx][ny] == 3:
                    st.session_state.player_pos = [nx, ny]
                    trigger_confetti()
                    st.balloons()
                    bonus_xp = 100 if "Khó" in maze_difficulty else 50
                    st.success(f"🎉 THÀNH CÔNG! Bạn đã vượt qua Mê cung và tới Đích! Nhận được +{bonus_xp} XP!")
                    add_xp(bonus_xp)
                
                else:
                    st.session_state.player_pos = [nx, ny]
                
                st.rerun()

    with col_m2:
        st.markdown("##### ⚔️ **Trận Đấu Quái Vật & Sử Dụng Vật Phẩm:**")
        if st.session_state.active_monster_q:
            mq = st.session_state.active_monster_q
            st.error("👾 **QUÁI VẬT CẢN ĐƯỜNG! Trả lời đúng để di chuyển tiếp!**")
            st.write(f"**Câu hỏi:** {mq.get('question')}")
            
            mq_ans = st.radio("Chọn đáp án:", mq.get('options', []), key="mq_radio")
            
            col_fight1, col_fight2 = st.columns(2)
            with col_fight1:
                if st.button("⚔️ Tấn Công", type="primary", key="btn_fight_monster"):
                    if mq_ans[0] == mq.get('answer').strip().upper():
                        trigger_confetti()
                        st.success("🎉 CHÍNH XÁC! Quái vật đã bị hạ! (+20 XP)")
                        
                        mx, my = st.session_state.monster_pos
                        st.session_state.maze[mx][my] = 0
                        st.session_state.player_pos = [mx, my]
                        
                        st.session_state.active_monster_q = None
                        st.session_state.monster_pos = None
                        st.session_state.maze_defeated_monsters += 1
                        
                        add_xp(20)
                        st.rerun()
                    else:
                        if st.session_state.item_shield > 0:
                            st.session_state.item_shield -= 1
                            st.warning("🛡️ Khiên Bảo Vệ đã đỡ đòn cho bạn! Hãy chọn lại đáp án khác!")
                        else:
                            st.error("❌ Trả lời sai rồi! Quái vật vẫn chặn đường, hãy thử lại!")

            with col_fight2:
                if st.button("🧪 Dùng Thuốc Bỏ Qua", key="btn_use_skip_item"):
                    if st.session_state.item_skip > 0:
                        st.session_state.item_skip -= 1
                        trigger_confetti()
                        st.success("🧪 Đã tiêu tốn 1 Thuốc Bỏ Qua! Hạ gục quái vật thành công!")
                        
                        mx, my = st.session_state.monster_pos
                        st.session_state.maze[mx][my] = 0
                        st.session_state.player_pos = [mx, my]
                        
                        st.session_state.active_monster_q = None
                        st.session_state.monster_pos = None
                        st.session_state.maze_defeated_monsters += 1
                        add_xp(10)
                        st.rerun()
                    else:
                        st.warning("⚠️ Bạn đã hết Thuốc Bỏ Qua!")
        else:
            st.info("🟢 Đường đi an toàn. Hãy bấm nút di chuyển để tìm Đích 🏁!")
            st.write(f"📊 Quái vật đã hạ gục: **{st.session_state.get('maze_defeated_monsters', 0)}**")

# 13. CÁ NHÂN HÓA & THỦ KÊ TIẾN ĐỘ
with tab_analytics:
    st.subheader(f"📊 Phân Tích Tiến Độ Học Tập - **{st.session_state.fullname}**")
    st.caption("💡 *Hệ thống theo dõi tự động phân tích điểm số, thói quen học tập và đưa ra gợi ý lộ trình thông minh cho bạn!*")
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.metric("⭐ Tổng Điểm XP", f"{st.session_state.xp} XP", delta="+XP mới")
    with col_a2:
        st.metric("❤️ Từ Vựng Đã Lưu", f"{len(st.session_state.favorites)} từ")
    with col_a3:
        st.metric("👾 Quái Vật Hạ Gục", f"{st.session_state.get('maze_defeated_monsters', 0)} con")
    with col_a4:
        xp = st.session_state.xp
        rank = "🌱 Tập sự"
        if xp >= 300: rank = "🏆 Bậc Thầy"
        elif xp >= 150: rank = "💎 Chuyên Gia"
        elif xp >= 50: rank = "⚡ Thành Thạo"
        st.metric("🏅 Cấp Độ Trình Độ", rank)

    st.divider()
    
    col_g1, col_g2 = st.columns([1.2, 1])
    
    with col_g1:
        st.markdown("##### 📈 **Biểu Đồ Tiến Độ Tích Lũy Kinh Nghiệm (XP Analytics):**")
        current_xp = st.session_state.xp
        chart_data = {
            "Ngày học": ["Ngày 1", "Ngày 2", "Ngày 3", "Ngày 4", "Ngày 5", "Ngày 6", "Hôm nay"],
            "Điểm XP": [
                max(0, current_xp - 60), 
                max(0, current_xp - 45), 
                max(0, current_xp - 35), 
                max(0, current_xp - 25), 
                max(0, current_xp - 15), 
                max(0, current_xp - 5), 
                current_xp
            ]
        }
        st.line_chart(chart_data, x="Ngày học", y="Điểm XP")
        
    with col_g2:
        st.markdown("##### 🎯 **Phân Tích & Gợi Ý Lộ Trình Thông Minh Từ AI:**")
        if st.button("🤖 AI Chẩn Đoán Tiến Độ & Lộ Trình", type="primary", key="btn_ai_analytics"):
            with st.spinner("AI Gemini 3.6 đang phân tích thói quen học tập..."):
                prompt_analytics = f"""
                Hãy đóng vai là Cố vấn học tập Tiếng Anh AI cá nhân hóa.
                Thông tin học viên:
                - Họ tên: {st.session_state.fullname}
                - Lớp: {st.session_state.user_class} - Trường: {st.session_state.school}
                - Trình độ/Mục tiêu: {st.session_state.level}
                - Tổng điểm XP hiện tại: {st.session_state.xp} XP
                - Số từ vựng yêu thích đã lưu: {len(st.session_state.favorites)} từ
                - Số quái vật mê cung đã tiêu diệt: {st.session_state.get('maze_defeated_monsters', 0)}

                Hãy phân tích ngắn gọn theo định dạng Markdown:
                1. 📊 **Đánh giá tổng quan hiệu suất học tập**: [Khen ngợi điểm mạnh]
                2. 🔍 **Điểm cần cải thiện & Tự ôn tập**: [Đưa ra 2 kỹ năng nên luyện thêm]
                3. 🚀 **Lộ trình mục tiêu tiếp theo**: [Gợi ý tính năng nên học tiếp theo trong app để tăng XP]
                """
                try:
                    res_an = client.models.generate_content(model=MODEL_NAME, contents=prompt_analytics)
                    st.session_state.ai_analysis_res = res_an.text
                except Exception as e:
                    st.error(f"Lỗi phân tích AI: {e}")

        if "ai_analysis_res" in st.session_state:
            st.markdown(f"""
            <div class="analytics-box">
                {st.session_state.ai_analysis_res}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Bấm vào nút phía trên để nhận đánh giá phân tích tiến độ cá nhân hóa từ AI!")
