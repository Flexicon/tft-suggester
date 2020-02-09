from unittest.mock import patch

from api.handlers import get_champions_handler
from common.models import Champion


@patch('pymongo.collection.Collection')
def test_handler_returns_a_list_of_collection_results(collection):
    collection.find.return_value = [Champion('Master Yi', 'image1.png'), Champion('Zed', 'image2.png')]
    result = get_champions_handler(collection)

    collection.find.assert_called_once()
    assert len(result) is 2
    assert result[0].name is 'Master Yi'
    assert result[1].name is 'Zed'
