"""
Auth controllers
"""
class Login:
    def on_post(self, req, resp):
        resp.body = "ok"
