# Trading System Database Setup

This module sets up the **MySQL relational database** for the Trading System project. It includes scripts to create the database schema and automate data loading from CSV files containing Stocks, Indices, and ETFs information.

## Contents
- `TradingSystem.sql` — Defines the database schema using SQL (tables, relationships, etc.).
- `DB_Insert.py` — Python script to load CSV data into the database via MySQL's Python API.
- `Stocks/`, `Indices/`, `ETFs/` — Directories containing CSV datasets.

## Prerequisites
- **MySQL** installed and running.
- **Python 3.x** installed.
- Install required Python package:
  ```bash
  pip install mysql-connector-python
  ```

## Setup Instructions
**1. Start MySQL Server**  
- Ensure your MySQL server is running.

**2. Create Database Schema**  
- Run the following command to execute the schema script:
```bash
mysql -u root -p < TradingSystem.sql
```
This will create the necessary database and tables.

**3. Load Data into Database**  
- Execute the Python script to automatically load all CSV files from the `Stocks/`, `Indices/`, and `ETFs/` directories:
```bash
python DB_Insert.py
```
This script will:  
- Connect to your MySQL database.
- Parse CSV files.
- Insert data into corresponding tables.

## Directory Structure
```bash
├── TradingSystem.sql
├── DB_Insert.py
├── Stocks/
├── Indices/
└── ETFs/
```

## Note
- Ensure that database connection settings (username, password, host) inside DB_Insert.py match your local MySQL configuration.  
- CSV files should follow the expected format as defined in the schema.

## License
For academic use only.
