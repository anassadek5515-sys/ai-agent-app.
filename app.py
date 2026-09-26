import streamlit as st
import os
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS

# 1. إعدادات الصفحة الأساسية (واجهة راقية بدون شريط جانبي)
st.set_page_config(
    page_title="Super AI Agent",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS احترافي (Dark Mode)
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background-color: #131314;
        color: #e3e3e3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #1e1f20 !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: transparent !important;
        padding: 15px 10px !important;
        margin: 10px 0 !important;
    }

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
    </style>
""", unsafe_allow_html=True)

# 3. إعداد نموذج الذكاء الاصطناعي
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

if not HF_TOKEN:
    st.error("⚠️ يرجى إدخال HF_TOKEN في إعدادات Secrets على Streamlit Cloud.")
    st.stop()

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# 🌐 دالة البحث السريع في الإنترنت
def search_web(query, max_results=3):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- المصدر: {r['title']}\n  الملخص: {r['body']}\n  الرابط: {r['href']}")
        return "\n".join(results)
    except Exception as e:
        return ""

# 4. الواجهة الرئيسية
st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 5px;'>✨ أنا مساعدك الخارق.. اسألني أو ابحث معي في الإنترنت!</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 1, 4])
with col2:
    if st.button("🧹 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 5. التوجيهات الخارقة للذكاء الاصطناعي
SUPER_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي خارق ومتقدم، تمتلك الوصول المباشر للإنترنت ولدي المعرفة الكاملة بجميع العلوم.
قواعد الإجابة:
1. الفهم والدقة: أجب بدقة وشكل مفصل ومباشر باللغة العربية.
2. التنظيم: استخدم العناوين والخط العريض (Bold) والنقاط لجعل الإجابة مريحة ومنظمة.
3. معالجة نتائج البحث: إذا تم تزويدك بـ "نتائج بحث من الإنترنت"، استخدمها لصياغة إجابة محدثة ودقيقة جداً واذكر الأسباب أو الأخبار بوضوح.
4. الثقة: تحدث بثقة واحترافية عالية كأفضل ذكاء اصطناعي في العالم."""

# 6. إدارة سجل المحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. معالجة إدخال المستخدم والبحث الحي
if user_prompt := st.chat_input("اسألني عن أي شيء، أخبار، أو كود..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        with st.spinner("🔍 جاري البحث في الإنترنت والتفكير..."):
            # البحث المباشر في النت في الخلفية
            search_context = search_web(user_prompt)
            
            #دمج نتائج البحث مع برومبت النظام
            system_instruction = SUPER_SYSTEM_PROMPT
            if search_context:
                system_instruction += f"\n\n--- [نتائج البحث الحي المباشر من الإنترنت] ---\n{search_context}"

            api_messages = [{"role": "system", "content": system_instruction}]
            
            for m in st.session_state.messages[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            api_messages.append({"role": "user", "content": user_prompt})

            try:
                response = client.chat_completion(
                    messages=api_messages,
                    max_tokens=4096,
                    temperature=0.3,
                )
                response_text = response.choices[0].message.content
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {e}")
