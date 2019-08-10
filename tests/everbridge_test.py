"""
Test Everbridge funtionallity
"""
import sys
import os
import json
import inspect
import pytest
import requests
from requests import HTTPError
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)
import api.everbridge_api
import api.everbridge_logic
CONFIG = json.load(open(CURRENTDIR + "/testConfig.json"))
def test_everbridgeauth():
    """
    Expected: Will return a 401 header due to invalid auth
    """
    header = api.everbridge_logic.create_authheader("Test", "Test")
    resp = requests.get("https://api.everbridge.net/rest/organizations",
                        data=None,
                        headers=header).json()
    assert resp["status"] == 401
def test_everbridgeorg():
    """
    Expected: Will return a 401 header due to incorrect Org ID
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    resp = requests.get('https://api.everbridge.net/rest/contacts/' +"123456778" + '/',
                        data=None, headers=header).json()
    assert resp["status"] == 401
def test_everbridgecontacts():
    """
    Expected: Will return a list of all contacts in the org
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    resp = requests.get('https://api.everbridge.net/rest/contacts/'
                        + CONFIG["everbridgeOrg"]
                        + '/', data=None, headers=header).json()
    assert resp['message'] == 'OK' and resp['page']['totalCount'] > 25
def test_everbridgefilter():
    """
    Expected: Will return exactly one contact using a search filter
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    filtertest = api.everbridge_logic.create_query([{"givenName":"Hello","surname":"Bye", "businessPhones":[], "mail":"evan.c.law@hawaii.gov","mobilePhone":None}])
    resp = api.everbridge_api.get_filtered_contacts(filtertest,header,CONFIG["everbridgeOrg"])
    assert resp["page"]["totalCount"] == 1
def test_invalidcontact():
    """
    Expected: Will return a HTTP error due to invalid phone number for US
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    user = api.everbridge_logic.create_contact({"givenName":"Invalid",
                                           "surname":"PhoneTest",
                                           "mail":"PythonTest@hawaii.gov",
                                           "businessPhones":["8081234567"], "mobilePhone":None})
    resp = api.everbridge_api.insert_new_contacts([user], CONFIG["everbridgeOrg"], header)
    assert resp["data"][0] ==  'The [1] Phone number format invalid for selected country.'
def test_insertanddeletecontact():
    """
    Expected: Will return a ok message as the new contact will be created then deleted
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    
    newuser = api.everbridge_logic.create_contact({"givenName":"Invalid",
                                              "surname":"PhoneTest",
                                              "mail":"PythonTest@hawaii.gov",
                                              "businessPhones":["8087278435"],"mobilePhone":None})
    api.everbridge_api.insert_new_contacts([newuser], CONFIG["everbridgeOrg"], header)
    infouser = api.everbridge_api.get_filtered_contacts("&externalIds=PythonTest@hawaii.gov", header, CONFIG["everbridgeOrg"])
    assert infouser["page"]["data"][0]["firstName"] == "Invalid"
    delrequests = api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/contacts/'
                                                       + CONFIG["everbridgeOrg"] + '/'
                                                       + str(infouser["page"]["data"][0]["id"]), header, None)
    assert delrequests["message"] == "OK"
def test_addandremovefromgroup():
    """
    Expected: Will create a new user and add that user to the group
    """
    header = api.everbridge_logic.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])    
    newuser = api.everbridge_logic.create_contact({"givenName":"TestTest",
                                              "surname":"Automated",
                                              "mail":"NewTest@hawaii.gov",
                                              "businessPhones":["8087278435"], "mobilePhone":None})
    api.everbridge_api.insert_new_contacts([newuser], CONFIG["everbridgeOrg"], header)
    infouser = api.everbridge_api.get_filtered_contacts("&externalIds=NewTest@hawaii.gov", header, CONFIG["everbridgeOrg"])
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    originalnumber = evergroup["page"]["totalCount"]
    testId = infouser["page"]["data"][0]["id"]
    insertResp = api.everbridge_api.add_contacts_to_group(CONFIG["everbridgeOrg"],
                                    CONFIG["everbridgeGroup"],
                                    header, [testId])
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    assert evergroup["page"]["totalCount"] == originalnumber + 1
    delrequests = api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/contacts/'
                                                        + CONFIG["everbridgeOrg"] + '/'
                                                        + str(infouser["page"]["data"][0]["id"]), header, None)
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    assert evergroup["page"]["totalCount"] == originalnumber
    assert delrequests["message"] == "OK"
    