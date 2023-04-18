import dash
from dash import html
import ccxt

app = dash.Dash(__name__)

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]

app.layout = html.Div([
    html.H1('Bybit Tickers'),
    html.Ul([html.Li(symbol) for symbol in symbol_list])
])

if __name__ == '__main__':
    app.run_server(debug=True)