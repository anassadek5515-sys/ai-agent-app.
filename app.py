import streamlit as st
import os
import json
from datetime import datetime
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS
from pypdf import PdfReader

# ==========================================
# 1. إعدادات الشاشة الأساسية
# ==========================================
st.set_page_config(page_title="Anas AI Ultra", page_icon="💎", layout="centered")

# ==========================================
# 2. تصميم CSS الشامل (UI/UX + إصلاحات الموبايل)
# ==========================================
st.markdown("""
    <style>
    :root { color-scheme: dark !important; }
    
    /* إخفاء العلامات المائية لستريمليت */
    [data-testid="stSidebar"], #MainMenu, header, footer { display: none !important; }
    
    /* الخلفية العامة */
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

    /* تصميم فقاعات المحادثة (Premium UI) */
    [data-testid="stChatMessage"] {
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* رسالة المستخدم */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #1f6feb 0%, #1158c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
        color: #ffffff !important;
    }

    /* رسالة الذكاء الاصطناعي */
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }

    /* --- التغلب القطعي على مشكلة مربع الإدخال الأبيض في أندرويد --- */
    div[data-testid="stChatInput"], div[data-testid="stBottom"], .stChatInputContainer {
        background-color: #0d1117 !important;
        background: #0d1117 !important;
        border: none !important;
    }

    .stChatInputContainer {
        border-radius: 30px !important;
        border: 1px solid #30363d !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.5) !important;
    }

    .stChatInputContainer textarea, div[data-testid="stChatInput"] * {
        background-color: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        -webkit-appearance: none !important;
        font-size: 16px !important;
        box-shadow: none !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: #8b949e !important;
        -webkit-text-fill-color: #8b949e !important;
    }
    
    /* تصميم الأزرار */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #30363d !important;
        background-color: #21262d !important;
        color: #ffffff !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        border-color: #8b949e !important;
        background-color: #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. إعدادات السيرفرات والمفاتيح
# ==========================================
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة HF_TOKEN في Secrets.")
    st.stop()

TEXT_MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

# ==========================================
# 4. الدوال الأساسية (بحث، صور، ملفات)
# ==========================================
def search_web(query, max_results=3):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- المصدر: {r['title']}\n  الملخص: {r['body']}")
        return "\n".join(results)
    except Exception:
        return ""

def generate_image(prompt):
    try:
        client = InferenceClient(model=IMAGE_MODEL, token=HF_TOKEN)
        return client.text_to_image(prompt)
    except Exception:
        return None

def extract_file_text(uploaded_file):
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            return "".join([page.extract_text() or "" for page in reader.pages])[:5000]
        elif uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")[:5000]
    except Exception:
        return ""

# ==========================================
# 5. واجهة المستخدم والتفاعل
# ==========================================
st.markdown("<h2 style='text-align: center; color: #ffffff;'>💎 أنس AI Ultra</h2>", unsafe_allow_html=True)

# ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# إعدادات متقدمة (Expander)
with st.expander("⚙️ الإعدادات المتقدمة وسجل المحادثة", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        persona = st.selectbox("شخصية المساعد:", ["مساعد ذكي خارق", "مبرمج ومهندس برمجيات", "مستشار أعمال وتسويق", "طبيب ومستشار صحي"])
    with col2:
        temperature = st.slider("نسبة الإبداع (0=دقيق، 1=مبدع):", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("🧹 مسح الذاكرة", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col4:
        # تحميل سجل المحادثة كملف نصي
        chat_history_text = "\n\n".join([f"{'أنت' if m['role']=='user' else 'أنس AI'}: {m['content']}" for m in st.session_state.messages if m.get('type') == 'text'])
        st.download_button(label="💾 حفظ المحادثة", data=chat_history_text, file_name=f"Anas_AI_Chat_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)

# اختيار الوضع
mode = st.radio("اختر وضع التشغيل:", ["💬 بحث ومحادثة", "🎨 رسم وتوليد صور", "📄 تحليل ملفات (PDF/TXT)"], horizontal=True, label_visibility="collapsed")

# معالجة الملفات إذا تم اختيار الوضع
file_context = ""
if mode == "📄 تحليل ملفات (PDF/TXT)":
    uploaded_file = st.file_uploader("ارفع ملف PDF أو TXT:", type=["pdf", "txt"])
    if uploaded_file:
        with st.spinner("📄 جاري قراءة الملف..."):
            file_context = extract_file_text(uploaded_file)
            st.success("تم قراءة الملف بنجاح! اسألني عن محتواه.")

# تخصيص شخصية الذكاء الاصطناعي
PERSONAS = {
    "مساعد ذكي خارق": "أنت مساعد ذكاء اصطناعي خارق، تمتلك الوصول للإنترنت.",
    "مبرمج ومهندس برمجيات": "أنت مهندس برمجيات محترف (Senior Developer). أجب بأكواد نظيفة ومنسقة مع الشرح.",
    "مستشار أعمال وتسويق": "أنت خبير في إدارة الأعمال والتسويق الإلكتروني. قدم استراتيجيات عملية بالأرقام.",
    "طبيب ومستشار صحي": "أنت مستشار صحي وطبي مبني على العلم، قدم نصائح عامة مع التنبيه بضرورة استشارة طبيب مختص."
}
SYSTEM_PROMPT = f"{PERSONAS[persona]}\nقواعد: أجب باللغة العربية بدقة، استخدم النقاط والعناوين العريضة للتنسيق."

# عرض المحادثات السابقة
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "💎"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"], caption="الصورة المولدة")
        else:
            st.markdown(msg["content"])

# إدخال المستخدم
placeholder_dict = {
    "💬 بحث ومحادثة": "اسألني، ابحث في الإنترنت، أو أطلب كود...",
    "🎨 رسم وتوليد صور": "اكتب وصف الصورة بالتفصيل...",
    "📄 تحليل ملفات (PDF/TXT)": "اطلب تلخيص الملف أو اسأل عن معلومة جواه..."
}

if user_prompt := st.chat_input(placeholder_dict[mode]):
    st.session_state.messages.append({"role": "user", "content": user_prompt, "type": "text"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="💎"):
        if mode == "🎨 رسم وتوليد صور":
            with st.spinner("🎨 جاري الإبداع ورسم الصورة..."):
                img = generate_image(user_prompt)
                if img:
                    st.image(img, caption=f"رسمة: {user_prompt}")
                    st.session_state.messages.append({"role": "assistant", "content": img, "type": "image"})
                else:
                    st.error("تعذر رسم الصورة، حاول تغيير الوصف.")
        else:
            message_placeholder = st.empty()
            with st.spinner("🔍 جاري التحليل والتفكير..."):
                system_instruction = SYSTEM_PROMPT
                
                # إضافة سياق الملف أو البحث
                if file_context:
                    system_instruction += f"\n\n--- [محتوى الملف المرفوع] ---\n{file_context}"
                else:
                    search_context = search_web(user_prompt)
                    if search_context:
                        system_instruction += f"\n\n--- [نتائج بحث الإنترنت الحي] ---\n{search_context}"

                # تجهيز الذاكرة الكاملة للإرسال (Full Memory)
                api_messages = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.messages[:-1]:
                    if m.get("type") != "image":  # لا ترسل الصور للـ Text Model
                        api_messages.append({"role": m["role"], "content": m["content"]})
                api_messages.append({"role": "user", "content": user_prompt})

                # الاتصال بالسيرفرات مع Fallback
                response_text = None
                for model_id in TEXT_MODELS:
                    try:
                        client = InferenceClient(model=model_id, token=HF_TOKEN)
                        response = client.chat_completion(messages=api_messages, max_tokens=4096, temperature=temperature)
                        response_text = response.choices[0].message.content
                        if response_text: break
                    except Exception:
                        continue

                if response_text:
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text, "type": "text"})
                else:
                    st.error("حدث خطأ في الاتصال بالخوادم، جرب مرة أخرى.")
