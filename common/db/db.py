import os
from typing import Optional, Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure

STAGING_SUFFIX = "__staging"


def replace_collection(collection: Collection, documents: list[dict]) -> None:
    """Replace a collection's contents, preferring an atomic swap.

    Documents are written to a staging collection that is then renamed over the
    target, so readers see either the old or the new data. Deployments that do
    not allow ``renameCollection`` fall back to drop + insert.
    """
    database = collection.database
    name = collection.name
    staging_name = f"{name}{STAGING_SUFFIX}"
    staging = database.get_collection(staging_name)

    staging.drop()
    if documents:
        staging.insert_many(documents)

    try:
        staging.rename(name, dropTarget=True)
    except OperationFailure as exc:
        print(
            f"Could not atomically swap '{name}' ({exc}); "
            "falling back to drop + insert."
        )
        target = database.get_collection(name)
        target.drop()
        if documents:
            target.insert_many(documents)
        staging.drop()


class DB:
    def __init__(self) -> None:
        self._connection: Optional[MongoClient] = None
        self._database: Optional[Database] = None

    def connect(self, connection_url: Union[str, None] = None) -> "DB":
        if self._connection is not None:
            self._connection.close()

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
            self._connection = None
        self._database = None

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

    def replace_collection(self, name: str, documents: list[dict]) -> None:
        replace_collection(self._get_collection(name), documents)
