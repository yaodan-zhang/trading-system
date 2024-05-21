# utils.py
# This file contains utility functions that are used in the application.
# Reference: https://docs.anychart.com/Stock_Charts/Technical_Indicators/Mathematical_Description


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def process_raw_price(row):
    day = row[0]
    open = round(row[1], 2)
    high = round(row[2], 2)
    low = round(row[3], 2)
    close = round(row[4], 2)
    
    return (day, open, high, low, close)


# ------------------------------------------------------------------------------
# Alpha 1: Money Flow Multiplier
# Money Flow Multiplier (MFM) is a technical indicator that measures the strength of money flow.
# ------------------------------------------------------------------------------

def money_flow_multiplier(df):
    mfm = (
        ((df["close"] - df["low"]) - (df["high"] - df["close"]))
        / (df["high"] - df["low"])
    )
    
    return mfm


# ------------------------------------------------------------------------------
# This function returns a list of strings containing the image names of the plots.
# The plots are saved in the "static" folder.
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# def plot_price_with_alphas(price_data : list[tuple]) -> list[str]:
# ------------------------------------------------------------------------------

def plot_price_with_alphas(price_data):
    df = pd.DataFrame(price_data, columns=["date", "open", "high", "low", "close"])
    
    plt.plot(df["date"], df["close"], "b", label="raw_price")
    raw_price = "raw_price.png"
    plt.legend()
    plt.savefig("./static/" + raw_price)
    plt.clf()

    plt.plot(df["date"], money_flow_multiplier(df), "r", label="money_flow_multiplier")
    alpha1 = "alpha1.png"
    plt.legend()
    plt.savefig("./static/" + alpha1)
    plt.clf()

    return [
        raw_price,
        alpha1,
    ]


def calculate_overall_return(data):
    """
    Calculates the overall return for a stock given a list of daily price data.
    """

    df = pd.DataFrame(
        data, columns=["sID", "ticker", "open", "high", "low", "close", "day"]
    )
    cumulative_return = 1.0

    for _, day in df.iterrows():
        open_price = float(day["open"])
        close_price = float(day["close"])

        # Calculates daily return and updates cumulative return.
        daily_return = (close_price - open_price) / open_price
        cumulative_return *= 1 + daily_return

    overall_return = cumulative_return - 1

    return overall_return


def calculate_risk(data):
    """
    Calculates the risk (standard deviation) of the trading session.
    """

    df = pd.DataFrame(
        data, columns=["sID", "ticker", "open", "high", "low", "close", "day"]
    )

    # Extracts daily returns based on the close prices.
    daily_changes = [
        (float(day["close"]) - float(day["open"])) / float(day["open"])
        for _, day in df.iterrows()
    ]

    # Calculates the standard deviation of daily returns.
    risk = np.std(daily_changes)

    return risk
