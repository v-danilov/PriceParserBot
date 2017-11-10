import requests
from bs4 import BeautifulSoup
import datetime
import os
import json
import pymysql
from threading import Thread


class DataBase:
    def __init__(self):
        conn = pymysql.connect(host="progist.pro", user="progist_marzi", db="progist_marzi", passwd="KatyaKlapp911",
                               charset="utf8",
                               autocommit=True)
        self.cursor = conn.cursor()

    def check(self):
        try:
            self.cursor.execute('SELECT version()')
        except:
            conn = pymysql.connect(host="progist.pro", user="progist_marzi", db="progist_marzi", passwd="KatyaKlapp911",
                                   charset="utf8",
                                   autocommit=True)
            self.cursor = conn.cursor()

    def get(self):
        lock = Lock()
        lock.acquire()
        self.check()
        self.cursor.execute('select * from bot')
        ids = self.cursor.fetchall()
        ids_new = []
        for i in ids:
            id, =i
            ids_new.append(id)
        lock.release()
        return ids_new

    def remove(self,id):
        self.check()
        self.cursor.execute('delete from bot where id = {}'.format(id))

    def add(self, id):
        self.check()
        self.cursor.execute('insert into bot set id = {} on duplicate key update id = id'.format(id))



class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text,'parse_mode':'HTML', 'reply_markup':json.dumps({'keyboard':[['Подписаться','Отписаться'], ['Текущая цена'],['Помощь']],'resize_keyboard':True}).encode('utf-8')}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None
        return last_update

def get_html(url):
    resp = requests.get(url)
    return resp.text

def get_price(html_page):
    soup = BeautifulSoup(html_page, "html5lib")
    div_container = soup.find_all('div',class_='product-intro__purchase')
    
    for div in div_container:
        div_price = div.find_all('div', class_='product-price__main')
        for span in div_price:
            price = span.getText().strip().replace(' ', '')[:-1]
            return int(price)

def check_price():
    adress = 'https://www.wellfix.ru/shop/product/displei-oneplus-x-s-tachskrinom-chernyi'
    
    new_price = get_price(get_html(adress))
    if( new_price < price):
        output = "🎉Дождались🎉! Дисплей по скидону! Новая цена: {} рублёу!".format(new_price)
    else:
        output = "Ждём и надеемся... \U0001F610 Текущая цена <b>{}</b> рублёу.".format(new_price)
    return output

def update(new_offset):

    price_bot.get_updates(new_offset)
    last_update = price_bot.get_last_update()
            
    if last_update is not None:
        last_update_id = last_update['update_id']    
        last_chat_id = last_update['message']['chat']['id']
        last_chat_text = last_update['message']['text']

        if last_chat_text in ['/start', "Подписаться"] :
            if last_chat_id not in db.get():
                db.add(last_chat_id)
                price_bot.send_message(last_chat_id, "\U00002705 Вы успешно подписаны на ежедневную рассылку! Информация обновляется в \U0001F559 10 часов 5 минут \U0001F559. Чтобы отписаться от рассылки отправьте \"/stop\"")
                price_bot.send_message(last_chat_id, check_price())
            else:
                price_bot.send_message(last_chat_id, 'Ты уже подписан. Попробуй это: /help')

        elif last_chat_text in ['/stop', "Отписаться"]:
            if last_chat_id in db.get():
                db.remove(last_chat_id)
                price_bot.send_message(last_chat_id, "Вы отписались от рассылки. Пок \U0001F618")

        elif last_chat_text in ['/info', 'Текущая цена']:
            price_bot.send_message(last_chat_id, check_price())

        elif last_chat_text in ['/help', 'Помощь']:
            price_bot.send_message(last_chat_id, 'Возможные команды: /start - подписаться на ежедневную рассылку, /stop - отписаться от рассылки, /info - получить свежую инфу')
            
        new_offset = last_update_id + 1

def notify():

    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour
        minute = now.minute

        if (hour == 17 and minute == 0) or (hour == 7 and minute == 5):
                print("Daily update for {} user(s)".format(len(db.get())))
                text_mes = check_price()
                for chat in db.get():
                    price_bot.send_message(chat, text_mes)


#___________Variables___________
price_bot = BotHandler('401670663:AAELFfb0SSv6qTiTlBTwkzhytSc9bH0cikI')
price = 7000
db = DataBase()

#_______________________________

def main():
    new_offset = None
    thread = Thread(target = notify)
    
    while True:
        update(new_offset)


if __name__ == '__main__':  
    try:
        main()
    except IndexError:
        print('Index error')
    except KeyError:
        print('KeyError')
    except KeyboardInterrupt:
        print("Goodbye!")
        exit()