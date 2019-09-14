"""
Test ContactTracker
"""
from api.contact_tracker import ContactTracker

def create_tracker():
    """
    Creates ContactTracker instacne with data
    """
    ad_gid = 123
    ev_gid = 456
    tracker = ContactTracker(ad_gid, ev_gid)
    tracker.push(ContactTracker.INSERT_CONTACT, {'externalId': 'aaa1@test.com'})
    tracker.push(ContactTracker.INSERT_CONTACT, {'externalId': 'aaa2@test.com'})
    tracker.push(ContactTracker.INSERT_CONTACT, {'externalId': 'aaa3@test.com'})
    tracker.push(ContactTracker.UPDATE_CONTACT, {'id': 1, 'externalId': 'bbb1@test.com'})
    tracker.push(ContactTracker.UPDATE_CONTACT, {'id': 2, 'externalId': 'bbb2@test.com'})
    tracker.push(ContactTracker.UPDATE_CONTACT, {'id': 3, 'externalId': 'bbb3@test.com'})
    tracker.push(ContactTracker.REMOVE_MEMBER,
                 {'id': 4, 'externalId': 'ccc4@test.com', 'groups': [1, 2]})
    tracker.push(ContactTracker.REMOVE_MEMBER,
                 {'id': 5, 'externalId': 'ccc5@test.com', 'groups': [1]})
    tracker.push(ContactTracker.REMOVE_MEMBER,
                 {'id': 6, 'externalId': 'ccc6@test.com'})
    return tracker

def test_insert_contact():
    """
    Should return INSERT_CONTACT contacts
    """
    tracker = create_tracker()
    contacts = tracker.get_contacts(ContactTracker.INSERT_CONTACT)
    expected = [
        {'externalId': 'aaa1@test.com'},
        {'externalId': 'aaa2@test.com'},
        {'externalId': 'aaa3@test.com'}]
    assert contacts == expected

def test_update_contact():
    """
    Should return UPDATE_CONTACT contacts
    """
    tracker = create_tracker()
    contacts = tracker.get_contacts(ContactTracker.UPDATE_CONTACT)
    expected = [
        {'id': 1, 'externalId': 'bbb1@test.com'},
        {'id': 2, 'externalId': 'bbb2@test.com'},
        {'id': 3, 'externalId': 'bbb3@test.com'}]
    assert contacts == expected

def test_remove_member():
    """
    Should return REMOVE_MEMBER contacts
    """
    tracker = create_tracker()
    contacts = tracker.get_contacts(ContactTracker.REMOVE_MEMBER)
    expected = [
        {'id': 4, 'externalId': 'ccc4@test.com', 'groups': [1, 2]},
        {'id': 5, 'externalId': 'ccc5@test.com', 'groups': [1]},
        {'id': 6, 'externalId': 'ccc6@test.com'}]
    assert contacts == expected

def test_get_upsert_contacts():
    """
    Should return contacts for upsert
    """
    tracker = create_tracker()
    contacts = tracker.get_upsert_contacts()
    expected = [
        {'id': 1, 'externalId': 'bbb1@test.com'},
        {'id': 2, 'externalId': 'bbb2@test.com'},
        {'id': 3, 'externalId': 'bbb3@test.com'},
        {'externalId': 'aaa1@test.com'},
        {'externalId': 'aaa2@test.com'},
        {'externalId': 'aaa3@test.com'}]
    assert contacts == expected

def test_get_inserted_contact_external_ids():
    """
    Should return ids of inserted contacts
    """
    tracker = create_tracker()
    ids = tracker.get_inserted_contact_external_ids()
    exp = [('&externalIds=aaa1@test.com' +
            '&externalIds=aaa2@test.com' +
            '&externalIds=aaa3@test.com')]
    assert ids == exp
    ids = tracker.get_inserted_contact_external_ids(1)
    exp = ['&externalIds=aaa1@test.com',
           '&externalIds=aaa2@test.com',
           '&externalIds=aaa3@test.com']
    assert ids == exp
    ids = tracker.get_inserted_contact_external_ids(2)
    exp = ['&externalIds=aaa1@test.com&externalIds=aaa2@test.com',
           '&externalIds=aaa3@test.com']
    assert ids == exp

def test_get_remove_member_ids():
    """
    Should return contact ids for removing members
    """
    tracker = create_tracker()
    ids = tracker.get_remove_member_ids()
    exp = [4, 5, 6]
    assert ids == exp

def test_get_delete_contact_ids():
    """
    Should return ids of contacts not belonging to any groups
    """
    tracker = create_tracker()
    ids = tracker.get_delete_contact_ids()
    exp = [5]
    assert ids == exp

def test_report():
    """
    Should return report
    """
    tracker = create_tracker()
    rslt = tracker.report()
    exp = {
        'azure_group_id': 123, 'everbridge_group_id': 456,
        'azure_count': 0, 'everbridge_count': 0,
        'inserted_contacts': 3, 'removed_members': 3, 'updated_contacts': 3,
        'deleted_contacts': 0, 'added_members': 0}
    assert rslt == exp
