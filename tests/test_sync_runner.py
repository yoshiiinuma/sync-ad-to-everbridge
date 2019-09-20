"""
Tests SyncRunner
"""
from unittest.mock import MagicMock, patch
import pytest
from api.exceptions import SyncRunnerException
from api.sync_runner import SyncRunner
# pylint: disable=unused-import
import tests.log_helper

@patch('api.sync_runner.Azure', autospec=True)
@patch('api.sync_runner.Everbridge', autospec=True)
@patch('api.sync_runner.Synchronizer', autospec=True)
def test_run(mock_sync, mock_ever, mock_azure):
    """
    Should call Synchronizer with proper arguments
    """
    conf = SyncRunner.load_config('./config/sampleConfig.json')
    # Create mocks
    azure = MagicMock()
    azure.setup = MagicMock()
    mock_azure.return_value = azure
    everbridge = MagicMock()
    mock_ever.return_value = everbridge
    sync = MagicMock()
    sync.run = MagicMock()
    mock_sync.return_value = sync
    # Call SyncRuunner#run
    runner = SyncRunner('./config/sampleConfig.json')
    runner.run()
    # Test if each function is called properly
    mock_azure.assert_called_with(conf['clientId'],
                                  conf['clientSecret'],
                                  conf['adTenant'])
    mock_ever.assert_called_with(conf['everbridgeOrg'],
                                 conf['everbridgeUsername'],
                                 conf['everbridgePassword'])
    mock_sync.assert_called_with(azure, everbridge)
    sync.run.assert_called_with(conf['adGroupId'])

def test_load_config():
    """
    Should return config object
    """
    conf = SyncRunner.load_config('./config/sampleConfig.json')
    exp = {
        'clientId':'Azure AD Client ID',
        'clientSecret':'Azure AD Client Secret',
        'everbridgeUsername':'EverBridge User Name',
        'everbridgePassword':'EverBridge Password',
        'everbridgeOrg':'EverBridge Org',
        'adTenant':'Azure AD Tenant',
        'adGroupId':['Azure AD Group ID1', 'Azure AD Group ID2'],
        'logFileName':'test.log',
        'logLevel':'DEBUG'
    }
    assert conf == exp

def test_load_config_with_nonexistent_file():
    """
    Should return config object
    """
    with pytest.raises(SyncRunnerException):
        SyncRunner.load_config('NOTEXIST.json')

def test_check_config():
    """
    Should not raise Exception
    """
    conf = {
        'clientId':'cid',
        'clientSecret':'secret',
        'everbridgeUsername':'user',
        'everbridgePassword':'pass',
        'everbridgeOrg':'12345',
        'adTenant':'98765',
        'adGroupId':['group1', 'group2'],
        'logFileName':'test.log',
        'logLevel':'DEBUG'
    }
    try:
        SyncRunner.check_config(conf)
    # pylint: disable=broad-except
    except Exception:
        pytest.fail('SyncRunner.check_config raised an Exception')

def test_check_config_with_errors():
    """
    Should raise Exception when required param is missing
    """
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adGroupId':['group1', 'group2']
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765'
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':'group1'
        })
    with pytest.raises(SyncRunnerException):
        SyncRunner.check_config({
            'clientId':'cid',
            'clientSecret':'secret',
            'everbridgeUsername':'user',
            'everbridgePassword':'pass',
            'everbridgeOrg':'12345',
            'adTenant':'98765',
            'adGroupId':['group1', 'group2'],
            'logLevel':'XXXXX'
        })
