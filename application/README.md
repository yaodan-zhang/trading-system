### Trading System app

**home:** main home page before any log in, can look up asset info or log in/sign up.

**asset:** look up stocks/indices/ETFs price data or displaying customized alphas for an asset.

    -- raw price data

    -- asset type (stocks/indices/ETFs) -> list all tickers of that asset type -> list all price data for each ticker

    -- See alphas for an asset

    -- accept user input and display results

---

**Things to add/ TO DO/ TO ADD:**

1. More data for Stocks, Indices, and ETFs from yahoo!finance.
   For Stocks for example: you can see [S&amp;P500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies), which tells you all companies/stocks that the S&P500 index contains, so you can look them up in yahoo!finance and download files.
2. Alphas / Technical Indicators.
3. User Trading Session.
4. Optional/Not important:

   1. Insert records into the Compose Table in the Database.
   2. Image cleanup after each image display.
   3. More error handling for user inputs.

   ---

   Important notes: When querying the database in Python, you need to add single quotation mark (') around a condition variable, e.g., WHERE ticker = 'MMM', so that you need to include single quotation marks inside the double quotation marks where the double ones are for the query.
