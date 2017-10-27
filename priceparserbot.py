import requests
from bs4 import BeautifulSoup
import datetime


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
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
        	print(len(get_result))
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
		output = "??Дождались??! Дисплей по скидону! Новая цена: {} рублёу!".format(new_price)
	else:
		output = "Ждём и надеемся... \U0001F610 Текущая цена {} рублёу.".format(new_price)
	return output


#___________Variables___________
price_bot = BotHandler('401670663:AAELFfb0SSv6qTiTlBTwkzhytSc9bH0cikI')
chat_list = []
price = 7000
now = datetime.datetime.now()
#_______________________________

def main():

	new_offset = None
	today = now.day
	hour = now.hour
	minute = now.minute

	while True:
		price_bot.get_updates(new_offset)
		last_update = price_bot.get_last_update()
		
		if last_update != None
			last_update_id = last_update['update_id']	
			last_chat_id = last_update['message']['chat']['id']
			last_chat_text = last_update['message']['text']

			if last_chat_text == '/start'
				if last_chat_id not in chat_list:
					chat_list.append(last_chat_id)
					price_bot.send_message(last_chat_id, "\U00002705 Вы успешно подписаны на ежедневную рассылку! Информация обновляется в \U0001F559 10 часов 5 минут \U0001F559. Чтобы отписаться от рассылки отправьте \"/stop\"")
					price_bot.send_message(last_chat_id, check_price())

			elif last_chat_text == '/stop':
				chat_list.remove(last_chat_id)
				price_bot.send_message(last_chat_id, "Вы отписались от рассылки. Пок \U0001F618")

			elif last_chat_text == '/info'
				price_bot.send_message(last_chat_id, check_price())

			elif last_chat_text == '/help'
				price_bot.send_message(last_chat_id, 'Возможные команды: /start - подписаться на ежедневную рассылку, /stop - отписаться от рассылки, /info - получить свежую инфу')
		
			if hour == 10 and minute == 5:
				text_mes = check_price()
				for chat in chat_list:
					price_bot.send_message(chat, text_mes)
		
			new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except IndexError:
    	print('Index error')
    except KeyboardInterrupt:
        exit()