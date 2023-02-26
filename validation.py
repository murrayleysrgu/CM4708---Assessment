
import os
import requests
import pymongo
import pandas as pd
import numpy as np

import datetime as dt
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model


def create_windowed_dataset(dataset, step=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - step - 1):
        a = dataset[i:i + step, 0]
        dataX.append(a)
        dataY.append(dataset[i + step, 0])
    return np.array(dataX), np.array(dataY)


def validation():
    # get enironmet variables
    load_dotenv()
    DB_URI = os.getenv('DB_URI')

    # Setup database connection
    db_client = pymongo.MongoClient(DB_URI)
    database = db_client.trader

    # Get price data from database
    collection = database['ETHBUSD-1h']
    x = collection.find().sort("CloseTime", 1)
    df = pd.DataFrame(list(x))

    load_dotenv()
    DB_URI = os.getenv('DB_URI')
    print('DB==', DB_URI)  # Check that env variabes are loaded correctly

    # Get the latest data from API
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
    # Low:w
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
    # Medium term price data
    raw_data2 = requests.get(url=URL, params=PARAMS_MEDIUM)
    print('Headers:', raw_data2.headers)
    print('Status Code:', raw_data2.status_code)
    print(raw_data2)
    json_data2 = raw_data2.json()
    df = pd.DataFrame(json_data2, columns=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume',
                                           'QtyOfTrades', 'TBBAV', 'TBQAV', 'Ignore'])
    df['Close'] = df['Close'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['High'] = df['High'].astype(float)

    df['timeindex'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.CloseTime]
    print(df)

    min5 = df
    hrdata = df[df.OpenTime % 3600000 == 0].reset_index()['Close']
    df1 = df.reset_index()['Close']

    # Uncomment if you want to validate against historical data stored in the database
    # print(hrdata)
    # print(df1.shape)
    # print(df1[899:1000])
    # print(df1.tail())
    # collection = database['ETHBUSD-1h']
    # x1 = collection.find()
    # df = pd.DataFrame(list(x1))
    #
    # plt.plot(df)
    # ax = df.plot(x='timeindex', y='Close', label="Close 1h")
    # plt.show()

    scaler = MinMaxScaler(feature_range=(0, 1))
    df1 = scaler.fit_transform(np.array(df1).reshape(-1, 1))
    print(df1.shape)

    training_size = int(len(df1) * 0.80)
    # test_size = len(df1) - training_size

    # print(df1, test_size)

    training_data, test_data = df1[0:training_size, :], df1[training_size:len(df1), :1]
    test_data = df1

    window = 100
    x_train, y_train = create_windowed_dataset(training_data, window)
    x_test, y_test = create_windowed_dataset(test_data, window)

    x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

    new_model = load_model("ethbusdmodel-1h-lstm.h5")
    new_model.summary()

    loaded_predictions = new_model.predict(x_test)
    loaded_predictions = scaler.inverse_transform(loaded_predictions)

    # print("Data Slice")
    # print(df1[900:1000])
    # print("Number of Predictions:", len(loaded_predictions))
    trade_predictions = []
    for i in range(len(loaded_predictions)):
        # if loaded_predictions[i - 1] < loaded_predictions[i]:
        #     trade_predictions.append(1)
        # else:
        #     trade_predictions.append(-1)
        ppl = (loaded_predictions[i][0] - loaded_predictions[i - 1][0]) / loaded_predictions[i - 1][0]
        trade_predictions.append(ppl)

    # print(trade_predictions, len(trade_predictions))

    fund = 100
    leverage = 10
    df = pd.DataFrame(list(x))
    correct = []
    balance = [fund]
    stop_loss_per = 9.029  # Replace 9 with 0 to add stop loss to teh validation model
    tradepl = []
    # print(min5)
    # print("Number of Predictions:")
    # print(len(trade_predictions))
    training_size = 0  # Use whole dataset - no train split required

    # Run through data placing dummy trades to validaet model and strategy
    for i in range(0, len(loaded_predictions) - 1):
        pl = (min5.Close[i + training_size + window] - min5.Close[i + training_size + window - 1]) / min5.Close[i + training_size + window - 1] * leverage
        stop_loss = stop_loss_per * min5.Close[i + training_size + window - 1]
        tradepl.append(pl)
        if pl > 0:
            # if min5.Low[i + training_size + window] <= 0 - stop_loss + min5.Close[i + training_size + window - 1]:
            if min5.High[i + training_size + window] >= stop_loss + min5.Close[i + training_size + window - 1]:
                correct.append(-1)
                pl = stop_loss_per
                print("STOP LOSS TRIGGERES", stop_loss, pl)
            elif loaded_predictions[i] > min5.Close[i + training_size + window - 1]:
                correct.append(1)
            else:

                correct.append(-1)
        else:
            if min5.Low[i + training_size + window] <= 0 - stop_loss + min5.Close[i + training_size + window - 1]:
                correct.append(-1)
                pl = stop_loss_per
                print("STOP LOSS TRIGGERES", stop_loss, pl)
            elif loaded_predictions[i] < min5.Close[i + training_size + window - 1]:
                correct.append(1)
            else:
                correct.append(-1)

        fund = fund + abs(pl) * correct[i] * fund
        print(fund, i, "LAST:", min5.Close[i + training_size + window - 1], "NOW:", min5.Close[i + training_size + window],
              "SLOSS:", stop_loss, "HIGH:", min5.High[i + training_size + window], "PREDICTION:", loaded_predictions[i], "PL:", pl * 100, trade_predictions[i], correct[i])

        if fund < 0:
            fund = 0
        balance.append(fund)

    print(len([x for x in correct if x == 1]) / len(correct) * 100)

    print(len([x for x in correct if x == 1]))
    print(len([x for x in correct if x != 1]))
    print(len(correct))
    plt.plot(balance)
    plt.xlabel("Hours (No. of Trades)")
    plt.ylabel("Account Balance")
    plt.title("Trading Strategy Model Validation")
    plt.show()

    return


if __name__ == "__main__":
    validation()
