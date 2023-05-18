import dash
from dash import html, Input, Output, State, dcc
import ccxt
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

external_script = ["https://tailwindcss.com/",
                   {"src": "https://cdn.tailwindcss.com"}]
external_stylesheets = ['/assets/custom.css']

app = dash.Dash(__name__, external_scripts=external_script,
                external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
server = app.server

# debug_messages = []
start = True
scan_status = ""

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]


limit = 100

max_threads = 10

# TODO: consolidate into one callback


@app.callback(Output("FOB-container", "children"),
              Input("pair_list", "data"), prevent_initial_call=True)
def update_FOB(data):
    data = json.loads(data)
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in data["FOB_list"]]


@app.callback(Output("FOD-container", "children"),
              Input("pair_list", "data"), prevent_initial_call=True)
def update_FOD(data):
    data = json.loads(data)
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in data["FOD_list"]]


@app.callback(Output("rFOD-container", "children"),
              Input("pair_list", "data"), prevent_initial_call=True)
def update_rFOD(data):
    data = json.loads(data)
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in data["rFOD_list"]]


@app.callback(Output("rFOB-container", "children"),
              Input("pair_list", "data"), prevent_initial_call=True)
def update_rFOB(data):
    data = json.loads(data)
    return [html.Button(button, className="bg-[#0083FF] inter font-bold text-white py-2 px-4 rounded-md mr-2 w-36") for button in data["rFOB_list"]]


def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):
    delta = ohlc["close"].diff()

    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1/period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1/period).mean()

    rsi = np.where(up == 0, 0, np.where(
        down == 0, 100, 100 - (100 / (1 + up / down))))

    return np.round(rsi, 2) if round_rsi else rsi


def fetch_data(symbol, interval):
    # global debug_messages
    # debug_messages.append(f"Processing {symbol}")
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
    df.index = pd.MultiIndex.from_product(
        [[symbol], df.index], names=["symbol", "timestamp"])

    return df


def screen(symbol_list, df):
    FOD_list_local = []
    FOB_list_local = []
    rFOD_list_local = []
    rFOB_list_local = []
    for symbol in symbol_list:
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
            strongdowntrend = curma50 > curma20 > curma8
            retracedowntrend = curma50 > curma8 > curma20
            if ema4x8cross:
                if strongtrend and rsi14 >= 60:
                    FOD_list_local.append(symbol)
                elif retracetrend and rsi14 >= 50:
                    FOB_list_local.append(symbol)
            if reversecross:
                if strongdowntrend and rsi14 <= 40:
                    rFOD_list_local.append(symbol)
                elif retracedowntrend and rsi14 <= 50:
                    rFOB_list_local.append(symbol)
        except:
            pass

    print(
        f"LISTS: \n FOB: {FOB_list_local} \nFOD: {FOD_list_local} \nrFOB: {rFOB_list_local} \nrFOD: {rFOD_list_local}")
    print("Screen complete.")
    return {
        "FOB_list": FOB_list_local,
        "FOD_list": FOD_list_local,
        "rFOD_list": rFOD_list_local,
        "rFOB_list": rFOB_list_local
    }


@app.callback(Output('btn-m5', 'className'),
              Output('btn-m15', 'className'),
              Output('btn-1h', 'className'),
              Output('btn-4h', 'className'),
              Output('btn-1d', 'className'),
              Input('btn-m5', 'n_clicks'),
              Input('btn-m15', 'n_clicks'),
              Input('btn-1h', 'n_clicks'),
              Input('btn-4h', 'n_clicks'),
              Input('btn-1d', 'n_clicks'),
              prevent_initial_call=True)
def update_button_style(btn_m5, btn_m15, btn_1h, btn_4h, btn_1d):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_style = "bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"
    reset_style = "bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"
    if button_id == 'btn-m5':
        return button_style, reset_style, reset_style, reset_style, reset_style
    elif button_id == 'btn-m15':
        return reset_style, button_style, reset_style, reset_style, reset_style
    elif button_id == 'btn-1h':
        return reset_style, reset_style, button_style, reset_style, reset_style
    elif button_id == 'btn-4h':
        return reset_style, reset_style, reset_style, button_style, reset_style
    elif button_id == 'btn-1d':
        return reset_style, reset_style, reset_style, reset_style, button_style


# Storing the FOD, FOB, rFOD, rFOB lists in store.
@app.callback(Output("dummy-state", "children"),
              Output("dummy-state2", "children"),
              Output("pair_list", "data"),
              Input("btn-refresh", "n_clicks"),
              State("btn-m5", "className"),
              State("btn-m15", "className"),
              State("btn-1h", "className"),
              State("btn-4h", "className"),
              State("btn-1d", "className"),
              prevent_initial_call=True,
              )
