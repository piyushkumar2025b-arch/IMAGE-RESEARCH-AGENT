from dotenv import load_dotenv
import os
import json

load_dotenv()

import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page
st.set_page_config(
    page_title="IRIS - Image Research Intelligence System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default UI elements
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 0rem;
                padding-right: 0rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ── Read the HTML file ───────────────────────────────────────
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# ── Inject .env keys as JS prefill so the user doesn't have
#    to type them manually in the browser ────────────────────
prefill_keys = {
    "gemini":           os.getenv("GEMINI_API_KEY", ""),
    "groq":             os.getenv("GROQ_API_KEY", ""),
    "openrouter":       os.getenv("OPENROUTER_API_KEY", ""),
    "serpapi":          os.getenv("SERPAPI_KEY", ""),
    "imgbb":            os.getenv("IMGBB_KEY", ""),
    "supabaseUrl":      os.getenv("SUPABASE_URL", ""),
    "supabaseKey":      os.getenv("SUPABASE_KEY", ""),
    "emailjs":          os.getenv("EMAILJS_PUBLIC_KEY", ""),
    "emailjsService":   os.getenv("EMAILJS_SERVICE_ID", ""),
    "emailjsTemplate":  os.getenv("EMAILJS_TEMPLATE_ID", ""),
    "telegramToken":    os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegramChatId":   os.getenv("TELEGRAM_CHAT_ID", ""),
    "huggingface":      os.getenv("HUGGINGFACE_API_KEY", ""),
    "ocrspace":         os.getenv("OCRSPACE_API_KEY", ""),
    "unsplash":         os.getenv("UNSPLASH_API_KEY", ""),
    "clarifai":         os.getenv("CLARIFAI_PAT", ""),
    "deepl":            os.getenv("DEEPL_API_KEY", ""),
    "jsonbin":          os.getenv("JSONBIN_MASTER_KEY", ""),
}

# Only include keys that are actually set in .env
prefill_keys = {k: v for k, v in prefill_keys.items() if v}

inject_script = f"""<script>
// Injected by app.py from .env — auto-fills API key fields on load
window.IRIS_PREFILL = {json.dumps(prefill_keys)};
</script>"""

# Insert just before </head>
html_content = html_content.replace("</head>", inject_script + "\n</head>")

# ── Optional: SerpAPI server-side proxy ─────────────────────
# If you want to avoid the CORS proxy entirely, you can route
# SerpAPI calls through Python. To enable this, set
# SERPAPI_PROXY_ENABLED=true in your .env.
# The JS already handles the direct call with corsproxy.io as
# a fallback — this is just an extra option for reliability.

# ── Render the HTML application ─────────────────────────────
components.html(html_content, height=1200, scrolling=True)
