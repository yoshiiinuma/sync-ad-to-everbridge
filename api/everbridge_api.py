"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import json
import logging
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
        return URL.LOGIN + URL.API_GROUPS +  org + '/' + param
    @staticmethod
    def contacts_groups_url(org, param):
        """
        Returns authority URL for authentication context
        """
        return URL.LOGIN + URL.API_CONTACTS_GROUPS +  org + '/' + param
class Session:
    """
    Session for Everbridge
    """
    def __init__(self, org, header):
        self.headers = header
        self.s = requests.Session()
        self.s.headers.update(header)
        self.org = org
    def update_header(self, header):
        """
        Updates header
        """
        self.headers = header
    def post(self, url, data):
        """
        Post HTTP Call for everbridge
        """
        try:
            resp = requests.post(url, json=data, headers=self.headers)
            return resp.json()
        except requests.exceptions.RequestException as error:
            logging.error(error)
            raise error
    def delete(self, url, data):
        """
        Delete HTTP Call for everbridge
        """
        try:
            resp = self.s.delete(url, data=json.dumps(data))
            return resp.json()
        except requests.exceptions.RequestException as error:
            logging.error(error)
            raise error
    def get(self, url, data):
        """
        GET HTTP Call for everbridge
        """
        try:
            resp = self.s.get(url, json=json.dumps(data))
            return resp.json()
        except requests.exceptions.RequestException as error:
            logging.error(error)
            raise error
    def put(self, url, data):
        """
        PUT HTTP Call for everbridge
        """
        try:
            resp = self.s.put(url, json=data)
            return resp.json()
        except requests.exceptions.RequestException as error:
            logging.error(error)
            raise error
    def update_contacts(self, update_list):
        """
        Update contacts paths
        ?updateType determines to fully update all contact fields or certain feilds
        ?idType determines to search by id or externalId
        """
        return self.put(URL.contacts_url(self.org, "batch?idType=id&updateType=partial"),
                        update_list)
    def get_filtered_contacts(self, filter_string):
        """
        Get a list of contacts from Everbridge
        """
        return self.get(URL.contacts_url(self.org, '?sortBy="lastName"&searchType=OR'
                                         + filter_string),
                        None)
    def insert_new_contacts(self, batch_insert):
        """
        Inserts new contacts to everbridge org
        ?Version determines the batch API for insert values are 0 or 1
        """
        return self.post(URL.contacts_url(self.org, "batch?version=1"),
                         batch_insert)
    def get_everbridge_group(self, group_id, page_number):
        """
        Gets Everbridge group contact
        ?idType determines to get the group by id or name
        """
        return self.get(URL.contacts_groups_url(self.org, '?byType=id&groupId='+ str(group_id)
                                                + '&pageSize=100&pageNumber=' + str(page_number)), None)
    def delete_contacts_from_group(self, group_id, delete_list):
        """
        Deletes extra users in group
        ?idType determines to delete by id or externalId
        """
        return self.delete(URL.groups_url(self.org, 'contacts?byType=id&groupId=' + str(group_id)
                                          + '&idType=id'),
                           delete_list)
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
        return self.s.post(URL.groups_url(self.org, 'contacts?byType=id&groupId='
                                          + str(group_id)+ '&idType=id'),
                           data=json.dumps(contact_list)).json()
    def add_group(self, group_name):
        """
        Inserts new group into everbridge
        """
        return self.s.post(URL.groups_url(self.org, ''),
                           data=json.dumps({"name":group_name,
                                            "organizationId":self.org})).json()
    def get_group_info(self, group_name):
        """
        Gets Group Info from Everbidge
        ?queryType searches by name or group Id
        """
        return self.s.get(URL.groups_url(self.org, group_name + "?queryType=name")).json()
    def delete_group(self, group_id):
        """
        Deletes Group from Everbridge
        ?queryType searches by name or group Id
        """
        return self.s.delete(URL.groups_url(self.org, str(group_id))).json()
