"""
Provides iterator for azure group members
"""

class BaseIterator:
    """
    Iterates azure group members
    WARNING: Expects api supports set_pagesize method; override set_pagesize if not
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, api, group_id):
        self.api = api
        self.group_id = group_id
        self.current_page = 0
        self.members = []
        self.index = 0
        self.nom = 0 # the number of the current members
        self.total = 0
        self.no_more_data = False
        self.pagesize = 100

    # pylint: disable=no-self-use
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

    def __iter__(self):
        """
        Returns self when gets called by iter
        """
        return self

    def __next__(self):
        """
        Returns next group member object
        """
        self.show()
        if self.no_more_data:
            return None
        if self.index >= self.nom:
            self._get_next_page()
        if self.nom == 0:
            return None
        next_obj = self.members[self.index]
        self.index += 1
        self.total += 1
        # no more data if the # of memebers from the last fetch is smaller than the page size
        if self.total > 0 and self.nom < self.pagesize and self.nom == self.index:
            self.no_more_data = True
        return next_obj

    def get_total(self):
        """
        Returns the total count
        """
        return self.total

    def get_group_id(self):
        """
        Returns the group_id
        """
        return self.group_id

    def set_pagesize(self, pagesize):
        """
        Sets pagesize
        WARNING: Expects api supports set_pagesize method
        """
        self.pagesize = pagesize
        self.api.set_pagesize(pagesize)

    def show(self):
        """
        Prints the status of the instance
        """
        status = f"page: {self.current_page}, total: {self.total}, index: {self.index}, "
        status += f"member: {self.nom}, psize: {self.pagesize}"
        print(status)
