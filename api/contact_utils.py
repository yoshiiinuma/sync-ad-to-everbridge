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

def fill_azure_contact(contact):
    """
    Fills missing info in AD Contact
    """
    if not contact:
        return
    if 'givenName' not in contact:
        first = 'XXXXX'
        last = 'None'
        names = contact['displayName'].split(' ')
        logging.warning("%s has no first/last name. Adding in placeholder", contact['displayName'])
        if len(names) > 1:
            first = names.pop(0)
            last = ''.join(str(x) for x in names)
        else:
            first = contact['displayName']
        contact['givenName'] = first
        contact['surname'] = last
    if 'userPrincipalName' in contact:
        contact['mail'] = contact['userPrincipalName']
    else:
        if 'mail' not in contact:
            logging.warning("%s has no email. Adding in placeholder", contact['displayName'])
            contact['userPrincipalName'] = ('XXX_MISSINGMAIL_XXX.' + contact['givenName'] +
                                            '.' + contact['surname'] + '@hawaii.gov')
        else:
            contact['userPrincipalName'] = contact['mail']
    if 'businessPhones' in contact:
        contact['businessPhones'] = list(map(normalize_phone, contact['businessPhones']))
    else:
        logging.warning("%s has no phone", contact['displayName'])
        contact['businessPhones'] = []
    if 'mobilePhone' in contact:
        contact['mobilePhone'] = normalize_phone(contact['mobilePhone'])

#def is_different(con_ad, con_ev):
#    """
#    Returns True if Everbridge Contact is different from AD Contact
#    """
#    # Checks Work Desk Phone
#    if con_ad['businessPhones']:
#        phone = con_ad['businessPhones'][0]
#        if not con_ev['workPhone'] == '' or phone != con_ev['workPhone']['value']:
#            return True
#    # Checks External ID
#    if con_ad['userPrincipalName'] != con_ev['mail']:
#        return True
#    # Checks Mobile Phone
#    if con_ad.get('mobilePhone'):
#        if con_ad['mobilePhone'] != con_ev['mobilePhone']['value']:
#            return True
#    return False

def convert_to_everbridge(contact, ever_id=None):
    """
    Create New EverBridge Contact with Email Delivery and Phone Delivery if available
    Contact Paths are the delivery methods for notifications in Everbridge.
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
            'skipValidation': 'false'
        }
    ]
    if contact['businessPhones']:
        for phone in contact['businessPhones']:
            #Checks to see if phone has extension
            extension = None
            if 'x' in phone:
                phone, extension, *ignore = phone.split('x')
            path = {
                'waitTime': 0,
                'status': 'A',
                'pathId': 241901148045321,
                'countryCode': 'US',
                'value': phone,
                'skipValidation': 'false'}
            if extension:
                path['phoneExt'] = extension
            #if len(phone) >= 10:
            if re.fullmatch(r'\d{10}|\d{7}', phone):
                paths.append(path)
            else:
                logging.warning("%s has invalid working phone number %s", contact["displayName"], phone)
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
                    'skipValidation': 'false'
                })
            # Adds Work Cell SMS Path to contact
            paths.append(
                {
                    'waitTime': 0,
                    'status': 'A',
                    'pathId': 241901148045324,
                    'countryCode': 'US',
                    'value': contact['mobilePhone'],
                    'skipValidation': 'false'
                })
        else:
            logging.warning("%s has invalid mobile phone number %s", contact["displayName"], contact['mobilePhone'])
    # Base info for Contact
    # Record Types are required for contact creation.
    # Record Types allow the org to categorize employees.
    # The static Record Type Id is the default 'Employee' record type.
    # There is only 1 record type in the org but more can be added.
    # To manage Record Types, go to Settings -> Contacts and Groups-> Contact Record Types.
    # https://api.everbridge.net/rest/recordTypes/org
    new_contact = {
        'firstName': contact['givenName'],
        'lastName': contact['surname'],
        'externalId': contact['userPrincipalName'],
        'recordTypeId': 892807736729062,
        'paths': paths
    }
    if ever_id:
        new_contact['id'] = ever_id
    return new_contact
