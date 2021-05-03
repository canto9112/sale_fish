from environs import Env
import logging
import redis

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from functools import partial
import moltin
from pprint import pprint

_database = None


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text=f"Selected option: {query.data}",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def start(bot, update, products):
    keyboard = []
    for product in products:
        button = [InlineKeyboardButton(product['name'], callback_data=product['id'])]
        keyboard.append(button)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "BUTTON"


def echo(bot, update):
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return "ECHO"


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
        'BUTTON': button
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
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

    # moltin_client_id = env('MULTIN_CLIENT_ID')
    # moltin_client_secret = env('MULTIN_CLIENT_SECRET')

    telegram_token = env("TELEGRAM_TOKEN")

    # moltin_access_token = moltin.get_access_token(moltin_client_id, moltin_client_secret)
    # products = moltin.get_all_products(moltin_access_token)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()