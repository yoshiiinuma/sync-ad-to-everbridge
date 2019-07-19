#Requests Client Crediential Token and then performs API call to get Login Events
import adal
import requests
import json
import logging
from requests.exceptions import HTTPError 

#Get Azure AD Token
def get_Token(id,secret,authority,url):
    logging.info("Getting authority token")
    context = adal.AuthenticationContext(authority)
    token = context.acquire_token_with_client_credentials(url,id,secret)
    return token
def get_AzureGroups(auth,tenant,id,secret,url,inquiry,groupName,groupId):
    #Fetch Azure AD Group with Adal
    authority = auth + tenant
    #Request Token
    token = get_Token(id,secret,authority,url)
    #Create Rest Session
    logging.info("Getting Azure groups")
    SESSION = requests.Session()
    SESSION.headers.update({'Authorization': f"Bearer {token['accessToken']}",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'})
    #Return Group Array
    if len(groupId) > 0:
        logging.info("Getting Group by Id")
        inquiry += groupId + "/members"
        response = SESSION.get(url + inquiry)
        if response.status_code == 200:
            logging.info("Returning group data by Id")
            return(response.json()["value"])
        else: 
            logging.error("No group found through Id")
            return None
    #Will manually search through all groups if Group ID is empty
    else:
        logging.info("Searching group by groupname")
        response = SESSION.get(url + inquiry)
        data = response.json()["value"]
        for group in data:
            if group["displayName"] == groupName:
                inquiry += group["id"] + "/members"
                groupResponse = SESSION.get(url + inquiry)
                if groupResponse.status_code == 200:
                    logging.info("Searching group by groupname")
                    return(groupResponse.json()["value"])
                else: 
                    logging.error("Unable to get group members")
                    return None
        logging.error("No group name found")
        return None
