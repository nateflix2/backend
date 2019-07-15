"""
Database security functions
"""

import os
from time import time
import hashlib
import jwt


def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()


def encode_jwt(username, exp_time=2592000):
    jwt_key = os.environ["NF_SECRET_KEY"]
    exp_time = int(time()) + exp_time
    return jwt.encode({"username": username, "exp": exp_time}, jwt_key).decode()


def decode_jwt(jwt_in):
    jwt_key = os.environ["NF_SECRET_KEY"]

    try:
        decoded = jwt.decode(jwt_in, jwt_key)
    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return None

    return decoded
