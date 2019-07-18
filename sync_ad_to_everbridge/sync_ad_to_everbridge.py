#Requests Client Crediential Token and then performs API call to get Login Events
import adal
import requests
import json
import base64
import argparse
import logging
import os
from datetime import datetime
from requests.exceptions import HTTPError
LOG_FILENAME = datetime.now().strftime(os.getcwd() + '/logs/logfile_%H_%M_%S_%d_%m_%Y.log')
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)    
def get_Argparser():
    #Build argument parser.
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    parser.add_argument('--logfile', help="logfile for program", default=None)
    return parser
#Get Azure AD Token
def create_AuthHeader(username, password):

    combineString = username + ":" + password
    combineBytes = combineString.encode("utf-8")
    combineEncode = base64.b64encode(combineBytes)
    header = {'Authorization': combineEncode,
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'}
    return header
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
#REST API Calls to Everbridge
def delete_Everbridge(url,header,data):
    resp = requests.delete(url, data=json.dumps(data), headers=header)
    resp.raise_for_status()
    return resp.json()
def post_Everbridge(url,header,data):
    resp = requests.post(url, data=json.dumps(data),headers=header)
    resp.raise_for_status()
    return resp.json()
def get_EverBridge(url,header,data):
    resp = requests.get(url, data=json.dumps(data),headers=header)
    resp.raise_for_status()
    return resp.json()
def create_filter(firstName,lastName,url,header):
    #Create New Filter that will have the contact's full name as the criteria
    logging.info("Creating search filter for " + firstName + " " + lastName)
    newFilter = {
        "name":firstName + " " + lastName + "Filter",
        #Inserts 2 rules that matches on the contacts firstname and lastname
        "contactFilterRules":[
            {
                "contactFieldId": 1,
                "type": "SYSTEM",
                "operator": "LIKE",
                "dataType": "STRING",
                "columnName": "firstName",
                "contactFilterOption": "LIKE",
                "columnValue":firstName
            },
             {
                "contactFieldId": 2,
                "type": "SYSTEM",
                "operator": "NLIKE",
                "dataType": "STRING",
                "columnName": "lastName",
                "contactFilterOption": "LIKE",
                "columnValue": lastName
            }
        ]
    }
    #Create POST Request to insert new Filter
    return post_Everbridge(url,header,newFilter)
def create_user(firstName,lastName,phone,email,url,header):
    logging.info("Creating new Everbridge Contact for " + firstName + " " + lastName)
    #Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    paths = [
        #Add Email to Delivery Method
        {
        "waitTime": 0,
        "status": "A",
        "pathId": 241901148045316,
        "countryCode": "US",
        "value": email,
        "skipValidation": "false"
        }
    ]
    if len(phone) > 0:
        #Add phone number if phone number array isn't empty
        phoneString = phone[0].replace(" ","").replace("-","")
        paths.append({
            "waitTime": 0,
            "status": "A",
            "pathId": 241901148045319,
            "countryCode": "US",
            "value": phoneString,
            "skipValidation": "false"
        })
    #Base info for Contact
    newContact = {
        "firstName": firstName,
        "lastName": lastName,
        "externalId": email,
        "recordTypeId": 892807736729062,
        "paths":paths
    }
    #Do POST Request to insert User
    return post_Everbridge(url, header, newContact)
def get_EverContacts(filterString, header, org):
    #Get a list of contacts from Everbridge
    return get_EverBridge('https://api.everbridge.net/rest/contacts/'+ org + '/?sortBy="lastName"&searchType=OR'+ filterString,header,None)
def create_query(filterArray,groupData,org,header):
    filterString = ""
    for contact in groupData:
    #Each Filter can only have 1 full name, so a contact filter must be created for each person
        filterData = create_filter(contact["givenName"],contact["surname"],'https://api.everbridge.net/rest/contactFilters/' + org +'/',header)
        filterString += "&contactFilterIds=" + str(filterData["id"])
        filterArray.append(filterData["id"])
    return filterString
