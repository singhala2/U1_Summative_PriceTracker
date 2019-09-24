import requests
from bs4 import BeautifulSoup
import smtplib
from sinchsms import SinchSMS
import time

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

def game_search():
    
    print("Please type in the game title you'd like to search")
    search_string_init = input()
    search_string_final = search_string_init.replace(" ","+")
    print(search_string_final)
    search_url = "https://isthereanydeal.com/search/?q=" + search_string_final
    search_page = requests.get(search_url, headers=headers)

    search_soup = BeautifulSoup(search_page.content, 'lxml')
    final_url = search_soup.find(class_="card__title".href).get_text()


def price_check():

    page = requests.get(final_url, headers=headers)

    soup = BeautifulSoup(page.content, 'lxml')

    global title 
    title = soup.find(id="gameTitle").get_text()
    global price 
    price = [float(p.get_text()[1:]) for p in soup.find_all(class_='gh-po__price')]

    global converted_price 
    converted_price = float(price[1])

    print(title)
    print(price)
    #print(price[1].get_text())
    print(converted_price)

    print("At what price should we notify you?")
    threshold_price = input()

    if(converted_price < threshold_price):
        send_sms()


def send_sms():

    title_id = str(title)
    price_value = str(converted_price)
    number = '+your_phone_number'
    message = title_id + " is available for $ " + price_value +  ", buy it now!"
    client = SinchSMS("app_key", "app_secret")

    print("Sending '%s' to %s" % (message, number))
    response = client.send_message(number, message)
    message_id = response['messageId']

    response = client.check_status(message_id)
    while response['status'] != 'Successful':
        print(response['status'])
        time.sleep(5)
        response = client.check_status(message_id)
        print(response['status'])

game_search()
price_check()