import mock
import pytest
import sys 
import os
import json
from adal import AdalError
sys.path.append(os.path.abspath("../sync_ad_to_everbridge"))
from sync_ad_to_everbridge import *
config = json.load(open("testConfig.json"))

#Expected: Will return None because secret is wrong
def test_AzureFailCredientials():
    with pytest.raises(AdalError):
        data = get_AzureGroups("https://login.microsoftonline.com/",
            config["adTenant"],config["clientId"],"", "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],config["adGroupId"])
#Expected: Will return None because there is no group with matching name
def test_AzureFailGroupFinder():
    data = get_AzureGroups("https://login.microsoftonline.com/",
            config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/","","")
    assert(data is None)
def test_AzureCorrectGroupFinder():
    data = get_AzureGroups("https://login.microsoftonline.com/",
            config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],"")
    assert(len(data) > 0)
def test_AzureCorrectGroupFinderId():
    data = get_AzureGroups("https://login.microsoftonline.com/",
            config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/","",config["adGroupId"])
    assert(len(data) > 0)
def test_EverbridgeFailLogin():
    