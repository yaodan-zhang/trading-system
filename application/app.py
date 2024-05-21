# app.py
#
# This file contains the main application code for the Trading System.
# It contains the main routes for the application, including the following:
#     1. Home page;
#     2. User sign up;
#     3. User log in;
#     4. User home page;
#     5. Trading session result;
#     6. New trading session;
#     7. Delete trading session;
#     8. Portfolio page;
#     9. Asset home page;
#     10. Asset price main page;
#     11. Stock asset price page;
#     12. Index asset price page;
#     13. ETF asset price page;
#     14. Asset alpha main page;
#     15. Stock asset alpha page;
#     16. Index asset alpha page;
#     17. ETF asset alpha page;
#     18. Portfolio page.
#
# The application is run using the Flask framework and connects to a MySQL database to retrieve and store data.
# The application also uses the utils.py file to process and plot data.


import matplotlib
import mysql.connector
import utils


from flask import Flask
from flask import redirect, render_template, request, url_for
from utils import process_raw_price, plot_price_with_alphas


matplotlib.use("Agg")


# Modifies the parameters to match your local machine.
"""
DB_Connection = mysql.connector.connect(
    host="127.0.0.1",
    user="teammate",
    password="mpcs53001",
    database="TradingSystem"
)
"""


DB_Connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mpcs53001",
    database="TradingSystem"
)
cursorObject = DB_Connection.cursor()



app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("home"))


# ------------------------------------------------------------------------------
# This is the home page of the application.
# ------------------------------------------------------------------------------

@app.route("/ts/home/")
def home():
    return render_template("home.html")


# ------------------------------------------------------------------------------
# This is the user sign up page.
# ------------------------------------------------------------------------------

