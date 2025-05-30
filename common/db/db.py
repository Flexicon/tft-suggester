import os
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection


class DB:
    _connection = None
    _database = None

    def connect(self, connection_url: Union[str, None] = None) -> "DB":
        if connection_url is None:
            connection_url = os.getenv("MONGODB_URI")

        self._connection = MongoClient(
            connection_url,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
        )
        self._database = self._connection.get_database()
        return self

    def disconnect(self):
        if self._connection:
            self._connection.close()

    def _get_collection(self, name: str):
        if self._database is None:
            raise ConnectionError(
                "Database not connected. Make sure to run connect() first."
            )
        return self._database.get_collection(name)

    def get_comps_collection(self) -> Collection:
        return self._get_collection("comps")

    def get_champions_collection(self) -> Collection:
        return self._get_collection("champions")

    def get_items_collection(self) -> Collection:
        return self._get_collection("items")
