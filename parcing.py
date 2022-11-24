from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import config
import os


def get_database():
    CONNECTION_STRING = config.CONNECTION_STRING

    client = MongoClient(CONNECTION_STRING)

    return client['firebox_bot']


dbname = get_database()
collection_name = dbname["shoes"]

base_url = 'https://fireboxclub.com'
url = 'https://fireboxclub.com/catalogue/sale990?show=1&sGen=1'
url_g = 'https://fireboxclub.com/catalogue/sale990?show=1&sGen=2'

headers= {
 'Accept': '*/*',
 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0'
}

# Сделали запрос, поняли сколько страниц на сайте mans
def make_mans_db():
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    find_lats_pages = soup.find(class_="pag-wrapper").find_all('a')[-2].text

    for count in range(1, int(find_lats_pages)+1):
        req = requests.get(url+f'&page={count}', headers=headers)

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
            print(f'\n{item_name}-{item_model}\nold price:{old_price},\nnew price:{new_price}\n{item_size}\n{item_href}\n{item_picture}\n'+'*'*100)
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
























