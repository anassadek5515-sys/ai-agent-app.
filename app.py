import streamlit as st
import os
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS

# 1. إعدادات الشاشة
st.set_page_config(page_title="Super AI Agent", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# 2. تصميم CSS صارم لإلغاء أي ألوان بيضاء من نظام الأندرويد نهائياً
st.markdown("""
    <style>
    :root {
        color-scheme: dark !important;
    }
    
    [data-testid="collapsedControl"], [data-testid="stSidebar"], #MainMenu, header, footer { display: none !important; }
    
    html, body, .stApp { 
        background-color: #121212 !important; 
        color: #FFFFFF !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    p, span, div, h1, h2, h3, h4, label, li {
        color: #FFFFFF !important;
        direction: rtl;
        text-align: right;
    }

    /* فقاعات المحادثة */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #242526 !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
        margin: 8px 0 !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3B3C !important;
    }

    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: transparent !important;
        padding: 12px 10px !important;
        margin: 8px 0 !important;
        color: #FFFFFF !important;
    }

    /* --- التغلب على خلفية WebView البيضاء بالكامل --- */
    div[data-testid="stChatInput"],
    div[data-testid="stBottom"],
    .stChatInputContainer,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background-color: #1E1E1E !important;
        background: #1E1E1E !important;
        border-radius: 25px !important;
        border: 1px solid #444444 !important;
    }

    /* إجبار النص داخل حقل الإدخال وحاوياته على اللون الأبيض */
    .stChatInputContainer textarea,
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] * {
        background-color: #1E1E1E !important;
        background: #1E1E1E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        -webkit-appearance: none !important;
        box-shadow: none !important;
    }

    .stChatInputContainer textarea::placeholder,
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. إعداد المفتاح
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة HF_TOKEN في Secrets.")
    st.stop()

# نماذج النصوص والمحادثة
TEXT_MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

# نموذج توليد الصور
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

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
        image = client.text_to_image(prompt)
        return image
    except Exception:
        return None

st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>✨ أنس AI</h2>", unsafe_allow_html=True)

# شريط التحكم والأزرار
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🧹 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col2:
    mode = st.radio("الوضع:", ["💬 محادثة وبحث", "🎨 رسم صورة"], horizontal=True, label_visibility="collapsed")

SUPER_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي خارق ومتقدم، تمتلك الوصول المباشر للإنترنت.
قواعد الإجابة:
1. الفهم والدقة: أجب بدقة وشكل مفصل ومباشر باللغة العربية.
2. التنظيم: استخدم العناوين والخط العريض (Bold) والنقاط.
3. المظهر: أجب بتنسيق احترافي جداً وبثقة."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("type") == "image":
            st.image(msg["content"], caption="الصورة الناتجة")
        else:
            st.markdown(msg["content"])

placeholder_text = "اكتب وصف الصورة بالإنجليزية أو العربية..." if mode == "🎨 رسم صورة" else "اسألني عن أي شيء..."

if user_prompt := st.chat_input(placeholder_text):
    st.session_state.messages.append({"role": "user", "content": user_prompt, "type": "text"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="✨"):
        if mode == "🎨 رسم صورة":
            with st.spinner("🎨 جاري رسم الصورة..."):
                img = generate_image(user_prompt)
                if img:
                    st.image(img, caption=f"رسمة: {user_prompt}")
                    st.session_state.messages.append({"role": "assistant", "content": img, "type": "image"})
                else:
                    st.error("تعذر رسم الصورة حالياً، جرب وصفاً آخر.")
        else:
            message_placeholder = st.empty()
            with st.spinner("🔍 جاري التفكير والبحث..."):
                search_context = search_web(user_prompt)
                system_instruction = SUPER_SYSTEM_PROMPT
                
                if search_context:
                    system_instruction += f"\n\n--- [نتائج البحث الحي من الإنترنت] ---\n{search_context}"

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
                    except Exception:
                        continue

                if response_text:
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text, "type": "text"})
                else:
                    st.error("حدث خطأ في الاتصال بالسيرفرات.")
