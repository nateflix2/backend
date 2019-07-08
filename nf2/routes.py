"""
routes module
"""
from .controllers.auth import Login, Register


def add_routes(app):
    # /auth/register
    # json params: username, password
    # returns: success (bool)
    register = Register()
    app.add_route("/auth/register", register)

    # /auth/login
    # json params: username, password
    # returns: success (bool), token
    login = Login()
    app.add_route("/auth/login", login)
