import streamlit as st
import os
import base64
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS

# 1. إعدادات الشاشة
st.set_page_config(page_title="Super AI Agent", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# 2. تصميم CSS
st.markdown("""
    <style>
    [data-testid="collapsedControl"], [data-testid="stSidebar"], #MainMenu, header, footer { display: none !important; }
    .stApp { background-color: #131314; color: #e3e3e3; font-family: 'Segoe UI', sans-serif; }
    html, body, [class*="css"] { direction: rtl; text-align: right; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #1e1f20 !important; border-radius: 20px !important; padding: 15px 20px !important; margin: 10px 0 !important;
    }
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: transparent !important; padding: 15px 10px !important; margin: 10px 0 !important;
    }
    .stChatInputContainer {
        background-color: #1e1f20 !important; border-radius: 30px !important; border: 1px solid rgba(255,255,255,0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. المفتاح والنماذج
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة HF_TOKEN في Secrets.")
    st.stop()

AVAILABLE_MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

def search_web(query, max_results=3):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- المصدر: {r['title']}\n  الملخص: {r['body']}")
        return "\n".join(results)
    except Exception:
        return ""

st.markdown("<h2 style='text-align: center; color: white;'>✨ مساعدك الذكي الخارق</h2>", unsafe_allow_html=True)

# خيار رفع صورة لتحليلها
uploaded_image = st.file_uploader("📷 ارفق صورة لتحليلها (اختياري)", type=["jpg", "png", "jpeg"])

col1, col2, col3 = st.columns([4, 1, 4])
with col2:
    if st.button("🧹 جديد", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

SUPER_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي خارق ومتقدم، تمتلك الوصول المباشر للإنترنت وتحليل البيانات.
قواعد الإجابة:
1. الفهم والدقة: أجب بدقة وشكل مفصل ومباشر باللغة العربية.
2. التنظيم: استخدم العناوين والخط العريض (Bold) والنقاط.
3. المظهر: أجب بتنسيق احترافي جداً وبثقة."""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if user_prompt := st.chat_input("اسألني عن أي شيء، كود، أو صورة..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        with st.spinner("🔍 جاري المعالجة والتفكير..."):
            search_context = search_web(user_prompt)
            system_instruction = SUPER_SYSTEM_PROMPT
            
            if search_context:
                system_instruction += f"\n\n--- [نتائج البحث الحي من الإنترنت] ---\n{search_context}"
            if uploaded_image:
                system_instruction += f"\n\n--- [ملاحظة: تم إرفاق صورة باسم {uploaded_image.name}] ---"

            api_messages = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            api_messages.append({"role": "user", "content": user_prompt})

            response_text = None
            for model_id in AVAILABLE_MODELS:
                try:
                    client = InferenceClient(model=model_id, token=HF_TOKEN)
                    response = client.chat_completion(messages=api_messages, max_tokens=4096, temperature=0.3)
                    response_text = response.choices[0].message.content
                    if response_text: break
                except Exception:
                    continue

            if response_text:
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("حدث خطأ في الاتصال بالسيرفرات.")

