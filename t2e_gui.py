from flask import Flask, redirect, url_for
from flask_login import login_user, LoginManager, UserMixin, current_user
import yaml

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
# import  dash_bootstrap_templates as dbt
# from pages.login import layout as login_layout

from logger import log


# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)
app = dash.Dash(
    __name__, server=server, use_pages=True, suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.ZEPHYR]
)


# Load config
with open('config/config.yaml', "r") as config_file:
    log.info('Reading config')
    config = yaml.safe_load(config_file)

# Keep this out of source code repository - save in a file or a database
#  passwords should be encrypted
VALID_USERNAME_PASSWORD = config['users']


# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
# server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
server.config.update(SECRET_KEY=config['FLASK_SECRET_KEY'])

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="user-status-header", style={'text-align': 'right', 'font-weight': 'bold', 'margin-right': '1em'}),
        html.Hr(),
        dash.page_container,
        # login_layout
    ]
)


@app.callback(
    Output("user-status-header", "children"),
    Input("url", "pathname"),
)
def update_authentication_status(_):
    if current_user.is_authenticated:
        return dcc.Link("logout", href="/logout")
    return dcc.Link("login", href="/login")


@app.callback(
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def login_button_click(n_clicks, username, password):
    log.info(f'user {username} login/logout')
    if n_clicks > 0:
        if VALID_USERNAME_PASSWORD.get(username) is None:
            # return dcc.Location(pathname="/login", id="someid_doesnt_matter")
            return "Невірний логін або пароль"
        if VALID_USERNAME_PASSWORD.get(username) == password:
            login_user(User(username))
            return dcc.Location(pathname="/", id="home-id")
            # return "Login Successful"
        # return dcc.Location(pathname="/login", id="output-state")
        return "Невірний логін або пароль"


# @server.route('/')
# def redirect_to_login():
#     return redirect(url_for('login'))


if __name__ == "__main__":
    # app.run_server(debug=True)
    log.info('start server')
    app.run_server(host='0.0.0.0', port=8050, debug=True)
