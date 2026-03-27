import os
import telebot
from flask import Flask, request
from google import genai
from google.genai import types

# الإعدادات
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN, threaded=False)
client = genai.Client(api_key=API_KEY)
app = Flask(__name__)

user_sessions = {}

def get_ai_response(user_id, text_input):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(
                system_instruction="أنت مساعد ذكي وصديق لمحمد محبوب نصار، رد بالمصري."
            )
        )
    return user_sessions[user_id].send_message(text_input).text

# السطر ده هو اللي هيشغل البوت بناءً على الصورة (الرابط بالتوكن)
@app.route('/' + TOKEN, methods=['POST'])
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
