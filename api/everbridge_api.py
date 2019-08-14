"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import json
import logging
import sys
import requests
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
def put_everbridge(url, header, data):
    """
    PUT HTTP Call for Everbridge
    """
    try:
        resp = requests.put(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        sys.exit(1)
def update_contacts(update_list, header, org):
    """
    Update contacts paths
    """
    return put_everbridge('https://api.everbridge.net/rest/contacts/'+ org
                          +"/batch?idType=id&updateType=partial",
                          header, update_list)
def get_filtered_contacts(filter_string, header, org):
    """
    Get a list of contacts from Everbridge
    """
    return get_everbridge('https://api.everbridge.net/rest/contacts/'+ org
                          +'/?sortBy="lastName"&searchType=OR'+ filter_string,
                          header, None)
def insert_new_contacts(batch_insert, org, header):
    """
    Updates Everbridge group
    """
    return post_everbridge("https://api.everbridge.net/rest/contacts/" + org + "/batch?version=1",
                    header,
                    batch_insert)
def get_everbridge_group(org, group_name, header):
    """
    Gets Everbridge group contact
    """
    group_data = get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                + org + '?byType=name&groupName='
                                + group_name + '&pageSize=100&pageNumber=1',
                                header, None)
    return group_data
def delete_contacts_from_group(org, group_name, header, delete_list):
    """
    Deletes extra users in group
    """
    delete_everbridge('https://api.everbridge.net/rest/groups/'
                      + org + '/contacts?byType=name&groupName='
                      + group_name + '&idType=id', header, delete_list)
def delete_contacts_from_org(org, group_name, header, remove_list):
    """
    Deletes users from the org if they don't belong in a group
    """
    delete_everbridge('https://api.everbridge.net/rest/contacts/'
                        + org + '/batch', header, remove_list)
def add_contacts_to_group(org, group_name, header, contact_list):
    """
    Inserts contacts into everbridge group
    """
    return post_everbridge('https://api.everbridge.net/rest/groups/' + org
                    + '/contacts?byType=name&groupName=' + group_name
                    + '&idType=id', header, contact_list)
