from functools import partial

import redis
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from pprint import pprint

import moltin


def start(bot, update, products):
    keyboard = start_keyboard(products)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "HANDLE_MENU"


def start_keyboard(products):
    keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id'])] for product in products]
    return keyboard


def del_old_message(bot, update):
    query = update.callback_query
    old_message = update.callback_query.message['message_id']

    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=old_message)


def handle_button_menu(bot, update, access_token):
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("1 кг", callback_data=f'{1}/{query.data}'),
                 InlineKeyboardButton("5 кг", callback_data=f'{5}/{query.data}'),
                 InlineKeyboardButton("10 кг", callback_data=f'{10}/{query.data}')],
                [InlineKeyboardButton("Меню", callback_data=f'{"Меню"}/{query.data}')],
                [InlineKeyboardButton("Корзина", callback_data=f'{"Корзина"}/{query.data}')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    product = moltin.get_product(access_token, query.data)

    product_name = product['data']['name']
    price = product['data']['meta']['display_price']['with_tax']['formatted']
    stock = product['data']['meta']['stock']['level']
    description = product['data']['description']
    file_id = product['data']['relationships']['main_image']['data']['id']

    image = moltin.get_image_url(access_token, file_id)
    bot.send_photo(query.message.chat_id, image, caption=f"{product_name}\n"
                                                         f"{price} per kg\n"
                                                         f"{stock}kg on stock\n"
                                                         f"{description}", reply_markup=reply_markup)
    del_old_message(bot, update)
    return "HANDLE_DESCRIPTION"


def get_cart(bot, update, products, access_token):
    query = update.callback_query

    if query.data == 'Меню':
        del_old_message(bot, update)
        keyboard = start_keyboard(products)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=query.message.chat_id, text='Please choose:', reply_markup=reply_markup)
        return 'HANDLE_MENU'

    elif query.data == 'Оплатить':
        bot.send_message(chat_id=query.message.chat_id, text='Введите вашу почту для связи:')
        return "WAITING_EMAIL"

    elif query.data:
        moltin.delete_product_in_cart(access_token, query.message.chat_id, query.data)
        get_updating_cart(bot, update, access_token)
        return "HANDLE_CART"


def get_updating_cart(bot, update, access_token):
    query = update.callback_query

    button_menu = [InlineKeyboardButton("Меню", callback_data="Меню")]
    button_pay = [InlineKeyboardButton("Оплатить", callback_data="Оплатить")]

    cart_items = moltin.get_cart_items(access_token, query.message.chat_id)
    cart = moltin.get_cart(access_token, query.message.chat_id)
    total_price = cart['data']['meta']['display_price']['with_tax']['formatted']

    products_in_cart = []
    keyboard = []
    for product_in_cart in cart_items['data']:
        product_name = product_in_cart['name']
        description = product_in_cart['description']
        price = product_in_cart['meta']['display_price']['with_tax']['unit']['formatted']
        quantity = product_in_cart['quantity']
        all_price = product_in_cart['meta']['display_price']['with_tax']['value']['formatted']

        button = [InlineKeyboardButton(f'Убрать из корзины {product_name}', callback_data=product_in_cart['id'])]
        keyboard.append(button)
        products_in_cart.append(f'{product_name}\n'
                                f'{description}\n'
                                f'{price}per kg\n'
                                f'{quantity}kg in cart for {all_price}\n\n')

    keyboard.append(button_menu)
    keyboard.append(button_pay)
    reply_markup = InlineKeyboardMarkup(keyboard)
    cart_text = ''.join(products_in_cart)

    del_old_message(bot, update)

    bot.send_message(chat_id=query.message.chat_id, text=f'{cart_text}\n'
                                                         f'Всего на сумму:\n'
                                                         f'{total_price}', reply_markup=reply_markup)


def send_mail(bot, update, access_token):
    users_reply = update.message.text
    username = update.message['chat']['first_name']
    moltin.create_customer(access_token, username, users_reply)
    update.message.reply_text(f'Вы отправили почту вот эту - {users_reply}')


def handle_description(bot, update, products, access_token):
    query = update.callback_query
    button, product_id = query.data.split('/')

    if button == 'Меню':
        del_old_message(bot, update)
        keyboard = start_keyboard(products)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=query.message.chat_id, text='Please choose:', reply_markup=reply_markup)
        return 'HANDLE_MENU'

    elif button == 'Корзина':
        get_updating_cart(bot, update, access_token)
        return "HANDLE_CART"

    elif button:
        moltin.add_product_to_cart(access_token, product_id, query.message.chat_id, button)
        return "HANDLE_DESCRIPTION"


def handle_users_reply(bot, update, moltin_access_token, products):
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
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(start,
                         products=products),
        'HANDLE_MENU': partial(handle_button_menu,
                               access_token=moltin_access_token),
        'HANDLE_DESCRIPTION': partial(handle_description,
                                      products=products,
                                      access_token=moltin_access_token),
        'HANDLE_CART': partial(get_cart,
                               products=products,
                               access_token=moltin_access_token),
        'WAITING_EMAIL': partial(send_mail,
                                 access_token=moltin_access_token)
    }
    state_handler = states_functions[user_state]

    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection():
    database_password = env("REDIS_PASSWORD")
    database_host = env("REDIS_HOST")
    database_port = env("REDIS_PORT")
    database = redis.Redis(host=database_host,
                           port=database_port,
                           password=database_password)
    return database


if __name__ == '__main__':
    env = Env()
    env.read_env()

    db = get_database_connection()

    telegram_token = env("TELEGRAM_TOKEN")
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_access_token = moltin.get_access_token(moltin_client_id, moltin_client_secret)
    products = moltin.get_all_products(moltin_access_token)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(partial(handle_users_reply,
                                                        moltin_access_token=moltin_access_token,
                                                        products=products)))
    dispatcher.add_handler(MessageHandler(Filters.text, (partial(handle_users_reply,
                                                                 moltin_access_token=moltin_access_token,
                                                                 products=products))))
    dispatcher.add_handler(CommandHandler('start', (partial(handle_users_reply,
                                                            moltin_access_token=moltin_access_token,
                                                            products=products))))

    updater.start_polling()
