
import time
import alpaca_trade_api as tradeapi
from alpaca_trade_api import TimeFrame
from datetime import datetime
import numpy as np

# Setup API information

base_url = "https://paper-api.alpaca.markets"
api_key = "INPUT API KEY HERE"
secret_key = "INPUT SECRET KEY HERE"
stock_choice = input("Please enter the stock symbol you would like to trade.")

# Setup and initialization of REST API connection

api = tradeapi.REST(api_key, secret_key, base_url, api_version = "v2")

# Setup date and time zone

market_open = "09:30:00"
last_call = "15:45:00"
market_close = "16:00:00"

# Welcome message

print("""-----------------------------------------------------------
Taurus is starting up...
-----------------------------------------------------------""")

# Tracking current time

def time_check():
    global start_time
    global current_time

    start_time = time.time()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

time_check()

# Identification of current number of positions held

def get_position():
    positions_qty = api.list_positions()
    result = 0

    for i in positions_qty:
        if int(i.qty) == 1:
            result = 1
        else:
            result = 2

    return result


# Polling data

def data_scrape():
    global stock_data
    stock_data = api.get_bars(stock_choice, TimeFrame.Minute).df

# Calculation of simple moving averages

def sma_indicator():
    data_scrape()
    stock_data["sma_5"] = stock_data["close"].rolling(window=5, min_periods=1).mean()
    stock_data["sma_13"] = stock_data["close"].rolling(window=13, min_periods=1).mean()

    if np.where(stock_data["sma_5"] > stock_data["sma_13"]):
        indicator = 1

    else:
        indicator = 0

    return indicator


# Main logic

while market_open < current_time < last_call:
    time_check()
    if sma_indicator() == 1 and get_position() == 0:
        execute_buy_order = api.submit_order(stock_choice, 1, "buy", "market", "gtc")
        print(execute_buy_order)
        print("You have purchased 1 {} position.\nYou now have 1 open {} position.".format(stock_choice, stock_choice))
        print("Time check: {} \n-----------------------------------------------------------".format(current_time))


    elif sma_indicator() == 1 and get_position() == 1:
        print("Maximum {} positions reached.\nYou still have 1 open {} position.".format(stock_choice, stock_choice))
        print("Time check: {} \n-----------------------------------------------------------".format(current_time))


    else:
        execute_sell_order = api.submit_order(stock_choice, 1, "sell", "market", "gtc")
        print(execute_sell_order)
        print("You have sold 1 {} position./nYou now have 0 open {} positions.".format(stock_choice, stock_choice))
        print("Time check: {} \n-----------------------------------------------------------".format(current_time))



    time.sleep(60.0 - ((time.time() - start_time) % 60.0))


if last_call < current_time < market_close:
    time_check()
    execute_liquidate_order = api.submit_order(stock_choice, 1, "sell", "market", "gtc")
    print(execute_liquidate_order)
    print("-----------------------------------------------------------\n ")
    print("Taurus is shutting down and has liquidated all {} positions.\n".format(stock_choice))
    print("Time check: {}\n".format(time_check()))
    print("-----------------------------------------------------------")




