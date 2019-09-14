"""
Tests Synchronizer
"""
import pprint
from unittest.mock import MagicMock
from api.synchronizer import Synchronizer
from api.azure_group_member_iterator import AzureGroupMemberIterator
from api.everbridge_group_member_iterator import EverbridgeGroupMemberIterator
from azure_helper import create_azure_instance, create_azure_contacts
from everbridge_helper import create_everbridge_instance, create_everbridge_contacts
# pylint: disable=unused-import
import tests.log_helper

def pp(obj):
    """
    Prtty Print
    """
    pprint.PrettyPrinter().pprint(obj)

def create_azure_mock(group_name, ids):
    """
    Creates Azure API mock
    """
    data = [create_azure_contacts(ids)]
    azure = create_azure_instance()
    azure.get_group_name = MagicMock(return_value=group_name)
    azure.get_paged_group_members = MagicMock(side_effect=data)
    return azure

def create_everbridge_mock(data):
    """
    Creates Everbridge API mock
    """
    ever = create_everbridge_instance()
    ever.get_get_group_id_by_name = MagicMock(return_value=123)
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

def test_sync_group_insert_and_delete():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2, 5, 9])
    data = [create_everbridge_contacts([1, 3, 5, 7, 8], True)]
    delete_ids = [3, 7, 8]
    upsert_ids = [2, 9]
    upsert_data = create_everbridge_contacts(upsert_ids, False)
    inserted_data = [create_everbridge_contacts(upsert_ids, True)]
    inserted_exids = "&externalIds=aaabbb0002@xxx.com&externalIds=aaabbb0009@xxx.com"
    ever = create_everbridge_mock(data)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    itr_ad = AzureGroupMemberIterator(azure, gid)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group(itr_ad, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_contacts.assert_not_called()
    ever.delete_members_from_group.assert_called_with(gid, delete_ids)
    ever.upsert_contacts.assert_called_with(upsert_data)
    ever.get_contacts_by_external_ids.assert_called_with(inserted_exids)
    ever.add_members_to_group.assert_called_with(gid, upsert_ids)
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 4, 'everbridge_count': 5,
        'inserted_contacts': 2, 'updated_contacts': 0, 'removed_members': 3,
        'deleted_contacts': 0, 'added_members': 2
    }

def test_sync_group_upadte():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2, 3, 4])
    data = [create_everbridge_contacts([1, 2, 3, 4], True)]
    upsert_ids = [2, 4]
    modify_everbridge_data(data[0], upsert_ids, 'phone', '8087779999')
    upsert_data = create_everbridge_contacts(upsert_ids, True)
    ever = create_everbridge_mock(data)
    itr_ad = AzureGroupMemberIterator(azure, gid)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group(itr_ad, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_contacts.assert_not_called()
    ever.delete_members_from_group.assert_not_called()
    ever.upsert_contacts.assert_called_with(upsert_data)
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 4, 'everbridge_count': 4,
        'inserted_contacts': 0, 'updated_contacts': 2, 'removed_members': 0,
        'deleted_contacts': 0, 'added_members': 0
    }

def test_sync_group_only_everbridge():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [])
    data = [create_everbridge_contacts([1, 2, 3], True)]
    delete_ids = [1, 2, 3]
    modify_everbridge_data(data[0], [1, 2], 'groups', [123])
    ever = create_everbridge_mock(data)
    #ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted)
    itr_ad = AzureGroupMemberIterator(azure, gid)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group(itr_ad, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_members_from_group.assert_called_with(gid, delete_ids)
    ever.delete_contacts.assert_called_with(gid, [1, 2])
    ever.upsert_contacts.assert_not_called()
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 0, 'everbridge_count': 3,
        'inserted_contacts': 0, 'updated_contacts': 0, 'removed_members': 3,
        'deleted_contacts': 2, 'added_members': 0
    }

def test_sync_group_only_ad():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2, 3])
    data = [create_everbridge_contacts([], True)]
    upsert_ids = [1, 2, 3]
    upsert_data = create_everbridge_contacts(upsert_ids, False)
    inserted_data = [create_everbridge_contacts(upsert_ids, True)]
    inserted_exids = ('&externalIds=aaabbb0001@xxx.com' +
                      '&externalIds=aaabbb0002@xxx.com' +
                      '&externalIds=aaabbb0003@xxx.com')
    ever = create_everbridge_mock(data)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    itr_ad = AzureGroupMemberIterator(azure, gid)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group(itr_ad, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_contacts.assert_not_called()
    ever.delete_members_from_group.assert_not_called()
    ever.upsert_contacts.assert_called_with(upsert_data)
    ever.get_contacts_by_external_ids.assert_called_with(inserted_exids)
    ever.add_members_to_group.assert_called_with(gid, upsert_ids)
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 3, 'everbridge_count': 0,
        'inserted_contacts': 3, 'updated_contacts': 0, 'removed_members': 0,
        'deleted_contacts': 0, 'added_members': 3
    }

def test_sync_group_no_data():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [])
    data = [create_everbridge_contacts([], True)]
    ever = create_everbridge_mock(data)
    itr_ad = AzureGroupMemberIterator(azure, gid)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group(itr_ad, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_contacts.assert_not_called()
    ever.delete_members_from_group.assert_not_called()
    ever.upsert_contacts.assert_not_called()
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 0, 'everbridge_count': 0,
        'inserted_contacts': 0, 'updated_contacts': 0, 'removed_members': 0,
        'deleted_contacts': 0, 'added_members': 0
    }
