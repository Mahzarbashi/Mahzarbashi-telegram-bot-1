from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
        system_prompt = """شما یک دستیار هوشمند وبسایت "محر بashi" هستید. به سوالات حقوقی پاسخ می‌دهید."""
        
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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋 به دستیار هوشمند محر بashi خوش آمدید.\n\n"
        "من اینجا هستم تا به سوالات اولیه حقوقی شما پاسخ دهم.\n\n"
        f"برای دریافت مشاوره تخصصی: {WEBSITE_URL}"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "شما فقط کافیه سوال حقوقی خودتون رو اینجا بنویسید. من سعی می‌کنم بهتون کمک کنم."
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    ai_response_text = get_ai_response(user_message)
    
    text_with_signoff = ai_response_text + f"\n\n---\nبرای مشاوره تخصصی: {WEBSITE_URL}"
    await update.message.reply_text(text_with_signoff)
    
    await update.message.chat.send_action(action="record_voice")
    audio_filename = generate_audio_from_text(ai_response_text)
    
    if audio_filename:
        try:
            with open(audio_filename, 'rb') as audio_file:
                await update.message.reply_voice(voice=audio_file, caption="پاسخ صوتی")
        except Exception as e:
            print(f"Error sending audio: {e}")
        finally:
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

# ==================== MAIN FUNCTION ====================
def main():
    print("Starting Mahzar Assistant Bot...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات شروع به کار کرد")
    application.run_polling()

if __name__ == '__main__':
    main()
