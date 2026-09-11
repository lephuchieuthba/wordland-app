import csv
import random
import io
import json
import re
from gtts import gTTS
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# Khởi tạo Gemini Client
client = genai.Client()
MODEL_NAME = "gemini-3.6-flash"

# Cấu hình trang web Streamlit
st.set_page_config(
    page_title="Wordland - Chạm tay vào thế giới ngôn ngữ 🚀", 
    page_icon="🎨", 
    layout="wide"
)

# --- HÀM TẠO HIỆU ỨNG PHÁO HOA (CANVAS CONFETTI) ---
def trigger_confetti():
    """Nhúng JavaScript kích hoạt pháo hoa nổ tung màn hình"""
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

# --- HÀM DỌN DẸP CHUỖI JSON ĐỂ KHÔNG BỊ LỖI PARSE ---
def clean_json_text(text):
    """Xóa bỏ các ký tự Markdown codeblock nếu Gemini trả về"""
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    return text.strip()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #A8EDEA 0%, #FED6E3 50%, #E0C3FC 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-title {
        color: #FF4757;
        text-align: center;
        font-weight: 900;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #6C5CE7;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 25px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease-in-out !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
    }
    .flashcard {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border: 3px solid #FF7675;
        text-align: center;
        margin-bottom: 20px;
    }
    .word-icon { font-size: 3.5rem; margin-bottom: 10px; }
    .word-title { font-size: 2rem; color: #2D3436; font-weight: bold; }
    .word-ipa { font-size: 1.2rem; color: #0984E3; font-style: italic; }
    .word-meaning { font-size: 1.3rem; color: #6C5CE7; font-weight: bold; margin-top: 5px; }
    .reading-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #6C5CE7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .chat-bubble-a {
        background-color: #E3F2FD;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0px;
        margin-bottom: 8px;
        border-left: 4px solid #2196F3;
    }
    .chat-bubble-b {
        background-color: #F3E5F5;
        padding: 10px 15px;
        border-radius: 15px 15px 0px 15px;
        margin-bottom: 8px;
        border-right: 4px solid #9C27B0;
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

# --- HÀM XỬ LÝ CSV & LƯU ĐIỂM XP ---
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

# State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "xp" not in st.session_state:
    st.session_state.xp = 0

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
if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.markdown("<h1 class='main-title'>🎈 Wordland - Chạm tay vào thế giới ngôn ngữ 🎈</h1>", unsafe_allow_html=True)
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

tab_cards, tab_speaking, tab_grammar_check, tab_reading, tab_dialogue, tab_tense_game = st.tabs([
    "🃏 Flashcards", "🎙️ Luyện Phát Âm", "📝 Sửa Lỗi Ngữ Pháp", "📖 Đọc Hiểu", "🎧 Hội Thoại & Chat", "⚙️ Đấu Trường Ngữ Pháp"
])

# 1. FLASHCARDS (ĐÃ SỬA LỖI TRIỆT ĐỂ)
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
            Chỉ trả về định dạng JSON thuần túy trong cặp ngoặc vuông, không viết thêm chữ dẫn dắt nào khác.
            """
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME, 
                    contents=prompt
                )
                cleaned_text = clean_json_text(res.text)
                cards = json.loads(cleaned_text)
                st.session_state.flashcards = cards
            except Exception as e:
                st.error(f"Lỗi tải dữ liệu, vui lòng bấm nút tạo lại! (Chi tiết: {e})")

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
                    <p style="font-size:0.9rem; color:#636E72; margin-top:10px;"><i>"{card.get('example', '')}"</i></p>
                </div>
                """, unsafe_allow_html=True)
                st.audio(text_to_speech(card.get('word', '')), format="audio/mp3")

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
            audio_bytes = audio_input.read()
            prompt_speak = f"""
            Hãy phân tích file âm thanh phát âm tiếng Anh của học sinh THCS.
            Từ/Câu mục tiêu học sinh cần đọc là: "{target_word}"
            Trả lời theo định dạng:
            - Điểm phát âm: [X/10]
            - Đánh giá: [Đúng chuẩn / Cần cải thiện âm nào]
            - Lời khuyên chi tiết bằng tiếng Việt cho học sinh.
            """
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[{"inline_data": {"mime_type": "audio/wav", "data": audio_bytes}}, prompt_speak]
                )
                st.success("🎯 Kết quả phân tích:")
                st.markdown(response.text)
                trigger_confetti()
            except Exception as e:
                st.error(f"Lỗi xử lý âm thanh, vui lòng ghi âm lại! ({e})")

# 3. SỬA LỖI NGỮ PHÁP
with tab_grammar_check:
    st.subheader("📝 Bác Sĩ Ngữ Pháp - Kiểm Tra & Sửa Lỗi Câu")
    user_text = st.text_area("Nhập đoạn văn/câu tiếng Anh của bạn:", height=120, placeholder="Ví dụ: Yesterday I go to school...")
    if st.button("🔍 Kiểm Tra Lỗi Ngữ Pháp", type="primary"):
        if not user_text.strip():
            st.warning("Vui lòng nhập văn bản tiếng Anh cần kiểm tra!")
        else:
            with st.spinner("AI đang soi lỗi ngữ pháp..."):
                prompt_grammar = f"""
                Hãy đóng vai là một giáo viên tiếng Anh THCS tận tâm.
                Nhiệm vụ: Kiểm tra ngữ pháp, chính tả và cách dùng từ cho đoạn văn sau:
                "{user_text}"
                
                Trả về kết quả theo cấu trúc:
                1. 📝 **Đoạn văn đã được sửa chuẩn**
                2. 🔍 **Chi tiết các lỗi sai & Giải thích**
                3. 💡 **Đánh giá chung**
                """
                res = client.models.generate_content(model=MODEL_NAME, contents=prompt_grammar)
                st.info("🎯 Kết quả kiểm tra từ AI:")
                st.markdown(res.text)

# 4. ĐỌC HIỂU
with tab_reading:
    st.subheader(f"📖 Luyện Đọc Hiểu - Chủ đề: {selected_topic}")
    if st.button("✨ Tạo Bài Đọc & 5 Câu Hỏi Mới", type="primary"):
        with st.spinner("AI đang viết bài đọc..."):
            prompt_reading = f"""
            Tạo 1 bài đọc tiếng Anh khoảng 100-150 từ phù hợp học sinh THCS thuộc chủ đề '{selected_topic}'.
            Kèm theo đúng 5 câu hỏi trắc nghiệm đọc hiểu.
            Trả về duy nhất JSON:
            {{
              "title": "Tên bài đọc",
              "passage": "Nội dung bài đọc...",
              "questions": [
                 {{
                   "id": 1,
                   "question": "Nội dung câu hỏi?",
                   "options": ["A...", "B...", "C...", "D..."],
                   "answer": "A",
                   "explain": "Giải thích..."
                 }}
              ]
            }}
            Chỉ trả về JSON thuần túy không kèm văn bản dẫn dắt.
            """
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME, contents=prompt_reading
                )
                cleaned_text = clean_json_text(res.text)
                st.session_state.reading_data = json.loads(cleaned_text)
            except Exception as e:
                st.error(f"Không thể tạo bài đọc, vui lòng thử lại! ({e})")

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
    st.subheader(f"🎧 Hội Thoại AI & Bài Tập Nghe - Chủ đề: {selected_topic}")
    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        num_q = st.slider("Số lượng câu hỏi bài nghe (Tối đa 7 câu):", min_value=3, max_value=7, value=5)
    
    if st.button("💬 Tạo Cuộc Hội Thoại & Câu Hỏi Mới", type="primary"):
        with st.spinner("AI đang soạn cuộc trò chuyện giữa 2 người..."):
            prompt_dialogue = f"""
            Tạo 1 cuộc hội thoại tiếng Anh ngắn giữa 2 người về chủ đề '{selected_topic}', phù hợp học sinh THCS.
            Sau đó tạo ĐÚNG {num_q} câu hỏi trắc nghiệm kiểm tra khả năng nghe/hiểu nội dung bài hội thoại.
            Trả về định dạng JSON thuần túy không kèm văn bản dẫn dắt:
            {{
              "topic": "{selected_topic}",
              "dialogue": [
                 {{"speaker": "Alex", "text": "Hi Sarah! How was your weekend?"}},
                 {{"speaker": "Sarah", "text": "It was great! I went to the park."}}
              ],
              "questions": [
                 {{
                   "id": 1,
                   "question": "Câu hỏi nghe hiểu?",
                   "options": ["A...", "B...", "C...", "D..."],
                   "answer": "A",
                   "explain": "Giải thích..."
                 }}
              ]
            }}
            """
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME, contents=prompt_dialogue
                )
                cleaned_text = clean_json_text(res.text)
                st.session_state.dialogue_data = json.loads(cleaned_text)
                st.session_state.chat_history = []
            except Exception as e:
                st.error(f"Lỗi khởi tạo hội thoại, vui lòng thử lại! ({e})")

    if "dialogue_data" in st.session_state:
        d_data = st.session_state.dialogue_data
        st.markdown("### 🗣️ Đoạn Hội Thoại:")
        full_dialogue_text = ""
        for line in d_data.get("dialogue", []):
            speaker, text = line.get("speaker", "Person"), line.get("text", "")
            full_dialogue_text += f"{speaker}: {text}\n"
            bubble_class = "chat-bubble-a" if speaker == d_data["dialogue"][0]["speaker"] else "chat-bubble-b"
            st.markdown(f"<div class='{bubble_class}'><b>{speaker}:</b> {text}</div>", unsafe_allow_html=True)
            
        st.write("🔊 **Phát âm toàn bộ cuộc hội thoại:**")
        st.audio(text_to_speech(full_dialogue_text), format="audio/mp3")
        st.divider()
        
        st.markdown(f"### ❓ Bài Tập Nghe Hiểu ({len(d_data.get('questions', []))} Câu Hỏi):")
        d_answers = {}
        for q in d_data.get("questions", []):
            st.write(f"**Câu {q['id']}: {q['question']}**")
            d_answers[q['id']] = st.radio(f"Chọn đáp án câu {q['id']}:", q['options'], key=f"dialogue_q_{q['id']}")
            
        if st.button("🚀 Nộp Bài Nghe Hiểu", type="primary", key="sub_dialogue"):
            d_score = sum(1 for q in d_data.get("questions", []) if d_answers[q['id']][0] == q['answer'].strip().upper())
            add_xp(d_score * 5)
            trigger_confetti()
            st.success(f"🎉 Kết quả: Đúng {d_score}/{len(d_data.get('questions', []))} câu! Bạn nhận +{d_score*5} XP!")

        st.divider()
        st.markdown("### 💬 Trò Chuyện Trực Tiếp Cùng AI (Luyện Phản Xạ)")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])

        user_msg = st.chat_input("Nhập tin nhắn tiếng Anh của bạn...")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            st.chat_message("user").write(user_msg)
            with st.spinner("AI đang trả lời..."):
                prompt_chat = f"Nhập vai nói chuyện ngắn gọn về '{selected_topic}' bằng tiếng Anh phù hợp THCS. Lịch sử: {st.session_state.chat_history}"
                chat_res = client.models.generate_content(model=MODEL_NAME, contents=prompt_chat)
                st.session_state.chat_history.append({"role": "assistant", "content": chat_res.text})
                st.chat_message("assistant").write(chat_res.text)

