"""
Tests Contact Utility functions
"""
from api.contact_utils import normalize_phone
from api.contact_utils import fill_azure_contact
from api.contact_utils import convert_to_everbridge
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
        'businessPhones': ['8081112222', '8081113333'],
        'mobilePhone': '8081114444'}
    exp = {
        'firstName': 'AAA',
        'lastName': 'BBB',
        'externalId': 'AAA.BBB@hawaii.gov',
        'recordTypeId': 892807736729062,
        'paths': [
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
                'value': 'AAA.BBB@hawaii.gov', 'skipValidation': 'false'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081112222', 'skipValidation': 'false'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
                'countryCode': 'US', 'value': '8081113333', 'skipValidation': 'false'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': 'false'
            },
            {
                'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
                'countryCode': 'US', 'value': '8081114444', 'skipValidation': 'false'
            }
        ]}
    converted = convert_to_everbridge(con)
    assert converted == exp
