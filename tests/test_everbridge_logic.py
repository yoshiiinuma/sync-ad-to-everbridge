"""
Test Everbrige Functions
"""
import json
import pytest
import ast
from requests.exceptions import HTTPError, Timeout
import api.everbridge_logic
from api.everbridge import Everbridge
from tests.mock_helper import create_everbridge_mock, create_everbridge_group_mock, create_everbridge_delete_mock, create_everbridge_get_group_mock, create_everbridge_insert_mock

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
    assert(query == ["&externalIds=AAA.BBB@hawaii.gov"])
    # Set up mocks
    mock_session = create_everbridge_mock(ever_raw, 200)
    # Call get_filtered_contacts
    contacts = mock_session.get_filtered_contacts(query)
    # Check if arguments passed to session.get are correct
    mock_session.get_filtered_contacts.assert_called_with(query)
    assert contacts.json()["page"]["data"] == ever_raw["page"]["data"]

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
    mock_session = create_everbridge_get_group_mock(empty_group, new_group)
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
    mock_session = create_everbridge_get_group_mock(actual_group, None)
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
    mock_session =  create_everbridge_get_group_mock(error_message, None)
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
    mock_session = create_everbridge_delete_mock(delete_group_return, group_return_value, delete_batch_return)
    count = api.everbridge_logic.delete_evercontacts("123456",{},mock_session)
    assert count == -1
    assert mock_session.delete_contacts_from_group.called_with("123456", [0, 0, 0])
    assert mock_session.delete_group.assert_called_once

def test_parse_ever_data():
    """
    Returns a dictionary and list based on the AD Group
    """
    group_return_value = {
    "message": "OK",
    "page": {
        "currentPageNo": 0,
        "data": [
            {
                "externalId": "first@hawaii.gov",
                "firstName": "first",
                "lastName": "One",
                "groups": [
                    0
                ],
                "id": 1,
                "paths":[                   
                        {
                            "countryCode": "US",
                            "pathId": 241901148045316,
                            "status": "A",
                            "value": "first@hawaii.gov",
                            "waitTime": 0
                        },
                        {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": "111-1111",
                        "skipValidation": "false"
                        }
                    ]
                },
            {
                "externalId": "second@hawaii.gov",
                "firstName": "second",
                "groups": [
                    0
                ],
                "id": 2,
            "paths":[  {
                            "countryCode": "US",
                            "pathId": 241901148045316,
                            "status": "A",
                            "value": "second@hawaii.gov",
                            "waitTime": 0
                        },
                        {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": "222-2222",
                        "skipValidation": "false"
                        }],
                "lastName": "two",
            },
            {
            "externalId": "three@hawaii.gov",
            "firstName": "third",
            "groups": [
                0
            ],
            "paths":[  {
                            "countryCode": "US",
                            "pathId": 241901148045316,
                            "status": "A",
                            "value": "three@hawaii.gov",
                            "waitTime": 0
                        },
                        {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": "333-3333",
                        "skipValidation": "false"
                        }],
            "id": 3,
            "lastName": "three",
            }
        ],
        "pageSize": 1,
        "totalCount": 3,
        "totalPageCount": 0
    },
    "previousPageUri": "string"
    }
    parsed_data = api.everbridge_logic.parse_ever_data(group_return_value["page"]["data"])
    assert parsed_data[1] == [1, 2 ,3]
    assert parsed_data[0]["three@hawaii.gov"]["workPhone"]["value"] == "333-3333"

def test_ad_parse():
    """
    Returns a array equal to the number of AD Users due to different phone numbers
    """
    ad_info = [{
            "@odata.type": "#microsoft.graph.user",
            "id": "abc1",
            "businessPhones": [
                "808 111-1111"
            ],
            "displayName": "One, First",
            "givenName": "Fist",
            "jobTitle": "Secretary",
            "mail": "First.One@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Somewhere",
            "preferredLanguage": "",
            "surname": "One",
            "userPrincipalName": "First.One@hawaii.gov"
        },
        {
            "@odata.type": "#microsoft.graph.user",
            "id": "def2",
            "businessPhones": [
                "808 222-2222"
            ],
            "displayName": "Two, Second",
            "givenName": "Second",
            "jobTitle": "IT Manager",
            "mail": "Second.Two@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Nowhere",
            "preferredLanguage": "",
            "surname": "Two",
            "userPrincipalName": "Second.Two@hawaii.gov"
        },
        {
            "@odata.type": "#microsoft.graph.user",
            "id": "ghi3",
            "businessPhones": [
                "808 333-3333"
            ],
            "displayName": "Three,Third",
            "givenName": "Third",
            "jobTitle": "Senior Communications Manager",
            "mail": "Third.Three@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Everwhere",
            "preferredLanguage": "",
            "surname": "Three",
            "userPrincipalName": "Third.Three@hawaii.gov"
        }]
    group_return_value = {
        "message": "OK",
        "page": {
            "currentPageNo": 0,
            "data": [
                {
                    "externalId": "First.One@hawaii.gov",
                    "firstName": "First",
                    "lastName": "One",
                    "groups": [
                        0
                    ],
                    "id": 1,
                    "paths":[                   
                            {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "First.One@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "567-4321",
                            "skipValidation": "false"
                            }
                        ]
                    },
                {
                    "externalId": "Second.Two@hawaii.gov",
                    "firstName": "Second",
                    "groups": [
                        0
                    ],
                    "id": 2,
                "paths":[  {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "Second.Two@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "321-3241",
                            "skipValidation": "false"
                            }],
                    "lastName": "two",
                },
                {
                "externalId": "Third.Three@hawaii.gov",
                "firstName": "Third",
                "groups": [
                    0
                ],
                "paths":[  {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "Third.Three@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "355-4321",
                            "skipValidation": "false"
                            }],
                "id": 3,
                "lastName": "Three",
                }
            ],
            "pageSize": 1,
            "totalCount": 3,
            "totalPageCount": 0
        },
        "previousPageUri": "string"
        }
    parsed_data = api.everbridge_logic.parse_ever_data(group_return_value["page"]["data"])
    contact_check = parsed_data[0]
    parsed_group_data = api.everbridge_logic.parse_ad_data(ad_info, contact_check)
    update_list = parsed_group_data[1]
    assert len(update_list) == 3

