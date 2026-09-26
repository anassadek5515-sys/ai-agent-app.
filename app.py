# 2. تصميم CSS احترافي لإصلاح مربع الإدخال على الأندرويد
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

    /* فقاعات الرسائل */
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

    /* --- حل مشكلة أبيض على أبيض في مربع الإدخال --- */
    div[data-testid="stChatInput"] {
        background-color: #1E1E1E !important;
        border-radius: 25px !important;
    }

    .stChatInputContainer {
        background-color: #1E1E1E !important;
        border-radius: 25px !important;
        border: 1px solid #444444 !important;
    }

    .stChatInputContainer textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        -webkit-appearance: none !important;
        font-size: 16px !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
    }
    </style>
""", unsafe_allow_html=True)
