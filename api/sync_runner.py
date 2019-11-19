"""
Runs Sync application
"""
import json
import logging
from os.path import exists
from . import azure as Azure
from . import exceptions
from . import everbridge as Everbridge
from . import synchronizer as Synchronizer
from . import logger
class SyncRunner:
    """
    Runs Sync application
    """
    def __init__(self, configfile):
        self.configfile = configfile
        self.conf = {}
        self.azure = None
        self.everbridge = None

    def run(self, groups_only=False):
        """
        Runs Sync application
        """
        # pylint: disable=broad-except
        logger.setup_logger()
        self.conf = SyncRunner.load_config(self.configfile)
        SyncRunner.check_config(self.conf)
        logger.setup_logger(self.conf.get('logFileName'), self.conf.get('logLevel'))
        self._setup_azure_api()
        self._setup_everbridge_api()
        sync = Synchronizer.Synchronizer(self.azure, self.everbridge)
        #sync.run(self.conf['adGroupId'])
        #Syncs whole group or group emails only based on boolean in argument
        if groups_only:
            sync.sync_only_group_emails(self.conf['adGroupId'], self.conf['adMemberId'], self.conf['parentGroup'])
        else:
            sync.run_with_map(self.conf['adGroupId'], self.conf['adMemberId'], self.conf['parentGroup'])
    @staticmethod
    def load_config(configfile):
        """
        Creates conf object from config file
        """
        if not exists(configfile):
            msg = 'SYNC_RUNNCER.LOAD_CONFIG: Config File Not Found: ' + configfile
            logging.error(msg)
            raise exceptions.SyncRunnerException(msg)
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
        elif not isinstance(conf['adGroupId'], list):
            errors.append('adGroupId Not List')
        if 'everbridgeOrg' not in conf:
            errors.append('everbridgeOrg Not Found')
        if 'everbridgeUsername' not in conf:
            errors.append('everbridgeUsername Not Found')
        if 'everbridgePassword' not in conf:
            errors.append('everbridgePassword Not Found')
        if 'logLevel' in conf:
            if conf['logLevel'] not in logger.SUPPORTED_LOGLEVELS:
                errors.append('LogLevel Not Supported: ' + conf['logLevel'])
        if errors:
            for err in errors:
                logging.error(err)
            raise exceptions.SyncRunnerException('SYNC_RUNNCER.CHECK_CONFIG: Invalid Config File')

    def _setup_azure_api(self):
        """
        Sets up Azure API
        """
        self.azure = Azure.Azure(self.conf['clientId'],
                                 self.conf['clientSecret'],
                                 self.conf['adTenant'])
        self.azure.setup() # Retrieves token; call once before any API calls

    def _setup_everbridge_api(self):
        """
        Sets up Everbridge API
        """
        self.everbridge = Everbridge.Everbridge(self.conf['everbridgeOrg'],
                                                self.conf['everbridgeUsername'],
                                                self.conf['everbridgePassword'])
