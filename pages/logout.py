import dash
from dash import html, dcc
from flask_login import logout_user, current_user

dash.register_page(__name__)


def layout():
    if current_user.is_authenticated:
        logout_user()
    return dcc.Location(pathname="/login", id="login-id")

