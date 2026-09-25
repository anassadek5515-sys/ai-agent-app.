import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="Super AI Agent", page_icon="🧠", layout="wide")

st.title("🧠 المساعد الذكي المتكامل - Super AI Agent")
st.caption("تطبيق ذكاء اصطناعي تفاعلي يعتمد على نموذج Qwen1.5 المطور")

# 2. الشريط الجانبي (Sidebar) للتحكم في الخصائص
st.sidebar.header("⚙️ إعدادات الـ Agent")

agent_role = st.sidebar.selectbox(
    "اختر تخصص الـ Agent:",
    (
        "محلل مهام وخبرات (Task Planner)",
        "مساعد برمجة وحلول تقنية (Code Expert)",
        "محرر ومترجم نصوص احترافي (Writer & Translator)"
    )
)

temperature = st.sidebar.slider("مستوى الإبداع (Temperature):", 0.1, 1.0, 0.3, 0.1)
max_tokens = st.sidebar.slider("أقصى طول للرد (Max Tokens):", 100, 500, 300, 50)

if st.sidebar.button("مسح الذاكرة وبدء محادثة جديدة 🧹"):
    st.session_state.messages = []
    st.rerun()

# 3. تحميل النموذج وتخزينه في الذاكرة المؤقتة
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

# 4. تحديد التوجيه الخاص بالنظام بناءً على الخيار
system_prompts = {
    "محلل مهام وخبرات (Task Planner)": "أنت عميل ذكاء اصطناعي متخصص في تفكيك المشاكل والمهام إلى خطة عمل من خطوات تنفيذية مرتبة. أجب باللغة العربية بوضوح.",
    "مساعد برمجة وحلول تقنية (Code Expert)": "أنت خبير برمجة وتطوير برمجيات. قم بكتابة الأكواد وتصحيح الأخطاء مع شرح بسيط. أجب باللغة العربية.",
    "محرر ومترجم نصوص احترافي (Writer & Translator)": "أنت ممارس محترف لكتابة المحتوى والترجمة. قم بإعادة صياغة النصوص أو ترجمتها بأسلوب سلس واحترافي باللغة العربية."
}

# 5. إدارة سجل المحادثة (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة على الشاشة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. استقبال مدخلات المستخدم والتفاعل معه
if prompt := st.chat_input("اكتب سؤالك أو مهمتك هنا..."):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # معالجة الرد من الـ AI
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير وصياغة الرد..."):
            # بناء سياق الحوار مع الـ System Prompt
            formatted_messages = [{"role": "system", "content": system_prompts[agent_role]}]
            for msg in st.session_state.messages:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
            formatted_input = tokenizer.apply_chat_template(
                formatted_messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            outputs = pipe(
                formatted_input, 
                max_new_tokens=max_tokens, 
                do_sample=True, 
                temperature=temperature,
                repetition_penalty=1.2
            )
            
            full_text = outputs[0]["generated_text"]
            response_text = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
            
            st.markdown(response_text)
            
    # حفظ رد الـ AI في الذاكرة
    st.session_state.messages.append({"role": "assistant", "content": response_text})
