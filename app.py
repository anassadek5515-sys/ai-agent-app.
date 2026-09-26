# 2. تصميم CSS احترافي متوافق 100% مع تطبيق الموبايل (WebView)
st.markdown("""
    <style>
    /* إجبار النظام على اعتماد النمط الداكن لمنع تداخل الألوان */
    :root {
        color-scheme: dark !important;
    }
    
    [data-testid="collapsedControl"], [data-testid="stSidebar"], #MainMenu, header, footer { display: none !important; }
    
    /* خلفية داكنة ثابتة ونصوص بيضاء صريحة */
    html, body, .stApp { 
        background-color: #121212 !important; 
        color: #FFFFFF !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* توحيد لون كل النصوص */
    p, span, div, h1, h2, h3, h4, label, li {
        color: #FFFFFF !important;
        direction: rtl;
        text-align: right;
    }

    /* فقاعة رسالة المستخدم */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #242526 !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
        margin: 8px 0 !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3B3C !important;
    }

    /* فقاعة رسالة الذكاء الاصطناعي */
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background-color: transparent !important;
        padding: 12px 10px !important;
        margin: 8px 0 !important;
        color: #FFFFFF !important;
    }

    /* مربع إدخال النص للأندرويد */
    .stChatInputContainer textarea {
        color: #FFFFFF !important;
        background-color: #242526 !important;
        -webkit-text-fill-color: #FFFFFF !important; /* خاص بمحرك أندرويد */
    }
    
    .stChatInputContainer {
        background-color: #242526 !important;
        border-radius: 25px !important;
        border: 1px solid #4E4F50 !important;
    }
    </style>
""", unsafe_allow_html=True)