def test_create_contact():
    """
    Will return 1 due to 2 members being returned from contact query 
    """
    ad_info = [{
            "@odata.type": "#microsoft.graph.user",
            "id": "abc1",
            "businessPhones": [
                "808 111-1111"
            ],
            "displayName": "One, First",
            "givenName": "Fist",
            "jobTitle": "Secretary",
            "mail": "First.One@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Somewhere",
            "preferredLanguage": "",
            "surname": "One",
            "userPrincipalName": "First.One@hawaii.gov"
        },
        {
            "@odata.type": "#microsoft.graph.user",
            "id": "def2",
            "businessPhones": [
                "808 222-2222"
            ],
            "displayName": "Two, Second",
            "givenName": "Second",
            "jobTitle": "IT Manager",
            "mail": "Second.Two@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Nowhere",
            "preferredLanguage": "",
            "surname": "Two",
            "userPrincipalName": "Second.Two@hawaii.gov"
        },
        {
            "@odata.type": "#microsoft.graph.user",
            "id": "ghi3",
            "businessPhones": [
                "808 333-333"
            ],
            "displayName": "Three,Third",
            "givenName": "Third",
            "jobTitle": "Senior Communications Manager",
            "mail": "Third.Three@hawaii.gov",
            "mobilePhone": "",
            "officeLocation": "Everwhere",
            "preferredLanguage": "",
            "surname": "Three",
            "userPrincipalName": "Third.Three@hawaii.gov"
        }]
    group_return_value = {
        "message": "OK",
        "page": {
            "currentPageNo": 0,
            "data": [
                {
                    "externalId": "First.One@hawaii.gov",
                    "firstName": "First",
                    "lastName": "One",
                    "groups": [
                        0
                    ],
                    "id": 1,
                    "paths":[                   
                            {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "First.One@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "111-1111",
                            "skipValidation": "false"
                            }
                        ]
                    },
                {
                "externalId": "Third.Three@hawaii.gov",
                "firstName": "Third",
                "groups": [
                    0
                ],
                "paths":[  {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "Third.Three@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "333-3333",
                            "skipValidation": "false"
                            }],
                "id": 3,
                "lastName": "Three",
                }
            ],
            "pageSize": 1,
            "totalCount": 3,
            "totalPageCount": 0
        },
        "previousPageUri": "string"
        }
    contact_list = []
    mock_sesion = create_everbridge_insert_mock(group_return_value)
    insert_count = api.everbridge_logic.create_evercontacts(ad_info, contact_list, mock_sesion)
    assert insert_count == 2
    assert contact_list == [1 ,3]

