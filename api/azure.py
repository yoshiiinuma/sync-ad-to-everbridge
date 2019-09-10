"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal

class URL:
    """
    Defines URL constants
    """
    LOGIN = 'https://login.microsoftonline.com/'
    API_BASE = 'https://graph.microsoft.com/'
    API_GROUPS = API_BASE + 'v1.0/groups/'
    @staticmethod
    def authority_url(tenant):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + tenant
    @staticmethod
    def group_members_url(group_id):
        """
        Returns group members api URL
        """
        return URL.API_GROUPS + group_id + '/members'
    @staticmethod
    def group_url(group_id):
        """
        Returns group info api URL
        """
        return URL.API_GROUPS + group_id + '/'

def get_token(client_id, secret, tenant):
    """
    Gets Azure AD Token
    """
    if not client_id or not secret or not tenant:
        logging.error('AZURE.API.get_token: Invalid Parameter')
        raise Exception('AZURE.API.get_token: Invalid parameter')
    context = adal.AuthenticationContext(URL.authority_url(tenant))
    try:
        token = context.acquire_token_with_client_credentials(
            URL.API_BASE, client_id, secret)
        return token
    except Exception as err:
        logging.error(err)
        raise err

def get_group_members(group_id, token):
    """
    Fetches Azure AD Group Members with Adal
    """
    if not group_id:
        logging.error('AZURE.API.get_group_members: Invalid Group ID')
        raise Exception('AZURE.API.get_group_members: Invalid Group ID')
    if not token or not token['accessToken']:
        logging.error('AZURE.API.get_group_members: Invalid Token')
        raise Exception('AZURE.API.get_group_members: Invalid Token')
    # Create Rest session
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    url = URL.group_members_url(group_id)
    # Will manually search through all groups if Group ID is empty
    try:
        response = session.get(url)
        if response.status_code == 200:
            return response.json()['value']
        logging.error('AZURE.GET_GROUP_MEMBERS: Unexpected Error')
        logging.error(response.status_code)
        logging.error(response.json())
        return None
    except Exception as err:
        logging.error(err)
        raise err

def get_group_name(group_id, token):
    """
    Fetches Azure AD Group Members with Adal
    """
    if not group_id:
        logging.error('AZURE.API.get_group_name: Invalid Group ID')
        raise Exception('AZURE.API.get_group_name: Invalid Group ID')
    if not token or not token['accessToken']:
        logging.error('AZURE.API.get_group_name: Invalid Token')
        raise Exception('AZURE.API.get_group_name: Invalid Token')
    # Create Rest session
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    url = URL.group_url(group_id)
    # Will manually search through all groups if Group ID is empty
    try:
        response = session.get(url)
        if response.status_code == 200:
            return response.json()['displayName']
        logging.error('AZURE.GET_GROUP_NAME: Unexpected Error')
        logging.error(response.status_code)
        logging.error(response.json())
        return None
    except Exception as err:
        logging.error(err)
        raise err

class Azure:
    """
    Handles Azure Graph API requests
    """
    LOGIN = 'https://login.microsoftonline.com/'
    API_BASE = 'https://graph.microsoft.com/'
    API_GROUPS = API_BASE + 'v1.0/groups/'

    def __init__(self, client_id, secret, tenant):
        self.client_id = client_id
        self.secret = secret
        self.tenant = tenant
        self.token = None

    def setup(self):
        """
        Sets up token if it is empty; Must be called onece before any API calls
        """
        if not self.token:
            self.reset_token()

    def check_token(self):
        """
        Raises an Exception if token is not set
        """
        if not self.token or not self.token['accessToken']:
            logging.error('AZURE.API.get_group_name: Invalid Token')
            raise Exception('AZURE.API.get_group_name: Invalid Token')

    def reset_token(self):
        """
        Resets token
        """
        self.set_token(self.get_token())

    def get_token(self):
        """
        Gets Azure AD Token
        """
        if not self.client_id or not self.secret or not self.tenant:
            logging.error('AZURE.API.get_token: Invalid Parameter')
            raise Exception('AZURE.API.get_token: Invalid parameter')
        context = adal.AuthenticationContext(self.authority_url())
        try:
            token = context.acquire_token_with_client_credentials(
                Azure.API_BASE, self.client_id, self.secret)
            return token
        except Exception as err:
            logging.error(err)
            raise err

    def set_token(self, token):
        """
        Sets Azure AD Token to the internal variable
        """
        self.token = token

    def authority_url(self):
        """
        Returns authority URL for authentication context
        """
        return Azure.LOGIN + self.tenant

    # pylint: disable=no-self-use
    def group_members_url(self, group_id):
        """
        Returns group members api URL
        """
        return Azure.API_GROUPS + group_id + '/members'

    # pylint: disable=no-self-use
    def group_url(self, group_id):
        """
        Returns group info api URL
        """
        return Azure.API_GROUPS + group_id + '/'

    def get_group_members(self, group_id):
        """
        Fetches Azure AD Group Members with Adal
        """
        if not group_id:
            logging.error('AZURE.API.get_group_members: Invalid Group ID')
            raise Exception('AZURE.API.get_group_members: Invalid Group ID')
        self.check_token()
        token = self.token['accessToken']
        # Create Rest session
        session = requests.session()
        session.headers.update({'Authorization': f"Bearer {token}",
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'})
        url = self.group_members_url(group_id)
        # Will manually search through all groups if Group ID is empty
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.json()['value']
            logging.error('AZURE.GET_GROUP_MEMBERS: Unexpected Error')
            logging.error(response.status_code)
            logging.error(response.json())
            return None
        except Exception as err:
            logging.error(err)
            raise err

    def get_group_name(self, group_id):
        """
        Fetches Azure AD Group Members with Adal
        """
        if not group_id:
            logging.error('AZURE.API.get_group_name: Invalid Group ID')
            raise Exception('AZURE.API.get_group_name: Invalid Group ID')
        self.check_token()
        token = self.token['accessToken']
        # Create Rest session
        session = requests.session()
        session.headers.update({'Authorization': f"Bearer {token}",
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'})
        url = self.group_url(group_id)
        # Will manually search through all groups if Group ID is empty
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.json()['displayName']
            logging.error('AZURE.GET_GROUP_NAME: Unexpected Error')
            logging.error(response.status_code)
            logging.error(response.json())
            return None
        except Exception as err:
            logging.error(err)
            raise err
