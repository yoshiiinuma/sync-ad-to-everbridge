"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal
def get_token(client_id, secret, authority):
    """
    Get Azure AD Token
    """
    logging.info("Getting authority token")
    context = adal.AuthenticationContext(authority)
    token = context.acquire_token_with_client_credentials("https://graph.microsoft.com/",
                                                          client_id, secret)
    return token
def get_azuregroups(tenant, client_id, secret, url, group_name):
    """
    Fetch Azure AD Group with Adal
    """
    authority = "https://login.microsoftonline.com/" + tenant
    #Request Token
    token = get_token(client_id, secret, authority)
    #Create Rest session
    logging.info("Getting Azure groups")
    session = requests.session()
    session.headers.update({'Authorization': f"Bearer {token['accessToken']}",
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'return-client-request-id': 'true'})
    #Will manually search through all groups if Group ID is empty
    logging.info("Searching group by groupname")
    response = session.get(url)
    data = response.json()["value"]
    for group in data:
        if group["displayName"] == group_name:
            inquiry = group["id"] + "/members"
            group_response = session.get(url + inquiry)
            if group_response.status_code == 200:
                logging.info("Returning Group Data")
                return group_response.json()["value"]
    logging.error("No group name found")
    return None
