"""
Provides iterator for azure group members
"""
from api.base_iterator import BaseIterator
from api.azure import Azure
from api.contact_utils import fill_azure_contact

class AzureGroupMemberIterator(BaseIterator):
    """
    Iterates azure group members
    """
    def __init__(self, api, group_id):
        super().__init__(api, group_id)
        self.pagesize = Azure.DEFAULT_PAGESIZE

    def __next__(self):
        """
        Returns next azure group member object
        """
        obj = super().__next__()
        if obj:
            fill_azure_contact(obj)
        return obj