# 6. ĐẤU TRƯỜNG NGỮ PHÁP
with tab_tense_game:
    st.subheader(f"⚙️ Thử Thách Chuyên Sâu: Thì **{selected_tense}**")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.info(f"👉 Bạn đang chọn thì **{selected_tense}**. Nhấn bên dưới để AI tạo 5 câu hỏi chia động từ!")
    with col_t2:
        if st.button("📖 Xem Cấu Trúc Thì Này", key="btn_quick_rule"):
            with st.spinner("AI đang tìm công thức..."):
                p_rule = f"Cung cấp ngắn gọn công thức Khẳng định, Phủ định, Nghi vấn và Dấu hiệu nhận biết của thì '{selected_tense}' cho học sinh THCS."
                res_rule = client.models.generate_content(model=MODEL_NAME, contents=p_rule)
                st.markdown(res_rule.text)

    if st.button("⚡ Bắt Đầu Thử Thách Ngữ Pháp", type="primary", key="btn_gen_tense_quiz"):
        trigger_confetti()
        with st.spinner(f"AI đang soạn 5 câu bài tập về thì {selected_tense}..."):
            p_tense_quiz = f"""
            Hãy tạo 5 câu hỏi trắc nghiệm chia động từ thuộc thì '{selected_tense}' trình độ THCS.
            Trả về định dạng JSON thuần túy không kèm văn bản dẫn dắt:
            [
              {{
                "id": 1,
                "question": "Nội dung câu hỏi điền vào chỗ trống?",
                "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
                "answer": "A",
                "explain": "Giải thích ngắn vì sao dùng thì này"
              }}
            ]
            """
            try:
                res_t = client.models.generate_content(
                    model=MODEL_NAME, contents=p_tense_quiz
                )
                cleaned_text = clean_json_text(res_t.text)
                st.session_state.tense_quiz_data = json.loads(cleaned_text)
            except Exception as e:
                st.error(f"Không thể tạo bài tập ngữ pháp, vui lòng thử lại! ({e})")

    if "tense_quiz_data" in st.session_state:
        t_data = st.session_state.tense_quiz_data
        st.write("---")
        t_ans = {}
        for item in t_data:
            st.write(f"**Câu {item['id']}: {item['question']}**")
            t_ans[item['id']] = st.radio(f"Chọn đáp án đúng:", item['options'], key=f"t_q_{item['id']}")
            
        if st.button("🚀 Nộp Bài Ngữ Pháp", type="primary", key="sub_tense_quiz"):
            t_score = sum(1 for item in t_data if t_ans[item['id']][0] == item['answer'].strip().upper())
            earned_xp = t_score * 10
            add_xp(earned_xp)
            trigger_confetti()
            
            if t_score >= 4:
                st.success(f"🎉 Xuất sắc! Bạn đúng {t_score}/5 câu về thì {selected_tense}! Nhận được +{earned_xp} XP!")
            else:
                st.warning(f"👍 Bạn đúng {t_score}/5 câu. Cùng xem giải thích bên dưới nhé!")
                
            for item in t_data:
                st.caption(f"💡 *Câu {item['id']} - Đáp án đúng {item['answer']}:* {item.get('explain', '')}")