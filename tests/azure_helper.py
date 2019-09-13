"""
Azure Test Helper
"""
from unittest.mock import MagicMock
from api.azure import Azure

# pylint: disable=dangerous-default-value
def create_azure_instance(cid=None, secret=None, tenant=None,
                          token={'accessToken':'XXXTOKENXXX'}):
    """
    Creates Azure instance
    """
    if not cid:
        cid = 'cid'
    if not secret:
        secret = 'secret'
    if not tenant:
        tenant = 'tenant'
    azure = Azure(cid, secret, tenant)
    azure.set_token(token)
    return azure

def create_azure_mock(side_ad_list):
    """
    Creates Azure instance
    """
    azure = Azure('cid', 'secret', 'tenant')
    azure.set_token({'accessToken':'XXXTOKENXXX'})
    azure.get_group_members = MagicMock()
    azure.get_group_members.side_effect = side_ad_list
    return azure
