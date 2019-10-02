"""
Provides iterator for everbridge group members
"""
from . import base_iterator
from . import everbridge

class EverbridgeGroupMemberIterator(base_iterator.BaseIterator):
    """
    Iterates everbridge group members
    """
    def __init__(self, api, group_id):
        super().__init__(api, group_id)
        self.pagesize = everbridge.Everbridge.DEFAULT_PAGESIZE
