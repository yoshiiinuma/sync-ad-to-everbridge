"""
Logic to handle the Everbridge Contacts
"""
import base64
import re
import logging
from .everbridge_api import SESSION
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
def check_contact(contact, update_list, first, last):
    """
    Checks AD contact data with everbridge contact data and updates if mismatched
    """
    need_to_update = 0
    # Checks Work Desk Phone
    if contact["businessPhones"]:
       
        phone_string = contact["businessPhones"][0]
        phone_string = re.sub(r'-|\s|\(|\)|\+1', '', phone_string)
        if len(phone_string) == 7:
            phone_string = "808" + phone_string
        if (update_list["contact_check"][first + last]["workPhone"] == '' or
                (update_list["contact_check"][first + last]["workPhone"] != '' and
                 int(phone_string) !=
                 int(update_list["contact_check"][first + last]["workPhone"]["value"]))):
            need_to_update = 1
    #Checks External ID
    if contact["userPrincipalName"] != update_list["contact_check"][first + last]["mail"]:
        need_to_update = 1
    #Checks Mobile Phone
    
    if ((contact.get("mobilePhone") is not None and
         update_list["contact_check"][first + last]["mobilePhone"] == '') or
            contact.get("mobilePhone") is not None and
                re.sub(r'-|\s|\(|\)|\+1', '', contact["mobilePhone"]) != 
                    update_list["contact_check"][first + last]["mobilePhone"]["value"]):
        need_to_update = 1
    #Creates Contact Object to be sent
    if need_to_update == 1:
        updated_contact = create_contact(contact, update_list["contact_check"][first + last]["Id"])
        update_list["updated_users"].append(updated_contact)
