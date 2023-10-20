from flask import Flask, render_template, request
from datetime import datetime
import main
#import pandas as pd
import locale
import functions

app = Flask(__name__)

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


@app.route('/', methods=['GET', 'POST'])
def display_json_as_table():
    if request.method == 'POST':
        selected_account = request.form['account']
        # Update data based on the selected_account (e.g., filter data)
        # Call the analyze_stocks function with the updated data
        # Filter the DataFrame based on the selected account
        updated_symbols = main.df_accounts[main.df_accounts['Account'] == selected_account]['Symbol'].tolist()

        json_data = functions.analyze_stocks(updated_symbols)
    else:
        # If it's a GET request, load the default data
        json_data = main.results

    for record in json_data:
        # Convert "close_price" to float before formatting as currency
        record['close_price'] = float(record['close_price'])
        # Parse the date string into a date object
        if isinstance(record['date'], str):
            record['date'] = datetime.strptime(record['date'], '%Y-%m-%d %H:%M:%S')

    # Assuming you have pandas DataFrame, you can convert it to HTML
    # If your data is not in a DataFrame, you might need to format it accordingly
    #if isinstance(json_data, pd.DataFrame):
    #    table_html = json_data.to_html(classes='table table-striped')
    #else:
        # Handle non-DataFrame JSON data here
    #    table_html = "<p>No data to display</p>"

    # return render_template('table_action.html', json_data=json_data)
    return render_template('table_action.html', json_data=json_data, unique_accounts=main.unique_accounts,
                           selected_account=main.selected_account)


if __name__ == '__main__':
    app.run()
