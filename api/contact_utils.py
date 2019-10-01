"""
Contact Utility Functions
"""
from api.contact_validator import validate_and_fix_azure_contact

def extract_attributes_for_comparison(contact):
    """
    Returns Everbridge Contact which has the minimum set of attributes needed for comparison
    """
    keys = ('id', 'externalId', 'firstName', 'lastName', 'paths', 'recordTypeId')
    return {key: contact.get(key, '') for key in keys}

def is_different(con_ad, con_ev):
    """
    Returns True if Everbridge Contact is different from AD Contact
    """
    extracted_ad = extract_attributes_for_comparison(con_ad)
    extracted_ev = extract_attributes_for_comparison(con_ev)
    return extracted_ad != extracted_ev

def convert_to_everbridge(contact, ever_id=None):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    """
    # Base info for Contact
    # Record Types are required for contact creation.
    # Record Types allow the org to categorize employees.
    # The static Record Type Id is the default 'Employee' record type.
    # There is only 1 record type in the org but more can be added.
    # To manage Record Types, go to Settings -> Contacts and Groups-> Contact Record Types.
    # https://api.everbridge.net/rest/recordTypes/org
    validate_and_fix_azure_contact(contact)
    new_contact = {
        'firstName': contact['givenName'],
        'lastName': contact['surname'],
        'externalId': contact['userPrincipalName'],
        'recordTypeId': 892807736729062,
        'paths': create_everbridge_contact_paths(contact)
    }
    new_contact['errors'] = contact.get('errors', False)
    if ever_id:
        new_contact['id'] = ever_id
    return new_contact

def create_everbridge_contact_paths(contact):
    """
    Create EverBridge Contact Paths, which are the delivery methods for notifications
    Contact Paths can not be created or deleted through the API.
    To view paths in the org, go to Settings -> Notifications -> Delivery Methods
    https://api.everbridge.net/rest/contactPaths/org
    """
    paths = []
    if 'userPrincipalName' in contact:
        paths.append(create_email_path(contact['userPrincipalName']))
    if 'businessPhones' in contact:
        for phone in contact['businessPhones']:
            paths.append(create_business_phone_path(phone))
    if 'mobilePhone' in contact:
        paths.append(create_mobile_phone_path(contact['mobilePhone']))
        paths.append(create_sms_path(contact['mobilePhone']))
    return paths

def create_email_path(email):
    """
    Creates EverBridge Email path
    """
    return {
        'waitTime': 0,
        'status': 'A',
        'pathId': 241901148045316,
        'value': email,
        'skipValidation': False
    }

def create_business_phone_path(phone):
    """
    Creates EverBridge business phone path
    """
    extension = None
    # pylint: disable=unused-variable
    if 'x' in phone:
        phone, extension, *ignore = phone.split('x')
    path = {
        'waitTime': 0,
        'status': 'A',
        'pathId': 241901148045321,
        'countryCode': 'US',
        'value': phone,
        'skipValidation': False}
    if extension:
        path['phoneExt'] = extension
    return path

def create_mobile_phone_path(mobile_phone):
    """
    Creates EverBridge business phone path
    """
    return {
        'waitTime': 0,
        'status': 'A',
        'pathId': 241901148045319,
        'countryCode': 'US',
        'value': mobile_phone,
        'skipValidation': False
    }

def create_sms_path(mobile_phone):
    """
    Creates EverBridge SMS path
    """
    return {
        'waitTime': 0,
        'status': 'A',
        'pathId': 241901148045324,
        'countryCode': 'US',
        'value': mobile_phone,
        'skipValidation': False
    }
