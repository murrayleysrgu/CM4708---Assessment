import os
import pymongo
import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt
from dotenv import load_dotenv
from requests import models
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import GRU 


# get enironmet variables
load_dotenv()
DB_URI = os.getenv('DB_URI')

# Setup database connection
db_client = pymongo.MongoClient(DB_URI)
database = db_client.trader

# Get price data from database
collection = database['ETHBUSD-5m']
x = collection.find()
df = pd.DataFrame(list(x))
min5 = df
hrdata = df[df.OpenTime % 3600000 == 0].reset_index()['Close']
df1 = df.reset_index()['Close']
print(hrdata)
print(df1.shape)

collection = database['ETHBUSD-1m']
x1 = collection.find()
df1min = pd.DataFrame(list(x1))

plt.plot(df1)
ax = df.plot(x='timeindex', y='Close', label="Close 5m")
df1min.plot(ax=ax, x='timeindex', y='Close', label="Close 1m")
plt.show()

scaler = MinMaxScaler(feature_range=(0,1))
df1 = scaler.fit_transform(np.array(df1).reshape(-1,1))
print(df1.shape)


training_size = int(len(df1)*0.80)
test_size = len(df1) - training_size


training_data, test_data = df1[0:training_size, :], df1[training_size:len(df1), :1]


def create_windowed_dataset(dataset, step=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - step - 1):
        a = dataset[i:i + step, 0]
        dataX.append(a)
        dataY.append(dataset[i + step, 0])
    return np.array(dataX), np.array(dataY)

window = 100
x_train, y_train = create_windowed_dataset(training_data, window)
x_test, y_test = create_windowed_dataset(test_data, window)

print(x_train)
print(x_train.shape)
print(y_train.shape)
print(x_test.shape)
print(y_test.shape)

x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

model = Sequential()
model.add(GRU(50, return_sequences=True, input_shape=(100, 1)))
model.add(GRU(50, return_sequences=True))
model.add(GRU(50))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')

model.summary()

model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=100, batch_size=64, verbose=1)


train_predictions = model.predict(x_train)
test_predictions = model.predict(x_test)

train_predictions=scaler.inverse_transform(train_predictions)
test_predictions=scaler.inverse_transform(test_predictions)

print('train error:', math.sqrt(mean_squared_error(y_train, train_predictions)))
print('test error:', math.sqrt(mean_squared_error(y_test, test_predictions)))


train_predict_plot = np.empty_like(df1)
train_predict_plot[:, :] = np.nan
train_predict_plot[window:len(train_predictions) + window, :] = train_predictions


test_predict_plot = np.empty_like(df1)
test_predict_plot[:, :] = np.nan
test_predict_plot[len(train_predictions) + window * 2 + 1:len(df1) - 1, :] = test_predictions

plt.plot(scaler.inverse_transform(df1))
plt.plot(train_predict_plot, marker='o')
plt.plot(test_predict_plot, marker='o')
plt.show()
