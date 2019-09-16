"""
Runs Sync application
"""
import json
import logging
from os.path import exists
from api.azure import Azure
from api.everbridge import Everbridge
from api.synchronizer import Synchronizer
from api.logger import setup_logger, SUPPORTED_LOGLEVELS

class SyncRunner:
    """
    Runs Sync application
    """
    def __init__(self, configfile):
        self.configfile = configfile
        self.conf = {}
        self.azure = None
        self.everbridge = None

    def run(self):
        """
        Runs Sync application
        """
        setup_logger()
        self.conf = SyncRunner.load_config(self.configfile)
        SyncRunner.check_config(self.conf)
        setup_logger(self.conf.get('logFileName'), self.conf.get('logLevel'))
        self._setup_azure_api()
        self._setup_everbridge_api()
        sync = Synchronizer(self.azure, self.everbridge)
        sync.run(self.conf['adGroupId'])

    @staticmethod
    def load_config(configfile):
        """
        Creates conf object from config file
        """
        if not exists(configfile):
            logging.error('SYNC_RUNNCER.LOAD_CONFIG: Config File Not Found: %s', configfile)
            raise Exception('SYNC_RUNNCER.LOAD_CONFIG: Config File Not Found: ' + configfile)
        return json.load(open(configfile))

    @staticmethod
    def check_config(conf):
        """
        Raises Exception if config doesn't have expected attributes
        """
        errors = []
        if 'clientId' not in conf:
            errors.append('clientId Not Found')
        if 'clientSecret' not in conf:
            errors.append('clientSecret Not Found')
        if 'adTenant' not in conf:
            errors.append('adTenant Not Found')
        if 'adGroupId' not in conf:
            errors.append('adGroupId Not Found')
        if not isinstance(conf['adGroupId'], list):
            errors.append('adGroupId Not List')
        if 'everbridgeOrg' not in conf:
            errors.append('everbridgeOrg Not Found')
        if 'everbridgeUsername' not in conf:
            errors.append('everbridgeUsername Not Found')
        if 'everbridgePassword' not in conf:
            errors.append('everbridgePassword Not Found')
        if 'logLevel' in conf:
            if conf['logLevel'] not in SUPPORTED_LOGLEVELS:
                errors.append('LogLevel Not Supported: ' + conf['logLevel'])
        if errors:
            for err in errors:
                logging.error(err)
            raise Exception('SYNC_RUNNCER.CHECK_CONFIG: Invalid Config File')

    def _setup_azure_api(self):
        """
        Sets up Azure API
        """
        self.azure = Azure(self.conf['clientId'],
                           self.conf['clientSecret'],
                           self.conf['adTenant'])
        self.azure.setup() # Retrieves token; call once before any API calls

    def _setup_everbridge_api(self):
        """
        Sets up Everbridge API
        """
        self.everbridge = Everbridge(self.conf['everbridgeOrg'],
                                     self.conf['everbridgeUsername'],
                                     self.conf['everbridgePassword'])
