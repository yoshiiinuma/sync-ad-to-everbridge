"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import json
import logging
import sys
import requests
class URL():
    """
    Define URL constants
    """
    LOGIN = 'https://api.everbridge.net/rest/'
    API_CONTACTS = 'contacts/'
    API_CONTACTS_GROUPS = 'contacts/groups/'
    API_GROUPS = 'groups/'
    @staticmethod
    def contacts_url(org, param):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + URL.API_CONTACTS +  org + '/' + param
    @staticmethod
    def groups_url(org, param):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + URL.API_CONTACTS +  org + '/' + param
    @staticmethod
    def contacts_groups_url(org, param):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + URL.API_CONTACTS_GROUPS +  org + '/' + param
def delete_everbridge(url, header, data):
    """
    Delete HTTP Call for everbridge
    """
    try:
        resp = requests.delete(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        raise error
def post_everbridge(url, header, data):
    """
    POST HTTP Call for Everbridge
    """
    try:
        resp = requests.post(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        raise error
def get_everbridge(url, header, data):
    """
    GET HTTP Call for Everbridge
    """
    try:
        resp = requests.get(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        raise error
def put_everbridge(url, header, data):
    """
    PUT HTTP Call for Everbridge
    """
    try:
        resp = requests.put(url, data=json.dumps(data), headers=header)
        return resp.json()
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        logging.error(error)
        raise error
def update_contacts(update_list, header, org):
    """
    Update contacts paths
    """
    return put_everbridge(URL.contacts_url(org,"batch?idType=id&updateType=partial"),
                          header, update_list)
def get_filtered_contacts(filter_string, header, org):
    """
    Get a list of contacts from Everbridge
    """
    return get_everbridge(URL.contacts_url(org,'?sortBy="lastName"&searchType=OR' + filter_string),
                          header, None)
def insert_new_contacts(batch_insert, org, header):
    """
    Inserts new contacts to everbridge org
    """
    return post_everbridge(URL.contacts_url(org, "batch?version=1"),
                    header,
                    batch_insert)
def get_everbridge_group(org, group_name, header):
    """
    Gets Everbridge group contact
    """
    group_data = get_everbridge(URL.contacts_groups_url(org, '?byType=name&groupName='+ group_name + '&pageSize=100&pageNumber=1'),
                                header, None)
    return group_data
def delete_contacts_from_group(org, group_name, header, delete_list):
    """
    Deletes extra users in group
    """
    delete_everbridge(URL.groups_url(org,'contacts?byType=name&groupName=' + group_name + '&idType=id'),
                      header, delete_list)
def delete_contacts_from_org(org, group_name, header, remove_list):
    """
    Deletes users from the org if they don't belong in a group
    """
    delete_everbridge(URL.contacts_url(org, "batch"), header, remove_list)
def add_contacts_to_group(org, group_name, header, contact_list):
    """
    Inserts contacts into everbridge group
    """
    return post_everbridge(URL.groups_url(org,'contacts?byType=name&groupName=' + group_name+ '&idType=id'),
                           header, contact_list)
