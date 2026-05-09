"""
IRIS — Image Research Intelligence System
Standalone server — serves index.html directly (no iframe sandboxing).

Run:
  pip install -r requirements.txt
  python app.py          # runs on http://localhost:5000
  python app.py 8501     # custom port

Or with Streamlit (legacy):
  streamlit run app_streamlit.py
"""
import os, json
from flask import Flask, send_file, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

_script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Build JS prefill from .env so the browser auto-fills API key fields ──
def get_prefill_keys():
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


@app.route('/')
def index():
    html_path = os.path.join(_script_dir, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Inject prefill keys from .env
    prefill = get_prefill_keys()
    inject = f'<script>\nwindow.IRIS_PREFILL = {json.dumps(prefill)};\n</script>'
    html = html.replace('</head>', inject + '\n</head>', 1)

    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


# ── Optional server-side SerpAPI proxy (avoids CORS issues entirely) ──
@app.route('/api/serpapi-lens')
def serpapi_proxy():
    image_url = request.args.get('url', '')
    api_key = os.getenv('SERPAPI_KEY', request.args.get('key', ''))
    if not api_key:
        return jsonify({'error': 'No SerpAPI key configured'}), 400
    import urllib.request
    target = f'https://serpapi.com/search?engine=google_lens&url={urllib.parse.quote(image_url)}&api_key={api_key}'
    try:
        import urllib.parse
        target = f'https://serpapi.com/search?engine=google_lens&url={urllib.parse.quote(image_url)}&api_key={api_key}'
        with urllib.request.urlopen(target, timeout=15) as r:
            data = r.read()
        return data, 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        return jsonify({'error': str(e)}), 502


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f'\n🔬 IRIS starting on http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)
