import os
import logging
import redis
from dotenv import load_dotenv
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import textwrap

from elasticpath_api import (
    get_products, get_product_by_id, add_product_to_cart, get_image_by_id)
from main_menu_handler import handle_main_menu

_database = None


def start(bot, update):
    handle_main_menu(bot, update)
    return 'HANDLE_MENU'


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


def handle_description(bot, update):
    query = update.callback_query
    chat_id = update.effective_chat.id
    if query.data == 'back':
        handle_main_menu(bot, update)
        return 'HANDLE_MENU'
    else:
        amount, product_id = query.data.split('|')
        cart_id = query.message.chat.id
        products_in_cart = add_product_to_cart(product_id, int(amount), cart_id)
        print(products_in_cart)
        bot.bot.send_message(
            chat_id=chat_id,
            text=products_in_cart, )
        return 'HANDLE_DESCRIPTION'

def handle_menu(bot, update):
    query = update.callback_query
    prod_id = query.data
    product_description = get_product_by_id(prod_id)
    keyboard = [
        [InlineKeyboardButton('1кг', callback_data=f'{1}|{prod_id}'),
         InlineKeyboardButton('5кг', callback_data=f'{5}|{prod_id}'),
         InlineKeyboardButton('10кг', callback_data=f'{10}|{prod_id}')],
        [InlineKeyboardButton('В главное меню', callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    img_id = product_description['data']['relationships']['main_image']['data']['id']
    image = get_image_by_id(img_id)
    text = textwrap.dedent(f'''
    Название: {product_description['data']['name']}
    Описание: {product_description['data']['description']}
    Цена: {product_description['data']['meta']['display_price']['with_tax']['formatted']} за кг.
    Наличие на складе: {product_description['data']['meta']['stock']['level']} кг.''')
    chat_id = update.effective_chat.id

    if image:
        bot.bot.send_photo(
            photo=image,
            chat_id=chat_id,
            caption=text,
            reply_markup=reply_markup)
    else:
        bot.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup)

    bot.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id,)
    return 'HANDLE_DESCRIPTION'


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
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
    }
    state_handler = states_functions[user_state]
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
