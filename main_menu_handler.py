from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from elasticpath_api import get_products


def handle_main_menu(bot, update):
    query = update.callback_query
    chat_id = update.effective_chat.id
    shop_products = get_products()
    bot.bot.send_message(chat_id=chat_id, text='Я чувствую волнение силы')
    keyboard = []
    for product in shop_products['data']:
        keyboard.append([InlineKeyboardButton(product['name'],
                                              callback_data=product['id'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.bot.send_message(
        chat_id=chat_id,
        text='Please choose:',
        reply_markup=reply_markup)
    if query:
        bot.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.message_id, )
