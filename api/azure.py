"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal
from api.exceptions import AzureException

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
        self.session = None
        self.pagesize = Azure.DEFAULT_PAGESIZE

    def setup(self):
        """
        Sets up token and session
        MUST BE cALLED ONECE before any API calls
        """
        if not self.token:
            self.reset_token()
        self._setup_session()

    def _setup_session(self):
        """
        Creates Rest session
        """
        if not self.token or not self.token['accessToken']:
            return
        token = 'Bearer ' + self.token['accessToken']
        self.session = requests.Session()
        self.session.headers.update({'Authorization': token,
                                     'Accept': 'application/json',
                                     'Content-Type': 'application/json',
                                     'return-client-request-id': 'true'})

    def _check_setup(self):
        """
        Raises an Exception if token or session is not set up
        """
        self._check_token()
        self._check_session()

    def _check_token(self):
        """
        Raises an Exception if token is not set
        """
        if not self.token or not self.token['accessToken']:
            logging.error('AZURE._CHECK_TOKEN: Invalid Token')
            raise AzureException('AZURE._CHECK_TOKEN: Invalid Token')

    def _check_session(self):
        """
        Raises an Exception if session is not set
        """
        if not self.session:
            logging.error('AZURE.API._CHECK_SESSION: Session Not Established')
            raise AzureException('AZURE.API._CHECK_SESSION: Session Not Established')

    @staticmethod
    def _log_unexpected_response(caller, response):
        """
        Logs unexpected response
        """
        msg = 'AZURE.' + caller.upper() + ': Unexpected Response'
        logging.error(msg)
        logging.error(response.status_code)
        logging.error(response.json())

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
            raise AzureException('AZURE.API.get_token: Invalid parameter')
        context = adal.AuthenticationContext(self.authority_url())
        try:
            token = context.acquire_token_with_client_credentials(
                Azure.API_BASE, self.client_id, self.secret)
            return token
        except Exception as err:
            logging.error(err)
            raise AzureException() from err

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
        params = f"?$orderby=userPrincipalName&$top={self.pagesize}"
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

    def get_paged_group_members(self, group_id, page):
        """
        Fetches Azure AD Group Members
        """
        # Graph API currently does not support OrderBy
        # Will get 400 BadRequest 'OrderBy not supported'
        if not group_id:
            logging.error('AZURE.GET_PAGED_GROUP_MEMBERS: Invalid Group ID')
            raise AzureException('AZURE.GET_PAGED_GROUP_MEMBERS: Invalid Group ID')
        if not isinstance(page, int) or page < 1:
            logging.error('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
            raise AzureException('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
        self._check_setup()
        url = self.paged_group_members_url(group_id, page=1)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()['value']
        except Exception as err:
            logging.error(err)
            raise AzureException() from err
        Azure._log_unexpected_response('get_paged_group_members', response)
        raise AzureException('AZURE.GET_PAGED_GROUP_MEMBERS: Unexpected Response')

    def get_group_members(self, group_id, skip_token=None):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
            raise AzureException('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
        self._check_setup()
        url = self.group_members_url(group_id)
        #Adds Skip token for next page
        if skip_token is not None:
            url = self.group_members_url(group_id) + "?" + skip_token
        # Will manually search through all groups if Group ID is empty
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as err:
            logging.error(err)
            raise AzureException from err
        Azure._log_unexpected_response('get_group_members', response)
        raise AzureException('AZURE.GET_GROUP_MEMBERS: Unexpected Response')

    def get_group_name(self, group_id):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.get_group_name: Invalid Group ID')
            raise AzureException('AZURE.GET_GROUP_NAME: Invalid Group ID')
        self._check_setup()
        url = self.group_url(group_id)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()['displayName']
        except Exception as err:
            logging.error(err)
            raise AzureException() from err
        Azure._log_unexpected_response('get_group_name', response)
        raise AzureException('AZURE.GET_GROUP_NAME: Unexpected Response')

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

    def get_all_group_members_map(self, group_id):
        """
        Returns the Dictionary(<userPrincipalName>, <Contact>) of all group members
        """
        dictionary = {}
        members = self.get_all_group_members(group_id)
        print(members)
        for contact in members:
            dictionary[contact['userPrincipalName']] = contact
        return dictionary

    # Graph API currently does not support OrderBy
    # Delete this function after it does
    def get_sorted_group_members(self, group_id):
        """
        Fetches All Azure AD Group Members ordered by userPrincipalName
        """
        members = self.get_all_group_members(group_id)
        return sorted(members, key=(lambda con: con.get('userPrincipalName')))
