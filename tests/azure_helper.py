"""
Azure Test Helper
"""
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
    padded = str(seq).zfill(4)
    return {
        'id': seq,
        'displayName': f'AAA{padded} BBB{padded}',
        'givenName': f'AAA{padded}',
        'surname': f'BBB{padded}',
        'businessPhones': ['808111' + padded],
        'mobilePhone': '808222' + padded,
        'mail': f'aaabbb{padded}@xxx.com',
        'userPrincipalName': f'aaabbb{padded}@xxx.com'}

def create_azure_contacts(ids):
    """
    Returns Azure Contacts with specified IDs
    """
    return [create_azure_contact(seq) for seq in ids]
