"""
Keeps track of contacts in the list according to the operation
"""
from api.exceptions import ContactTrackerException


class ContactTracker:
    """
    Keeps track of contacts in the list according to the operation
    """
    INSERT_CONTACT = 'INSERT_CONTACT'
    UPDATE_CONTACT = 'UPDATE_CONTACT'
    REMOVE_MEMBER = 'REMOVE_MEMBER'

    def __init__(self):
        self.new_contacts = []
        self.updated_contacts = []
        self.obsolete_contacts = []
        self.obsolete_members = []
        self.new_members = []

    def set_new_members(self, members):
        """
        Sets new members
        """
        self.new_members = members

    def push(self, optype, contact):
        """
        Keeps track of contacts in the list according to the operation
        """
        if optype == ContactTracker.INSERT_CONTACT:
            self.new_contacts.append(contact)
        elif optype == ContactTracker.UPDATE_CONTACT:
            self.updated_contacts.append(contact)
        elif optype == ContactTracker.REMOVE_MEMBER:
            self.obsolete_members.append(contact)
        else:
            raise ContactTrackerException('CONTACT_TRACKER.PUSH: OPTYPE NOT SUPPORTED ' + optype)

    def get_contacts(self, optype):
        """
        Returns the contact list specified by optype
        """
        if optype == ContactTracker.INSERT_CONTACT:
            return self.new_contacts
        if optype == ContactTracker.UPDATE_CONTACT:
            return self.updated_contacts
        if optype == ContactTracker.REMOVE_MEMBER:
            return self.obsolete_members
        raise ContactTrackerException('CONTACT_TRACKER.GET: OPTYPE NOT SUPPORTED ' + optype)

    def get_upsert_contacts(self):
        """
        Returns Contacts for upserting
        """
        return self.updated_contacts + self.new_contacts

    def get_inserted_contact_external_ids(self, per=100):
        """
        Returns the list of externalIds from new_contacts
        The list is divided into sublists per given number (default 100)
        """
        filters = []
        ids = ""
        cnt = 0
        for contact in self.new_contacts:
            cnt += 1
            ids += '&externalIds=' + contact['externalId']
            if cnt % per == 0:
                filters.append(ids)
                ids = ""
        if ids:
            filters.append(ids)
        return filters

    def get_remove_member_ids(self):
        """
        Returns the list of Contact IDs from obsolete_members
        """
        return [con['id'] for con in self.obsolete_members]

    def get_delete_contact_ids(self):
        """
        Returns the IDs of contacts which do/will not belong to any groups
        """
        self.obsolete_contacts = []
        for contact in self.obsolete_members:
            # groups attribute contains ids of groups which the user belongs to
            # we should delete the contact if the user belongs to only the current one
            if 'groups' in contact:
                if len(contact['groups']) == 1:
                    self.obsolete_contacts.append(contact['id'])
        return self.obsolete_contacts

    def report(self):
        """
        Returns size of each list
        """
        return {
            'inserted_contacts': len(self.new_contacts),
            'updated_contacts': len(self.updated_contacts),
            'deleted_contacts': len(self.obsolete_contacts),
            'added_members': len(self.new_members),
            'removed_members': len(self.obsolete_members)}
