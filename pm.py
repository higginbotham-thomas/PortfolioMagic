from flask import Flask, render_template
from datetime import date, datetime
import main # Import main.py module
import pandas as pd
import locale


app = Flask(__name__)

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

@app.route('/')
def display_json_as_table():
    # Call a function from main.py to get JSON data
    json_data = main.results

    for record in json_data:
        # Convert "close_price" to float before formatting as currency
        record['close_price'] = float(record['close_price'])
        # Parse the date string into a date object
        record['date'] = datetime.strptime(record['date'], '%Y-%m-%d %H:%M:%S')


    # Assuming you have pandas DataFrame, you can convert it to HTML
    # If your data is not in a DataFrame, you might need to format it accordingly
    if isinstance(json_data, pd.DataFrame):
        table_html = json_data.to_html(classes='table table-striped')
    else:
        # Handle non-DataFrame JSON data here
        table_html = "<p>No data to display</p>"

    return render_template('table_action.html', json_data=json_data)


if __name__ == '__main__':
    app.run()