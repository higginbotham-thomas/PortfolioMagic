# Portfolio Magic
This tool will help you find a good mix of stocks, ETFs and mutual funds for a given portfolio, using Monte Carlo simulation and Mean-Variance Optimization. Supply a csv file with your portfolio, enter the amount of risk that is appropriate, choose the number of days of price history to use, and the number of simulations to run. Risk is a number from 0.0 to 1.0, with 0.0 being the least risk. Experiment with different choices for the days of price history. For example, it might be useful to start from a certain historical point marking a change in the market to see what might have worked best since that point. 

Mean-Variance Optimization (MVO) is a mathematical approach used to construct investment portfolios that maximize expected return for a given level of risk. The method was introduced by Harry Markowitz in 1952 and is a fundamental aspect of modern portfolio theory (MPT). The primary idea behind MVO is to quantify both the expected returns and risks of different assets, and then to find the optimal combination of assets that offers the highest expected return for a given level of risk. Risk is typically measured as the standard deviation of the asset's returns, and the correlation between the returns of different assets is also taken into account.

Monte Carlo simulation is a statistical technique used to model and analyze the behavior of complex systems or processes that have many uncertain variables. It is named after the Monte Carlo Casino in Monaco, as the technique uses random sampling, similar to casino games like roulette. In the context of portfolio optimization, a Monte Carlo simulation can be used to model the behavior of different investment portfolios under various market conditions. By running simulations with different combinations of assets, it is possible to assess the risk and return profile of each portfolio and to identify the one that is most likely to achieve the desired investment objectives.
# Getting Started:
 You will need a portfolio file, in .csv format. You can export a portfolio from your brokerage, or you can compile a simple csv file. You can use sample_portfolios.csv from this repository as an example. The portfolio must have the following items:
- Symbol: the symbol of the asset (for example, *AAPL* for Apple)
- Quantity: a decimal number showing the total number of shares you hold for that symbol
- Market Value: this can be the market value of the assets
- One blank line following the assets
- After that blank line, a line with "Account Total" in the Symbol column, and the total market value of the portfolio in the "Market Value" column
# Data Source:
Portfolio Magic uses the [FinancialModelingPrep API](https://site.financialmodelingprep.com/developer/docs) as the source for all data. A Free plan is available. 

The API Key is stored securely in a .env file. Create a new blank file called .env, and in that file, add this line,  `FMPKEY = "YOUR_API_KEY"` replacing `YOUR_API_KEY` with the key obtained from FinancialModelingPrep.
# Prompts
 - **Path for the CSV file** - no quotes, use forward slashes only:
	 - Windows: `C:/Users/username/Downloads/portfolio.csv`
	 - MacOS `/Users/username/directory/portfolio.csv`
 - **Your Risk Tolerance**
	 - A decimal number between 0 and 1, showing the amount of risk you are willing to tolerate
	 - For example, 0.15 is 15% risk
 - **Number of Trading Days**
	 - Enter a number of trading days to use for calculating risk (There are normally 252 trading days in the US)
	 - The program will choose the latest number of trading days, from the most recent day back
 - **Number of Simulations**
	 - Enter a number of times you'd like the program to create portfolios based on the other inputs.
	 - This is a Monte Carlo simulation. The best performing portfolio from the number of simulations ran that does not exceed your risk tolerance will be displayed.
# Notes
- Every time you run the program, you will get different results.
- Consult a professional before trading if you are not comfortable with the concepts.