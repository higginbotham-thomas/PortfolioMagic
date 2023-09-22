from flask import Flask, render_template
import main # Import main.py module
import pandas as pd

app = Flask(__name__)

@app.route('/')
def display_json_as_table():
    # Call a function from main.py to get JSON data
    json_data = main.results

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
