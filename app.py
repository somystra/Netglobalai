import os
import threading
from flask import Flask, render_template, request, jsonify
import openai
import telebot

# Flask ilovasini yaratish
app = Flask(__name__)

# Kalitlarni Render "Environment Variables"dan oladi
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# API mijozlarini sozlash
client = openai.OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_ai_response(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Siz NetGlobal AI yordamchisiz. Yaratuvchilaringiz: Solijon Muhammadkarimov, Ulug'bek Shuxratullayev va Dilmurod Abduvaxobov."},
                {"role": "user", "content": user_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

# --- VEBSAYT YO'LLARI ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_message = data.get("message")
        bot_reply = get_ai_response(user_message)
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": "Xatolik yuz berdi."}), 500

# --- TELEGRAM BOT LOGIKASI ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🌐 *NetGlobal AI* botiga xush kelibsiz!\nSavolingizni yozing.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = get_ai_response(message.text)
    bot.reply_to(message, reply)

# Telegram botni alohida oqimda ishga tushirish funksiyasi
def run_bot():
    bot.infinity_polling(non_stop=True)

if __name__ == "__main__":
    # 1. Botni alohida oqimda boshlash
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # 2. Flask veb-serverni Render portida ishga tushirish
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
