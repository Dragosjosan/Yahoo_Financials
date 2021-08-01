import yfinance as yf
import os
import numpy as np
from pandas_datareader import data
import pandas as pd
import pandas_datareader as web

df_info = pd.DataFrame(yf.Ticker("FB").info)
df_financials = pd.DataFrame(yf.Ticker("FB").financials)
df_info.to_excel('YF_Info.xlsx',sheet_name='Yfiance')
df_financials.to_excel('YF_Financials.xlsx',sheet_name='Yfiance')

# market_data=[]
# for ticker in tickers:
#     print(ticker)
#     try:
#        market_data.append(web.get_quote_yahoo(ticker))
#     except:
#        print('Error with: ', ticker)
# df=pd.concat(market_data, axis=0)
