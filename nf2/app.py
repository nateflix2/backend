"""
application
"""

import falcon

from .routes import add_routes
from .controllers.middleware import AuthMiddleware, CORSMiddleware

APP_SETTINGS = {
    "middleware": [CORSMiddleware(), AuthMiddleware()]
}


def make_app():
    app = falcon.API(**APP_SETTINGS)
    add_routes(app)
    return app


# gunicorn support
application = make_app()
