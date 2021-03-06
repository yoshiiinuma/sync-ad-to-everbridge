"""
Tests Synchronizer
"""
from unittest.mock import MagicMock
from api.synchronizer import Synchronizer
from api.synchronizer import AdContactMap
from api.azure_group_member_iterator import AzureGroupMemberIterator
from api.everbridge_group_member_iterator import EverbridgeGroupMemberIterator
from azure_helper import create_azure_mock
from everbridge_helper import create_everbridge_mock, \
                              create_everbridge_contacts, \
                              modify_everbridge_data
# pylint: disable=unused-import
import tests.log_helper

def test_run():
    """
    Should synchronize specified AD groups to Everbridge
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2, 4, 5, 6, 7])
    data = [create_everbridge_contacts([1, 2, 3, 5, 8], True)]
    delete_ids = [3, 8]
    update_ids = [1, 2]
    insert_ids = [4, 6, 7]
    modify_everbridge_data(data[0], update_ids, 'phone', '8087779999')
    modify_everbridge_data(data[0], delete_ids, 'groups', [gid])
    update_data = create_everbridge_contacts(update_ids, True)
    insert_data = create_everbridge_contacts(insert_ids, False)
    upsert_data = update_data + insert_data
    inserted_data = [create_everbridge_contacts(insert_ids, True)]
    inserted_exids = (
        '&externalIds=aaa.bbb0004@xxx.com' +
        '&externalIds=aaa.bbb0006@xxx.com' +
        '&externalIds=aaa.bbb0007@xxx.com')
    ever = create_everbridge_mock(data)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    app = Synchronizer(azure, ever)
    # Call run
    rslt = app.run([gid])
    # Tests each method call
    azure.get_group_name.assert_called_with(123)
    ever.get_group_id_by_name.assert_called_with('GROUP1')
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_members_from_group.assert_called_with(gid, delete_ids)
    ever.delete_contacts.assert_called_with(delete_ids)
    ever.upsert_contacts.assert_called_with(upsert_data)
    ever.get_contacts_by_external_ids.assert_called_with(inserted_exids)
    ever.add_members_to_group.assert_called_with(gid, insert_ids)
    assert rslt == {
        'GROUP1': {
            'azure_group_id': 123, 'everbridge_group_id': 123,
            'azure_count': 6, 'everbridge_count': 5, 'error_contacts': 0,
            'inserted_contacts': 3, 'updated_contacts': 2, 'removed_members': 2,
            'deleted_contacts': 2, 'added_members': 3}
        }

def test_run_add_group():
    """
    Should add a group to Everbridge and insert all the members
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2])
    data = [create_everbridge_contacts([], True)]
    insert_ids = [1, 2]
    insert_data = create_everbridge_contacts(insert_ids, False)
    inserted_data = [create_everbridge_contacts(insert_ids, True)]
    inserted_exids = ('&externalIds=aaa.bbb0001@xxx.com&externalIds=aaa.bbb0002@xxx.com')
    ever = create_everbridge_mock(data)
    ever.add_group = MagicMock(return_value={'id': 123})
    ever.get_group_id_by_name = MagicMock(return_value=None)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    app = Synchronizer(azure, ever)
    # Call run
    rslt = app.run([gid])
    # Tests each method call
    azure.get_group_name.assert_called_with(gid)
    ever.get_group_id_by_name.assert_called_with('GROUP1')
    ever.add_group.assert_called_with('GROUP1', None)
    ever.delete_group.assert_not_called()
    ever.delete_members_from_group.assert_not_called()
    ever.delete_contacts.assert_not_called()
    ever.upsert_contacts.assert_called_with(insert_data)
    ever.get_contacts_by_external_ids.assert_called_with(inserted_exids)
    ever.add_members_to_group.assert_called_with(gid, insert_ids)
    assert rslt == {
        'GROUP1': {
            'azure_group_id': 123, 'everbridge_group_id': 123,
            'azure_count': 2, 'everbridge_count': 0, 'error_contacts': 0,
            'inserted_contacts': 2, 'updated_contacts': 0, 'removed_members': 0,
            'deleted_contacts': 0, 'added_members': 2}
        }

