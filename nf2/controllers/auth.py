"""
Auth controllers
"""
import falcon
from .hooks import require_json_params
from ..db.security import hash_pass


@falcon.before(require_json_params(["username", "password"]))
class Register:
    def on_post(self, req, resp):
        password = req.media["password"]
        resp.media = {"pwhash": hash_pass(password)}


class Login:
    def on_post(self, req, resp):
        resp.body = "ok"
