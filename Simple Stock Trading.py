import psycopg2
import pandas as pd
import datetime
import matplotlib.pyplot as plt

def connect_db():
    try:
        conn = psycopg2.connect(
            database="equity_db",
            host="",
            port=,
            user="",
            password="" #hidden for safety
        )
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print(f"Database connection error: {e}")
        return None, None

def close_db_connection(conn, cursor):
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close() # may upload excel instead of using database

# Calculate Exponential Moving Average (EMA)
def EMA(series, n):
    ema = [series[0]]
    for i in range(1, len(series)):
        ema.append(2/(n+1) * series[i] + (1 - 2/(n+1)) * ema[i-1])
    return ema

# Note: Alternatively, you can use the pandas `ewm` function to calculate EMA:
# series.ewm(span=n, adjust=False).mean()

# Extracting data
def stock_data(cursor, stock, start_date):
    try:
        cursor.execute('''
                    SELECT security_symbol, open_price, close_price, high_price, low_price, date_key_int, volume
                    FROM us_equity_daily_finn
                    WHERE security_symbol=%s AND date_key_int > %s;
                    ''', (stock, start_date))
        
        data = cursor.fetchall()
        if not data:
            raise ValueError("No data returned from the query.")
        
        df = pd.DataFrame(data, columns=['stock', 'Open', 'Close', 'High', 'Low', 'date_key_int', 'Volume'])
        df['date_key_int'] = pd.to_datetime(df['date_key_int'], format='%Y%m%d')
        df = df.set_index("date_key_int")
        df.index.name = 'Date'

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Strategy model
def full_model(cursor, stock, start_date):
    df = stock_data(cursor, stock, start_date)
    if df is None:
        return None
    
    df['MA5'] = EMA(df['Close'], 5)
    df['MA20'] = EMA(df['Close'], 20)

    hold_signals = []
    cash_income = []
    holding_stock = 0

    # Strategy logic
    for i in range(1, df.shape[0]):
        if (df['MA20'][i] < df['MA5'][i]) and (df['MA20'][i-1] >= df['MA5'][i-1]):
            hold_signals.append('Buy')
            holding_stock = 1
        elif (df['MA20'][i] < df['MA5'][i]) and (df['MA20'][i-1] < df['MA5'][i-1]):
            hold_signals.append('Hold')
        elif (df['MA20'][i] >= df['MA5'][i]) and (df['MA20'][i-1] >= df['MA5'][i-1]):
            hold_signals.append('Hold')
        elif (df['MA20'][i] >= df['MA5'][i]) and (df['MA20'][i-1] < df['MA5'][i-1]):
            if holding_stock == 1:
                hold_signals.append('Sell')
                holding_stock = 0
            else:
                hold_signals.append('Lucky I didn’t buy')
        else:
            print('Calculation error')
            hold_signals.append('Error')

    df['hold_signals'] = ['Hold'] + hold_signals

    # Cash income so far
    buying_prices = []
    selling_prices = []

    for k in range(df.shape[0]):
        if df['hold_signals'][k] == 'Buy':
            buying_prices.append(df['Close'][k])
            if not cash_income:
                cash_income.append(-buying_prices[-1])
            else:
                cash_income.append(cash_income[-1] - buying_prices[-1])
        elif df['hold_signals'][k] == 'Sell':
            if buying_prices:
                selling_prices.append(df['Close'][k])
                cash_income.append(cash_income[-1] + selling_prices[-1])
            else:
                cash_income.append(cash_income[-1])
        else:
            if k == 0:
                cash_income.append(0)
            else:
                cash_income.append(cash_income[-1])

    df['cash_income'] = cash_income

    # Stock price change since purchase
    current_revenue = []

    for a in range(df.shape[0]):
        if buying_prices:
            current_revenue.append(df['Close'][a] - buying_prices[-1])
        else:
            current_revenue.append(0)

    df['current_revenue'] = current_revenue

    return df

# Example call
if __name__ == "__main__":
    conn, cursor = connect_db()
    if conn is not None and cursor is not None:
        stock = "AAPL"
        start_date = "20200101"
        df_result = full_model(cursor, stock, start_date)
        if df_result is not None:
            print(df_result.head())
        close_db_connection(conn, cursor)


