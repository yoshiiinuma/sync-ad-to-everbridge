"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import sys
import requests
from requests import HTTPError
import adal
def get_token(client_id, secret, authority):
    """
    Get Azure AD Token
    """
    context = adal.AuthenticationContext(authority)
    try:
        token = context.acquire_token_with_client_credentials("https://graph.microsoft.com/",
                                                              client_id, secret)
        return token
    except HTTPError as error:
        logging.error(error)
        sys.exit(1)
def get_azuregroups(tenant, client_id, secret, url):
    """
    Fetch Azure AD Group with Adal
    """
    authority = "https://login.microsoftonline.com/" + tenant
    #Request Token
    token = get_token(client_id, secret, authority)
    #Create Rest session
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    #Will manually search through all groups if Group ID is empty
    try:
        response = session.get(url)
        if response.status_code == 200:
            return response.json()["value"]
        else:
            return None
    except requests.exceptions.RequestException as error:
        logging.error(error)
        sys.exit(1)
