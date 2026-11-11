import telebot
from telebot import types

TOKEN = '8868759031:AAHAVkIfeyafQusWFbFCeTejNUDiw9Ce_Vw'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_shop = types.InlineKeyboardButton("🛒 МАГАЗИН", callback_data="open_shop")
    markup.add(btn_shop)
    bot.send_message(message.chat.id, "Привет! Ты попал в магазин сервера JORO.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "open_shop":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Выберите раздел товара:\n\n💰 Деньги\n🪙 Донат монеты")

bot.infinity_polling()
