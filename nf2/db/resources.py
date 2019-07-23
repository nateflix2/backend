"""
Database resources
"""
import re
from time import time
from pymongo.collation import Collation
from .db import db
from .security import encode_jwt, hash_pass

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

IGNORE_CASE = lambda x: re.compile("^{}$".format(x), re.IGNORECASE)

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

        doc = COL_USER.find_one({"username": self.username})

        # strip _id
        del doc["_id"]
        return doc

    def set_credentials(self, username=None, password=None, email=None):
        """
        Set one or more of this user's credentials
        """
        doc = self.get_document()
        if username is not None:
            doc["username"] = username

        if password is not None:
            doc["password"] = hash_pass(password)

        if email is not None:
            doc["email"] = email

        COL_USER.replace_one({"username": self.username}, doc)

        # update this instance
        if username:
            self.username = username

    def set_admin_perms(self, has_perms):
        COL_USER.update_one(
            {"username": self.username}, {"$set": {"admin_perms": has_perms}}
        )

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
        new_user["password"] = hash_pass(password)

        COL_USER.insert_one(new_user)

        user = User(username)

        return user

    @staticmethod
    def login(username, password):
        """
        Attempt to log in a user with a username and password.
        Returns a JWT or None if the login failed
        """
        user_query = {"username": IGNORE_CASE(username), "password": hash_pass(password)}

        user = COL_USER.find_one(user_query)
        if not user:
            return None

        User(user["username"]).update_last_active()

        return encode_jwt(user["username"])

    @staticmethod
    def find_by_email(email):
        """
        Find a user by email, returns None if no user could be found
        """
        query = {"email": IGNORE_CASE(email)}

        user = COL_USER.find_one(query)
        if not user:
            return None

        return User(user["username"])

    @staticmethod
    def find_all(skip=0, limit=1000):
        """
        Find all users sorted by most recently active
        """
        users = COL_USER.find(skip=skip, limit=limit).sort("last_active", -1)
        docs = []
        for doc in users:
            del doc["_id"]
            docs.append(doc)

        print(docs)
        return docs

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
