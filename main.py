import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Load data
# df = pd.read_csv(
#     'https://raw.githubusercontent.com/plotly/datasets/master/iris.csv')
FOD_list = ["BTCUSDT","BTCUSDT","BTCUSDT","BTCUSDT"]
FOB_list = ["BTCUSDT","BTCUSDT","BTCUSDT","BTCUSDT"]
# Create app
app = dash.Dash(__name__)
server=app.server
# Define layout
app.layout = html.Div(
    [
        html.H1('My Lists'),
        html.Div(
            [
                html.H4('15m FOB LIST'),
                html.Ul(
                    [html.Li(symbol) for symbol in FOB_list]
                )
            ],
            style={'margin-bottom': '10px'}
        ),
        html.Div(
            [
                html.H4('15m FOD LIST'),
                html.Ul(
                    [html.Li(symbol) for symbol in FOD_list]
                )
            ]
        )
    ]
)

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
