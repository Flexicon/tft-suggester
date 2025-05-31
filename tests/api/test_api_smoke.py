import os
import pytest
from testcontainers.mongodb import MongoDbContainer

from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient

from api import app, db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    mongodb = MongoDbContainer()
    mongodb.start()

    def remove_container():
        mongodb.stop()

    request.addfinalizer(remove_container)

    mongodb_uri = f"{mongodb.get_connection_url()}/tft_suggester?authSource=admin"
    os.environ["MONGODB_URI"] = mongodb_uri

    def disconnect_db():
        db.disconnect()

    request.addfinalizer(disconnect_db)
    db.connect()


@pytest.mark.integration
def test_get_root():
    response = client.get("/")
    assert HTTP_200_OK == response.status_code


@pytest.mark.integration
def test_get_comps():
    response = client.get("/comps")
    assert HTTP_200_OK == response.status_code


@pytest.mark.integration
def test_get_champions():
    response = client.get("/champions")
    assert HTTP_200_OK == response.status_code


@pytest.mark.integration
def test_get_items():
    response = client.get("/items")
    assert HTTP_200_OK == response.status_code
