import unittest
from unittest.mock import patch, Mock

from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient

from api import app

client = TestClient(app)


class ApiTest(unittest.TestCase):
    def test_get_root(self):
        response = client.get("/")
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertDictEqual(response.json(), {"msg": "TFT Suggester API"})

    @patch("api.api.db")
    def test_get_comps(self, db_mock):
        collection_mock = Mock()
        collection_mock.find.return_value = [
            {
                "_id": "comp-id-1",
                "name": "Inferno",
                "tier": "S",
                "champions": [
                    {
                        "_id": "champ-id-1",
                        "name": "Varus",
                        "image": "varus.png",
                        "cost": 1,
                        "traits": ["Exotech", "Executioner"],
                    },
                    {
                        "_id": "champ-id-2",
                        "name": "Zyra",
                        "image": "zyra.png",
                        "cost": 3,
                    },
                ],
                "playstyle": "Slow Roll",
                "item_recommendations": [],
            },
        ]
        db_mock.get_comps_collection.return_value = collection_mock

        response = client.get("/comps")
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(
            response.json(),
            [
                {
                    "name": "Inferno",
                    "tier": "S",
                    "champions": [
                        {
                            "name": "Varus",
                            "image": "varus.png",
                            "cost": 1,
                            "traits": ["Exotech", "Executioner"],
                        },
                        {
                            "name": "Zyra",
                            "image": "zyra.png",
                            "cost": 3,
                            "traits": [],
                        },
                    ],
                    "playstyle": "Slow Roll",
                    "item_recommendations": [],
                }
            ],
        )

    @patch("api.api.db")
    def test_get_champions(self, db_mock):
        collection_mock = Mock()
        collection_mock.find.return_value = [
            {
                "_id": "champ-id-1",
                "name": "Varus",
                "image": "varus.png",
                "cost": 1,
                "traits": ["Exotech", "Executioner"],
            },
            {
                "_id": "champ-id-2",
                "name": "Zyra",
                "image": "zyra.png",
                "cost": 3,
                "traits": ["Street Demon", "Techie"],
            },
        ]
        db_mock.get_champions_collection.return_value = collection_mock

        response = client.get("/champions")
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(
            response.json(),
            [
                {
                    "name": "Varus",
                    "image": "varus.png",
                    "cost": 1,
                    "traits": ["Exotech", "Executioner"],
                },
                {
                    "name": "Zyra",
                    "image": "zyra.png",
                    "cost": 3,
                    "traits": ["Street Demon", "Techie"],
                },
            ],
        )
