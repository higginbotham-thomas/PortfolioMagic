"""Module with shared functions for the app"""
from datetime import datetime, timedelta
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


# Function to compute buy/sell recommendations
def compute_buy_sell_recommendations(
        current_portfolio, acct, highest_sharpe_weights, stocks, stock_history
):
    """Function to compute buy/sell recommendations"""
    # Convert weights to desired monetary value in the portfolio
    desired_values = np.array(highest_sharpe_weights) * acct  # Convert to NumPy array

    # Get the latest stock prices
    current_prices = {stock: stock_history[stock].iloc[-1] for stock in stocks}

    # Calculate desired shares (decimal value)
    desired_shares_decimal = {
        stock: desired_values[i] / current_prices[stock] for i, stock in enumerate(stocks)}

    # Calculate Buy/Sell (rounded value)
    buy_sell_shares = \
        {stock: (desired_shares_decimal[stock]) -
            current_portfolio[current_portfolio['Symbol'] == stock]['Shares'].values[0]
         for stock in stocks}

    # Merge current portfolio with desired shares
    merged_portfolio = current_portfolio.merge(pd.DataFrame(
        buy_sell_shares.items(), columns=['Symbol', 'Buy/Sell']), on='Symbol')

    # Calculate other columns
    merged_portfolio['CurrentSharePrice'] = merged_portfolio['Symbol'].map(
        current_prices)
    merged_portfolio['TargetValue'] = merged_portfolio['Symbol'].map(
        dict(zip(stocks, desired_values)))
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
        dict(zip(stocks, highest_sharpe_weights))) * 100
    merged_portfolio['ActualWeightAfterAction'] = merged_portfolio['ValueAfterAction'] / \
        (merged_portfolio['ValueAfterAction'].sum()) * \
        100  # Convert to percentage

    # Sort dataframe by 'Buy/Sell' column with negative values first
    merged_portfolio = merged_portfolio.sort_values(
        by='Buy/Sell', ascending=True)  # Sell first, settle, then buy

    return merged_portfolio[['Symbol', 'Buy/Sell', 'CurrentSharePrice', 'CurrentValue',
                             'Shares', 'TargetValue', 'ValueAfterAction', 'SharesAfterAction',
                             'TargetSharpeWeight', 'ActualWeightAfterAction']]


def get_treasury_data(api_key):
    """Function to get the latest stock prices"""
    # Get today's date
    today = datetime.today()

    # Check if today is Monday (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    if today.weekday() in [0, 6]:
        # If today is Monday, set from_date to the previous Friday
        from_date = (today - timedelta(days=3)).strftime('%Y-%m-%d')
    else:
        # Otherwise, set from_date to yesterday
        from_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    # Format the dates in 'YYYY-MM-DD' format
    to_date = today.strftime('%Y-%m-%d')

    # Construct the URI
    base_url = "https://financialmodelingprep.com/api/v4/treasury"
    url = f"?from={from_date}&to={to_date}&apikey={api_key}"
    uri = f"{base_url}{url}"

    # Make the GET request
    response = requests.get(uri, timeout=10)

    # Return the JSON response
    return response.json()


def get_stock_history(stocks, number_of_days, api_key):
    """Function to get the latest stock prices"""
    stock_history = {}
    base_url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    for stock in stocks:
        url = f'{base_url}{stock}?serietype=line&apikey={api_key}'
        try:
            response = requests.get(url, timeout=10)
            # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            prices = response.json()
            prices_df = pd.DataFrame(prices['historical'])

            # Ensure the data is sorted by date in descending order (most recent first)
            prices_df['date'] = pd.to_datetime(prices_df['date'])
            prices_df = prices_df.sort_values('date', ascending=False)

            # Select closing prices for the chosen number of days
            recent_prices = prices_df.head(number_of_days).set_index('date')['close']
            stock_history[stock] = recent_prices
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except KeyError:
            print(f"Error: No data found for stock {stock}")

    return stock_history


def get_return_stocks(stock_history):
    """Function to get returns for the latest stock prices"""
    # Concatenate all stock close prices into a single dataframe
    portfolio = pd.concat(stock_history, axis=1)
    # Calculate daily returns
    return_stocks = portfolio.pct_change().dropna()
    # Return the daily returns and stock history
    return return_stocks


def get_montecarlo_simulation(args):
    """
    Calculate the portfolio returns, risks, Sharpe ratios,
    and weights for a given set of parameters.

    Args:
        args (dict): Dictionary containing the following keys:
            - number_of_portfolios (int): The number of portfolios to simulate.
            - stocks (list): List of stock tickers.
            - return_stocks (DataFrame): DataFrame containing the stock returns.
            - trading_days (int): The number of trading days in a year.
            - rf (float): The risk-free rate.
            - risk (float): The maximum acceptable portfolio risk.

    Returns:
        DataFrame: A DataFrame containing the portfolio returns, risks, Sharpe ratios, and weights.
    """
    number_of_portfolios, stocks, return_stocks, trading_days, rf, risk = args.values()
    matrix_covariance_portfolio = (return_stocks.cov()) * trading_days

    portfolios = {
        'returns': [],
        'risks': [],
        'sharpes': [],
        'weights': [],
    }

    for _ in range(number_of_portfolios):
        weights = np.random.random_sample(len(stocks))
        weights /= np.sum(weights)
        returns = np.sum((return_stocks.mean() * weights) * trading_days) - rf
        portfolios['returns'].append(returns)

        portfolio_variance = np.dot(weights.T, np.dot(matrix_covariance_portfolio, weights))
        portfolios['risks'].append(np.sqrt(portfolio_variance))

        portfolios['sharpes'].append((returns - rf) / np.sqrt(portfolio_variance))

        portfolios['weights'].append(weights)

    indices_within_risk = np.where(np.array(portfolios['risks']) <= risk)[0]

    df = pd.DataFrame({
        'Port Returns': np.array(portfolios['returns'])[indices_within_risk],
        'Port Risk': np.array(portfolios['risks'])[indices_within_risk],
        'Sharpe Ratio': np.array(portfolios['sharpes'])[indices_within_risk],
        'Portfolio Weights': np.array(portfolios['weights'])[indices_within_risk].tolist(),
    })

    for col in ['Port Returns', 'Port Risk', 'Sharpe Ratio']:
        df[col] = df[col].astype(float)

    return df


