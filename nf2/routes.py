"""
routes module
"""
from .controllers.auth import Login, Register

# these routes do not require authentication
AUTH_WHITELIST = [
    "/auth/login"
]

def add_routes(app):
    # POST /auth/register
    # json params: username, password
    # returns: success (bool)
    register = Register()
    app.add_route("/auth/register", register)

    # POST /auth/login
    # json params: username, password
    # returns: success (bool), token
    login = Login()
    app.add_route("/auth/login", login)

    # POST /users/{username}/completeregistration
    # json params: email, newpassword
    # returns: success (bool)
