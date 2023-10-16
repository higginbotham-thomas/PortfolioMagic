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
        sma80_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=80&type=sma&apikey={FMPKEY}')[0]
        sma50_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=50&type=sma&apikey={FMPKEY}')[0]
        sma20_data = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=20&type=sma&apikey={FMPKEY}')[0]

        date = sma80_data['date']
        close = sma80_data['close']
        sma80 = sma80_data['sma']
        sma50 = sma50_data['sma']
        sma20 = sma20_data['sma']

        if float(sma20) > float(sma50) > float(sma80):
            action = 'BUY'
        else:
            action = 'SELL'

        result = {
            'symbol': symbol,
            'date': date,
            'close_price': close,
            'sma50': sma20,
            'sma100': sma50,
            'sma200': sma80,
            'action': action
        }

        results.append(result)

    return results
