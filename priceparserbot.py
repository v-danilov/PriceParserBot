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
        	last_update = None
        return last_update

class FileHandler:

	def __init__(self, file_name):
		self.file_name = file_name

	def write_line(self, line):
		file = open(self.file_name,'a')
		file.write(str(line) + '\n')
		file.close()

	def write_list(self, list_lines):
		file = open(self.file_name, 'w')
		for ln in list_lines:
			file.write(str(ln) + '\n')
		file.close()

	def read_lines(self):
		file = open(self.file_name, 'r')
		lines = file.read().splitlines()
		file.close()
		list_ids = list(map(int, lines))
		return list_ids

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
		output = "🎉Дождались🎉! Дисплей по скидону! Новая цена: <b>{}</b> рублёу!".format(new_price)
	else:
		output = "Ждём и надеемся... \U0001F610 Текущая цена <b>{}</b> рублёу.".format(new_price)
	return output


#___________Variables___________
price_bot = BotHandler('401670663:AAELFfb0SSv6qTiTlBTwkzhytSc9bH0cikI')
file_handler = FileHandler("ulist.txt")
chat_list = []
price = 7000

#_______________________________

def main():

	new_offset = None
	print(file_handler.read_lines())
	chat_list = file_handler.read_lines()
	
	while True:

			now = datetime.datetime.now()
			today = now.day
			hour = now.hour
			minute = now.minute

			price_bot.get_updates(new_offset)
			last_update = price_bot.get_last_update()
			
			if last_update is not None:
				last_update_id = last_update['update_id']	
				last_chat_id = last_update['message']['chat']['id']
				last_chat_text = last_update['message']['text']

				if last_chat_text == '/start':
					print(file_handler.read_lines())
					if last_chat_id not in chat_list:
						chat_list.append(last_chat_id)
						price_bot.send_message(last_chat_id, "\U00002705 Вы успешно подписаны на ежедневную рассылку! Информация обновляется в \U0001F559 10 часов 5 минут \U0001F559. Чтобы отписаться от рассылки отправьте \"/stop\"")
						price_bot.send_message(last_chat_id, check_price())
						file_handler.write_line(last_chat_id)
					else:
						price_bot.send_message(last_chat_id, 'Ты уже подписан. Попробуй это: /help')

				elif last_chat_text == '/stop':
					if last_chat_id in chat_list:
						chat_list.remove(last_chat_id)
						price_bot.send_message(last_chat_id, "Вы отписались от рассылки. Пок \U0001F618")
						file_handler.write_list(chat_list)

				elif last_chat_text == '/info':
					price_bot.send_message(last_chat_id, check_price())

				elif last_chat_text == '/help':
					price_bot.send_message(last_chat_id, 'Возможные команды: /start - подписаться на ежедневную рассылку, /stop - отписаться от рассылки, /info - получить свежую инфу')
			
				new_offset = last_update_id + 1

			if (hour == 17 and minute == 0) or (hour == 7 and minute == 5):
				print("Daily update for {} user(s)".format(len(chat_list)))
				text_mes = check_price()
				for chat in chat_list:
					price_bot.send_message(chat, text_mes)



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
    
    
    	
    	
