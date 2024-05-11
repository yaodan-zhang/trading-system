# Insert records into the tables of the database created in TradingSystem.sql, codes are modified from Alexandra's and my codes from the last homework assignment.
# Id in each asset entity set should be an automatically incremented integer starting at 0.
# We use yahoo!finance as data source.
import mysql.connector
import os
import pandas as pd

def connect_database():
    try:
        # modify the parameters that match your local workbench with TradingSystem database & corresponding tables created inside
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="teammate",
            password="mpcs53001",
            database="TradingSystem"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def universal_preprocess(fileID, filename, row):
    ID = fileID
    ticker = filename[:-4] # Remove ".csv" to get file name
    open = row['Open']
    high = row['High']
    low = row['Low']
    close = row['Adj Close']
    day = row["Date"]
    return (ID, ticker, open, high, low, close, day)

def load_dir(connection, dirpath, preprocess, query):
    """Loads all CSV files from a directory into the database."""
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
    
    stock_insert = "INSERT INTO Stocks (sID, ticker, open, high, low, close, day) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    index_insert = "INSERT INTO Indices (iID, ticker, open, high, low, close, day) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    etf_insert = "INSERT INTO ETFs (eID, ticker, open, high, low, close, day) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    
    load_dir(connection, './Stocks', universal_preprocess, stock_insert)
    load_dir(connection, './Indices', universal_preprocess, index_insert)
    load_dir(connection, './ETFs', universal_preprocess, etf_insert)
    
    connection.close()

if __name__ == "__main__":
    main()