def test_multi_page():
    contacts = []
    group_return_value = {
        "message": "OK",
        "page": {
            "currentPageNo": 0,
            "data": [
                {
                    "externalId": "First.One@hawaii.gov",
                    "firstName": "First",
                    "lastName": "One",
                    "groups": [
                        0
                    ],
                    "id": 1,
                    "paths":[                   
                            {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "First.One@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "111-1111",
                            "skipValidation": "false"
                            }
                        ]
                    },
                {
                    "externalId": "Second.Two@hawaii.gov",
                    "firstName": "Second",
                    "groups": [
                        0
                    ],
                    "id": 2,
                "paths":[  {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "Second.Two@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "222-2222",
                            "skipValidation": "false"
                            }],
                    "lastName": "two",
                },
                {
                "externalId": "Third.Three@hawaii.gov",
                "firstName": "Third",
                "groups": [
                    0
                ],
                "paths":[  {
                                "countryCode": "US",
                                "pathId": 241901148045316,
                                "status": "A",
                                "value": "Third.Three@hawaii.gov",
                                "waitTime": 0
                            },
                            {
                            "waitTime": 0,
                            "status": "A",
                            "pathId": 241901148045321,
                            "countryCode": "US",
                            "value": "333-3333",
                            "skipValidation": "false"
                            }],
                "id": 3,
                "lastName": "Three",
                }
            ],
            "pageSize": 1,
            "totalCount": 3,
            "totalPageCount": 0
        },
        "previousPageUri": "string"
        }
    parsed_data = api.everbridge_logic.parse_ever_data(group_return_value["page"]["data"])
    contact_check = parsed_data[0]
    parsed_group_data = api.everbridge_logic.parse_ad_data(contacts, contact_check)
    lucky_number = 777
    for count in range(lucky_number):
        contacts.append( 
            {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "808 222-2222"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
            }
        )
    mock_session = create_everbridge_insert_mock(group_return_value)
    queries = api.everbridge_logic.create_query(contacts)
    contact_list = []
    insert_count = api.everbridge_logic.create_evercontacts(contacts, contact_list, mock_session)
    assert mock_session.get_filtered_contacts.call_count == 8

def test_invalid_phone():
    """
    New Contact will not have business phone due to invalid format
    """
    bad_contact_one = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "abcdefgh"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    new_contact_one = api.everbridge_logic.create_contact(bad_contact_one)
    assert len(new_contact_one["paths"]) == 1
    bad_contact_two = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "112345678910"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    new_contact_two = api.everbridge_logic.create_contact(bad_contact_two)
    assert len(new_contact_two["paths"]) == 1
def test_phone_ext():
    """
    Asserts Contact Path for business phone will have a extension key
    """
    contact = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "8085603043x343"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contact = api.everbridge_logic.create_contact(contact)
    assert ever_contact["paths"][1]["phoneExt"] == "343"
def test_invalid_mobile_phone():
    """
    Asserts Contact Paths will not have mobile phone and sms
    """
    contact = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "8085603043x343"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "(808)3333-3333",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contact = api.everbridge_logic.create_contact(contact)
    assert len(ever_contact["paths"]) == 2
    contactTwo = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "8085603043x343"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "(8048)3333-3333",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contactTwo = api.everbridge_logic.create_contact(contactTwo)
    assert len(ever_contactTwo["paths"]) == 2
    contactThree = {
                "@odata.type": "#microsoft.graph.user",
                "id": "def2",
                "businessPhones": [
                    "8085603043x343"
                ],
                "displayName": "Two, Second",
                "givenName": "Second",
                "jobTitle": "IT Manager",
                "mail": "Second.Two@hawaii.gov",
                "mobilePhone": "(808)333-3333x33333333333333333",
                "officeLocation": "Nowhere",
                "preferredLanguage": "",
                "surname": "Two",
                "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contactThree = api.everbridge_logic.create_contact(contactThree)
    assert len(ever_contactThree["paths"]) == 2
def test_mobile_phone():
    """
    Asserts Contact Paths will have mobile phone and sms
    """
    contact = {
        "@odata.type": "#microsoft.graph.user",
        "id": "def2",
        "businessPhones": [
            "8085603043x343"
        ],
        "displayName": "Two, Second",
        "givenName": "Second",
        "jobTitle": "IT Manager",
        "mail": "Second.Two@hawaii.gov",
        "mobilePhone": "(808)333-3333",
        "officeLocation": "Nowhere",
        "preferredLanguage": "",
        "surname": "Two",
        "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contact = api.everbridge_logic.create_contact(contact)
    assert len(ever_contact["paths"]) == 4
    contactTwo = {
        "@odata.type": "#microsoft.graph.user",
        "id": "def2",
        "businessPhones": [
            "8085603043x343"
        ],
        "displayName": "Two, Second",
        "givenName": "Second",
        "jobTitle": "IT Manager",
        "mail": "Second.Two@hawaii.gov",
        "mobilePhone": "808-333-3333",
        "officeLocation": "Nowhere",
        "preferredLanguage": "",
        "surname": "Two",
        "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contactTwo = api.everbridge_logic.create_contact(contactTwo)
    assert len(ever_contactTwo["paths"]) == 4
    contactThree = {
        "@odata.type": "#microsoft.graph.user",
        "id": "def2",
        "businessPhones": [
            "8085603043x343"
        ],
        "displayName": "Two, Second",
        "givenName": "Second",
        "jobTitle": "IT Manager",
        "mail": "Second.Two@hawaii.gov",
        "mobilePhone": "333-3333",
        "officeLocation": "Nowhere",
        "preferredLanguage": "",
        "surname": "Two",
        "userPrincipalName": "Second.Two@hawaii.gov"
    }
    ever_contactThree = api.everbridge_logic.create_contact(contactThree)
    assert len(ever_contactThree["paths"]) == 4


