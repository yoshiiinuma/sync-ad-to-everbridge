"""
Requests Client Crediential Token and then performs API call to get Login Events
"""
import logging
import requests
import adal
from . import exceptions
from . import contact_validator
class Azure:
    """
    Handles Azure Graph API requests
    """
    LOGIN = 'https://login.microsoftonline.com/'
    API_BASE = 'https://graph.microsoft.com/'
    API_GROUPS = API_BASE + 'v1.0/groups/'
    API_USERS = API_BASE + 'v1.0/users/'
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
            raise exceptions.AzureException('AZURE._CHECK_TOKEN: Invalid Token')

    def _check_session(self):
        """
        Raises an Exception if session is not set
        """
        if not self.session:
            logging.error('AZURE.API._CHECK_SESSION: Session Not Established')
            raise exceptions.AzureException('AZURE.API._CHECK_SESSION: Session Not Established')

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
            raise exceptions.AzureException('AZURE.API.get_token: Invalid parameter')
        context = adal.AuthenticationContext(self.authority_url())
        try:
            token = context.acquire_token_with_client_credentials(
                Azure.API_BASE, self.client_id, self.secret)
            return token
        except Exception as err:
            logging.error(err)
            raise exceptions.AzureException() from err

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
            raise exceptions.AzureException('AZURE.GET_PAGED_GROUP_MEMBERS: Invalid Group ID')
        if not isinstance(page, int) or page < 1:
            logging.error('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
            raise exceptions.AzureException('AZURE.PAGED_GROUP_MEMBERS_URL: Invalid Page')
        self._check_setup()
        url = self.paged_group_members_url(group_id, page=1)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()['value']
        except Exception as err:
            logging.error(err)
            raise exceptions.AzureException() from err
        Azure._log_unexpected_response('get_paged_group_members', response)
        raise exceptions.AzureException('AZURE.GET_PAGED_GROUP_MEMBERS: Unexpected Response')

    def get_group_members(self, group_id, skip_token=None):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
            raise exceptions.AzureException('AZURE.GET_GROUP_MEMBERS: Invalid Group ID')
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
            raise exceptions.AzureException from err
        Azure._log_unexpected_response('get_group_members', response)
        raise exceptions.AzureException('AZURE.GET_GROUP_MEMBERS: Unexpected Response')

    def get_group_name(self, group_id):
        """
        Fetches Azure AD Group Members
        """
        if not group_id:
            logging.error('AZURE.get_group_name: Invalid Group ID')
            raise exceptions.AzureException('AZURE.GET_GROUP_NAME: Invalid Group ID')
        self._check_setup()
        url = self.group_url(group_id)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()['displayName']
        except Exception as err:
            logging.error(err)
            raise exceptions.AzureException() from err
        Azure._log_unexpected_response('get_group_name', response)
        raise exceptions.AzureException('AZURE.GET_GROUP_NAME: Unexpected Response')

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
        for contact in members:
            contact = contact_validator.validate_and_fix_azure_contact(contact)
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

    def user_url(self, user_id):
        """
        Returns group info api URL
        """
        return Azure.API_USERS + user_id + '/'

    def user_filter_url(self, filter_string):
        """
        Returns group info api URL
        """
        return Azure.API_USERS + filter_string

    def get_user(self, user_id):
        """
        Fetches individual user
        """
        if not user_id:
            logging.error('AZURE.user: Invalid User ID')
            raise exceptions.AzureException('AZURE.GET_USER: Invalid User ID')
        self._check_setup()
        url = self.user_url(user_id)
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                contact = contact_validator.validate_and_fix_azure_contact(response.json())
                return contact
        except Exception as err:
            logging.error(err)
            raise exceptions.AzureException() from err
        Azure._log_unexpected_response('get_user', response)
        raise exceptions.AzureException('AZURE.GET_USER: Unexpected Response')

    def generate_email_filter_string(ad_user_emails):
        if not ad_user_emails:
            return ""
        filter_string = "$filter="
        count = 0
        for email in ad_user_emails:
            filter_string = filter_string + "startswith(mail, '" + email + "')"
            count = count + 1
    def get_users_with_filters(self, ad_user_emails):
    """
    Fetches multiple users by filtering using emails
    """

    if not ad_user_emails:
        logging.error('AZURE.get_users_with_filters: No User Id Provided')
        raise exceptions.AzureException('AZURE.GET_USERS_WITH_FILTERS: No User Id Provided')

    filter_string = "$filter=startswith(mail, '" + str(ad_user_emails[0])
    self._check_setup()
    url = self.user_filter_url(ad_user_emails)
    try:
        response = self.session.get(url)
        if response.status_code == 200:
            for contact in response.json():
                contact = contact_validator.validate_and_fix_azure_contact(contact)
            return response.json()
    except Exception as err:
        logging.error(err)
        raise exceptions.AzureException() from err
    Azure._log_unexpected_response('get_users_with_filters', response)
    raise exceptions.AzureException('AZURE.GET_USERS_WITH_FILTERS: Unexpected Response')