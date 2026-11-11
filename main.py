import telebot
from telebot import types

# Вставьте сюда ваш токен от BotFather вместо 'YOUR_BOT_TOKEN'
TOKEN = '8868759031:AAHAVkIfeyafQusWFbFCeTejNUDiw9Ce_Vw'
bot = telebot.TeleBot(TOKEN)

# Словарь для сохранения введенных ников и выбранных товаров игроков
user_data = {}

# 1. Команда /start и установка меню кнопки
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'menu'}
    
    # Установка постоянной кнопки меню рядом с полем ввода
    bot.set_chat_menu_button(chat_id=message.chat.id, menu_button=types.MenuButtonCommands(type='commands'))
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_shop = types.InlineKeyboardButton("Магазин 🛒", callback_data="open_shop")
    markup.add(btn_shop)
    
    bot.send_message(
        message.chat.id, 
        "💙Привет это магазин JORO RP🛒", 
        reply_markup=markup
    )

# Обработка нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {}

    if call.data == "open_shop":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_money = types.InlineKeyboardButton("Деньги 💰", callback_data="cat_money")
        btn_coins = types.InlineKeyboardButton("Донат монетки 🪙", callback_data="cat_coins")
        markup.add(btn_money, btn_coins)
        
        bot.edit_message_text(
            "Выбирай категорию📦:", 
            call.message.chat.id, 
            call.message.message_id, 
            reply_markup=markup
        )

    elif call.data == "cat_money":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Цены в звездах (Telegram Stars)
        markup.add(
            types.InlineKeyboardButton("10.000₽ (80 ⭐)", callback_data="buy_m_80"),
            types.InlineKeyboardButton("60.000₽ (350 ⭐)", callback_data="buy_m_350"),
            types.InlineKeyboardButton("100.000₽ (499 ⭐)", callback_data="buy_m_499"),
            types.InlineKeyboardButton("250.000₽ (799 ⭐)", callback_data="buy_m_799"),
            types.InlineKeyboardButton("500.000₽ (999 ⭐)", callback_data="buy_m_999"),
            types.InlineKeyboardButton("1.000.000₽ (1500 ⭐)", callback_data="buy_m_1500")
        )
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="open_shop"))
        
        bot.edit_message_text(
            "💰 **Виновыберите сумму игровых денег:** (Деньги не настоящие, для РП сервера)", 
            call.message.chat.id, 
            call.message.message_id, 
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data == "cat_coins":
        bot.answer_callback_query(call.id)
        user_data[user_id]['step'] = 'wait_coins_amount'
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="open_shop"))
        
        bot.edit_message_text(
            "🪙 **Донат монеты**\n\nКурс: 1 монета = 3 звезды ⭐\n\n💬 Напиши в чат число монет, которые хочешь купить (например: `5` или `50`):", 
            call.message.chat.id, 
            call.message.message_id, 
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data.startswith("buy_m_"):
        bot.answer_callback_query(call.id)
        stars = int(call.data.split("_")[2])
        
        if stars == 80: title, desc = "10.000₽", "Игровые деньги для JORO RP (10k)"
        elif stars == 350: title, desc = "60.000₽", "Игровые деньги для JORO RP (60k)"
        elif stars == 499: title, desc = "100.000₽", "Игровые деньги для JORO RP (100k)"
        elif stars == 799: title, desc = "250.000₽", "Игровые деньги для JORO RP (250k)"
        elif stars == 999: title, desc = "500.000₽", "Игровые деньги для JORO RP (500k)"
        else: title, desc = "1.000.000₽", "Игровые деньги для JORO RP (1кк)"

        user_data[user_id]['pending_order'] = {
            'title': f"Деньги: {title}",
            'price': stars
        }
        ask_for_credentials(call.message.chat.id, user_id)

# Запрос никнейма и ID
def ask_for_credentials(chat_id, user_id):
    user_data[user_id]['step'] = 'wait_credentials'
    saved_nick = user_data[user_id].get('nickname', 'еще не указан')
    
    text = (
        f"📝 **Укажи свой Ник и ID в игре**\n\n"
        f"Твой текущий сохраненный ник/ID: `{saved_nick}`\n\n"
        f"Отправь в чат сообщение в формате:\n`Artem Pupki Id=123`\n\n"
        f"*(Ты можешь изменить его в любой момент, просто отправив новый вариант)*"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")

# Обработка текстовых сообщений (ввод монет или ника)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in user_data:
        user_data[user_id] = {'step': 'menu'}
        
    current_step = user_data[user_id].get('step', 'menu')

    # Шаг 1: Пользователь вводит количество донат-монет
    if current_step == 'wait_coins_amount':
        if not text.isdigit() or int(text) <= 0:
            bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число цифрой (например: 10):")
            return
            
        coins = int(text)
        stars = coins * 3
        
        user_data[user_id]['pending_order'] = {
            'title': f"{coins} Донат монет",
            'price': stars
        }
        ask_for_credentials(message.chat.id, user_id)

    # Шаг 2: Пользователь вводит ник и ID
    elif current_step == 'wait_credentials':
        user_data[user_id]['nickname'] = text
        user_data[user_id]['step'] = 'ready_to_pay'
        
        order = user_data[user_id].get('pending_order')
        if not order:
            bot.send_message(message.chat.id, "⚠️ Сначала выберите товар в магазине через /start")
            return

        # Уведомление вам (администратору) в консоль или чат (если нужно, можно указать ваш Telegram ID)
        print(f"📦 Новый игрок указал данные! Юзер: @{message.from_user.username}, Данные: {text}")
        
        # Кнопка отправки инвойса (оплата звёздами)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"💳 Оплатить {order['price']} ⭐", callback_data="pay_invoice"))
        markup.add(types.InlineKeyboardButton("✏️ Изменить ник/ID", callback_data="change_cred"))
        
        bot.send_message(
            message.chat.id,
            f"✅ Данные сохранены: `{text}`\n\nТовар: **{order['title']}**\nЦена: **{order['price']} ⭐**\n\nНажми кнопку ниже для оплаты:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    else:
        bot.send_message(message.chat.id, "Нажми /start, чтобы открыть магазин 🛒")

# Изменение данных
@bot.callback_query_handler(func=lambda call: call.data == "change_cred")
def change_cred_callback(call):
    bot.answer_callback_query(call.id)
    ask_for_credentials(call.message.chat.id, call.from_user.id)

# Выставление счета через Telegram Stars
@bot.callback_query_handler(func=lambda call: call.data == "pay_invoice")
def pay_invoice_callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    order = user_data.get(user_id, {}).get('pending_order')
    nickname = user_data.get(user_id, {}).get('nickname', 'Не указан')
    
    if not order:
        bot.send_message(call.message.chat.id, "Ошибка заказа. Начните заново: /start")
        return

    prices = [types.LabeledPrice(label=order['title'], amount=order['price'])]
    
    # Отправка инвойса в Звездах (XTR)
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title=order['title'],
        description=ل description := f"Покупка для игрока: {nickname}",
        invoice_payload="joro_rp_payment",
        currency="XTR", # Валюта Telegram Stars
        prices=prices
    )

# Подтверждение успешной оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = message.from_user.id
    nickname = user_data.get(user_id, {}).get('nickname', 'Неизвестно')
    order = user_data.get(user_id, {}).get('pending_order', {}).get('title', 'Товар')
    
    bot.send_message(
        message.chat.id, 
        "🎉 **Оплата успешно прошла!**\n\nВаш заказ передан администратору, скоро он будет выдан вам на сервере JORO RP.",
        parse_mode="Markdown"
    )
    
    # Сюда бот пришлет вам отчет об успешной покупке (в чат с ботом или можно настроить ваш ID)
    # Если вы хотите получать уведомления себе, бот может присылать их в этот же чат или мы можем прописать ваш ID администратора.
    bot.send_message(
        message.chat.id, 
        f"🚨 **НОВАЯ ПОКУПКА!**\nИгрок: `{nickname}`\nКупил: `{order}`\nTelegram: @{message.from_user.username}",
        parse_mode="Markdown"
    )

bot.infinity_polling()
