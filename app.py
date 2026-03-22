import os
from flask import Flask, render_template, request, jsonify
import openai
import telebot

app = Flask(__name__)

# Kalitlar
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

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

# --- VEBSAYT QISMI ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get("message")
    bot_reply = get_ai_response(user_message)
    return jsonify({"reply": bot_reply})

# --- TELEGRAM QISMI ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🌐 *NetGlobal AI* botiga xush kelibsiz!\nSavolingizni yozing.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = get_ai_response(message.text)
    bot.reply_to(message, reply)

if __name__ == "__main__":
    # Render porti uchun moslashuv
    port = int(os.environ.get("PORT", 5000))
    # Telegram botni alohida thread'da emas, oddiyroq usulda ishga tushiramiz
    import threading
    threading.Thread(target=lambda: bot.infinity_polling(non_stop=True)).start()
    app.run(host='0.0.0.0', port=port)
