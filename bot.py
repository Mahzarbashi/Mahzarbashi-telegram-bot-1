import os
import sys
import requests
import json
from gtts import gTTS
import time
from flask import Flask, request

app = Flask(__name__)

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
WEBSITE_URL = "https://mahzarbashi.ir"

# بررسی وجود توکن‌ها
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    print("لطفاً توکن‌ها را در Environment Variables تنظیم کنید")
    sys.exit(1)

print("✅ توکن‌ها با موفقیت بارگذاری شدند")

# ==================== AI ANSWER FUNCTION ====================
def get_ai_response(user_message):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": f"شما یک دستیار هوشمند وبسایت 'محر بashi' به آدرس {WEBSITE_URL} هستید. به سوالات حقوقی پاسخ می‌دهید. پاسخ‌های شما باید دوستانه و مفید باشد."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI API Error: {response.status_code}, {response.text}")
            return "متأسفم، در پردازش سوال شما مشکلی پیش آمد."
            
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "متأسفم، در پردازش سوال شما مشکلی پیش آمد."

# ==================== TEXT TO SPEECH FUNCTION ====================
def generate_audio_from_text(text, filename="response.mp3"):
    try:
        tts = gTTS(text=text, lang='fa', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# ==================== TELEGRAM API FUNCTIONS ====================
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response.json()

def send_telegram_voice(chat_id, audio_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice"
    with open(audio_path, 'rb') as audio_file:
        files = {'voice': audio_file}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(url, files=files, data=data)
    return response.json()

def send_typing_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    data = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, data=data)

def send_recording_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    data = {"chat_id": chat_id, "action": "record_voice"}
    requests.post(url, data=data)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

# ==================== MESSAGE PROCESSING ====================
def process_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    
    if text.startswith("/start"):
        welcome_text = (
            "سلام! 👋 به دستیار هوشمند محر بashi خوش آمدید.\n\n"
            "من اینجا هستم تا به سوالات اولیه حقوقی شما پاسخ دهم.\n\n"
            f"برای دریافت مشاوره تخصصی: {WEBSITE_URL}"
        )
        send_telegram_message(chat_id, welcome_text)
        
    elif text.startswith("/help"):
        help_text = "شما فقط کافیه سوال حقوقی خودتون رو اینجا بنویسید. من سعی می‌کنم بهتون کمک کنم."
        send_telegram_message(chat_id, help_text)
        
    elif text:
        # نشان دادن عمل تایپ
        send_typing_action(chat_id)
        
        # دریافت پاسخ از هوش مصنوعی
        ai_response = get_ai_response(text)
        response_with_footer = f"{ai_response}\n\n---\nبرای مشاوره تخصصی: {WEBSITE_URL}"
        
        # ارسال پاسخ متنی
        send_telegram_message(chat_id, response_with_footer)
        
        # نشان دادن عمل ضبط صدا
        send_recording_action(chat_id)
        
        # تولید و ارسال پاسخ صوتی
        audio_filename = generate_audio_from_text(ai_response)
        if audio_filename:
            try:
                send_telegram_voice(chat_id, audio_filename, "پاسخ صوتی 🎧")
            except Exception as e:
                print(f"Error sending audio: {e}")
            finally:
                # حذف فایل موقت
                if os.path.exists(audio_filename):
                    os.remove(audio_filename)

# ==================== FLASK ROUTES FOR WEBHOOK ====================
@app.route('/')
def index():
    return "ربات محر بashi در حال اجراست!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        process_message(data["message"])
    return "OK"

# ==================== POLLING MODE ====================
def polling_mode():
    print("Starting bot in polling mode...")
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        process_message(update["message"])
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error in polling: {e}")
            time.sleep(5)

# ==================== MAIN FUNCTION ====================
if __name__ == '__main__':
    # استفاده از polling mode (مناسب برای Render)
    polling_mode()
    
    # اگر می‌خواهید از webhook استفاده کنید، خط زیر را فعال کنید
    # app.run(host='0.0.0.0', port=5000)
