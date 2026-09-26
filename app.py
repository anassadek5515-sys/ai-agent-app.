import streamlit as st
import os
from huggingface_hub import InferenceClient

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Super AI Agent",
    page_icon="🤖",
    layout="wide"
)

# 2. فحص وجود المفتاح
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

if not HF_TOKEN:
    st.error("⚠️ يرجى إضافة مفتاح HF_TOKEN في Streamlit Secrets ليعمل التطبيق!")
    st.info("💡 طريقة الإضافة: افتح Settings في Streamlit Cloud -> ثم Secrets -> واكتب HF_TOKEN = 'your_token'")
    st.stop()

# 3. إعداد العميل للموديل السريع Qwen2.5-7B
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 4. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.title("⚙️ خيارات الـ Agent")
    selected_mode = st.radio(
        "اختر نمط المحرك:",
        (
            "💼 نمط تجاري وأعمال",
            "🎨 نمط ابتكاري وإبداعي",
            "📊 نمط اقتصادي وتحليلي",
            "🧩 نمط حل المشكلات المعقدة"
        )
    )
    st.divider()
    temperature = st.slider("مستوى الإبداع:", 0.1, 1.0, 0.4, 0.1)
    max_tokens = st.slider("أقصى طول للإجابة:", 200, 2000, 800, 100)
    st.divider()
    uploaded_file = st.file_uploader("📂 رفع ملف/كود للتحليل (حتى 250 صفحة):", type=["txt", "py", "md", "csv", "json"])
    st.divider()
    if st.button("بدء محادثة جديدة 🔄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 5. الواجهة الرئيسية
st.title("✨ الذكاء الاصطناعي الخارق والكامل")
st.caption("دعم التحليل المعقد، رفع الأكواد والملفات، وإجابات دقيقة وسريعة")

prompts = {
    "💼 نمط تجاري وأعمال": "أنت خبير استشاري تجاري وإداري. قدم خططاً احترافية باللغة العربية.",
    "🎨 نمط ابتكاري وإبداعي": "أنت مبتكر ومبدع. قدم أفكاراً جبارة وحلولاً إبداعية جديدة باللغة العربية.",
    "📊 نمط اقتصادي وتحليلي": "أنت خبير اقتصادي ومحلل بيانات. قدم تحليلات اقتصادية موثوقة باللغة العربية.",
    "🧩 نمط حل المشكلات المعقدة": "أنت مهندس ذكاء اصطناعي خبير في حل المشاكل البرمجية والتعامل مع الأكواد الطويلة."
}

# 6. إدارة سجل المحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. استقبال المدخلات والتشغيل
if user_prompt := st.chat_input("اكتب سؤالك أو كودك هنا..."):
    full_content = user_prompt
    if uploaded_file is not None:
        file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        full_content += f"\n\n--- [ملف مرفق: {uploaded_file.name}] ---\n{file_text[:15000]}"

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="⚡"):
        message_placeholder = st.empty()
        api_messages = [{"role": "system", "content": prompts[selected_mode]}]
        
        for m in st.session_state.messages[:-1]:
            api_messages.append({"role": m["role"], "content": m["content"]})
        api_messages.append({"role": "user", "content": full_content})

        with st.spinner("جاري التفكير والصياغة..."):
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
