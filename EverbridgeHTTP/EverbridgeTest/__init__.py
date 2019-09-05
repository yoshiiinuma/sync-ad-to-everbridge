import logging
import json
import azure.functions as func
from . import azure as azure
from . import everbridge_api as everbridge_api
from . import everbridge_logic as everbridge_logic
import pathlib
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    CONFIG = json.load(open(pathlib.Path(__file__).parent / 'config.json', 'rb'))
    token = azure.get_token(CONFIG["clientId"], CONFIG["clientSecret"], CONFIG["adTenant"])
    resultString = {}
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
        logging.info("Manual Update called")
        group_split = other_groups.split(',')
        CONFIG["adGroupId"] = group_split
        resultString["Input"] = group_split
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
    return func.HttpResponse(
            json.dumps(resultString),
            status_code=200
    )
