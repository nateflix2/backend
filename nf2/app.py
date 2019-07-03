"""
application
"""

import falcon

from .routes import add_routes

APP_SETTINGS = {}

def make_app():
    app = falcon.API(**APP_SETTINGS)
    add_routes(app)
    return app

# gunicorn support
application = make_app()