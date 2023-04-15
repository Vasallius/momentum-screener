import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/iris.csv')

# Create app
app = dash.Dash(__name__)
server=app.server
# Define layout
app.layout = html.Div(children=[
    html.H1(children='Iris Dataset'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': df.SepalLength, 'y': df.SepalWidth,
                    'type': 'scatter', 'mode': 'markers'}
            ],
            'layout': {
                'title': 'Sepal Length vs Sepal Width'
            }
        }
    )
])

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
