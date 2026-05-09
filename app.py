from flask import Flask, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    api_key = data.get('api_key')
    query = data.get('query')
    
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
        
    # Standard text search using SerpApi
    params = {
      "engine": "google",
      "q": query,
      "api_key": api_key
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lens', methods=['POST'])
def lens_search():
    data = request.json
    api_key = data.get('api_key')
    image_url = data.get('image_url')
    
    if not api_key or not image_url:
        return jsonify({"error": "Missing api_key or image_url"}), 400
        
    params = {
      "engine": "google_lens",
      "url": image_url,
      "api_key": api_key
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
