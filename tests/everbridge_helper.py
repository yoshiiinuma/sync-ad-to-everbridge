"""
Everbridge Test Helper
"""
from unittest.mock import MagicMock
from api.everbridge import Everbridge
from api.contact_utils import convert_to_everbridge
from tests.azure_helper import create_azure_contact

def create_everbridge_mock(data):
    """
    Creates Everbridge API mock
    """
    ever = create_everbridge_instance()
    ever.get_group_id_by_name = MagicMock(return_value=123)
    ever.get_paged_group_members = MagicMock(side_effect=data)
    ever.add_group = MagicMock()
    ever.delete_group = MagicMock()
    ever.get_contacts_by_external_ids = MagicMock()
    ever.delete_contacts = MagicMock()
    ever.upsert_contacts = MagicMock()
    ever.add_members_to_group = MagicMock()
    ever.delete_members_from_group = MagicMock()
    return ever

def modify_everbridge_data(data, ids, key, val):
    """
    Changes contacts specified by ids
    """
    for contact in data:
        if contact['id'] in ids:
            if key == 'phone':
                contact['paths'][1]['value'] = val
            elif key == 'mobile':
                contact['paths'][2]['value'] = val
            elif key == 'sms':
                contact['paths'][2]['value'] = val
            else:
                contact[key] = val

def create_everbridge_instance(org=None, username=None, passwd=None):
    """
    Returns Everbridge instance
    """
    if not org:
        org = '1234567'
    if not username:
        username = 'user'
    if not passwd:
        passwd = 'pass'
    ever = Everbridge(org, username, passwd)
    return ever

def create_everbridge_contact(seq, eid=None):
    """
    Returns Everbridge Contact Object
    """
    return convert_to_everbridge(create_azure_contact(seq), eid)

def create_everbridge_contacts(ad_ids, need_ever_id=False):
    """
    Returns Everbridge Contacts with specified IDs
    """
    if need_ever_id:
        return [create_everbridge_contact(seq, seq) for seq in ad_ids]
    return [create_everbridge_contact(seq) for seq in ad_ids]
