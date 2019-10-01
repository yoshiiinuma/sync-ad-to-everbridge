"""
Tests Contact Utility functions
"""
import copy
from api.contact_utils import normalize_phone
from api.contact_utils import is_valid_phone
from api.contact_utils import is_valid_email
from api.contact_utils import get_names_from_email
from api.contact_utils import get_names_from_displayname
from api.contact_utils import validate_name
from api.contact_utils import validate_paths
from api.contact_utils import validate_azure_contact
from api.contact_utils import fix_azure_contact
from api.contact_utils import fill_azure_contact
from api.contact_utils import convert_to_everbridge
from api.contact_utils import extract_attributes_for_comparison
from api.contact_utils import is_different
from api.contact_utils import ContactValidationResult
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

def test_is_valid_phone():
    """
    Should return true if given phone number is valid
    """
    assert not is_valid_phone('1')
    assert not is_valid_phone('12')
    assert not is_valid_phone('123')
    assert not is_valid_phone('123456789')
    assert not is_valid_phone('12345678901')
    assert not is_valid_phone('123456789x')
    assert not is_valid_phone('123456789z')
    assert is_valid_phone('1234567890')
    assert is_valid_phone('1234567890x999')

def test_is_valid_email():
    """
    Should return true if given email is valid
    """
    assert is_valid_email('abc.efg@test.com')
    assert is_valid_email('Abc-Efg@test.com')
    assert is_valid_email('abc.efg@test.co.jp')
    assert not is_valid_email('@')
    assert not is_valid_email('abc.efg@@test.com')
    assert not is_valid_email('abc.efg@test..com')
    assert not is_valid_email('abc efg@test.com')
    assert not is_valid_email('abc.efg@ test.com')

def test_get_names_from_email():
    """
    Should return first and last name extracted from displayName
    """
    assert get_names_from_email('') == [None, None]
    assert get_names_from_email('Aaaa Bbbb') == [None, None]
    assert get_names_from_email('Aaaa@test.com') == [None, None]
    assert get_names_from_email('Aaaa.Bbbb@test.com') == ['Aaaa', 'Bbbb']
    assert get_names_from_email('Aaaa.c.Bbbb@test.com') == ['Aaaa', 'Bbbb']

def test_get_names_from_displayname():
    """
    Should return first and last name extracted from displayName
    """
    assert get_names_from_displayname('Aaaa Bbbb') == ['Aaaa', 'Bbbb']
    assert get_names_from_displayname('  Aaaa    Bbbb   ') == ['Aaaa', 'Bbbb']
    assert get_names_from_displayname('Aaaa Bbbb Cccc') == ['Aaaa', 'Bbbb.Cccc']

