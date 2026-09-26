import streamlit as st
import os
from huggingface_hub import InferenceClient

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Super AI Agent Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. فحص لغة الجهاز/المتصفح تلقائياً
user_lang = "ar"
try:
    headers = st.context.headers
    accept_lang = headers.get("Accept-Language", "")
    if accept_lang.startswith("en"):
        user_lang = "en"
except:
    user_lang = "ar"

selected_lang = st.sidebar.selectbox(
    "🌐 Language / اللغة",
    ("العربية", "English"),
    index=0 if user_lang == "ar" else 1
)

is_arabic = (selected_lang == "العربية")

# 3. تصميم CSS احترافي بألوان مبهجة ومتحركة واحترافية (Neon & Gradient Effects)
st.markdown("""
    <style>
    /* خلفية التطبيق والتدرج اللوني المبهج */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #311042, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #ffffff;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* إطار وأزرار متحركة بألوان مبهجة */
    .stButton>button {
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
        background-size: 200% auto;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
    }

    .stButton>button:hover {
        background-position: right center;
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
    }

    /* تحسين إطار الدردشة */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

if is_arabic:
    st.markdown("<style>html, body, [class*='css'] { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>html, body, [class*='css'] { direction: ltr; text-align: left; }</style>", unsafe_allow_html=True)

# 4. معجم النصوص والأنماط الـ 4 المطلوبة في الورقة
texts = {
    "ar": {
        "title": "✨ الذكاء الاصطناعي الخارق والكامل",
        "caption": "مزامنة تلقائية مع لغة جهازك، سرعة فائقة، ودعم التحليل المعقد والأكواد الطويلة",
        "sidebar_title": "⚙️ محرك الاستخدام",
        "modes": [
            "💼 نمط تجاري وأعمال (Business)",
            "🎨 نمط ابتكاري وإبداعي (Creative)",
            "📊 نمط اقتصادي وتحليلي (Economic)",
            "🧩 نمط حل المشكلات المعقدة (Problem Solving)"
        ],
        "temp": "مستوى المرونة والابتكار:",
        "tokens": "أقصى طول للإجابة (يدعم الإجابات الطويلة):",
        "upload_label": "📂 رفع ملفات أسطر/أكواد طويلة للتحليل (يدعم حتى 250 صفحة):",
        "reset": "بدء محادثة جديدة 🔄",
        "input_placeholder": "اسأل عن أي شيء، كود، أو مسألة صعبة بأي لغة...",
        "thinking": "جاري التفكير والصياغة السريعة...",
        "prompts": {
            "💼 نمط تجاري وأعمال (Business)": "أنت خبير استشاري تجاري وإداري. قم بتقديم خطط تسويقية وإدارية احترافية بأسلوب عملي ودقيق.",
            "🎨 نمط ابتكاري وإبداعي (Creative)": "أنت مبتكر ومبدع خارق. قدم أفكاراً غير تقليدية وحلولاً إبداعية جديدة ومميزة.",
            "📊 نمط اقتصادي وتحليلي (Economic)": "أنت خبير اقتصادي ومحلل بيانات دقيق. قم بتقييم الأرقام والبيانات وتقديم تحليلات اقتصادية موثوقة.",
            "🧩 نمط حل المشكلات المعقدة (Problem Solving)": "أنت مهندس ذكاء اصطناعي وخبير في تفكيك وتتبع أعقد المشاكل والأكواد البرمجية الطويلة خطوة بخطوة."
        }
    },
    "en": {
        "title": "✨ Super Ultimate AI Agent",
        "caption": "Auto-adapts to your device language, ultra-fast, supports complex analysis & massive code/docs",
        "sidebar_title": "⚙️ Engine Mode",
        "modes": [
            "💼 Business Mode",
            "🎨 Creative Mode",
            "📊 Economic Mode",
            "🧩 Complex Problem Solving"
        ],
        "temp": "Flexibility & Creativity Level:",
        "tokens": "Max Output Tokens (Supports Long Responses):",
        "upload_label": "📂 Upload large files/code for deep analysis (Up to 250 pages):",
        "reset": "Start New Session 🔄",
        "input_placeholder": "Ask anything, code, or complex queries in any language...",
        "thinking": "Fast processing & reasoning...",
        "prompts": {
            "💼 Business Mode": "You are an expert business consultant. Provide high-level professional strategies.",
            "🎨 Creative Mode": "You are a creative genius. Generate highly original and innovative ideas.",
            "📊 Economic Mode": "You are an expert economist and data analyst. Provide deep economic and data analysis.",
            "🧩 Complex Problem Solving": "You are an AI engineer specializing in solving complex multi-step problems and long codebases."
        }
    }
}

t = texts["ar" if is_arabic else "en"]

st.title(t["title"])
st.caption(t["caption"])

# 5. إعداد الاتصال بالسيرفر السريع Qwen2.5-7B
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إدخال HF_TOKEN في Streamlit Secrets لضمان السرعة العالية!")
    st.stop()

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 6. القائمة الجانبية (الشريط الجانبي)
with st.sidebar:
    st.title(t["sidebar_title"])
    selected_mode = st.radio("اختر المحرك المناسب:", t["modes"])
    st.divider()
    temperature = st.slider(t["temp"], 0.1, 1.0, 0.4, 0.1)
    max_tokens = st.slider(t["tokens"], 200, 2000, 800, 100)
    
    st.divider()
    uploaded_file = st.file_uploader(t["upload_label"], type=["txt", "py", "md", "csv", "json"])
    
    st.divider()
    if st.button(t["reset"], use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. إدارة سجل المحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 8. استقبال المدخلات والملفات وإرسالها للمحرك
if user_prompt := st.chat_input(t["input_placeholder"]):
    full_user_content = user_prompt
    
    # قراءة الملفات الكبيرة لو تم رفعها
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        full_user_content += f"\n\n--- [المحتوى المرفق من الملف ({uploaded_file.name})] ---\n{file_content[:15000]}"

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="⚡"):
        message_placeholder = st.empty()
        
        system_prompt = t["prompts"][selected_mode]
        api_messages = [{"role": "system", "content": system_prompt}]
        
        for m in st.session_state.messages[:-1]:
            api_messages.append({"role": m["role"], "content": m["content"]})
        api_messages.append({"role": "user", "content": full_user_content})
            
        with st.spinner(t["thinking"]):
            try:
                response = client.chat_completion(
                    messages=api_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                response_text = response.choices[0].message.content
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")

