from pymongo.collection import Collection


def handler(comps: Collection):
    return list(comps.find())
