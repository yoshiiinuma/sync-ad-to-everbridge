import pytest
import sys 
import os
import json
import requests
from adal import AdalError
import inspect
from datetime import datetime
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import api.azure_api
config = json.load(open(currentdir + "/testConfig.json"))

#Expected: Will return None because secret is wrong
def test_AzureFailCredientials():
	with pytest.raises(AdalError):
		data = api.azure_api.get_AzureGroups("https://login.microsoftonline.com/",
		config["adTenant"],config["clientId"],"", "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],config["adGroupId"])
#Expected: Will return None because there is no group with matching name
def test_AzureFailGroupFinder():
	data = api.azure_api.get_AzureGroups("https://login.microsoftonline.com/",
	config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/","","")
	assert(data is None)
#Exptected: Will return a array of members of a group through group name
def test_AzureCorrectGroupFinder():
	data = api.azure_api.get_AzureGroups("https://login.microsoftonline.com/",
	config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],"")
	assert(len(data) > 0)
#Exptected: Will return a array of members of a group through group Id
def test_AzureCorrectGroupFinderId():
	data = api.azure_api.get_AzureGroups("https://login.microsoftonline.com/",
	config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/","",config["adGroupId"])
	assert(len(data) > 0)
