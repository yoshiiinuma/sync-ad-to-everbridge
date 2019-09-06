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
def check_group(group_name, Session):
    """
    Checks if everbridge group exists and inserts new group if not
    Raises error if invalid header or org id
    Converts Group_name to Group_ID for group delete function
    """
    group_info = Session.get_group_info(group_name)
    if group_info["message"] == "OK":
        if group_info["result"]["id"] == 0:
            new_group = Session.add_group(group_name)
            logging.info("Creating new Everbridge Group %s", group_name)
            return new_group["id"]
        else:
            return group_info["result"]["id"]
    elif group_info.get("status") is not None and group_info["status"] == 401:
        logging.error(group_info["message"])
        raise ValueError
def check_contact(contact, content_check):
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
        if (content_check["workPhone"] == '' or
                (content_check["workPhone"] != '' and
                 str(phone_string) !=
                 str(content_check["workPhone"]["value"]))):
            need_to_update = 1
    #Checks External ID
    if contact["userPrincipalName"] != content_check["mail"]:
        need_to_update = 1
    #Checks Mobile Phone
    if ((contact.get("mobilePhone") is not None and
         content_check["mobilePhone"] == '') or
            contact.get("mobilePhone") is not None and
                re.sub(r'-|\s|\(|\)|\+1', '', contact["mobilePhone"]) !=
                content_check["mobilePhone"]["value"]):
        need_to_update = 1
    #Creates Contact Object to be sent
    return need_to_update
def create_contact(contact, ever_id):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
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
    https://api.everbridge.net/rest/recordTypes/org
    """
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
        logging.warning("%s has no first/last name. Adding in placeholder", contact["displayName"])
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
        logging.warning("%s has no email. Adding in placeholder", contact["displayName"])
        contact["userPrincipalName"] = "missingmail" + contact["givenName"] +"@hawaii.gov"
    elif contact.get("userPrincipalName") is None and contact["mail"] is not None:
        contact["userPrincipalName"] = contact["mail"]
    else:
        contact["mail"] = contact["userPrincipalName"]
    if contact.get("businessPhones") is None:
        logging.warning("%s has no phone", contact["displayName"])
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
def parse_ad_data(group_data, contact_check):
    """
    Checks AD group against Everbrige dictionary to add in new contacts
    """
    #Checks if a user in AD has not been added in Everbridge
    copy_list = group_data.copy()
    group_backup = {}
    update_list = []
    for contact in copy_list:
        fill_contact(contact)
        if contact_check.get(contact["mail"]) is not None:
            #Updates contacts that have different properties from their AD infromation
            if check_contact(contact, contact_check[contact["mail"]]) == 1:
                contact_updater = create_contact(contact, contact_check[contact["mail"]]["Id"])
                update_list.append(contact_updater)
            group_data.remove(contact)
            group_backup[contact["mail"]] = contact
    return group_backup, update_list
def parse_ever_data(ever_data):
    """
    Add everbridge ids to group batch insert and check dictionary
    """
    contact_check = {}
    contact_list = []
    for contact in ever_data["page"]["data"]:
        contact_list.append(contact["id"])
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
        contact_check[contact["externalId"]] = ever_contact
    return contact_check, contact_list
def create_evercontacts(group_data,
                        contact_list,
                        Session):
    """
    Checks AD group against filtered query and adds new contacts
    """
    #Adds contact ID to Group Contact List
    #Inserts New User to Everbridge if group_data is not empty
    batch_insert = []
    count = 0
    if group_data:
        new_query = create_query(group_data)
        for contact in group_data:
            new_user = create_contact(contact, None)
            batch_insert.append(new_user)
        Session.insert_new_contacts(batch_insert)
        new_contacts = Session.get_filtered_contacts(new_query)
        for contact in new_contacts["page"]["data"]:
            contact_list.append(contact["id"])
        count = len(new_contacts)
    return count
def delete_evercontacts(group_id, group_backup, Session):
    """
    Deletes extra users in group
    """
    delete_count = 0
    #Get all current users in group
    ever_group = Session.get_everbridge_group(group_id)
    #Removes users not in the AD Group
    if ever_group["page"]["totalCount"] > 0:
        remove_list = []
        delete_list = []
        data_array = ever_group["page"]["data"]
        copy_array = data_array.copy()
        for contact in copy_array:
            full_name = contact["externalId"]
            if group_backup.get(full_name) is not None:
                data_array.remove(contact)
            else:
                if len(contact["groups"]) == 1:
                    remove_list.append(contact["id"])
                delete_list.append(contact["id"])
        #Deletes users in Everbridge Group
        if delete_list:
            Session.delete_contacts_from_group(group_id, delete_list)
            delete_count = len(delete_list)
            #Deletes a group if there is no members in the group
            if ever_group["page"]["totalCount"] - delete_count == 0:
                Session.delete_group(group_id)
                logging.info("Deleting Everbridge Group")
                return -1
        #Deletes users from the org if the user doesn't belong to the group
        if remove_list:
            Session.delete_contacts_from_org(remove_list)
            logging.info("Removing %s Everbridge Contacts from org" , len(remove_list))
    return delete_count
def sync_everbridge_group(username, password, org, group_data, group_name):
    """
    Main Function
    """
    if (username, password, org, group_name) is None or not group_data:
        logging.error('sync_everbridge_group: Invalid Parameter')
        raise Exception('Async_everbridge_group: Invalid parameter')
    #Convert username and password to base64
    contact_list = []
    contact_check = {}
    header = create_authheader(username, password)
    Session = SESSION(org, header)
    #Checks to see if group exists in Everbridge Org
    group_id = check_group(group_name, Session)
    #Create the search query for the group Everbridge Contacts
    #Grabs the contacts from Everbridge with the given contact filters
    ever_data = Session.get_filtered_contacts(create_query(group_data))
    #Parse Everbridge Data to filter contacts
    #Contact List = parse_ever_data[1]
    if ever_data["page"].get("data") is not None:
        contact_check = parse_ever_data(ever_data)[0]
        contact_list = parse_ever_data(ever_data)[1]
    group_backup = parse_ad_data(group_data, contact_check)[0]
    update_list = parse_ad_data(group_data, contact_check)[1]
    #Create new contacts
    insert_count = create_evercontacts(group_data, contact_list, Session)
    #Delete extra users in group
    delete_count = delete_evercontacts(group_id, group_backup, Session)
    #Updates Everbridge Contacts
    if update_list:
        Session.update_contacts(update_list)
    #Inserts users to group
    
    logging.info("%s contacts created,%s users removed from group, %s users upserted to the group",
                 insert_count,
                 delete_count,
                 len(contact_list))
    if delete_count != -1:
        return Session.add_contacts_to_group(group_id, contact_list)
    else:
        return "Group has been deleted"
