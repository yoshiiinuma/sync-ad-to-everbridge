"""
Test Azure Functions
"""
import json
import pytest
from adal import AdalError
from requests.exceptions import HTTPError, Timeout
import api.azure
from api.azure import URL
from tests.mock_helper import AdalMock, RequestsMock

#from os.path import dirname, abspath
#ROOTDIR = dirname(dirname(abspath(__file__)))
#CONF = json.load(open(ROOTDIR + "/config/test.json"))
#
#def test_real_get_token_with_valid_credential():
#    """
#    Should return token
#    """
#    token = api.azure.get_token(CONF['clientId'], CONF['clientSecret'], CONF['adTenant'])
#    assert token
#    assert token['accessToken']
#
#def test_real_get_token_with_invalid_credential():
#    """
#    Should raise an exception
#    """
#    with pytest.raises(AdalError):
#        api.azure.get_token('WrongClientId', CONF['clientSecret'], CONF['adTenant'])
#    with pytest.raises(AdalError):
#        api.azure.get_token(CONF['clientId'], 'WrongSecret', CONF['adTenant'])
#    with pytest.raises(AdalError):
#        api.azure.get_token(CONF['clientId'], CONF['clientSecret'], 'WrongcTenant')
#
#def test_real_get_group_members():
#    """
#    Exptected: Will return a array of members of a group through group name
#    """
#    token = api.azure.get_token(CONF['clientId'], CONF['clientSecret'], CONF['adTenant'])
#    data = api.azure.get_group_members(CONF['adGroupId'], token)
#    assert data
#    assert False

def test_authority_url_with_valid_param():
    """
    Shoud return expected URL with a valid parameter
    """
    tenant = 'tenant'
    url = URL.authority_url(tenant)
    assert url == 'https://login.microsoftonline.com/tenant'

def test_group_members_url_with_valid_param():
    """
    Should return expected URL with a valid parameter
    """
    gid = 'groupid'
    url = URL.group_members_url(gid)
    assert url == 'https://graph.microsoft.com/v1.0/groups/' + gid + '/members'

def test_get_token_with_invalid_parmeter():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.azure.get_token('aaa', 'bbb', None)
    with pytest.raises(Exception):
        api.azure.get_token('aaa', None, 'ccc')
    with pytest.raises(Exception):
        api.azure.get_token(None, 'bbb', 'ccc')
    with pytest.raises(Exception):
        api.azure.get_token('aaa', 'bbb', '')
    with pytest.raises(Exception):
        api.azure.get_token('aaa', '', 'ccc')
    with pytest.raises(Exception):
        api.azure.get_token('', 'bbb', 'ccc')

def test_get_token_with_valid_params():
    """
    Should return token
    """
    tenant = 'adtenant'
    cid = 'clientid'
    secret = 'clientsecret'
    expected_res = {'accessToken':'XXXXTOKENXXX'}
    authority_url = URL.authority_url(tenant)
    api_url = URL.API_BASE
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(expected_res)
    # Call get_token function
    token = api.azure.get_token(cid, secret, tenant)
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
    with pytest.raises(HTTPError):
        api.azure.get_token('cid', 'secrete', 'tenant')
    # Reinstate mocked functions
    mock.restore()

def test_get_token_with_timeout():
    """
    Should raise an exception
    """
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(Timeout, True)
    with pytest.raises(Timeout):
        api.azure.get_token('cid', 'secrete', 'tenant')
    # Reinstate mocked functions
    mock.restore()

def test_get_token_with_adalerror():
    """
    Should raise an exception
    """
    # Set up adal mock functions
    mock = AdalMock()
    mock.setup(AdalError('Invalid Client'), True)
    with pytest.raises(AdalError):
        api.azure.get_token('cid', 'secrete', 'tenant')
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_invalid_groupid():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.azure.get_group_members(None, {'accessToken':'XXXTOKENXXX'})
    with pytest.raises(Exception):
        api.azure.get_group_members('', {'accessToken':'XXXTOKENXXX'})

def test_get_group_members_with_invalid_token():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.azure.get_group_members('aaa', None)
    with pytest.raises(Exception):
        api.azure.get_group_members('aaa', {})
    with pytest.raises(Exception):
        api.azure.get_group_members('aaa', {'accessToken':None})

def test_get_group_members_with_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
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
    expected_url = URL.group_members_url(gid)
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 200)
    # Call get_group_members
    data = api.azure.get_group_members(gid, token)
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

def test_get_group_members_with_400():
    """
    Should return None; AD returns 400 when token exprires
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
    raw = {'error': {'code': 'Request_BadRequest',
                     'message': 'Invalid object identifier \'WrongGroupId\'.'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 400)
    # Call get_group_members
    data = api.azure.get_group_members(gid, token)
    assert data is None
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_401():
    """
    Should return None; AD returns 401 when token exprires
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
    raw = {'error': {'code': 'InvalidAuthenticationToken', 'message': 'Access token has expired.'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 401)
    # Call get_group_members
    data = api.azure.get_group_members(gid, token)
    assert data is None
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_404():
    """
    Should return None; AD returns 404 when group doesn't exist
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
    raw = {'error': {'code': 'Request_ResourceNotFound',
                     'message': 'Resource \'0000aaa-bbbb-cccc\' does not exist'}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 404)
    # Call get_group_members
    data = api.azure.get_group_members(gid, token)
    assert data is None
    # Reinstate mocked functions
    mock.restore()

def test_get_group_members_with_timeout():
    """
    Should return None
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
    # Set up mocks
    mock = RequestsMock()
    mock.setup(Timeout)
    with pytest.raises(Exception):
        # Call get_group_members
        api.azure.get_group_members(gid, token)
    # Reinstate mocked functions
    mock.restore()
def test_get_group_name_with_invalid_groupid():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.azure.get_group_name(None, {'accessToken':'XXXTOKENXXX'})
    with pytest.raises(Exception):
        api.azure.get_group_name('', {'accessToken':'XXXTOKENXXX'})

def test_get_group_name_with_invalid_token():
    """
    Should raise an exception with an empty parameter
    """
    with pytest.raises(Exception):
        api.azure.get_group_name('aaa', None)
    with pytest.raises(Exception):
        api.azure.get_group_name('aaa', {})
    with pytest.raises(Exception):
        api.azure.get_group_name('aaa', {'accessToken':None})

def test_get_group_name_with_valid_params():
    """
    Should return group member data
    """
    gid = "000abcde-f123-56gh-i789-000000000jkl"
    token = {'accessToken':'XXXTOKENXXX'}
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
    expected_url = URL.group_url(gid)
    # Set up mocks
    mock = RequestsMock()
    mock.setup(expected, 200)
    # Call get_group_members
    data = api.azure.get_group_name(gid, token)
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