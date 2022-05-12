import os
import logging
import redis
from dotenv import load_dotenv

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from elasticpath_api import (TOKEN_EXPIRES, SHOP_TOKEN, get_token, get_products)

_database = None


def start(bot, update):
    shop_products = get_products()
    update.message.reply_text(text='Я чувствую волнение силы')
    keyboard = []
    for product in shop_products['data']:
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=product['id'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'ECHO'


def echo(bot, update):
    try:
        users_reply = update.message.text
        update.message.reply_text(users_reply)
    except AttributeError:
        users_reply = update.callback_query.data
        chat_id = update.effective_chat.id
    bot.bot.send_message(
        chat_id=chat_id,
        text=users_reply,)
    return "ECHO"


def buttons(bot, update):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'ECHO'


def handle_users_reply(update, bot):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)

    states_functions = {
        'START': start,
        'ECHO': echo,
        'BUTTONS': buttons,
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
        print(db.get(chat_id))
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        #database_password = os.getenv("DATABASE_PASSWORD", 123)
        database_host = os.getenv("DATABASE_HOST", 'localhost')
        database_port = os.getenv("DATABASE_PORT", 6379)
        _database = redis.Redis(host=database_host, port=database_port,
                                decode_responses=True)
                                #password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    tg_token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(tg_token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()
