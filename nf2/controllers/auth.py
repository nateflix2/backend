"""
Auth controllers
"""
import falcon
from .hooks import require_json_params
from ..db.resources import User


@falcon.before(require_json_params(["username", "password"]))
class Register:
    def on_post(self, req, resp):
        # try to register the user, user will be None on fail
        user = User.register(req.media["username"], req.media["password"])
        response = {"success": False}
        if user:
            response["success"] = True

        resp.media = response


@falcon.before(require_json_params(["username", "password"]))
class Login:
    def on_post(self, req, resp):
        jwt = User.login(req.media["username"], req.media["password"])
        response = {"success": False}
        if jwt:
            response["success"] = True
            response["token"] = jwt

        resp.media = response
