import threading
import asyncio
from flask import Flask, jsonify, request
from content import get_content
from poster import post_to_telegram
from config import Config

app = Flask(__name__)

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

@app.route("/")
def index():
    return jsonify({"message": "Telegram Meme Bot running!"}), 200

@app.route("/post-now", methods=["GET", "POST"])
def post_now():
    api_key = request.args.get("api_key")
    if api_key != Config.API_KEY:
        return jsonify({"message": "Invalid or missing API key"}), 401
    
    type = request.args.get("type")
    content = get_content(type)
    
    if not content:
        return jsonify({"message": "No meme found"}), 200
    
    # Schedule coroutine safely on background event loop
    asyncio.run_coroutine_threadsafe(post_to_telegram(content), loop)
    
    return jsonify({"status": "queued", "type": content["type"]})

if __name__=="__main__":
    app.run(debug=True)