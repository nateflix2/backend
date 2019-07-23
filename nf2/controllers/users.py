"""
User controllers
"""
import falcon
from ..db.resources import User
from .hooks import require_json_params, require_user


class SingleUser:
    @falcon.before(require_user)
    def on_get(self, req, resp, username):
        """
        Get a specific user's document
        """
        user = User(username)
        resp.media = user.get_document()

    @falcon.before(require_user)
    def on_post(self, req, resp, username):
        """
        Change a user document, supported attributes only
        
        """
        user = User(username)

        # credentials
        new_username = None
        new_password = None
        new_email = None

        if "username" in req.media:
            new_username = req.media["username"]

        if "password" in req.media:
            new_password = req.media["password"]

        if "email" in req.media:
            new_email = req.media["email"]

        user.set_credentials(new_username, new_password, new_email)

        # admin perms
        if "admin_perms" in req.media:
            if not req.context.user_has_admin:
                raise falcon.HTTPForbidden(
                    "403 Forbidden", "You are not permitted to change admin_perms"
                )

            user.set_admin_perms(req.media["admin_perms"])

        resp.media = {"success": True, "updatedUser": user.get_document()}


class Users:
    def on_get(self, req, resp):
        """
        Get all users
        For scale limit and skip params should be accepted, but are not right now.
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

        user.set_credentials(password=newpassword, email=email)
        user.set_completed_registration(True)
        user.update_last_active()

        resp.media = {"success": True}
