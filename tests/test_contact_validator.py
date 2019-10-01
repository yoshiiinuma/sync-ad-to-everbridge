"""
Tests Contact Validator functions
"""
from api.contact_validator import normalize_phone
from api.contact_validator import is_valid_phone
from api.contact_validator import is_valid_email
from api.contact_validator import get_names_from_email
from api.contact_validator import get_names_from_displayname
from api.contact_validator import validate_name
from api.contact_validator import validate_paths
from api.contact_validator import validate_azure_contact
from api.contact_validator import fix_azure_contact
from api.contact_validator import validate_and_fix_azure_contact
from api.contact_validator import ContactValidationResult
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

def test_validate_name_with_invalid_userprincipalname():
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

def test_validate_name_with_invalid_displayname():
    """
    Should return appropriate error messages
    """
    # Only Invalid displayName
    rslt = ContactValidationResult()
    con = {'displayName': 'Aaaa'}
    validate_name(con, rslt)
    assert rslt.errors == ['NoNameFound']
    assert rslt.warnings == []
    assert not rslt.first
    assert not rslt.last
    assert not rslt.has_valid_name()

def test_validate_name_without_name():
    """
    Should return appropriate error messages
    """
    # No Name Provided
    rslt = ContactValidationResult()
    con = {}
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

def test_validate_paths_without_path_data():
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

def test_validate_paths_with_invalid_userprincipalname():
    """
    Should return appropriate error messages
    """
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

def test_validate_paths_without_userprincipalname():
    """
    Should return appropriate error messages
    """
    # Empty userPrincipalName
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

def test_validate_paths_without_business_phones():
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

def test_validate_paths_with_blank_business_phones():
    """
    Should return appropriate error messages
    """
    # Empty business phone
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

def test_validate_paths_with_invalid_business_phone():
    """
    Should return appropriate error messages
    """
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
    # Invalid business phone
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
    con = {'businessPhones': ['1234567890'], 'mobilePhone': '12345'}
    validate_paths(con, rslt)
    assert rslt.errors == []
    assert rslt.warnings == ['InvalidMobilePhone:12345']
    assert rslt.has_valid_paths()
    assert rslt.business_phones == ['1234567890']
    assert not rslt.email
    assert not rslt.mobile_phone
    assert rslt.has_valid_paths()

def test_validate_paths_with_blank_mobile_phone():
    """
    Should return appropriate error messages
    """
    # Empty mobile phone
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

def test_validate_azure_contact_with_invalid_name():
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
    # No valid name but valid as email
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

def test_validate_azure_contact_with_invalid_path():
    """
    Should return true if contact is valid
    """
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

def test_validate_and_fix_azure_contact():
    """
    Should fix invalid values in AD Contact
    """
    con = {'userPrincipalName': 'abc.def@test.com',
           'businessPhones': ['+1(808)1234567', '567-9999', '1234444 x 888'],
           'mobilePhone': '+1 (808) 123 - 4567 x 9999'}
    validate_and_fix_azure_contact(con)
    assert con['userPrincipalName'] == 'abc.def@test.com'
    assert con['givenName'] == 'abc'
    assert con['surname'] == 'def'
    assert con['businessPhones'] == ['8081234567', '8085679999', '8081234444x888']
    assert con['mobilePhone'] == '8081234567x9999'
    assert con['fixed']
    assert not con['errors']

def test_validate_and_fix_azure_contact_without_fix():
    """
    Should not fix any values in AD Contact
    """
    con = {'userPrincipalName': 'abc.def@test.com',
           'givenName': 'abc', 'surname': 'def',
           'businessPhones': ['8081234567', '8085679999', '8081234444x888'],
           'mobilePhone': '8081234567x9999'}
    validate_and_fix_azure_contact(con)
    assert con['userPrincipalName'] == 'abc.def@test.com'
    assert con['givenName'] == 'abc'
    assert con['surname'] == 'def'
    assert con['businessPhones'] == ['8081234567', '8085679999', '8081234444x888']
    assert con['mobilePhone'] == '8081234567x9999'
    assert not con['fixed']
    assert not con['errors']

def test_validate_and_fix_azure_contact_with_errors():
    """
    Should fix invalid valuds in AD Contact
    """
    con = {'userPrincipalName': 'abcdef@test..com',
           'businessPhones': ['+1(808)1234567', '567-9999', '1234444 x 888'],
           'mobilePhone': '+1 (808) 123 - 4567 x 9999'}
    validate_and_fix_azure_contact(con)
    assert con['userPrincipalName'] == 'abcdef@test..com'
    assert con['businessPhones'] == ['8081234567', '8085679999', '8081234444x888']
    assert con['mobilePhone'] == '8081234567x9999'
    assert con['fixed']
    assert con['errors']
