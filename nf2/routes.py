"""
routes module
"""
from .controllers.auth import Login, Register, ResetPassword, Check
from .controllers.users import Users, SingleUser, CompleteRegistration

# these routes do not require authentication
AUTH_WHITELIST = ["/auth/login", "/auth/resetpassword"]


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

    # GET /auth/check
    # returns: username, userHasAdmin (bool)
    check = Check()
    app.add_route("/auth/check", check)

    # POST /auth/resetpassword
    # json params: email, url
    # returns: success (bool)
    #
    # PATCH /auth/resetpassword
    # json params: resetToken newPassword
    # returns: success (bool)
    reset_pw = ResetPassword()
    app.add_route("/auth/resetpassword", reset_pw)

    # GET /users
    # returns: all users
    users = Users()
    app.add_route("/users", users)

    # GET /users/{username}
    # returns: user doc
    #
    # POST /users/{username}
    # accepted params: username, password, email, admin_perms
    # requires admin to set admin_params
    # returns: success(bool), updatedUser (doc)
    single_user = SingleUser()
    app.add_route("/users/{username}", single_user)

    # GET /users/{username}/completeregistration
    # returns: completed (bool)
    #
    # POST /users/{username}/completeregistration
    # json params: email, newpassword
    # returns: success (bool)
    complete_reg = CompleteRegistration()
    app.add_route("/users/{username}/completeregistration", complete_reg)
