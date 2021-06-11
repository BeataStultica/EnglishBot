import telebot
import os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.getenv('TELEGRAM_API'))
import psycopg2

con = psycopg2.connect(
  database=os.getenv('DB'),
  user=os.getenv('USER'),
  password=os.getenv('PASSWORD'),
  host=os.getenv('HOST'),
  port=os.getenv('PORT')
)
cur = con.cursor()

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Hello!")
    cur.execute("CALL CurrCommand(%i, '%s' )"%(message.chat.id, 'start'))
    con.commit()

@bot.message_handler(commands=['translate_en'])
def trans_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_en'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато переклад слів")
    bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")

@bot.message_handler(commands=['add_new'])
def start_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'add_new'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато додавання слів")
    bot.send_message(message.chat.id, "Введіть нове слово або словосполучення або іншу команду")

@bot.message_handler(content_types=['text'])
def add_word(message):
    cur.execute("SELECT * FROM Sessions WHERE Sessions.UserId=%i" % message.chat.id)
    com = cur.fetchall()[0][1]
    if com=='add_new':
        msg = bot.send_message(message.chat.id, 'Введіть переклад')
        bot.register_next_step_handler(msg, continue_add, message.text)
    elif com=='translate_en':
        cur.execute("SELECT * FROM Dictionaries WHERE UserId=%i AND word='%s'" % (message.chat.id, message.text))
        rows = cur.fetchall()
        for i in rows:
            bot.send_message(message.chat.id, "Переклад: " + i[2])
        if len(rows)==0:
            bot.send_message(message.chat.id, "Слово або словосполучення відсутнє в словнику")
        cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_en'))
        con.commit()
        bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")
def continue_add(message, word):
    cur.execute("INSERT INTO Dictionaries(UserId, word, translates) VALUES(%i, '%s', '%s')"%(message.chat.id, word, message.text))
    con.commit()
    bot.send_message(message.chat.id, 'Добавлено в словник: '+word + ', переклад: '+message.text)
    bot.send_message(message.chat.id, "Введіть нове слово або словосполучення або іншу команду")

bot.polling(none_stop=True, interval=0)
