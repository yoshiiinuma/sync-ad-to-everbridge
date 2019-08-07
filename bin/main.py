"""
Gets AD Group and Syncs with Everbridge Group
"""
import json
import argparse
import logging
import os
import sys
import inspect
from datetime import datetime
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)
import api.azure_api
import api.everbridge_api
logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
def get_argparser():
    """
    Build Argument Parser
    """
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    return parser
def main():
    """
    Main Function
    """
    args = get_argparser().parse_args()
    config = json.load(open(args.filename))
    if config["logFileName"]:
        log_filename = os.getcwd() + '/logs/' + config["logFileName"]
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=log_filename,
                            level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    data = api.azure_api.get_azuregroups(config["adTenant"],
                                         config["clientId"],
                                         config["clientSecret"],
                                         "https://graph.microsoft.com/v1.0/groups/" + config["adGroupId"] + "/members",
                                         )
    if data is not None:
        api.everbridge_api.sync_everbridgegroups(config["everbridgeUsername"],
                                                config["everbridgePassword"],
                                                config["everbridgeOrg"],
                                                data,
                                                config["everbridgeGroup"])
if __name__ == '__main__':
    main()
