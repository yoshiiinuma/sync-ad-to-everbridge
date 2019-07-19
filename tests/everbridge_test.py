import mock
import pytest
import sys 
import os
import json
import requests
from adal import AdalError
from requests.exceptions import HTTPError 
sys.path.append(os.path.abspath("../sync_ad_to_everbridge"))
from sync_ad_to_everbridge import *
config = json.load(open("testConfig.json"))

#Expected: Will return a 401 header due to lack of org ID  
def test_EverbridgeAuth():
	header = create_AuthHeader("Test","Test")
	resp = requests.get("https://api.everbridge.net/rest/organizations", data=None,headers=header).json()
	assert(resp["status"] == 401)
#Expected: Will return a 401 header due to incorrect Org ID
def test_EverbridgeOrg():
	header = create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	resp = requests.get('https://api.everbridge.net/rest/contacts/' +"123456778" + '/', data=None,headers=header).json()
	assert(resp["status"] == 401)
#Expected: Will return a list of all contacts in the org
def test_EverbridgeContacts():
	header = create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	resp = requests.get('https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"]+ '/', data=None,headers=header).json()
	assert(resp['message'] == 'OK' and resp['page']['totalCount'] > 300)
#Expected: Will return exactly one contact using a search filter
def test_EverbridgeFilter():
	header = create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	filterTest = create_filter("Tyler","Aratani",'https://api.everbridge.net/rest/contactFilters/' + config["everbridgeOrg"] +'/',header)
	resp = get_EverBridge('https://api.everbridge.net/rest/contacts/'+ config["everbridgeOrg"] + '/?sortBy="lastName"&searchType=OR&contactFilterIds=' + str(filterTest["id"]),header,None)
	delete_Everbridge('https://api.everbridge.net/rest/contactFilters/' + config["everbridgeOrg"] + '/' + str(filterTest["id"]),header,None) 
	assert(resp["page"]["totalCount"] == 2)
def test_InvalidContact():
	header = create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	with pytest.raises(HTTPError):
		newUser = create_user("Invalid","PhoneTest",["8081234567"],"PythonTest@hawallig.gov",'https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/',header)
def test_DeleteContact():
	header = create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	newUser = create_user("Invalid","PhoneTest",["8087278435"],"PythonTest@hawallig.gov",'https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/',header)
	deleteRequests = delete_Everbridge('https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/' + str(newUser["id"]),header,None)
	assert(deleteRequests["message"] == "OK")
	
