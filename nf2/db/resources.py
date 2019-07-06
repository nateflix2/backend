"""
Database resources
"""
from .db import db
from .security import hash_pass

## Collections
COL_USER = db.db.get_collection("users")

## Schema definitions

SCHEMA_USER = {
    # unique username
    "username": None,
    # sha256 password hash
    "password": None,
    # admin permission flags
    "admin_perms": [],
    # unix timestamp of last activity
    "last_active": None,
}


class User:
    def __init__(self, username):
        """
        Init a user by unique username
        """
        self.document = COL_USER.find_one({"username": username})

        # missing user, this should never happen and with throw an error
        if not self.document:
            raise RuntimeError("Missing user {} in database.".format(username))

    @staticmethod
    def register(username, password):
        """
        Attempt to register a new user in the database
        Returns the User, or None if the username exists.
        """
        if COL_USER.find_one({"username": username}):
            return None

        new_user = SCHEMA_USER.copy()
        new_user["username"] = username
        new_user["password"] = hash_pass(password)

        COL_USER.insert_one(new_user)

        return User(username)

    @staticmethod
    def login(username, password):
        """
        Attempt to log in a user with a username and password.
        Returns a JWT or None if the login failed
        """
        return None
