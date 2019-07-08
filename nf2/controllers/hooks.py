"""
Controller hooks
"""
import falcon


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
