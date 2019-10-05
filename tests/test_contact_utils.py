"""
Tests Contact Utility functions
"""
import copy
from api.contact_utils import convert_to_everbridge
from api.contact_utils import create_everbridge_contact_paths
from api.contact_utils import create_email_path
from api.contact_utils import create_business_phone_path
from api.contact_utils import create_mobile_phone_path
from api.contact_utils import create_sms_path
from api.contact_utils import extract_attributes_for_comparison
from api.contact_utils import is_different
# pylint: disable=unused-import
import tests.log_helper

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
        'mobilePhone': '8081114444',
        'mail':'AAA.BBB@hawaii.gov'}
    exp = {
        'errors': False,
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

def test_create_everbridge_contact_paths():
    """
    Should create Everbridge Contact paths
    """
    con = {
        'displayName': 'AAA BBB',
        'givenName': 'AAA',
        'surname': 'BBB',
        'userPrincipalName': 'AAA.BBB@hawaii.gov',
        'businessPhones': ['8081112222x999', '8081113333x888'],
        'mobilePhone': '8081114444',
        'mail':'AAA.BBB@hawaii.gov'}
    exp = [
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
    ]
    assert create_everbridge_contact_paths(con) == exp

def test_create_email_path():
    """
    Should Everbridge Email path
    """
    email = 'AAA.BBB@hawaii.gov'
    exp = {
        'waitTime': 0, 'status': 'A', 'pathId': 241901148045316,
        'value': 'AAA.BBB@hawaii.gov', 'skipValidation': False
    }
    assert create_email_path(email) == exp

def test_create_business_phone_path():
    """
    Should Everbridge business phone path
    """
    phone = '8081112222x999'
    exp = {
        'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
        'countryCode': 'US', 'value': '8081112222', 'skipValidation': False,
        'phoneExt': '999'
    }
    assert create_business_phone_path(phone) == exp
    phone = '8081114444'
    exp = {
        'waitTime': 0, 'status': 'A', 'pathId': 241901148045321,
        'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
    }
    assert create_business_phone_path(phone) == exp

def test_create_mobile_phone_path():
    """
    Should Everbridge mobile phone path
    """
    phone = '8081114444'
    exp = {
        'waitTime': 0, 'status': 'A', 'pathId': 241901148045319,
        'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
    }
    assert create_mobile_phone_path(phone) == exp

def test_create_sms_path():
    """
    Should Everbridge SMS path
    """
    phone = '8081114444'
    exp = {
        'waitTime': 0, 'status': 'A', 'pathId': 241901148045324,
        'countryCode': 'US', 'value': '8081114444', 'skipValidation': False
    }
    assert create_sms_path(phone) == exp

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