def get_recommendations(portfolio_dfs, current_portfolio, acct, stocks, stock_history):
    """Function to get the rebalance recommendations"""
    highest_sharpe_port = portfolio_dfs.iloc[portfolio_dfs['Sharpe Ratio'].idxmax()]
    highest_sharpe_weights = highest_sharpe_port['Portfolio Weights']

    # Get buy/sell recommendations
    recommendations = compute_buy_sell_recommendations(
        current_portfolio, acct, highest_sharpe_weights, stocks, stock_history)

    recommendations = recommendations.loc[(recommendations['CurrentValue']
                                           != recommendations['ValueAfterAction']) |
                                          ((recommendations['CurrentValue'] != 0) &
                                           (recommendations['ValueAfterAction'] != 0))]

    return recommendations


def plot_portfolio_metrics(portfolio_dfs, number_of_portfolios, acct, rf, risk):
    """Function to plot the portfolio metrics (returns, risk, sharpe ratio)"""
    highest_sharpe_port = portfolio_dfs.iloc[portfolio_dfs['Sharpe Ratio'].idxmax()]

    # First Graphic: Text String Block
    _, ax1 = plt.subplots(figsize=(15, 5))

    # Add text annotations
    textstr = "Portfolio Metrics for the Highest Sharpe Ratio Portfolio:\n\n"
    textstr += f"Number of portfolios analyzed: {number_of_portfolios}\n"
    textstr += f"Returns: {highest_sharpe_port['Port Returns'] * 100:.2f}%\n"
    textstr += f"Risk (Standard Deviation): {highest_sharpe_port['Port Risk'] * 100:.2f}%\n"
    textstr += f"Sharpe Ratio: {highest_sharpe_port['Sharpe Ratio']:.2f}\n\n"
    textstr += f"Portfolio Value: ${acct:.2f}\n"
    textstr += f"Risk Free Rate: {rf * 100:.2f}%\n\n"
    textstr += f"Selected Risk Tolerance: {risk * 100:.2f}%:\n"

    # Place the text on the figure
    ax1.text(0.05, 0.7, textstr, transform=ax1.transAxes, fontsize=12, verticalalignment='top',
             horizontalalignment='left')

    # Hide the axes
    ax1.axis('off')

    # Show the figure
    plt.show()


def plot_portfolio_changes(recommendations):
    """Function to plot the portfolio changes"""

    # Round and format the values in the specified columns
    recommendations['Shares'] = recommendations['Shares'].apply(lambda x: f"{x:.4f}")
    recommendations['SharesAfterAction'] = recommendations['SharesAfterAction'] \
        .apply(lambda x: f"{x:.4f}")
    recommendations['TargetSharpeWeight'] = recommendations['TargetSharpeWeight'].round(2)
    recommendations['ActualWeightAfterAction'] = recommendations['ActualWeightAfterAction'].round(2)

    # Second Graphic: Table of Recommendations
    _, ax2 = plt.subplots(figsize=(15, 5))

    # Create a table for the recommendations
    table_data = []
    columns = recommendations.columns.tolist()
    table_data.append(columns)
    for row in recommendations.itertuples():
        table_data.append(row[1:])

    # Add table to the figure
    _ = ax2.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.2]
                  * len(columns), bbox=[0, 0, 1, 1],
                  fontsize=18)

    # Hide the axes
    ax2.axis('off')

    # Show the figure
    plt.show()


def plot_risk_scatterplot(portfolio_dfs):
    """Function to create a dataframe with the returns and risk value for each portfolio"""
    portfolio_returns = portfolio_dfs['Port Returns']
    portfolio_risk = portfolio_dfs['Port Risk']

    plt.figure(figsize=(15, 15))
    plt.scatter(portfolio_risk, portfolio_returns, c=portfolio_returns / portfolio_risk)
    plt.xlabel('Volatility (Risk)')
    plt.ylabel('Returns')
    plt.colorbar(label='Sharpe ratio')
    plt.title('Tested Portfolios (Returns vs Volatility)')

    plt.show()


def plot_correlation_matrix(return_stocks):
    """Function to plot the correlation matrix"""

    # Calculate the correlation matrix
    correlation_matrix = return_stocks.corr()

    # Visualize the correlation matrix using a heatmap
    plt.figure(figsize=(15, 15))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
    plt.title("Correlation Matrix of Asset Returns")
    plt.show()
