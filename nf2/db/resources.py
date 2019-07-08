"""
Database resources
"""
import re
from time import time
from pymongo.collation import Collation
from .db import db
from .security import hash_pass, encode_jwt

## Collections
COL_USER = db.db.get_collection("users")

## Create indexes
# Case-insensitive username index
COL_USER.create_index("username", collation=Collation("en", strength=1))

## Schema definitions

SCHEMA_USER = {
    # unique username
    "username": "",
    # sha256 password hash
    "password": "",
    # admin permission flags
    "admin_perms": [],
    # unix timestamp of last activity
    "last_active": 0,
}

## Constants

IGNORE_CASE = lambda x: re.compile("{}".format(x), re.IGNORECASE)


class User:
    def __init__(self, username):
        """
        Init a user by unique username
        """
        doc = COL_USER.find_one({"username": username})

        # missing user, this should never happen and will throw an error
        if not doc:
            raise RuntimeError("Missing user {} in database.".format(username))

        # self.username is the username exactly as it is in the database
        # it is safe to query a user by self.username
        self.username = doc["username"]

    def update_last_active(self):
        """
        Update this user's last active
        """
        COL_USER.update_one(
            {"username": self.username}, {"$set": {"last_active": int(time())}}
        )

    @staticmethod
    def register(username, password):
        """
        Attempt to register a new user in the database
        Returns the User, or None if the username exists.
        """
        # using RE to ignore case
        if COL_USER.find_one({"username": IGNORE_CASE(username)}):
            return None

        new_user = SCHEMA_USER.copy()
        new_user["username"] = username
        new_user["password"] = hash_pass(password)

        COL_USER.insert_one(new_user)

        user = User(username)
        user.update_last_active()

        return user

    @staticmethod
    def login(username, password):
        """
        Attempt to log in a user with a username and password.
        Returns a JWT or None if the login failed
        """
        user_query = {
            "username": IGNORE_CASE(username),
            "password": hash_pass(password),
        }

        user = COL_USER.find_one(user_query)
        if not user:
            return None

        return encode_jwt(user["username"])
