import pytest
import sys 
import os
import json
import requests
import inspect
from requests import HTTPError
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import api.everbridge_api
config = json.load(open(currentdir + "/testConfig.json"))
#Expected: Will return a 401 header due to lack of org ID  
def test_EverbridgeAuth():
	header = api.everbridge_api.create_AuthHeader("Test","Test")
	resp = requests.get("https://api.everbridge.net/rest/organizations", data=None,headers=header).json()
	assert(resp["status"] == 401)
#Expected: Will return a 401 header due to incorrect Org ID
def test_EverbridgeOrg():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	resp = requests.get('https://api.everbridge.net/rest/contacts/' +"123456778" + '/', data=None,headers=header).json()
	assert(resp["status"] == 401)
#Expected: Will return a list of all contacts in the org
def test_EverbridgeContacts():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	resp = requests.get('https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"]+ '/', data=None,headers=header).json()
	assert(resp['message'] == 'OK' and resp['page']['totalCount'] > 300)
#Expected: Will return exactly one contact using a search filter
def test_EverbridgeFilter():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	filterTest = api.everbridge_api.create_filter("Tyler","Aratani",'https://api.everbridge.net/rest/contactFilters/' + config["everbridgeOrg"] +'/',header)
	resp = api.everbridge_api.get_EverBridge('https://api.everbridge.net/rest/contacts/'+ config["everbridgeOrg"] + '/?sortBy="lastName"&searchType=OR&contactFilterIds=' + str(filterTest["id"]),header,None)
	api.everbridge_api.delete_Everbridge('https://api.everbridge.net/rest/contactFilters/' + config["everbridgeOrg"] + '/' + str(filterTest["id"]),header,None) 
	assert(resp["page"]["totalCount"] == 2)
#Expected: Will return a HTTP error due to invalid phone number for US
def test_InvalidContact():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	with pytest.raises(HTTPError):
		newUser = api.everbridge_api.create_user("Invalid","PhoneTest",["8081234567"],"PythonTest@hawallig.gov",'https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/',header)
#Expected: Will return a ok message as the new contact will be created then deleted
def test_InsertAndDeleteContact():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	newUser = api.everbridge_api.create_user("Invalid","PhoneTest",["8087278435"],"PythonTest@hawaii.gov",'https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/',header)
	infoUser =  api.everbridge_api.get_EverBridge('https://api.everbridge.net/rest/contacts/'+ config["everbridgeOrg"] + '/' + str(newUser["id"]),header,None)
	assert(infoUser["result"]["firstName"] == "Invalid")
	deleteRequests = api.everbridge_api.delete_Everbridge('https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/' + str(newUser["id"]),header,None)
	assert(deleteRequests["message"] == "OK")
#Expected: Will create a new user and add that user to the group 
def test_AddAndRemoveFromGroup():
	header = api.everbridge_api.create_AuthHeader(config["everbridgeUsername"],config["everbridgePassword"])
	newUser = api.everbridge_api.create_user("TestTest","Automated",["8087278435"],"NewTest@hawaii.gov",'https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/',header)
	everGroup = api.everbridge_api.get_EverBridge('https://api.everbridge.net/rest/contacts/groups/' + config["everbridgeOrg"] + '?byType=name&groupName=' + config["everbridgeGroup"] + 
	'&pageSize=100&pageNumber=1',header,None)
	originalNumber = everGroup["page"]["totalCount"]
	api.everbridge_api.add_contacts(config["everbridgeOrg"],config["everbridgeGroup"],header,[newUser["id"]])
	everGroup = api.everbridge_api.get_EverBridge('https://api.everbridge.net/rest/contacts/groups/' + config["everbridgeOrg"] + '?byType=name&groupName=' + config["everbridgeGroup"] + 
	'&pageSize=100&pageNumber=1',header,None)
	assert(everGroup["page"]["totalCount"] == originalNumber + 1)
	api.everbridge_api.delete_Everbridge('https://api.everbridge.net/rest/groups/' + config["everbridgeOrg"] + '/contacts?byType=name&groupName=' + config["everbridgeGroup"]
	 + '&idType=id',header,[newUser["id"]])
	everGroup = api.everbridge_api.get_EverBridge('https://api.everbridge.net/rest/contacts/groups/' + config["everbridgeOrg"] + '?byType=name&groupName=' + config["everbridgeGroup"] + 
	'&pageSize=100&pageNumber=1',header,None)
	assert(everGroup["page"]["totalCount"] == originalNumber)
	deleteRequests = api.everbridge_api.delete_Everbridge('https://api.everbridge.net/rest/contacts/' + config["everbridgeOrg"] + '/' + str(newUser["id"]),header,None)
	assert(deleteRequests["message"] == "OK")
	 
