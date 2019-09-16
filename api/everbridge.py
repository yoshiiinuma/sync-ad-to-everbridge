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

    def show(self):
        """
        Prints internal variables
        """
        print(self.headers)
        print(self.org)

    def _post(self, url, data):
        """
        Sends POST HTTP request
        """
        try:
            resp = self.session.post(url, json=data)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def _delete(self, url, data=None):
        """
        Sends DELETE HTTP request
        """
        try:
            if data:
                resp = self.session.delete(url, json=data)
            else:
                resp = self.session.delete(url)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def _get(self, url, data=None):
        """
        Sends GET HTTP request
        """
        try:
            if data:
                resp = self.session.get(url, json=data)
            else:
                resp = self.session.get(url)
            return resp.json()
        except Exception as error:
            logging.error(error)
            raise error

    def _put(self, url, data):
        """
        Sends PUT HTTP request
        """
        try:
            resp = self.session.put(url, json=data)
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
    #    return self._put(url, data=contacts)

    def get_contacts_by_external_ids(self, external_ids):
        """
        Gets a list of contacts from Everbridge
        """
        if not external_ids:
            raise Exception('EVERBRIDGE.GET_CONTACTS_BY_EXTERNAL_IDS: No External IDs Provided')
        url = self.contacts_url('?sortBy=externalId&direction=ASC&searchType=AND' + external_ids)
        res = self._get(url)
        print(res)
        if 'page' in res and 'data' in res['page']:
            return res['page']['data']
        logging.error('EVERBRIDGE.GET_CONTACTS_BY_EXTERNAL_IDS: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_CONTACTS_BY_EXTERNAL_IDS: Unexpected Response')

    def upsert_contacts(self, contacts):
        """
        Upserts contacts to everbridge org
        ?Version determines the batch API for insert values are 0 or 1
        """
        if not contacts:
            raise Exception('EVERBRIDGE.UPSERT_CONTACTS: No Contacts Provided')
        # TODO MAX contacts 1000
        url = self.contacts_url("batch?version=1")
        return self._post(url, data=contacts)

    def delete_contacts(self, contacts):
        """
        Deletes users from the org if they don't belong in a group
        """
        if not contacts:
            raise Exception('EVERBRIDGE.DELETE_CONTACTS: No Contacts Provided')
        return self._delete(self.contacts_url("batch"), data=contacts)

    #def get_group(self, group_id, page):
    #    """
    #    Gets Everbridge group contact
    #    ?idType determines to get the group by id or name
    #    """
    #    #params = '?byType=id&groupId='+ str(group_id) + '&pageSize=100&pageNumber=' + str(page)
    #    params = f"?byType=id&groupId={group_id}&pageSize={self.pagesize}&pageNumber={page}"
    #    url = self.contacts_groups_url(params)
    #    return self._get(url)

    def get_all_groups(self, page=1):
        """
        Gets Everbridge group contact
        ?idType determines to get the group by id or name
        """
        params = f"?pageSize={self.pagesize}&pageNumber={page}"
        url = self.groups_url(params)
        res = self._get(url)
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
    #    res = self._get(url)
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
        if not name:
            raise Exception('EVERBRIDGE.GET_GROUP_BY_NAME: No GroupName Provided')
        params = f"/{name}?queryType=name"
        url = self.groups_url(params)
        res = self._get(url)
        if 'result' in res:
            return res['result']
        logging.error('EVERBRIDGE.GET_GROUP_BY_NAME: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_BY_NAME: Unexpected Response')

    def get_group_id_by_name(self, name):
        """
        Gets Everbridge group id by group name
        """
        if not name:
            raise Exception('EVERBRIDGE.GET_GROUP_ID_BY_NAME: No GroupName Provided')
        res = self.get_group_by_name(name)
        if 'id' in res:
            return res['id']
        logging.error('EVERBRIDGE.GET_GROUP_ID_BY_NAME: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_ID_BY_NAME: Unexpected Response')

    def get_paged_group_members(self, group_id, page=1):
        """
        Gets Everbridge group members that are ordered by email
        """
        if not group_id:
            raise Exception('EVERBRIDGE.GET_PAGED_GROUP_MEMBERS: No Group ID Provided')
        params = f"?groupIds={group_id}&pageSize={self.pagesize}&pageNumber={page}"
        params += "&sortBy=externalId&direction=ASC"
        url = self.contacts_url(params)
        res = self._get(url)
        if 'page' in res and 'data' in res['page']:
            return res['page']['data']
        logging.error('EVERBRIDGE.GET_GROUP_MEMBERS: Unexpected Response')
        logging.error(res)
        raise Exception('EVERBRIDGE.GET_GROUP_MEMBERS: Unexpected Response')

    def delete_members_from_group(self, group_id, members):
        """
        Deletes extra users in group
        ?idType determines to delete by id or externalId
        """
        if not group_id:
            raise Exception('EVERBRIDGE.DELETE_MEMBERS_FROM_GROUP: No Group ID Provided')
        if not members:
            raise Exception('EVERBRIDGE.DELETE_MEMBERS_FROM_GROUP: No Members Provided')
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = self.groups_url(params)
        return self._delete(url, data=members)

    def add_members_to_group(self, group_id, members):
        """
        Inserts contacts into everbridge group
        ?byType add everbridge contacts to group by name or id
        """
        if not group_id:
            raise Exception('EVERBRIDGE.ADD_MEMBERS_TO_GROUP: No Group ID Provided')
        if not members:
            raise Exception('EVERBRIDGE.ADD_MEMBERS_TO_GROUP: No Members Provided')
        params = 'contacts?byType=id&groupId=' + str(group_id) + '&idType=id'
        url = self.groups_url(params)
        return self._post(url, data=members)

    def add_group(self, group_name):
        """
        Inserts new group into everbridge
        """
        if not group_name:
            raise Exception('EVERBRIDGE.ADD_GROUP: No Group Name Provided')
        data = {'name': group_name, 'organizationId': self.org}
        rslt = self._post(self.groups_url(''), data=data)
        if not rslt or 'message' not in rslt or rslt['message'] != 'OK':
            logging.error('EVERBRIDGE.ADD_GROUP: Unexpected Response')
            logging.error(rslt)
            raise Exception('EVERBRIDGE.ADD_GROUP: Failed')
        return rslt

    def delete_group(self, group_id):
        """
        Deletes Group from Everbridge
        ?queryType searches by name or group Id
        """
        if not group_id:
            raise Exception('EVERBRIDGE.DELETE_GROUP: No Group ID Provided')
        return self._delete(self.groups_url(group_id))
