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
    # pylint: disable=too-many-instance-attributes
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


    def _get_next_page(self):
        """
        Fetches paged group members
        """
        if self.no_more_data:
            return
        self.current_page += 1
        self.members = self.api.get_paged_group_members(self.group_id, self.current_page)
        self.index = 0
        self.nom = len(self.members)
        # no more data if the number of memebers from the last fetch is 0
        if self.nom == 0:
            self.no_more_data = True
