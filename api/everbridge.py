"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import base64
import json
import logging
import requests

class URL():
    """
    Defines URL constants
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
        return URL.LOGIN + URL.API_GROUPS +  org + '/' + param

    @staticmethod
    def contacts_groups_url(org, param):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + URL.API_CONTACTS_GROUPS +  org + '/' + param

class Everbridge:
    """
    Handles Everbridge API requests
    """
    def __init__(self, org, username, password):
        self.headers = Everbridge.create_authheader(username, password)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.org = org

    @staticmethod
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

    def update_header(self, header):
        """
        Updates header
        """
        self.headers = header

    def post(self, url, data):
        """
        Sends Post HTTP request
        """
        try:
            resp = requests.post(url, json=data, headers=self.headers)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def delete(self, url, data):
        """
        Sends Delete HTTP request
        """
        try:
            resp = self.session.delete(url, data=json.dumps(data))
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def get(self, url, data):
        """
        Sends GET HTTP request
        """
        try:
            resp = self.session.get(url, json=json.dumps(data))
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def put(self, url, data):
        """
        Sends PUT HTTP request
        """
        try:
            resp = self.session.put(url, json=data)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def update_contacts(self, update_list):
        """
        Update contacts paths
        ?updateType determines to fully update all contact fields or certain feilds
        ?idType determines to search by id or externalId
        """
        url = URL.contacts_url(self.org, "batch?idType=id&updateType=partial")
        return self.put(url, update_list)

    def get_filtered_contacts(self, filter_string):
        """
        Get a list of contacts from Everbridge
        """
        url = URL.contacts_url(self.org, '?sortBy="lastName"&searchType=OR' + filter_string)
        return self.get(url, None)

    def insert_new_contacts(self, batch_insert):
        """
        Inserts new contacts to everbridge org
        ?Version determines the batch API for insert values are 0 or 1
        """
        url = URL.contacts_url(self.org, "batch?version=1")
        return self.post(url, batch_insert)

    def get_everbridge_group(self, group_id):
        """
        Gets Everbridge group contact
        ?idType determines to get the group by id or name
        """
        params = '?byType=id&groupId='+ str(group_id) + '&pageSize=100&pageNumber=1'
        url = URL.contacts_groups_url(self.org, params)
        return self.get(url, None)

    def delete_contacts_from_group(self, group_id, delete_list):
        """
        Deletes extra users in group
        ?idType determines to delete by id or externalId
        """
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = URL.groups_url(self.org, params)
        return self.delete(url, delete_list)

    def delete_contacts_from_org(self, remove_list):
        """
        Deletes users from the org if they don't belong in a group
        """
        return self.delete(URL.contacts_url(self.org, "batch"), remove_list)

    def add_contacts_to_group(self, group_id, contact_list):
        """
        Inserts contacts into everbridge group
        ?byType add everbridge contacts to group by name or id
        """
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = URL.groups_url(self.org, params)
        return self.session.post(url, data=json.dumps(contact_list)).json()

    def add_group(self, group_name):
        """
        Inserts new group into everbridge
        """
        data = json.dumps({"name":group_name, "organizationId":self.org})
        return self.session.post(URL.groups_url(self.org, ''), data=data).json()

    def get_group_info(self, group_name):
        """
        Gets Group Info from Everbidge
        ?queryType searches by name or group Id
        """
        params = group_name + "?queryType=name"
        return self.session.get(URL.groups_url(self.org, params)).json()

    def delete_group(self, group_id):
        """
        Deletes Group from Everbridge
        ?queryType searches by name or group Id
        """
        return self.session.delete(URL.groups_url(self.org, str(group_id))).json()
