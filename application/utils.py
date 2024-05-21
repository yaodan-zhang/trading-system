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
# Alpha 2: Relative Strength Index
# Relative Strength Index (RSI) is a technical indicator that measures the speed and change of price movements.
# ------------------------------------------------------------------------------

def relative_strength_index(df, periods=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# ------------------------------------------------------------------------------
# This function returns a list of strings containing the image names of the plots.
# The plots are saved in the "static" folder.
# Function Signature:
#     def plot_price_with_alphas(price_data : list[tuple]) -> list[str]:
# ------------------------------------------------------------------------------

def plot_price_with_alphas(price_data):
    df = pd.DataFrame(
        price_data,
        columns=["date", "open", "high", "low", "close"]
    )
    
    # Plots the raw price chart.
    plt.figure(figsize=(10, 6))

    # Applies smoothing with a rolling average.
    smooth_mfm = df["close"].rolling(window=5, center=True).mean()
    plt.plot(
        df["date"], smooth_mfm,
        color="magenta", label="Raw Price"
    )
    plt.title("Raw Price Over Time")
    plt.xlabel("Date", fontsize=8)
    plt.ylabel("Price", fontsize=8)
    plt.legend()
    plt.grid(True)
    raw_price = "raw_price.png"
    plt.savefig("./static/" + raw_price)
    plt.clf()

    # Plots the Money Flow Multiplier.
    plt.figure(figsize=(10, 6))
    
    # Applies smoothing with a rolling average.
    smooth_mfm = money_flow_multiplier(df).rolling(window=5, center=True).mean()
    plt.plot(
        df["date"], smooth_mfm,
        color="salmon", label="Money Flow Multiplier"
    )
    plt.title("Money Flow Multiplier Over Time")
    plt.xlabel("Date", fontsize=8)
    plt.ylabel("Multiplier", fontsize=8)
    plt.legend()
    plt.grid(True)
    alpha1 = "alpha1.png"
    plt.savefig("./static/" + alpha1)
    plt.clf()

    # Plots the Relative Strength Index.
    plt.figure(figsize=(10, 6))

    # Applies smoothing with a rolling average.
    smooth_mfm = relative_strength_index(df).rolling(
        window=5, center=True
    ).mean()
    plt.plot(
        df["date"], relative_strength_index(df),
        color="deepskyblue", label="RSI"
    )
    plt.title("Relative Strength Index Over Time")
    plt.xlabel("Date", fontsize=8)
    plt.ylabel("RSI", fontsize=8)
    plt.legend()
    plt.grid(True)
    alpha2 = "rsi_chart.png"
    plt.savefig("./static/" +alpha2)
    plt.clf()

    return [
        raw_price,
        alpha1, alpha2
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
        open_price, close_price = float(day["open"]), float(day["close"])
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


def plot_cumulative_return(data):
    # Creates DataFrame from the price data.
    df = pd.DataFrame(
        data,
        columns=["sID", "ticker", "open", "high", "low", "close", "day"]
    )
    
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    df["cumulative_return"] = (df["close"] / df["close"].iloc[0]) - 1

    # Applies smoothing with a rolling average.
    df["smoothed_return"] = df["cumulative_return"].rolling(window=5).mean()
    plt.figure(figsize=(10, 6))
    plt.plot(
        df["day"], df["smoothed_return"],
        label="Asset", color="forestgreen"
    )
    plt.title("Cumulative Return")
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.grid(True)
    
    # Saves the plot to a file.
    cumulative_return_graph = "cumulative_return.png"
    plt.savefig("./static/" + cumulative_return_graph)
    plt.clf()

    return cumulative_return_graph
