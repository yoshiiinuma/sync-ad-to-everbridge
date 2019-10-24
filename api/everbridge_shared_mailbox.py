import re
def get_parent_group(ev_parent_name, Synchronizer, user):
    search_query = re.sub(r'@|\.', '', str(user['mail']))
    gid_ev = Synchronizer.everbridge.get_group_id_by_name(ev_parent_name)
    # Create Everbridge parent group if  group does not exist
    if not gid_ev:
        gid_ev = Synchronizer._create_new_everbridge_group(ev_parent_name)
    parent_group = Synchronizer.everbridge.get_group_id_by_name(search_query)
    return parent_group

def get_child_group(child_id, everbridge):
    print("Hello")

def del_extra_groups():
    print("Hello")