def test_validate_name_with_valid_name():
    """
    Should return no error messages but valid name
    """
    # Valid userPrincipalName
    rslt = ContactValidationResult()
    con = {'userPrincipalName': 'abc.efg@test.com'}
    validate_name(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == ['NameExtractedFromEmail']
    assert rslt.first == 'abc'
    assert rslt.last == 'efg'
    assert rslt.has_valid_name()
    # Valid displayName
    rslt = ContactValidationResult()
    con = {'displayName': 'Aaaa Bbbb Cccc'}
    validate_name(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == ['NameExtractedFromDisplayName']
    assert rslt.first == 'Aaaa'
    assert rslt.last == 'Bbbb.Cccc'
    assert rslt.has_valid_name()
    # Valid name
    rslt = ContactValidationResult()
    con = {'userPrincipalName': 'abc.def@test.com',
           'givenName': 'Aaaa',
           'surname': 'Bbbb',
           'displayName': 'Ccc Ddd',
           'businessPhones': ['123456789X', '123456789Y'],
           'mobilePhone': '123456789Z'}
    validate_name(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == []
    assert rslt.first == 'Aaaa'
    assert rslt.last == 'Bbbb'
    assert rslt.has_valid_name()

def test_validate_name_with_invalid_data():
    """
    Should return appropriate error messages
    """
    # Invalid userPrincipalName
    rslt = ContactValidationResult()
    con = {'userPrincipalName': 'abcefg@test..com'}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # Empty userPrincipalName
    rslt = ContactValidationResult()
    con = {'userPrincipalName': ''}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # No Name Provided
    rslt = ContactValidationResult()
    con = {}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # Only Invalid displayName
    rslt = ContactValidationResult()
    con = {'displayName': 'Aaaa'}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # Empty givenName and surname
    rslt = ContactValidationResult()
    con = {'givenName': '', 'surname': ''}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # Empty givenName and surname and displayName
    rslt = ContactValidationResult()
    con = {'givenName': '', 'surname': '', 'displayName': ''}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    # Empty givenName and surname and Invalid displayName
    rslt = ContactValidationResult()
    con = {'givenName': '', 'surname': '', 'displayName': 'Aaaa'}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()

def test_validate_paths_with_valid_data():
    """
    Should return appropriate error messages
    """
    # Valid userPrincipalName
    rslt = ContactValidationResult()
    con = {'userPrincipalName': 'abc.efg@test.com'}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == []
    assert rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert rslt.email == 'abc.efg@test.com'
    assert not rslt.mobile_phone
    assert rslt.has_valid_paths()
    # Valid business phone
    rslt = ContactValidationResult()
    con = {'businessPhones': ['1234567890', '1234567891']}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == []
    assert rslt.has_valid_paths()
    assert rslt.business_phones == ['1234567890', '1234567891']
    assert not rslt.email
    assert not rslt.mobile_phone
    assert rslt.has_valid_paths()
    # Valid mobile phone
    rslt = ContactValidationResult()
    con = {'mobilePhone': '1234567890'}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == []
    assert rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert rslt.mobile_phone == '1234567890'
    assert rslt.has_valid_paths()

def test_validate_paths_with_invalid_data():
    """
    Should return appropriate error messages
    """
    # No Path
    rslt = ContactValidationResult()
    con = {}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == []
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    # Invalid userPrincipalName
    rslt = ContactValidationResult()
    con = {'userPrincipalName': 'abc.efg@test..com'}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidUserPrincipalName:abc.efg@test..com']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    rslt = ContactValidationResult()
    con = {'userPrincipalName': ''}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidUserPrincipalName:']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()

def test_validate_paths_with_invalid_business_phone():
    """
    Should return appropriate error messages
    """
    # No business phone
    rslt = ContactValidationResult()
    con = {'businessPhones': []}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == []
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    # Invalid business phone
    rslt = ContactValidationResult()
    con = {'businessPhones': ['12345']}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidBusinessPhone:12345']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    rslt = ContactValidationResult()
    con = {'businessPhones': ['']}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidBusinessPhone:']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    rslt = ContactValidationResult()
    con = {'businessPhones': ['abcde', '1234567890']}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == ['InvalidBusinessPhone:abcde']
    assert rslt.has_valid_paths()
    assert rslt.business_phones == ['1234567890']
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.email
    assert not rslt.mobile_phone
    assert rslt.has_valid_paths()

def test_validate_paths_with_invalid_mobile_phone():
    """
    Should return appropriate error messages
    """
    # Invalid mobile phone
    rslt = ContactValidationResult()
    con = {'mobilePhone': '12345'}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidMobilePhone:12345']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    rslt = ContactValidationResult()
    con = {'mobilePhone': ''}
    validate_paths(con, rslt)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == ['InvalidMobilePhone:']
    assert not rslt.has_valid_paths()
    assert rslt.business_phones == []
    assert not rslt.email
    assert not rslt.mobile_phone
    assert not rslt.has_valid_paths()
    rslt = ContactValidationResult()
    con = {'businessPhones': ['1234567890'], 'mobilePhone': '12345'}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == ['InvalidMobilePhone:12345']
    assert rslt.has_valid_paths()
    assert rslt.business_phones == ['1234567890']
    assert not rslt.email
    assert not rslt.mobile_phone
    assert rslt.has_valid_paths()

def test_validate_azure_contact_with_valid_data():
    """
    Should return true if contact is valid
    """
    # Valid contact
    con = {'userPrincipalName': 'abc.def@test.com',
           'givenName': 'abc',
           'surname': 'def',
           'displayName': 'abc def',
           'businessPhones': ['1234567890', '1234567891'],
           'mobilePhone': '1234567892'}
    rslt = validate_azure_contact(con)
    assert rslt.errors == []
    assert rslt.warnings == []
    assert rslt.has_valid_paths()
    assert rslt.email == 'abc.def@test.com'
    assert rslt.business_phones == ['1234567890', '1234567891']
    assert rslt.mobile_phone == '1234567892'
    assert rslt.first == 'abc'
    assert rslt.last == 'def'
    assert rslt.has_valid_name()
    assert rslt.has_valid_paths()

def test_validate_azure_contact_with_invalid_data():
    """
    Should return true if contact is valid
    """
    # No valid name
    con = {'userPrincipalName': 'abcdef@test...com',
           'displayName': 'abcdef',
           'businessPhones': ['1234567890', '1234567891'],
           'mobilePhone': '1234567892'}
    rslt = validate_azure_contact(con)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == ['InvalidUserPrincipalName:abcdef@test...com']
    assert rslt.has_valid_paths()
    assert not rslt.email
    assert rslt.business_phones == ['1234567890', '1234567891']
    assert rslt.mobile_phone == '1234567892'
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    assert rslt.has_valid_paths()
    # No valid name
    con = {'userPrincipalName': 'abcdef@test.com',
           'businessPhones': ['1234567890', '1234567891'],
           'mobilePhone': '1234567892'}
    rslt = validate_azure_contact(con)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert rslt.has_valid_paths()
    assert rslt.email == 'abcdef@test.com'
    assert rslt.business_phones == ['1234567890', '1234567891']
    assert rslt.mobile_phone == '1234567892'
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()
    assert rslt.has_valid_paths()
    # No valid path
    con = {'userPrincipalName': 'abc.def@test..com',
           'givenName': 'abc',
           'surname': 'def',
           'displayName': 'abc def',
           'businessPhones': ['123456789X', '123456789Y'],
           'mobilePhone': '123456789Z'}
    rslt = validate_azure_contact(con)
    assert rslt.errors == ['NoPathFound']
    assert rslt.warnings == [
        'InvalidUserPrincipalName:abc.def@test..com',
        'InvalidBusinessPhone:123456789X',
        'InvalidBusinessPhone:123456789Y',
        'InvalidMobilePhone:123456789Z']
    assert not rslt.has_valid_paths()
    assert not rslt.email
    assert rslt.business_phones == []
    assert not rslt.mobile_phone
    assert rslt.first == 'abc'
    assert rslt.last == 'def'
    assert rslt.has_valid_name()
    assert not rslt.has_valid_paths()
    # One valid path
    con = {'givenName': 'abc',
           'surname': 'def',
           'businessPhones': ['123456789X', '123456789Y'],
           'mobilePhone': '1234567892'}
    rslt = validate_azure_contact(con)
    assert rslt.errors == []
    assert rslt.warnings == ['InvalidBusinessPhone:123456789X', 'InvalidBusinessPhone:123456789Y']
    assert rslt.has_valid_paths()
    assert not rslt.email
    assert rslt.business_phones == []
    assert rslt.mobile_phone == '1234567892'
    assert rslt.first == 'abc'
    assert rslt.last == 'def'
    assert rslt.has_valid_name()
    assert rslt.has_valid_paths()

def test_fix_azure_contact():
    """
    Should fix invalid valuds in AD Contact
    """
    con = {'userPrincipalName': 'abc.def@test.com',
           'businessPhones': ['+1(808)1234567', '567-9999', '1234444 x 888'],
           'mobilePhone': '+1 (808) 123 - 4567 x 9999'}
    validated = validate_azure_contact(con)
    fix_azure_contact(con, validated)
    assert con['userPrincipalName'] == 'abc.def@test.com'
    assert con['givenName'] == 'abc'
    assert con['surname'] == 'def'
    assert con['businessPhones'] == ['8081234567', '8085679999', '8081234444x888']
    assert con['mobilePhone'] == '8081234567x9999'

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
        'surname': 'XXXXX',
        'userPrincipalName': 'XXX_MISSINGMAIL_XXX.AAA.XXXXX@hawaii.gov',
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
