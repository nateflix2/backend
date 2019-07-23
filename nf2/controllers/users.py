"""
User controllers
"""
import falcon
from ..db.resources import User
from .hooks import require_json_params, require_user

class Users:
    def on_get(self, req, resp):
        """
        Get all users
        """
        users = User.find_all()
        resp.media = users
        

class CompleteRegistration:
    @falcon.before(require_user)
    def on_get(self, req, resp, username):
        """
        Respond with whether or not the user has completed registration.
        """
        completed = False
        user = User(username)
        if not user.valid:
            raise falcon.HTTPBadRequest("Bad Request", "Invalid User")

        completed = user.get_document()["completed_registration"]

        resp.media = {"completed": completed}

    @falcon.before(require_json_params(["email", "newpassword"]))
    @falcon.before(require_user)
    def on_post(self, req, resp, username):
        """
        Complete the registration process
        """
        email = req.media["email"]
        newpassword = req.media["newpassword"]

        user = User(username)
        if not user.valid:
            raise falcon.HTTPBadRequest("Bad Request", "Invalid User")

        user.set_credentials(password=newpassword, email=email)
        user.set_completed_registration(True)
        user.update_last_active()

        resp.media = {"success": True}
