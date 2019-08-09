"""
Test Azure Functions
"""
import sys
import os
import json
import inspect
import pytest
from adal import AdalError
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)
import api.azure_api
CONFIG = json.load(open(CURRENTDIR + "/testConfig.json"))

def test_azurefailcredientials():
    """
    Expected: Will return None because secret is wrong
    """
    with pytest.raises(AdalError):
        api.azure_api.get_azuregroups(CONFIG["adTenant"],
                                      CONFIG["clientId"],
                                      "",
                                      "https://graph.microsoft.com/v1.0/groups/")
def test_azurefailgroupfinder():
    """
    Expected: Will return None because there is no group with matching name
    """
    data = api.azure_api.get_azuregroups(CONFIG["adTenant"],
                                         CONFIG["clientId"],
                                         CONFIG["clientSecret"],
                                         "https://graph.microsoft.com/v1.0/groups/" + "ABC" + "/members")
    assert data is None
def test_azurecorrectgroupfinder():
    """
    Exptected: Will return a array of members of a group through group name
    """
    data = api.azure_api.get_azuregroups(CONFIG["adTenant"],
                                         CONFIG["clientId"],
                                         CONFIG["clientSecret"],
                                         "https://graph.microsoft.com/v1.0/groups/" + CONFIG["adGroupId"] + "/members")
    assert data
