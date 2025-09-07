import os
import sys
import requests
from gtts import gTTS

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
                {"role": "system", "content": "شما یک دستیار هوشمند وبسایت محر بashi هستید."},
                {"role": "user", "content": user_message}
            ]
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        return response.json()["choices"][0]["message"]["content"]
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

# ==================== TELEGRAM BOT FUNCTIONS ====================
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)
    return response.json()

def send_telegram_voice(chat_id, audio_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice"
    with open(audio_path, 'rb') as audio_file:
        files = {'voice': audio_file}
        data = {'chat_id': chat_id}
        response = requests.post(url, files=files, data=data)
    return response.json()

# ==================== MAIN FUNCTION ====================
def main():
    print("Starting Mahzar Assistant Bot...")
    print("این یک نسخه ساده‌تر از ربات است که از APIهای مستقیم استفاده می‌کند")
    
    # در اینجا می‌توانید منطق轮询 برای دریافت پیام‌های جدید را اضافه کنید
    # برای ساده‌سازی، این نسخه فقط نشان می‌دهد که توکن‌ها کار می‌کنند
    
    print("✅ ربات آماده به کار است")

if __name__ == '__main__':
    main()
