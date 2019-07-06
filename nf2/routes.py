"""
routes module
"""

from .controllers.auth import Login


def add_routes(app):
    login = Login()
    app.add_route("/auth/login", login)
