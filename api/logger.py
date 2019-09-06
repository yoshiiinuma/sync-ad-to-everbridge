"""
Changes log destination

-- logger log level --
    50 CRITICAL
    40 ERROR
    30 WARNING
    20 INFO
    10 DEBUG
    0  NOTEST
----------------------
"""
from os.path import dirname, abspath, join
import sys
import logging

def setup_logger(filename=None, level=None):
    """
    Sets up logger
    """
    if not level:
        level = logging.INFO
    if isinstance(level, str):
        level = getattr(logging, level.upper(), None)
    if filename:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        path = join(dirname(dirname(abspath(__file__))), 'logs', filename)
        logging.basicConfig(filename=path,
                            level=level,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(stream=sys.stdout,
                            level=level,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
