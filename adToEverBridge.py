#Requests Client Crediential Token and then performs API call to get Login Events
import adal
import requests
import json
import base64
import argparse
#https://manager.everbridge.net/saml/login/ETSEverbridgeSSO
def get_argparser():
    #Build argument parser.
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    return parser

def get_AzureGroups(tenant,username,password,id,secret,url,inquiry,):
    #Fetch Azure AD Group with Adal
    authority = "https://login.microsoftonline.com/" + tenant
    #Request Token
    context = adal.AuthenticationContext(authority)
    token = context.acquire_token_with_username_password(url,username,password,id)
    #Create Rest Session
    SESSION = requests.Session()
    SESSION.headers.update({'Authorization': f"Bearer {token['accessToken']}",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'})
    #Return Group Array
    response = SESSION.get(url + inquiry)
    if response.status_code == 200:
        return response.json()
    else: 
        print(response.raise_for_status())
        return None
def post_EverbridgeGroups(username,password,id,groupData, groupId):
    #Update Everbridge Group

    #Convert username and password to base64
    combineString = username + ":" + password
    combineBytes = combineString.encode("utf-8")
    combineEncode = base64.b64encode(combineBytes)
    everSession = requests.Session()
    print(combineEncode)
    everSession.headers.update({'Authorization': combineEncode,
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'})
    everData = everSession.get('https://api.everbridge.net/rest/contacts/892807736729063/?sortBy="lastName"').json()
    MaxPage = everData["lastPageUri"]
if __name__ == '__main__':
    args = get_argparser().parse_args()
    config = json.load(open(args.filename))

    data = get_AzureGroups(config["adTenant"],config["adUsername"],config["adPassword"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/" + config["adGroup"] + "/members")
    post_EverbridgeGroups(config["everbridgeUsername"],config["everbridgePassword"],config["everbridgeId"],data["value"],"")
