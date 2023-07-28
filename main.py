import threading
import time
import sqlite3
from telegram import Bot
import pandas as pd

import telegram.ext
from telegram.ext import Updater, Filters, MessageHandler

TOKEN = open("TOKEN.txt", "r").read()
bot = Bot(token=TOKEN)
conn = sqlite3.connect("database1.db", check_same_thread=False)
cursor = conn.cursor()



updater = Updater(TOKEN, use_context=True)
disp = updater.dispatcher

current_name = None
current_date = None


def start(update, context):
    update.message.reply_text("Hello World! /new to create new reminder! /addfile")
    global cursor
    user_id = update.message.chat_id

    cursor.execute("SELECT * FROM user WHERE id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (id) VALUES (?)", (user_id,))
    conn.commit()


def addfile(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="alomu alaykum! Faylni yuboring.")


def save_file(update, context):
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    file_path = context.bot.get_file(file_id).file_path

    # Faylni olish va saqlash
    context.bot.get_file(file_id).download(file_name)

    user_id = update.message.from_user.id

    df = pd.read_excel(file_path)

    for index, row in df.iterrows():
        cell_value_a = row['date']
        cell_value_b = row['name']

        print(cell_value_a, cell_value_b)
        print(user_id)


    # Ma'lumotlar bazasiga ulashish
        conn = sqlite3.connect("database1.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO birthday_reminder(date, name, reminder, user_id) VALUES (?, ?, ?, ?)",
                       (cell_value_a, cell_value_b, 0, user_id))
        conn.commit()
        conn.close()

        df = pd.read_excel(file_name)

        conn = sqlite3.connect('database.db')

        df.to_sql('birthday_reminder', conn, if_exists='replace', index=False)

        conn.close()


    context.bot.send_message(chat_id=update.effective_chat.id, text="Fayl saqlandi!")

def new_reminder(update, context):
    update.message.reply_text("Whose birthday shall I reminder you of?")
    return 1


def get_name(update, context):
    global current_name
    current_name = update.message.text
    update.message.reply_text("When is the birthday (Year-Month-Day)?")
    return 2


def get_date(update, context):
    global current_date
    global cursor

    current_date = update.message.text
    user_id = update.message.chat_id



    cursor.execute("INSERT INTO birthday_reminder (user_id, name, date, reminder) VALUES (?, ?, ?, ?)",
                   (user_id, current_name, current_date, 0))

    conn.commit()

    update.message.reply_text("I will remind you!")
    return telegram.ext.ConversationHandler.END


def cancel():
    pass


def do_reminder():
    while True:
        # today = dt.date.today().strftime("%Y-%m-%d")

        cursor.execute("SELECT * FROM birthday_reminder WHERE strftime('%d', date) = strftime('%d', 'now')"
                       "AND strftime('%m', date) = strftime('%m', 'now') AND reminder = 0")

        rows = cursor.fetchall()
        for row in rows:
            row_id = row[0]
            name = row[2]
            user_id = row[4]
            cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
            for user in users:
                user_id = user[0]
                updater.bot.send_message(chat_id=user_id, text=f"It's {name}'s birthday today!")
                cursor.execute("UPDATE birthday_reminder SET reminder = 1 WHERE id = ?", (row_id,))
            conn.commit()

        time.sleep(10)

conv_handler = telegram.ext.ConversationHandler(
    entry_points=[telegram.ext.CommandHandler("new", new_reminder)],
    states={
        1: [telegram.ext.MessageHandler(telegram.ext.Filters.text, get_name)],
        2: [telegram.ext.MessageHandler(telegram.ext.Filters.text, get_date)]
    },
    fallbacks=[telegram.ext.CommandHandler("cancel", cancel)]
)

disp.add_handler(telegram.ext.CommandHandler("start", start))
disp.add_handler(telegram.ext.CommandHandler("addfile", addfile))

updater.dispatcher.add_handler(MessageHandler(Filters.document, save_file))
disp.add_handler(conv_handler)

threading.Thread(target=do_reminder).start()

updater.start_polling()
updater.idle()