def create_EverContacts(contactList, contactCheck,groupData, groupBackup, everData, org, header):
    #Adds contact ID to Group Contact List
    for contact in everData["page"]["data"]:
        logging.info("Adding " + contact["firstName"] + " " + contact["lastName"] + "to Everbridge group")
        contactList.append(contact["id"])
        contactCheck.append({"name":contact["firstName"] + " " + contact["lastName"],"Id":contact["id"]})
    #Checks if a user in AD has not been added in Everbridge
    for check in contactCheck:
        for contact in groupData:
            if check["name"] == contact["givenName"] + " " + contact["surname"]:
                groupData.remove(contact)
                groupBackup.append(contact)
    #Inserts New User to Everbridge if GroupData is not empty
    for contact in groupData:
        newUser = create_user(contact["givenName"],contact["surname"],contact["businessPhones"],contact["mail"],'https://api.everbridge.net/rest/contacts/' + org + '/',header)
        contactList.append(newUser["id"])
def delete_EverContacts(org,groupName,header,groupBackup):
    #Deletes extra users in group
    #Get all current users in group
    everGroup = get_EverBridge('https://api.everbridge.net/rest/contacts/groups/' + org + '?byType=name&groupName=' + groupName + '&pageSize=100&pageNumber=1',header,None)
    #Removes users not in the AD Group
    if(everGroup["page"]["totalCount"] > 0):
        dataArray = everGroup["page"]["data"]
        for group in groupBackup:
            for contact in dataArray:
                if contact["firstName"] + contact["lastName"] == group["givenName"] + group["surname"]:
                    dataArray.remove(contact)
        deleteList = []
        #Deletes users in Everbridge Group
        for contact in dataArray:
            logging.info("Deleting contact " + contact["firstName"] + " " + contact["lastName"] + "from Everbridge Group " + groupName)
            deleteList.append(contact["id"])
        if(len(deleteList) > 0):
            deleteRequests = delete_Everbridge('https://api.everbridge.net/rest/groups/' + org + '/contacts?byType=name&groupName=' + groupName + '&idType=id',header,deleteList)
def add_contacts(org,groupName,header,contactList):
    post_Everbridge('https://api.everbridge.net/rest/groups/' + org + '/contacts?byType=name&groupName=' + groupName + '&idType=id',header,contactList)   
def sync_EverbridgeGroups(username,password,org,groupData,groupName):
    if len(groupData) < 1 or len(username) < 10 or len(password) < 8 or len(org) < 10 or len(groupName) < 1:
        return None
    #Convert username and password to base64
    header = create_AuthHeader(username,password)
    #Create the search query for the group Everbridge Contacts
    filterArray = []
    filterString = create_query(filterArray, groupData,org,header)
    #Grabs the contacts from Everbridge with the given contact filters
    everData = get_EverContacts(filterString, header, org)
    #Delete Filters once they have been used
    logging.info("Deleting Search Filters")
    for filterId in filterArray:
        delete_Everbridge('https://api.everbridge.net/rest/contactFilters/' + org + '/' + str(filterId),header,None) 
    contactList = []
    contactCheck = []
    groupBackup = []
    #Create new contacts
    create_EverContacts(contactList,contactCheck,groupData,groupBackup,everData,org,header)
    #Delete extra users in group
    delete_EverContacts(org,groupName,header,groupBackup)
    #Inserts users to group
    add_contacts(org,groupName,header,contactList)
if __name__ == '__main__':
    args = get_Argparser().parse_args()
    logging.info("Program Start")
    config = json.load(open(args.filename))
    data = get_AzureGroups("https://login.microsoftonline.com/",
        config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],config["adGroupId"])
    sync_EverbridgeGroups(config["everbridgeUsername"],config["everbridgePassword"],config["everbridgeOrg"],data,config["everbridgeGroup"])
