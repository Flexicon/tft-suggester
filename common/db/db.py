from pymongo import MongoClient
from pymongo.collection import Collection


class DB:
    _instance = None
    _connection = None
    _database = None

    def __init__(self):
        self._connection = MongoClient('mongodb://root:pass@mongo:27017/')
        self._database = self._connection.get_database('tft_suggester')

    @classmethod
    def connect(cls):
        if cls._instance is None:
            cls._instance = cls()

    @classmethod
    def disconnect(cls):
        cls._connection.close()
        cls._database = None
        cls._instance = None

    @classmethod
    def get_instance(cls) -> 'DB':
        cls.connect()
        return cls._instance

    def _get_collection(self, name: str):
        return self._database.get_collection(name)

    def get_comps_collection(self) -> Collection:
        return self._get_collection('comps')

    def get_champions_collection(self) -> Collection:
        return self._get_collection('champions')
