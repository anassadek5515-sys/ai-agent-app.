import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

st.set_page_config(page_title="AI Agent App", page_icon="🤖")
st.title("🤖 مشروع الـ AI Agent المستقل")
st.write("أهلاً بك! اكتب مهمتك للـ AI Agent ليقوم بتفكيكها وتحليلها:")

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

user_input = st.text_input("المهمة المطلوبة:", placeholder="مثال: كيف أبني خطة تسويق لمنتجي؟")

if st.button("تشغيل الـ Agent 🚀"):
    if user_input:
        with st.spinner("جاري التفكير وتحليل المهمة..."):
            agent_system_prompt = "أنت عميل ذكاء اصطناعي مستقل (AI Agent). مهمتك تفكيك المشكلة التقنية إلى خطوات تنفيذية عملية. أجب باللغة العربية فقط."
            messages = [
                {"role": "system", "content": agent_system_prompt},
                {"role": "user", "content": f"المهمة المطلوبة: {user_input}"}
            ]
            formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            out = pipe(formatted, max_new_tokens=250, do_sample=True, temperature=0.3, repetition_penalty=1.2)
            
            full_text = out[0]["generated_text"]
            response = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "")
            
            st.success("تم استخراج خطة العمل بنجاح:")
            st.markdown(response)
    else:
        st.warning("يرجى كتابة سؤال أو مهمة أولاً!")
