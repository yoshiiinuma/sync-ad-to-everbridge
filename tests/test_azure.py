"""
Tests Azure Functions
"""
import json
from unittest.mock import MagicMock
import pytest
from adal import AdalError
from requests.exceptions import HTTPError, Timeout
from api.exceptions import AzureException
from api.azure import Azure
from tests.mock_helper import AdalMock, RequestsMock
from tests.azure_helper import create_azure_instance, \
                               create_azure_instance_without_token, \
                               create_azure_contacts
# pylint: disable=unused-import
import tests.log_helper

def test_setup():
    """
    Tests if setup method calls get_token and set_token
    """
    token = {'accessToken':'XXXTOKENXXX'}
    azure = Azure('cid', 'secret', 'tenant')
    # Sets up mocks
    azure.get_token = MagicMock(return_value=token)
    azure.set_token = MagicMock()
    # Call setup method
    azure.setup()
    # Tests if specified methods are called
    azure.get_token.assert_called_with()
    azure.set_token.assert_called_with(token)

def test_setup_with_preset_token():
    """
    Tests if setup method does not call reset_token if token is alraedy set
    """
    token = {'accessToken':'XXXTOKENXXX'}
    azure = Azure('cid', 'secret', 'tenant')
    azure.set_token(token)
    # Sets up mocks
    azure.reset_token = MagicMock()
    # Call setup method
    azure.setup()
    # Tests if reset_token is not called
    assert not azure.reset_token.called

def test_reset_token():
    """
    Tests if reset_token calls get_token and set_token
    """
    token = {'accessToken':'XXXTOKENXXX'}
    azure = Azure('cid', 'secret', 'tenant')
    # Sets up mocks
    #azure.token = MagicMock()
    azure.get_token = MagicMock(return_value=token)
    azure.set_token = MagicMock()
    # Call reset method
    azure.reset_token()
    # Tests if specified methods are called
    azure.get_token.assert_called_with()
    azure.set_token.assert_called_with(token)

def test_authority_url_with_valid_param():
    """
    Shoud return expected URL with a valid parameter
    """
    azure = create_azure_instance()
    url = azure.authority_url()
    assert url == 'https://login.microsoftonline.com/tenant'

def test_paged_group_members_url():
    """
    Should return expected URL with default value
    """
    azure = create_azure_instance()
    gid = 'xxxx'
    base = "https://graph.microsoft.com/v1.0/groups/xxxx/members"
    url = azure.paged_group_members_url(gid, 1)
    assert url == base + '?$orderby=userPrincipalName&$top=100'
    url = azure.paged_group_members_url(gid, 2)
    assert url == base + '?$orderby=userPrincipalName&$top=100&$skip=100'
    url = azure.paged_group_members_url(gid, 3)
    assert url == base + '?$orderby=userPrincipalName&$top=100&$skip=200'

def test_paged_group_members_url_with_pagesize():
    """
    Should return expected URL with default value

    """
    azure = create_azure_instance()
    azure.set_pagesize(5)
    gid = 'xxxx'
    base = "https://graph.microsoft.com/v1.0/groups/xxxx/members"
    url = azure.paged_group_members_url(gid, 1)
    assert url == base + '?$orderby=userPrincipalName&$top=5'
    url = azure.paged_group_members_url(gid, 2)
    assert url == base + '?$orderby=userPrincipalName&$top=5&$skip=5'
    url = azure.paged_group_members_url(gid, 3)
    assert url == base + '?$orderby=userPrincipalName&$top=5&$skip=10'

def test_get_token_with_invalid_parmeter():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(AzureException):
        azure = Azure('aaa', 'bbb', None)
        azure.get_token()
    with pytest.raises(AzureException):
        azure = Azure('aaa', None, 'ccc')
        azure.get_token()
    with pytest.raises(AzureException):
        azure = Azure(None, 'bbb', 'ccc')
        azure.get_token()
    with pytest.raises(AzureException):
        azure = Azure('aaa', 'bbb', '')
        azure.get_token()
    with pytest.raises(AzureException):
        azure = Azure('aaa', '', 'ccc')
        azure.get_token()
    with pytest.raises(AzureException):
        azure = Azure('', 'bbb', 'ccc')
        azure.get_token()

