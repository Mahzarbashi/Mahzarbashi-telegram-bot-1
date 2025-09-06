from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import os
from gtts import gTTS

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
WEBSITE_URL = "https://mahzarbashi.ir"

# بررسی وجود توکن‌ها
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("لطفاً توکن‌ها را در Environment Variables تنظیم کنید")

print("✅ توکن‌ها با موفقیت بارگذاری شدند")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==================== AI ANSWER FUNCTION ====================
def get_ai_response(user_message):
    try:
        system_prompt = f"""شما یک دستیار هوشمند وبسایت "محر بashi" هستید."""
        
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
    await update.message.reply_text("سلام! به ربات خوش آمدید.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("راهنما: سوالات خود را بپرسید.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    ai_response_text = get_ai_response(user_message)
    
    text_with_signoff = ai_response_text + f"\n\n---\n🤵 برای مشاوره تخصصی: {WEBSITE_URL}"
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
    
    # ایجاد برنامه با استفاده از Builder pattern
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # اضافه کردن handlerها
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات شروع به کار کرد")
    
    # شروع轮询
    application.run_polling()

if __name__ == '__main__':
    main()
