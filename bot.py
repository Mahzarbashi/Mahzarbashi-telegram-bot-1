from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai import OpenAI
import os
from gtts import gTTS
import sys

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
WEBSITE_URL = "https://mahzarbashi.ir"

# بررسی وجود توکن‌ها
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    print("لطفاً توکن‌ها را در Environment Variables تنظیم کنید")
    sys.exit(1)

print("✅ توکن‌ها با موفقیت بارگذاری شدند")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==================== AI ANSWER FUNCTION ====================
def get_ai_response(user_message):
    try:
        system_prompt = f"""شما یک دستیار هوشمند وبسایت "محر بashi" هستید. به سوالات حقوقی پاسخ می‌دهید."""
        
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return completion.choices[0].message.content
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

# ==================== TELEGRAM BOT HANDLERS ====================
def start_command(update: Update, context: CallbackContext):
    welcome_text = (
        "سلام! 👋 به دستیار هوشمند محر بashi خوش آمدید.\n\n"
        "من اینجا هستم تا به سوالات اولیه حقوقی شما پاسخ دهم.\n\n"
        f"برای دریافت مشاوره تخصصی: {WEBSITE_URL}"
    )
    update.message.reply_text(welcome_text)

def help_command(update: Update, context: CallbackContext):
    help_text = "شما فقط کافیه سوال حقوقی خودتون رو اینجا بنویسید. من سعی می‌کنم بهتون کمک کنم."
    update.message.reply_text(help_text)

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    
    # شبیه‌سازی عمل تایپ کردن
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_response_text = get_ai_response(user_message)
    
    text_with_signoff = ai_response_text + f"\n\n---\nبرای مشاوره تخصصی: {WEBSITE_URL}"
    update.message.reply_text(text_with_signoff)
    
    # شبیه‌سازی عمل ضبط صدا
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
    
    audio_filename = generate_audio_from_text(ai_response_text)
    
    if audio_filename:
        try:
            with open(audio_filename, 'rb') as audio_file:
                update.message.reply_voice(voice=audio_file, caption="پاسخ صوتی")
        except Exception as e:
            print(f"Error sending audio: {e}")
        finally:
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

# ==================== MAIN FUNCTION ====================
def main():
    print("Starting Mahzar Assistant Bot...")
    
    # استفاده از Updater به جای Application (سازگارتر با نسخه‌های مختلف)
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    
    # گرفتن dispatcher برای ثبت handlerها
    dp = updater.dispatcher
    
    # اضافه کردن handlerها
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("✅ ربات شروع به کار کرد")
    
    # شروع轮询
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
