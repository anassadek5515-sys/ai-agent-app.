import streamlit as st
import os
from huggingface_hub import InferenceClient

# 1. إعدادات الصفحة وإخفاء القائمة الجانبية
st.set_page_config(
    page_title="AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS عصري وانسيابي (بدون قائمة جانبية وبخيارات علوية)
st.markdown("""
    <style>
    /* إخفاء القائمة الجانبية بالكامل */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* خلفية متدرجة وانسيابية */
    .stApp {
        background: linear-gradient(-45deg, #0b0f19, #111827, #1e1b4b, #0d1117);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
        color: #f3f4f6;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ضبط اتجاه النصوص للغة العربية */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    /* تحسين شكل فقاعات المحادثة */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    /* أزرار الهيدر والتصميم */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# 3. التأكد من المفتاح
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

if not HF_TOKEN:
    st.error("⚠️ يرجى إدخال HF_TOKEN في Secrets على Streamlit Cloud ليعمل الذكاء الاصطناعي!")
    st.stop()

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 4. الهيدر والخيارات العلوية (Top Controls)
col1, col2 = st.columns([3, 1])

with col1:
    st.title("✨ المساعد الذكي المتكامل")
    st.caption("ذكاء اصطناعي تفاعلي وسريع - أسلوب إجابات دقيق وانسيابي")

with col2:
    if st.button("محادثة جديدة 🔄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# أزرار الاختيار العلوية (Pills Top Selector)
selected_mode = st.segmented_control(
    "اختر نمط الإجابة:",
    [
        "💼 تجاري وأعمال",
        "🎨 ابتكاري وإبداعي",
        "📊 اقتصادي وتحليلي",
        "🧩 حل المشكلات والأكواد"
    ],
    default="💼 تجاري وأعمال"
)

# خيار رفع الملفات في أعلى الصفحة بشكل خفيف
with st.expander("📂 رفع ملف أو كود للتحليل (اختياري)"):
    uploaded_file = st.file_uploader("ارفق ملفك هنا:", type=["txt", "py", "md", "csv", "json"], label_visibility="collapsed")

st.divider()

# 5. التوجيهات
prompts = {
    "💼 تجاري وأعمال": "أنت مساعد ذكاء اصطناعي وخبير استشاري إداري وتجاري. قدم شروحات دقيقة واحترافية باللغة العربية.",
    "🎨 ابتكاري وإبداعي": "أنت مبتكر ومبدع. قدم أفكاراً جبارة وحلولاً إبداعية جديدة باللغة العربية.",
    "📊 اقتصادي وتحليلي": "أنت خبير اقتصادي ومحلل بيانات. قدم تحليلات موثوقة ودقيقة باللغة العربية.",
    "🧩 حل المشكلات والأكواد": "أنت مهندس ذكاء اصطناعي خبير في حل الأكواد والمشاكل التقنية المعقدة باللغة العربية."
}

# 6. إدارة عرض المحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. استقبال وتوليد الردود
if user_prompt := st.chat_input("اكتب سؤالك، كودك، أو مهمتك هنا..."):
    full_content = user_prompt
    if uploaded_file is not None:
        file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        full_content += f"\n\n--- [ملف مرفق: {uploaded_file.name}] ---\n{file_text[:20000]}"

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        mode_key = selected_mode if selected_mode in prompts else "💼 تجاري وأعمال"
        api_messages = [{"role": "system", "content": prompts[mode_key]}]
        
        for m in st.session_state.messages[:-1]:
            api_messages.append({"role": m["role"], "content": m["content"]})
        api_messages.append({"role": "user", "content": full_content})

        with st.spinner("جاري الصياغة والتفكير..."):
            try:
                response = client.chat_completion(
                    messages=api_messages,
                    max_tokens=4096,
                    temperature=0.4,
                )
                response_text = response.choices[0].message.content
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
