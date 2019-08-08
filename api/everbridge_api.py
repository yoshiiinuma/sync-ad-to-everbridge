"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import json
import base64
import logging
import sys
import requests
#Counts of the update
class STATEMENT:
    """
    Counter for the end program statement
    """
    def __init__(self, new, delete, update):
        self.new = new
        self.delete = delete
        self.update = update
    def statement(self):
        """
        Return statement string
        """
        return self.update + self.delete + self.new
    def reset(self):
        """
        Reset counter
        """
        self.new = 0
        self.update = 0
        self.delete = 0
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
    try:
        resp = requests.delete(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        sys.exit(1)
def post_everbridge(url, header, data):
    """
    POST HTTP Call for Everbridge
    """
    try:
        resp = requests.post(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        sys.exit(1)
def get_everbridge(url, header, data):
    """
    GET HTTP Call for Everbridge
    """
    try:
        resp = requests.get(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        sys.exit(1)
def create_filter(first_name, last_name, url, header):
    """
    Create New Filter that will have the contact's full name as the criteria
    """
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
                "operator": "LIKE",
                "dataType": "STRING",
                "columnName": "lastName",
                "contactFilterOption": "LIKE",
                "columnValue": last_name
            }
        ]
    }
    #Create POST Request to insert new Filter
    return post_everbridge(url, header, new_filter)