def refresh(n_clicks, btn_m5_class, btn_m15_class, btn_1h_class, btn_4h_class, btn_1d_class):
    # get the value of the selected time interval
    # global interval, FOB_list, FOD_list, data_list, scan_status
    scan_status = "Scan Ongoing"
    # print("Set scan status to scan ongoing")
    data_list = []

    # set the interval to active button
    active_class = "bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"
    if active_class in btn_m5_class:
        interval = "5m"
    elif active_class in btn_m15_class:
        interval = "15m"
    elif active_class in btn_1h_class:
        interval = "1h"
    elif active_class in btn_4h_class:
        interval = "4h"
    elif active_class in btn_1d_class:
        interval = "1d"
    else:
        interval = "1h"
        return interval, "No interval select, defaulting to 1h"

    print(f"interval to run threads: {interval}")

    # Run multi-threaded function to get data
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(fetch_data, symbol, interval)
                   for symbol in symbol_list]

        for future in as_completed(futures):
            symbol_df = future.result()
            data_list.append(symbol_df)

    data_df = pd.concat(data_list, axis=0)

    # Run screen function to filter cryptocurrency pairs
    result = screen(symbol_list, data_df)
    result = json.dumps(result)
    scan_status = "Scan Complete"
    print(scan_status)

    return interval, f"Finished scanning for {interval}", result


# @app.callback(Output("debug-output", "children"),
#               Input("interval-update", "n_intervals"))
# def update_debug_output(n):
#     global debug_messages
#     # Convert the list of debug messages into a list of html.P elements
#     debug_output = [html.P(message) for message in debug_messages]
#     debug_messages.clear() # Clear debug messages after displaying
#     return debug_output

@app.callback(Output("scan-status", "children"),
              Input("interval-update-scan-status", "n_intervals"))
def update_scan_status(n):
    # print("Updating Scan Status.")
    global scan_status
    # print(f"Scan status = {scan_status}")
    return scan_status


app.layout = html.Div(
    [
        html.Div([
            # header
            html.Div([

                html.Div([
                    html.Div([
                        html.H1(
                            'Kreios', className="text-[#0083FF] dmsans text-7xl font-bold mr-2"),
                        html.Span(
                            'Screener', className="text-white dmsans text-7xl font-bold mr-2"),
                    ], className="flex items-center justify-center "),


                    html.Div([
                        html.Img(src=app.get_asset_url('bybitlogo.png'),
                                 alt='BYBIT', className='ml-auto'),
                    ], className='flex '),


                    html.Div([
                        html.P(
                            'Disclaimer: These are NOT signals and data is from Bybit.', className="text-center"),
                        html.P('Please check accordingly.',
                               className="text-center"),
                    ], className="text-white text-xl "),


                ], className="flex flex-col "),


                # v1.0
                html.Div([
                    html.Span(
                        'v1.1', className="text-white inter font-normal bg-[#0083FF]"),
                ], className="flex items-start"),
            ], className="flex flex-row mx-auto mt-32 mb-9"),

            # buttons
            html.Div([
                html.Button(
                    'M5', id="btn-m5", className="bg-[#0083FF] inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button(
                    'M15', id="btn-m15", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button(
                    '1H', id="btn-1h", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button(
                    '4H', id="btn-4h", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button(
                    '1D', id="btn-1d", className="bg-white inter font-bold tracking-wider text-black py-2 px-4 rounded-md mr-2"),
                html.Button('REFRESH', id="btn-refresh",
                            className="bg-[#FF0000] inter font-bold tracking-wider text-white py-2 px-6 rounded-md"),

            ], className="flex flex-row mx-auto mb-6"),
            html.Div(id="scan-status",
                     className="text-white font-bold dmsans text-xl mx-auto"),
            dcc.Interval(id="interval-update-scan-status",
                         interval=1 * 1000, n_intervals=0),  # 1 second interval
            # FOB and FOD
            html.Div([
                html.Div(
                    "FOB", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="FOB-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
                html.Div(
                    "FOD", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="FOD-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
                html.Div(
                    "R-FOD", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="rFOD-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
                html.Div(
                    "R-FOB", className="text-white font-bold dmsans text-4xl mx-auto"),
                html.Div(
                    id="rFOB-container",
                    className="grid grid-cols-5 gap-4 mt-4"
                ),
            ], className="flex flex-col items-center"),
            html.Div(id="dummy-state"),
            html.Div(id="dummy-state2", className="text-white"),
            dcc.Store(id='pair_list'),
            html.Div(id="dummy-state3", className="text-white"),

            # html.Div(id="debug-output",className="text-white"),
        ], className="flex flex-col", id="heading"),

        html.Div(id="output", className="text-white"),
        dcc.Interval(id="interval-update", interval=2 * 1000,
                     n_intervals=0),  # 1 second interval
        # 1 second interval


    ],
    className="min-h-screen flex flex-col",
    style={'background-color': '#1E1E1E'}
)

if __name__ == '__main__':
    app.run_server(debug=False)
