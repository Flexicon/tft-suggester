from unittest.mock import MagicMock

import pytest
from pymongo.errors import OperationFailure
from testcontainers.community.mongodb import MongoDbContainer

from common.db import DB
from common.db.db import replace_collection


def _fake_collection(name: str = "comps"):
    staging = MagicMock()
    target = MagicMock()
    database = MagicMock()
    database.get_collection.side_effect = lambda collection_name: (
        staging if collection_name.endswith("__staging") else target
    )
    collection = MagicMock()
    collection.name = name
    collection.database = database
    return collection, staging, target


def test_replace_collection_swaps_staging_into_target():
    collection, staging, target = _fake_collection()

    replace_collection(collection, [{"name": "new"}])

    staging.drop.assert_called_once()
    staging.insert_many.assert_called_once_with([{"name": "new"}])
    staging.rename.assert_called_once_with("comps", dropTarget=True)
    target.drop.assert_not_called()
    target.insert_many.assert_not_called()


def test_replace_collection_falls_back_when_rename_is_rejected():
    collection, staging, target = _fake_collection()
    staging.rename.side_effect = OperationFailure("not authorized")

    replace_collection(collection, [{"name": "new"}])

    target.drop.assert_called_once()
    target.insert_many.assert_called_once_with([{"name": "new"}])
    assert staging.drop.call_count == 2, "staging should be cleaned up on failure"


@pytest.fixture(scope="module")
def db():
    container = MongoDbContainer()
    container.start()
    connection_url = f"{container.get_connection_url()}/tft_suggester?authSource=admin"
    database = DB().connect(connection_url)
    try:
        yield database
    finally:
        database.disconnect()
        container.stop()


@pytest.mark.integration
def test_replace_collection_swaps_documents(db):
    db.get_comps_collection().insert_many([{"name": "old"}])

    db.replace_collection("comps", [{"name": "new"}])

    assert [doc["name"] for doc in db.get_comps_collection().find()] == ["new"]


@pytest.mark.integration
def test_replace_collection_accepts_empty_documents(db):
    db.get_comps_collection().insert_many([{"name": "old"}])

    db.replace_collection("comps", [])

    assert list(db.get_comps_collection().find()) == []
