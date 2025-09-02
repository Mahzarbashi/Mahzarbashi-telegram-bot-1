from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import os
from gtts import gTTS
import requests
import json

# ==================== CONFIGURATION - TOKENS ====================
# توکن ربات شما - لطفا بعداً این توکن را عوض کنید!
TELEGRAM_BOT_TOKEN = "932785959:AAETBE4j1mFIJ4rT5oN28j0zPQkxQHQVUM0"
# کلید API OpenAI خود را اینجا قرار دهید
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
WEBSITE_URL = "https://mahzarbashi.ir"

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==================== AI ANSWER FUNCTION ====================
def get_ai_response(user_message):
    """
    این تابع سوال کاربر را به OpenAI می‌فرستد و پاسخ هوش مصنوعی را دریافت می‌کند.
    """
    try:
        system_prompt = f"""
        شما یک دستیار هوشمند و خودمونی وبسایت "محر بashi" به آدرس {WEBSITE_URL} هستید.
        شما به سوالات اولیه کاربران در زمینه حقوقی پاسخ می‌دهید.
        لحن پاسخ‌های شما باید دوستانه، صمیمی، قابل فهم برای عموم مردم و فاقد اصطلاحات بسیار پیچیده حقوقی باشد.
        در پایان هر پاسخ، اگر موضوع پیچیده است، کاربر را به وبسایت برای دریافت مشاوره تخصصی از وکلای ما راهنمایی کنید.
        پاسخ‌های شما کوتاه، مفید و بیش از ۱۵۰ کلمه نباشد.
        """

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
        return "متأسفم، در پردازش سوال شما مشکلی پیش آمد. لطفاً کمی بعد دوباره سعی کنید."

# ==================== TEXT TO SPEECH FUNCTION ====================
def generate_audio_from_text(text, filename="response.mp3"):
    """
    این تابع پاسخ متنی را گرفته و با استفاده از gTTS آن را به فایل صوتی تبدیل می‌کند.
    """
    try:
        tts = gTTS(text=text, lang='fa', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    welcome_text = (
        "سلام! 👋 به دستیار هوشمند محر بashi خوش آمدید.\n\n"
        "من اینجا هستم تا به سوالات اولیه حقوقی شما پاسخ دهم. "
        "مثلاً می‌تونید در مورد قراردادها، دعاوی ملکی، خانواده و... بپرسید.\n\n"
        "**برای دریافت مشاوره تخصصی و ارتباط با وکلای مجرب ما، می‌تونید به وبسایت مراجعه کنید:**\n"
        f"[{WEBSITE_URL}]({WEBSITE_URL})"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    help_text = (
        "شما فقط کافیه سوال حقوقی خودتون رو اینجا بنویسید. من سعی می‌کنم بهتون کمک کنم.\n\n"
        "من همچنین یک پاسخ صوتی هم براتون می‌فرستم تا راحت‌تر به جواب خودتون برسید.\n\n"
        "اگر سوال شما تخصصی باشد، حتماً شما رو به وکلای باتجربه ما در وبسایت معرفی می‌کنم."
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for all text messages that are not commands"""
    user_message = update.message.text
    user_id = update.effective_user.id

    await update.message.chat.send_action(action="typing")
    ai_response_text = get_ai_response(user_message)
    text_with_signoff = ai_response_text + f"\n\n---\n🤵 برای مشاوره تخصصی: {WEBSITE_URL}"
    await update.message.reply_text(text_with_signoff)

    await update.message.chat.send_action(action="record_voice")
    audio_filename = generate_audio_from_text(ai_response_text)

    if audio_filename:
        try:
            with open(audio_filename, 'rb
