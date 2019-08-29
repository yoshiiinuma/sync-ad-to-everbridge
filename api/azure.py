"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal

class URL:
    """
    Define URL constants
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
    Get Azure AD Token
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
    Fetch Azure AD Group Members with Adal
    """
    if not group_id:
        logging.error('AZURE.API.get_group_members: Invalid Group ID')
        raise Exception('AZURE.API.get_group_members: Invalid Group ID')
    if not token or not token['accessToken']:
        logging.error('AZURE.API.get_group_members: Invalid Token')
        raise Exception('AZURE.API.get_group_members: Invalid Token')
    #Create Rest session
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    url = URL.group_members_url(group_id)
    #Will manually search through all groups if Group ID is empty
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
    Fetch Azure AD Group Members with Adal
    """
    if not group_id:
        logging.error('AZURE.API.get_group_name: Invalid Group ID')
        raise Exception('AZURE.API.get_group_name: Invalid Group ID')
    if not token or not token['accessToken']:
        logging.error('AZURE.API.get_group_name: Invalid Token')
        raise Exception('AZURE.API.get_group_name: Invalid Token')
    #Create Rest session
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    url = URL.group_url(group_id)
    #Will manually search through all groups if Group ID is empty
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

