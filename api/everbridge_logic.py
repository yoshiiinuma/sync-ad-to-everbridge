"""
Logic to handle the Everbridge Contacts
"""
import base64
import re
import logging
from .everbridge_api import Session
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
def check_group(group_name, session):
    """
    Checks if everbridge group exists and inserts new group if not
    Raises error if invalid header or org id
    Converts Group_name to Group_ID for group delete function
    """
    group_info = session.get_group_info(group_name)
    if group_info["message"] == "OK":
        if group_info["result"]["id"] == 0:
            new_group = session.add_group(group_name)
            logging.info("Creating new Everbridge Group %s", group_name)
            return new_group["id"]
        return group_info["result"]["id"]
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
    # Checks External ID
    if contact["userPrincipalName"] != content_check["mail"]:
        need_to_update = 1
    # Checks Mobile Phone
    if ((contact.get("mobilePhone") is not None and
         content_check["mobilePhone"] == '') or
            contact.get("mobilePhone") is not None and
                re.sub(r'-|\s|\(|\)|\+1', '', contact["mobilePhone"]) !=
                content_check["mobilePhone"]["value"]):
        need_to_update = 1
    # Creates Contact Object to be sent
    return need_to_update
def create_contact(contact, ever_id):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    Contact Paths are the delivery methods for notifications in Everbridge.
    Contact Paths can not be created or deleted through the API.
    To view paths in the org, go to Settings -> Notifications -> Delivery Methods
    """
    paths = [
        # Add Email Contact Path to the new contact
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
                # Add phone number if phone number array isn't empty
                # Adds Work Desk Phone Path to contact
                paths.append(
                    {
                        "waitTime": 0,
                        "status": "A",
                        "pathId": 241901148045321,
                        "countryCode": "US",
                        "value": phone_string,
                        "skipValidation": "false"
                    })
    # Adds Work Cell Path to contact if mobile phone number is present
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
        # Adds Work Cell SMS Path to contact
        paths.append(
            {
                "waitTime": 0,
                "status": "A",
                "pathId": 241901148045324,
                "countryCode": "US",
                "value": phone_string,
                "skipValidation": "false"
            })
    # Record Types allow the org to categorize employees.
    # The static Record Type Id is the default "Employee" record type.
    # To manage Record Types, go to Settings -> Contacts and Groups-> Contact Record Types.
    new_contact = {
        "firstName": contact["givenName"],
        "lastName": contact["surname"],
        "externalId": contact["userPrincipalName"],
        "recordTypeId": 892807736729062,
        "paths":paths
    }
    # For Creating Put Request Contact
    if ever_id is not None:
        new_contact["id"] = ever_id
    # Do POST Request to insert User
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
    filter_string_list = []
    filter_string = ""
    # Fills in missing fields in the Microsoft AD Member info
    count = 0
    total_count = 0
    for contact in group_data:
        fill_contact(contact)
        filter_string += "&externalIds=" + contact["userPrincipalName"]
        count+= 1
        total_count += 1
        if count == 99 or total_count - len(group_data) == 0:
            filter_string_list.append(filter_string)
            count = 0
            filter_string = ""
    return filter_string_list
def parse_ad_data(group_data, contact_check):
    """
    Checks AD group against Everbrige dictionary to add in new contacts
    """
    # Checks if a user in AD has not been added in Everbridge
    copy_list = group_data.copy()
    group_backup = {}
    update_list = []
    for contact in copy_list:
        fill_contact(contact)
        if contact_check.get(contact["mail"]) is not None:
            # Updates contacts that have different properties from their AD infromation
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
    if not ever_data:
        return contact_check, contact_list
    for contact in ever_data:
        contact_list.append(contact['id'])
        ever_contact = {"name":contact["firstName"]
                               + " " + contact["lastName"],
                        "Id":contact['id'],
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
                        session):
    """
    Checks AD group against filtered query and adds new contacts
    """
    # Adds contact ID to Group Contact List
    # Inserts New User to Everbridge if group_data is not empty
    batch_insert = []
    count = 0
    if group_data:
        new_queries = create_query(group_data)
        for contact in group_data:
            new_user = create_contact(contact, None)
            batch_insert.append(new_user)
        session.insert_new_contacts(batch_insert)
        new_contacts = []
        #Will do multiple queries in batches of 100 if size is over 100
        for query in new_queries:
            query_data = session.get_filtered_contacts(query)
            if query_data["page"].get("data") is not None:
                new_contacts = new_contacts + query_data["page"]["data"]
        if new_contacts:
            for contact in new_contacts:
                contact_list.append(contact['id'])
            count = len(new_contacts)
    return count
def delete_evercontacts(group_id, group_backup, session):
    """
    Deletes extra users in group
    """
    delete_count = 0
    # Get all current users in group
    page_number = 0
    ever_group = []
    #Does multiple queries if group size is greater than 100
    ever_group_data = session.get_everbridge_group(group_id, 1)
    if ever_group_data["page"].get("data") is not None:
        ever_group = ever_group + ever_group_data["page"]["data"]
    if ever_group_data["page"]["totalPageCount"] > 1:
        page_number = ever_group_data["page"]["totalPageCount"]
        for page in range(1,page_number):
            ever_group_data = session.get_everbridge_group(group_id, page)
            ever_group = ever_group + ever_group_data["page"]["data"]
    # Removes users not in the AD Group
    if ever_group:
        remove_list = []
        delete_list = []
        data_array = ever_group
        copy_array = data_array.copy()
        for contact in copy_array:
            full_name = contact["externalId"]
            if group_backup.get(full_name) is not None:
                data_array.remove(contact)
            else:
                if len(contact["groups"]) == 1:
                    remove_list.append(contact['id'])
                delete_list.append(contact['id'])
        # Deletes users in Everbridge Group
        if delete_list:
            #print(delete_list)
            session.delete_contacts_from_group(group_id, delete_list)
            # Deletes a group if there is no members in the group
            if len(ever_group) - len(delete_list) == 0:
                #session.delete_group(group_id)
                logging.info("Deleting Everbridge Group")
                return -1
        # Deletes users from the org if the user doesn't belong to the group
        if remove_list:
            session.delete_contacts_from_org(remove_list)
            logging.info("Removing %s Everbridge Contacts from org", len(remove_list))
    return delete_count
def sync_everbridge_group(username, password, org, group_data, group_name):
    """
    Main Function
    """
    if (username, password, org, group_name) is None or not group_data:
        logging.error('sync_everbridge_group: Invalid Parameter')
        raise Exception('Async_everbridge_group: Invalid parameter')
    # Convert username and password to base64
    session = Session(org, create_authheader(username, password))
    # Checks to see if group exists in Everbridge Org
    group_id = check_group(group_name, session)
    # Create the search query for the group Everbridge Contacts
    # Grabs the contacts from Everbridge with the given contact filters  
    queries = create_query(group_data)
    #Will do multiple queries in batches of 100 if size is over 100
    ever_data = []
    for query in queries:
        get_contact = session.get_filtered_contacts(query)
        if get_contact["page"].get("data") is not None:
            ever_data = ever_data + get_contact["page"]["data"]
    # Parse Everbridge Data to filter contacts
    parsed_ever_data = parse_ever_data(ever_data)
    contact_list = parsed_ever_data[1]
    parsed_group_data = parse_ad_data(group_data, parsed_ever_data[0])
    # Create new contacts
    insert_count = create_evercontacts(group_data, contact_list, session)
    # Delete extra users in group
    delete_count = delete_evercontacts(group_id, parsed_group_data[0], session)
    # Updates Everbridge Contacts
    if parsed_group_data[1]:
        session.update_contacts(parsed_group_data[1])
    # Inserts users to group
    logging.info("%s contacts created,%s users removed from group, %s users upserted to the group",
                 insert_count,
                 delete_count,
                 len(contact_list))
    if delete_count != -1:
        return session.add_contacts_to_group(group_id, contact_list)
    return "Group has been deleted"
