"""
Tests Everbridge API Functions
"""
import json
from unittest.mock import MagicMock
import pytest
from api.everbridge import Everbridge
from tests.mock_helper import AdalMock, RequestsMock
# pylint: disable=unused-import
import tests.log_helper

def test_contact_url():
    """
    Should return contact API URL
    """
    pass

def test_groups_url():
    """
    Should return groups API URL
    """
    pass

def test_contact_groups_url():
    """
    Should return contact groups API URL
    """
    pass

def test_get_contacts_by_external_ids():
    """
    Should send GET request to specific URL
    """
    pass

def test_get_contacts_by_external_ids_with_no_external_ids():
    """
    Should raise Exception
    """
    pass

def test_get_contacts_by_external_ids_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_upsert_contacts():
    """
    Should upsert contacts
    """
    pass

def test_upsert_contacts_with_no_contacts():
    """
    Should raise Exception
    """
    pass

def test_upsert_contacts_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_delete_contacts():
    """
    Should delete contacts
    """
    pass

def test_delete_contacts_with_no_contacts():
    """
    Should raise Exception
    """
    pass

def test_delete_contacts_with_unexpected_result():
    """
    Should raise Exception
    """
    pass

def test_get_group_by_name():
    """
    Should return group
    """
    pass

def test_get_group_by_name_without_name():
    """
    Should raise Exception
    """
    pass

def test_get_group_by_name_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_get_group_id_by_name():
    """
    Should return group ID
    """
    pass

def test_get_group_id_by_name_with_no_group_id():
    """
    Should raise Exception
    """
    pass

def test_get_group_id_by_name_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_paged_group_members():
    """
    Should return paged group members
    """
    pass

def test_paged_group_members_with_no_group_id():
    """
    Should raise Exception
    """
    pass

def test_paged_group_members_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_delete_members_from_group():
    """
    Should delete members from group
    """
    pass

def test_delete_members_from_group_with_no_group_id():
    """
    Should raise Exception
    """
    pass

def test_delete_members_from_group_with_no_members():
    """
    Should raise Exception
    """
    pass

def test_delete_members_from_group_with_unexpected_result():
    """
    Should raise Exception
    """
    pass

def test_add_members_to_group():
    """
    Should add members to group
    """
    pass

def test_add_members_to_group_with_no_group_id():
    """
    Should
    """
    pass

def test_add_members_to_group_with_no_members():
    """
    Should
    """
    pass

def test_add_members_to_group_with_unexpected_response():
    """
    Should
    """
    pass

def test_add_group():
    """
    Should add group
    """
    pass

def test_add_group_with_no_group_id():
    """
    Should raise Exception
    """
    pass

def test_add_group_with_unexpected_response():
    """
    Should raise Exception
    """
    pass

def test_delete_group():
    """
    Should delete group
    """
    pass

def test_delete_group_with_no_group_id():
    """
    Should raise Exception
    """
    pass

def test_delete_group_with_unexpected_response():
    """
    Should raise Exception
    """
    pass
