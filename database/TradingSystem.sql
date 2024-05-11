DROP DATABASE TradingSystem;
CREATE DATABASE TradingSystem;
USE TradingSystem;

# Change the primary key to composite (sID, day) because same stock with different dates have same sID.
CREATE TABLE Stocks(
sID INTEGER, # start from 0
ticker VARCHAR(50) NOT NULL,
open DECIMAL(20,10) NOT NULL,
high DECIMAL(20,10) NOT NULL,
low DECIMAL(20,10) NOT NULL,
close DECIMAL(20,10) NOT NULL,
day Date NOT NULL,
PRIMARY KEY(sID, day),
CHECK(open > 0 AND high >0 AND low>0 AND close>0)
);

# Change primary key to (iID, day).
CREATE TABLE Indices(
iID INTEGER, # start from 0
ticker VARCHAR(50) NOT NULL,
open DECIMAL(20,10) NOT NULL,
high DECIMAL(20,10) NOT NULL,
low DECIMAL(20,10) NOT NULL,
close DECIMAL(20,10) NOT NULL,
day Date NOT NULL,
PRIMARY KEY(iID, day),
CHECK(open > 0 AND high >0 AND low>0 AND close>0)
);

# Change primary key to (eID, day).
CREATE TABLE ETFs(
eID INTEGER, # start from 0
ticker VARCHAR(50) NOT NULL,
open DECIMAL(20,10) NOT NULL,
high DECIMAL(20,10) NOT NULL,
low DECIMAL(20,10) NOT NULL,
close DECIMAL(20,10) NOT NULL,
day Date NOT NULL,
PRIMARY KEY(eID, day),
CHECK(open > 0 AND high >0 AND low>0 AND close>0)
);

CREATE TABLE Compose(
iID INTEGER NOT NULL,
sID INTEGER NOT NULL,
PRIMARY KEY (iID,sID),
FOREIGN KEY (sID) REFERENCES Stocks(sID),
FOREIGN KEY (iID) REFERENCES Indices(iID)
);

# We remove AUM since it can be queried from UserTradingSessions
CREATE TABLE Users(
uID INTEGER,
firstName VARCHAR(20) DEFAULT "no first name",
lastName VARCHAR(20) DEFAULT "no last name",
phone VARCHAR(20) DEFAULT "000-000-0000",
email VARCHAR(50) DEFAULT "email not provided",
preferences VARCHAR(20) DEFAULT "all",
PRIMARY KEY (uID),
CHECK (preferences IN ("stock","index","ETF","stock&index","stock&ETF","index&ETF","all"))
);

# Underlying id: p means asset is a portfolio
# others e.g., s0 - s50, i0-i5, e0-e30 refer to sID, iID, eID
CREATE TABLE UserTradingSessions(
sessionID INTEGER NOT NULL,
uID INTEGER NOT NULL,
startDay DATE NOT NULL,
endDay DATE NOT NULL,
volume INTEGER DEFAULT 1,
underlyingID VARCHAR(10) NOT NULL,
positionLS VARCHAR(1) DEFAULT "L",
PRIMARY KEY (sessionID, uID),
CHECK (volume > 0),
CHECK (positionLS IN ("L","S")),
FOREIGN KEY (uID) REFERENCES Users(uID)
);

# We remove the Contain table as it is the same as the Portfolio table.

# Rename return into gain to avoid keyword collision
CREATE TABLE Result(
uID INTEGER NOT NULL,
sessionID INTEGER NOT NULL,
gain DECIMAL(5,2) NOT NULL, 
risk DECIMAL(10,2) NOT NULL,
SharpeRatio DECIMAL(10,2) NOT NULL,
PRIMARY KEY (uID, sessionID),
FOREIGN KEY (uID) REFERENCES Users(uID),
FOREIGN KEY (sessionID) REFERENCES UserTradingSessions(sessionID),
CHECK (gain >= 0),
CHECK (risk > 0),
CHECK (SharpeRatio >= 0)
);

# We remove the start and end day of the portfolio to make it corresponds to a session's start and end day,
# i.e., for each session, the user can either trade a porfolio or an invidisual asset.
CREATE TABLE Portfolio(
uID INTEGER NOT NULL,
sessionID INTEGER NOT NULL,
assetAllocation JSON, # weights must add up to 1
PRIMARY KEY (uID, sessionID),
FOREIGN KEY (uID) REFERENCES Users(uID),
FOREIGN KEY (sessionID) REFERENCES UserTradingSessions(sessionID)
);

# We merge Preferences into Users

# View tables
SELECT * FROM Stocks;
SELECT * FROM Indices;
SELECT * FROM ETFs;