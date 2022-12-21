from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import config
import os

import schedule

def get_database():
    CONNECTION_STRING = config.CONNECTION_STRING

    client = MongoClient(CONNECTION_STRING)

    return client['firebox_bot']


dbname = get_database()
collection_name = dbname["shoes"]

dbname = get_database()
collection_name_w = dbname["shoes_w"]



# scrap
base_url = 'https://fireboxclub.com'
url_m = 'https://fireboxclub.com/catalogue/sale990?show=1&sGen=1'
url_g = 'https://fireboxclub.com/catalogue/sale990?show=1&sGen=2'


headers = {
 'Accept': '*/*',
 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0'
}

def clear_db():
    collection_name.delete_many({})
    collection_name_w.delete_many({})
    return 'Удалили старые данные'

# scrap man
def make_mans_db():
    req = requests.get(url_m, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    find_lats_pages = soup.find(class_="pag-wrapper").find_all('a')[-2].text

    for count in range(1, int(find_lats_pages)+1):
        req = requests.get(url_m+f'&page={count}', headers=headers)

        src = req.text
        print(f'[+][{count}/{find_lats_pages}]Собираем пагинацию мужских кросовок')

        with open(f'data/index{count}.html', 'w') as file:
            file.write(src)

    for count in range(1, int(find_lats_pages)+1):

        with open(f'data/index{count}.html') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        find_objects = soup.find(class_='icat w1400').find_all('a')

        for item in find_objects:
            item_href = base_url + item.get('href')
            item_name = item.find(class_='name').find('b').text
            item_model = item.find(class_='name').find(class_='upp').text
            old_price = item.find(class_='name').find(class_='old_price_prew').text.split(' ')[0]
            new_price = item.find(class_='name').find(class_='new_price_prew').text.split(' ')[0]
            item_size = item.find(class_='size').text.strip()
            item_picture = base_url + item.find(class_='photo p1 current').find('img')['src']
            print(f'\n{item_name}-{item_model}\nold price:{old_price},\nnew price:{new_price}'
                  f'\n{item_size}\n{item_href}\n{item_picture}\n'+'*'*100)

            shoes = ({
                "item_picture": item_picture,
                'item_name': item_name,
                'item_model': item_model,
                'old_price': int(old_price),
                'new_price': int(new_price),
                'item_size': item_size,
                'item_href': item_href,
            })

            collection_name.replace_one({'item_href': shoes['item_href']}, shoes, upsert=True)

    return print('Мужская база данных обнавлена')


def clear_derectory_data():
    try:
        dir = './data'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    except:
        print('Не получуилось удалить файлы в директории data')

    return print('Файлы из директории /data отчищены')


# scrap woman

def make_woman_db():
    req = requests.get(url_g, headers=headers)
    src = req.text
    soup = BeautifulSoup(src)
    find_lats_pages = soup.find(class_="pag-wrapper").find_all('a')[-2].text

    for count in range(1, int(find_lats_pages)+1):
        req = requests.get(url_g+f'&page={count}', headers=headers)

        src = req.text
        print(f'[+][{count}/{find_lats_pages}]Собираем пагинацию женских кросовок')

        with open(f'data_g/index{count}.html', 'w') as file:
            file.write(src)

    for count in range(1, int(find_lats_pages)+1):

        with open(f'data_g/index{count}.html') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        find_objects = soup.find(class_='icat w1400').find_all('a')
        for item in find_objects:
            item_href = base_url + item.get('href')
            item_name = item.find(class_='name').find('b').text
            item_model = item.find(class_='name').find(class_='upp').text
            old_price = item.find(class_='name').find(class_='old_price_prew').text.split(' ')[0]
            new_price = item.find(class_='name').find(class_='new_price_prew').text.split(' ')[0]
            item_size = item.find(class_='size').text.strip()
            item_picture = base_url + item.find(class_='photo p1 current').find('img')['src']
            print(f'\n{item_name}-{item_model}\nold price:{old_price}\nnew price:{new_price}\n'
                  f'{item_size}\n{item_href}\n{item_picture}\n'+'*'*100)

            shoes_w = ({
                "item_picture": item_picture,
                'item_name': item_name,
                'item_model': item_model,
                'old_price': int(old_price),
                'new_price': int(new_price),
                'item_size': item_size,
                'item_href': item_href,
            })

            collection_name_w.replace_one({'item_href': shoes_w['item_href']}, shoes_w, upsert=True)

    return print('Женская база данных обнавлена')


def clear_derectory_data_g():
    try:
        dir = './data_g'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    except:
        print('Не получилось удалить файлы')

    return print('Файлы из директории /data_g отчищены')

if __name__ == '__main__':
    schedule.every().day.at("05:59").do(clear_db)
    schedule.every().day.at("06:00").do(make_mans_db)
    schedule.every().day.at("06:01").do(clear_derectory_data)
    schedule.every().day.at("06:02").do(make_woman_db)
    schedule.every().day.at("06:03").do(clear_derectory_data_g)
    schedule.every().day.at("12:59:55").do(clear_db)
    schedule.every().day.at("13:00").do(make_mans_db)
    schedule.every().day.at("13:01").do(clear_derectory_data)
    schedule.every().day.at("13:02").do(make_woman_db)
    schedule.every().day.at("13:03").do(clear_derectory_data_g)
    make_mans_db()
    make_woman_db()
    while True:
        schedule.run_pending()




















