"""
Logic to handle the Everbridge Contacts
"""
import base64
import logging
from .everbridge_api import get_filtered_contacts, insert_new_contacts, get_everbridge_group, delete_contacts_from_group, add_contacts_to_group
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
def create_contact(contact):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    """
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
                #Work Desk Phone Path
                paths.append(
                    {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": phone_string,
                        "skipValidation": "false"
                    })
    #Adds Cell phone to paths if mobile phone number is present
    if contact["mobilePhone"] is not None:
        phone_string = contact["mobilePhone"].replace(" ", "").replace("-", "")
        #Work Cell Path
        paths.append(
            {
                "waitTime": 0,
                "status": "A",
                "pathId": 241901148045319,
                "countryCode": "US",
                "value": phone_string,
                "skipValidation": "false"
            })
        #Work Cell SMS Path
        paths.append(
            {
                "waitTime": 0,
                "status": "A",
                "pathId": 241901148045324,
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
    return new_contact
def fill_contact(contact):
    """
    Fill missing info in AD Contact
    """
    if contact.get("givenName") is None:
        first = "first"
        last = "last"
        space_array = contact["displayName"].split(" ")
        if len(space_array) > 1:
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
def create_query(group_data):
    """
    Create query using externalId
    """
    filter_string = ""
    #Fills in missing fields in the Microsoft AD Member info
    for contact in group_data:
        fill_contact(contact)
        filter_string += "&externalIds=" + contact["mail"]
    return filter_string
def create_evercontacts(group_data,
                        ever_data,
                        org,
                        header):
    """
    Checks AD group against filtered query and adds new contacts
    """
    #Adds contact ID to Group Contact List
    update_list = {"contact_list":[],
                   "contact_check":{},
                   "group_backup":{}}
    if ever_data["page"].get("data") is not None:
        for contact in ever_data["page"]["data"]:
            key_name = str(contact["firstName"]) + str(contact["lastName"])
            update_list["contact_list"].append(contact["id"])
            update_list["contact_check"][key_name] = {"name":contact["firstName"]
                                                             + " " + contact["lastName"],
                                                      "Id":contact["id"]}
    #Checks if a user in AD has not been added in Everbridge
    copy_list = group_data.copy()
    for contact in copy_list:
        #Special case if contact has no first or last name
        if contact.get("givenName") is None:
            first = "first"
            last = "last"
            space_array = contact["displayName"].split(" ")
            if len(space_array) > 1:
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
            if update_list["contact_check"].get(str(contact["givenName"])
                                                + str(contact["surname"])) is not None:
                group_data.remove(contact)
                update_list["group_backup"][str(contact["givenName"])
                                            + str(contact["surname"])] = contact
    #Inserts New User to Everbridge if group_data is not empty
    batch_insert = []
    if len(group_data) > 0:
        new_query = create_query(group_data)
        for contact in group_data:
            new_user = create_contact(contact)
            batch_insert.append(new_user)
        insert_new_contacts(batch_insert, org, header)
        new_contacts = get_filtered_contacts(new_query, header, org)
        for contact in new_contacts["page"]["data"]:
            update_list["contact_list"].append(contact["id"])
    return update_list
def delete_evercontacts(org, group_name, header, group_backup):
    """
    Deletes extra users in group
    """
    #Get all current users in group
    ever_group = get_everbridge_group(org, group_name, header)
    #Removes users not in the AD Group
    if ever_group["page"]["totalCount"] > 0:
        data_array = ever_group["page"]["data"]
        copy_array = data_array.copy()
        for contact in copy_array:
            full_name = contact["firstName"] + contact["lastName"]
            if group_backup.get(full_name) is not None:
                data_array.remove(contact)
        delete_list = data_array
        #Deletes users in Everbridge Group
        if len(delete_list) > 0:
            delete_contacts_from_group(org, group_name, header, delete_list)
def sync_everbridgegroups(username, password, org, group_data, group_name):
    """
    Main Function
    """
    if (group_data, username, password, org, group_name) is None:
        return None
    #Convert username and password to base64
    header = create_authheader(username, password)
    #Create the search query for the group Everbridge Contacts
    filter_string = create_query(group_data)
    #Grabs the contacts from Everbridge with the given contact filters
    ever_data = get_filtered_contacts(filter_string, header, org)
    #Create new contacts
    update_list = create_evercontacts(group_data,
                                      ever_data, org, header)
    #Delete extra users in group
    delete_evercontacts(org, group_name, header, update_list["group_backup"])
    #Inserts users to group
    add_contacts_to_group(org, group_name, header, update_list["contact_list"])
    return group_name + " has been synced"
