from flask import Flask, request
import requests
import os
import json
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECRET = os.environ.get("SECRET")
CHANNELS = json.loads(os.environ.get("CHANNELS", "{}"))

EMOJI_MAP = {
    "div_4h": "⏰",
    "div_5m": "⚡",
    "etc": "🔔",
    "sniper_bb": "🎯",
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
        stop = data.get("stop")  # 손절가
        leverage = data.get("leverage")  # 배율
        
        # 한국 시간 (KST = UTC+9)
        kst = timezone(timedelta(hours=9))
        kst_time = datetime.now(kst)
        
        # 메시지 구성
        message_parts = [
            f"{emoji} <b>{signal_type}</b>",
            f"━━━━━━━━━━━━━━",
            f"📌 종목: <code>{symbol}</code>",
            f"💰 진입: <code>{price}</code>"
        ]
        
        # 손절가와 배율이 있으면 추가
        if stop:
            message_parts.append(f"🛑 손절: <code>{stop}</code>")
        if leverage:
            message_parts.append(f"⚡ 배율: <code>{leverage}</code>")
        
        message_parts.append(f"🕐 {kst_time.strftime('%H:%M:%S')}")
        
        message = "\n".join(message_parts)
        
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
