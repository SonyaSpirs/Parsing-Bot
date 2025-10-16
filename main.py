# import telebot
# from telebot import types
# # import config
#
# bot = telebot.TeleBot('8453465834:AAEdzYPmtmjayAtTfhitVaiiA3aBtELRDQY')
#
#
# @bot.message_handler(commands=['start'])
# def start(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("Поздороваться 👋")
#     btn2 = types.KeyboardButton("Задать вопрос ❓")
#     markup.add(btn1, btn2)
#     bot.send_message(message.chat.id,
#                      text="Привет, {0.first_name}! Я Telegram бот для парсинга IT статей".format(
#                          message.from_user), reply_markup=markup)
#
#
# @bot.message_handler(content_types=['text'])
# def func(message):
#     if message.text == "Поздороваться 👋":
#         bot.send_message(message.chat.id, text="Привеет.. Спасибо что читаешь статью!)")
#     elif message.text == "Задать вопрос ❓":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btn1 = types.KeyboardButton("Статья")
#         btn2 = types.KeyboardButton("Что я могу?")
#         back = types.KeyboardButton("Вернуться в главное меню")
#         markup.add(btn1, btn2, back)
#         bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)
#     elif message.text == "Как меня зовут?":
#         bot.send_message(message.chat.id, "Меня зовут Parsing-Bot")
#
#     elif message.text == "Статья":
#         bot.send_message(message.chat.id, text="Прочитать статью")
#
#     elif message.text == "Вернуться в главное меню":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         button1 = types.KeyboardButton("Поздороваться 👋")
#         button2 = types.KeyboardButton("Задать вопрос ❓")
#         markup.add(button1, button2)
#         bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")
#
#
# bot.polling(none_stop=True)