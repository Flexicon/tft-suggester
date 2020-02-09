from unittest.mock import patch

from api.handlers import get_comps_handler
from common.models import Comp


@patch('pymongo.collection.Collection')
def test_handler_returns_a_list_of_collection_results(collection):
    collection.find.return_value = [Comp('Comp 1'), Comp('Comp 2')]
    result = get_comps_handler(collection)

    collection.find.assert_called_once()
    assert len(result) is 2
    assert result[0].name is 'Comp 1'
    assert result[1].name is 'Comp 2'
