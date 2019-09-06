"""
Helps mock management in tests
"""
import logging
from unittest.mock import MagicMock
import adal
import requests
from requests import Response
from api.everbridge_api import Session

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

class SessionMock(BaseMock):
    """
    Handles requests session mock
    """
    def setup(self, org, url, header, rtnval, code=None):
        """
        Sets  Get up mocks
        """
        mock_session = Session(org, header)
        if code:
            # If code is provided, session.get returns Response that contains rtnval
            res = Response()
            res.status_code = code
            res.json = MagicMock(return_value=rtnval)
            mock_session.get_filtered_contacts = MagicMock(return_value=res)
            self.register('get_filtered_contacts', mock_session.get_filtered_contacts)
            value = mock_session.get_filtered_contacts(url)
            mock_session.get_filtered_contacts.assert_called_with(url)
            assert value.json() == rtnval
        else:
            # Without code, session.get returns side_effect
            mock_session.get_filtered_contacts = MagicMock(side_effect=rtnval)
    def get_group_setup(self, org, header, rtnval, group_info):
        """
        Sets group mocks
        """
        mock_session = Session(org, header)
        mock_session.get_group_info = MagicMock(return_value=rtnval)
        mock_session.add_group = MagicMock(return_value=group_info)
        return mock_session
    def delete_setup(self, contact_value, group_value, group_delete):
        """
        Sets delete mocks
        """
        session = Session("1234567", {})
        session.delete_group = MagicMock(return_value=group_delete)
        session.delete_contacts_from_org = MagicMock(return_value=contact_value)
        session.delete_contacts_from_group = MagicMock(return_value=contact_value)
        session.get_everbridge_group = MagicMock(return_value=group_value)
        return session

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
