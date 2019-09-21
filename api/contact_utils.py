"""
Contact Utility Functions
"""
import re
import logging

def normalize_phone(phone):
    """
    Normalizes phone number
    """
    if not phone:
        return ''
    phone = re.sub(r'-|\s|\(|\)|\+1', '', str(phone))
    if len(phone) == 7:
        phone = '808' + phone
    return phone

def is_valid_phone(phone):
    """
    Returns True if phone number is valid; False otherwise
    """
    return not not re.fullmatch(r'\d{10}', phone)

def is_valid_azure_contact(contact):
    """
    Returns True if contact is valid for upserting Everbridge; Error object otherwise
    NOTE: Should call fill_azure_contact before this function
    WARNING: Remove invalid phone number from contact
    """
    path_found = False
    errors = []
    warnings = []
    if 'givenName' not in contact and 'surname' not in contact:
        errors.append('NoNameFound')
    elif contact['surname'] == 'XXXXX':
        warnings.append('NoLastNameFound')
    if 'userPrincipalName' in contact:
        path_found = True
    if 'businessPhones' in contact and contact['businessPhones']:
        valid_phones = []
        for phone in contact['businessPhones']:
            if is_valid_phone(phone):
                valid_phones.append(phone)
            else:
                warnings.append('InvalidBusinessPhone:' + phone)
        if valid_phones:
            contact['businessPhones'] = valid_phones
            path_found = True
    if 'mobilePhone' in contact and contact['mobilePhone']:
        if is_valid_phone(contact['mobilePhone']):
            path_found = True
        else:
            warnings.append('InvalidMobilePhone:' + contact['mobilePhone'])
    if not path_found:
        errors.append('NoPathFound')
    if warnings:
        msg = 'CONTACT_UTILS.IS_VALID_AZURE_CONTACT: ' + ', '.join(warnings)
        logger.error(msg)
    if errors:
        msg = 'CONTACT_UTILS.IS_VALID_AZURE_CONTACT: ' + ', '.join(errors)
        logger.error(msg)
        return False
    return True

def fill_azure_contact(contact):
    """
    Fills missing info in AD Contact
    NOTE: phone nubmers will be normalized
    """
    if not contact:
        return
    if 'givenName' not in contact:
        first = 'XXXXX'
        last = 'XXXXX'
        names = contact['displayName'].split(' ')
        logging.warning("%s has no first/last name. Adding in placeholder", contact['displayName'])
        if len(names) > 1:
            first = names.pop(0)
            last = ''.join(str(x) for x in names)
        else:
            first = contact['displayName']
        contact['givenName'] = first
        if 'surname' not in contact or not contact['surname']:
            if last == 'XXXXX':
                msg = 'CONTACT_UTILS.FILL_AZURE_CONTACT: NoLastName '
                logging.error(msg)
            contact['surname'] = last
    if 'userPrincipalName' not in contact:
        if 'mail' in contact:
            contact['userPrincipalName'] = contact['mail']
        else:
            logging.warning("%s has no email. Adding in placeholder", contact['displayName'])
            contact['userPrincipalName'] = ('XXX_MISSINGMAIL_XXX.' + contact['givenName'] +
                                            '.' + contact['surname'] + '@hawaii.gov')
    if 'businessPhones' in contact:
        if contact['businessPhones']:
            contact['businessPhones'] = list(map(normalize_phone, contact['businessPhones']))
    else:
        contact['businessPhones'] = []
    if 'mobilePhone' in contact:
        contact['mobilePhone'] = normalize_phone(contact['mobilePhone'])

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
    return con_ad != extract_attributes_for_comparison(con_ev)

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
    fill_azure_contact(contact)
    new_contact = {
        'firstName': contact['givenName'],
        'lastName': contact['surname'],
        'externalId': contact['userPrincipalName'],
        'recordTypeId': 892807736729062,
        'paths': create_everbridge_contact_paths(contact)
    }
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
    paths = [
        # Add Email Contact Path to the new contact
        {
            'waitTime': 0,
            'status': 'A',
            'pathId': 241901148045316,
            'value': contact['userPrincipalName'],
            'skipValidation': False
        }
    ]
    if contact['businessPhones']:
        for phone in contact['businessPhones']:
            #Checks to see if phone has extension
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
            if re.fullmatch(r'\d{10}|\d{7}', phone):
                paths.append(path)
            else:
                logging.warning("%s has invalid working phone number %s",
                                contact["displayName"], phone)
    # Adds Work Cell Path to contact if mobile phone number is present
    if contact.get('mobilePhone'):
        if re.fullmatch(r'\d{10}|\d{7}', contact['mobilePhone']):
            paths.append(
                {
                    'waitTime': 0,
                    'status': 'A',
                    'pathId': 241901148045319,
                    'countryCode': 'US',
                    'value': contact['mobilePhone'],
                    'skipValidation': False
                })
            # Adds Work Cell SMS Path to contact
            paths.append(
                {
                    'waitTime': 0,
                    'status': 'A',
                    'pathId': 241901148045324,
                    'countryCode': 'US',
                    'value': contact['mobilePhone'],
                    'skipValidation': False
                })
        else:
            logging.warning("%s has invalid mobile phone number %s",
                            contact["displayName"], contact['mobilePhone'])
    return paths
