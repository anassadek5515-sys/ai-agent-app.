import streamlit as st
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# 1. إعدادات الصفحة والتصميم العالي
st.set_page_config(
    page_title="Gemini-Style AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# لمسة CSS لتنسيق الواجهة وتقريبها من واجهات الذكاء الاصطناعي الاحترافية
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✨ المساعد الذكي التفاعلي")
st.caption("تطبيق AI Agent متكامل يدعم المحادثة المستمرة وتفكيك المهام")

# 2. الشريط الجانبي للإعدادات وتخصيص الشخصية
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bot.png", width=70)
    st.title("تخصيص الـ Agent")
    
    personality = st.radio(
        "اختر نمط المساعد:",
        ("✨ متكامل وتفاعلي (Gemini Style)", "💻 خبير تقني وبرمجة", "📋 منظم ومحلل مهام")
    )
    
    st.divider()
    
    temperature = st.slider("مستوى المرونة والابتكار:", 0.1, 1.0, 0.4, 0.1)
    max_tokens = st.slider("أقصى طول للإجابة:", 150, 600, 350, 50)
    
    st.divider()
    
    if st.button("بدء محادثة جديدة 🔄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. تحميل النموذج
@st.cache_resource
def load_model():
    model_id = "Qwen/Qwen1.5-0.5B-Chat"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return tokenizer, pipe

tokenizer, pipe = load_model()

# 4. توجيه النظام (System Prompts)
system_prompts = {
    "✨ متكامل وتفاعلي (Gemini Style)": "أنت مساعد ذكاء اصطناعي ذكي، متعاون، وبسيط في الشرح. أجب بوضوح ودقة باللغة العربية مع دعم التنسيق المنظم.",
    "💻 خبير تقني وبرمجة": "أنت مهندس برمجيات وخبير تقني. قدم حلولاً برمجية نظيفة مع شرح الكود والخطوات. أجب باللغة العربية.",
    "📋 منظم ومحلل مهام": "أنت خبير في إدارة المشاريع والمهام. قم بتفكيك الأهداف الصعبة إلى 3-5 خطوات تنفيذية مباشرة. أجب باللغة العربية."
}

# 5. إدارة سياق وذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض سياق الحوار السابق
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 6. استقبال المدخلات وتوليد الرد بالبث التفاعلي
if user_prompt := st.chat_input("اسألني عن أي شيء أو اطلب مهمة..."):
    # إضافة ورسم رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    # معالجة وتوليد الرد
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        
        # إعداد الرسائل وتغذية سياق الحوار الكامل للنموذج
        formatted_messages = [{"role": "system", "content": system_prompts[personality]}]
        for m in st.session_state.messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})
            
        formatted_input = tokenizer.apply_chat_template(
            formatted_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        with st.spinner("جاري صياغة الإجابة..."):
            outputs = pipe(
                formatted_input,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                repetition_penalty=1.2
            )
            
            full_text = outputs[0]["generated_text"]
            response_text = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()

        # محاكاة تأثير ظهور النص التدريجي (Streaming Effect)
        displayed_text = ""
        for chunk in response_text.split(" "):
            displayed_text += chunk + " "
            time.sleep(0.03)
            message_placeholder.markdown(displayed_text + "▌")
        
        message_placeholder.markdown(response_text)

    # حفظ الرد في ذاكرة المحادثة
    st.session_state.messages.append({"role": "assistant", "content": response_text})
