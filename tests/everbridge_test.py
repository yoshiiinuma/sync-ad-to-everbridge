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
CONFIG = json.load(open(CURRENTDIR + "/testConfig.json"))
def test_everbridgeauth():
    """
    Expected: Will return a 401 header due to lack of org ID
    """
    header = api.everbridge_api.create_authheader("Test", "Test")
    resp = requests.get("https://api.everbridge.net/rest/organizations",
                        data=None,
                        headers=header).json()
    assert resp["status"] == 401
def test_everbridgeorg():
    """
    Expected: Will return a 401 header due to incorrect Org ID
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    resp = requests.get('https://api.everbridge.net/rest/contacts/' +"123456778" + '/',
                        data=None, headers=header).json()
    assert resp["status"] == 401
def test_everbridgecontacts():
    """
    Expected: Will return a list of all contacts in the org
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    resp = requests.get('https://api.everbridge.net/rest/contacts/'
                        + CONFIG["everbridgeOrg"]
                        + '/', data=None, headers=header).json()
    assert resp['message'] == 'OK' and resp['page']['totalCount'] > 300
def test_everbridgefilter():
    """
    Expected: Will return exactly one contact using a search filter
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    filtertest = api.everbridge_api.create_filter("Tyler", "Aratani",
                                                  'https://api.everbridge.net/rest/contactFilters/'
                                                  + CONFIG["everbridgeOrg"] +'/', header)
    resp = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/'
                                             + CONFIG["everbridgeOrg"]
                                             + '/?sortBy="lastName"&searchType=OR&contactFilterIds='
                                             + str(filtertest["id"]),
                                             header, None)
    api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/contactFilters/'
                                         + CONFIG["everbridgeOrg"] + '/'
                                         + str(filtertest["id"]), header, None)
    assert resp["page"]["totalCount"] == 2
def test_invalidcontact():
    """
    Expected: Will return a HTTP error due to invalid phone number for US
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    counter = api.everbridge_api.STATEMENT(0,0,0)
    user = api.everbridge_api.create_user("Invalid",
                                    "PhoneTest",
                                    ["808-1111-1111"],
                                    "PythonTest@hawallig.gov",
                                    'https://api.everbridge.net/rest/contacts/'
                                    + CONFIG["everbridgeOrg"]
                                    + '/', header, counter)
    assert user["message"] ==  'Phone number format invalid for selected country.'
def test_insertanddeletecontact():
    """
    Expected: Will return a ok message as the new contact will be created then deleted
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    counter = api.everbridge_api.STATEMENT(0,0,0)
    newuser = api.everbridge_api.create_user("Invalid",
                                             "PhoneTest",
                                             ["8087278435"],
                                             "PythonTest@hawaii.gov",
                                             'https://api.everbridge.net/rest/contacts/'
                                             + CONFIG["everbridgeOrg"] + '/', header, counter)
    infouser = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/'
                                                 + CONFIG["everbridgeOrg"] + '/'
                                                 + str(newuser["id"]), header, None)
    assert infouser["result"]["firstName"] == "Invalid"
    delrequests = api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/contacts/'
                                                       + CONFIG["everbridgeOrg"] + '/'
                                                       + str(newuser["id"]), header, None)
    assert delrequests["message"] == "OK"
def test_addandremovefromgroup():
    """
    Expected: Will create a new user and add that user to the group
    """
    header = api.everbridge_api.create_authheader(CONFIG["everbridgeUsername"],
                                                  CONFIG["everbridgePassword"])
    counter = api.everbridge_api.STATEMENT(0,0,0)
    newuser = api.everbridge_api.create_user("TestTest", "Automated", ["8087278435"],
                                             "NewTest@hawaii.gov",
                                             'https://api.everbridge.net/rest/contacts/'
                                             + CONFIG["everbridgeOrg"] + '/', header, counter)
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    originalnumber = evergroup["page"]["totalCount"]
    api.everbridge_api.add_contacts(CONFIG["everbridgeOrg"],
                                    CONFIG["everbridgeGroup"],
                                    header, [newuser["id"]])
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    assert evergroup["page"]["totalCount"] == originalnumber + 1
    api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/groups/'
                                         + CONFIG["everbridgeOrg"]
                                         + '/contacts?byType=name&groupName='
                                         + CONFIG["everbridgeGroup"]
                                         + '&idType=id', header, [newuser["id"]])
    evergroup = api.everbridge_api.get_everbridge('https://api.everbridge.net/rest/contacts/groups/'
                                                  + CONFIG["everbridgeOrg"]
                                                  + '?byType=name&groupName='
                                                  + CONFIG["everbridgeGroup"] +
                                                  '&pageSize=100&pageNumber=1', header, None)
    assert evergroup["page"]["totalCount"] == originalnumber
    delquests = api.everbridge_api.delete_everbridge('https://api.everbridge.net/rest/contacts/'
                                                     + CONFIG["everbridgeOrg"]
                                                     + '/' + str(newuser["id"]), header, None)
    assert delquests["message"] == "OK"
    