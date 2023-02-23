import os
import random
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

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
hrdata = df[df.OpenTime % 3600000 == 0]

print(hrdata)  # Confirm data is correctly returned


# calculate potential profits
# 50% win rate
leverage = 10
initial_investment = 100

# win percentages
random_luck = 0.5
small = 0.55
medium = 0.6
high = 0.69

lower_limit = 50
upper_limit = 66

interest_rate = 0.022192
lossper = []
for loop in range(lower_limit, upper_limit):
    high = loop / 100
    print('Calculating: ', high)
    maxh = 0
    minh = initial_investment * 1000
    high_returns = []

    for j in range(0, 1000):
        fund_luck = [initial_investment]
        fund_small = [initial_investment]
        fund_medium = [initial_investment]
        fund_high = [initial_investment]

        win_luck = []
        fund_luck = [initial_investment]

        # _medium% win rate
        win_small = []
        fund_small = [initial_investment]

        # _medium% win rate
        win_medium = []
        fund_medium = [initial_investment]

        # _large% win rate
        win_high = []
        fund_high = [initial_investment]

        for i in range(1, 672):  # df.shape[0] - 1)::
            chance = random.random()
            chance2 = random.random()
            chance3 = random.random()
            chance4 = random.random()
            pl = (df.Close[i] - df.Close[i - 1]) / df.Close[i - 1]
            if chance <= random_luck:
                win_luck.append(abs(pl))
            else:
                win_luck.append(0 - abs(pl))

            if chance2 <= small:
                win_small.append(abs(pl))
            else:
                win_small.append(0 - abs(pl))

            if chance3 <= medium:
                win_medium.append(abs(pl))
            else:
                win_medium.append(0 - abs(pl))

            if chance4 <= high:
                win_high.append(abs(pl))
            else:
                win_high.append(0 - abs(pl))

        for i in range(0, len(win_high) - 1):
            fund_luck.append(max(0, fund_luck[i] * (1 + win_luck[i] * leverage) - fund_luck[i] * leverage * interest_rate / 24 / 100))
            fund_small.append(max(0, fund_small[i] * (1 + win_small[i] * leverage) - fund_small[i] * leverage * interest_rate / 24 / 100))
            fund_medium.append(max(0, fund_medium[i] * (1 + win_medium[i] * leverage) - fund_medium[i] * leverage * interest_rate / 24 / 100))
            fund_high.append(max(0, fund_high[i] * (1 + win_high[i] * leverage) - fund_high[i] * leverage * interest_rate / 24 / 100))
        # print('high', len(fund_high), win_high)
        maxh = max(maxh, fund_high[len(fund_high)-1])
        minh = min(minh, fund_high[len(fund_high)-1])
        high_returns.append(fund_high[len(fund_high)-1])

    losses = sorted(i for i in high_returns if i < 100)
    lossper.append(len(losses) / 10)

print(lossper)
# plt.plot([50,51,52,53,54,55,56,57,58,59,60,61,62,63,64], lossper)
plt.plot([*range(lower_limit, upper_limit)], lossper)
plt.xlabel("Model Accuaracy %")
plt.ylabel("% Chance of Losing initial Investment Fund")
plt.title("Trading Strategy Validation")
plt.show()

perf = pd.DataFrame(list(zip(fund_luck, fund_small, fund_medium, fund_high)), columns=['luck - 50%',
                                                                                       'small - ' + str(int(small * 100)) + '%',
                                                                                       'medium - ' + str(int(medium * 100)) + '%',
                                                                                       'high - ' + str(int(high * 100)) + '%'])


plt.plot(win_luck)
plt.show()

print('MIN ?? MAX ', minh, maxh)
print(perf.describe(include='all'))
high_returns.sort()
losses = sorted(i for i in high_returns if i < 100)
wins = sorted(i for i in high_returns if i > 100)
# print(high_returns)
print('Loss:', len(losses) / 10, '%', losses)
perf.plot()
plt.show()
