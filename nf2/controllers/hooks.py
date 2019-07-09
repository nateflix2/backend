"""
Controller hooks
"""
import falcon
from ..db.resources import User


def require_json_params(param_list):
    """
    Hook to require a list of top-level json parameters, as well as a json content type
    Returns a callable instance of _RequireJsonParams
    """

    return lambda req, resp, resource, params: _require_json_call(
        req, resp, resource, params, param_list
    )


def _require_json_call(req, resp, resource, params, param_list):
    # require json body
    bad_req = falcon.HTTPBadRequest("Bad Request", "This endpoint requires JSON")
    if not req.media:
        raise bad_req

    if req.content_type != "application/json":
        raise bad_req

    missing_param = lambda x: falcon.HTTPBadRequest(
        "Bad Request", "Missing parameter '{}'".format(x)
    )

    for param in param_list:
        if param not in req.media:
            raise missing_param(param)


def require_admin(req, resp, resource, params):
    if not req.context.user_has_admin:
        raise falcon.HTTPForbidden("403 Forbidden.", "Admin rights are required.")


def require_user(req, resp, resource, params):
    """
    Hook to require a specific user be making the request
    Additionally, after this hook, the username passed is guaranteed 
    to be a valid user
    """
    required_user = params["username"]
    passed = False
    if req.context.user_has_auth:
        user = User(req.context.username)
        if user.valid and user.username.lower() == required_user.lower():
            passed = True

    if not passed:
        raise falcon.HTTPForbidden(
            "403 Forbidden.", "You are not permitted to make that request."
        )
