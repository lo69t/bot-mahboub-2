import os
import telebot
from flask import Flask, request
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# إعدادات التوكن
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

user_sessions = {}

def get_ai_response(user_id, text_input):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(
                system_instruction="انت مساعد ذكي ومطورك هو م. محمد محبوب نصار، رد بالمصري."
            )
        )
    chat = user_sessions[user_id]
    response = chat.send_message(text_input)
    return response.text

# الرابط اللي تليجرام هيبعت عليه الرسائل
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
    # هنا هنحط رابط الموقع بتاعك لما يشتغل
    return "Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
