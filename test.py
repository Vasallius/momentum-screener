import dash
from dash import html, callback, Input, Output, State
import ccxt
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed



external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]
external_stylesheets = ['/assets/custom.css']

app = dash.Dash(__name__, external_scripts=external_script, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
server = app.server


FOB_list = ['TROY/USDT', 'Button 2', 'Button 3', 'Button 4','Button 1', 'Button 2', 'Button 3', 'Button 4','Button 1', 'Button 2', 'Button 3', 'Button 4']
FOD_list = ['Button 5', 'Button 6', 'Button 1', 'Button 2', 'Button 3', 'Button 4','Button 1', 'Button 2', 'Button 3', 'Button 4']

start = True
interval = "5m"

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]


limit = 100

max_threads = 10
data_list = []

@app.callback(Output("FOB-container", "children"),
              Input("dummy-state", "children"))
def update_FOB(n_clicks):
    global FOB_list
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in FOB_list]

@app.callback(Output("FOD-container", "children"),
              Input("dummy-state", "children"))
def update_FOD(n_clicks):
    global FOD_list
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in FOD_list]

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

def fetch_data(symbol, interval):
    print(f"Processing {symbol}")
    print(interval)
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

    # df = df.tail(2)
    last_five_rows = df.tail(20)
    df = last_five_rows.head(2)
    df.index = pd.MultiIndex.from_product([[symbol], df.index], names=["symbol", "timestamp"])

    return df



def screen(symbol_list,df):
    global FOD_list, FOB_list
    FOD_list = []
    FOB_list = []
    print(f"LISTS: {FOB_list}, {FOD_list}")
    for symbol in symbol_list:
        print(f"Testing {symbol} for setups.")
        try:
            rows = df.loc[f'{symbol}:USDT']
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
            pass
    print(f"LISTS: {FOB_list}, {FOD_list}")
    print("Screen complete.")

@app.callback(
    Output("btn-m5", "className"),
    Output("btn-m15", "className"),
    Output("btn-1h", "className"),
    Output("btn-4h", "className"),
    Output("btn-1d", "className"),
    Input("btn-m5", "n_clicks"),
    Input("btn-m15", "n_clicks"),
    Input("btn-1h", "n_clicks"),
    Input("btn-4h", "n_clicks"),
    Input("btn-1d", "n_clicks"),
)
def toggle_active_state(btn_m5_clicks, btn_m15_clicks, btn_1h_clicks, btn_4h_clicks, btn_1d_clicks):
    global start
    button_states = [False, False, False, False, False]
    
    if start:
        button_states[0] = True
        start = False
    else:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "btn-m5":
            button_states[0] = True
        elif button_id == "btn-m15":
            button_states[1] = True
        elif button_id == "btn-1h":
            button_states[2] = True
        elif button_id == "btn-4h":
            button_states[3] = True
        elif button_id == "btn-1d":
            button_states[4] = True
            
    return ["bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2 active" if state else "bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2" for state in button_states]

@app.callback(Output("dummy-state", "children"),
              Input("btn-refresh", "n_clicks"),
              State("btn-m5", "className"),
              State("btn-m15", "className"),
              State("btn-1h", "className"),
              State("btn-4h", "className"),
              State("btn-1d", "className"))
def refresh(n_clicks, btn_m5_class, btn_m15_class, btn_1h_class, btn_4h_class, btn_1d_class):
    # get the value of the selected time interval
    global interval, FOB_list, FOD_list, data_list

    data_list = []

    
    # set the interval to active button
    active_class = "bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"
    if active_class in btn_m5_class:
        interval = "5m"
        FOB_list =["KIDDKOSA", "CHAW CHAW"]

    elif active_class in btn_m15_class:
        interval = "15m"
        FOB_list =["KIDDKOSA", "CHAW CHAW"]

    elif active_class in btn_1h_class:
        interval = "1h"
        FOB_list =["KIDDKOSA", "CHAW CHAW"]

    elif active_class in btn_4h_class:
        interval = "4h"
        FOB_list =["KIDDKOSA", "CHAW CHAW", "JINN"]

    elif active_class in btn_1d_class:
        interval = "1d"
    else:
        interval = "test"

    # Run multi-thread
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(fetch_data, symbol, interval) for symbol in symbol_list]

        for future in as_completed(futures):
            symbol_df = future.result()
            data_list.append(symbol_df)

    data_df = pd.concat(data_list, axis=0)

    # Run out setup screen
    screen(symbol_list,data_df)
    return interval
app.layout = html.Div(
    [
        html.Div([
            # header
            html.Div([
    
                html.Div([
                    html.Div([
                        html.H1('Kreios', className="text-[#0083FF] dmsans text-7xl font-bold mr-2"),
                        html.Span('Screener', className="text-white dmsans text-7xl font-bold mr-2"),
                    ], className="flex items-center justify-center "),


                    html.Div([
                        html.Img(src=app.get_asset_url('bybitlogo.png'), alt='BYBIT', className='ml-auto'),
                    ], className='flex '),


                    html.Div([
                        html.P('Disclaimer: These are NOT signals and data is from Bybit.', className="text-center"),
                        html.P('Please check accordingly.', className="text-center"),
                    ], className="text-white text-xl "),


                    ],className="flex flex-col "),
                    

                # v1.0
                html.Div([
                    html.Span('v1.0', className="text-white inter font-normal bg-[#0083FF]"),
                ], className="flex items-start"), 
            ], className="flex flex-row mx-auto mt-32 mb-9"),
                
            # buttons
            html.Div([
                html.Button('M5', id="btn-m5", className="bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('M15', id="btn-m15", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('1H', id="btn-1h", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('4H', id="btn-4h", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('1D', id="btn-1d", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('REFRESH', id="btn-refresh", className="bg-[#FF0000] inter font-bold tracking-wider text-white py-2 px-6 rounded-md"),

            ], className="flex flex-row mx-auto mb-6"),

             # FOB and FOD
            html.Div([
                html.Div("FOB", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="FOB-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
                html.Div("FOD", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="FOD-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
            ], className="flex flex-col items-center"),
        ], className="flex flex-col", id="heading"),

        html.Div(id="output",className="text-white"),
        html.Div(id="dummy-state", style={"display": "none"}),

    ],
    className="min-h-screen flex flex-col",
    style={'background-color': '#1E1E1E'}
)

if __name__ == '__main__':
    app.run_server(debug=True) 
