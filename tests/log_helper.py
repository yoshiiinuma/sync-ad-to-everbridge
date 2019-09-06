"""
Import this in test files so that test logs will output to test.log
*** DO NOT IMPORT IN tests/test_logger.py ***
"""
from api.logger import setup_logger

setup_logger('test.log', 'DEBUG')