def create_user(contact, url, header, counter):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    """
    counter.new = counter.new + 1
    if contact.get("givenName") is None:
        first = "first"
        last = "last"
        space_array = contact["displayName"].split(" ")
        if(len(space_array) > 1):
            first = space_array[0]
            space_array.pop(0)
            last = "".join(str(x) for x in space_array)
        else:
            first = contact["displayName"]
            last = "None"
        contact["givenName"] = first
        contact["surname"] = last
    if contact["mail"] is None:
        contact["mail"] = "missingmail" + contact["givenName"] +"@hawaii.gov"
    if contact.get("businessPhones") is None:
        contact["businessPhones"] = []
    paths = [
        #Add Email to Delivery Method
        {
            "waitTime": 0,
            "status": "A",
            "pathId": 241901148045316,
            "countryCode": "US",
            "value": contact["mail"],
            "skipValidation": "false"
        }
    ]
    if contact["businessPhones"]:
        for phone_number in contact["businessPhones"]:
            if len(phone_number) >= 10:
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
        "firstName": contact["givenName"],
        "lastName": contact["surname"],
        "externalId": contact["mail"],
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
def create_query( group_data, org, header):
    """
    Create query using multiple contact filters
    """
    filter_string = ""
    for contact in group_data:
    #Each Filter can only have 1 full name, so a contact filter must be created for each person
        if contact.get("givenName") is None:
            space_array = contact["displayName"].split(" ")
            if(len(space_array) > 1):
                contact["givenName"] = space_array[0]
                space_array.pop(0)
                contact["surname"] = "".join(str(x) for x in space_array)
            else:
                contact["givenName"] = contact["displayName"]
                contact["surname"] = "None"
        filter_data = get_everbridge("https://api.everbridge.net/rest/contactFilters/" + org + "/"+ contact["givenName"] + " " + contact["surname"] + "filter" + "?queryType=name",header,{})
        if filter_data["result"]["id"] == 0:
            filter_data = create_filter(contact["givenName"], contact["surname"],
                                        'https://api.everbridge.net/rest/contactFilters/'
                                        + org +'/', header)
            filter_string += "&contactFilterIds=" + str(filter_data["id"])
        else:
            filter_string += "&contactFilterIds=" + str(filter_data["result"]["id"])
    return filter_string
def create_evercontacts(group_data,
                        ever_data,
                        org,
                        header,
                        counter):
    """
    Updates Everbridge group
    """
    #Adds contact ID to Group Contact List
    update_list = {"contact_list":[],
                   "contact_check":{},
                   "group_backup":{}}
    if(ever_data["page"].get("data") is not None):
        for contact in ever_data["page"]["data"]:
            key_name = str(contact["firstName"]) + str(contact["lastName"])
            update_list["contact_list"].append(contact["id"])
            counter.update = counter.update + 1
            update_list["contact_check"][key_name] = {"name":contact["firstName"]
                                                        + " " + contact["lastName"],
                                                "Id":contact["id"]}
    #Checks if a user in AD has not been added in Everbridge
    copy_list = group_data.copy()
    for contact in copy_list:
        if contact.get("givenName") is None:
            first = "first"
            last = "last"
            space_array = contact["displayName"].split(" ")
            if(len(space_array) > 1):
                first = space_array[0]
                space_array.pop(0)
                last = "".join(str(x) for x in space_array)
            else:
                first = contact["displayName"]
                last = "None"
            if update_list["contact_check"].get(first + last) is not None:
                group_data.remove(contact)
                update_list["group_backup"][first + last] = contact
        else:
            if update_list["contact_check"].get(str(contact["givenName"]) + str(contact["surname"])) is not None:
                group_data.remove(contact)
                update_list["group_backup"][str(contact["givenName"]) + str(contact["surname"])] = contact
    #Inserts New User to Everbridge if group_data is not empty
    for contact in group_data:
        new_user = create_user(contact,
                               'https://api.everbridge.net/rest/contacts/'
                               + org + '/', header, counter)
        print(new_user)
        update_list["contact_list"].append(new_user["id"])
    return update_list
def delete_evercontacts(org, group_name, header, group_backup, counter):
    """
    Deletes extra users in group
    """
    #Get all current users in group
    ever_group = get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                + org + '?byType=name&groupName='
                                + group_name + '&pageSize=100&pageNumber=1',
                                header, None)
    #Removes users not in the AD Group
    if ever_group["page"]["totalCount"] > 0:
        data_array = ever_group["page"]["data"]
        for contact in data_array:
            full_name = contact["firstName"] + contact["lastName"]
            if group_backup.get(full_name) is not None:
                data_array.remove(contact)
        delete_list = []
        #Deletes users in Everbridge Group
        for contact in data_array:
            counter.delete = counter.delete + 1
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
    counter = STATEMENT(0, 0, 0)
    if (group_data, username, password, org, group_name) is None:
        return None
    #Convert username and password to base64
    header = create_authheader(username, password)
    #Create the search query for the group Everbridge Contacts
    #filter_string = create_query(group_data, org, header)
    #Grabs the contacts from Everbridge with the given contact filters
    filter_string = "&contactFilterIds=350903123051033&contactFilterIds=350765684097592&contactFilterIds=350628245144126&contactFilterIds=350765684097593&contactFilterIds=351040562004613&contactFilterIds=351040562004614&contactFilterIds=351178000958043&contactFilterIds=350765684097594&contactFilterIds=350903123051034&contactFilterIds=350490806190563&contactFilterIds=350628245144127&contactFilterIds=350903123051035&contactFilterIds=350765684097595&contactFilterIds=351178000958044&contactFilterIds=351178000958045&contactFilterIds=351040562004615&contactFilterIds=350765684097596&contactFilterIds=351178000958046&contactFilterIds=350628245144128&contactFilterIds=350765684097597&contactFilterIds=350628245144129&contactFilterIds=350903123051036&contactFilterIds=350490806190564&contactFilterIds=351040562004616&contactFilterIds=350628245144130&contactFilterIds=350490806190565&contactFilterIds=350765684097598&contactFilterIds=350903123051037&contactFilterIds=350765684097599&contactFilterIds=351178000958047&contactFilterIds=351040562004617&contactFilterIds=350490806190566&contactFilterIds=351178000958048&contactFilterIds=350903123051038&contactFilterIds=350903123051039&contactFilterIds=351040562004618&contactFilterIds=350765684097600&contactFilterIds=350903123051040&contactFilterIds=351040562004619&contactFilterIds=350490806190567&contactFilterIds=350628245144131&contactFilterIds=351040562004620&contactFilterIds=350628245144132&contactFilterIds=351040562004621&contactFilterIds=350765684097601&contactFilterIds=350490806190568&contactFilterIds=350628245144133&contactFilterIds=351178000958049&contactFilterIds=350765684097602&contactFilterIds=350628245144134&contactFilterIds=351040562004622&contactFilterIds=351178000958050&contactFilterIds=350903123051041&contactFilterIds=350765684097603&contactFilterIds=351040562004623&contactFilterIds=350628245144135&contactFilterIds=350628245144136&contactFilterIds=351178000958051&contactFilterIds=351040562004624&contactFilterIds=350628245144137&contactFilterIds=351178000958052&contactFilterIds=350903123051042&contactFilterIds=350765684097604&contactFilterIds=350628245144138&contactFilterIds=351178000958053&contactFilterIds=350490806190569&contactFilterIds=351040562004625&contactFilterIds=351178000958054&contactFilterIds=351040562004626&contactFilterIds=350490806190570&contactFilterIds=350765684097606"
    ever_data = get_evercontacts(filter_string, header, org)
    #Create new contacts
    update_list = create_evercontacts(group_data,
                                      ever_data, org, header,
                                      counter)
    #Delete extra users in group
    delete_evercontacts(org, group_name, header, update_list["group_backup"], counter)
    #Inserts users to group
    add_contacts(org, group_name, header, update_list["contact_list"])
    logging.info("%s contacts created,%s users removed from group, %s users upserted to the group",
                 counter.new,
                 counter.delete,
                 counter.update)
    return group_name + " has been synced"