def test_run_delete_group():
    """
    Should delete the all the members and the group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [])
    data = [create_everbridge_contacts([1, 2, 3], True)]
    delete_ids = [1, 2, 3]
    modify_everbridge_data(data[0], delete_ids, 'groups', [gid])
    ever = create_everbridge_mock(data)
    app = Synchronizer(azure, ever)
    # Call run
    rslt = app.run([gid])
    # Tests each method call
    azure.get_group_name.assert_called_with(123)
    ever.get_group_id_by_name.assert_called_with('GROUP1')
    ever.add_group.assert_not_called()
    ever.delete_group.assert_called_with(gid)
    ever.delete_members_from_group.assert_called_with(gid, delete_ids)
    ever.delete_contacts.assert_called_with(delete_ids)
    ever.upsert_contacts.assert_not_called()
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'GROUP1': {
            'azure_group_id': 123, 'everbridge_group_id': 123,
            'azure_count': 0, 'everbridge_count': 3, 'error_contacts': 0,
            'inserted_contacts': 0, 'updated_contacts': 0, 'removed_members': 3,
            'deleted_contacts': 3, 'added_members': 0, 'removed': True}
        }

def test_sync_group_with_map_insert_and_delete():
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
    inserted_exids = '&externalIds=aaa.bbb0002@xxx.com&externalIds=aaa.bbb0009@xxx.com'
    ever = create_everbridge_mock(data)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    members_map = azure.get_all_group_members_map(gid)
    admap = AdContactMap(gid, members_map)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group_with_map(admap, itr_ev)
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
        'deleted_contacts': 0, 'added_members': 2, 'error_contacts': 0
    }

def test_sync_group_with_map_upadte():
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
    members_map = azure.get_all_group_members_map(gid)
    admap = AdContactMap(gid, members_map)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group_with_map(admap, itr_ev)
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
        'deleted_contacts': 0, 'added_members': 0, 'error_contacts': 0
    }

def test_sync_group_with_map_only_everbridge():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [])
    data = [create_everbridge_contacts([1, 2, 3], True)]
    delete_ids = [1, 2, 3]
    modify_everbridge_data(data[0], [1, 2], 'groups', [123])
    ever = create_everbridge_mock(data)
    members_map = azure.get_all_group_members_map(gid)
    admap = AdContactMap(gid, members_map)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group_with_map(admap, itr_ev)
    # Tests each method call
    ever.add_group.assert_not_called()
    ever.delete_group.assert_not_called()
    ever.delete_members_from_group.assert_called_with(gid, delete_ids)
    ever.delete_contacts.assert_called_with([1, 2])
    ever.upsert_contacts.assert_not_called()
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 0, 'everbridge_count': 3,
        'inserted_contacts': 0, 'updated_contacts': 0, 'removed_members': 3,
        'deleted_contacts': 2, 'added_members': 0, 'error_contacts': 0
    }

def test_sync_group_with_map_only_ad():
    """
    Should synchronize AD group to Everbridge group
    """
    gid = 123
    azure = create_azure_mock('GROUP1', [1, 2, 3])
    data = [create_everbridge_contacts([], True)]
    upsert_ids = [1, 2, 3]
    upsert_data = create_everbridge_contacts(upsert_ids, False)
    inserted_data = [create_everbridge_contacts(upsert_ids, True)]
    inserted_exids = ('&externalIds=aaa.bbb0001@xxx.com' +
                      '&externalIds=aaa.bbb0002@xxx.com' +
                      '&externalIds=aaa.bbb0003@xxx.com')
    ever = create_everbridge_mock(data)
    ever.get_contacts_by_external_ids = MagicMock(side_effect=inserted_data)
    members_map = azure.get_all_group_members_map(gid)
    admap = AdContactMap(gid, members_map)
    itr_ev = EverbridgeGroupMemberIterator(ever, gid)
    app = Synchronizer(azure, ever)
    # Call sync_group
    rslt = app.sync_group_with_map(admap, itr_ev)
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
        'deleted_contacts': 0, 'added_members': 3, 'error_contacts': 0
    }

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
    inserted_exids = '&externalIds=aaa.bbb0002@xxx.com&externalIds=aaa.bbb0009@xxx.com'
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
        'deleted_contacts': 0, 'added_members': 2, 'error_contacts': 0
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
    print(upsert_data)
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
        'deleted_contacts': 0, 'added_members': 0, 'error_contacts': 0
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
    ever.delete_contacts.assert_called_with([1, 2])
    ever.upsert_contacts.assert_not_called()
    ever.get_contacts_by_external_ids.assert_not_called()
    ever.add_members_to_group.assert_not_called()
    assert rslt == {
        'azure_group_id': 123, 'everbridge_group_id': 123, 'azure_count': 0, 'everbridge_count': 3,
        'inserted_contacts': 0, 'updated_contacts': 0, 'removed_members': 3,
        'deleted_contacts': 2, 'added_members': 0, 'error_contacts': 0
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
    inserted_exids = ('&externalIds=aaa.bbb0001@xxx.com' +
                      '&externalIds=aaa.bbb0002@xxx.com' +
                      '&externalIds=aaa.bbb0003@xxx.com')
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
        'deleted_contacts': 0, 'added_members': 3, 'error_contacts': 0
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
        'deleted_contacts': 0, 'added_members': 0, 'error_contacts': 0
    }
