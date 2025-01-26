import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose
from pandas.plotting import autocorrelation_plot
from sklearn.preprocessing import StandardScaler
from prophet import Prophet
from datetime import datetime

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

sub_file = pd.read_csv('data/sample_submission.csv')


def transform_data(data):
    if 'num_sold' in data.columns: 
        data.fillna({'num_sold':0}, inplace=True)

    data['month'] = pd.to_datetime(data['date']).dt.month
    data['year'] = pd.to_datetime(data['date']).dt.year
    data['season'] = data['month'].map({1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring', 6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Autumn', 10: 'Autumn', 11: 'Autumn', 12: 'Winter'})

    # change season to categorical
    data['season'] = data['season'].astype('category')
    data['season'] = data['season'].cat.codes

    # change product to categorical
    data['product'] = data['product'].astype('category')
    data['product'] = data['product'].cat.codes

    # change country to categorical
    data['country'] = data['country'].astype('category')
    data['country'] = data['country'].cat.codes

    # change store to categorical
    data['store'] = data['store'].astype('category')
    data['store'] = data['store'].cat.codes

    # change store to categorical
    data['year'] = data['year'].astype('category')
    data['year'] = data['year'].cat.codes

    data[['country', 'store', 'product',  'month', 'year', 'season']] = data[['country', 'store', 'product',  'month', 'year', 'season']].astype(int)

    return data

train = transform_data(train)
test = transform_data(test)

# log scale train and test
train_log = train.copy()
test_log = test.copy()

train_log[['country', 'store', 'product',  'month', 'year', 'season','num_sold']] = train_log[['country', 'store', 'product',  'month', 'year', 'season', 'num_sold']] + 1
test_log[['country', 'store', 'product',  'month', 'year', 'season']] = test_log[['country', 'store', 'product',  'month', 'year', 'season']] + 1

train_log[['country', 'store', 'product',  'month', 'year', 'season','num_sold']] = np.log(train_log[['country', 'store', 'product',  'month', 'year', 'season','num_sold']])
test_log[['country', 'store', 'product',  'month', 'year', 'season']] = np.log(test_log[['country', 'store', 'product',  'month', 'year', 'season']])


# start scaling 
scaler = StandardScaler()

train_log[['country', 'store', 'product',  'month', 'year', 'season']] = scaler.fit_transform(train_log[['country', 'store', 'product',  'month', 'year', 'season']])
test_log[['country', 'store', 'product',  'month', 'year', 'season']] = scaler.transform(test_log[['country', 'store', 'product',  'month', 'year', 'season']])

train[['country', 'store', 'product',  'month', 'year', 'season']] = scaler.fit_transform(train[['country', 'store', 'product',  'month', 'year', 'season']])
test[['country', 'store', 'product',  'month', 'year', 'season']] = scaler.transform(test[['country', 'store', 'product',  'month', 'year', 'season']])

# rename date and target column 
train_log = train_log.rename(columns={'date': 'ds', 'num_sold': 'y'})
test_log = test_log.rename(columns={'date': 'ds', 'num_sold': 'y'})

train = train.rename(columns={'date': 'ds', 'num_sold': 'y'})
test = test.rename(columns={'date': 'ds', 'num_sold': 'y'})

train = train.drop(columns=['id'])
test = test.drop(columns=['id'])

# Initialize and fit the Prophet model
model = Prophet()
model.fit(train)


# predict y given a df of x values
test_pred = model.predict(test)

# non log submission 1 
sub_file['num_sold'] = test_pred['yhat']
# add timestamp to file name 
file_name = datetime.now().strftime('submissions/submission_%Y%m%d_%H%M.csv')
sub_file.to_csv(file_name, index=False)