def create_contact(contact, ever_id):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    """

    """
    Contact Paths are the delivery methods for notifications in Everbridge. 
    Contact Paths can not be created or deleted through the API.
    To view paths in the org, go to Settings -> Notifications -> Delivery Methods
    https://api.everbridge.net/rest/contactPaths/org
    """
    paths = [
        #Add Email Contact Path to the new contact
        {
            "waitTime": 0,
            "status": "A",
            "pathId": 241901148045316,
            "value": contact["userPrincipalName"],
            "skipValidation": "false"
        }
    ]
    if contact["businessPhones"]:
        for phone_number in contact["businessPhones"]:
            phone_string = phone_number
            re.sub(r'-|\s|\(|\)|\+1', '', phone_string)
            if len(phone_string) == 7:
                phone_string = "808" + phone_string
            if len(phone_string) >= 10:
                #Add phone number if phone number array isn't empty
                #Adds Work Desk Phone Path to contact
                paths.append(
                    {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": phone_string,
                        "skipValidation": "false"
                    })
    #Adds Work Cell Path to contact if mobile phone number is present
    if contact.get("mobilePhone") is not None:
        phone_string = contact["mobilePhone"].replace(" ", "").replace("-", "")
        paths.append(
            {
                "waitTime": 0,
                "status": "A",
                "pathId": 241901148045319,
                "countryCode": "US",
                "value": phone_string,
                "skipValidation": "false"
            })
        #Adds Work Cell SMS Path to contact
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
    """
    Record Types are required for contact creation.
    Record Types allow the org to categorize employees.
    The static Record Type Id is the default "Employee" record type.
    There is only 1 record type in the org but more can be added.
    To manage Record Types, go to Settings -> Contacts and Groups-> Contact Record Types.
    """
    # https://api.everbridge.net/rest/recordTypes/org
    new_contact = {
        "firstName": contact["givenName"],
        "lastName": contact["surname"],
        "externalId": contact["userPrincipalName"],
        "recordTypeId": 892807736729062,
        "paths":paths
    }
    #For Creating Put Request Contact
    if ever_id is not None:
        new_contact["id"] = ever_id
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
        logging.warning(contact["displayName"] + "has no first/last name. Adding in placeholder")
        if len(space_array) > 1:
            first = space_array[0]
            space_array.pop(0)
            last = "".join(str(x) for x in space_array)
        else:
            first = contact["displayName"]
            last = "None"
        contact["givenName"] = first
        contact["surname"] = last
    if contact.get("userPrincipalName") is None and contact["mail"] is None:
        logging.warning(contact["displayName"] + " has no email. Adding in placeholder")
        contact["userPrincipalName"] = "missingmail" + contact["givenName"] +"@hawaii.gov"
    elif contact.get("userPrincipalName") is None and contact["mail"] is not None:
        contact["userPrincipalName"] = contact["mail"]
    if contact.get("businessPhones") is None:
        logging.warning(contact["displayName"] + "has no phone")
        contact["businessPhones"] = []
def create_query(group_data):
    """
    Create query using externalId
    """
    filter_string = ""
    #Fills in missing fields in the Microsoft AD Member info
    for contact in group_data:
        fill_contact(contact)
        filter_string += "&externalIds=" + contact["userPrincipalName"]
    return filter_string
def parse_ad_data(group_data, update_list):
    """
    Checks AD group against Everbrige dictionary to add in new contacts
    """
    #Checks if a user in AD has not been added in Everbridge
    copy_list = group_data.copy()
    for contact in copy_list:
        fill_contact(contact)
        if update_list["contact_check"].get(str(contact["givenName"])
                                            + str(contact["surname"])) is not None:
            #Updates contacts that have different properties from their AD infromation
            check_contact(contact, update_list, contact["givenName"], contact["surname"])
            group_data.remove(contact)
            update_list["group_backup"][str(contact["givenName"])
                                        + str(contact["surname"])] = contact
def parse_ever_data(ever_data, update_list):
    """
    Add everbridge ids to group batch insert and check dictionary
    """
    for contact in ever_data["page"]["data"]:
        update_list["contact_list"].append(contact["id"])
        ever_contact = {"name":contact["firstName"]
                               + " " + contact["lastName"],
                        "Id":contact["id"],
                        "mobilePhone":"",
                        "workPhone":"",
                        "mail":contact["externalId"]}
        if len(contact["paths"]) > 1 and contact["paths"][1]["pathId"] == 241901148045321:
            ever_contact["workPhone"] = contact["paths"][1]
        if len(contact["paths"]) > 2:
            ever_contact["mobilePhone"] = contact["paths"][2]
        update_list["contact_check"][str(contact["firstName"])
                                     + str(contact["lastName"])] = ever_contact
def create_evercontacts(group_data,
                        ever_data,
                        Session):
    """
    Checks AD group against filtered query and adds new contacts
    """
    #Adds contact ID to Group Contact List
    update_list = {"contact_list":[],
                   "contact_check":{},
                   "group_backup":{},
                   "new_users":0,
                   "updated_users":[]}
    if ever_data["page"].get("data") is not None:
        parse_ever_data(ever_data, update_list)
    parse_ad_data(group_data, update_list)
    #Inserts New User to Everbridge if group_data is not empty
    batch_insert = []
    if group_data:
        new_query = create_query(group_data)
        for contact in group_data:
            new_user = create_contact(contact, None)
            batch_insert.append(new_user)
        Session.insert_new_contacts(batch_insert)
        new_contacts = Session.get_filtered_contacts(new_query)
        update_list["new_users"] = len(group_data)
        for contact in new_contacts["page"]["data"]:
            update_list["contact_list"].append(contact["id"])
    return update_list
def delete_evercontacts(group_name,group_backup, Session):
    """
    Deletes extra users in group
    """
    delete_count = 0
    #Get all current users in group
    ever_group = Session.get_everbridge_group(group_name)
    #Removes users not in the AD Group
    if ever_group["page"]["totalCount"] > 0:
        remove_list = []
        data_array = ever_group["page"]["data"]
        copy_array = data_array.copy()
        for contact in copy_array:
            full_name = contact["firstName"] + contact["lastName"]
            if group_backup.get(full_name) is not None:
                data_array.remove(contact)
            else:
                if len(contact["groups"]) == 1:
                    remove_list.append(contact["id"])
                    data_array.remove(contact)
        delete_list = data_array
        #Deletes users in Everbridge Group
        if delete_list:
            Session.delete_contacts_from_group(group_name, delete_list)
            delete_count = len(delete_list)
        if remove_list:
            Session.delete_contacts_from_org(remove_list)
    return delete_count
def sync_everbridge_group(username, password, org, group_data, group_name):
    """
    Main Function
    """
    if (username, password, org, group_name) is None or not group_data:
        logging.error('sync_everbridge_group: Invalid Parameter')
        raise Exception('Async_everbridge_group: Invalid parameter')
    #Convert username and password to base64
    header = create_authheader(username, password)
    Session = SESSION(org,header)
    #Create the search query for the group Everbridge Contacts
    filter_string = create_query(group_data)
    #Grabs the contacts from Everbridge with the given contact filters
    ever_data = Session.get_filtered_contacts(filter_string)
    #Create new contacts
    update_list = create_evercontacts(group_data,
                                      ever_data, Session)
    #Delete extra users in group
    delete_count = delete_evercontacts(group_name, update_list["group_backup"], Session)
    #Updates Everbridge Contacts
    if update_list["updated_users"]:
        Session.update_contacts(update_list["updated_users"])
    #Inserts users to group
    Session.add_contacts_to_group(group_name,update_list["contact_list"])
    logging.info("%s contacts created,%s users removed from group, %s users upserted to the group",
                 update_list["new_users"],
                 delete_count,
                 len(update_list["contact_list"]))
    return group_name + " has been synced"
