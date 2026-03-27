import os
import telebot
from flask import Flask, request
from google import genai
from google.genai import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات التوكن (مباشرة من Vercel)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

user_sessions = {}

def get_ai_response(user_id, text_input):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(
                # هنا بنعرف البوت بشخصيته الجديدة (صديق ومساعد دراسة)
                system_instruction="أنت مساعد ذكي وصديق مخلص، مطورك هو م. محمد محبوب نصار. ردك يكون بالمصري العامية، خليك ودود جداً، ساعد المستخدم في المذاكرة أو الدردشة كأنك صاحبه."
            )
        )
    chat = user_sessions[user_id]
    response = chat.send_message(text_input)
    return response.text

# رسالة الترحيب بالأزرار (بدون تغيير في المسارات)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name}! 👋\n\n"
        "أنا مساعدك الذكي وصديقك.. تقدر تدردش معايا في أي حاجة أو نذاكر سوا. 📚✨\n\n"
        "✨ **عن المطور وخدماته:**\n"
        "م. محمد محبوب نصار، متخصص في تقديم الحلول التقنية والبرمجية.\n\n"
        "للتواصل مع المطور مباشرة 👇"
    )
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("تليجرام ✈️", url="https://t.me/Mohamed_3m"),
        InlineKeyboardButton("واتساب 🟢", url="https://wa.me/201012289349"), # تأكد من رقمك هنا
        InlineKeyboardButton("جيميل 📧", url="mailto:your-email@gmail.com")
    )
    
    bot.reply_to(message, welcome_text, reply_markup=markup)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        reply = get_ai_response(message.from_user.id, message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")

@app.route("/")
def webhook():
    return "Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
