from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def _connect() -> Database:
    client = MongoClient('mongodb://root:pass@mongo:27017/')
    return client.get_database('tft_suggester')


def connect_champions_collection() -> Collection:
    return _connect().get_collection('champions')


def connect_items_collection() -> Collection:
    return _connect().get_collection('items')


def connect_comps_collection() -> Collection:
    return _connect().get_collection('comps')
