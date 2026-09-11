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

# --- CẤU HÌNH CƠ BẢN & MODEL ---
MODEL_NAME = "gemini-3.6-flash"

# Điền API Key trực tiếp vào đây nếu bạn không dùng biến môi trường (Environment Variable)
API_KEY_DEFAULT = "" 

st.set_page_config(
    page_title="Wordland - Chạm tay vào thế giới ngôn ngữ 🚀", 
    page_icon="🎨", 
    layout="wide"
)

# Khởi tạo Gemini Client tự động (Không hiển thị khung nhập trên Sidebar)
if API_KEY_DEFAULT.strip():
    client = genai.Client(api_key=API_KEY_DEFAULT.strip())
else:
    client = genai.Client() # Tự động tìm GOOGLE_API_KEY từ hệ thống

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

# --- CUSTOM CSS NÂNG CẤP GIAO DIỆN & HIỆU ỨNG ---
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

    /* Tiêu Đề Chính Nổi Bật */
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

    /* Hiệu ứng Thẻ Flashcard 3D Hover */
    .flashcard {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border: 2px solid #FF7675;
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .flashcard:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 30px rgba(0,0,0,0.25);
    }
    .word-icon { font-size: 3.5rem; margin-bottom: 10px; }
    .word-title { font-size: 2rem; color: #2D3436; font-weight: 800; }
    .word-ipa { font-size: 1.1rem; color: #0984E3; font-style: italic; }
    .word-meaning { font-size: 1.3rem; color: #6C5CE7; font-weight: bold; margin-top: 8px; }

    /* Thiết Kế Nút Bấm Đẹp Mắt */
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

    /* Khung Bài Đọc & Hộp Thoại Nổi */
    .reading-box {
        background: rgba(255, 255, 255, 0.92);
        border-radius: 18px;
        padding: 25px;
        border-left: 6px solid #6C5CE7;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .chat-bubble-a {
        background-color: #E3F2FD;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0px;
        margin-bottom: 10px;
        border-left: 4px solid #2196F3;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .chat-bubble-b {
        background-color: #F3E5F5;
        padding: 12px 18px;
        border-radius: 18px 18px 0px 18px;
        margin-bottom: 10px;
        border-right: 4px solid #9C27B0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .favorite-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #FF4757;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
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

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- HÀM XỬ LÝ CSV, ĐĂNG NHẬP & XP ---
def check_login(user, pwd):
    try:
        with open("list.csv", mode="r", encoding="utf-8") as f:
            users = list(csv.reader(f))
            for row in users:
                if row and row[0].strip() == user and len(row) > 1 and row[1].strip() == pwd:
                    xp = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else 0
                    return True, xp
            return False, 0
    except FileNotFoundError:
        return False, 0

def register_user(user, pwd):
    existing_users = []
    try:
        with open("list.csv", mode="r", encoding="utf-8") as f:
            existing_users = [row[0].strip().lower() for row in csv.reader(f) if row]
    except FileNotFoundError:
        pass

    if user.lower() in existing_users:
        return False, "Tên đăng nhập đã tồn tại!"
    
    with open("list.csv", mode="a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([user, pwd, 0])
    return True, "Đăng ký tài khoản thành công!"

def save_xp_to_csv(user, new_xp):
    try:
        rows = []
        with open("list.csv", mode="r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == user.lower():
                pwd = row[1] if len(row) > 1 else ""
                rows[i] = [user, pwd, new_xp]
                break

        with open("list.csv", mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    except Exception:
        pass

def add_xp(points):
    st.session_state.xp += points
    save_xp_to_csv(st.session_state.user, st.session_state.xp)

# --- QUẢN LÝ TỪ VỰNG YÊU THÍCH ---
def save_favorite_word(word, meaning, ipa, example):
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    # Kiểm tra từ trùng lặp
    for item in st.session_state.favorites:
        if item['word'].lower() == word.lower():
            return False
            
    st.session_state.favorites.append({
        "word": word,
        "meaning": meaning,
        "ipa": ipa,
        "example": example
    })
    return True

# Initialize States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>🎒 Wordland - Chạm tay vào thế giới ngôn ngữ 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Học Tiếng Anh Thông Minh Cùng AI Gemini</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký mới"])
        with tab1:
            user_input = st.text_input("Tên đăng nhập", key="login_user")
            pwd_input = st.text_input("Mật khẩu", type="password", key="login_pwd")
            if st.button("🚀 Vào học ngay", use_container_width=True):
                success, saved_xp = check_login(user_input.strip(), pwd_input.strip())
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user_input.strip()
                    st.session_state.xp = saved_xp
                    trigger_confetti()
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu!")
        with tab2:
            reg_user = st.text_input("Tạo tên đăng nhập", key="reg_user")
            reg_pwd = st.text_input("Tạo mật khẩu", type="password", key="reg_pwd")
            if st.button("✨ Tạo tài khoản", use_container_width=True):
                if not reg_user or not reg_pwd:
                    st.warning("Vui lòng nhập đầy đủ thông tin!")
                else:
                    ok, msg = register_user(reg_user.strip(), reg_pwd.strip())
                    if ok:
                        st.success(msg)
                        trigger_confetti()
                    else:
                        st.error(msg)
    st.stop()

# --- MÀN HÌNH CHÍNH ---
st.sidebar.markdown(f"### 🌟 Học viên: **{st.session_state.user}**")
st.sidebar.markdown(f"⭐ **Điểm kinh nghiệm (XP):** `{st.session_state.xp}`")
st.sidebar.markdown(f"❤️ **Từ vựng đã lưu:** `{len(st.session_state.favorites)}` từ")

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
tab_cards, tab_speaking, tab_grammar_check, tab_reading, tab_dialogue, tab_tense_game, tab_writing, tab_dict, tab_fav = st.tabs([
    "🃏 Flashcards", "🎙️ Luyện Phát Âm", "📝 Sửa Lỗi Ngữ Pháp", "📖 Đọc Hiểu", 
    "🎧 Hội Thoại", "⚙️ Ngữ Pháp", "✍️ Thử Thách Viết Văn", "📚 Từ Điển & Dịch", "❤️ Từ Vựng Yêu Thích"
])

# 1. FLASHCARDS
with tab_cards:
    st.subheader(f"📌 Thẻ từ vựng sinh động: {selected_topic}")
    if st.button("✨ Tạo bộ Flashcards mới", key="btn_fc"):
        trigger_confetti()
        with st.spinner("AI đang tạo Flashcards..."):
            prompt = f"""
            Tạo 5 từ vựng tiếng Anh chủ đề '{selected_topic}' phù hợp học sinh THCS.
            Định dạng trả về duy nhất chuỗi JSON danh sách như sau:
            [
              {{"icon": "🍎", "word": "Apple", "ipa": "/ˈæp.əl/", "meaning": "Quả táo", "example": "I eat an apple every day."}}
            ]
            Chỉ trả về định dạng JSON thuần túy trong cặp ngoặc vuông.
            """
            try:
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                cleaned_text = clean_json_text(res.text)
                st.session_state.flashcards = json.loads(cleaned_text)
            except Exception as e:
                st.error(f"Lỗi tải dữ liệu: {e}")

    if "flashcards" in st.session_state:
        cols = st.columns(len(st.session_state.flashcards))
        for idx, card in enumerate(st.session_state.flashcards):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="flashcard">
                    <div class="word-icon">{card.get('icon', '📌')}</div>
                    <div class="word-title">{card.get('word', '')}</div>
                    <div class="word-ipa">{card.get('ipa', '')}</div>
                    <div class="word-meaning">{card.get('meaning', '')}</div>
                    <p style="font-size:0.85rem; color:#636E72; margin-top:8px;"><i>"{card.get('example', '')}"</i></p>
                </div>
                """, unsafe_allow_html=True)
                st.audio(text_to_speech(card.get('word', '')), format="audio/mp3")
                
                if st.button(f"❤️ Lưu từ", key=f"fav_fc_{idx}"):
                    if save_favorite_word(card.get('word'), card.get('meaning'), card.get('ipa'), card.get('example')):
                        st.toast(f"Đã lưu '{card.get('word')}' vào danh sách yêu thích!", icon="❤️")
                    else:
                        st.toast(f"Từ '{card.get('word')}' đã có trong danh sách!", icon="⚠️")

# 2. PHÁT ÂM
with tab_speaking:
    st.subheader("🎙️ Phòng Luyện Phát Âm & Kiểm Tra AI")
    target_word = st.text_input("Nhập từ/câu tiếng Anh bạn muốn luyện phát âm:", "Opportunity")
    if target_word:
        st.write("🔊 **Nghe AI phát âm mẫu:**")
        st.audio(text_to_speech(target_word), format="audio/mp3")
    
    audio_input = st.audio_input("Ghi âm giọng đọc của bạn tại đây:")
    if audio_input is not None and st.button("🔍 AI Chấm điểm phát âm", type="primary"):
        with st.spinner("AI đang lắng nghe và phân tích..."):
            try:
                audio_bytes = audio_input.read()
                audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
                prompt_speak = f"Phân tích phát âm câu/từ: '{target_word}'. Trả lời: Điểm (X/10), Đánh giá chi tiết, Lời khuyên bằng tiếng Việt."
                
                response = client.models.generate_content(model=MODEL_NAME, contents=[audio_part, prompt_speak])
                st.success("🎯 Kết quả phân tích:")
                st.markdown(response.text)
                trigger_confetti()
            except Exception as e:
                st.error(f"Lỗi xử lý âm thanh: {e}")

# 3. SỬA LỖI NGỮ PHÁP
with tab_grammar_check:
    st.subheader("📝 Bác Sĩ Ngữ Pháp - Kiểm Tra & Sửa Lỗi Câu")
    user_text = st.text_area("Nhập đoạn văn/câu tiếng Anh của bạn:", height=120, placeholder="Ví dụ: Yesterday I go to school...")
    if st.button("🔍 Kiểm Tra Lỗi Ngữ Pháp", type="primary"):
        if not user_text.strip():
            st.warning("Vui lòng nhập văn bản tiếng Anh cần kiểm tra!")
        else:
            with st.spinner("AI đang soi lỗi ngữ pháp..."):
                prompt_grammar = f"Giáo viên kiểm tra đoạn văn: '{user_text}'. Trả về: 1. Đoạn sửa chuẩn, 2. Giải thích lỗi sai, 3. Đánh giá chung."
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt_grammar)
                st.info("🎯 Kết quả kiểm tra từ AI:")
                st.markdown(res.text)

# 4. ĐỌC HIỂU
with tab_reading:
    st.subheader(f"📖 Luyện Đọc Hiểu - Chủ đề: {selected_topic}")
    if st.button("✨ Tạo Bài Đọc & 5 Câu Hỏi Mới", type="primary"):
        with st.spinner("AI đang viết bài đọc..."):
            prompt_reading = f"""
            Tạo 1 bài đọc 100-150 từ về '{selected_topic}' kèm 5 câu hỏi trắc nghiệm.
            Trả về JSON: {{"title": "", "passage": "", "questions": [{{"id": 1, "question": "", "options": ["A..","B..","C..","D.."], "answer": "A", "explain": ""}}]}}
            """
            try:
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt_reading)
                st.session_state.reading_data = json.loads(clean_json_text(res.text))
            except Exception as e:
                st.error(f"Không thể tạo bài đọc: {e}")

    if "reading_data" in st.session_state:
        data = st.session_state.reading_data
        st.markdown(f"<div class='reading-box'><h3>📖 {data.get('title')}</h3><p>{data.get('passage')}</p></div>", unsafe_allow_html=True)
        st.audio(text_to_speech(data.get('passage', '')), format="audio/mp3")
        st.divider()
        
        user_ans = {}
        for q in data.get('questions', []):
            st.write(f"**Câu {q['id']}: {q['question']}**")
            user_ans[q['id']] = st.radio(f"Chọn đáp án câu {q['id']}:", q['options'], key=f"read_q_{q['id']}")
            
        if st.button("🚀 Nộp Bài Đọc Hiểu", type="primary"):
            score = sum(1 for q in data.get('questions', []) if user_ans[q['id']][0] == q['answer'].strip().upper())
            add_xp(score * 5)
            trigger_confetti()
            st.info(f"🏆 Tổng điểm: {score}/5! Nhận được +{score*5} XP!")

# 5. HỘI THOẠI & CHAT
with tab_dialogue:
    st.subheader(f"🎧 Hội Thoại AI - Chủ đề: {selected_topic}")
    if st.button("💬 Tạo Cuộc Hội Thoại Mới", type="primary"):
        with st.spinner("AI đang soạn hội thoại..."):
            prompt_dialogue = f"""
            Tạo hội thoại ngắn 2 người về chủ đề '{selected_topic}' kèm 3 câu hỏi trắc nghiệm.
            Trả về JSON: {{"topic": "{selected_topic}", "dialogue": [{{"speaker": "Alex", "text": "Hi"}}], "questions": [{{"id": 1, "question": "", "options": ["A..","B.."], "answer": "A"}}]}}
            """
            try:
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt_dialogue)
                st.session_state.dialogue_data = json.loads(clean_json_text(res.text))
            except Exception as e:
                st.error(f"Lỗi khởi tạo: {e}")

    if "dialogue_data" in st.session_state:
        d_data = st.session_state.dialogue_data
        for line in d_data.get("dialogue", []):
            speaker, text = line.get("speaker", "Person"), line.get("text", "")
            bubble_class = "chat-bubble-a" if speaker == d_data["dialogue"][0]["speaker"] else "chat-bubble-b"
            st.markdown(f"<div class='{bubble_class}'><b>{speaker}:</b> {text}</div>", unsafe_allow_html=True)

# 6. ĐẤU TRƯỜNG NGỮ PHÁP
with tab_tense_game:
    st.subheader(f"⚙️ Thử Thách Ngữ Pháp: Thì **{selected_tense}**")
    if st.button("⚡ Bắt Đầu Thử Thách Ngữ Pháp", type="primary"):
        with st.spinner("AI đang tạo câu hỏi..."):
            p_tense_quiz = f"""
            Tạo 5 câu trắc nghiệm chia động từ về thì '{selected_tense}'.
            Trả về JSON danh sách: [{{"id": 1, "question": "", "options": ["A..","B..","C..","D.."], "answer": "A", "explain": ""}}]
            """
            try:
                res_t = client.models.generate_content(model=MODEL_NAME, contents=p_tense_quiz)
                st.session_state.tense_quiz_data = json.loads(clean_json_text(res_t.text))
            except Exception as e:
                st.error(f"Lỗi tạo bài tập: {e}")

    if "tense_quiz_data" in st.session_state:
        t_data = st.session_state.tense_quiz_data
        t_ans = {}
        for item in t_data:
            st.write(f"**Câu {item['id']}: {item['question']}**")
            t_ans[item['id']] = st.radio(f"Chọn đáp án:", item['options'], key=f"t_q_{item['id']}")
            
        if st.button("🚀 Nộp Bài Ngữ Pháp", type="primary"):
            t_score = sum(1 for item in t_data if t_ans[item['id']][0] == item['answer'].strip().upper())
            add_xp(t_score * 10)
            trigger_confetti()
            st.success(f"🎉 Bạn đúng {t_score}/5 câu! Nhận +{t_score*10} XP!")

# 7. THỬ THÁCH VIẾT ĐOẠN VĂN
with tab_writing:
    st.subheader("✍️ Thử Thách Viết Đoạn Văn Cùng AI")
    st.write("AI sẽ ngẫu nhiên chọn một chủ đề, bạn hãy thực hành viết một đoạn văn tiếng Anh về chủ đề đó!")

    col_w1, col_w2 = st.columns([1, 1])
    with col_w1:
        min_words = st.number_input("🎯 Nhập số từ tối thiểu yêu cầu:", min_value=7, max_value=200, value=20, step=1)
    
    if st.button("🎲 AI Bốc Chủ Đề Ngẫu Nhiên", type="primary", key="btn_gen_write_topic"):
        with st.spinner("AI đang chọn chủ đề độc đáo..."):
            prompt_topic = "Hãy đề xuất 1 chủ đề viết đoạn văn ngắn tiếng Anh độc đáo, phù hợp học sinh. Trả về dạng JSON: {\"topic_en\": \"Topic Name\", \"topic_vi\": \"Tên chủ đề\", \"hint\": \"Gợi ý 2-3 ý nên viết\"}"
            try:
                res_topic = client.models.generate_content(model=MODEL_NAME, contents=prompt_topic)
                st.session_state.write_topic_data = json.loads(clean_json_text(res_topic.text))
            except Exception as e:
                st.error(f"Không thể tạo chủ đề: {e}")

    if "write_topic_data" in st.session_state:
        wt = st.session_state.write_topic_data
        st.info(f"📌 **Chủ đề bài viết:** {wt.get('topic_en')} ({wt.get('topic_vi')})\n\n💡 **Gợi ý:** {wt.get('hint')}")

        student_paragraph = st.text_area("Viết đoạn văn của bạn tại đây (bằng tiếng Anh):", height=180, placeholder="Start typing your paragraph here...")
        
        word_count = len(re.findall(r'\b\w+\b', student_paragraph))
        
        if word_count < min_words:
            st.caption(f"🔴 Số từ hiện tại: **{word_count}** / {min_words} từ tối thiểu (Cần viết thêm {min_words - word_count} từ nữa).")
        else:
            st.caption(f"🟢 Số từ hiện tại: **{word_count}** / {min_words} từ tối thiểu (Đã đạt yêu cầu độ dài!).")

        if st.button("🚀 AI Chấm Điểm & Phân Tích Bài Viết", type="primary", key="btn_grade_writing"):
            if word_count < min_words:
                st.error(f"Đoạn văn của bạn chưa đủ độ dài! Bạn cần viết ít nhất {min_words} từ (Hiện tại: {word_count} từ).")
            else:
                with st.spinner("AI đang đọc và chấm bài viết của bạn..."):
                    prompt_grade = f"""
                    Hãy đóng vai là giáo viên chấm bài viết tiếng Anh.
                    Chủ đề: '{wt.get('topic_en')}'
                    Yêu cầu độ dài: Ít nhất {min_words} từ.
                    Bài viết học sinh ({word_count} từ): "{student_paragraph}"

                    Hãy đánh giá chi tiết theo dạng Markdown:
                    - 🏆 **Điểm số**: [X/10]
                    - 📏 **Đánh giá độ dài**: Đạt yêu cầu ({word_count} từ).
                    - ✨ **Ưu điểm**: [Những câu/từ dùng hay]
                    - 🛠️ **Sửa lỗi & Gợi ý nâng cấp**: [Chỉ ra các lỗi ngữ pháp/dùng từ và cách sửa hay hơn]
                    - 📝 **Phiên bản bài viết hoàn thiện mẫu**: [Viết lại bài học sinh một cách mượt mà nhất]
                    """
                    try:
                        res_grade = client.models.generate_content(model=MODEL_NAME, contents=prompt_grade)
                        st.success("🎯 Kết quả chấm bài từ AI:")
                        st.markdown(res_grade.text)
                        
                        earned_xp = min(50, word_count // 2)
                        add_xp(earned_xp)
                        trigger_confetti()
                        st.toast(f"Bạn nhận được +{earned_xp} XP cho bài viết!", icon="🎉")
                    except Exception as e:
                        st.error(f"Lỗi khi chấm bài: {e}")

# 8. TỪ ĐIỂN & DỊCH VĂN BẢN
with tab_dict:
    st.subheader("📚 Từ Điển Thông Minh & Dịch Thuật AI")
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        dict_input = st.text_area("Nhập từ vựng hoặc đoạn văn cần tra/dịch:", height=100, placeholder="Ví dụ: Resilience hoặc 'Practice makes perfect'")
    with col_d2:
        trans_mode = st.radio("Chế độ:", ["Tự động", "Anh ➔ Việt", "Việt ➔ Anh"])

    if st.button("🔍 Tra Cứu / Dịch Ngay", type="primary", key="btn_dict_search"):
        if not dict_input.strip():
            st.warning("Vui lòng nhập văn bản cần tra!")
        else:
            with st.spinner("AI đang tra cứu từ điển..."):
                prompt_dict = f"""
                Từ điển & Dịch thuật AI. Xử lý: "{dict_input}", Chế độ: {trans_mode}.
                Nếu là từ đơn: Trả về Từ gốc, IPA, Từ loại, Nghĩa Tiếng Việt, 2 Ví dụ kèm dịch, Từ đồng nghĩa/trái nghĩa.
                Nếu là đoạn văn: Trả về Bài dịch mượt mà và 3-5 từ vựng hay trong đoạn.
                """
                try:
                    res_dict = client.models.generate_content(model=MODEL_NAME, contents=prompt_dict)
                    st.success("🎯 Kết quả:")
                    st.markdown(res_dict.text)
                    
                    if len(dict_input.split()) <= 3:
                        st.write("🔊 **Nghe phát âm:**")
                        st.audio(text_to_speech(dict_input), format="audio/mp3")
                        if st.button("❤️ Lưu từ này vào Yêu thích", key="btn_save_dict"):
                            if save_favorite_word(dict_input, "Đã lưu từ Từ điển", "", ""):
                                st.success(f"Đã lưu '{dict_input}' vào danh sách từ vựng yêu thích!")
                except Exception as e:
                    st.error(f"Lỗi tra cứu: {e}")

# 9. DANH SÁCH TỪ VỰNG YÊU THÍCH
with tab_fav:
    st.subheader("❤️ Danh Sách Từ Vựng Đã Lưu")
    
    if not st.session_state.favorites:
        st.info("Bạn chưa lưu từ vựng nào! Hãy nhấn nút '❤️ Lưu từ' ở các thẻ Flashcards hoặc Từ điển để thêm vào đây.")
    else:
        st.write(f"Tổng cộng: **{len(st.session_state.favorites)}** từ vựng đã lưu.")
        
        if st.button("🗑️ Xóa toàn bộ danh sách"):
            st.session_state.favorites = []
            st.rerun()
            
        st.divider()
        
        for idx, fav in enumerate(st.session_state.favorites):
            col_f1, col_f2 = st.columns([4, 1])
            with col_f1:
                st.markdown(f"""
                <div class="favorite-card">
                    <h3 style="margin:0; color:#2D3436;">📌 {fav['word']} <span style="font-size:1rem; color:#0984E3;">{fav.get('ipa','')}</span></h3>
                    <p style="margin:5px 0; font-weight:bold; color:#6C5CE7;">👉 Nghĩa: {fav['meaning']}</p>
                    <p style="margin:0; color:#636E72; font-size:0.9rem;"><i>Ví dụ: "{fav.get('example','')}"</i></p>
                </div>
                """, unsafe_allow_html=True)
            with col_f2:
                st.audio(text_to_speech(fav['word']), format="audio/mp3")
                if st.button("❌ Xóa", key=f"del_fav_{idx}"):
                    st.session_state.favorites.pop(idx)
                    st.rerun()
