"""
Helps mock management in tests
"""
import logging
from unittest.mock import MagicMock
import adal
import requests
from requests import Response
from api.azure import Azure
from api.everbridge import Everbridge

class BaseMock:
    """
    Defins the basic behavior of Mock Class
    Implement setup method in inherited class
    """
    def __init__(self):
        self.saved_functions = []
        self.mocked = {}
    def restore(self):
        """
        Reinstates mocked functions
        """
        for func in self.saved_functions:
            func['target'] = func['original']
    def access(self, target_name):
        """
        Returns mocked function
        """
        return self.mocked[target_name]
    def register(self, name, target):
        """
        Keeps track of each mocked function to expose it through access method
        """
        self.mocked[name] = target
    def save(self, target, original):
        """
        Keeps track of each mocked function to reinstate it
        """
        self.saved_functions.append({'target':target, 'original':original})

class AdalMock(BaseMock):
    """
    Handles adal mock
    """
    def setup(self, rtnval, side_effect=False):
        """
        Sets up mocks
        """
        context = MagicMock()
        if side_effect:
            context.acquire_token_with_client_credentials = MagicMock(side_effect=rtnval)
        else:
            context.acquire_token_with_client_credentials = MagicMock(return_value=rtnval)
        self.register('context.acquire_token_with_client_credentials',
                      context.acquire_token_with_client_credentials)
        orig_func = adal.AuthenticationContext
        adal.AuthenticationContext = MagicMock(return_value=context)
        self.register('adal.AuthenticationContext', adal.AuthenticationContext)
        self.save(adal.AuthenticationContext, orig_func)

class RequestsMock(BaseMock):
    """
    Handles requests session mock
    """
    def setup(self, rtnval, code=None):
        """
        Sets up mocks
        """
        orig_func = requests.session
        session = MagicMock()
        session.headers.update = MagicMock()
        self.register('session.headers.update', session.headers.update)
        if code:
            # If code is provided, session.get returns Response that contains rtnval
            res = Response()
            res.status_code = code
            res.json = MagicMock(return_value=rtnval)
            session.get = MagicMock(return_value=res)
            self.register('session.get', session.get)
        else:
            # Without code, session.get returns side_effect
            session.get = MagicMock(side_effect=rtnval)
        requests.session = MagicMock(return_value=session)
        self.save(requests.session, orig_func)

def create_everbridge_mock(rtnval, code=None):
    """
    Sets up Everbidge mock
    """
    mock = Everbridge("1234567", "user", "pass")
    if code:
        # If code is provided, session.get returns Response that contains rtnval
        res = Response()
        res.status_code = code
        res.json = MagicMock(return_value=rtnval)
        mock.get_filtered_contacts = MagicMock(return_value=res)
    else:
        # Without code, session.get returns side_effect
        mock.get_filtered_contacts = MagicMock(side_effect=rtnval)
    return mock

def create_everbridge_group_mock(rtnval, group_info):
    """
    Sets up Everbidge mock
    """
    mock = Everbridge("1234567", "user", "pass")
    mock.get_group_info = MagicMock(return_value=rtnval)
    mock.add_group = MagicMock(return_value=group_info)
    return mock

def create_everbridge_get_group_mock(rtnval, group_info):
    """
    Setup group mock session
    """
    mock_session = MagicMock()
    mock_session.get_group_info = MagicMock(return_value=rtnval)
    mock_session.add_group = MagicMock(return_value=group_info)
    return mock_session

def create_everbridge_delete_mock(contact_value, group_value, group_delete):
    """
    Sets delete mocks
    """
    mock = Everbridge("1234567", "user", "pass")
    mock.delete_group = MagicMock(return_value=group_delete)
    mock.delete_contacts_from_org = MagicMock(return_value=contact_value)
    mock.delete_contacts_from_group = MagicMock(return_value=contact_value)
    mock.get_group = MagicMock(return_value=group_value)
    return mock

def create_everbridge_insert_mock(group_value):
    """
    Setup delete mock session
    """
    mock_session = MagicMock()
    mock_session.get_filtered_contacts = MagicMock(return_value = group_value)
    mock_session.insert_new_contacts = MagicMock(return_value = None)
    return mock_session

class LoggingMock(BaseMock):
    """
    Handles logging mock
    """
    def setup(self):
        """
        Sets up mocks
        """
        orig1 = logging.root.handlers
        orig2 = logging.root.removeHandler
        orig3 = logging.basicConfig
        logging.root.handlers = MagicMock()
        logging.root.removeHandlers = MagicMock()
        logging.basicConfig = MagicMock()
        self.register('logging.basicConfig', logging.basicConfig)
        self.save('logging.basicConfig', orig3)
        self.save('logging.root.handlers', orig1)
        self.save('logging.root.removeHandlers', orig2)

# pylint: disable=dangerous-default-value
def create_azure_instance(cid=None, secret=None, tenant=None,
                          token={'accessToken':'XXXTOKENXXX'}):
    """
    Creates Azure instance
    """
    if not cid:
        cid = 'cid'
    if not secret:
        secret = 'secret'
    if not tenant:
        tenant = 'tenant'
    azure = Azure(cid, secret, tenant)
    azure.set_token(token)
    return azure

def create_azure_mock(side_ad_list):
    """
    Creates Azure instance
    """
    azure = Azure('cid', 'secret', 'tenant')
    azure.set_token({'accessToken':'XXXTOKENXXX'})
    azure.get_group_members = MagicMock()
    azure.get_group_members.side_effect = side_ad_list
    return azure
