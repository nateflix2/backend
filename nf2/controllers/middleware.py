"""
Middleware
"""
import falcon
from ..routes import AUTH_WHITELIST
from ..db.security import decode_jwt
from ..db.resources import User


class AuthMiddleware:
    """
    Middleware to check if a jwt is provided in the request header
    or in the query string
    """

    def process_request(self, req, resp):
        req.context.auth_token = None
        req.context.user_has_auth = False
        req.context.user_has_admin = False
        req.context.username = ""

        # check auth header
        if req.auth:
            auth_token = req.auth.replace(" ", "").replace("Bearer", "")

            # may still be 'None' if decode failed
            req.context.auth_token = decode_jwt(auth_token)

        # check query string if auth token still not found
        if "token" in req.params and not req.context.auth_token:
            token_val = req.params["token"]
            if isinstance(token_val, str):
                req.context.auth_token = decode_jwt(token_val)

        # check for valid auth and admin
        if req.context.auth_token:
            if "username" in req.context.auth_token:
                user = User(req.context.auth_token["username"])
                if user.valid:
                    # valid user
                    req.context.user_has_auth = True
                    req.context.username = user.username

                    # check admin
                    user_doc = user.get_document()
                    req.context.user_has_admin = user_doc["admin_perms"]

        # if the route is not in the auth whitelist, we need auth
        if req.path not in AUTH_WHITELIST and not req.context.user_has_auth:
            raise falcon.HTTPForbidden(
                "403 Forbidden", "An auth token must be provided."
            )
