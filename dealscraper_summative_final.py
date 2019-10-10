#Library imports

import requests
from bs4 import BeautifulSoup
import smtplib
from sinchsms import SinchSMS
import schedule, time
import csv
from datetime import datetime
import pytz
import pandas as pd
import plotly.express as px

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

#game search def, establishes game title, url, and threshold price based on user input

def game_search():
    
    print("Please type in the game title you'd like to search")
    search_string_init = input()
    search_string_final = search_string_init.replace(" ","+")
    print(search_string_final)
    search_url = "https://isthereanydeal.com/search/?q=" + search_string_final
    search_page = requests.get(search_url, headers=headers)

    search_soup = BeautifulSoup(search_page.content, 'lxml')
    global final_url
    final_url = search_soup.find(class_="card__title").get('href')
    print(final_url)

    print("At what price should we notify you?")
    global threshold_price
    threshold_price = float(input())


#Scraping def, gets game price data from the website

def price_check():
    
    check_url = "https://isthereanydeal.com" + final_url

    page = requests.get(check_url, headers=headers)

    soup = BeautifulSoup(page.content, 'lxml')

    global title 
    title = soup.find(id="gameTitle").get_text()
    global price 
    price = [float(p.get_text()[1:]) for p in soup.find_all(class_='gh-po__price')]

    global converted_price 
    converted_price = float(price[1])

    print(title)
    print(price)
    print(converted_price)

    # Time logging 

    tz = pytz.timezone('Asia/Kolkata')

    log_time = datetime.now()
    log_time = log_time.replace(tzinfo = tz)
    log_time = log_time.astimezone(tz)
    
    #Save data to CSV for visualization

    row = [title, converted_price, threshold_price, log_time]
    with open('game_price_history_summative.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()

    if(converted_price < threshold_price):
        send_sms()

    #Opens updated graph of Game Price/Time

    df = pd.read_csv('game_price_history_summative.csv')

    fig = px.line(df, x = 'Time', y = 'Current Price', title= title + 'Price Over Time')
    fig.show()
        
#Sends SMS using API

def send_sms():

    title_id = str(title)
    price_value = str(converted_price)
    number = "phone_number"
    message = title_id + " is available for $ " + price_value +  ", buy it now!"
    client = SinchSMS("app_key", "app_token")

    print("Sending '%s' to %s" % (message, number))
    response = client.send_message(number, message)
    message_id = response['messageId']

    response = client.check_status(message_id)
    while response['status'] != 'Successful':
        print(response['status'])
        time.sleep(5)
        response = client.check_status(message_id)
        print(response['status'])

def main():
    game_search()
    price_check()

main()

#Calls price_check every ten seconds to keep updating price

schedule.every(10).seconds.do(price_check)

while True:
    schedule.run_pending()
    time.sleep(1)