import logging
import os
import textwrap

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
from validate_email import validate_email

from elasticpath_api import (add_product_to_cart, create_customer,
                             get_cart_total, get_image_by_id,
                             get_product_by_id, get_products_in_cart,
                             remove_cart_item)
from main_menu_handler import handle_main_menu

_database = None
logger = logging.getLogger(__name__)


def get_cart_details(update, context):
    all_carts_items = ''
    cart_names = list()
    chat_id = update.effective_chat.id
    cart_products = get_products_in_cart(chat_id)
    total_in_card = get_cart_total(chat_id)

    for cart_item in cart_products['data']:
        display_price = cart_item['meta']['display_price']['with_tax']
        cart_names.append((cart_item['name'], cart_item['id']))
        text = textwrap.dedent(
            f"""\
                    {cart_item['name']}
                    {cart_item['description']}
                    {display_price['unit']['formatted']} per kg
                    {cart_item['quantity']} kg in cart for {display_price['value']['formatted']}
                    """)
        all_carts_items += text + '\n'
    all_carts_items += 'Total: ' + str(
        total_in_card['data']['meta']['display_price']['with_tax']['formatted'])
    return all_carts_items, cart_names



def start(update, context):
    """
    Блок обработки начала работы с ботом
    """
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text='Я чувствую волнение силы')
    handle_main_menu(update, context)
    return 'HANDLE_MENU'


def handle_description(update, context):
    """
    Блок обработки нажатия клавиши меню выбранного товара
    """
    query = update.callback_query

    if query.data == 'back':
        handle_main_menu(update, context)
        return 'HANDLE_MENU'

    elif query.data == 'cart':
        handle_card(update, context)
        return 'HANDLE_CART'

    else:
        amount, product_id = query.data.split('|')
        cart_id = query.message.chat.id
        cart_products = add_product_to_cart(product_id, int(amount), cart_id)
        logger.info(cart_products)
        return 'HANDLE_DESCRIPTION'


def handle_menu(update, context):
    """
    Блок обработки меню выбранного товара
    """
    query = update.callback_query
    prod_id = query.data
    product_description = get_product_by_id(prod_id)
    keyboard = [
        [InlineKeyboardButton('1кг', callback_data=f'{1}|{prod_id}'),
         InlineKeyboardButton('5кг', callback_data=f'{5}|{prod_id}'),
         InlineKeyboardButton('10кг', callback_data=f'{10}|{prod_id}')],
        [InlineKeyboardButton('В главное меню', callback_data='back')],
        [InlineKeyboardButton('Корзина', callback_data='cart')]]
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
        context.bot.send_photo(
            photo=image,
            chat_id=chat_id,
            caption=text,
            reply_markup=reply_markup)
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup)

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id,)

    return 'HANDLE_DESCRIPTION'


def handle_card(update, context):
    """
    Блок обработки меню корзины
    """
    chat_id = update.effective_chat.id
    all_carts_items, cart_names = get_cart_details(update, context)
    keyboard = []
    query = update.callback_query

    if query.data == 'cart':
        for name, product_id in cart_names:
            keyboard.append(
                [InlineKeyboardButton(
                    f'убрать из корзины {name}', callback_data=product_id)])
        keyboard.append(
            [InlineKeyboardButton('В главное меню', callback_data='back')])
        keyboard.append(
            [InlineKeyboardButton('оплатить', callback_data='payment')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=chat_id,
            text=all_carts_items,
            reply_markup=reply_markup,)

    elif query.data == 'back':
        handle_main_menu(update, context)
        return 'HANDLE_MENU'
    elif query.data == 'payment':
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите адрес электронной почты:',)
        return 'WAITING_EMAIL'
    else:
        remove_cart_item(chat_id, query.data)

    return 'HANDLE_CART'


def waiting_email(update, context):
    """
    Блок меню ввода и обработки почты при покупке товара
    """
    user_email = update.message.text
    chat_id = update.message.chat_id
    is_mail_valid = validate_email(
        email_address=user_email,
        check_blacklist=True,
        check_dns=True,)
    if is_mail_valid:
        text = textwrap.dedent(f'''
        Вы ввели адрес электронной почты: {user_email}
        Ваш звонок очень важен для нас!
        в ближайшее время к вам выедут наши менеджеры!''')
        context.bot.send_message(
            chat_id=chat_id,
            text=text,)
        handle_main_menu(update, context)

        result = create_customer(str(chat_id), user_email)
        logger.info(f'создан клиент {result}')

        return 'HANDLE_MENU'
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text='Не верный адрес электронной почты', )
        return 'WAITING_EMAIL'


def handle_users_reply(update, context):
    """
    Корневая функция
    """
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
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_card,
        'WAITING_EMAIL': waiting_email,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
        logger.info(db.get(chat_id))
    except Exception as err:
        logger.exception(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_host = os.getenv("DATABASE_HOST", 'localhost')
        database_port = os.getenv("DATABASE_PORT", 6379)
        database_password = os.getenv("DATABASE_PASS")
        _database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password,
            decode_responses=True)
    return _database


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s; %(levelname)s; %(name)s; %(message)s')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        'log.lod', maxBytes=2000, backupCount=2)
    logger.addHandler(handler)

    load_dotenv()
    tg_token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(tg_token)

    logger.info('Выходим из гиперпространства!')
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()
