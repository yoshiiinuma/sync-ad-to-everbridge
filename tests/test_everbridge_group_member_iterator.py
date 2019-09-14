"""
Tests EverbridgeGroupMemberIterator class
"""
import json
from unittest.mock import MagicMock
from api.everbridge_group_member_iterator import EverbridgeGroupMemberIterator
# pylint: disable=unused-import
import tests.log_helper

def create_iterator(rtnvals):
    """
    Creates EverbridgeGroupMemberIterator mock
    """
    gid = 'xxxxx'
    api = MagicMock()
    api.set_pagesize = MagicMock()
    api.get_paged_group_members = MagicMock(side_effect=rtnvals)
    itr = EverbridgeGroupMemberIterator(api, gid)
    return itr

def test_iterator_with_data():
    """
    Should return each group member until the end
    """
    raw1 = [
        {'id': '1', 'externalId': 'aaa1@test.com'},
        {'id': '2', 'externalId': 'aaa2@test.com'}
    ]
    raw2 = [
        {'id': '3', 'externalId': 'aaa3@test.com'},
        {'id': '4', 'externalId': 'aaa4@test.com'}
    ]
    raw3 = [{'id': '5', 'externalId': 'aaa5@test.com'}]
    page1 = json.loads(json.dumps(raw1))
    page2 = json.loads(json.dumps(raw2))
    page3 = json.loads(json.dumps(raw3))
    # Creates a mock
    itr = create_iterator([page1, page2, page3, []])
    itr.set_pagesize(2)
    assert next(itr) == {'id': '1', 'externalId': 'aaa1@test.com'}
    assert next(itr) == {'id': '2', 'externalId': 'aaa2@test.com'}
    assert next(itr) == {'id': '3', 'externalId': 'aaa3@test.com'}
    assert next(itr) == {'id': '4', 'externalId': 'aaa4@test.com'}
    assert next(itr) == {'id': '5', 'externalId': 'aaa5@test.com'}
    assert next(itr) is None
    assert next(itr) is None
    assert itr.get_total() == 5

def test_iterator_with_no_data():
    """
    Should return None each time
    """
    # Creates a mock
    itr = create_iterator([[]])
    itr.set_pagesize(2)
    assert next(itr) is None
    assert next(itr) is None
    assert next(itr) is None
    assert itr.get_total() == 0
