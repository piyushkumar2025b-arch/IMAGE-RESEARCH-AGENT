"""
IRIS — Image Research Intelligence System
Fixed Streamlit deployment.

THE ORIGINAL PROBLEM:
    st.components.v1.iframe("/app/static/iris.html") doesn't work on
    Streamlit Community Cloud — the /app/static/ route is NOT publicly
    served.  The iframe loads a blank page, so nothing works.

THE FIX:
    Read index.html, inject the API-key prefill script, then render it
    with st.components.v1.html() which embeds the HTML directly in the
    page inside a sandboxed iframe that Streamlit itself creates.
    This works on both local dev and Streamlit Community Cloud.

KEY MANAGEMENT (two sources, merged):
    1. Local dev:  .env file  (python-dotenv)
    2. Cloud:      Streamlit Secrets  (st.secrets)
       → add keys to .streamlit/secrets.toml or the Secrets panel on
         share.streamlit.io — keys from BOTH sources are merged.

Run locally:  streamlit run app.py
Deploy:       Push to GitHub → connect to share.streamlit.io
              Add your secrets in the app's Secrets panel.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

# ── Load .env for local development ───────────────────────────
load_dotenv()

st.set_page_config(
    page_title="IRIS – Image Research Intelligence System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide all Streamlit chrome so IRIS fills the page ──────────
st.markdown("""
<style>
  /* Hide toolbar, footer, header, deploy button */
  #MainMenu, footer, header,
  .stDeployButton,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] {
    display: none !important;
  }
  /* Remove all padding so iframe fills the viewport */
  .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
  }
  /* Streamlit wraps components in a div with padding */
  [data-testid="stVerticalBlock"] > div:first-child {
    padding: 0 !important;
  }
  section[data-testid="stMain"] > div {
    padding-top: 0 !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Collect API keys: .env first, then st.secrets override ────
def get_prefill() -> dict:
    """
    Merge keys from .env (local dev) and st.secrets (Cloud).
    st.secrets values take priority so Cloud deployments work without
    committing any .env file.
    """
    # Map: prefill_key → (env_var_name, secrets_key)
    KEY_MAP = {
        "gemini":          ("GEMINI_API_KEY",       "GEMINI_API_KEY"),
        "groq":            ("GROQ_API_KEY",          "GROQ_API_KEY"),
        "openrouter":      ("OPENROUTER_API_KEY",    "OPENROUTER_API_KEY"),
        "serpapi":         ("SERPAPI_KEY",            "SERPAPI_KEY"),
        "imgbb":           ("IMGBB_KEY",              "IMGBB_KEY"),
        "supabaseUrl":     ("SUPABASE_URL",           "SUPABASE_URL"),
        "supabaseKey":     ("SUPABASE_KEY",           "SUPABASE_KEY"),
        "emailjs":         ("EMAILJS_PUBLIC_KEY",     "EMAILJS_PUBLIC_KEY"),
        "emailjsService":  ("EMAILJS_SERVICE_ID",     "EMAILJS_SERVICE_ID"),
        "emailjsTemplate": ("EMAILJS_TEMPLATE_ID",    "EMAILJS_TEMPLATE_ID"),
        "telegramToken":   ("TELEGRAM_BOT_TOKEN",     "TELEGRAM_BOT_TOKEN"),
        "telegramChatId":  ("TELEGRAM_CHAT_ID",       "TELEGRAM_CHAT_ID"),
        "huggingface":     ("HUGGINGFACE_API_KEY",    "HUGGINGFACE_API_KEY"),
        "ocrspace":        ("OCRSPACE_API_KEY",       "OCRSPACE_API_KEY"),
        "unsplash":        ("UNSPLASH_API_KEY",       "UNSPLASH_API_KEY"),
        "clarifai":        ("CLARIFAI_PAT",           "CLARIFAI_PAT"),
        "deepl":           ("DEEPL_API_KEY",          "DEEPL_API_KEY"),
        "jsonbin":         ("JSONBIN_MASTER_KEY",     "JSONBIN_MASTER_KEY"),
    }

    result: dict = {}

    # 1. Pull from environment (.env already loaded by dotenv)
    for prefill_key, (env_name, _) in KEY_MAP.items():
        val = os.getenv(env_name, "")
        if val:
            result[prefill_key] = val

    # 2. Override / add from st.secrets (works on Streamlit Cloud)
    try:
        for prefill_key, (_, secret_name) in KEY_MAP.items():
            val = st.secrets.get(secret_name, "")
            if val:
                result[prefill_key] = val
    except Exception:
        # st.secrets throws if secrets.toml doesn't exist locally — ignore
        pass

    return result


# ── Read and prepare index.html ────────────────────────────────
@st.cache_resource
def load_html() -> str:
    """
    Read index.html from the same directory as app.py, inject the
    IRIS_PREFILL script, and return the complete HTML string.
    Cached so the file is only read once per server start.
    """
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        st.error(
            "❌ `index.html` not found next to `app.py`. "
            "Make sure both files are in the same folder."
        )
        st.stop()
    return html_path.read_text(encoding="utf-8")


def build_html() -> str:
    """Inject current prefill keys into the HTML (re-runs each request)."""
    html = load_html()
    prefill = get_prefill()

    # Inject before </head> so it's available when DOMContentLoaded fires
    inject = (
        "<script>\n"
        f"window.IRIS_PREFILL = {json.dumps(prefill)};\n"
        "</script>"
    )
    return html.replace("</head>", inject + "\n</head>", 1)


# ── Render ─────────────────────────────────────────────────────
# st.components.v1.html() works on local + Streamlit Cloud.
# height is set tall; scrolling=True lets the user scroll inside.
st.components.v1.html(
    build_html(),
    height=960,
    scrolling=True,
)
