import streamlit as st
import os
from huggingface_hub import InferenceClient

# 1. إعدادات الصفحة الأساسية (إخفاء القائمة الجانبية تماماً)
st.set_page_config(
    page_title="AI Pro Assistant",
    page_icon="✨",
    layout="centered", # التمركز في المنتصف ليكون مطابقاً لواجهات الذكاء الاصطناعي
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS احترافي (Dark Mode) مطابق للذكاء الاصطناعي الحديث
st.markdown("""
    <style>
    /* إخفاء القائمة الجانبية وعناصر Streamlit الافتراضية بالكامل */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* خلفية داكنة راقية ومريحة للعين */
    .stApp {
        background-color: #131314; /* لون خلفية احترافي */
        color: #e3e3e3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* ضبط اتجاه النصوص للغة العربية */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }

    /* تنسيق رسالة المستخدم (User Bubble) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #1e1f20 !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* تنسيق رسالة الذكاء الاصطناعي (AI Bubble) */
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: transparent !important;
        padding: 15px 10px !important;
        margin: 10px 0 !important;
    }

    /* مربع إدخال النص العائم والمنحني */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 5px 10px;
        transition: all 0.3s ease-in-out;
    }
    .stChatInputContainer:focus-within {
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important;
    }

    /* أزرار الخيارات العلوية (Radio Buttons) لتكون مثل الأزرار الانسيابية */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        background: #1e1f20;
        padding: 10px;
        border-radius: 25px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. إعداد نموذج الذكاء الاصطناعي
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

if not HF_TOKEN:
    st.error("⚠️ يرجى إدخال HF_TOKEN في إعدادات Secrets.")
    st.stop()

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 4. واجهة المستخدم (الخيارات العلوية)
st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 5px;'>✨ كيف يمكنني مساعدتك اليوم؟</h2>", unsafe_allow_html=True)

# أزرار اختيار النمط متمركزة في الأعلى
selected_mode = st.radio(
    "اختر تخصص المساعد:",
    ["💼 تجاري وأعمال", "🎨 ابتكاري وإبداعي", "📊 تحليل اقتصادي", "💻 برمجة وتقنية"],
    horizontal=True,
    label_visibility="collapsed"
)

prompts = {
    "💼 تجاري وأعمال": "أنت مساعد ذكي وخبير استشاري تجاري. قدم إجابات دقيقة واحترافية باللغة العربية.",
    "🎨 ابتكاري وإبداعي": "أنت مساعد ذكي ومبدع. قدم أفكاراً مبتكرة وحلولاً غير تقليدية باللغة العربية.",
    "📊 تحليل اقتصادي": "أنت مساعد ذكي وخبير اقتصادي. قدم تحليلات موثوقة ومبنية على المنطق باللغة العربية.",
    "💻 برمجة وتقنية": "أنت مساعد ذكي ومهندس برمجيات محترف. أجب عن الأسئلة التقنية واكتب أكواداً دقيقة باللغة العربية."
}

# 5. زر مسح المحادثة بشكل خفي وأنيق
col1, col2, col3 = st.columns([4, 1, 4])
with col2:
    if st.button("🧹 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 6. إدارة سجل المحادثة (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. مربع الإدخال الرئيسي والاستجابة (بدون حدود للطول)
if user_prompt := st.chat_input("اكتب رسالتك هنا..."):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # تجهيز السياق للذكاء الاصطناعي
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        api_messages = [{"role": "system", "content": prompts.get(selected_mode, prompts["💼 تجاري وأعمال"])}]
        
        for m in st.session_state.messages[:-1]:
            api_messages.append({"role": m["role"], "content": m["content"]})
        
        api_messages.append({"role": "user", "content": user_prompt})

        with st.spinner("يفكر..."):
            try:
                # الاستدعاء بدون أي حد أقصى ليجاوب بحرية تامة
                response = client.chat_completion(
                    messages=api_messages,
                    max_tokens=4096,  # السعة القصوى للاستجابات الطويلة
                    temperature=0.3,  # دقة عالية وإجابات مركزة
                )
                response_text = response.choices[0].message.content
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
