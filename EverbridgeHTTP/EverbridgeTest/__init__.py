"""
Function that gets called from Azure Function
"""
import logging
import json
import azure.functions as func
from . import azure as azure
from . import everbridge_api as everbridge_api
from . import everbridge_logic as everbridge_logic
import pathlib
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Does the same function as main.py with a optional parameter to include additional groups
    """
    logging.info('Python HTTP trigger function processed a request.')
    #Get Token
    CONFIG = json.load(open(pathlib.Path(__file__).parent / 'config.json', 'rb'))
    token = azure.get_token(CONFIG["clientId"], CONFIG["clientSecret"], CONFIG["adTenant"])
    resultString = {}
    #Checks for additional Groups
    other_groups = req.params.get('groups')
    count = 0
    if not other_groups:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            other_groups = req_body.get('groups')

    if other_groups:
        #Replaces config.json groups with parameters seperated by ,
        logging.info("Manual Update called")
        group_split = other_groups.split(',')
        CONFIG["adGroupId"] = group_split
        resultString["Input"] = group_split
        #Group limit to limit cost
        if len(group_split > 10):
            return func.HttpResponse(
                    "Too many groups",
                    status_code=400
            )
    #Syncs AD Groups with Everbridge
    for group in CONFIG["adGroupId"]:
        data = azure.get_group_members(group, token)
        group_name = azure.get_group_name(group, token)
        if data is not None:
            resultString[group] = everbridge_logic.sync_everbridge_group(CONFIG["everbridgeUsername"],
                                                        CONFIG["everbridgePassword"],
                                                        CONFIG["everbridgeOrg"],
                                                        data,
                                                        group_name)
        else:
            logging.error("AD Group %s was not found", group)
            resultString[group] = "Error: No AD Group found"
            count += 1
    #Returns error codes if groups do not have AD group data
    if count == 0:
        return func.HttpResponse(
                json.dumps(resultString),
                status_code=200
        )
    elif count == len(CONFIG["adGroupId"]):
        return func.HttpResponse(
                json.dumps(resultString),
                status_code=400
        )
    else:
        return func.HttpResponse(
                json.dumps(resultString),
                status_code=409
        )