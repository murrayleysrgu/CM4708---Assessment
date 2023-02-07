import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

URL = "https://api.binance.com/api/v3/klines"
tokenpair = "ETHBUSD"
interval = "5m"
PARAMS = {'symbol': tokenpair, 'interval': interval}

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
raw_data = requests.get(url=URL, params=PARAMS)
json_data = raw_data.json()
df = pd.DataFrame(json_data, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                                      'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])
df['Close'] = df['Close'].astype(float)
df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.CloseTime]

# print(json_data)  # Check that data is downloaded correctly
# print(df.dtypes)

# Plot graph of data and compare to correct plot on tradingview.com to verify that the downloaded data is corect
df["Close"].plot(title=tokenpair + ' :: ' + interval, legend='close')
plt.show()
