import streamlit as st
import os
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS
from pypdf import PdfReader

# 1. إعدادات الشاشة الأساسية
st.set_page_config(page_title="Anas AI Ultra", page_icon="💎", layout="centered", initial_sidebar_state="collapsed")

# 2. تصميم CSS الخارق للواجهة البيضاوية العائمة (Gemini style)
st.markdown("""
    <style>
    :root { color-scheme: dark !important; }
    
    /* إخفاء العناصر غير الضرورية */
    [data-testid="stSidebar"], #MainMenu, header, footer { display: none !important; }
    
    /* الخلفية الداكنة العامة للموقع والصفحة */
    html, body, .stApp { 
        background-color: #0d1117 !important; 
        color: #c9d1d9 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    p, span, div, h1, h2, h3, h4, label, li {
        color: #c9d1d9 !important;
        direction: rtl;
        text-align: right;
    }

    /* تصميم فقاعات المحادثة العائمة */
    [data-testid="stChatMessage"] {
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* رسالة المستخدم بلون متدرج */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #1f6feb 0%, #1158c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
        color: #ffffff !important;
    }

    /* رسالة الذكاء الاصطناعي بلون داكن */
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }

    /* ========================================================
       تصميم مربع الإدخال البيضاوي العائم (Gemini/ الصورة الثانية)
       ======================================================== */
       
    /* 1. إزالة الشريط السفلي تماماً وجعل الخلفية شفافة */
    div[data-testid="stBottom"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 20px !important; /* رفعه قليلاً عن الكيبورد */
    }

    /* 2. تصميم الحاوية البيضاوية العائمة */
    .stChatInputContainer {
        background-color: #131314 !important; /* لون داكن مطابق للصورة الثانية */
        border-radius: 35px !important; /* حواف بيضاوية دائرية بالكامل */
        border: 1px solid #444746 !important; /* إطار رمادي خفيف */
        padding: 5px 20px !important;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.6) !important; /* تأثير ظل العوم القوي */
        width: 95% !important; /* ترك مسافة صغيرة من الجوانب */
        margin: 0 auto !important; /* توسيط المربع */
    }

    /* 3. تضبيط خط الكتابة الداخلي واللون */
    .stChatInputContainer textarea {
        background-color: transparent !important;
        color: #e3e3e3 !important;
        -webkit-text-fill-color: #e3e3e3 !important;
        -webkit-appearance: none !important;
        font-size: 16px !important;
        box-shadow: none !important;
    }

    /* 4. لون نص التوضيح داخل المربع */
    .stChatInputContainer textarea::placeholder {
        color: #8b949e !important;
        -webkit-text-fill-color: #8b949e !important;
    }
    
    /* تصميم الأزرار العلوية */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #30363d !important;
        background-color: #21262d !important;
        color: #ffffff !important;
        transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# 3. إعداد المفاتيح والنماذج (بقيت كما هي)
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة HF_TOKEN.")
    st.stop()

TEXT_MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

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

# 4. واجهة التطبيق
st.markdown("<h2 style='text-align: center; color: #ffffff;'>💎 أنس AI Ultra</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🧹 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col2:
    mode = st.radio("الوضع:", ["💬 محادثة وبحث", "🎨 رسم صورة", "📄 تحليل PDF"], horizontal=True, label_visibility="collapsed")

pdf_context = ""
if mode == "📄 تحليل PDF":
    uploaded_file = st.file_uploader("ارفع ملف PDF للتحليل:", type=["pdf"])
    if uploaded_file:
        with st.spinner("📄 جاري قراءة الملف..."):
            pdf_context = extract_pdf_text(uploaded_file)
            st.success("تم قراءة الملف بنجاح!")

SUPER_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي خارق، تمتلك الوصول للإنترنت.
أجب بدقة باللغة العربية، استخدم التنسيق والنقاط."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "💎"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"], caption="الصورة المولدة")
        else:
            st.markdown(msg["content"])

# إدخال المستخدم
placeholder_text = "اسألني، ابحث في الإنترنت، أو أطلب كود..." if mode == "💬 محادثة وبحث" else "اكتب وصف الصورة..."

if user_prompt := st.chat_input(placeholder_text):
    st.session_state.messages.append({"role": "user", "content": user_prompt, "type": "text"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="💎"):
        if mode == "🎨 رسم صورة":
            with st.spinner("🎨 جاري رسم الصورة..."):
                img = generate_image(user_prompt)
                if img:
                    st.image(img, caption=f"رسمة: {user_prompt}")
                    st.session_state.messages.append({"role": "assistant", "content": img, "type": "image"})
                else:
                    st.error("تعذر رسم الصورة.")
        else:
            message_placeholder = st.empty()
            with st.spinner("🔍 جاري المعالجة..."):
                system_instruction = SUPER_SYSTEM_PROMPT
                if pdf_context:
                    system_instruction += f"\n\n--- [محتوى PDF] ---\n{pdf_context}"
                else:
                    search_context = search_web(user_prompt)
                    if search_context:
                        system_instruction += f"\n\n--- [نتائج البحث] ---\n{search_context}"

                api_messages = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.messages[:-1]:
                    if m.get("type") != "image":
                        api_messages.append({"role": m["role"], "content": m["content"]})
                api_messages.append({"role": "user", "content": user_prompt})

                response_text = None
                for model_id in TEXT_MODELS:
                    try:
                        client = InferenceClient(model=model_id, token=HF_TOKEN)
                        response = client.chat_completion(messages=api_messages, max_tokens=4096, temperature=0.3)
                        response_text = response.choices[0].message.content
                        if response_text: break
                    except Exception: continue

                if response_text:
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text, "type": "text"})
                else:
                    st.error("حدث خطأ.")