def test_get_token_with_valid_params():
    """
    Should return token
    """
    tenant = 'adtenant'
    cid = 'clientid'
    secret = 'clientsecret'
    expected_res = {'accessToken':'XXXXTOKENXXX'}
    api_url = Azure.API_BASE
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(expected_res)
    # Call get_token function
    azure = create_azure_instance(cid, secret, tenant, expected_res)
    token = azure.get_token()
    authority_url = azure.authority_url()
    # Check if arguments passed to adal functions are correct
    mock.access('adal.AuthenticationContext').assert_called_with(authority_url)
    mock.access('context.acquire_token_with_client_credentials') \
        .assert_called_with(api_url, cid, secret)
    assert token == expected_res
    # Reinstate mocked functions
    mock.restore()

def test_get_token_with_httperror():
    """
    Should raise an exception
    """
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(HTTPError, True)
    # Call get_token
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_token()
    # Reinstate mocked functions
    mock.restore()

def test_get_token_with_timeout():
    """
    Should raise an exception
    """
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(Timeout, True)
    # Call get_token
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_token()
    # Reinstate mocked functions
    mock.restore()

def test_get_token_with_adalerror():
    """
    Should raise an exception
    """
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(AdalError('Invalid Client'), True)
    # Call get_token
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_token()
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_invalid_groupid():
    """
    Should raise an exception with an empty parameter
    """
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_group_members(None, None)
    with pytest.raises(AzureException):
        azure.get_group_members('', None)

def test_get_group_members_with_invalid_token():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', None)
        azure.get_group_members('aaa', None)
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {})
        azure.get_group_members('aaa', None)
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {'accessToken':None})
        azure.get_group_members('aaa', None)

