"""
Contact Utility Functions
"""
import re
import logging

class ContactValidationResult:
    """
    Keeps track of Azure contact validation results
    """
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.first = None
        self.last = None
        self.email = None
        self.business_phones = []
        self.mobile_phone = None

    def has_valid_name(self):
        """
        Returns True if valid name exists; False otherwise
        """
        if self.first and self.last:
            return True
        return False

    def has_valid_paths(self):
        """
        Returns True if valid path exists; False otherwise
        """
        if self.email or self.business_phones or self.mobile_phone:
            return True
        return False

    def append_error(self, err):
        """
        Set an error
        """
        self.errors.append(err)

    def append_warning(self, warn):
        """
        Set an warning
        """
        self.warnings.append(warn)

    def set_name(self, first, last):
        """
        Set a valid name
        """
        self.first = first
        self.last = last

    def set_email(self, email):
        """
        Set a valid email
        """
        self.email = email

    def append_business_phone(self, phone):
        """
        Set a valid business phone
        """
        self.business_phones.append(phone)

    def set_mobile_phone(self, phone):
        """
        Set a valid mobile phone
        """
        self.mobile_phone = phone

def normalize_phone(phone):
    """
    Normalizes phone number
    """
    if not phone:
        return ''
    phone = re.sub(r'-|\s|\(|\)|\+1', '', str(phone))
    ext = ''
    if 'x' in phone:
        matched = re.match(r'(\d+)x(\d+)', phone)
        if matched:
            phone = matched.group(1)
            ext = matched.group(2)
    if len(phone) == 7:
        phone = '808' + phone
    if ext:
        phone += 'x' + ext
    return phone

def is_valid_phone(phone):
    """
    Returns True if phone number is valid; False otherwise
    A phone number must be 10 digits exclude extension
    'x' + Extension may follow the phone number
    """
    phone = normalize_phone(phone)
    # pylint: disable=unneeded-not
    return not not re.fullmatch(r'\d{10}(x\d+)?', phone)

def is_valid_email(email):
    """
    Returns True if email address is valid; False otherwise
    """
    # pylint: disable=unneeded-not
    return not not re.fullmatch(r'^[^@ ]+@[^@ \.]+(\.[^@ \.]+)+$', email)

def get_names_from_email(email):
    """
    Returns [firstName, lastName] extracted from email (userPrincipalName)
    """
    first = None
    last = None
    if '@' in email:
        name = re.sub(r'@.*$', '', email.strip())
        if '.' in name:
            # pylint: disable=unused-variable
            first, *ignore, last = re.split(r'\.', name)
    return [first, last]

def get_names_from_displayname(displayname):
    """
    Returns [firstName, lastName] extracted from displayName
    """
    first = None
    last = None
    names = re.split(r' +', displayname.strip())
    if len(names) > 1:
        first = names.pop(0)
        last = '.'.join(str(x) for x in names)
    return [first, last]

def validate_name(contact, rslt):
    """
    Validates name of given cotanct and returns error tracking object
    Errors => Cannot insert into Everbridge contact
    Warnings => Can insert into Everbridge contact but needs to be updated
    """
    first = contact.get('givenName', '')
    last = contact.get('surname', '')
    if first and last:
        rslt.set_name(first, last)
        return
    if 'userPrincipalName' in contact:
        first, last = get_names_from_email(contact['userPrincipalName'])
        if first and last:
            rslt.set_name(first, last)
            rslt.append_warning('NameExtractedFromEmail')
            return
    if 'displayName' in contact:
        first, last = get_names_from_displayname(contact['displayName'])
        if first and last:
            rslt.set_name(first, last)
            rslt.append_warning('NameExtractedFromDisplayName')
            return
    rslt.append_error('NoNameFound')

def validate_paths(contact, rslt):
    """
    Validates paths of given cotanct and returns error tracking object
    Errors => Cannot insert into Everbridge contact
    Warnings => Can insert into Everbridge contact but needs to be updated
    """
    if 'userPrincipalName' in contact:
        if is_valid_email(contact['userPrincipalName']):
            rslt.set_email(contact['userPrincipalName'])
        else:
            rslt.append_warning('InvalidUserPrincipalName:' + contact['userPrincipalName'])
    if 'businessPhones' in contact and contact['businessPhones']:
        for phone in contact['businessPhones']:
            if is_valid_phone(phone):
                rslt.append_business_phone(phone)
            else:
                rslt.append_warning('InvalidBusinessPhone:' + phone)
    if 'mobilePhone' in contact:
        if contact['mobilePhone'] and is_valid_phone(contact['mobilePhone']):
            rslt.set_mobile_phone(contact['mobilePhone'])
        else:
            rslt.append_warning('InvalidMobilePhone:' + contact['mobilePhone'])
    if not rslt.has_valid_paths():
        rslt.append_error('NoPathFound')

def validate_azure_contact(contact):
    """
    Checks if the contact is valid for upserting, and returns the result
    """
    rslt = ContactValidationResult()
    validate_name(contact, rslt)
    validate_paths(contact, rslt)
    if rslt.warnings:
        msg = 'CONTACT_UTILS.VALIDATE_AZURE_CONTACT: ' + ', '.join(rslt.warnings)
        logging.error(msg)
    if rslt.errors:
        msg = 'CONTACT_UTILS.VALIDATE_AZURE_CONTACT: ' + ', '.join(rslt.errors)
        logging.error(msg)
    if rslt.warnings or rslt.errors:
        logging.error(contact)
    return rslt

def fix_azure_contact(contact, validated):
    """
    Fixes invalid values in AD Contact
    """
    contact['fixed'] = False
    if validated.first:
        if 'givenName' not in contact or contact['givenName'] != validated.first:
            contact['fixed'] = True
            contact['givenName'] = validated.first
    if validated.last:
        if 'surname' not in contact or contact['surname'] != validated.last:
            contact['fixed'] = True
            contact['surname'] = validated.last
    if validated.email:
        if 'userPrincipalName' not in contact or contact['userPrincipalName'] != validated.email:
            contact['fixed'] = True
            contact['userPrincipalName'] = validated.email
    if validated.business_phones:
        fixed_phones = list(map(normalize_phone, validated.business_phones))
        if 'businessPhones' not in contact or contact['businessPhones'] != fixed_phones:
            contact['fixed'] = True
            contact['businessPhones'] = fixed_phones
    if validated.mobile_phone:
        normalized_phone = normalize_phone(validated.mobile_phone)
        if 'mobilePhone' not in contact or contact['mobilePhone'] != normalized_phone:
            contact['fixed'] = True
            contact['mobilePhone'] = normalize_phone(validated.mobile_phone)

def validate_and_fix_azure_contact(contact):
    """
    Validates valuees in AD Contact and fixes errors if possible
    """
    rslt = validate_azure_contact(contact)
    contact['errors'] = True
    if rslt.has_valid_name() and rslt.has_valid_paths():
        contact['errors'] = False
    fix_azure_contact(contact, rslt)

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
