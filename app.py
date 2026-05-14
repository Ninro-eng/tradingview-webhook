from flask import Flask, request
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECRET = os.environ.get("SECRET")
CHANNELS = json.loads(os.environ.get("CHANNELS", "{}"))

EMOJI_MAP = {
    "div_4h": "⏰",
    "div_5m": "⚡",
    "etc": "🔔",
}

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Content-Type에 관계없이 JSON 파싱 시도
        if request.is_json:
            data = request.json
        else:
            data = request.get_json(force=True)
        
        if data.get("secret") != SECRET:
            return "Unauthorized", 401
        
        channel_key = data.get("channel", "etc")
        target_chat = CHANNELS.get(channel_key)
        
        if not target_chat:
            return "Channel not found", 400
        
        emoji = EMOJI_MAP.get(channel_key, "🔔")
        signal_type = data.get("type", "신호 발생")
        symbol = data.get("symbol", "Unknown")
        price = data.get("price", "-")
        
        message = (
            f"{emoji} <b>{signal_type}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📌 종목: <code>{symbol}</code>\n"
            f"💰 가격: <code>{price}</code>\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}"
        )
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=5)
        
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
            return "Telegram error", 500
        
        return "OK", 200
    
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}", 500

@app.route("/")
def home():
    return "Server is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
