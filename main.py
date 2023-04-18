import dash
from dash import html
import ccxt

app = dash.Dash(__name__)
server = app.server

bybit = ccxt.bybit()
markets = bybit.load_markets()

symbol_list = [symbol for symbol in markets.keys()]

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
