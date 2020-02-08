from pymongo.collection import Collection


def get_comps_handler(comps: Collection):
    return list(comps.find())
