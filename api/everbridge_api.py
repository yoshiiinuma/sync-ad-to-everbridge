"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import json
import base64
import logging
import requests
def create_authheader(username, password):
    """
    Creates Header for HTTP CALLS, Creates base64 encode for auth
    """
    combine_string = username + ":" + password
    combine_bytes = combine_string.encode("utf-8")
    combine_encode = base64.b64encode(combine_bytes)
    header = {'Authorization': combine_encode,
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'return-client-request-id': 'true'}
    return header
def delete_everbridge(url, header, data):
    """
    Delete HTTP Call for everbridge
    """
    resp = requests.delete(url, data=json.dumps(data), headers=header)
    resp.raise_for_status()
    return resp.json()
def post_everbridge(url, header, data):
    """
    POST HTTP Call for Everbridge
    """
    resp = requests.post(url, data=json.dumps(data), headers=header)
    resp.raise_for_status()
    return resp.json()
def get_everbridge(url, header, data):
    """
    GET HTTP Call for Everbridge
    """
    print(url)
    resp = requests.get(url, data=json.dumps(data), headers=header)
    resp.raise_for_status()
    return resp.json()
def create_filter(first_name, last_name, url, header):
    """
    Create New Filter that will have the contact's full name as the criteria
    """
    logging.info("Creating search filter for " + first_name + " " + last_name)
    new_filter = {
        "name":first_name + " " + last_name + "Filter",
        #Inserts 2 rules that matches on the contacts firstName and lastName
        "contactFilterRules":[
            {
                "contactFieldId": 1,
                "type": "SYSTEM",
                "operator": "LIKE",
                "dataType": "STRING",
                "columnName": "firstName",
                "contactFilterOption": "LIKE",
                "columnValue":first_name
            },
            {
                "contactFieldId": 2,
                "type": "SYSTEM",
                "operator": "NLIKE",
                "dataType": "STRING",
                "columnName": "lastName",
                "contactFilterOption": "LIKE",
                "columnValue": last_name
            }
        ]
    }
    #Create POST Request to insert new Filter
    return post_everbridge(url, header, new_filter)
def create_user(first_name, last_name, phone, email, url, header):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    """
    logging.info("Creating new Everbridge Contact for " + first_name + " " + last_name)
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
    if phone:
        for phone_number in phone:
            #Add phone number if phone number array isn't empty
            phone_string = phone_number.replace(" ", "").replace("-", "")
            paths.append(
                {
                    "waitTime": 0,
                    "status": "A",
                    "pathId": 241901148045319,
                    "countryCode": "US",
                    "value": phone_string,
                    "skipValidation": "false"
                })
    #Base info for Contact
    new_contact = {
        "firstName": first_name,
        "lastName": last_name,
        "externalId": email,
        "recordTypeId": 892807736729062,
        "paths":paths
    }
    #Do POST Request to insert User
    return post_everbridge(url, header, new_contact)
def get_evercontacts(filter_string, header, org):
    """
    Get a list of contacts from Everbridge
    """
    return get_everbridge('https://api.everbridge.net/rest/contacts/'+ org
                          +'/?sortBy="lastName"&searchType=OR'+ filter_string,
                          header, None)
def create_query(filter_array, group_data, org, header):
    """
    Create query using multiple contact filters
    """
    filter_string = ""
    for contact in group_data:
    #Each Filter can only have 1 full name, so a contact filter must be created for each person
        filter_data = create_filter(contact["givenName"], contact["surname"],
                                    'https://api.everbridge.net/rest/contactFilters/'
                                    + org +'/', header)
        filter_string += "&contactFilterIds=" + str(filter_data["id"])
        filter_array.append(filter_data["id"])
    return filter_string
def create_evercontacts(contact_list,
                        contact_check,
                        group_data,
                        group_backup,
                        ever_data,
                        org,
                        header):
    """
    Updates Everbridge group
    """
    #Adds contact ID to Group Contact List
    for contact in ever_data["page"]["data"]:
        logging.info("Adding %s %s to Everbridge group", contact["firstName"], contact["lastName"])
        contact_list.append(contact["id"])
        contact_check.append({"name":contact["firstName"]
                                     + " " + contact["lastName"], "Id":contact["id"]})
    #Checks if a user in AD has not been added in Everbridge
    for check in contact_check:
        for contact in group_data:
            if check["name"] == contact["givenName"] + " " + contact["surname"]:
                group_data.remove(contact)
                group_backup.append(contact)
    #Inserts New User to Everbridge if group_data is not empty
    for contact in group_data:
        new_user = create_user(contact["givenName"],
                               contact["surname"],
                               contact["businessPhones"],
                               contact["mail"],
                               'https://api.everbridge.net/rest/contacts/' + org + '/', header)
        contact_list.append(new_user["id"])
def delete_evercontacts(org, group_name, header, group_backup):
    """
    Deletes extra users in group
    """
    #Get all current users in group
    ever_group = get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                + org + '?byType=name&groupName='
                                + group_name + '&pageSize=100&pageNumber=1',
                                header, None)
    #Removes users not in the AD Group
    if ever_group["page"]["totalCount"] is not None:
        data_array = ever_group["page"]["data"]
        for group in group_backup:
            for contact in data_array:
                full_name = contact["firstName"] + contact["lastName"]
                if full_name == group["givenName"] + group["surname"]:
                    data_array.remove(contact)
        delete_list = []
        #Deletes users in Everbridge Group
        for contact in data_array:
            logging.info("Deleting contact "
                         + contact["firstName"]
                         + " "
                         + contact["lastName"]
                         + " from Everbridge Group "
                         + group_name)
            delete_list.append(contact["id"])
        if delete_list:
            delete_everbridge('https://api.everbridge.net/rest/groups/'
                              + org + '/contacts?byType=name&groupName='
                              + group_name + '&idType=id', header, delete_list)
def add_contacts(org, group_name, header, contact_list):
    """
    Inserts contacts into everbridge group
    """
    post_everbridge('https://api.everbridge.net/rest/groups/' + org
                    + '/contacts?byType=name&groupName=' + group_name
                    + '&idType=id', header, contact_list)
def sync_everbridgegroups(username, password, org, group_data, group_name):
    """
    Main Function
    """
    if (group_data, username, password, org, group_name) is None:
        return None
    #Convert username and password to base64
    header = create_authheader(username, password)
    #Create the search query for the group Everbridge Contacts
    filter_array = []
    filter_string = create_query(filter_array, group_data, org, header)
    #Grabs the contacts from Everbridge with the given contact filters
    ever_data = get_evercontacts(filter_string, header, org)
    print(ever_data["page"]["totalCount"])
    #Delete Filters once they have been used
    logging.info("Deleting Search Filters")

    for filter_id in filter_array:
        delete_everbridge('https://api.everbridge.net/rest/contactFilters/' + org
                          + '/' + str(filter_id), header, None)
    logging.info("Done Deleting Search Filters")
    contact_list = []
    contact_check = []
    group_backup = []
    #Create new contacts
    create_evercontacts(contact_list,
                        contact_check,
                        group_data,
                        group_backup,
                        ever_data, org, header)
    #Delete extra users in group
    #Inserts users to group
    add_contacts(org, group_name, header, contact_list)
    delete_evercontacts(org, group_name, header, group_backup)
    return group_name + " has been synced"
