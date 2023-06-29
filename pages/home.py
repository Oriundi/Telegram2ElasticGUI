import dash
from dash import html, dcc, Output, Input, State, callback
# from dash import dash_table as ddt
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import date

from models.home import get_chats, get_users, get_messages

import pandas as pd

dash.register_page(__name__)


def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    chats = get_chats()
    users = get_users()

    df = get_messages(date_from=date.today().strftime('%Y-%m-%d'))
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('Europe/Kiev').dt.strftime('%Y-%m-%d\n%H:%M:%S')
    df.sort_values(by=['timestamp'], ascending=[False], inplace=True)
    table_header = html.Tr([html.Th(column) for column in df.columns])
    table_header = [html.Thead(children=table_header)]

    table_body = list()
    for ii in df.index:
        tr = list()
        for jj in df.columns:
            tr.append(html.Td(df.loc[ii, jj]))
        table_body.append(html.Tr(tr))
    # table_body = df.applymap(lambda x: html.Tr(html.Td(x))).values.tolist()
    table_body = [html.Tbody(id='message-data-body', children=table_body)]

    table = dbc.Table(
        id='message-data',
        children=table_header + table_body,
        bordered=True)

    layout = html.Div(
        id='select-menu',
        children=[
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            html.Div(
                                children=[
                                    dbc.Button('Пошук', id='search-button',
                                               color="primary", size="lg", outline=True, className="me-1"
                                               )],
                                style={'margin-top': '5rem'},
                                className="d-grid gap-2 d-md-flex justify-content-md-center")
                        ], width={"size": 3, "offset": 0}),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                children=[
                                    dbc.CardHeader("Слова для пошуку"),
                                    dbc.CardBody(
                                        children=[
                                            dbc.Input(id='search-words', placeholder="Введіть слова для пошуку", type="text")
                                        ]
                                    ),
                                    dbc.CardFooter(
                                        children=[dbc.RadioItems(id="bool-condition",
                                                                 options=[{"label": 'І', "value": 'AND'},
                                                                          {"label": 'АБО', "value": 'OR'}],
                                                                 inline=True,
                                                                 value='OR'
                                                                 )]
                                    )
                                ],
                            )
                        ], width={"size": 6, "offset": 0})
                ]),
            html.Br(),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            dbc.Card(
                                children=[
                                    dbc.CardHeader("Оберіть чат"),
                                    dbc.CardBody(
                                        children=[
                                            dcc.Dropdown(
                                                id='select-chats',
                                                options=chats,
                                                multi=True,
                                                searchable=True
                                            )
                                        ]
                                    )
                                ],
                            ),
                            dbc.Card(
                                children=[
                                    dbc.CardHeader("Оберіть користувача"),
                                    dbc.CardBody(
                                        children=[
                                            dcc.Dropdown(
                                                id='select-users',
                                                options=users,
                                                multi=True,
                                                searchable=True
                                            )
                                        ]
                                    )
                                ],
                            ),
                            dbc.Card(
                                children=[
                                    dbc.CardHeader("Оберіть початкову дату"),
                                    dbc.CardBody(
                                        children=[
                                            dcc.DatePickerSingle(
                                                id='select-start-date',
                                                min_date_allowed=date(2020, 1, 1),
                                                max_date_allowed=date.today(),
                                                initial_visible_month=date.today(),
                                                date=date.today()
                                            ),
                                        ]
                                    )
                                ],
                            )],
                        width={"size": 3, "offset": 0},
                        className='md3'
                    ),
                    dbc.Col(
                        children=[table],
                        width={"size": 8, "offset": 0},
                        className='md6')
                ])
        ])

    return html.Div(
        [
            layout
        ]
    )


@callback(Output("message-data", "children"),
          [Input("search-button", "n_clicks")],
          [State('bool-condition', 'value'),
           State('search-words', 'value'),
           State('select-chats', 'value'),
           State('select-users', 'value'),
           State('select-start-date', 'date')],
          config_prevent_initial_callbacks=True)
def make_search(n_clicks, condition, words, chats, users, start_date):
    df = get_messages(date_from=start_date, condition=condition, search_words=words, username=users, chat=chats, limit=0)
    table_header = html.Tr([html.Th(column) for column in df.columns])
    table_header = [html.Thead(children=table_header)]

    if df.empty:
        return table_header
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('Europe/Kiev').dt.strftime('%Y-%m-%d\n%H:%M:%S')
        df.sort_values(by=['timestamp'], ascending=[False], inplace=True)

        table_body = list()
        for ii in df.index:
            tr = list()
            for jj in df.columns:
                tr.append(html.Td(df.loc[ii, jj]))
            table_body.append(html.Tr(tr))

        table_body = [html.Tbody(id='message-data-body', children=table_body)]
        return table_header + table_body
