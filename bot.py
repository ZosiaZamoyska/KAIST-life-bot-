import telebot
import requests
import json
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

bot = telebot.TeleBot('911305435:AAGXq7c4Qf3tUBbF4-7nZ_vYqmj4LeRaX84')
TOKEN = '911305435:AAGXq7c4Qf3tUBbF4-7nZ_vYqmj4LeRaX84'
def get_menu(selector, date=None):
    URL = 'http://www.kaist.edu/_prog/fodlst/?site_dvs_cd=en'

    if date:
        URL += '&stt_dt=' + date

    response = requests.get(URL)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.select(selector)
    elem = elems[0]
    menu = elem.get_text()

    return menu

def get_photo():
    URL = 'https://dog.ceo/api/breeds/image/random'

    response = requests.get(URL)
    html = response.content

    soup = str(BeautifulSoup(html, 'html.parser'))

    return soup

def get_time():
    URL = 'http://www.kaist.edu/html/en/kaist/kaist_010701.html'

    response = requests.get(URL)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    schedule = soup.find_all(rowspan="2")
    return schedule

def main():
    # https://api.telegram.org/bot<token>/METHOD_NAME

    offset = 0

    while True:
        params = {
            'offset': offset,
            'timeout': 30,
        }
        api_url = 'https://api.telegram.org/bot' + TOKEN + '/getUpdates'
        data = requests.get(api_url, data=params).json()
        print('data', data)

        if not data['ok']:
            continue

        updates = data['result']

        for update in updates:
            offset = max(offset, update['update_id'] + 1)
            print(update['update_id'], update['message']['text'])

            message = update['message']
            text = message['text']
            chat_id = message['chat']['id']

            breakfast_selector = '#txt > table > tbody > tr > td:nth-child(1)'
            lunch_selector =     '#txt > table > tbody > tr > td:nth-child(2)'
            dinner_selector = '#txt > table > tbody > tr > td:nth-child(3)'

            if text == '/breakfast':
                answer = 'BREAKFAST\n\n' + get_menu(breakfast_selector)
            elif text == '/lunch':
                answer = 'LUNCH\n\n' + get_menu(lunch_selector)
            elif text == '/dinner':
                # dinner_selector = '#txt > table > tbody > tr > td.t_end'
                answer = 'DINNER\n\n' + get_menu(dinner_selector)
            elif text == '/tomorrow':
                tmr = date.today() + timedelta(days=1)
                tmr_str = tmr.isoformat()
                breakfast = get_menu(breakfast_selector, tmr_str)
                lunch = get_menu(lunch_selector, tmr_str)
                dinner = get_menu(dinner_selector, tmr_str)
                answer = ( '### TOMORROW ###\n\n'
                           'BREAKFAST\n-----------\n' + breakfast + '\n\n'
                           'LUNCH\n-----------\n' + lunch + '\n\n'
                           'DINNER\n-----------\n' + dinner + '\n\n' )
            elif text == 'Im sad':
                j = json.loads(get_photo())
                image = j['message']
                answer = image
            elif text == 'bus':
                current_time = str(datetime.now().time()).split(':')
                answer = str(get_time())
            else:
                answer = ( 'I dont get it 😔\n'
                           'You can use following commands:\n'
                           '- /breakfast\n'
                           '- /lunch\n'
                           '- /dinner\n' )

            api_url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
            params = {
                'chat_id': chat_id,
                'text': answer,
            }
            requests.post(api_url, data=params).json()

main()

bot.polling(none_stop=False, interval=0, timeout=5)