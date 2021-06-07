
# Section 1 - Import packages required for the assignment

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import requests
from bs4 import BeautifulSoup as bs
import re




# timer decorator - to check what functions are taking a long time to run!!
import time
def timer(func):
    """A decorator that prints how long a function took to run."""
    # Define the wrapper function to return.
    def wrapper(*args, **kwargs):
        # When wrapper() is called, get the current time.
        t_start = time.time()
        # Call the decorated function and store the result.
        result = func(*args, **kwargs)
        # Get the total time it took to run, and print it.
        t_total = time.time() - t_start
        print('{} took {}s'.format(func.__name__, t_total))
        return result
    return wrapper


###############################################################################################################
# Section 2.1 - Get the tickers for all stocks that trade on the NYSE & the NASDAQ and import them into Pycharm
###############################################################################################################

# The list of stocks traded on either the NYSE or the NASDAQ was sourced from the NASDAQ website
# (https://www.nasdaq.com/market-activity/stocks/screener) on the 05/06/2021

stocks = pd.read_csv(r'Files\NYSE_NASDAQ_stocks_20210604.csv')

# Section 2.2 - Exploratory data analysis

stocks.head()  # print out the first 5 rows
stocks.shape  # 7,377 stocks with 11 different features
stocks.describe()  # No issues with any of the data, the min IPO year is 1972 and the max IPO year is 2021
stocks.dtypes  # IPO year should be an integer
stocks.isnull().sum()
# There is a large number of Nulls for % Change (3), Market cap (476), Country (597),
# IPO year (3100), sector (1910) and industry (1911).
# Given that these unpopulated fields are populated in yahoo finance I will only use the ticker value going forward

# Stock name
stock_df = stocks[['Symbol','Name']]
stock_name_list = (list(stock_df.to_records(index=False)))
print(stock_name_list)


# Check to see how many of the 7,377 stocks are either notes or warrants
# We use regex to print out a list of tuples containing first the list position of where the Note or list
# is contained and the second is the whether the word is notes or warrants in that position
# There are 557 entries which are either Notes or Warrants in our lists which need to be removed
# (422 warrants and 135 Notes)

regex1 = r'[Ww]arrant|[Nn]otes|[Dd]ebenture'
regex2 = r'\W'
removal_list1 = []
removal_list2 = []
upd_stock_list = []

for i in range(len(stock_name_list)):
    reg1 = re.findall(regex1, stock_name_list[i][1].strip())
    reg2 = re.findall(regex2, stock_name_list[i][0].strip())
    if reg1 != []:
        removal_list1.append((i, reg1))
    elif reg2 != [] and reg2 != ['/']:
        removal_list2.append((i, reg2))
    else:
        upd_stock_list.append(stock_name_list[i][0].strip())

print(removal_list1)
print(removal_list2)

print(len(stock_name_list)) # 7377
print(len(removal_list1)) # 581 (422 warrants, 135 notes and 24 debentures)
print(len(removal_list2)) # 432 (preferred stock)
print(len(upd_stock_list)) # 6364 (7377 - 581 - 432)

######################################################################################################################
            # Section 2.3 - Get required info from Alpha Vantage
######################################################################################################################

# We want to try and find the stock information on the 6,364 stocks.
# We need to ensure that we do not bring in any forward looking metrics including market cap and the number of full
# time employees

# Company Overview

API_key  = "OSPJN1YHMULW3OEO"


Overview_df = pd.DataFrame()
columns = ['Symbol', 'AssetType', 'Name', 'Exchange',  'Currency', 'Country', 'Sector', 'Industry']



for stock in upd_stock_list:
    time.sleep(1)
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'OVERVIEW',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {} or list(output.keys())[0] == 'Error Message':
        Temp_data_df = pd.DataFrame()
    else:
        Temp_data_df = pd.DataFrame(list(output.values())).transpose()
        Temp_data_df.columns = [list(output.keys())]
        Temp_data_df = Temp_data_df[columns]

    Overview_df = Overview_df.append(Temp_data_df, ignore_index=True)

print(Overview_df)


# Write out the CSV
Overview_df.to_csv(r'Files\Overview_df.csv', index=False, header=True)

stk_list = ['AMZN', 'TSLA']
print(stk_list)


