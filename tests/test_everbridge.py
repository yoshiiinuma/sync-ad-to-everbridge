"""
Tests Everbridge API Functions
"""
import json
from unittest.mock import patch
import pytest
from api.exceptions import EverbridgeException
from tests.everbridge_helper import create_everbridge_contacts, \
                                    create_everbridge_instance, \
                                    create_session_mock, \
                                    expected_header
# pylint: disable=unused-import
import tests.log_helper

def test_contacts_url():
    """
    Should return contacts API URL
    """
    ever = create_everbridge_instance()
    exp = 'https://api.everbridge.net/rest/contacts/1234567'
    assert ever.contacts_url() == exp

def test_groups_url():
    """
    Should return groups API URL
    """
    ever = create_everbridge_instance()
    exp = 'https://api.everbridge.net/rest/groups/1234567'
    assert ever.groups_url() == exp

def test_contacts_groups_url():
    """
    Should return contacts groups API URL
    """
    ever = create_everbridge_instance()
    exp = 'https://api.everbridge.net/rest/contacts/groups/1234567'
    assert ever.contacts_groups_url() == exp

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_contacts_by_external_ids(mock_session):
    """
    Should send GET request to specific URL
    """
    extids = (
        '&externalIds=aaabbb0001@xxx.com' +
        '&externalIds=aaabbb0002@xxx.com' +
        '&externalIds=aaabbb0003@xxx.com')
    data = create_everbridge_contacts([1, 2, 3,], True)
    raw = {
        'message': 'OK',
        'page': {
            'pageSize': 100,
            'start': 0,
            'totalCount': 3,
            'totalPageCount': 0,
            'currentPageNo': 0,
            'data': data
        }
    }
    params = '?sortBy=externalId&direction=ASC&searchType=AND' + extids
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.contacts_url(params)
    # call get_contacts_by_external_ids
    rslt = ever.get_contacts_by_external_ids(extids)
    # Check if correct arguments are passed to session functions
    session.get.assert_called_with(expected_url)
    session.headers.update.assert_called_with(expected_header())
    assert rslt == data

