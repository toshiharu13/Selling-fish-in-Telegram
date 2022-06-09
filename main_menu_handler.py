from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from elasticpath_api import get_products


def handle_main_menu(update, context):
    """
     Блок обработки главного меню
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    shop_products = get_products()
    keyboard = []
    for product in shop_products['data']:
        keyboard.append([InlineKeyboardButton(product['name'],
                                              callback_data=product['id'])])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id,
        text='РРРРыба моя!:',
        reply_markup=reply_markup)
    if query:
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.message_id, )
