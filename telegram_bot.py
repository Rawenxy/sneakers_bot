import telebot
from telebot import types
from pymongo import MongoClient
import config


def get_database():
    CONNECTION_STRING = config.CONNECTION_STRING

    client = MongoClient(CONNECTION_STRING)

    return client['firebox_bot']


dbname = get_database()
collection_name = dbname["shoes"]

dbname = get_database()
collection_name_w = dbname["shoes_w"]

TG_TOKEN = config.TG_TOKEN

bot = telebot.TeleBot(TG_TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
def man_or_woman(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    man = types.KeyboardButton('Мужские')
    woman = types.KeyboardButton('Женские')
    markup.add(man, woman)
    bot.send_message(message.chat.id,
                     'Привет, этот бот подкинет тебе пару классных кросовок по низкой цене!', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     'Для того чтоб вернуться в начало используй "/start"')


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
            print("mt", message.text)
            print("message.chat.id", message.chat.id)
            print("message.text", message.text)

            price_selected[message.chat.id] = message.text


            gender_collection = collection_name if gender[message.chat.id] == 'Мужские' else collection_name_w

            query = {
                'item_name': {f'$regex': f'^{brand_selected[message.chat.id]}(.*?)'},
                'new_price': price[price_selected[message.chat.id]]
            }

            print(query)

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


bot.polling()
