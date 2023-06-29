import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
# import  dash_bootstrap_templates as dbt

dash.register_page(__name__)


# Login screen
# layout = html.Div(
#     [
#         html.H2("Please log in to continue:", id="h1"),
#         dcc.Input(placeholder="Enter your username", type="text", id="uname-box"),
#         dcc.Input(placeholder="Enter your password", type="password", id="pwd-box"),
#         html.Button(children="Login", n_clicks=0, type="submit", id="login-button"),
#         html.Div(children="", id="output-state"),
#         html.Br(),
#         dcc.Link("Home", href="/"),
#     ]
# )

layout = html.Div(
    children=[
        html.Br(),
        html.H2('Введіть логін та пароль, щоб продовжити', style={'font-weight': 'bold', 'font-size': 32, 'text-align': 'center'}),
        html.Br(),
        html.Div(id='login-block', className='dark-theme-control',
                 children=[
                     dbc.Row(
                         children=[
                             dbc.Label("Username", html_for="username-row", width={"size": 1, "offset": 4}),
                             dbc.Col(dbc.Input(placeholder="Enter your username", type="text", id="uname-box"), width={"size": 2, "offset": 0}),
                         ], className="mb-3"),
                     dbc.Row(
                         children=[
                             dbc.Label("Password", html_for="password-row", width={"size": 1, "offset": 4}),
                             dbc.Col(dbc.Input(placeholder="Enter your password", type="password", id="pwd-box"), width={"size": 2, "offset": 0}),
                        ], className="mb-3"),

                     dbc.Row(
                         dbc.Col(children=[
                         html.Button(children="Login", n_clicks=0, type="submit", id="login-button"),
                         html.Div(id="output-state"),
                         html.Br()
                         ], width={"size": 2, "offset": 5}), className="mb-3"
                     ),
                     # dbc.Row(children=[dcc.Link("Home", href="/"),])
                   ]),
        ])