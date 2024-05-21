# DB_Insert.py
# This script is used to insert data from CSV files into the database.
# The script will load all CSV files from the Stocks, Indices, and ETFs directories into the database.


import mysql.connector
import os
import pandas as pd


# Modifies the parameters that match your local workbench.
"""
db = mysql.connector.connect(
    host="127.0.0.1",
    user="teammate",
    password="mpcs53001",
    database="TradingSystem"
)
"""


def connect_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mpcs53001",
            database="TradingSystem"
        )
        return db
    except mysql.connector.Error as err:
        print(f"These is an error.\n{err}")
        return None


def universal_preprocess(fileID, filename, row):
    ID, ticker = fileID, filename[:-4]

    day = row["Date"]
    open, close = row["Open"], row["Adj Close"]
    low, high = row["Low"], row["High"]
    
    return (ID, ticker, open, high, low, close, day)


def load_dir(connection, dirpath, preprocess, query):
    cursor = connection.cursor()
    
    fileID = 0
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        
        file = pd.read_csv(filepath).reset_index()
        for _, row in file.iterrows():
            processed_data = preprocess(fileID, filename, row)
            cursor.execute(query, processed_data)
        connection.commit()
        
        fileID += 1
    
    cursor.close()


def main():
    connection = connect_database()
    if connection is None:
        print("Failed to connect to the database.")

    stock_insert = (
        "INSERT INTO Stocks (sID, ticker, open, high, low, close, day) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    index_insert = (
        "INSERT INTO Indices (iID, ticker, open, high, low, close, day) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    etf_insert = (
        "INSERT INTO ETFs (eID, ticker, open, high, low, close, day) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )

    load_dir(connection, "./Stocks", universal_preprocess, stock_insert)
    load_dir(connection, "./Indices", universal_preprocess, index_insert)
    load_dir(connection, "./ETFs", universal_preprocess, etf_insert)

    connection.close()


if __name__ == "__main__":
    main()
