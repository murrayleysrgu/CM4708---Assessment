

This code requires a MongoDB database called trader
setup its uri via the DB_URI variable in a .env file

run the below command to setup a conda environent and install the dependencies 
conda env create -f requirements.yml


To conduct the experiment as detailed in the report, run the experiment.py python module which will in turn run the below python modules in the following order

getklinedata.py
dataanalysis.py
model.py
validation.py

getklinedata will download Kline data from the Binance API 
dataanalysis will performa analysis on teh downloded data
model.py will create, train, test and save the model
validation will evaluate the model on the latest data from Binance and report on its performance

More information on the Binance API can be found via the below link
https://github.com/binance/binance-spot-api-docs
