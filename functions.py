import os

import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('FMPKEY')


# Function to compute buy/sell recommendations
def compute_buy_sell_recommendations(current_portfolio, acct, highest_sharpe_weights, stocks, stock_history):
    # Convert weights to desired monetary value in the portfolio
    desired_values = highest_sharpe_weights * acct

    # Get the latest stock prices
    current_prices = {stock: stock_history[stock].iloc[-1] for stock in stocks}

    # Calculate desired shares (decimal value)
    desired_shares_decimal = {
        stock: desired_values[i] / current_prices[stock] for i, stock in enumerate(stocks)}

    # Calculate Buy/Sell (rounded value)
    buy_sell_shares = \
        {stock: (desired_shares_decimal[stock]) -
            current_portfolio[current_portfolio['Symbol'] == stock]['Shares'].values[0] for stock in stocks}

    # Merge current portfolio with desired shares
    merged_portfolio = current_portfolio.merge(pd.DataFrame(
        buy_sell_shares.items(), columns=['Symbol', 'Buy/Sell']), on='Symbol')

    # Calculate other columns
    merged_portfolio['CurrentSharePrice'] = merged_portfolio['Symbol'].map(
        current_prices)
    merged_portfolio['TargetValue'] = merged_portfolio['Symbol'].map(
        {stock: value for stock, value in zip(stocks, desired_values)})
    merged_portfolio['TargetValue'] = merged_portfolio['TargetValue'].round(2)
    merged_portfolio['CurrentValue'] = merged_portfolio['Shares'] * \
        merged_portfolio['CurrentSharePrice']
    merged_portfolio['CurrentValue'] = merged_portfolio['CurrentValue'].round(
        2)
    merged_portfolio['Buy/Sell'] = (merged_portfolio['Buy/Sell']).round(0)
    merged_portfolio['SharesAfterAction'] = merged_portfolio['Shares'] + \
        merged_portfolio['Buy/Sell']
    merged_portfolio['ValueAfterAction'] = merged_portfolio['SharesAfterAction'] * \
        merged_portfolio['CurrentSharePrice']
    merged_portfolio['ValueAfterAction'] = merged_portfolio['ValueAfterAction'].round(
        2)
    merged_portfolio['TargetSharpeWeight'] = merged_portfolio['Symbol'].map(
        {stock: weight for stock, weight in zip(stocks, highest_sharpe_weights)})*100  # Convert to percentage
    merged_portfolio['ActualWeightAfterAction'] = merged_portfolio['ValueAfterAction'] / \
        (merged_portfolio['ValueAfterAction'].sum()) * \
        100  # Convert to percentage

    # Sort dataframe by 'Buy/Sell' column with negative values first
    merged_portfolio = merged_portfolio.sort_values(
        by='Buy/Sell', ascending=True)  # Sell first, settle, then buy

    return merged_portfolio[['Symbol', 'Buy/Sell', 'CurrentSharePrice', 'CurrentValue', 'Shares', 'TargetValue',
                             'ValueAfterAction', 'SharesAfterAction', 'TargetSharpeWeight', 'ActualWeightAfterAction']]


def get_treasury_data():
    api_key = API_KEY
    # Get today's date
    today = datetime.today()

    # Get yesterday's date
    yesterday = today - timedelta(days=1)

    # Format the dates in 'YYYY-MM-DD' format
    from_date = yesterday.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    # Construct the URI
    uri = f"https://financialmodelingprep.com/api/v4/treasury?from={from_date}&to={to_date}&apikey={api_key}"

    # Make the GET request
    response = requests.get(uri)

    # Return the JSON response
    return response.json()
