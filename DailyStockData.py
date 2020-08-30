from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import numpy as np

yf.pdr_override()

class DailyStockData:
    def getDaytoDayPercChange(self, ticker, start_date="2000-01-01"):
        try:
            tickerData = pdr.get_data_yahoo(ticker, start=start_date, end=currentDate)
            newData = []
            for count in range(1,tickerData.shape[0]):
                newData.append((tickerData.Close.iloc[count]-tickerData.Close.iloc[count-1])/tickerData.Close.iloc[count-1])
            return pd.DataFrame(newData, columns=[ticker])
        except:
            print('symbol not listed')

    def getDaytoDayDollarChange(self, ticker, start_date="2000-01-01"):
        try:
            tickerData = pdr.get_data_yahoo(ticker, start=start_date, end=currentDate)
            newData = []
            for count in range(1,tickerData.shape[0]):
                newData.append((tickerData.Close.iloc[count]-tickerData.Close.iloc[count-1])/tickerData.Close.iloc[count-1])
            return pd.DataFrame(newData, columns=[ticker])
        except:
            print('symbol not listed')

    def getDailyPrice(self, ticker, start_date="2000-01-01"):
        try:
            return pdr.get_data_yahoo(ticker, start="2000-01-01", end=currentDate)
        except:
            print('symbol not listed')
        