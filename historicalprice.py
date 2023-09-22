import requests
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

FMPKEY = os.getenv('FMPKEY')
SYMBOL = ('aapl')

url = f"https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?from=2022-09-20&to=2023-09-20&apikey={FMPKEY}"

payload = ""
headers = {
  'symbol': f'{SYMBOL}'
}

response = requests.request("POST", url, headers=headers, data=payload)

if response.status_code == 200:
    api_data = response.json()
else:
    print("Failed to fetch data from the API.")
    exit()

# Extract x and y data from the API response (modify this according to your data structure)
x_data = [entry['date'] for entry in api_data['historical']]
y_data = [entry['adjClose'] for entry in api_data['historical']]

# Create the line graph
plt.plot(x_data, y_data, label='Data')
plt.xlabel('X-axis Label')
plt.ylabel('Y-axis Label')
plt.title('API Data Line Graph')
plt.legend()
plt.grid(True)

# Show the graph
plt.show()