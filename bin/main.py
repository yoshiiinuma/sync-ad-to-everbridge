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
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    args = get_argparser().parse_args()
    log_filename = datetime.now().strftime(os.getcwd() + '/logs/logfile_%H_%M_%S_%d_%m_%Y.log')
    config = json.load(open(args.filename))
    if config["logFileName"]:
        log_filename = os.getcwd() + '/logs/' + config["logFileName"]
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info("Program Start")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    data = api.azure_api.get_azuregroups(config["adTenant"],
                                         config["clientId"],
                                         config["clientSecret"],
                                         "https://graph.microsoft.com/v1.0/groups/",
                                         config["adGroupName"])
    api.everbridge_api.sync_everbridgegroups(config["everbridgeUsername"],
                                             config["everbridgePassword"],
                                             config["everbridgeOrg"],
                                             data,
                                             config["everbridgeGroup"])
if __name__ == '__main__':
    main()