def test_get_group_members_with_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {
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
            },
            {
                '@odata.type': '#microsoft.graph.user',
                'id': '2000aaa-11bb-22cc-3344-1234567890ab',
                'businessPhones': ['808 000-0002'],
                'displayName': 'DDD, CCC',
                'givenName': 'CCC',
                'jobTitle': 'IT Specialist',
                'mail': 'CCC.DDD@hawaii.gov',
                'mobilePhone': None,
                'officeLocation': 'ZZZ',
                'preferredLanguage': None,
                'surname': 'DDD',
                'userPrincipalName': 'CCC.DDD@hawaii.gov'
            },
            {
                '@odata.type': '#microsoft.graph.user',
                'id': '3000aaa-11bb-22cc-3344-1234567890ab',
                'businessPhones': ['808 000-0003'],
                'displayName': 'FFF, EEE',
                'givenName': 'EEE',
                'jobTitle': 'IT Specialist',
                'mail': 'EEE.FFF@hawaii.gov',
                'mobilePhone': None,
                'officeLocation': 'ZZZ',
                'preferredLanguage': None,
                'surname': 'FFF',
                'userPrincipalName': 'EEE.FFF@hawaii.gov'
            }
        ]
    }
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 200)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    data = azure.get_group_members(gid, None)
    expected_url = azure.group_members_url(gid)
    # Check if arguments passed to session.get are correct
    mock.access('session.get').assert_called_with(expected_url)
    mock.access('session.headers.update').assert_called_with({
        'Authorization': 'Bearer XXXTOKENXXX',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'
    })
    assert data["value"] == expected['value']
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_400():
    """
    Should return None; AD returns 400 when token exprires
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {'error': {'code': 'Request_BadRequest',
                     'message': 'Invalid object identifier \'WrongGroupId\'.'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 400)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    with pytest.raises(AzureException):
        azure.get_group_members(gid, None)
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_401():
    """
    Should return None; AD returns 401 when token exprires
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {'error': {'code': 'InvalidAuthenticationToken', 'message': 'Access token has expired.'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 401)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    with pytest.raises(AzureException):
        azure.get_group_members(gid, None)
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_404():
    """
    Should return None; AD returns 404 when group doesn't exist
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {'error': {'code': 'Request_ResourceNotFound',
                     'message': 'Resource \'0000aaa-bbbb-cccc\' does not exist'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 404)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    with pytest.raises(AzureException):
        azure.get_group_members(gid, None)
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_timeout():
    """
    Should raise Exception
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    # Set up mocks
    mock = RequestsMock()
    mock.setup(Timeout)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    with pytest.raises(AzureException):
        azure.get_group_members(gid, None)
    # Reinstate mocked functions
    mock.restore()

def test_get_paged_group_members_with_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {
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
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 200)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    data = azure.get_paged_group_members(gid, 1)
    expected_url = azure.paged_group_members_url(gid, 1)
    # Check if arguments passed to session.get are correct
    mock.access('session.get').assert_called_with(expected_url)
    mock.access('session.headers.update').assert_called_with({
        'Authorization': 'Bearer XXXTOKENXXX',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'
    })
    assert data == expected['value']
    # Reinstate mocked functions
    mock.restore()

def test_get_paged_group_members_with_invalid_group_id():
    """
    Should raise Exception
    """
    # Set up mocks
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_paged_group_members(None, 1)

def test_get_paged_group_members_with_invalid_page():
    """
    Should raise Exception
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    # Set up mocks
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_paged_group_members(gid, "1")
    with pytest.raises(AzureException):
        azure.get_paged_group_members(gid, 0)
    with pytest.raises(AzureException):
        azure.get_paged_group_members(gid, -1)

def test_get_group_name_with_invalid_groupid():
    """
    Should raise an exception with an empty parameter
    """
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_group_name(None)
    with pytest.raises(AzureException):
        azure.get_group_name('')

def test_get_group_name_with_invalid_token():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(AzureException):
        azure = create_azure_instance_without_token('cid', 'secret', 'tenant')
        azure.get_group_name('aaa')
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {})
        azure.get_group_name('aaa')
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {'accessToken':None})
        azure.get_group_name('aaa')

def test_get_group_name_with_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    raw = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#groups/$entity",
        "id": "111111111111111111111111111111",
        "deletedDateTime": "",
        "classification": "",
        "createdDateTime": "2018-11-07T23:13:45Z",
        "creationOptions": [],
        "description": "Test",
        "displayName": "ETest",
        "groupTypes": [],
        "mail": "Test",
        "mailEnabled": "",
        "mailNickname": "ets.it.coordinators",
        "onPremisesLastSyncDateTime": "2019-08-28T02:45:05Z",
        "onPremisesSecurityIdentifier": "",
        "onPremisesSyncEnabled": "",
        "preferredDataLocation": "",
        "proxyAddresses": [
        ],
        "renewedDateTime": "2018-11-07T23:13:45Z",
        "resourceBehaviorOptions": [],
        "resourceProvisioningOptions": [],
        "securityEnabled": "",
        "visibility": "",
        "onPremisesProvisioningErrors": []
    }
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 200)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    data = azure.get_group_name(gid)
    expected_url = azure.group_url(gid)
    # Check if arguments passed to session.get are correct
    mock.access('session.get').assert_called_with(expected_url)
    mock.access('session.headers.update').assert_called_with({
        'Authorization': 'Bearer XXXTOKENXXX',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'
    })
    assert data == expected["displayName"]
    # Reinstate mocked functions
    mock.restore()

def test_get_all_group_members():
    """
    Should return members and get called 7 times
    """
    side_ad_list = []
    base = 'https://graph.microsoft.com/v1.0/'
    context = base + '$metadata#directoryObjects'
    next_link = 'groups/da594e05-6c27-4eeb-b3d3-e60ee124218b/members?$skiptoken=ABCDEFG'
    for data in range(7):
        ad_data = {
            "@odata.context": context,
            "@odata.nextLink": next_link,
            "value": [{}, {}, {}]
        }
        if data == 6:
            del ad_data["@odata.nextLink"]
        side_ad_list.append(ad_data)
    # Call get_group_members
    azure = create_azure_instance()
    azure.get_group_members = MagicMock(side_effect=side_ad_list)
    data = azure.get_all_group_members("")
    assert len(data) == 21
    assert azure.get_group_members.call_count == 7

def test_get_all_group_members_map():
    """
    Should return contacts sorted by userPrincipalName
    """
    contacts = create_azure_contacts([1, 2, 3, 4, 5])
    expected_keys = [con['userPrincipalName'] for con in contacts]
    azure = create_azure_instance()
    azure.get_all_group_members = MagicMock(return_value=contacts)
    rslt = azure.get_all_group_members_map(123)
    print(expected_keys)
    print(rslt.keys())
    assert list(rslt.keys()) == expected_keys
    for key in rslt:
        expected_contact = contacts.pop(0)
        assert rslt[key] == expected_contact

def test_get_sorted_group_members():
    """
    Should return contacts sorted by userPrincipalName
    """
    contacts = create_azure_contacts([5, 3, 2, 1, 4])
    expected = create_azure_contacts([1, 2, 3, 4, 5])
    azure = create_azure_instance()
    azure.get_all_group_members = MagicMock(return_value=contacts)
    sorted_contacts = azure.get_sorted_group_members(123)
    assert sorted_contacts == expected

def test_get_users_with_filters_map():
    """
    Should raise an exception with an empty or invalid parameter
    """
    azure = create_azure_instance()
    with pytest.raises(AzureException):
        azure.get_users_with_filters_map(None)
    with pytest.raises(AzureException):
        azure.get_users_with_filters_map('A')
    with pytest.raises(AzureException):
        azure.get_users_with_filters_map(1)

def test_get_users_with_filters_map_with_invalid_token():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(AzureException):
        azure = create_azure_instance_without_token('cid', 'secret', 'tenant')
        azure.get_users_with_filters_map([])
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {})
        azure.get_users_with_filters_map([])
    with pytest.raises(AzureException):
        azure = create_azure_instance('cid', 'secret', 'tenant', {'accessToken':None})
        azure.get_users_with_filters_map([])

def test_get_users_with_filters_map_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    return_value = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "value": [
            {
                "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
                "businessPhones": [],
                "displayName": "TESTUSER",
                "givenName": "",
                "jobTitle": "",
                "mail": "TESTUSER@hawaii.gov",
                "mobilePhone": "",
                "officeLocation": "",
                "preferredLanguage": "",
                "surname": "",
                "userPrincipalName": "TESTUSER@hawaii.gov",
                "id": "f12665e7-1ecf-4a3c-b3b0-59c0776251b2"
            }
        ]
    }
    expected_value = {
        "TESTUSER@hawaii.gov":
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
            "businessPhones": [],
            "displayName": "TESTUSER",
            "givenName": "TEST",
            "jobTitle": "",
            "mail": "TESTUSER@hawaii.gov",
            "mobilePhone": None,
            "officeLocation": "",
            "preferredLanguage": "",
            "surname": "USER",
            "userPrincipalName": "TESTUSER@hawaii.gov",
            "id": "f12665e7-1ecf-4a3c-b3b0-59c0776251b2",
            'errors': False,
            'fixed': True,
        }
    }
    expected = json.loads(json.dumps(return_value))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected , 200)
    # Call get_group_members
    azure = create_azure_instance()
    azure.setup()
    data = azure.get_users_with_filters_map(["TESTUSER@hawaii.gov"])
    expected_url = azure.user_filter_url(azure.generate_email_filter_string(["TESTUSER@hawaii.gov"]))
    # Check if arguments passed to session.get are correct
    mock.access('session.get').assert_called_with(expected_url)
    mock.access('session.headers.update').assert_called_with({
        'Authorization': 'Bearer XXXTOKENXXX',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'
    })
    print(data)
    assert data["TESTUSER@hawaii.gov"] == expected_value["TESTUSER@hawaii.gov"]
    # Reinstate mocked functions
    mock.restore()