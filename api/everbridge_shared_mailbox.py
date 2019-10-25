import re
def get_parent_group(ev_parent_name, Synchronizer):
    parent_group_id = Synchronizer.everbridge.get_group_id_by_name(ev_parent_name)
    # Create Everbridge parent group if  group does not exist
    if not parent_group_id:
        parent_group_id = Synchronizer._create_new_everbridge_group(ev_parent_name)
        return parent_group_id
    
def process_shared_mailboxes(ad_user_ids, Synchronizer):
    print("Hello")

def get_shared_mailbox():
    print("Hello")

def delete_shared_mailbox():
    print("Hello")