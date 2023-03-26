from pymongo.collection import Collection


def handler(items: Collection):
    return list(items.find())
