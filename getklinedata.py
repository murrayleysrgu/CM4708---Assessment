import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from pymongo import MongoClient
from dotenv import load_dotenv

# get enironmet variables
load_dotenv()
DB_URI = os.getenv('DB_URI')
print('DB==', DB_URI)  # Check that env variabes are loaded correctly

URL = "https://api.binance.com/api/v3/klines"
tokenpair = "ETHBUSD"
interval_short = "5m"
interval_medium = "1h"
interval_long = "6h"
limit = 1000
PARAMS_SHORT = {'symbol': tokenpair, 'interval': interval_short, 'limit': limit}
PARAMS_MEDIUM = {'symbol': tokenpair, 'interval': interval_medium, 'limit': limit}
PARAMS_LONG = {'symbol': tokenpair, 'interval': interval_long, 'limit': limit}

# intervals supported: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo

# RETURNED DATA
# Open time
# Open
# High
# Low
# Close
# Volume
# Close time
# Quote asset volume
# Number of trades
# Taker buy base asset volume
# Taker buy quote asset volume
# Ignore


# download data from Binance
# short term data
raw_data = requests.get(url=URL, params=PARAMS_SHORT)
json_data = raw_data.json()
df = pd.DataFrame(json_data, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])

df['Open'] = df['Open'].astype(float)
df['Close'] = df['Close'].astype(float)
df['High'] = df['High'].astype(float)
df['Low'] = df['Low'].astype(float)
df['Volume'] = df['Volume'].astype(float)
df['QtyOfTrades'] = df['QtyOfTrades'].astype(float)
df['timeindex'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.CloseTime]

# Medium term price data
raw_data2 = requests.get(url=URL, params=PARAMS_MEDIUM)
json_data2 = raw_data2.json()
df2 = pd.DataFrame(json_data2, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                                        'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])
df2['Close'] = df2['Close'].astype(float)
df2['timeindex'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df2.CloseTime]
df2 = df2[df2.timeindex >= df['timeindex'].min()]

# Long term price data
raw_data3 = requests.get(url=URL, params=PARAMS_LONG)
json_data3 = raw_data3.json()
df3 = pd.DataFrame(json_data3, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                                        'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])
df3['Close'] = df3['Close'].astype(float)
df3['timeindex'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df3.CloseTime]
df3 = df3[df3.timeindex >= df['timeindex'].min()]


# Plot graph of data and compare to correct plot on tradingview.com to verify that the downloaded data is corect
ax = df.plot(x='timeindex', y='Close', title=tokenpair + ' :: Price Data', label='Close ' + interval_short)
df2.plot(ax=ax, x='timeindex', y='Close', label="Close " + interval_medium)
df3.plot(ax=ax, x='timeindex', y='Close', label="Close " + interval_long)
plt.show()

# Save the price data to Database - prevent over use of api and backup data
db_client = MongoClient(DB_URI)
database = db_client.trader
print(database.list_collection_names())
dict = df.to_dict('records')
collection = database['ETHBUSD-5m']
x= collection.delete_many({})
x = collection.insert_many(df.to_dict('records'))
print(len(x.inserted_ids), 'price entries added to the database')
