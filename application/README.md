# Trading System Web Application

This is the **Flask-based web interface** for the Trading System project. The application connects to a MySQL database and allows users to interact with trading data (Stocks, Indices, ETFs) through a dynamic web UI powered by SQL queries.

## Prerequisites
- MySQL database set up via the [`database`](https://github.com/yaodan-zhang/trading-system/tree/main/database) folder.
- **Python 3.x** installed.
- Install required Python packages:

```bash
pip install flask mysql-connector-python
```

## Setup & Running the Application
**1. Ensure MySQL Database is Running**
Confirm that:
- Schema is created (TradingSystem.sql).
- Data is loaded using DB_Insert.py.

**2. Configure Database Connection**
In app.py and/or utils.py, verify:
- Host, User, Password, Database name.

**3. Launch the Flask App**
From the application directory:
```bash
python app.py
```
Access the app at:
`http://127.0.0.1:5000/`

## Features
- Web-based querying of trading datasets.

- Modular backend using utils.py for database operations.

- Lightweight, maintainable Flask architecture.

## Project Structure
```bash
application/
├── app.py          # Main Flask application
├── utils.py        # Helper functions for DB interactions
├── templates/      # HTML templates (if applicable)
└── static/         # CSS/JS assets (if applicable)
```

## License
For academic use only.
