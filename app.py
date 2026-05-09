"""
IRIS — Image Research Intelligence System
Streamlit Cloud deployment via st.iframe() + static file serving.

Streamlit serves files in the ./static/ folder at /app/static/<filename>
This gives a real src= iframe with no srcdoc sandbox restrictions.
All buttons, JS, and fetch() calls work natively.

Run locally:  streamlit run app.py
Deploy:       Push to GitHub → connect to share.streamlit.io
"""
import os, json, shutil
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="IRIS – Image Research Intelligence System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide Streamlit chrome completely ─────────────────────────
st.markdown("""<style>
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] { display:none!important; }
.block-container { padding:0!important; margin:0!important; max-width:100%!important; }
</style>""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────
_dir      = os.path.dirname(os.path.abspath(__file__))
_html_src = os.path.join(_dir, "index.html")
_static   = os.path.join(_dir, "static")          # served at /app/static/
_html_dst = os.path.join(_static, "iris.html")    # → /app/static/iris.html

# ── Read .env keys for browser prefill ───────────────────────
def _prefill():
    keys = {
        "gemini":          os.getenv("GEMINI_API_KEY", ""),
        "groq":            os.getenv("GROQ_API_KEY", ""),
        "openrouter":      os.getenv("OPENROUTER_API_KEY", ""),
        "serpapi":         os.getenv("SERPAPI_KEY", ""),
        "imgbb":           os.getenv("IMGBB_KEY", ""),
        "supabaseUrl":     os.getenv("SUPABASE_URL", ""),
        "supabaseKey":     os.getenv("SUPABASE_KEY", ""),
        "emailjs":         os.getenv("EMAILJS_PUBLIC_KEY", ""),
        "emailjsService":  os.getenv("EMAILJS_SERVICE_ID", ""),
        "emailjsTemplate": os.getenv("EMAILJS_TEMPLATE_ID", ""),
        "telegramToken":   os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegramChatId":  os.getenv("TELEGRAM_CHAT_ID", ""),
        "huggingface":     os.getenv("HUGGINGFACE_API_KEY", ""),
        "ocrspace":        os.getenv("OCRSPACE_API_KEY", ""),
        "unsplash":        os.getenv("UNSPLASH_API_KEY", ""),
        "clarifai":        os.getenv("CLARIFAI_PAT", ""),
        "deepl":           os.getenv("DEEPL_API_KEY", ""),
        "jsonbin":         os.getenv("JSONBIN_MASTER_KEY", ""),
    }
    return {k: v for k, v in keys.items() if v}

# ── Build and copy HTML into ./static/ (cached, runs once) ───
@st.cache_resource
def _build_static():
    os.makedirs(_static, exist_ok=True)
    with open(_html_src, "r", encoding="utf-8") as f:
        html = f.read()
    prefill = _prefill()
    inject  = f"<script>\nwindow.IRIS_PREFILL = {json.dumps(prefill)};\n</script>"
    html    = html.replace("</head>", inject + "\n</head>", 1)
    with open(_html_dst, "w", encoding="utf-8") as f:
        f.write(html)
    return True

_build_static()

# ── Render — real src= iframe, zero sandbox restrictions ─────
# /app/static/iris.html is served by Streamlit's built-in static file server
st.components.v1.iframe("/app/static/iris.html", height=900, scrolling=True)
