"""
Provides iterator for azure group members
"""
import math
from . import base_iterator 
from . import azure

class AzureGroupMemberIterator(base_iterator.BaseIterator):
    """
    Iterates azure group members
    """
    def __init__(self, api, group_id):
        super().__init__(api, group_id)
        self.pagesize = azure.Azure.DEFAULT_PAGESIZE
        self.first_time = True

    # Graph API currently does not support OrderBy
    # Use Azure.get_sorted_group_members instead of get_paged_group_members
    # Delete this function after it does
    def _get_next_page(self):
        """
        Fetches paged group members
        """
        if self.no_more_data:
            return
        if self.first_time:
            self.members = self.api.get_sorted_group_members(self.group_id)
            self.index = 0
            self.nom = len(self.members)
            self.current_page = math.ceil(self.nom / self.pagesize)
            self.first_time = False
        else:
            self.nom = 0
            self.no_more_data = True
