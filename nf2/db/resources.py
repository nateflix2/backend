"""
Database resources
"""
import re
from time import time
from pymongo.collation import Collation
from .db import db
from .security import encode_jwt

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
    # email
    "email": "",
    # has admin permissions?
    "admin_perms": False,
    # unix timestamp of last activity
    "last_active": 0,
    # require sign-up completion
    "completed_registration": False,
}

## Constants

IGNORE_CASE = lambda x: re.compile("{}".format(x), re.IGNORECASE)

## Resource Classes


class User:
    def __init__(self, username):
        """
        Init a user by unique username
        """
        # none until a valid user is instantiated
        self.username = None

        # true if a valid user was instantiated
        self.valid = False

        doc = COL_USER.find_one({"username": IGNORE_CASE(username)})

        # missing user
        if not doc:
            return

        self.valid = True

        # self.username is the username exactly as it is in the database
        # it is safe to query a user by self.username
        self.username = doc["username"]

        # add any missing keys to the document, from the schema
        _validate_schema({"username": doc["username"]}, COL_USER, SCHEMA_USER, doc)

    def get_document(self):
        """
        Retreive this user's entire document from the database
        """
        if self.username is None or not self.valid:
            raise RuntimeError("Can't get the document of an invalid user resource.")

        return COL_USER.find_one({"username": self.username})

    def set_credentials(self, username=None, password=None, email=None):
        """
        Set one or more of this user's credentials
        """
        doc = self.get_document()
        if username:
            doc["username"] = username

        if password:
            doc["password"] = password

        if email:
            doc["email"] = email

        COL_USER.replace_one({"username": self.username}, doc)
        if username:
            self.username = username

    def set_completed_registration(self, value):
        COL_USER.update_one(
            {"username": self.username}, {"$set": {"completed_registration": value}}
        )

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
        new_user["password"] = password

        COL_USER.insert_one(new_user)

        user = User(username)

        return user

    @staticmethod
    def login(username, password):
        """
        Attempt to log in a user with a username and password.
        Returns a JWT or None if the login failed
        """
        user_query = {"username": IGNORE_CASE(username), "password": password}

        user = COL_USER.find_one(user_query)
        if not user:
            return None

        User(user["username"]).update_last_active()

        return encode_jwt(user["username"])


## Utility Functions
def _validate_schema(query, collection, schema, document):
    """
    Tests document against schema, adding missing keys from schema into document, 
    then finds a matching document using query in collection and updates it.
    """
    for key in schema:
        if key not in document:
            document[key] = schema[key]

    collection.replace_one(query, document)