@app.route("/ts/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Extracts the user's information from the form and inserts it into the database.
        fname = request.form["fname"]
        lname = request.form["lname"]
        phone = request.form["phone"]
        email = request.form["email"]
        preferences = request.form["preferences"]

        # Checks if the email already exists in the database.
        cursorObject.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursorObject.fetchone()
        if existing_user:
            return "Email already exists. Please use a different email."

        # Inserts the user's information into the database.
        cursorObject.execute(
            "INSERT INTO users (firstName, lastName, phone, email, preferences) "
            "VALUES (%s, %s, %s, %s, %s)",
            (fname, lname, phone, email, preferences),
        )
        DB_Connection.commit()

        return redirect(url_for("signup_success"))
    return render_template("signup.html")


# ------------------------------------------------------------------------------
# This is the user sign up success page.
# ------------------------------------------------------------------------------

@app.route("/ts/signup_success")
def signup_success():
    return render_template("signup_success.html")


# ------------------------------------------------------------------------------
# This is the user login page.
# ------------------------------------------------------------------------------

@app.route("/ts/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Gets the user's email from the form and checks if it exists in the database.
        user_email = request.form["email"]
        cursorObject.execute(
            "SELECT * FROM users WHERE email = %s",
            (user_email,)
        )
        user = cursorObject.fetchone()
        
        #  If the email does not exist, an error message is displayed.
        if not user:
            return render_template(
                "error.html",
                message="Email does not exists. Please sign up for a email."
            )

        # Redirects to user's home page after login.
        uID = user[0]
        return redirect(url_for("user", user_id=uID))

    return render_template("login.html")


"""
    Extracts the user's information from the database and displays it on the user's home page.
    
    PART I
    1. The trading_sessions.html page will redirect to another route that displays the result of the trading session.
    2. Creates a new route for this which accept a variable endpoint i.e.<xx>, with the variable being the primary key of the Result Table.
    3. Extracts result from Result Table using the primary key and render an html template to display the extracted record.
    4. The result record page contains the following:
        (a) The overal return of the trading session.
        (b) The risk of the trading session (measured by asset price's standard deviation during that trading period).
        (c) The Sharpe Ratio of the trading session (return divided by std, i.e., step 1 divided by step 2).
        (d) A cumulative return graph plotted against the cumulative return graph of a benchmark.
    
    PART II
    1. The trading_session.html page have a button to accept new trading session created by the user.
    2. The button directs the user to a new route that is similar to the user sign up page which render an html to accept user inputs for the new session.
    3. After user submits, we adds the record into the database table -  UserTradingSessions.
    4. Calculates the result of this session and add it to the Result Table.
    5. The asset can be assumed to be an individual asset with long position.
"""

# ------------------------------------------------------------------------------
# This is the user's home page after login, displaying all trading sessions.
# ------------------------------------------------------------------------------

@app.route("/ts/user/<user_id>")
def user(user_id):
    cursorObject.execute("SELECT * FROM users WHERE uID = %s", (user_id,))
    user = cursorObject.fetchone()
    
    if user:
        cursorObject.execute(
            "SELECT * FROM UserTradingSessions WHERE uID = %s", (user[0],)
        )
        trading_sessions = cursorObject.fetchall()
        
        return render_template(
            "trading_sessions.html",
            userid=user_id,
            user=user,
            trading_sessions=trading_sessions,
            message=f"Welcome {user[1]} {user[2]}! ",
        )
    
    return "User not found."


# ------------------------------------------------------------------------------
# This is the trading session result page.
# ------------------------------------------------------------------------------

@app.route("/ts/user/<user_id>/trading_session_result/<session_id>")
def trading_session_result(session_id, user_id):
    cursorObject.execute(
        "SELECT * FROM Result WHERE sessionID = %s AND uID = %s",
        (session_id, user_id)
    )
    result = cursorObject.fetchone()
    if result:    
        return render_template(
            "trading_session_result.html",
            result=result,
            overall_return=result[2],
            risk=result[3],
            sharpe_ratio=result[4]
        )

    return "Trading session result not found."


# ------------------------------------------------------------------------------
# This is the new trading session page.
# ------------------------------------------------------------------------------

@app.route("/ts/user/<user_id>/new_trading_session", methods=["GET", "POST"])
def new_trading_session(user_id):
    if request.method == "POST":
        # Extracts new trading session information from the form and inserts it into the database.
        preference = request.form["preference"].lower()
        ticker = request.form["ticker"]
        
        # Uses the preference and ticker to find the underlying ID.
        # Determines the table and column based on preference.
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

        # Queries the underlying ID based on ticker.
        cursorObject.execute(
            f"SELECT DISTINCT {id_column} FROM {table} WHERE ticker = %s", (ticker,)
        )
        underlying = cursorObject.fetchone()
        if not underlying:
            return f"No underlying asset found with ticker {ticker} in {preference}."
        underlyingID = f"{table}-{ticker}-{underlying[0]}"

        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        volume = int(request.form["volume"])

        cursorObject.execute(
            "INSERT INTO UserTradingSessions (uID, startDay, endDay, volume, underlyingID, positionLS) "
            "VALUES (%s, %s,%s,%s,%s,%s)",
            (user_id, start_date, end_date, volume, underlyingID, "L"),
        )
        DB_Connection.commit()

        # Retrieves all trading sessions for the user.
        cursorObject.execute(
            "SELECT sessionID, volume FROM UserTradingSessions WHERE uID = %s",
            (user_id,),
        )
        sessions = cursorObject.fetchall()

        # Calculates the total volume.
        total_volume = sum(session[1] for session in sessions)
        cursorObject.execute(
            "INSERT INTO Portfolio (uID, sessionID, weight) VALUES (%s,%s,%s)",
            (user_id, sessions[-1][0], 0),
        )

        # Updates the weight for each session based on the new total volume.
        for session in sessions:
            session_id = session[0]
            session_volume = session[1]
            weight = session_volume / total_volume
            
            cursorObject.execute(
                "UPDATE Portfolio SET weight = %s WHERE sessionID = %s",
                (weight, session_id),
            )
        DB_Connection.commit()

        # Calculates results for the new session.
        cursorObject.execute(
            f"SELECT * FROM {table} "
            f"WHERE sID = {underlying[0]} AND day BETWEEN '{start_date}' AND '{end_date}'"
        )
        result = cursorObject.fetchall()

        # ----------------------------------------------------------------------
        # Calculates the overall return, risk, and Sharpe ratio.
        # ----------------------------------------------------------------------
        
        overall_return = -float(utils.calculate_overall_return(result))
        risk = float(utils.calculate_risk(result))
        sharpe_ratio = (
            round(overall_return / risk, 2) if risk != 0 else 0
        )
        utils.plot_cumulative_return(result)

        cursorObject.execute(
            "INSERT INTO Result (uID, sessionID, gain, risk, SharpeRatio) "
            "VALUES (%s, %s, %s, %s, %s)",
            (user_id, session_id, overall_return, risk, sharpe_ratio),
        )
        DB_Connection.commit()

        return redirect(url_for("user", user_id=user_id))

    stock_tickers = get_unique_tickers("Stocks")
    index_tickers = get_unique_tickers("Indices")
    etf_tickers = get_unique_tickers("ETFs")

    return render_template(
        "new_trading_session.html",
        user_id=user_id,
        stock_tickers=stock_tickers,
        index_tickers=index_tickers,
        etf_tickers=etf_tickers,
        image_names="cumulative_returns.png"
    )


def get_unique_tickers(table_name):
    query = f"SELECT DISTINCT ticker FROM {table_name}"
    cursorObject.execute(query)

    # Fetches all the tickers from the table.
    tickers = [row[0] for row in cursorObject.fetchall()]
    return tickers


# ------------------------------------------------------------------------------
# This is the delete trading session page.
# ------------------------------------------------------------------------------

@app.route("/ts/delete_trading_session/<session_id>/<user_id>", methods=["POST"])
def delete_trading_session(session_id, user_id):
    # Delete the trading session
    delete_id = session_id
    cursorObject.execute("DELETE FROM portfolio WHERE sessionID = %s", (delete_id,))
    cursorObject.execute("DELETE FROM Result WHERE sessionID = %s", (delete_id,))
    cursorObject.execute(
        "DELETE FROM usertradingsessions WHERE sessionID = %s", (delete_id,)
    )
    DB_Connection.commit()

    # Retrieves all trading sessions for the user.
    cursorObject.execute(
        "SELECT sessionID, volume FROM UserTradingSessions WHERE uID = %s", (user_id,)
    )
    sessions = cursorObject.fetchall()

    # Calculates the total volume.
    total_volume = sum(session[1] for session in sessions)

    # Updates the weight for each session based on the new total volume.
    for session in sessions:
        session_id = session[0]
        session_volume = session[1]
        weight = session_volume / total_volume if total_volume > 0 else 0
        cursorObject.execute(
            "UPDATE Portfolio SET weight = %s WHERE sessionID = %s",
            (weight, session_id),
        )
    DB_Connection.commit()

    return redirect(url_for("user", user_id=user_id))


# ------------------------------------------------------------------------------
# This is the portfolio page.
# ------------------------------------------------------------------------------

@app.route("/portfolio/<int:user_id>")
def portfolio(user_id):
    cursorObject.execute("SELECT * FROM Users WHERE uID = %s", (user_id,))
    user = cursorObject.fetchone()
    
    cursorObject.execute(
        "SELECT sessionID, weight FROM Portfolio WHERE uID = %s", (user_id,)
    )
    portfolio = cursorObject.fetchall()
    
    return render_template(
        "portfolio.html", user=user, user_id=user_id, portfolio=portfolio
    )


# ------------------------------------------------------------------------------
# This is the asset home page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset")
def asset():
    return render_template("asset.html")


# ------------------------------------------------------------------------------
# This is the asset price main page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price")
def price():
    return render_template("price.html")


# ------------------------------------------------------------------------------
# This is the stock asset price page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/stocks")
def stocks():
    # Extracts all stock tickers from database to display.
    cursorObject.execute("SELECT DISTINCT ticker FROM Stocks;")
    stock_tickers = [item[0] for item in cursorObject.fetchall()]
    
    return render_template("stocks.html", tickers=stock_tickers)


# ------------------------------------------------------------------------------
# This is the individual stock's all price data page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/stocks/<ticker>")
def stock_ticker_data(ticker):
    # Extracts all price data of this stock ticker from database and display it.
    query = (
        "SELECT day, open, high, low, close FROM Stocks WHERE ticker='"
        + ticker
        + "' ORDER BY day DESC;"
    )
    cursorObject.execute(query)
    
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    
    return render_template("stock_ticker.html", tick=ticker, data=price_data)


# ------------------------------------------------------------------------------
# This is the index asset price page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/indices")
def indices():
    # Extracts all index tickers from database to display.
    cursorObject.execute("SELECT DISTINCT ticker FROM Indices;")
    index_tickers = [item[0] for item in cursorObject.fetchall()]
    
    return render_template("indices.html", tickers=index_tickers)


# ------------------------------------------------------------------------------
# This is the individual index's all price data page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/indices/<ticker>")
def index_ticker_data(ticker):
    query = (
        "SELECT day, open, high, low, close FROM Indices WHERE ticker='"
        + ticker
        + "' ORDER BY day DESC;"
    )
    cursorObject.execute(query)
    
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    
    return render_template("index_ticker.html", tick=ticker, data=price_data)

# ------------------------------------------------------------------------------
# This is the ETF asset price page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/etfs")
def etfs():
    # Extracts all ETF tickers from database to display.
    cursorObject.execute("SELECT DISTINCT ticker FROM ETFs;")
    etf_tickers = [item[0] for item in cursorObject.fetchall()]
    
    return render_template("etfs.html", tickers=etf_tickers)


# ------------------------------------------------------------------------------
# This is the individual ETF's all price data page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/price/etfs/<ticker>")
def etf_ticker_data(ticker):
    # Extracts all price data of this ETF ticker from database and display it.
    query = (
        "SELECT day, open, high, low, close FROM ETFs WHERE ticker='"
        + ticker
        + "' ORDER BY day DESC;"
    )
    cursorObject.execute(query)
    
    price_data_raw = cursorObject.fetchall()
    price_data = [process_raw_price(item) for item in price_data_raw]
    
    return render_template("etf_ticker.html", tick=ticker, data=price_data)


# ------------------------------------------------------------------------------
# This is the asset alpha main page.
# ------------------------------------------------------------------------------

@app.route("/ts/asset/alpha", methods=["GET", "POST"])
def alpha():
    if request.method == "POST":
        # Extracts asset info from the html request to plot alphas on.
        asset_type = request.form["assettype"]
        ticker = request.form["ticker"]
        start_date = request.form["startdate"]
        end_date = request.form["enddate"]

        # Queries the database to get asset price data.
        if asset_type == "stock":
            DB_Table = "Stocks"
        elif asset_type == "index":
            DB_Table = "Indices"
        elif asset_type == "ETF":
            DB_Table = "ETFs"
        else:
            # Error handling and redirects to alpha.html.
            render_template("alpha.html")

        # The error handling for the ticker.
        ticker_query = "SELECT DISTINCT ticker FROM " + DB_Table + ";"
        cursorObject.execute(ticker_query)
        tickers = [item[0] for item in cursorObject.fetchall()]
        if ticker not in tickers:
            # Error handling and redirects to alpha.html.
            render_template("alpha.html")

        # Gets price data.
        data_query = (
            "SELECT day, open, high, low, close FROM "
            + DB_Table
            + " WHERE ticker='"
            + ticker
            + "' AND day>='"
            + start_date
            + "' AND day<='"
            + end_date
            + "' ORDER BY day ASC;"
        )
        cursorObject.execute(data_query)
        price_data = [process_raw_price(row) for row in cursorObject.fetchall()]

        # Plots alphas using asset price, plot asset price as well.
        image_names = plot_price_with_alphas(price_data)

        return render_template(
            "view_with_alphas.html", tick=ticker, image_names=image_names
        )

    return render_template("alpha.html")


app.run(host="0.0.0.0", port=5001, debug=True)
