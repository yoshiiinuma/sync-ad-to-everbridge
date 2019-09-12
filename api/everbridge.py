"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import base64
import json
import logging
import requests

class Everbridge:
    """
    Handles Everbridge API requests
    """
    API_BASE = 'https://api.everbridge.net/rest/'
    API_CONTACTS = API_BASE + 'contacts/'
    API_CONTACTS_GROUPS = API_BASE + 'contacts/groups/'
    API_GROUPS = API_BASE + 'groups/'
    DEFAULT_PAGESIZE = 100

    def __init__(self, org, username, password):
        self.headers = Everbridge.create_authheader(username, password)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.org = org
        self.pagesize = Everbridge.DEFAULT_PAGESIZE

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

    def set_pagesize(self, pagesize):
        """
        Sets pagesize
        """
        self.pagesize = pagesize

    def contacts_url(self, param=None):
        """
        Returns authority URL for authentication context
        """
        url = Everbridge.API_CONTACTS +  self.org
        if param:
            url += '/' + str(param)
        return url

    def groups_url(self, param=None):
        """
        Returns authority URL for authentication context
        """
        url = Everbridge.API_GROUPS +  self.org
        if param:
            url += '/' + str(param)
        return url

    def contacts_groups_url(self, param=None):
        """
        Returns authority URL for authentication context
        """
        url = Everbridge.API_CONTACTS_GROUPS +  self.org
        if param:
            url += '/' + str(param)
        return url

    def update_header(self, header):
        """
        Updates header
        """
        self.headers = header

    def post(self, url, data):
        """
        Sends POST HTTP request
        """
        try:
            resp = requests.post(url, json=json.dumps(data), headers=self.headers)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def delete(self, url, data=None):
        """
        Sends DELETE HTTP request
        """
        try:
            if data:
                resp = self.session.delete(url, json=json.dumps(data))
            else:
                resp = self.session.delete(url)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def get(self, url, data=None):
        """
        Sends GET HTTP request
        """
        try:
            if data:
                resp = self.session.get(url, json=json.dumps(data))
            else:
                resp = self.session.get(url)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def put(self, url, data):
        """
        Sends PUT HTTP request
        """
        try:
            resp = self.session.put(url, json=json.dumps(data))
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    #def update_contacts(self, contacts):
    #    """
    #    Updates contacts paths
    #    ?updateType determines to fully update all contact fields or certain feilds
    #    ?idType determines to search by id or externalId
    #    """
    #    url = self.contacts_url("batch?idType=id&updateType=partial")
    #    return self.put(url, data=contacts)

    #def get_filtered_contacts(self, filter_string):
    #    """
    #    Gets a list of contacts from Everbridge
    #    """
    #    url = self.contacts_url('?sortBy="lastName"&searchType=OR' + filter_string)
    #    return self.get(url)

    def insert_new_contacts(self, contacts):
        """
        Inserts new contacts to everbridge org
        ?Version determines the batch API for insert values are 0 or 1
        """
        url = self.contacts_url("batch?version=1")
        return self.post(url, data=contacts)

    #def get_group(self, group_id, page):
    #    """
    #    Gets Everbridge group contact
    #    ?idType determines to get the group by id or name
    #    """
    #    #params = '?byType=id&groupId='+ str(group_id) + '&pageSize=100&pageNumber=' + str(page)
    #    params = f"?byType=id&groupId={group_id}&pageSize={self.pagesize}&pageNumber={page}"
    #    url = self.contacts_groups_url(params)
    #    return self.get(url)

    def get_all_groups(self, page=1):
        """
        Gets Everbridge group contact
        ?idType determines to get the group by id or name
        """
        params = f"?pageSize={self.pagesize}&pageNumber={page}"
        url = self.groups_url(params)
        res = self.get(url)
        if 'page' in res and 'data' in res['page']:
            return res['page']['data']
        logging.error('EVERBRIDGE.GET_ALL_GROUP: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_ALL_GROUP: Unexpected Response')

    #def get_group_by_id(self, gid):
    #    """
    #    Gets Everbridge group by id
    #    """
    #    url = self.groups_url(f"/{gid}")
    #    res = self.get(url)
    #    if 'result' in res:
    #        return res['result']
    #    logging.error('EVERBRIDGE.GET_GROUP_BY_ID: Unexpected Response')
    #    logging.error(res)
    #    raise Exception('EVERBRIDGE.GET_GROUP_BY_ID: Unexpected Response')

    def get_group_by_name(self, name):
        """
        Gets Everbridge group by name
        queryType: id|name; default id
        """
        params = f"/{name}?queryType=name"
        url = self.groups_url(params)
        res = self.get(url)
        if 'result' in res:
            return res['result']
        logging.error('EVERBRIDGE.GET_GROUP_BY_NAME: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_BY_NAME: Unexpected Response')

    def get_group_id_by_name(self, name):
        """
        Gets Everbridge group id by group name
        """
        res = self.get_group_by_name(name)
        if 'id' in res:
            return res['id']
        logging.error('EVERBRIDGE.GET_GROUP_ID_BY_NAME: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_ID_BY_NAME: Unexpected Response')

    def get_paged_group_members(self, group_id, page):
        """
        Gets Everbridge group members that are ordered by email
        """
        params = f"?groupIds={group_id}&pageSize={self.pagesize}&pageNumber={page}"
        params += "&sortBy=externalId&direction=ASC"
        url = self.contacts_url(params)
        res = self.get(url)
        if 'page' in res and 'data' in res['page']:
            return res['page']['data']
        logging.error('EVERBRIDGE.GET_GROUP_MEMBERS: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_MEMBERS: Unexpected Response')

    def delete_contacts_from_group(self, group_id, members):
        """
        Deletes extra users in group
        ?idType determines to delete by id or externalId
        """
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = self.groups_url(params)
        return self.delete(url, data=members)

    def delete_contacts_from_org(self, contacts):
        """
        Deletes users from the org if they don't belong in a group
        """
        return self.delete(self.contacts_url("batch"), data=contacts)

    def add_contacts_to_group(self, group_id, members):
        """
        Inserts contacts into everbridge group
        ?byType add everbridge contacts to group by name or id
        """
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = self.groups_url(params)
        return self.post(url, data=members)

    def add_group(self, group_name):
        """
        Inserts new group into everbridge
        """
        data = {"name":group_name, "organizationId":self.org}
        return self.post(self.groups_url(''), data=data)

    #def get_group_info(self, group_name):
    #    """
    #    Gets Group Info from Everbidge
    #    ?queryType searches by name or group Id
    #    """
    #    params = group_name + "?queryType=name"
    #    return self.get(self.groups_url(params))

    def delete_group(self, group_id):
        """
        Deletes Group from Everbridge
        ?queryType searches by name or group Id
        """
        return self.delete(self.groups_url(group_id))
