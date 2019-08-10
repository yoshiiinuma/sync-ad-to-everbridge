"""
Gets AD Group and Syncs with Everbridge Group
"""
import json
import argparse
import logging
import os
import sys
import inspect
CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)
import api.azure_api
import api.everbridge_api
import api.everbridge_logic
def get_argparser():
    """
    Build Argument Parser
    """
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    return parser
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
ARGS = get_argparser().parse_args()
CONFIG = json.load(open(ARGS.filename))
if CONFIG["logFileName"]:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=os.getcwd() + '/logs/' + CONFIG["logFileName"],
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
def main():
    """
    Main Function
    """
    #Function will not run if number of ADGroups does not match Evergroups
    if len(CONFIG["adGroupId"]) == len(CONFIG["everbridgeGroup"]):
        for group in CONFIG["adGroupId"]:
            data = api.azure_api.get_azuregroups(CONFIG["adTenant"],
                                                    CONFIG["clientId"],
                                                    CONFIG["clientSecret"],
                                                    "https://graph.microsoft.com/v1.0/groups/"
                                                    + group
                                                    + "/members")
            if data is not None:
                api.everbridge_logic.sync_everbridgegroups(CONFIG["everbridgeUsername"],
                                                            CONFIG["everbridgePassword"],
                                                            CONFIG["everbridgeOrg"],
                                                            data,
                                                            CONFIG["everbridgeGroup"][CONFIG["adGroupId"].index(group)])
if __name__ == '__main__':
    main()
