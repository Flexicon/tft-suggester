from unittest.mock import Mock, patch

import responses

import scraper.http_client as http_client
from scraper.http_client import DEFAULT_TIMEOUT, get


@responses.activate
def test_get_returns_response():
    responses.add(responses.GET, "https://example.com/data", body="ok")

    response = get("https://example.com/data")

    assert response.text == "ok"


def test_get_uses_default_timeout():
    fake_response = Mock()

    with patch.object(
        http_client.session, "get", return_value=fake_response
    ) as get_mock:
        response = get("https://example.com/data")

    get_mock.assert_called_once_with(
        "https://example.com/data", timeout=DEFAULT_TIMEOUT
    )
    assert response is fake_response
