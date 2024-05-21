''' A utility functions library. '''

''' Process the raw price from database to keep 2 decimal places. '''
def process_raw_price(row):
    day = row[0]
    open = round(row[1],2)
    high = round(row[2],2)
    low = round(row[3],2)
    close = round(row[4],2)
    return (day, open, high, low, close)

''' Alpha library '''
''' The major way to do is to calculate alphas, draw them with price data,
save the image into the static folder, and display it using Flask-html '''
''' Alpha means technical indicators in our project '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1st alpha. Defined as the first indicator in below reference
def money_flow_multiplier(df):
    mfm = ((df['close']-df['low'])-(df['high']-df['close']))/(df['high']-df['low'])
    return mfm

# TO ADD MORE ALPHAS
# Some references to choose alphas from: https://docs.anychart.com/Stock_Charts/Technical_Indicators/Mathematical_Description
# You can search "technical indicators with fomulas" to see more.
# You can certainly calculate time-series related alphas utilizing the pd dataframe's 'date' column.
# You can optimize the codes below, it just gives you a rough idea to follow the steps.

# def plot_price_with_alphas(price_data : list[tuple]) -> list[str]: # return the image names in the 'static' folder
def plot_price_with_alphas(price_data): # return the image names in the 'static' folder
    # Convert price data into a pandas dataframe
    # Beware of column order.
    df = pd.DataFrame(price_data, columns=['date','open','high','low','close'])

    # Plot raw price, using each day's close price as that day's price, save it into 'static' folder.
    plt.plot(df['date'], df['close'], "b", label="raw_price")
    raw_price = "raw_price.png"
    plt.legend() # Show label
    plt.savefig('./static/'+raw_price) # Save figure
    plt.clf() # Clean previous plot

    # Calculate and plot alphas, save them into the 'static' folder.
    plt.plot(df['date'], money_flow_multiplier(df), "r", label="money_flow_multiplier")
    alpha1 = "alpha1.png"
    plt.legend()
    plt.savefig('./static/'+alpha1)
    plt.clf() 

    # TO ADD MORE ALPHA PLOTS
    # For Matplotlib pyplot color and linestyle see https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.pyplot.plot.html

    # Return image names list
    return [raw_price, alpha1] # TO ADD, beware of order because we want price to be displayed first, then its following alphas.


import matplotlib.pyplot as plt

def calculate_overall_return(data):
    """
    Calculate the overall return for a stock given a list of daily price data.
    
    Parameters:
    data (list of dict): Each dict contains 'sID', 'ticker', 'open', 'high', 'low', 'close', and 'day' prices.
    
    Returns:
    float: The overall return of the stock.
    """
    df = pd.DataFrame(data, columns=['sID', 'ticker', 'open', 'high', 'low', 'close', 'day'])
    cumulative_return = 1.0
    
    for _, day in df.iterrows():
        open_price = float(day['open'])
        close_price = float(day['close'])
        
        # Calculate daily return
        daily_return = (close_price - open_price) / open_price
        
        # Update cumulative return
        cumulative_return *= (1 + daily_return)
    
    # Calculate overall return
    overall_return = cumulative_return - 1
    
    return overall_return


def calculate_risk(data):
    """
    Calculate the risk (standard deviation) of the trading session.
    
    Parameters:
    data (list of dict): Each dict contains 'sID', 'ticker', 'open', 'high', 'low', 'close', and 'day' prices.
    
    Returns:
    float: The standard deviation of the price changes.
    """
    df = pd.DataFrame(data, columns=['sID', 'ticker', 'open', 'high', 'low', 'close', 'day'])
    
    # Extract daily returns based on the close prices
    daily_changes = [(float(day['close']) - float(day['open'])) / float(day['open']) for _, day in df.iterrows()]
    
    # Calculate the standard deviation of daily returns
    risk = np.std(daily_changes)

    return risk

