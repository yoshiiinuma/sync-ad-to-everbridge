"""
Syncs Azure AD contacts to Everbridge
"""
import logging
import re
from . import azure_group_member_iterator
from . import everbridge_group_member_iterator 
from . import contact_tracker 
from . import contact_utils
from . import exceptions 
from . import contact_validator
from . import everbridge_shared_mailbox
from . import everbridge_logic
class AdContactMap:
    """
    AD group members dictionary wrapper
    """
    def __init__(self, group_id, members_map):
        self.group_id = group_id
        self.members_map = members_map
        self.total = len(members_map)

    def get_group_id(self):
        """
        Returns group ID
        """
        return self.group_id

    def get_total(self):
        """
        Returns the total number of members
        """
        return self.total

    def pop(self, key):
        """
        Returns contact popped from the map if key exists; None otherwise
        """
        return self.members_map.pop(key, None)

    def values(self):
        """
        Returns all the contacts left in the map
        """
        return self.members_map.values()

class Synchronizer:
    """
    Syncs Azure AD contacts to Everbridge
    """
    def __init__(self, azure, everbridge):
        self.azure = azure
        self.everbridge = everbridge
        self.report = {}

    def run(self, ad_group_ids):
        """
        Syncs Azure AD contacts to Everbridge
        """
        self.report = {}
        for gid_ad in ad_group_ids:
            name = self.azure.get_group_name(gid_ad)
            gid_ev = self.everbridge.get_group_id_by_name(name)
            # Create a Everbridge group if not exist
            if not gid_ev:
                gid_ev = self._create_new_everbridge_group(name)
            # Create iterators
            itr_ad = azure_group_member_iterator.AzureGroupMemberIterator(self.azure, gid_ad)
            itr_ev = everbridge_group_member_iterator.EverbridgeGroupMemberIterator(self.everbridge, gid_ev)
            # Sync AD group to Everbridge
            rslt = self.sync_group(itr_ad, itr_ev)
            # Delete the group from Everbridge if no members exist
            if rslt['everbridge_count'] + rslt['inserted_contacts'] - rslt['removed_members'] == 0:
                self._delete_everbridge_group(gid_ev)
                rslt['removed'] = True
            self.report[name] = rslt
            logging.info("Synched %s", name)
            logging.info(rslt)
        return self.report

    def run_with_map(self, ad_group_ids, ad_users_emails, ev_parent_name):
        """
        Syncs Azure AD contacts to Everbridge
        """
        self.report = {}
        for gid_ad in ad_group_ids:
            name = self.azure.get_group_name(gid_ad)
            gid_ev = self.everbridge.get_group_id_by_name(name)
            # Create a Everbridge group if not exist
            if not gid_ev:
                gid_ev = self._create_new_everbridge_group(name)
            # Create iterators
            itr_ev = everbridge_group_member_iterator.EverbridgeGroupMemberIterator(self.everbridge, gid_ev)
            members_map = self.azure.get_all_group_members_map(gid_ad)
            admap = AdContactMap(gid_ad, members_map)
            # Sync AD group to Everbridge
            rslt = self.sync_group_with_map(admap, itr_ev)
            # Delete the group from Everbridge if no members exist
            if rslt['everbridge_count'] + rslt['inserted_contacts'] - rslt['removed_members'] == 0:
                self._delete_everbridge_group(gid_ev)
                rslt['removed'] = True
            self.report[name] = rslt
            logging.info("Synched %s", name)
            logging.info(rslt)
        #Managed Shared Mailboxes from AD 
        #Shared Mailboxes are user accounts in AD
        #Shared Mailboxes will be in the specified parent group

        # Create Everbridge parent group for shared mailboxes if not exist
        parent_group = everbridge_shared_mailbox.get_parent_group(ev_parent_name,self)
        #Gets individual users from AD. 
        #Similar to azure.get_all_group_members but uses the $filter ODA query
        ad_users_map = self.azure.get_users_with_filters_map(ad_users_emails)
        # Create iterators
        shared_mailbox_map = AdContactMap("",ad_users_map)
        iter_mailbox =  everbridge_group_member_iterator.EverbridgeGroupMemberIterator(self.everbridge, parent_group)
        # Sync Shared Mailbox group to Everbridge
        rslt = self.sync_group_with_map(shared_mailbox_map, iter_mailbox)
        self.report[ev_parent_name] = rslt
        logging.info("Synched %s", ev_parent_name)
        logging.info(rslt)
        return self.report

    def sync_group(self, itr_ad, itr_ev):
        """
        Syncs specified AD Grdoup to Everbridge group
        """
        tracker = contact_tracker.ContactTracker()
        con_ad = next(itr_ad)
        con_ev = next(itr_ev)
        while con_ad or con_ev:
            if not con_ad and con_ev:
                # the contact exists only in Everbridge => Delete it
                tracker.push(contact_tracker.ContactTracker.REMOVE_MEMBER, con_ev)
                con_ev = next(itr_ev)
            elif con_ad and not con_ev:
                # the contact exists only in AD => Insert it
                tracker.push(contact_tracker.ContactTracker.INSERT_CONTACT, contact_utils.convert_to_everbridge(con_ad))
                con_ad = next(itr_ad)
            elif con_ad['userPrincipalName'] == con_ev['externalId']:
                converted = contact_utils.convert_to_everbridge(con_ad, con_ev['id'])
                if contact_utils.is_different(converted, con_ev):
                    tracker.push(contact_tracker.ContactTracker.UPDATE_CONTACT, converted)
                con_ad = next(itr_ad)
                con_ev = next(itr_ev)
            elif con_ad['userPrincipalName'] > con_ev['externalId']:
                # the contact exists only in Everbridge => Delete it
                tracker.push(contact_tracker.ContactTracker.REMOVE_MEMBER, con_ev)
                con_ev = next(itr_ev)
            else:
                # the contact exists only in AD => Insert it
                tracker.push(contact_tracker.ContactTracker.INSERT_CONTACT, contact_utils.convert_to_everbridge(con_ad))
                con_ad = next(itr_ad)
        self._handle_delete(itr_ev.get_group_id(), tracker)
        self._handle_upsert(itr_ev.get_group_id(), tracker)
        return Synchronizer._enhance_report(tracker.report(), itr_ad, itr_ev)

    def sync_group_with_map(self, admap, itr_ev):
        """
        Syncs specified AD Grdoup to Everbridge group
        """
        tracker = contact_tracker.ContactTracker()
        con_ev = next(itr_ev)
        while con_ev:
            con_ad = admap.pop(con_ev['externalId'])
            if not con_ad:
                # the contact exists only in Everbridge => Delete it
                tracker.push(contact_tracker.ContactTracker.REMOVE_MEMBER, con_ev)
            elif con_ad['userPrincipalName'] == con_ev['externalId']:
                converted = contact_utils.convert_to_everbridge(con_ad, con_ev['id'])
                if contact_utils.is_different(converted, con_ev):
                    tracker.push(contact_tracker.ContactTracker.UPDATE_CONTACT, converted)
            con_ev = next(itr_ev)
        for con_ad in admap.values():
            tracker.push(contact_tracker.ContactTracker.INSERT_CONTACT, contact_utils.convert_to_everbridge(con_ad))
        self._handle_delete(itr_ev.get_group_id(), tracker)
        self._handle_upsert(itr_ev.get_group_id(), tracker)
        return Synchronizer._enhance_report(tracker.report(), admap, itr_ev)

    @staticmethod
    def _enhance_report(report, itr_ad, itr_ev):
        report['azure_group_id'] = itr_ad.get_group_id()
        report['everbridge_group_id'] = itr_ev.get_group_id()
        report['azure_count'] = itr_ad.get_total()
        report['everbridge_count'] = itr_ev.get_total()
        return report

    def _create_new_everbridge_group(self, group_name, parent_group=None):
        """
        Creates a new Everbridge group
        """
        new_group = self.everbridge.add_group(group_name, parent_group)
        if not new_group or 'id' not in new_group:
            msg = 'SYNCHRONIZER._CREATE_NEW_EVERBRIDGE_GROUP FAILED ' + group_name
            logging.error(msg)
            logging.error(new_group)
            raise exceptions.SynchronizerException(msg)
        logging.info("Created Everbridge Group %s", group_name)
        return new_group['id']

    def _delete_everbridge_group(self, group_name):
        """
        Deletes a Everbridge group
        """
        self.everbridge.delete_group(group_name)
        logging.info("Deleted Everbridge Group %s", group_name)

    def _handle_delete(self, group_id, tracker):
        """
        Removes members from group and deletes contacts not belonging to any groups
        """
        members = tracker.get_remove_member_ids()
        if not members:
            return
        self.everbridge.delete_members_from_group(group_id, members)
        contacts = tracker.get_delete_contact_ids()
        if contacts:
            self.everbridge.delete_contacts(contacts)

    def _handle_upsert(self, group_id, tracker):
        """
        Upserts contacts and adds newly inserted members to group
        """
        updated = tracker.get_upsert_contacts()
        if not updated:
            return
        self.everbridge.upsert_contacts(updated)
        new_members = []
        # Retrieve Everbridge IDs for newly inserted contacts
        # ids are given per 100
        for ids in tracker.get_inserted_contact_external_ids():
            contacts = self.everbridge.get_contacts_by_external_ids(ids)
            new_members += [con['id'] for con in contacts]
        if new_members:
            self.everbridge.add_members_to_group(group_id, new_members)
            tracker.set_new_members(new_members)
