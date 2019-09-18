"""
Tests api/logger.py

-- logger log level --
    50 CRITICAL
    40 ERROR
    30 WARNING
    20 INFO
    10 DEBUG
    0  NOTEST
----------------------
"""
import sys
from os.path import dirname, abspath
from api.logger import setup_logger
from tests.mock_helper import  LoggingMock

def test_setup_logger_with_empty_filename():
    """
    Should pass STDOUT to logging.basicConfig
    """
    # Set up mock function
    mock = LoggingMock()
    mock.setup()
    # Call setup_logger
    setup_logger(None)
    # Check if correct args are passed
    mock.access('logging.basicConfig').assert_called_with(
        stream=sys.stdout,
        level=20,
        format='%(asctime)s %(levelname)s %(message)s')
    # Reinstate mocked functions
    mock.restore()

def test_setup_logger_with_filename():
    """
    Should pass the path to the log file to logging.basicConfig
    """
    filename = 'xxxx.log'
    logpath = dirname(dirname(abspath(__file__))) +'/logs/' + filename
    # Set up mock function
    mock = LoggingMock()
    mock.setup()
    # Call setup_logger
    setup_logger(filename)
    # Check if correct args are passed
    mock.access('logging.basicConfig').assert_called_with(
        filename=logpath,
        level=20,
        format='%(asctime)s %(levelname)s %(message)s')
    # Reinstate mocked functions
    mock.restore()

def test_setup_logger_with_string_level():
    """
    Should pass numeric log level to logging.basicConfig
    """
    level = 'warning'
    filename = 'xxxx.log'
    logpath = dirname(dirname(abspath(__file__))) +'/logs/' + filename
    # Set up mock function
    mock = LoggingMock()
    mock.setup()
    # Call setup_logger
    setup_logger(filename, level)
    # Check if correct args are passed
    mock.access('logging.basicConfig').assert_called_with(
        filename=logpath,
        level=30,
        format='%(asctime)s %(levelname)s %(message)s')
    # Reinstate mocked functions
    mock.restore()

def test_setup_logger_with_numeric_level():
    """
    Should pass numeric log level to logging.basicConfig
    """
    level = 40
    filename = 'xxxx.log'
    logpath = dirname(dirname(abspath(__file__))) +'/logs/' + filename
    # Set up mock function
    mock = LoggingMock()
    mock.setup()
    # Call setup_logger
    setup_logger(filename, level)
    # Check if correct args are passed
    mock.access('logging.basicConfig').assert_called_with(
        filename=logpath,
        level=40,
        format='%(asctime)s %(levelname)s %(message)s')
    # Reinstate mocked functions
    mock.restore()

def test_setup_logger_with_empty_level():
    """
    Should pass default numeric log level to logging.basicConfig
    """
    level = None
    filename = 'xxxx.log'
    logpath = dirname(dirname(abspath(__file__))) +'/logs/' + filename
    # Set up mock function
    mock = LoggingMock()
    mock.setup()
    # Call setup_logger
    setup_logger(filename, level)
    # Check if correct args are passed
    mock.access('logging.basicConfig').assert_called_with(
        filename=logpath,
        level=20,
        format='%(asctime)s %(levelname)s %(message)s')
    # Reinstate mocked functions
    mock.restore()
