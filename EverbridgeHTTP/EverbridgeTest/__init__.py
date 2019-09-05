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
    for group in CONFIG["adGroupId"]:
        data = azure.get_group_members(group, token)
        group_name = azure.get_group_name(group, token)
        if data is not None:
            everbridge_logic.sync_everbridge_group(CONFIG["everbridgeUsername"],
                                                        CONFIG["everbridgePassword"],
                                                        CONFIG["everbridgeOrg"],
                                                        data,
                                                        group_name)
        return func.HttpResponse(
             "Sync has been completed",
             status_code=200
        )
