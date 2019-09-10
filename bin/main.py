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
    token = api.azure.get_token(CONFIG["clientId"], CONFIG["clientSecret"], CONFIG["adTenant"])
    for group in CONFIG["adGroupId"]:
        ad_group_data = []
        data = api.azure.get_group_members(group, token, None)
        ad_group_data = ad_group_data + data["value"]
        if data.get("@odata.nextLink") is not None:
            while data.get("@odata.nextLink") is not None:
                skip_token = data["@odata.nextLink"].split('?')
                data = api.azure.get_group_members(group, token, skip_token[1])
                ad_group_data = ad_group_data + data["value"]
        group_name = api.azure.get_group_name(group, token)
        if data is not None:
            result = api.everbridge_logic.sync_everbridge_group(CONFIG["everbridgeUsername"],
                                                        CONFIG["everbridgePassword"],
                                                        CONFIG["everbridgeOrg"],
                                                        ad_group_data,
                                                        group_name)
            if result != "Group has been deleted":
                print("Good " + str(len(result['data'])) + ":" + str(len(ad_group_data)))
            else:
                print("Bad Group was going to get deleted")
            
if __name__ == '__main__':
    main()
