import os
import telebot
from flask import Flask, request
from google import genai
from google.genai import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

user_sessions = {}

# دالة الذكاء الاصطناعي مع تعديل التعليمات ليكون "صديق أو مساعد دراسة"
def get_ai_response(user_id, text_input):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(
                system_instruction="""أنت مساعد ذكي وصديق مخلص، مطورك هو البشمهندس محمد محبوب نصار. 
                شخصيتك: ودود، بتفهم في الأصول، وبترد بالمصري العامية. 
                مهمتك: تساعد المستخدم في المذاكرة، تدردش معاه كأنه صاحبه، وتجاوب على أسئلته بذكاء وبساطة."""
            )
        )
    chat = user_sessions[user_id]
    response = chat.send_message(text_input)
    return response.text

# رسالة الترحيب الاحترافية عند الضغط على /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي الخاص بي! 👋\n\n"
        "أنا مساعدك الذكي، تقدر تعتبرني صاحبك اللي تدردش معاه في أي وقت، "
        "أو زميلك في المذاكرة اللي بيشرحلك أي حاجة صعبة. 📚✨\n\n"
        "✨ **عن المطور:**\n"
        "البشمهندس محمد محبوب نصار، متخصص في تقديم الخدمات التقنية والبرمجية.\n\n"
        "👇 تقدر تتواصل مع المطور مباشرة أو تشوف خدماته من الأزرار تحت او تقدر تكي مع البوت زي ما انت عاوز:"
    )
    
    # إنشاء أزرار التواصل
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("تليجرام ✈️", url="https://t.me/Mohamed_3m"), # استبدل YourUsername بيوزرك
        InlineKeyboardButton("واتساب 🟢", url="https://wa.me/201012289349"), # استبدل الرقم برقمك
        InlineKeyboardButton("جيميل 📧", url="mahaned9876j@gmail.com") # استبدل بالإيميل
    )
    
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

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
    bot.remove_webhook()
    return "Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
