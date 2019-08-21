"""
Test Everbrige Functions
"""
import json
import pytest
import ast
from requests.exceptions import HTTPError, Timeout
import api.everbridge_logic
import api.everbridge_api
from api.everbridge_api import URL
from tests.mock_helper import RequestsMock, GetMock

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
    mock = GetMock()
    mock.setup(expected["page"]["data"], 200)
    # Call get_filtered_contacts
    data = api.everbridge_api.get_filtered_contacts(query,header,org)
    # Check if arguments passed to session.get are correct
    # mock.access('requests.get').assert_called_with(expected_url)
    assert data == expected["page"]["data"]
    # Reinstate mocked functions
    mock.restore()