# EPS
Temp_data = pd.DataFrame()
eps_data = pd.DataFrame()
for stock in upd_stock_list:
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'EARNINGS',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {} or list(output.keys())[0] == 'Error Message':
        Temp_data = pd.DataFrame()
    else:
        Temp_data = pd.DataFrame(output['quarterlyEarnings'])
        Temp_data['Symbol'] = output['symbol']

    eps_data = eps_data.append(Temp_data, ignore_index=True)
    eps_data = eps_data.loc[eps_data['fiscalDateEnding'] > '2014-11-30']

print(eps_data)

# Write out the CSV
eps_data.to_csv(r'Files\eps_data.csv', index=False, header=True)

upd_stock_list[699]

# Income Statement

Temp_data = pd.DataFrame()
inc_st_data = pd.DataFrame()

for stock in upd_stock_list:
    time.sleep(0.75)
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'INCOME_STATEMENT',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {}  or list(output.keys())[0] == 'Error Message' :
        Temp_data = pd.DataFrame()
    else:
        Temp_data = pd.DataFrame(output['quarterlyReports'])
        Temp_data['Symbol'] = output['symbol']

    inc_st_data = inc_st_data.append(Temp_data, ignore_index=True)

print(inc_st_data)



# Write out the CSV
inc_st_data.to_csv(r'Files\inc_st_data.csv', index=False, header=True)

# Balance Sheet

Temp_data = pd.DataFrame()
BS_data = pd.DataFrame()

for stock in upd_stock_list:
    time.sleep(0.75)
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'BALANCE_SHEET',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {}  or list(output.keys())[0] == 'Error Message':
        Temp_data = pd.DataFrame()
    else:
        Temp_data = pd.DataFrame(output['quarterlyReports'])
        Temp_data['Symbol'] = output['symbol']

    BS_data = BS_data.append(Temp_data, ignore_index=True)

print(BS_data)

# BS_data[['fiscalDateEnding' , 'Symbol']]


# Write out the CSV
BS_data.to_csv(r'Files\BS_data.csv', index=False, header=True)

# Cash flow

Temp_data = pd.DataFrame()
CF_data = pd.DataFrame()

for stock in upd_stock_list:
    time.sleep(0.75)
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'CASH_FLOW',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {} or list(output.keys())[0] == 'Error Message':
        Temp_data = pd.DataFrame()
    else:
        Temp_data = pd.DataFrame(output['quarterlyReports'])
        Temp_data['Symbol'] = output['symbol']

    CF_data = CF_data.append(Temp_data, ignore_index=True)

print(CF_data)

# Write out the CSV
CF_data.to_csv(r'Files\CF_data.csv', index=False, header=True)

print(Temp_data)

# Monthly stock prices

upd_stock_list1 = upd_stock_list[5780:]
print(upd_stock_list1)

Temp_data = pd.DataFrame()
monthly_prices = pd.DataFrame()

for stock in upd_stock_list1:
    time.sleep(0.75)
    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
              'outputsize' : 'full',
              'symbol': stock,
              'apikey': API_key}

    response = requests.get(base_url, params=params)

    output = response.json()
    if output == {} or list(output.keys())[0] == 'Error Message':
        Temp_data = pd.DataFrame()
    else:
        Temp_data = pd.DataFrame(output['Monthly Adjusted Time Series']).transpose().rename_axis('dt').reset_index()
        Temp_data['Symbol'] = stock

    monthly_prices = monthly_prices.append(Temp_data, ignore_index=True)
    monthly_prices = monthly_prices.loc[monthly_prices['dt'] > '2014-11-30']

print(monthly_prices)


# Write out the CSV
monthly_prices.to_csv(r'Files\monthly_prices.csv', index=False, header=True)

monthly_prices2 = monthly_prices
print(monthly_prices2)



upd_stock_list[699]

Temp_data = pd.DataFrame()
inc_st_data = pd.DataFrame()

base_url = 'https://www.alphavantage.co/query?'
params = {'function': 'CASH_FLOW',
          'symbol': 'CYAD',
          'apikey': API_key}

response = requests.get(base_url, params=params)

output = response.json()
if output == {} or list(output.keys())[0] == 'Error Message':
    Temp_data = pd.DataFrame()
else:
    Temp_data = pd.DataFrame(output['quarterlyReports'])
    Temp_data['Symbol'] = output['symbol']

print(Temp_data)

upd_stock_list[624]