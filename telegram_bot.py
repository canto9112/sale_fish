from environs import Env
import logging
import redis

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from functools import partial
import moltin
from pprint import pprint
import json


_database = None


def start(bot, update, products):
    keyboard = start_keyboard(products)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "HANDLE_MENU"


def start_keyboard(products):
    keyboard = []
    for product in products:
        button = [InlineKeyboardButton(product['name'], callback_data=product['id'])]
        keyboard.append(button)
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


def cart(bot, update, products):
    query = update.callback_query

    if query.data == 'Меню':
        del_old_message(bot, update)
        keyboard = start_keyboard(products)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=query.message.chat_id, text='Please choose:', reply_markup=reply_markup)
        return 'HANDLE_MENU'


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
        button_menu = [[InlineKeyboardButton("Меню", callback_data="Меню")]]

        reply_markup = InlineKeyboardMarkup(button_menu)

        cart_items = moltin.get_cart_items(access_token, query.message.chat_id)
        products_in_cart = []
        for product_in_cart in cart_items['data']:
            product_name = product_in_cart['name']
            description = product_in_cart['description']
            price = product_in_cart['meta']['display_price']['with_tax']['unit']['formatted']
            quantity = product_in_cart['quantity']
            all_price = product_in_cart['meta']['display_price']['with_tax']['value']['formatted']

            products_in_cart.append(f'{product_name}\n{description}\n{price}per kg\n{quantity}kg in cart for {all_price}\n\n')

        myString = ''.join(products_in_cart)
        print(myString)
        print('============')
        new = json.dumps(products_in_cart)
        pprint(new)
        del_old_message(bot, update)

        cart = moltin.get_cart(access_token, query.message.chat_id)
        total_price = cart['data']['meta']['display_price']['with_tax']['formatted']
        bot.send_message(chat_id=query.message.chat_id, text=f'{myString}\n'
                                                             f'Всего на сумму:\n'
                                                             f'{total_price}', reply_markup=reply_markup)
        return "HANDLE_CART"

    elif button:
        moltin.add_product_to_cart(access_token, product_id, query.message.chat_id, button)
        return "HANDLE_DESCRIPTION"


def handle_users_reply(bot, update):
    moltin_client_id = env('MULTIN_CLIENT_ID')
    moltin_client_secret = env('MULTIN_CLIENT_SECRET')

    moltin_access_token = moltin.get_access_token(moltin_client_id, moltin_client_secret)
    products = moltin.get_all_products(moltin_access_token)

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
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(start, products=products),
        'HANDLE_MENU': partial(handle_button_menu, access_token=moltin_access_token),
        'HANDLE_DESCRIPTION': partial(handle_description, products=products, access_token=moltin_access_token),
        'HANDLE_CART': partial(cart, products=products)
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = env("REDIS_PASSWORD")
        database_host = env("REDIS_HOST")
        database_port = env("REDIS_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    env = Env()
    env.read_env()

    telegram_token = env("TELEGRAM_TOKEN")

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()