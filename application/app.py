from flask import Flask, request, url_for, redirect, render_template
from utils import process_raw_price, plot_price_with_alphas
import matplotlib
import utils
matplotlib.use('Agg')

# Connect to the Trading System database
import mysql.connector
DB_Connection = mysql.connector.connect(
    # Modify the parameters to match your local machine.
    host="localhost",
    user="root",
    password="20001016",
    database="TradingSystem"
    )
cursorObject = DB_Connection.cursor()

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

# Trading system home page
@app.route('/ts/home/')
def home():
    return render_template('home.html')

# User sign up page.
@app.route('/ts/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract signup info
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        email = request.form['email']
        preferences = request.form['preferences']

        # Check if email already exists in the database and add proper error handling.
        cursorObject.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursorObject.fetchone()
        if existing_user:
            return "Email already exists. Please use a different email or log in."
    
        # Insert record into Users table
        cursorObject.execute("INSERT INTO users (firstName, lastName, phone, email, preferences) VALUES (%s, %s, %s, %s, %s)",
                             (fname, lname, phone, email, preferences))
        DB_Connection.commit()

        return redirect(url_for('signup_success'))
    return render_template('signup.html')

# User sign up success page.
@app.route('/ts/signup_success')
def signup_success():
    return render_template('signup_success.html')

# User log in page.
@app.route('/ts/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user email from POST request
        user_email = request.form['email']
        cursorObject.execute("SELECT * FROM users WHERE email = %s", (user_email,))
        user = cursorObject.fetchone()
        #  optional: add error handling if user doesn't exist.
        if not user:
            return render_template('error.html', message="Email does not exists. Please sign up for a email.")
        
        # TO DO
        uID = user[0]

        return redirect(url_for('user',user_id = uID))
    # show the form before it was submitted
    return render_template('login.html')

'''
    Extract user's trading sessions by user_id from database and display them.
    TO DO: PART - I
    The trading_sessions.html page will redirect to another route that displays the result of the trading session.
    You need to create a new route for this which accept a variable endpoint i.e.<xx>, with the variable being the primary key of the Result Table.
    Then extract result from Result Table using the primary key and render an html template to display the extracted record.
    The result record page should contain the following as minimum: (some are not directly from the record so you need to properly define new functions in utils.py to calculate by yourself)
    1. The overal return of the trading session (X% or -X%) 
    2. The risk of the trading session (measured by asset price's standard deviation during that trading period)
    3. Sharpe Ratio of the trading session (return divided by std, i.e., step 1 divided by step 2)
    3. A cumulative return graph plotted against the cumulative return graph of a benchmark (usually we use S&P500 index, whose ticker name is "^GSPC")
      Note cumulative return is different from price, it should be calculated based on price.
      The way you want to display an image in html is similar to the alpha page. See more in alpha() below and utils.py so you can do it similarly.
   
    TO DO: PART - II
    The trading_session.html page should also have a button to accept new trading session created by the user.
    The button should direct the user to a new route that is similar to the user sign up page which render an html to accept user inputs for the new session.
    After user submits, you should add the record into the database table -  UserTradingSessions
    You should also calculated the result of this session and add it to the Result Table.
    The asset can be assumed to be an individual asset first (optional: handle a portfolio) with long position (optional: add short position).

'''

# User's home page after login, displaying all his hitorical trading sessions.
@app.route('/ts/user/<user_id>')
def user(user_id):
    cursorObject.execute("SELECT * FROM users WHERE uID = %s", (user_id,))
    user = cursorObject.fetchone()
    if user:
        cursorObject.execute("SELECT * FROM UserTradingSessions WHERE uID = %s", (user[0],))
        trading_sessions = cursorObject.fetchall()
        return render_template('trading_sessions.html', 
                                userid = user_id, 
                                user=user, 
                                trading_sessions=trading_sessions, 
                                message=f"Welcome {user[1]} {user[2]}! ")
    return "User not found."

# Result page
@app.route('/ts/user/<user_id>/trading_session_result/<session_id>')
def trading_session_result(session_id,user_id):

    cursorObject.execute("SELECT * FROM Result WHERE sessionID = %s AND uID = %s", (session_id,user_id))
    result = cursorObject.fetchone()
    if result:

        return render_template('trading_session_result.html', 
                               result=result,
                               overall_return=result[2], 
                               risk=result[3], 
                               sharpe_ratio=result[4])
    return "Trading session result not found."

# New Session page
@app.route('/ts/user/<user_id>/new_trading_session', methods=['GET', 'POST'])
def new_trading_session(user_id):

    if request.method == 'POST':
        # Extract new trading session info
        preference = request.form['preference'].lower()
        ticker = request.form['ticker']
        # use preference and ticker to find the underlying ID
        # Determine the table and column based on preference
        if preference == "stock":
            table = "Stocks"
            id_column = "sID"
        elif preference == "etf":
            table = "ETFs"
            id_column = "eID"
        elif preference == "index":
            table = "Indices"
            id_column = "iID"
        else:
            return "Invalid preference. Please choose 'stock', 'etf', or 'index'."
        
        # Query the underlying ID based on ticker
        cursorObject.execute(f"SELECT DISTINCT {id_column} FROM {table} WHERE ticker = %s", (ticker,))
        underlying = cursorObject.fetchone()
        if not underlying:
            return f"No underlying asset found with ticker {ticker} in {preference}."

        underlyingID = f"{table}-{ticker}-{underlying[0]}"

        start_date = request.form['start_date']
        end_date = request.form['end_date']
        volume = int(request.form['volume'])
        
        cursorObject.execute(
            "INSERT INTO UserTradingSessions (uID, startDay, endDay, volume, underlyingID, positionLS) VALUES (%s, %s,%s,%s,%s,%s)", 
            (user_id, start_date, end_date, volume, underlyingID, 'L')
        )
        DB_Connection.commit()

        # UP-TO-DATE Weight
        # Retrieve all trading sessions for the user
        cursorObject.execute("SELECT sessionID, volume FROM UserTradingSessions WHERE uID = %s", (user_id,))
        sessions = cursorObject.fetchall()
        
        # Calculate the total volume
        total_volume = sum(session[1] for session in sessions)
        cursorObject.execute("INSERT INTO Portfolio (uID, sessionID, weight) VALUES (%s,%s,%s)", 
                            (user_id, sessions[-1][0], 0))
            
        # Update the weight for each session based on the new total volume
        for session in sessions:
            session_id = session[0]
            session_volume = session[1]
            weight = session_volume / total_volume
            cursorObject.execute("UPDATE Portfolio SET weight = %s WHERE sessionID = %s", (weight, session_id))
        
        DB_Connection.commit()
  
        # Calculate results for the new session
        cursorObject.execute(f"SELECT * FROM {table} WHERE sID = {underlying[0]} AND day BETWEEN '{start_date}' AND '{end_date}'")
        result = cursorObject.fetchall()





        # =======================NEED CHANGE================================#
        # Calculate overall return, risk, and Sharpe ratio
        overall_return = -float(utils.calculate_overall_return(result))
        risk = float(utils.calculate_risk(result))
        sharpe_ratio = -round(overall_return / risk, 2) if risk != 0 else 0  # Avoid division by zero
        cursorObject.execute(
            "INSERT INTO Result (uID, sessionID, gain, risk, SharpeRatio) VALUES (%s, %s, %s, %s, %s)", 
            (user_id, session_id, overall_return, risk, sharpe_ratio)
        )
        DB_Connection.commit()







        
        return redirect(url_for('user', user_id=user_id))
        # Fetch unique tickers from the database

    stock_tickers = get_unique_tickers('Stocks')
    index_tickers = get_unique_tickers('Indices')
    etf_tickers = get_unique_tickers('ETFs')

    return render_template('new_trading_session.html', 
                           user_id=user_id,
                           stock_tickers=stock_tickers,
                           index_tickers=index_tickers,
                           etf_tickers=etf_tickers)

def get_unique_tickers(table_name):
    query = f"SELECT DISTINCT ticker FROM {table_name}"
    cursorObject.execute(query)
    
    # Fetch all unique tickers
    tickers = [row[0] for row in cursorObject.fetchall()]
    return tickers

# Delete trading session
@app.route('/ts/delete_trading_session/<session_id>/<user_id>', methods=['POST'])
def delete_trading_session(session_id, user_id):
    # Delete the trading session
    delete_id = session_id
    cursorObject.execute("DELETE FROM portfolio WHERE sessionID = %s", (delete_id,))
    cursorObject.execute("DELETE FROM Result WHERE sessionID = %s", (delete_id,))
    cursorObject.execute("DELETE FROM usertradingsessions WHERE sessionID = %s", (delete_id,))
    DB_Connection.commit()
    
    # Retrieve all trading sessions for the user
    cursorObject.execute("SELECT sessionID, volume FROM UserTradingSessions WHERE uID = %s", (user_id,))
    sessions = cursorObject.fetchall()
    
    # Calculate the total volume
    total_volume = sum(session[1] for session in sessions)
    
    # Update the weight for each session based on the new total volume
    for session in sessions:
        session_id = session[0]
        session_volume = session[1]
        weight = session_volume / total_volume if total_volume > 0 else 0
        cursorObject.execute("UPDATE Portfolio SET weight = %s WHERE sessionID = %s", (weight, session_id))
    
    DB_Connection.commit()
    
    return redirect(url_for('user', user_id=user_id))

# Portforlio Page
@app.route('/portfolio/<int:user_id>')
def portfolio(user_id):
    cursorObject.execute('SELECT * FROM Users WHERE uID = %s', (user_id,))
    user = cursorObject.fetchone()
    cursorObject.execute('SELECT sessionID, weight FROM Portfolio WHERE uID = %s', (user_id,))
    portfolio = cursorObject.fetchall()
    return render_template('portfolio.html', user=user, user_id=user_id, portfolio=portfolio)


# Assets' home page.
@app.route('/ts/asset')
def asset():
    return render_template('asset.html')

# Assets' price main page.
@app.route('/ts/asset/price')
def price():
    return render_template('price.html')

# Stock asset price page, displaying all stock tickers.
@app.route('/ts/asset/price/stocks')
def stocks():
    # Extract all stock tickers from database to display
    cursorObject.execute("SELECT DISTINCT ticker FROM Stocks;")
    stock_tickers = [item[0] for item in cursorObject.fetchall()]
    return render_template('stocks.html', tickers = stock_tickers)

# An individual stock's all price data.
@app.route('/ts/asset/price/stocks/<ticker>')
def stock_ticker_data(ticker):
    # Extract all price data of this stock ticker from database and display it
    query = "SELECT day, open, high, low, close FROM Stocks WHERE ticker='" + ticker + "' ORDER BY day DESC;"
    cursorObject.execute(query)
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    return render_template('stock_ticker.html', tick = ticker, data = price_data)

# Index asset price page, displaying all index tickers.
@app.route('/ts/asset/price/indices')
def indices():
    # Extract all index tickers from database to display
    cursorObject.execute("SELECT DISTINCT ticker FROM Indices;")
    index_tickers = [item[0] for item in cursorObject.fetchall()]
    return render_template('indices.html', tickers = index_tickers)

# An individual index's all price data.
@app.route('/ts/asset/price/indices/<ticker>')
def index_ticker_data(ticker):
    query = "SELECT day, open, high, low, close FROM Indices WHERE ticker='" + ticker + "' ORDER BY day DESC;"
    cursorObject.execute(query)
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    return render_template('index_ticker.html', tick = ticker, data = price_data)

# ETF asset price page, displaying all ETF tickers.
@app.route('/ts/asset/price/etfs')
def etfs():
    # Extract all ETF tickers from database to display
    cursorObject.execute("SELECT DISTINCT ticker FROM ETFs;")
    etf_tickers = [item[0] for item in cursorObject.fetchall()]
    return render_template('etfs.html', tickers = etf_tickers)

# An individual ETF's all price data.
@app.route('/ts/asset/price/etfs/<ticker>')
def etf_ticker_data(ticker):
    # Extract all price data of this ETF ticker from database and display it
    query = "SELECT day, open, high, low, close FROM ETFs WHERE ticker='" + ticker + "' ORDER BY day DESC;"
    cursorObject.execute(query)
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    return render_template('etf_ticker.html', tick = ticker, data = price_data)

# Asset's alpha main page.
@app.route('/ts/asset/alpha', methods=['GET', 'POST'])
def alpha():
    if request.method == 'POST':
        # Extract asset info from the html request to plot alphas on.
        asset_type = request.form['assettype']
        ticker = request.form['ticker']
        start_date = request.form['startdate']
        end_date = request.form['enddate']

        # Query database to get asset price data.
        if asset_type == "stock":
            DB_Table = "Stocks"
        elif asset_type == "index":
            DB_Table = "Indices"
        elif asset_type == "ETF":
            DB_Table = "ETFs"
        else:
            # Error handling and redirect to alpha.html
            # TO DO
            pass

        # Error handling for ticker.
        ticker_query = "SELECT DISTINCT ticker FROM " + DB_Table + ";"
        cursorObject.execute(ticker_query)
        tickers = [item[0] for item in cursorObject.fetchall()]
        if ticker not in tickers:
            # error handling and redirect to alpha.html
            # TO DO
            pass
        
        # Get price data.
        # Beware of adding '' surrounded around the condition, e.g., WHERE ticker = 'MMM'. i.e., add ' inside ""
        data_query = "SELECT day, open, high, low, close FROM " + DB_Table + " WHERE ticker='" + ticker + "' AND day>='"+start_date+"' AND day<='"+end_date+"' ORDER BY day ASC;"
        cursorObject.execute(data_query)
        price_data = [process_raw_price(row) for row in cursorObject.fetchall()]
        
        # Plot alphas using asset price, plot asset price as well. Get image names list.
        image_names = plot_price_with_alphas(price_data)

        return render_template('view_with_alphas.html', tick = ticker, image_names = image_names)
    return render_template('alpha.html')

app.run(host='0.0.0.0', debug=True)