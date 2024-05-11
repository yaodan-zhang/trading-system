from flask import Flask, request, url_for, redirect, render_template
from utils import process_raw_price, plot_price_with_alphas
import matplotlib
matplotlib.use('Agg')

# Connect to the Trading System database
import mysql.connector
DB_Connection = mysql.connector.connect(
    # Modify the parameters to match your local machine.
    user = 'teammate',
    password = 'mpcs53001',
    host = '127.0.0.1',
    database="TradingSystem"
    )
cursorObject = DB_Connection.cursor()

app = Flask(__name__)
# Trading system home page
@app.route('/ts/home/')
def home():
    return render_template('home.html')

# User log in page.
@app.route('/ts/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user email from POST request
        user_email = request.form['email']
        
        # Extract user id from database using user email.
        #  optional: add error handling if user doesn't exist.
        # TO DO
        uID = 0

        return redirect(url_for('user',user_id = uID))
    # show the form before it was submitted
    return render_template('login.html')

# User's home page after login, displaying all his hitorical trading sessions.
@app.route('/ts/user/<user_id>')
def user(user_id):
    # Extract user's trading sessions by user_id from database and display them.
    # TO DO: PART - I
    # The trading_sessions.html page will redirect to another route that displays the result of the trading session.
    # You need to create a new route for this which accept a variable endpoint i.e.<xx>, with the variable being the primary key of the Result Table.
    # Then extract result from Result Table using the primary key and render an html template to display the extracted record.
    # The result record page should contain the following as minimum: (some are not directly from the record so you need to properly define new functions in utils.py to calculate by yourself)
    # 1. The overal return of the trading session (X% or -X%) 
    # 2. The risk of the trading session (measured by asset price's standard deviation during that trading period)
    # 3. Sharpe Ratio of the trading session (return divided by std, i.e., step 1 divided by step 2)
    # 4. A cumulative return graph plotted against the cumulative return graph of a benchmark (usually we use S&P500 index, whose ticker name is "^GSPC")
    #   Note cumulative return is different from price, it should be calculated based on price.
    #   The way you want to display an image in html is similar to the alpha page. See more in alpha() below and utils.py so you can do it similarly.
    
    # TO DO: PART - II
    # The trading_session.html page should also have a button to accept new trading session created by the user.
    # The button should direct the user to a new route that is similar to the user sign up page which render an html to accept user inputs for the new session.
    # After user submits, you should add the record into the database table -  UserTradingSessions
    # You should also calculated the result of this session and add it to the Result Table.
    # The asset can be assumed to be an individual asset first (optional: handle a portfolio) with long position (optional: add short position).
    return render_template('trading_sessions.html', userid = user_id, paras = "ANY PARAMETERS")

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
        
        # Debug
        # print(fname,lname,phone,email,preferences)
        
        # Set uID to the max uID in the database's Users table increased by 1.
        # TO DO
        uID = None

        # Insert record into Users table
        # TO DO

        return redirect(url_for('signup_success'))
    return render_template('signup.html')

# User sign up success page.
@app.route('/ts/signup_success')
def signup_success():
    return render_template('signup_success.html')

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