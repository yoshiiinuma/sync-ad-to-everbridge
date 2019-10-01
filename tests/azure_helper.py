"""
Azure Test Helper
"""
from unittest.mock import MagicMock
from api.azure import Azure

def create_azure_mock(group_name, ids=None, data=None):
    """
    Creates Azure API mock
    """
    if not data:
        if not ids:
            ids = []
        data = [create_azure_contacts(ids)]
    azure = create_azure_instance()
    azure.get_group_name = MagicMock(return_value=group_name)
    azure.get_paged_group_members = MagicMock(side_effect=data)
    flattened = [item for sublist in data for item in sublist]
    azure.get_all_group_members = MagicMock(side_effect=[flattened])
    ####################################################################
    # Graph API currently does not support OrderBy
    # Delete the follwing lines after it does
    azure.get_sorted_group_members = MagicMock(return_value=flattened)
    ####################################################################
    return azure

def create_azure_instance_without_token(cid=None, secret=None, tenant=None):
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
    return azure

def create_azure_instance(cid=None, secret=None, tenant=None, token=None):
    """
    Returns Azure instance
    """
    if not token:
        token = {'accessToken': 'XXXTOKENXXX'}
    azure = create_azure_instance_without_token(cid, secret, tenant)
    azure.set_token(token)
    return azure

def create_azure_contact(seq):
    """
    Returns Azure Contact Object
    """
    padded = str(seq).zfill(4)
    return {
        'id': seq,
        'displayName': f'AAA BBB{padded}',
        'givenName': f'AAA',
        'surname': f'BBB{padded}',
        'businessPhones': ['808586' + padded],
        'mobilePhone': '808587' + padded,
        'mail': f'aaa.bbb{padded}@xxx.com',
        'userPrincipalName': f'aaa.bbb{padded}@xxx.com'}

def create_azure_contacts(ids):
    """
    Returns Azure Contacts with specified IDs
    """
    return [create_azure_contact(seq) for seq in ids]

def modify_azure_data(data, ids, key, val):
    """
    Changes contacts specified by ids
    """
    for contact in data:
        if contact['id'] in ids:
            contact[key] = val
