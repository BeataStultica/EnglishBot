import telebot
import os
from dotenv import load_dotenv
#from googletrans import Translator
from google_trans_new import google_translator
import psycopg2


load_dotenv()
bot = telebot.TeleBot(os.getenv('TELEGRAM_API'))

#translator = Translator()
translator =google_translator()
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
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/translate_en', '/translate_ua')
    keyboard.row('/add_new', '/add_new_en', '/add_new_ua')
    bot.send_message(message.chat.id, "Hello!", reply_markup=keyboard)
    cur.execute("CALL CurrCommand(%i, '%s' )"%(message.chat.id, 'start'))
    con.commit()


@bot.message_handler(commands=['translate_en'])
def trans_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_en'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато переклад з англійської слів зі словника")
    bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")
@bot.message_handler(commands=['translate_ua'])
def trans_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_ua'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато переклад з української слів зі словника")
    bot.send_message(message.chat.id, "Введіть  слово або словосполучення на українській або іншу команду")

@bot.message_handler(commands=['add_new_en'])
def auto_trans_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'add_new_en'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато переклад слів з англійської та додавання в словник")
    bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")
@bot.message_handler(commands=['add_new_ua'])
def auto_trans_command(message):
    cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'add_new_ua'))
    con.commit()
    bot.send_message(message.chat.id, "Розпочато переклад слів з української та додавання в словник")
    bot.send_message(message.chat.id, "Введіть  слово або словосполучення на українській або іншу команду")


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
        cur.execute("SELECT * FROM Dictionaries WHERE UserId=%i AND word='%s'" % (message.chat.id, message.text.strip()))
        rows = cur.fetchall()
        for i in rows:
            bot.send_message(message.chat.id, "Переклад: " + i[2])
        if len(rows)==0:
            bot.send_message(message.chat.id, "Слово або словосполучення відсутнє в словнику")
        #cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_en'))
        #con.commit()
        bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")

    elif com=='translate_ua':
        cur.execute("SELECT * FROM Dictionaries WHERE UserId=%i AND translates='%s'" % (message.chat.id, message.text.strip()))
        rows = cur.fetchall()
        for i in rows:
            bot.send_message(message.chat.id, "Переклад: " + i[1])
        if len(rows)==0:
            bot.send_message(message.chat.id, "Слово або словосполучення відсутнє в словнику")
        #cur.execute("CALL CurrCommand(%i, '%s' )" % (message.chat.id, 'translate_ua'))
        #con.commit()
        bot.send_message(message.chat.id, "Введіть  слово або словосполучення на англійській або іншу команду")
    elif com=='add_new_en':
        translates = translator.translate(message.text, lang_src='en', lang_tgt='uk').strip()
        cur.execute("INSERT INTO Dictionaries(UserId, word, translates) VALUES(%i, '%s', '%s')" % (
        message.chat.id, message.text.strip(), translates))
        con.commit()
        bot.send_message(message.chat.id, 'Добавлено в словник: ' + message.text + ', переклад: ' + translates)
        bot.send_message(message.chat.id, "Введіть нове слово або словосполучення або іншу команду")
    elif com=='add_new_ua':
        translates = translator.translate(message.text, lang_src='uk', lang_tgt='en').strip()
        cur.execute("INSERT INTO Dictionaries(UserId, word, translates) VALUES(%i, '%s', '%s')" % (
        message.chat.id, translates, message.text.strip()))
        con.commit()
        bot.send_message(message.chat.id, 'Добавлено в словник: ' + message.text + ', переклад: ' + translates)
        bot.send_message(message.chat.id, "Введіть нове слово або словосполучення або іншу команду")
def continue_add(message, word):
    if message.text[0] != '/':
        cur.execute("INSERT INTO Dictionaries(UserId, word, translates) VALUES(%i, '%s', '%s')"%(message.chat.id, word.strip(), message.text.strip()))
        con.commit()
        bot.send_message(message.chat.id, 'Добавлено в словник: '+word + ', переклад: '+message.text)
        bot.send_message(message.chat.id, "Введіть нове слово або словосполучення або іншу команду")
    else:
        bot.send_message(message.chat.id, 'Некоректний текст')
        bot.send_message(message.chat.id, "Введіть нове слово, словосполучення або іншу команду")
bot.polling(none_stop=True, interval=0)
