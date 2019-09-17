"""
Tests Contact Utility functions
"""
import copy
from api.contact_utils import normalize_phone
from api.contact_utils import fill_azure_contact
from api.contact_utils import convert_to_everbridge
from api.contact_utils import extract_attributes_for_comparison
from api.contact_utils import is_different
# pylint: disable=unused-import
import tests.log_helper

def test_normalzie_phone():
    """
    Should return normalized phone number
    """
    assert normalize_phone(' +1 (808) 111 - 2222 ') == '8081112222'
    assert normalize_phone('+1(808)111-2222') == '8081112222'
    assert normalize_phone('(808)111-2222') == '8081112222'
    assert normalize_phone('111-2222') == '8081112222'
    assert normalize_phone('1112222') == '8081112222'
    assert normalize_phone('2222') == '2222'
    assert normalize_phone(2222) == '2222'
    assert normalize_phone('') == ''
    assert normalize_phone(None) == ''

def test_fill_azure_contact_with_multiple_space_displayname():
    """
    Should fill missing info in AD Contact
    """
    con = {'displayName': 'AAA BBB CCC DDD'}
    exp = {
        'displayName': 'AAA BBB CCC DDD',
        'givenName': 'AAA',
        'surname': 'BBBCCCDDD',
        'userPrincipalName': 'XXX_MISSINGMAIL_XXX.AAA.BBBCCCDDD@hawaii.gov',
        'businessPhones': []}
    fill_azure_contact(con)
    assert con == exp

def test_fill_azure_contact_with_no_space_displayname():
    """
    Should fill missing info in AD Contact
    """
    con = {'displayName': 'AAA'}
    exp = {
        'displayName': 'AAA',
        'givenName': 'AAA',
        'surname': 'None',
        'userPrincipalName': 'XXX_MISSINGMAIL_XXX.AAA.None@hawaii.gov',
        'businessPhones': []}
    fill_azure_contact(con)
    assert con == exp

def test_fill_azure_contact_with_anomalous_phonenumbers():
    """
    Should normalize phone numbers
    """
    con = {
        'displayName': 'AAA BBB',
        'givenName': 'AAA',
        'surname': 'BBB',
        'userPrincipalName': 'AAA.BBB@hawaii.gov',
        'businessPhones': [' +1 (808) 111-2222 ', '111-3333'],
        'mobilePhone': ' +1 (808) 111-4444 '}
    exp = {
        'displayName': 'AAA BBB',
        'givenName': 'AAA',
        'surname': 'BBB',
        'userPrincipalName': 'AAA.BBB@hawaii.gov',
        'mail': 'AAA.BBB@hawaii.gov',
        'businessPhones': ['8081112222', '8081113333'],
        'mobilePhone': '8081114444'}
    fill_azure_contact(con)
    assert con == exp

def test_convert_to_everbridge():
    """
    Should convert AD Contact to Everbridge Contact
    """
    con = {
        'displayName': 'AAA BBB',
        'givenName': 'AAA',
        'surname': 'BBB',
        'userPrincipalName': 'AAA.BBB@hawaii.gov',
        'businessPhones': ['8081112222x999', '8081113333x888'],
        'mobilePhone': '8081114444'}
    exp = {
        'firstName': 'AAA',
        'lastName': 'BBB',
        'externalId': 'AAA.BBB@hawaii.gov',
        'recordTypeId': 892807736729062,
        'paths': [
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
                'value': 'AAA.BBB@hawaii.gov', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081112222', 'skipValidation': False,
                'phoneExt': '999'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081113333', 'skipValidation': False,
                'phoneExt': '888'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            }
        ]}
    converted = convert_to_everbridge(con)
    assert converted == exp

def test_extract_attributes_for_comparison():
    """
    Should return Everbridge Contact which has the minimum set of attributes needed for comparison
    """
    con = {
        'attribute1': 'Attribute 1',
        'attribute2': 'Attribute 2',
        'attribute3': 'Attribute 3',
        'externalId': 'AAA.BBB@hawaii.gov',
        'id': '12345',
        'firstName': 'AAA',
        'lastName': 'BBB',
        'recordTypeId': 892807736729062,
        'paths': [
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
                'value': 'AAA.BBB@hawaii.gov', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081112222', 'skipValidation': False,
                'phoneExt': '999'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081113333', 'skipValidation': False,
                'phoneExt': '888'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            }
        ]}
    exp = {
        'externalId': 'AAA.BBB@hawaii.gov',
        'id': '12345',
        'firstName': 'AAA',
        'lastName': 'BBB',
        'recordTypeId': 892807736729062,
        'paths': [
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
                'value': 'AAA.BBB@hawaii.gov', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081112222', 'skipValidation': False,
                'phoneExt': '999'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081113333', 'skipValidation': False,
                'phoneExt': '888'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            }
        ]}
    extracted = extract_attributes_for_comparison(con)
    assert extracted == exp

def test_is_different():
    """
    Should return True if two Everbridge Contacts are different
    """
    contact = {
        'attribute1': 'Attribute 1',
        'attribute2': 'Attribute 2',
        'attribute3': 'Attribute 3',
        'externalId': 'AAA.BBB@hawaii.gov',
        'id': '12345',
        'firstName': 'AAA',
        'lastName': 'BBB',
        'recordTypeId': 892807736729062,
        'paths': [
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
                'value': 'AAA.BBB@hawaii.gov', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081112222', 'skipValidation': False,
                'phoneExt': '999'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081113333', 'skipValidation': False,
                'phoneExt': '888'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
            }
        ]}
    con1 = extract_attributes_for_comparison(contact)
    con2 = copy.deepcopy(con1)
    con2['paths'][1]['value'] = '8089999999'
    assert is_different(con1, contact) is False
    assert is_different(con2, contact) is True
