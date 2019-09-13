"""
Azure Test Helper
"""
from unittest.mock import MagicMock
from api.azure import Azure

# pylint: disable=dangerous-default-value
def create_azure_instance(cid=None, secret=None, tenant=None,
                          token={'accessToken':'XXXTOKENXXX'}):
    """
    Returns Azure instance
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

def create_azure_contact(seq):
    """
    Returns Azure Contact Object
    """
    return {
        'id': seq,
        'displayName': f'AAA{seq} BBB{seq}',
        'givenName': f'AAA{seq}',
        'surname': f'BBB{seq}',
        'businessPhones': ['808111' + str(seq).zfill(4)],
        'mobilePhone': '808222' + str(seq).zfill(4),
        'mail': f'aaabbb{seq}1@xxx.com',
        'userPrincipalName': f'aaabbb{seq}1@xxx.com'}

def create_azure_contacts(ids):
    """
    Returns Azure Contacts with specified IDs
    """
    return [create_azure_contact(seq) for seq in ids]
