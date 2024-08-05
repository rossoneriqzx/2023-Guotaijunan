#!/usr/bin/env python3

import psycopg2
import pandas as pd
import mplfinance as mpf
import datetime
import matplotlib.pyplot as plt

    
conn = psycopg2.connect(
database = "equity_db",
host = "edw.cy1s98bz8vio.ca-central-1.rds.amazonaws.com",
port = 5555,
user = "wealthsigma_etl",
password = "algofamily")
cursor = conn.cursor()

#计算个股MA
def EMA(series, n):
    ema = [series[0]]
    for i in range(1, len(series)):
        ema.append(2/(n+1) * series[i] + (1 - 2/(n+1)) * ema[i-1])
    return ema

#提取数据
def stock_data(stock, start_date):
    cursor.execute(f'''
                SELECT security_symbol, open_price, close_price, high_price, low_price, date_key_int, volume
                FROM us_equity_daily_finn
                WHERE security_symbol='{stock}'
                AND date_key_int > {start_date};
                ''')
    df = pd.DataFrame(cursor.fetchall(), columns=['stock', 'Open', 'Close', 'High', 'Low', 'date_key_int', 'Volume'])

    df['date_key_int']=pd.to_datetime(df['date_key_int'],format='%Y%m%d')
    df = df.set_index("date_key_int")
    df.index.name = 'Date'

    return df

#策略模型
def full_model(stock, start_date):
    df = stock_data(stock, start_date)
    df['MA5'] = EMA(df['Close'],5)
    df['MA20'] = EMA(df['Close'],20)
    #df['MA100'] = EMA(df['Close'],100)

    hold = []
    cash_income = []
    have = 0
    
#策略逻辑
    for i in range(df.iloc[:,0].size):

                    
        if (df['MA20'][i] < df['MA5'][i]) and (df['MA20'][i-1] >= df['MA5'][i-1]):
            hold.append('买入')
            have = 1
            
        elif (df['MA20'][i] < df['MA5'][i]) and (df['MA20'][i-1] < df['MA5'][i-1]):
            hold.append('待定，不操作')
            
        elif (df['MA20'][i] >= df['MA5'][i]) and (df['MA20'][i-1] >= df['MA5'][i-1]):
            hold.append('待定，不操作')
            
        elif (df['MA20'][i] >= df['MA5'][i]) and (df['MA20'][i-1] < df['MA5'][i-1]):
            if have == 1:
                hold.append('卖出')
                have = 0
            else:
                hold.append('还好没买')
        
        else:
            print('算不出来')
            
    df['hold'] = hold

#目前为止的现金收入
    buying_price = []
    selling_price = []

    
    for k in range(df.iloc[:,0].size):
        if hold[k] == '买入':
            buying_price.append(df['Close'][k])
            if cash_income == []:
                cash_income.append(-buying_price[-1])
            else:
                cash_income.append(cash_income[-1] - buying_price[-1])
            
        elif hold[k] == '卖出':
            selling_price.append(df['Close'])
            cash_income.append(cash_income[-1] + selling_price[-1])
        else:
            if k == 0:
                cash_income.append(0)
            else:
                cash_income.append(cash_income[-1])
    df['cash_income'] = cash_income

    
#从购入起个股的价格变化
    current_revenue = []

    for a in range(df.iloc[:,0].size):
        if buying_price == []:
            current_revenue.append(0)
        else:
            current_revenue.append(df['Close'][a] - buying_price[-1])
            
    df['current_revenue'] = current_revenue
    
    return df


