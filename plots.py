import matplotlib.dates as mdates
import matplotlib.pyplot as plt
#import mplfinance as mpf
import pandas as pd
from dateutil.parser import parse as parse_date

import fndata


def plot_sma(sym_list):
    # Define the number of rows and columns for the subplot grid
    n_rows = len(sym_list) // 2 + len(sym_list) % 2
    n_cols = 2

    # Create the subplot grid
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(30, 8 * n_rows))

    # Flatten the axs array to iterate through all subplots
    axs = axs.flatten()

    # Loop through each symbol in the list and plot the SMA data
    for i, symbol in enumerate(sym_list):
        # Get the SMA data for the current symbol
        sma_data = fndata.get_sma_data(symbol)

        sma_data.loc[(sma_data['sma_50'] > sma_data['sma_200']) & (
                sma_data['sma_100'] > sma_data['sma_200']), 'Action'] = 'BUY'
        # & (sma_data['sma_100'] > sma_data['sma_200'])
        # & (sma_data['sma_50'] > sma_data['sma_200'])
        sma_data.loc[(sma_data['sma_50'] < sma_data['sma_100']), 'Action'] = 'SELL'
        sma_data.loc[(sma_data['sma_100'] < sma_data['sma_200']), 'Action'] = 'SELL'
        sma_data = sma_data.fillna('')
        # sma_data = sma_data.fillna(method='ffill')
        sma_data["isStatusChanged"] = sma_data["Action"].shift(
            -1, fill_value=sma_data["Action"].head(1)) != sma_data["Action"]
        sma_data['Action'] = sma_data['Action'].astype('string')

        # sma_filtered = sma_data[(sma_data["isStatusChanged"] == True) & (sma_data["Action"] != "")]

        sma_filtered = sma_data[(sma_data["isStatusChanged"]) & (sma_data["Action"] != "")]

        plot_data = sma_data.head(500)
        plot_data = plot_data.iloc[::-1]

        # Set the date column as the index
        plot_data.set_index('date', inplace=True)

        # Convert dates to a numeric format recognized by matplotlib
        plot_data.index = [mdates.date2num(
            parse_date(d)) for d in plot_data.index]

        # Set up the plot
        axs[i].set_ylabel('Price')
        axs[i].yaxis.tick_left()  # Plot the Y-axis ticks and labels on the right-hand side
        axs[i].tick_params(axis='x', which='major', labelsize=8, rotation=0)

        # Set the tick frequency and format for the X-axis
        axs[i].xaxis.set_major_locator(mdates.DayLocator(interval=90))
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        axs[i].set_title(f"{symbol} Price and Moving Averages", fontsize=10)
        axs[i].set_ylabel('Price', fontsize=8)

        # Create a twin axis for MACD and signal lines
        axs_macd = axs[i].twinx()
        axs_macd.plot(plot_data.index, plot_data['macd'], label='MACD', color='blue')
        axs_macd.plot(plot_data.index, plot_data['signal'], label='Signal', color='red')
        axs_macd.tick_params(axis='y', labelcolor='blue')

        # Add MACD histogram
        axs_macd.bar(plot_data.index, plot_data['histogram'], label='Histogram', color='gray', alpha=0.5)

        # Set the y-axis limits for the twin axis
        ymin = min(plot_data['sma_50'].min(), plot_data['sma_100'].min(), plot_data['sma_200'].min(),
                   plot_data['close'].min(), plot_data['macd'].min(), plot_data['signal'].min())
        ymax = max(plot_data['macd'].max(), plot_data['signal'].max()) + 30

        axs_macd.set_ylim(ymin=ymin, ymax=ymax)

        # Plot the historical prices and moving averages
        axs[i].plot(plot_data.index, plot_data['close'], label='Close')
        axs[i].plot(plot_data.index,
                    plot_data['sma_50'], color='green', label='SMA 50')
        axs[i].plot(plot_data.index,
                    plot_data['sma_100'], color='black', label='SMA 100')
        axs[i].plot(plot_data.index,
                    plot_data['sma_200'], color='red', label='SMA 200')

        # Add checkmarks for buy and sell points
        buy_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
                plot_data['Action'] == 'BUY')]
        sell_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
                plot_data['Action'] == 'SELL')]

        axs[i].scatter(buy_points.index,
                       buy_points['close'], marker='^', s=150, c='green', label='BUY')
        axs[i].scatter(sell_points.index,
                       sell_points['close'], marker='v', s=150, c='red', label='SELL')

        axs[i].legend()

    # Hide any unused axes
    for i in range(len(sym_list), n_cols * n_rows):
        axs[i].axis('off')

    plt.tight_layout()
    plt.show()


'''A new function to plot a single stock's price and moving averages'''


