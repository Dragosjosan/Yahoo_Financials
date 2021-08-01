import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.offline as pyo

df = pd.read_json('Yahoo_Financials.json')

company_list = []
evaluation_marker_list = []
values_list = []
USERNAME_PASSWORD = ['Yahoofinance', '007']


def populate_company_list():
    for company in df:
        company_list.append(company)


def populate_value_list():
    for company in df:
        values_list.append(df[company]['Valuation Measures']['Trailing P/E'])


def populate_marker_list():
    for company in df:
        for marker in df[company]['Valuation Measures']:
            evaluation_marker_list.append(marker)
    print(evaluation_marker_list)


app = dash.Dash()
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
app.layout = html.Div([
    html.Div(
        dcc.Graph(
            id='T-PE',
            figure={
                'data': [
                    {'x': company_list, 'y': [df[company]['Valuation Measures']['Trailing P/E'] for company in df],
                     'type': 'bar'}
                ],
                'layout': {
                    'title': 'Trailing P/E'
                }
            }
        ),
    ),
    html.Div(
        dcc.Graph(
            id='F-PE',
            figure={
                'data': [
                    {'x': company_list, 'y': [df[company]['Valuation Measures']['Forward P/E'] for company in df],
                     'type': 'bar'}
                ],
                'layout': {
                    'title': 'Forward P/E'
                }
            }
        )
    ),
    html.Div(
        dcc.Graph(
            id='Op-Margin',
            figure={
                'data': [
                    {'x': company_list,
                     'y': [df[company]['Management Effectiveness']['Operating Margin'] for company in df],
                     'type': 'bar'}
                ],
                'layout': {
                    'title': 'Operating Margin'
                }
            }
        ),
    ),
    html.Div(
        dcc.Graph(
            id='return-equity',
            figure={
                'data': [
                    {'x': company_list,
                     'y': [df[company]['Income Statement']['Return on Equity'] for company in df], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Return on Equity'
                }
            }
        ),
    ),
    html.Div(
        dcc.Graph(
            id='EBITDA',
            figure={
                'data': [
                    {'x': company_list,
                     'y': [df[company]['Income Statement']['EBITDA'] for company in df], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'EBITDA'
                }
            }
        ),
    ),
    html.Div(
        dcc.Graph(
            id='operating_cash_flow',
            figure={
                'data': [
                    {'x': company_list,
                     'y': [df[company]['Cash Flow Statement']['Operating Cash Flow'] for company in df], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Operating Cash Flow'
                }
            }
        )
    ),
],
    style={'width': '60%', 'height': '50%', 'display': 'inline-block'})

if __name__ == '__main__':
    populate_company_list()
    populate_marker_list()
    populate_value_list()
    app.run_server()
