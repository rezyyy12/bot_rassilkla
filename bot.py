import schedule
import telebot
import sqlite3
import time
import threading

TOKEN = "токен"  # из BotFather
ADMIN_ID = айди

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
db.commit()

user_states = {}

@bot.message_handler(commands=["start"])
def start(message):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (message.chat.id,))
    db.commit()
    bot.send_message(message.chat.id, "привет, тг the_rezyyy")

@bot.message_handler(commands=["broadcast"])
def broadcast_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    user_states[ADMIN_ID] = "waiting"
    bot.send_message(message.chat.id, "введи текст рассылки:")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and user_states.get(ADMIN_ID) == "waiting")
def get_broadcast_text(message):
    user_states.pop(ADMIN_ID, None)
    threading.Thread(target=send_broadcast, args=(message.text, message.chat.id)).start()
    bot.send_message(message.chat.id, "рассылка запущена...")

def send_broadcast(text, admin_id):
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    sent, failed = 0, 0
    for (user_id,) in users:
        try:
            bot.send_message(user_id, text)
            sent += 1
        except Exception as e:
            failed += 1
        time.sleep(0.05)
    bot.send_message(admin_id, f"готово. отправлено: {sent}, ошибок: {failed}")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# текст рассылки и время меняй здесь
schedule.every().day.at("10:00").do(send_broadcast, text="привет, это рассылка!", admin_id=ADMIN_ID)

threading.Thread(target=run_schedule).start()
bot.polling(none_stop=True)
