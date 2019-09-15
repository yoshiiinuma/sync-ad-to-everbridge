"""
Provides iterator for everbridge group members
"""
from api.base_iterator import BaseIterator
from api.everbridge import Everbridge

class EverbridgeGroupMemberIterator(BaseIterator):
    """
    Iterates everbridge group members
    """
    def __init__(self, api, group_id):
        super().__init__(api, group_id)
        self.pagesize = Everbridge.DEFAULT_PAGESIZE