def test_get_contacts_by_external_ids_with_no_external_ids():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.get_contacts_by_external_ids(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_contacts_by_external_ids_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    extids = '&externalIds=aaabbb0001@xxx.com&externalIds=aaabbb0002@xxx.com'
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call get_contacts_by_external_ids
    with pytest.raises(EverbridgeException):
        ever.get_contacts_by_external_ids(extids)

@patch('api.everbridge.requests.Session', autospec=True)
def test_upsert_contacts(mock_session):
    """
    Should send POST request to specific URL with data
    """
    contacts = create_everbridge_contacts([1, 2, 3,], True)
    raw = {'code': 100, 'message': 'OK'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.contacts_url('batch?version=1')
    # call upsert_contacts
    ever.upsert_contacts(contacts)
    # Check if correct arguments are passed to session functions
    session.post.assert_called_with(expected_url, json=contacts)
    session.headers.update.assert_called_with(expected_header())

def test_upsert_contacts_with_no_contacts():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.upsert_contacts(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_upsert_contacts_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    contacts = create_everbridge_contacts([1, 2, 3,], True)
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.upsert_contacts(contacts)

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_contacts(mock_session):
    """
    Should send DELETE request to specific URL with data
    """
    contacts = [1, 2, 3]
    raw = {'message': 'OK', 'code': 100}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.contacts_url('batch')
    # call delete_contacts
    ever.delete_contacts(contacts)
    # Check if correct arguments are passed to session functions
    session.delete.assert_called_with(expected_url, json=contacts)
    session.headers.update.assert_called_with(expected_header())

def test_delete_contacts_with_no_contacts():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.delete_contacts(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_contacts_with_unexpected_result(mock_session):
    """
    Should raise Exception
    """
    contacts = [1, 2, 3]
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.delete_contacts(contacts)

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_group_by_name(mock_session):
    """
    Should send GET request to specific URL
    """
    raw = {'message': 'OK', 'result': {'id': 123}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('xxxxx?queryType=name')
    # call get_group_by_name
    ever.get_group_by_name('xxxxx')
    # Check if correct arguments are passed to session functions
    session.get.assert_called_with(expected_url)
    session.headers.update.assert_called_with(expected_header())

def test_get_group_by_name_without_name():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.get_group_by_name(None)
    with pytest.raises(EverbridgeException):
        ever.get_group_by_name('')

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_group_by_name_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.get_group_by_name('name')

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_group_id_by_name(mock_session):
    """
    Should send GET request to specific URL
    """
    raw = {'message': 'OK', 'result': {'id': 123}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('xxxxx?queryType=name')
    # call get_group_by_name
    ever.get_group_id_by_name('xxxxx')
    # Check if correct arguments are passed to session functions
    session.get.assert_called_with(expected_url)
    session.headers.update.assert_called_with(expected_header())

def test_get_group_id_by_name_with_no_group_id():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.get_group_id_by_name(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_get_group_id_by_name_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.get_group_id_by_name('name')

@patch('api.everbridge.requests.Session', autospec=True)
def test_paged_group_members(mock_session):
    """
    Should send GET request to specific URL
    """
    raw = {'message': 'OK', 'page': {'data': []}}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    params = '?groupIds=123&pageSize=100&pageNumber=1&sortBy=externalId&direction=ASC'
    expected_url = ever.contacts_url(params)
    # call get_group_by_name
    ever.get_paged_group_members(123)
    # Check if correct arguments are passed to session functions
    session.get.assert_called_with(expected_url)
    session.headers.update.assert_called_with(expected_header())

def test_paged_group_members_with_no_group_id():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.get_paged_group_members(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_paged_group_members_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='GET')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.get_paged_group_members(123)

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_members_from_group(mock_session):
    """
    Should send DELETE request to specific URL
    """
    members = [1, 2, 3]
    raw = {'message': 'OK', 'code': 100}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('contacts?byType=id&groupId=123&idType=id')
    # call delete_members_from_group
    ever.delete_members_from_group(123, members)
    # Check if correct arguments are passed to session functions
    session.delete.assert_called_with(expected_url, json=members)
    session.headers.update.assert_called_with(expected_header())

def test_delete_members_from_group_with_no_group_id():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.delete_members_from_group(None, [])

def test_delete_members_from_group_with_no_members():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.delete_members_from_group(123, None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_members_from_group_with_unexpected_result(mock_session):
    """
    Should raise Exception
    """
    members = [1, 2, 3]
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.delete_members_from_group(123, members)

@patch('api.everbridge.requests.Session', autospec=True)
def test_add_members_to_group(mock_session):
    """
    Should send POST request to specific URL
    """
    members = [1, 2, 3]
    raw = {'message': 'OK', 'code': 100}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('contacts?byType=id&groupId=123&idType=id')
    # call add_members_to_group
    ever.add_members_to_group(123, members)
    # Check if correct arguments are passed to session functions
    session.post.assert_called_with(expected_url, json=members)
    session.headers.update.assert_called_with(expected_header())

def test_add_members_to_group_with_no_group_id():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.add_members_to_group(None, [])

def test_add_members_to_group_with_no_members():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.add_members_to_group(123, None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_add_members_to_group_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    members = [1, 2, 3,]
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.add_members_to_group(123, members)

@patch('api.everbridge.requests.Session', autospec=True)
def test_add_group(mock_session):
    """
    Should send POST request to specific URL
    """
    raw = {'message': 'OK'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('')
    data = {'name': 'xxxxx', 'organizationId': '1234567', 'parentId': None}
    # call add_group
    ever.add_group('xxxxx')
    # Check if correct arguments are passed to session functions
    session.post.assert_called_with(expected_url, json=data)
    session.headers.update.assert_called_with(expected_header())

def test_add_group_without_name():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.add_group(None)
    with pytest.raises(EverbridgeException):
        ever.add_group('')

@patch('api.everbridge.requests.Session', autospec=True)
def test_add_group_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='POST')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.add_group('name')

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_group(mock_session):
    """
    Should send DELETE request to specific URL
    """
    raw = {'message': 'OK'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=200, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    expected_url = ever.groups_url('123')
    # call delete_group
    ever.delete_group(123)
    # Check if correct arguments are passed to session functions
    session.delete.assert_called_with(expected_url)
    session.headers.update.assert_called_with(expected_header())

def test_delete_group_with_no_group_id():
    """
    Should raise Exception
    """
    ever = create_everbridge_instance()
    with pytest.raises(EverbridgeException):
        ever.delete_group(None)

@patch('api.everbridge.requests.Session', autospec=True)
def test_delete_group_with_unexpected_response(mock_session):
    """
    Should raise Exception
    """
    raw = {'status': 401, 'message': 'Invalid Credintials: Password Invalid'}
    expected = json.loads(json.dumps(raw))
    # Set up mocks
    session = create_session_mock(expected, code=401, method='DELETE')
    mock_session.return_value = session
    ever = create_everbridge_instance()
    # call upsert_contacts
    with pytest.raises(EverbridgeException):
        ever.delete_group(123)
