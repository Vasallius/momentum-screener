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

app = dash.Dash(__name__)
server = app.server

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]

interval = "5m"
limit = 100

max_threads = 10
data_list = []

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(fetch_data, symbol) for symbol in symbol_list]

    for future in as_completed(futures):
        symbol_df = future.result()
        data_list.append(symbol_df)

def fetch_data(symbol):
    print(f"Processing {symbol}")
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

ticker_data = {}
for symbol in symbol_list[:30]:
    print(symbol)
    ticker = bybit.fetch_ticker(symbol)
    last_price = ticker['last']
    ticker_data[symbol] = last_price

app.layout = html.Div([
    html.H1('Bybit Tickers'),
    html.Table([
        html.Thead([
            html.Tr([
                html.Th('Symbol'),
                html.Th('Last Price')
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(symbol),
                html.Td(f"{last_price:.2f}")
            ]) for symbol, last_price in ticker_data.items()
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
