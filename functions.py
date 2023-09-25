import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

FMPKEY = os.getenv('FMPKEY')

def get_jsonparsed_data(url):
    response = requests.get(url)
    data = response.json()
    return data

def analyze_stocks(symbols):
    results = []

    for symbol in symbols:
        sma200_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=200&type=sma&apikey={FMPKEY}')[0]
        sma100_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=100&type=sma&apikey={FMPKEY}')[0]
        sma50_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=50&type=sma&apikey={FMPKEY}')[0]

        date = sma200_data['date']
        close = sma200_data['close']
        sma200 = sma200_data['sma']
        sma100 = sma100_data['sma']
        sma50 = sma50_data['sma']

        if sma50 > sma200 and sma100 > sma200:
            action = 'BUY'
        else:
            action = 'SELL'

        result = {
            'symbol': symbol,
            'date': date,
            'close_price': close,
            'sma50': sma50,
            'sma100': sma100,
            'sma200': sma200,
            'action': action
        }

        results.append(result)

    return results