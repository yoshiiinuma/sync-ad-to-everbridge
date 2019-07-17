#Requests Client Crediential Token and then performs API call to get Login Events
import adal
import requests
import json
import base64
import argparse
def get_argparser():
    #Build argument parser.
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    return parser

def get_AzureGroups(tenant,id,secret,url,inquiry,):
    #Fetch Azure AD Group with Adal
    authority = "https://login.microsoftonline.com/" + tenant
    #Request Token
    context = adal.AuthenticationContext(authority)
    token = context.acquire_token_with_client_credentials(url,id,secret)
    #Create Rest Session
    SESSION = requests.Session()
    SESSION.headers.update({'Authorization': f"Bearer {token['accessToken']}",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'return-client-request-id': 'true'})
    #Return Group Array
    response = SESSION.get(url + inquiry)
    if response.status_code == 200:
        return response.json()["value"]
    else: 
        print(response.raise_for_status())
        return None
def post_EverbridgeGroups(username,password,org,groupData,groupName):
    #Convert username and password to base64
    combineString = username + ":" + password
    combineBytes = combineString.encode("utf-8")
    combineEncode = base64.b64encode(combineBytes)
    everSession = requests.Session()
    header = {'Authorization': combineEncode,
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'}
    everSession.headers.update(header)
    #Create Contact Filter to only request the groups contacts
    filterString = ""
    filterArray = []
    for contact in groupData:
        newFilter = {
        "name":contact["givenName"] + " " + contact["surname"] + "Filter",
        "contactFilterRules":[
        ]
        }
        newFilter["contactFilterRules"].append({
            "contactFieldId": 1,
            "type": "SYSTEM",
            "operator": "LIKE",
            "dataType": "STRING",
            "columnName": "firstName",
            "contactFilterOption": "LIKE",
            "columnValue": contact["givenName"]
        })
        newFilter["contactFilterRules"].append(
            {
                "contactFieldId": 2,
                "type": "SYSTEM",
                "operator": "NLIKE",
                "dataType": "STRING",
                "columnName": "lastName",
                "contactFilterOption": "LIKE",
                "columnValue": contact["surname"]
            }
        )
        #Each Filter can only have 1 full name, so a contact filter must be created for each person
        createFilter = everSession.post('https://api.everbridge.net/rest/contactFilters/' + org +'/',json.dumps(newFilter)).json()
        filterString += "&contactFilterIds=" + str(createFilter["id"])
        filterArray.append(createFilter["id"])
    #Grabs the contacts from Everbridge with the given contact filters
    everData = everSession.get('https://api.everbridge.net/rest/contacts/'+ org + '/?sortBy="lastName"&searchType=OR'+ filterString).json()
    contactList = []
    contactCheck = []
    groupBackup = []
    #Adds contact ID to Group Contact List
    for contact in everData["page"]["data"]:
        contactList.append(contact["id"])
        contactCheck.append({"name":contact["firstName"] + " " + contact["lastName"],"Id":contact["id"]})
    #Checks if a user in AD has not been added in Everbridge
    for check in contactCheck:
        for contact in groupData:
            if check["name"] == contact["givenName"] + " " + contact["surname"]:
                groupData.remove(contact)
                groupBackup.append(contact)
    #Delete Filters once they have been used
    for filterId in filterArray:
        everSession.delete('https://api.everbridge.net/rest/contactFilters/' + org + '/' + str(filterId))
    #Inserts New User to Everbridge if GroupData is not empty
    for contact in groupData:
        #Add Email as a delivery method
        paths = [
          {
            "waitTime": 0,
            "status": "A",
            "pathId": 241901148045316,
            "countryCode": "US",
            "value": contact["mail"],
            "skipValidation": "false"
          }
        ]
        if len(contact["businessPhones"]) > 0:
            #Add phone number if phone number array isn't empty
            phoneString = contact["businessPhones"][0].replace(" ","").replace("-","")
            paths.append({
                "waitTime": 0,
                "status": "A",
                "pathId": 241901148045319,
                "countryCode": "US",
                "value": phoneString,
                "skipValidation": "false"
            })
        newContact = {
            "firstName": contact["givenName"],
            "lastName": contact["surname"],
            "externalId": contact["mail"],
            "recordTypeId": 892807736729062,
            "paths":paths
        }
        newUser = everSession.post('https://api.everbridge.net/rest/contacts/' + org + '/',json.dumps(newContact)).json()
        contactList.append(newUser["id"])
    #Deletes extra users in group
    #Get all current users in group
    everGroup = everSession.get('https://api.everbridge.net/rest/contacts/groups/' + org + '?byType=name&groupName=' + groupName + '&pageSize=100&pageNumber=1').json()
    #Removes users not in the AD Group
    dataArray = everGroup["page"]["data"]
    for group in groupBackup:
        for contact in dataArray:
            if contact["firstName"] + contact["lastName"] == group["givenName"] + group["surname"]:
                dataArray.remove(contact)
    deleteList = []
    #Deletes users in Everbridge Group
    for contact in dataArray:
        deleteList.append(contact["id"])
    deleteRequests = requests.delete('https://api.everbridge.net/rest/groups/' + org + '/contacts?byType=name&groupName=' + groupName + '&idType=id',data=json.dumps(deleteList),headers=header)
    #Inserts users to group
    addContacts = everSession.post('https://api.everbridge.net/rest/groups/' + org + '/contacts?byType=name&groupName=' + groupName + '&idType=id',json.dumps(contactList)).json()    
    
if __name__ == '__main__':
    args = get_argparser().parse_args()
    config = json.load(open(args.filename))
    data = get_AzureGroups(config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/" + config["adGroup"] + "/members")
    post_EverbridgeGroups(config["everbridgeUsername"],config["everbridgePassword"],config["everbridgeOrg"],data,config["everbridgeGroup"])
