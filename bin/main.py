#Requests Client Crediential Token and then performs API call to get Login Events
import json
import argparse
import logging
import os
import sys
import inspect
from datetime import datetime
from requests.exceptions import HTTPError 
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import api.azure_api
import api.everbridge_api
def get_Argparser():
    #Build argument parser.
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('filename', help="filename to parse")
    parser.add_argument('--logfile', help="logfile for program", default=None)
    return parser

if __name__ == '__main__':
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    args = get_Argparser().parse_args()
    LOG_FILENAME = datetime.now().strftime(os.getcwd() + '/logs/logfile_%H_%M_%S_%d_%m_%Y.log')
    
    config = json.load(open(args.filename))
    if len(config["logFileName"]) > 0:
        LOG_FILENAME = os.getcwd() + '/logs/' + config["logFileName"]
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')   
    logging.info("Program Start")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    data = api.azure_api.get_AzureGroups("https://login.microsoftonline.com/",
        config["adTenant"],config["clientId"],config["clientSecret"], "https://graph.microsoft.com/","v1.0/groups/",config["adGroupName"],config["adGroupId"])
    api.everbridge_api.sync_EverbridgeGroups(config["everbridgeUsername"],config["everbridgePassword"],config["everbridgeOrg"],data,config["everbridgeGroup"])