def plot_sma_single(symbol):
    # Get the SMA data for the current symbol
    sma_data = fndata.get_sma_data(symbol)

    sma_data.loc[(sma_data['sma_50'] > sma_data['sma_200']) & (
            sma_data['sma_100'] > sma_data['sma_200']), 'Action'] = 'BUY'
    # & (sma_data['sma_100'] > sma_data['sma_200'])
    # & (sma_data['sma_50'] > sma_data['sma_200'])
    sma_data.loc[(sma_data['sma_50'] < sma_data['sma_100']), 'Action'] = 'SELL'
    sma_data.loc[(sma_data['sma_100'] < sma_data['sma_200']), 'Action'] = 'SELL'
    sma_data = sma_data.fillna('')
    # sma_data = sma_data.fillna(method='ffill')
    sma_data["isStatusChanged"] = sma_data["Action"].shift(
        -1, fill_value=sma_data["Action"].head(1)) != sma_data["Action"]
    sma_data['Action'] = sma_data['Action'].astype('string')

    # sma_filtered = sma_data[(sma_data["isStatusChanged"] == True) & (sma_data["Action"] != "")]

    sma_filtered = sma_data[(sma_data["isStatusChanged"]) & (sma_data["Action"] != "")]

    plot_data = sma_data.head(500)
    plot_data = plot_data.iloc[::-1]

    # Set the date column as the index
    plot_data.set_index('date', inplace=True)

    # Convert dates to a numeric format recognized by matplotlib
    plot_data.index = [mdates.date2num(
        parse_date(d)) for d in plot_data.index]

    # Set up the plot
    fig, axs = plt.subplots(figsize=(30, 8))
    axs.set_ylabel('Price')
    axs.yaxis.tick_left()  # Plot the Y-axis ticks and labels on the right-hand side
    axs.tick_params(axis='x', which='major', labelsize=8, rotation=0)

    # Set the tick frequency and format for the X-axis
    axs.xaxis.set_major_locator(mdates.DayLocator(interval=90))
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    axs.set_title(f"{symbol} Price and Moving Averages", fontsize=10)

    # Create a twin axis for MACD and signal lines

    axs_macd = axs.twinx()
    axs_macd.plot(plot_data.index, plot_data['macd'], label='MACD', color='blue')
    axs_macd.plot(plot_data.index, plot_data['signal'], label='Signal', color='red')
    axs_macd.tick_params(axis='y', labelcolor='blue')

    # Add MACD histogram
    axs_macd.bar(plot_data.index, plot_data['histogram'], label='Histogram', color='gray', alpha=0.5)

    # Set the y-axis limits for the twin axis
    ymin = min(plot_data['sma_50'].min(), plot_data['sma_100'].min(), plot_data['sma_200'].min(),
               plot_data['close'].min(), plot_data['macd'].min(), plot_data['signal'].min())
    ymax = max(plot_data['macd'].max(), plot_data['signal'].max()) + 30

    axs_macd.set_ylim(ymin=ymin, ymax=ymax)

    # Plot the historical prices and moving averages
    axs.plot(plot_data.index, plot_data['close'], label='Close')
    axs.plot(plot_data.index,
             plot_data['sma_50'], color='green', label='SMA 50')
    axs.plot(plot_data.index,
             plot_data['sma_100'], color='black', label='SMA 100')
    axs.plot(plot_data.index,
             plot_data['sma_200'], color='red', label='SMA 200')

    # Add checkmarks for buy and sell points
    buy_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
            plot_data['Action'] == 'BUY')]
    sell_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
            plot_data['Action'] == 'SELL')]
    axs.scatter(buy_points.index,
                buy_points['close'], marker='^', s=150, c='green', label='BUY')
    axs.scatter(sell_points.index,
                sell_points['close'], marker='v', s=150, c='red', label='SELL')

    axs.legend(loc='upper left', bbox_to_anchor=(0, 1), ncol=2)
    axs_macd.legend(loc='upper right', bbox_to_anchor=(1, 1), ncol=2)

    plt.show()


'''A new function to plot a single stock's price with ohlc candlesticks and moving averages'''


def plot_candlestick_single(symbol):
    # Get the SMA data for the current symbol

    sma_data = fndata.get_sma_data(symbol)

    sma_data.loc[(sma_data['sma_50'] > sma_data['sma_200']) & (
            sma_data['sma_100'] > sma_data['sma_200']), 'Action'] = 'BUY'
    # & (sma_data['sma_100'] > sma_data['sma_200'])
    # & (sma_data['sma_50'] > sma_data['sma_200'])
    sma_data.loc[(sma_data['sma_50'] < sma_data['sma_100']), 'Action'] = 'SELL'
    sma_data.loc[(sma_data['sma_100'] < sma_data['sma_200']), 'Action'] = 'SELL'
    sma_data = sma_data.fillna('')
    # sma_data = sma_data.fillna(method='ffill')
    sma_data["isStatusChanged"] = sma_data["Action"].shift(
        -1, fill_value=sma_data["Action"].head(1)) != sma_data["Action"]
    sma_data['Action'] = sma_data['Action'].astype('string')

    # sma_filtered = sma_data[(sma_data["isStatusChanged"] == True) & (sma_data["Action"] != "")]

    sma_filtered = sma_data[(sma_data["isStatusChanged"]) & (sma_data["Action"] != "")]

    plot_data = sma_data.head(500)
    plot_data = plot_data.iloc[::-1]

    # Set the date column as the index
    plot_data['date'] = pd.to_datetime(plot_data['date'])
    plot_data.set_index('date', inplace=True)
    plot_data = plot_data.drop(pd.Timestamp.today().strftime('%Y-%m-%d'))

    plot_data.fillna(method='ffill', inplace=True)

    # define the market colors
    mc = mpf.make_marketcolors(up='g', down='r')

    # create the mpf style
    style = mpf.make_mpf_style(marketcolors=mc)

    # Set up the plot
    fig, axs = mpf.plot(plot_data, type='candle', mav=(50, 100, 200), volume=False, style=style, returnfig=True,
                        xlim=(len(plot_data) - 365, len(plot_data)))

    # Add checkmarks for buy and sell points
    buy_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
            plot_data['Action'] == 'BUY')]
    sell_points = plot_data[(plot_data['isStatusChanged'] == 1) & (
            plot_data['Action'] == 'SELL')]
    axs[0].scatter(buy_points.index,
                   buy_points['close'], marker='^', s=150, c='green', label='BUY')
    axs[0].scatter(sell_points.index,
                   sell_points['close'], marker='v', s=150, c='red', label='SELL')

    plt.show()
