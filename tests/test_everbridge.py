"""
Test Everbrige Functions
"""
import json
import pytest
import ast
from requests.exceptions import HTTPError, Timeout
import api.everbridge_logic
import api.everbridge_api
from api.everbridge_api import URL, SESSION
from tests.mock_helper import RequestsMock, SessionMock

def test_sync_groups_with_invalid_parmeter():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("","","","","")
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("Test","","","","")
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("Test","Pass","","","")
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("Test","Pass","Org","","")
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("Test","Pass","Org",[],"")
    with pytest.raises(Exception):
        api.everbridge_logic.sync_everbridge_group("Test","Pass","Org",[{}],"")
def test_get_contacts_with_valid_params():
    """
    Should return contact data
    """
    org = "123456789101112"
    ad_data = {
        '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#directoryObjects',
        'value': [
            {
                '@odata.type': '#microsoft.graph.user',
                'id': '1000aaa-11bb-22cc-3344-1234567890ab',
                'businessPhones': ['808 000-0001'],
                'displayName': 'BBB, AAA',
                'givenName': 'AAA',
                'jobTitle': 'IT Specialist',
                'mail': 'AAA.BBB@hawaii.gov',
                'mobilePhone': None,
                'officeLocation': 'ZZZ',
                'preferredLanguage': None,
                'surname': 'BBB',
                'userPrincipalName': 'AAA.BBB@hawaii.gov'
            }
        ]
    }
    ever_raw = {
        "message": "OK",
        "firstPageUri": "",
        "lastPageUri": "",
        "page": {
            "pageSize": 100,
            "start": 0,
            "data": [
            {
                "groups": [
                    8105621194817886
                ],
                "createdName": "API USER",
                "lastName": "BBB",
                "externalId": "AAA.BBB.gov",
                "id": 350490806274647,
                "paths": [],
                "firstName": "AAA",
            }
        ],
        "totalCount": 1,
        "totalPageCount": 1,
        "currentPageNo": 1
        }
    }
    query = api.everbridge_logic.create_query(ad_data["value"])
    header = api.everbridge_logic.create_authheader("Test", "Pass")
    assert(query == "&externalIds=AAA.BBB@hawaii.gov")
    expected = json.loads(json.dumps(ever_raw))
    expected_url = URL.contacts_url(org,'?sortBy="lastName"&searchType=OR' + query) + ", data='null', headers=" + str(ast.literal_eval(str(header)))
    # Set up mocks
    mock = SessionMock()
    mock.setup(org, query, header, expected["page"]["data"], 200)
    # Call get_filtered_contacts
    # Check if arguments passed to session.get are correct
    # mock.access('requests.get').assert_called_with(expected_url)
    # Reinstate mocked functions
    mock.restore()
def test_get_group_with_empty_params():
    """
    Will return false because everbridge org does not have group
    """
    header = api.everbridge_logic.create_authheader("Test", "Pass")
    org = "123456789101112"
    empty_group = 	{
    "message": "OK",
    "result": {
        "lastModifiedTime": 0,
        "accountId": 0,
        "resourceBundleId": 0,
        "organizationId": 0,
        "id": 0,
        "parentId": 0,
        "lastModifiedId": 0,
        "createdId": 0,
        "lastSynchronizedTime": 0,
        "dirty": "false"
        }
    }
    new_group = {
        "baseUri": "string",
        "id": 132131313,
        "instanceUri": "string",
        "message": "string"
    }
    test_mock = SessionMock()
    mock_session = test_mock.get_group_setup(org, header, empty_group, new_group)
    insert_group = api.everbridge_logic.check_group("Hello", mock_session)
    assert insert_group == new_group["id"]
def test_get_group_with_valid_params():
    """
    Will return true because group exists within Everbridge
    """
    header = api.everbridge_logic.create_authheader("Test", "Pass")
    org = "123456789101112"
    actual_group = {
    "message": "OK",
    "result": {
        "createdName": "Test User",
        "lastModifiedTime": 1567042081488,
        "accountId": 0,
        "status": "A",
        "resourceBundleId": 0,
        "organizationId": 1111111111111,
        "id": 8105621194807886,
        "parentId": -1,
        "name": "TEST API",
        "lastModifiedDate": 1563240460233,
        "lastModifiedId": 351435698996023,
        "createdId": 8104014056945179,
        "createdDate": 1518292361877,
        "lastSynchronizedTime": 1508148670428,
        "lastModifiedName": "Test User",
        "enableSequencedContact": "false",
        "dirty": "false"
        }
    }
    test_mock = SessionMock()
    mock_session = test_mock.get_group_setup(org, header, actual_group, None)
    no_group = api.everbridge_logic.check_group("Hello", mock_session)
    assert no_group == actual_group["result"]["id"]
def test_get_group_with_error_params():
    """
    Will raise error from status code
    """
    header = api.everbridge_logic.create_authheader("Test", "Pass")
    org = "123456789101112"
    error_message = {
        "status": 401,
        "message":"error"
    }
    test_mock = SessionMock()
    mock_session = test_mock.get_group_setup(org, header, error_message, None)
    with pytest.raises(ValueError):
        api.everbridge_logic.check_group("Hello", mock_session)
def test_delete_group():
    """
    Will assert that delete group has been called
    """
    delete_batch_return = {
        "code": 200,
        "data": [
        "string"
        ],
        "message": "string"
    }
    delete_group_return = {
        "baseUri": "string",
        "id": 0,
        "instanceUri": "string",
        "message": "string"
    }
    group_return_value = {
    "message": "OK",
    "page": {
        "currentPageNo": 0,
        "data": [
            {
                "externalId": "string",
                "firstName": "string",
                "groups": [
                    0
                ],
                "id": 0,
                "lastName": "string",
            },
            {
                "externalId": "string",
                "firstName": "string",
                "groups": [
                    0
                ],
                "id": 0,
                "lastName": "string",
            },
            {
            "externalId": "string",
            "firstName": "string",
            "groups": [
                0
            ],
            "id": 0,
            "lastName": "string",
            }
        ],
        "pageSize": 1,
        "totalCount": 3,
        "totalPageCount": 0
    },
    "previousPageUri": "string"
    }
    test_mock = SessionMock()
    mock_session = test_mock.delete_setup(delete_group_return, group_return_value, delete_batch_return)
    count = api.everbridge_logic.delete_evercontacts("123456",{},mock_session)
    assert count == 3
    assert mock_session.delete_group.assert_called_once

