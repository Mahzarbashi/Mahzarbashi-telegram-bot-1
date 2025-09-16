import os
from flask import Flask, request
import telegram
import io
from gtts import gTTS
from responses import responses, CONTACT_URL

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text

        if text == "/start":
            reply = "سلام 👋 خوش اومدی به ربات محضرباشی ✅"
            bot.sendMessage(chat_id=chat_id, text=reply)
        else:
            # بررسی پاسخ
            reply = responses.get(text)
            if reply:
                # ارسال متن
                bot.sendMessage(chat_id=chat_id, text=reply)
                # تبدیل به صوت و ارسال
                tts = gTTS(reply, lang='fa')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                bot.sendAudio(chat_id=chat_id, audio=audio_fp, filename="response.mp3")
            else:
                # سوال تخصصی → هدایت به سایت
                reply = f"این سوال تخصصی است. لطفاً برای دریافت مشاوره کامل به لینک زیر مراجعه کنید:\n{CONTACT_URL}"
                bot.sendMessage(chat_id=chat_id, text=reply)

    return "ok"

@app.route("/")
def home():
    return "Mahzarbashi Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
