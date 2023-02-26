from getklinedata import getklinedata
from dataanalysis import dataanalysis
from model import model
from validation import validation

print('CM47080 Assessment - Experiment')
print('Downloading and Storing Kline data')
getklinedata()
print('Begin Data Analysis')
dataanalysis()
print('Create, train and test model')
model()
print('Validating model')
validation()
print('Experiment Complete')
