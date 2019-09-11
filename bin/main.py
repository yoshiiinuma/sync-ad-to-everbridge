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
import api.azure
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
    azure = api.azure.Azure(CONFIG["clientId"], CONFIG["clientSecret"], CONFIG["adTenant"])
    azure.set_token(azure.get_token())
    for group in CONFIG["adGroupId"]:
        group_name = azure.get_group_name(group)
        data = azure.get_all_group_members(group)
        if data is not None:
            result = api.everbridge_logic.sync_everbridge_group(CONFIG["everbridgeUsername"],
                                                        CONFIG["everbridgePassword"],
                                                        CONFIG["everbridgeOrg"],
                                                        data,
                                                        group_name)
            
if __name__ == '__main__':
    main()
