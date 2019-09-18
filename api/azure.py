"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal
class Azure:
    """
    Handles Azure Graph API requests
    """
    LOGIN = 'https://login.microsoftonline.com/'
    API_BASE = 'https://graph.microsoft.com/'
    API_GROUPS = API_BASE + 'v1.0/groups/'
    DEFAULT_PAGESIZE = 100

    def __init__(self, client_id, secret, tenant):
        self.client_id = client_id
        self.secret = secret
        self.tenant = tenant
        self.token = None
        self.pagesize = Azure.DEFAULT_PAGESIZE

    def setup(self):
        """
        Sets up token if it is empty; Must be called onece before any API calls
        """
        if not self.token:
            self.reset_token()

    def check_token(self):
        """
        Raises an Exception if token is not set
        """
        if not self.token or not self.token['accessToken']:
            logging.error('AZURE.API.get_group_name: Invalid Token')
            raise Exception('AZURE.API.get_group_name: Invalid Token')

    def reset_token(self):
        """
        Resets token
        """
        self.set_token(self.get_token())

    def get_token(self):
        """
        Gets Azure AD Token
        """
        if not self.client_id or not self.secret or not self.tenant:
            logging.error('AZURE.API.get_token: Invalid Parameter')
            raise Exception('AZURE.API.get_token: Invalid parameter')
        context = adal.AuthenticationContext(self.authority_url())
        try:
            token = context.acquire_token_with_client_credentials(
                Azure.API_BASE, self.client_id, self.secret)
            return token
        except Exception as err:
            logging.error(err)
            raise err

    def set_token(self, token):
        """
        Sets Azure AD Token to the internal variable
        """
        self.token = token

    def set_pagesize(self, pagesize):
        """
        Setter for pagesize
        """
        self.pagesize = pagesize

    def authority_url(self):
        """
        Returns authority URL for authentication context
        """
        return Azure.LOGIN + self.tenant

    # pylint: disable=no-self-use
    def group_members_url(self, group_id):
        """
        Returns group members api URL
        """
        return Azure.API_GROUPS + group_id + '/members'

    def paged_group_members_url(self, group_id, page=1):
        """
        Returns group members api URL
        """
        # Graph API currently does not support OrderBy
        # Suppress OrderyBy parameter for now
        #params = f"?$orderby=userPrincipalName&$top={self.pagesize}"
        params = f"?$top={self.pagesize}"
        skip = self.pagesize * (page - 1)
        if skip > 0:
            params += f"&$skip={skip}"
        return self.group_members_url(group_id) + params

    # pylint: disable=no-self-use
    def group_url(self, group_id):
        """
        Returns group info api URL
        """
        return Azure.API_GROUPS + group_id + '/'

    def setup_session(self):
        """
        Creates Rest session
        """
        self.check_token()
        token = 'Bearer ' + self.token['accessToken']
        session = requests.Session()
        session.headers.update({'Authorization': token,
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'return-client-request-id': 'true'})
        return session

    def get_paged_group_members(self, group_id, page):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.GET_PAGED_GROUP_MEMBERS: Invalid Group ID')
            raise Exception('AZURE.GET_PAGED_GROUP_MEMBERS: Invalid Group ID')
        if not isinstance(page, int) or page < 1:
            logging.error('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
            raise Exception('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
        session = self.setup_session()
        url = self.paged_group_members_url(group_id, page=1)
        print(url)
        # Will manually search through all groups if Group ID is empty
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.json()['value']
            logging.error('AZURE.GET_PAGED_GROUP_MEMBERS: Unexpected Error')
            logging.error(response.status_code)
            logging.error(response.json())
            raise Exception('AZURE.GET_PAGED_GROUP_MEMBERS: Unexpected Error')
        except Exception as err:
            logging.error(err)
            raise err

    def get_group_members(self, group_id, skip_token=None):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
            raise Exception('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
        session = self.setup_session()
        url = self.group_members_url(group_id)
        #Adds Skip token for next page
        if skip_token is not None:
            url = self.group_members_url(group_id) + "?" + skip_token
        # Will manually search through all groups if Group ID is empty
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.json()
            logging.error('AZURE.GET_GROUP_MEMBERS: Unexpected Error')
            logging.error(response.status_code)
            logging.error(response.json())
            raise Exception('AZURE.GET_GROUP_MEMBERS: Unexpected Error')
        except Exception as err:
            logging.error(err)
            raise err

    def get_group_name(self, group_id):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.get_group_name: Invalid Group ID')
            raise Exception('AZURE.GET_GROUP_NAME: Invalid Group ID')
        session = self.setup_session()
        url = self.group_url(group_id)
        # Will manually search through all groups if Group ID is empty
        try:
            response = session.get(url)
            if response.status_code == 200:
                return response.json()['displayName']
            logging.error('AZURE.GET_GROUP_NAME: Unexpected Error')
            logging.error(response.status_code)
            logging.error(response.json())
            raise Exception('AZURE.GET_GROUP_NAME: Unexpected Error')
        except Exception as err:
            logging.error(err)
            raise err

    def get_all_group_members(self, group_id):
        """
        Will go through all pages of a AD Group and then returns the data
        """
        ad_group_data = []
        data = self.get_group_members(group_id, None)
        ad_group_data = ad_group_data + data["value"]
        # Checks if there is a next page and if so, does the call again until there is no next page
        if data.get("@odata.nextLink") is not None:
            while data.get("@odata.nextLink") is not None:
                skip_token = data["@odata.nextLink"].split('?')
                data = self.get_group_members(group_id, skip_token[1])
                ad_group_data = ad_group_data + data["value"]
        return ad_group_data

    # Graph API currently does not support OrderBy
    # Delete after it does
    def get_sorted_group_members(self, group_id):
        """
        Fetches All Azure AD Group Members ordered by userPrincipalName
        """
        members = self.get_all_group_members(group_id)
        return sorted(members, key=(lambda con: con.get('userPrincipalName')))
