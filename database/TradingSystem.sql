-- TradingSystem.sql
-- This file contains the SQL code to create the database schema for the TradingSystem.
-- The schema includes the following tables:
--     1. Stocks: contains the stock data.
--     2. Indices: contains the index data.
--     3. ETFs: contains the ETF data.
--     4. Compose: contains the relationship between indices and stocks.
--     5. Users: contains the user data.
--     6. UserTradingSessions: contains the user trading session data.
--     7. Result: contains the result data.
--     8. Portfolio: contains the portfolio data.


-- DROP DATABASE TradingSystem;

DROP DATABASE TradingSystem;
CREATE DATABASE TradingSystem;
USE TradingSystem;


-- This table contains the stock data.
CREATE TABLE Stocks(
    sID INTEGER,
    ticker VARCHAR(50) NOT NULL,
    open DECIMAL(20, 10) NOT NULL,
    high DECIMAL(20, 10) NOT NULL,
    low DECIMAL(20, 10) NOT NULL,
    close DECIMAL(20, 10) NOT NULL,
    day Date NOT NULL,
    PRIMARY KEY(sID, day),
    CHECK(
        open > 0
        AND high > 0
        AND low > 0
        AND close > 0
    )
);


-- This table contains the index data.
CREATE TABLE Indices(
    iID INTEGER,
    ticker VARCHAR(50) NOT NULL,
    open DECIMAL(20, 10) NOT NULL,
    high DECIMAL(20, 10) NOT NULL,
    low DECIMAL(20, 10) NOT NULL,
    close DECIMAL(20, 10) NOT NULL,
    day Date NOT NULL,
    PRIMARY KEY(iID, day),
    CHECK(
        open > 0
        AND high > 0
        AND low > 0
        AND close > 0
    )
);


-- This table contains the ETF data.
CREATE TABLE ETFs(
    eID INTEGER,
    ticker VARCHAR(50) NOT NULL,
    open DECIMAL(20, 10) NOT NULL,
    high DECIMAL(20, 10) NOT NULL,
    low DECIMAL(20, 10) NOT NULL,
    close DECIMAL(20, 10) NOT NULL,
    day Date NOT NULL,
    PRIMARY KEY(eID, day),
    CHECK(
        open > 0
        AND high > 0
        AND low > 0
        AND close > 0
    )
);


-- This table contains the relationship between indices and stocks.
CREATE TABLE Compose(
    iID INTEGER NOT NULL,
    sID INTEGER NOT NULL,
    PRIMARY KEY (iID, sID),
    FOREIGN KEY (sID) REFERENCES Stocks(sID),
    FOREIGN KEY (iID) REFERENCES Indices(iID)
);


-- This table contains the user data.
CREATE TABLE Users(
    uID INTEGER NOT NULL AUTO_INCREMENT,
    firstName VARCHAR(20) DEFAULT "no first name",
    lastName VARCHAR(20) DEFAULT "no last name",
    phone VARCHAR(20) DEFAULT "000-000-0000",
    email VARCHAR(50) DEFAULT "email not provided",
    preferences VARCHAR(20) DEFAULT "all",
    PRIMARY KEY (uID),
    CHECK (
        preferences IN (
            "stock",
            "index",
            "ETF",
            "stock&index",
            "stock&ETF",
            "index&ETF",
            "all"
        )
    )
);


-- This table contains the user trading session data.
CREATE TABLE UserTradingSessions(
    sessionID INTEGER NOT NULL AUTO_INCREMENT,
    uID INTEGER NOT NULL,
    startDay DATE NOT NULL,
    endDay DATE NOT NULL,
    volume INTEGER DEFAULT 1,
    underlyingID VARCHAR(255) NOT NULL,
    positionLS VARCHAR(1) DEFAULT "L",
    PRIMARY KEY (sessionID, uID),
    CHECK (volume > 0),
    CHECK (positionLS IN ("L", "S")),
    FOREIGN KEY (uID) REFERENCES Users(uID)
);


-- This table contains the result data.
CREATE TABLE Result(
    uID INTEGER NOT NULL,
    sessionID INTEGER NOT NULL,
    gain DECIMAL(5, 2) NOT NULL,
    risk DECIMAL(10, 2) NOT NULL,
    SharpeRatio DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (uID, sessionID),
    FOREIGN KEY (uID) REFERENCES Users(uID),
    FOREIGN KEY (sessionID) REFERENCES UserTradingSessions(sessionID)
);


-- This table contains the portfolio data.
CREATE TABLE Portfolio(
    uID INTEGER NOT NULL,
    sessionID INTEGER NOT NULL,
    weight Decimal(10, 2) DEFAULT 1,
    PRIMARY KEY (uID, sessionID),
    FOREIGN KEY (uID) REFERENCES Users(uID),
    FOREIGN KEY (sessionID) REFERENCES UserTradingSessions(sessionID)
);


-- Insert some sample data into the tables.
-- SELECT *
-- FROM Stocks;


-- SELECT *
-- FROM Indices;


-- SELECT *
-- FROM ETFs;


-- SELECT *
-- FROM Users;


-- SELECT *
-- FROM Portfolio;


-- SELECT *
-- FROM UserTradingSessions;
