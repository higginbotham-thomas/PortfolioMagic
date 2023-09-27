import functions
import pandas as pd

df_accounts = pd.read_csv('Accounts.csv')

# Display unique values in the 'Account' column
unique_accounts = df_accounts['Account'].unique()
print("Unique Accounts:")
for i, account in enumerate(unique_accounts):
    print(f"{i + 1}. {account}")

# Prompt the user to choose an account
selected_account_index = int(input("Enter the number of the account you want to select: ")) - 1
selected_account = unique_accounts[selected_account_index]


# Filter the DataFrame based on the selected account
symbols = df_accounts[df_accounts['Account'] == selected_account]['Symbol'].tolist()

# Call the analyze_stocks function from functions.py
results = functions.analyze_stocks(symbols)
