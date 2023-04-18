import dash
from dash import html
import ccxt
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import ccxt
import dash
from dash import html   
import os

external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

app = dash.Dash(
    __name__,
    external_scripts=external_script,
)
app.scripts.config.serve_locally = True
server = app.server

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]

interval = "4h"
limit = 100

max_threads = 10
data_list = []

def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):
    delta = ohlc["close"].diff()

    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1/period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1/period).mean()

    rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

    return np.round(rsi, 2) if round_rsi else rsi

def fetch_data(symbol):
    # print(f"Processing {symbol}")
    ohlcv = bybit.fetch_ohlcv(symbol, interval, limit)
    headers = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(ohlcv, columns=headers)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp")

    df["EMA4"] = df["close"].ewm(span=4).mean()
    df["MA8"] = df["close"].rolling(8).mean()
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()

    df["RSI14"] = rsi_tradingview(df)

    df = df.tail(2)

    df.index = pd.MultiIndex.from_product([[symbol], df.index], names=["symbol", "timestamp"])

    return df

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(fetch_data, symbol) for symbol in symbol_list]

    for future in as_completed(futures):
        symbol_df = future.result()
        data_list.append(symbol_df)

data_df = pd.concat(data_list, axis=0)
# data_df.to_excel("crypto_data.xlsx")


FOD_list = []
FOB_list = []
for symbol in symbol_list:
    try:
        rows = data_df.loc[f'{symbol}:USDT']
        prev = rows.iloc[-2]
        cur = rows.iloc[-1]
        close = rows.iloc[-1].close
        prevema4 = prev.EMA4
        curema4 = cur.EMA4
        prevma8 = prev.MA8
        curma8 = cur.MA8
        prevma20 = prev.MA20
        curma20 = cur.MA20
        prevma50 = prev.MA50
        curma50 = cur.MA50
        rsi14 = cur.RSI14

        ema4x8cross = prevema4 < prevma8 and curema4 > curma8 
        reversecross = prevema4 > prevma8 and curema4 < curma8 
        strongtrend = curma8 > curma20 > curma50 
        retracetrend = curma20 > curma8 > curma50
        if ema4x8cross:
            if strongtrend and rsi14>=60:
                FOD_list.append(symbol)
            elif retracetrend and rsi14>=50:
                FOB_list.append(symbol)
    except:
        print(f"Error {symbol} not found")

print(FOB_list)
print(FOD_list)
app.layout = html.Div(
    [
        html.H1('My Lists'),
        html.Div(
            [
                html.H4(f'{interval} FOB LIST',className="bg-green-300 text-4xl"),
                html.Ul(
                    [html.Li(symbol) for symbol in FOB_list]
                )
            ],
            style={'margin-bottom': '10px'}
        ),
        html.Div(
            [
                html.H4(f'{interval} FOD LIST'),
                html.Ul(
                    [html.Li(symbol) for symbol in FOD_list]
                )
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
