"""
Auth controllers
"""
from urllib import parse
import falcon
from .hooks import require_json_params, require_admin
from ..db.resources import User
from ..db.security import encode_jwt, decode_jwt
from ..mail import send_password_reset_email


class Register:
    @falcon.before(require_admin)
    @falcon.before(require_json_params(["username", "password"]))
    def on_post(self, req, resp):
        # try to register the user, user will be None on fail
        if (not req.media["username"]) or (not req.media["password"]):
            raise falcon.HTTPBadRequest(
                "400 Bad Request", "username and password must not be empty."
            )

        user = User.register(req.media["username"], req.media["password"])
        response = {"success": False}

        if user:
            response["success"] = True

        resp.media = response


class Login:
    @falcon.before(require_json_params(["username", "password"]))
    def on_post(self, req, resp):
        jwt = User.login(req.media["username"], req.media["password"])
        response = {"success": False}
        if jwt:
            response["success"] = True
            response["token"] = jwt

        resp.media = response


class Check:
    def on_get(self, req, resp):
        resp.media = {
            "username": req.context.username,
            "userHasAdmin": req.context.user_has_admin,
        }


class ResetPassword:
    @falcon.before(require_json_params(["email", "url"]))
    def on_post(self, req, resp):
        """
        Send a reset link using url to the user's email only
        if a user is found by email
        """
        user = User.find_by_email(req.media["email"])
        if not user:
            resp.media = {"success": False}
            return

        # create a reset token expiring in 24 hours
        reset_token = encode_jwt(user.username, 86400)

        # format the url
        url = "{}{}{}".format(
            req.media["url"], "?", parse.urlencode({"resettoken": reset_token})
        )

        # send the email
        send_password_reset_email(req.media["email"], user.username, url)

        resp.media = {"success": True}

    @falcon.before(require_json_params(["resetToken", "newPassword"]))
    def on_patch(self, req, resp):
        """
        Reset password if the token is good
        """
        decoded = decode_jwt(req.media["resetToken"])
        if not decoded:
            resp.media = {"success": False}
            return

        user = User(decoded["username"])
        if not req.media["newPassword"]:
            raise falcon.HTTPBadRequest(
                "400 Bad Request", "newPassword must not be empty."
            )

        user.set_credentials(password=req.media["newPassword"])

        resp.media = {"success": True}
