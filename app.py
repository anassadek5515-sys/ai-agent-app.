import streamlit as st
import os
import sqlite3
from datetime import datetime
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS
from pypdf import PdfReader

# 1. إعدادات الشاشة الأساسية
st.set_page_config(page_title="Anas AI Ultra", page_icon="💎", layout="centered", initial_sidebar_state="expanded")

# 2. إعداد قاعدة البيانات لـ SQLite
def init_db():
    conn = sqlite3.connect("chat_history.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, type TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def save_message_to_db(role, content, msg_type="text"):
    c = db_conn.cursor()
    c.execute("INSERT INTO messages (role, content, type, timestamp) VALUES (?, ?, ?, ?)",
              (role, content, msg_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    db_conn.commit()

def load_messages_from_db():
    c = db_conn.cursor()
    c.execute("SELECT role, content, type FROM messages")
    rows = c.fetchall()
    return [{"role": r[0], "content": r[1], "type": r[2]} for r in rows]

def clear_db():
    c = db_conn.cursor()
    c.execute("DELETE FROM messages")
    db_conn.commit()

# 3. تصميم CSS المتقدم والداكن
st.markdown("""
    <style>
    :root, body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d1117 !important;
        background: #0d1117 !important;
        color-scheme: dark !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-left: 1px solid #30363d !important;
    }
    
    #MainMenu, footer, header { display: none !important; }
    
    p, span, div, h1, h2, h3, h4, label, li {
        color: #c9d1d9 !important;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stChatMessage"] {
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #1f6feb 0%, #1158c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }

    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: transparent !important;
        background: #0d1117 !important; 
        border: none !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] {
        background-color: transparent !important;
        padding-bottom: 20px !important;
    }

    [data-testid="stChatInput"] > div, 
    [data-testid="stChatInput"] > div > div {
        background-color: #131314 !important;
        border-radius: 35px !important;
        border: 1px solid #444746 !important;
        box-shadow: 0px 8px 24px rgba(0,0,0,0.6) !important;
        padding: 2px 10px !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #e3e3e3 !important;
        font-size: 16px !important;
        box-shadow: none !important;
        border: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8b949e !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. لوحة التحكم والإعدادات الجانبية المنظمة
with st.sidebar:
    st.markdown("### 👤 حساب المستخدم")
    st.info("📧 متصل بـ: Anas (Google Account)")
    
    st.markdown("---")
    st.markdown("### ⚙️ إعدادات النظام")
    
    selected_model_name = st.selectbox(
        "نموذج الذكاء الاصطناعي:",
        ("Qwen 2.5 Coder (سريع وممتاز)", "Mistral 7B (دقيق ومتوازن)")
    )
    
    # تم تحديث أسماء النماذج لنماذج متاحة ونشطة حالياً
    model_map = {
        "Qwen 2.5 Coder (سريع وممتاز)": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "Mistral 7B (دقيق ومتوازن)": "mistralai/Mistral-7B-Instruct-v0.3"
    }
    ACTIVE_TEXT_MODEL = model_map[selected_model_name]
    IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

    st.markdown("---")
    if st.button("🗑️ مسح الذاكرة الحالية", use_container_width=True):
        clear_db()
        st.rerun()
        
    st.markdown("<p style='text-align:center; font-size: 12px; color: #8b949e;'>Anas AI Ultra v4.1<br>Secured & 24/7 Live</p>", unsafe_allow_html=True)

# 5. المفاتيح ووظائف المعالجة
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة HF_TOKEN في Secrets.")
    st.stop()

def search_web(query, max_results=3):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- المصدر: {r['title']}\n  الملخص: {r['body']}")
        return "\n".join(results)
    except Exception: return ""

def generate_image(prompt):
    try:
        client = InferenceClient(model=IMAGE_MODEL, token=HF_TOKEN)
        return client.text_to_image(prompt)
    except Exception: return None

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return "".join([page.extract_text() or "" for page in reader.pages])[:4000]
    except Exception: return ""

# 6. الواجهة الرئيسية
st.markdown("<h2 style='text-align: center; color: #ffffff;'>💎 أنس AI Ultra</h2>", unsafe_allow_html=True)

mode = st.radio("الوضع:", ["💬 محادثة وبحث", "🎨 رسم صورة", "📄 تحليل PDF"], horizontal=True, label_visibility="collapsed")

pdf_context = ""
if mode == "📄 تحليل PDF":
    uploaded_file = st.file_uploader("ارفع ملف PDF للتحليل:", type=["pdf"])
    if uploaded_file:
        with st.spinner("📄 جاري قراءة الملف..."):
            pdf_context = extract_pdf_text(uploaded_file)
            st.success("تم قراءة الملف بنجاح!")

SUPER_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي ذكي وودود جداً اسمك 'أنس AI Ultra'.
- إذا كان المستخدم يلقي التحية أو يدردش معك بشكل عادي، أجب عليه بلطف وبطريقة طبيعية جداً.
- أما في الأسئلة العلمية والبحثية والبرمجية، أجب بدقة واحترافية واستخدم التنسيق والنقاط.
- أنت تمتلك الوصول للإنترنت للإجابة على الأسئلة الصعبة."""

messages = load_messages_from_db()

for msg in messages:
    avatar = "👤" if msg["role"] == "user" else "💎"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"], caption="الصورة المولدة")
        else:
            st.markdown(msg["content"])

if messages:
    chat_text_export = "\n".join([f"{m['role']}: {m['content']}" for m in messages if m.get('type') != 'image'])
    st.download_button("📥 تحميل سجل المحادثة (TXT)", chat_text_export, file_name="anas_ai_chat.txt", mime="text/plain", use_container_width=True)

placeholder_text = "اسألني، ابحث في الإنترنت، أو أطلب كود..." if mode == "💬 محادثة وبحث" else "اكتب وصف الصورة..."

if user_prompt := st.chat_input(placeholder_text):
    save_message_to_db("user", user_prompt, "text")
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="💎"):
        if mode == "🎨 رسم صورة":
            with st.spinner("🎨 جاري رسم الصورة عبر FLUX..."):
                img = generate_image(user_prompt)
                if img:
                    st.image(img, caption=f"رسمة: {user_prompt}")
                    save_message_to_db("assistant", "[صورة مولدة]", "image")
                else:
                    st.error("تعذر رسم الصورة.")
        else:
            message_placeholder = st.empty()
            with st.spinner("🔍 جاري المعالجة والبحث..."):
                system_instruction = SUPER_SYSTEM_PROMPT
                if pdf_context:
                    system_instruction += f"\n\n--- [محتوى PDF] ---\n{pdf_context}"
                else:
                    search_context = search_web(user_prompt)
                    if search_context:
                        system_instruction += f"\n\n--- [نتائج البحث] ---\n{search_context}"

                api_messages = [{"role": "system", "content": system_instruction}]
                for m in messages:
                    if m.get("type") != "image":
                        api_messages.append({"role": m["role"], "content": m["content"]})
                api_messages.append({"role": "user", "content": user_prompt})

                response_text = None
                try:
                    client = InferenceClient(model=ACTIVE_TEXT_MODEL, token=HF_TOKEN)
                    response = client.chat_completion(messages=api_messages, max_tokens=4096, temperature=0.3)
                    response_text = response.choices[0].message.content
                except Exception as e:
                    response_text = f"عذراً، حدث خطأ في الاتصال بالنموذج: {str(e)}"

                if response_text:
                    message_placeholder.markdown(response_text)
                    save_message_to_db("assistant", response_text, "text")
