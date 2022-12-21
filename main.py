import telebot
from telebot import types
from flask import Flask, request
import os
from pymongo import MongoClient
import config


TG_TOKEN = config.TG_TOKEN
bot = telebot.TeleBot(TG_TOKEN, parse_mode=None)
APP_URL = f'https://sneakers.herokuapp.com/{TG_TOKEN}'
server = Flask(__name__)


def get_database():
    CONNECTION_STRING = config.CONNECTION_STRING
    client = MongoClient(CONNECTION_STRING)
    return client['firebox_bot']


dbname = get_database()
collection_name = dbname["shoes"]
collection_name_w = dbname["shoes_w"]


@bot.message_handler(commands=['start'])
def man_or_woman(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    man = types.KeyboardButton('Мужские')
    woman = types.KeyboardButton('Женские')
    markup.add(man, woman)
    bot.send_message(message.chat.id,
                     'Привет, этот бот подкинет тебе пару классных кросовок по низкой цене!'
                     'Для справки используй /help', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     'Для того чтоб вернуться в начало используй "/start"'
                     '2 раза в день обнавляем базу данных! Занимает 1 минутку :)')


brands = ['Adidas', 'Nike', 'Reebok', 'Columbia', 'New Balance']


gender = {}
price_selected = {}
brand_selected = {}
price = {
    '2000₽-3000₽': {f'$gt': 2000, f'$lt': 3000},
    '3000₽-4000₽': {f'$gt': 3000, f'$lt': 4000},
    '4000₽ и более': {f'$gt': 4000}
}

prices_categories = list(price.keys())


@bot.message_handler(content_types=['text'])
def sneakers_find(message):
    try:
        global price_selected
        global gender
        global brand_selected
        if message.text in ['Мужские', 'Женские']:
            gender[message.chat.id] = message.text

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            adidas = types.KeyboardButton('Adidas')
            nike = types.KeyboardButton('Nike')
            reebok = types.KeyboardButton('Reebok')
            columbia = types.KeyboardButton('Columbia')
            new_balance = types.KeyboardButton('New Balance')
            markup.add(adidas, nike, reebok, columbia, new_balance)
            return bot.send_message(message.chat.id,
                                    'Выбери бренд кросовок', reply_markup=markup)

        if message.text in brands:
            brand_selected[message.chat.id] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for key in prices_categories:
                price1 = types.KeyboardButton(key)
                markup.add(price1)
            return bot.send_message(message.chat.id,
                                    'Выбери ценовую категорию', reply_markup=markup)

        if message.text in prices_categories:

            price_selected[message.chat.id] = message.text

            gender_collection = collection_name if gender[message.chat.id] == 'Мужские' else collection_name_w

            query = {
                'item_name': {f'$regex': f'^{brand_selected[message.chat.id]}(.*?)'},
                'new_price': price[price_selected[message.chat.id]]
            }


            for params in gender_collection.find(query):
                params_name = params['item_name']
                params_model = params['item_model']
                params_old_price = params['old_price']
                params_new_price = params['new_price']
                params_size = params['item_size']
                params_href = params['item_href']
                params_picture = params['item_picture']

                bot.send_message(
                    message.chat.id,
                    f'🔥 <b>{params_name}</b>\n'
                    f'🥾 {params_model}\n'
                    f'✅ Новая цена: <b>{params_new_price}₽</b>\n'
                    f'❌ Старая цена: {params_old_price}₽\n'
                    f'📐 {params_size}\n'
                    f'<a href="{params_picture}"> </a>'
                    f'<a href="{params_href}">Ссылка</a>', parse_mode='HTML'
                )
    except:
        bot.send_message(message.chat.id, 'Что-то не так, перезапусти меня с помошью /start')


@server.route(f"/{TG_TOKEN}", methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return "!", 200


if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


