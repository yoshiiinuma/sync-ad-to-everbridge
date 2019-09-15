"""
Everbridge Test Helper
"""
from api.everbridge import Everbridge
from api.contact_utils import convert_to_everbridge
from tests.azure_helper import create_azure_contact

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
