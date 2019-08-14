"""
Helps mock management in tests
"""
from unittest.mock import MagicMock
import requests
from requests import Response
import adal

class BaseMock:
    """
    Defins the basic behavior of Mock Class
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
        Keeps track of each mocked function to expose it through access
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
