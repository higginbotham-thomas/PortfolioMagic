import json
import os
from urllib.request import urlopen

import pandas as pd


def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def get_sma_data(symbol):
    dfs = []
    periods = ['10', '50', '80']
    fmpkey = os.getenv('FMPKEY')
    for period in periods:
        url = f"https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period={period}&type=sma&apikey={fmpkey}"
        data = get_jsonparsed_data(url)
        df = pd.DataFrame(data)
        df = df[['date', 'open', 'high', 'low', 'close', 'sma']]
        df['sma'] = pd.to_numeric(df['sma'])
        df = df.rename(columns={'sma': f'sma_{period}'})
        dfs.append(df)
    merged_df = pd.merge(dfs[0], dfs[1], on=['date', 'open', 'high', 'low', 'close'])
    merged_df = pd.merge(merged_df, dfs[2], on=['date', 'open', 'high', 'low', 'close'])
    merged_df.insert(0, 'symbol', symbol)

    merged_df = merged_df.sort_values(['date'])
    
    # Calculate the MACD line
    merged_df['ema_12'] = merged_df['close'].ewm(span=12, adjust=False).mean()
    merged_df['ema_26'] = merged_df['close'].ewm(span=26, adjust=False).mean()
    merged_df['macd'] = merged_df['ema_12'] - merged_df['ema_26']
    
    # Calculate the signal line
    merged_df['signal'] = merged_df['macd'].ewm(span=9, adjust=False).mean()

    # Calculate the Histogram
    merged_df['histogram'] = merged_df['macd'] - merged_df['signal']

    merged_df = merged_df[['date', 'open', 'high', 'low', 'close', 'sma_10', 'sma_50',
                           'sma_80', 'macd', 'signal', 'histogram']]

    merged_df = merged_df.sort_values(['date'], ascending=[False])

    return merged_df


def get_macd_data(symbol):
    fmpkey = os.getenv('FMPKEY')
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?serietype=line&apikey={fmpkey}"
    data = get_jsonparsed_data(url)
    df = pd.DataFrame.from_dict(pd.json_normalize(get_jsonparsed_data(url), record_path=['historical'],
                                                  meta=['symbol']), orient='columns')
    df = df[['date', 'close']]
    df = df.sort_values(['date'])
    
    # Calculate the MACD line
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    
    # Calculate the signal line
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # Calculate the Histogram
    df['histogram'] = df['macd'] - df['signal']

    df = df[['date', 'macd', 'signal', 'histogram']]

    return df
