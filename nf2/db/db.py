"""
Database module containing the database class singleton
"""
import os
from pymongo import MongoClient


class _DataBase:
    def __init__(self):
        self.db_addr = "localhost"
        self.db_port = 27017

        # non-default database address
        if "NF_DB_ADDR" in os.environ:
            self.db_addr = os.environ["NF_DB_ADDR"]

        if "NF_DB_PORT" in os.environ:
            self.db_port = int(os.environ["NF_DB_PORT"])

        self.client = MongoClient(self.db_addr, self.db_port)
        self.db = self.client.get_database("nateflix")


db = _DataBase()
