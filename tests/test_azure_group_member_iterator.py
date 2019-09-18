"""
Tests AzureGroupMemberIterator class
"""
import json
from unittest.mock import MagicMock
from api.azure_group_member_iterator import AzureGroupMemberIterator
# pylint: disable=unused-import
import tests.log_helper

def create_iterator(rtnvals):
    """
    Creates AzureGroupMemberIterator mock
    """
    gid = 'xxxxx'
    api = MagicMock()
    api.set_pagesize = MagicMock()
    api.get_paged_group_members = MagicMock(side_effect=rtnvals)
    ####################################################################
    # Graph API currently does not support OrderBy
    # Delete the following lines after it does
    #flattened = [item for sublist in rtnvals for item in sublist]
    flattened = [item for sublist in rtnvals for item in sublist]
    api.get_sorted_group_members = MagicMock(return_value=flattened)
    ####################################################################
    itr = AzureGroupMemberIterator(api, gid)
    return itr

def test_iterator_with_data():
    """
    Should return each group member until the end
    """
    raw1 = [
        {'id': '1', 'userPrincipalName': 'aaa1@test.com', 'displayName': 'bbb1 aaa1'},
        {'id': '2', 'userPrincipalName': 'aaa2@test.com', 'displayName': 'bbb2 aaa2'}
    ]
    raw2 = [
        {'id': '3', 'userPrincipalName': 'aaa3@test.com', 'displayName': 'bbb3 aaa3'},
        {'id': '4', 'userPrincipalName': 'aaa4@test.com', 'displayName': 'bbb4 aaa4'}
    ]
    raw3 = [{'id': '5', 'userPrincipalName': 'aaa5@test.com', 'displayName': 'bbb5 aaa5'}]
    page1 = json.loads(json.dumps(raw1))
    page2 = json.loads(json.dumps(raw2))
    page3 = json.loads(json.dumps(raw3))
    # Creates a mock
    itr = create_iterator([page1, page2, page3])
    itr.set_pagesize(2)
    assert next(itr) == {
        'id': '1',
        'userPrincipalName': 'aaa1@test.com',
        'displayName': 'bbb1 aaa1',
        'businessPhones': [],
        'mail': 'aaa1@test.com',
        'givenName': 'bbb1',
        'surname': 'aaa1'
    }
    assert next(itr) == {
        'id': '2',
        'userPrincipalName': 'aaa2@test.com',
        'displayName': 'bbb2 aaa2',
        'businessPhones': [],
        'mail': 'aaa2@test.com',
        'givenName': 'bbb2',
        'surname': 'aaa2'
    }
    assert next(itr) == {
        'id': '3',
        'userPrincipalName': 'aaa3@test.com',
        'displayName': 'bbb3 aaa3',
        'businessPhones': [],
        'mail': 'aaa3@test.com',
        'givenName': 'bbb3',
        'surname': 'aaa3'
    }
    assert next(itr) == {
        'id': '4',
        'userPrincipalName': 'aaa4@test.com',
        'displayName': 'bbb4 aaa4',
        'businessPhones': [],
        'mail': 'aaa4@test.com',
        'givenName': 'bbb4',
        'surname': 'aaa4'
    }
    assert next(itr) == {
        'id': '5',
        'userPrincipalName': 'aaa5@test.com',
        'displayName': 'bbb5 aaa5',
        'businessPhones': [],
        'mail': 'aaa5@test.com',
        'givenName': 'bbb5',
        'surname': 'aaa5'
    }
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
