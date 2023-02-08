import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

URL = "https://api.binance.com/api/v3/klines"
tokenpair = "ETHBUSD"
interval_short = "5m"
interval_medium = "1h"
interval_long = "6h"
PARAMS_SHORT = {'symbol': tokenpair, 'interval': interval_short}
PARAMS_MEDIUM = {'symbol': tokenpair, 'interval': interval_medium}
PARAMS_LONG = {'symbol': tokenpair, 'interval': interval_long}

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
df = pd.DataFrame(json_data, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                                      'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])
df['Close'] = df['Close'].astype(float)
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
