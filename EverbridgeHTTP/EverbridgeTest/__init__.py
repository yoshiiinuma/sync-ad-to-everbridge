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
    add = req.params.get('add')
    remove = req.params.get('remove')
    if not add:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            add = req_body.get('add')
    if not remove:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            remove = req_body.get('remove')
    if add:
        CONFIG["adGroupId"].append(add)
        with open('config/config.json', 'w') as outfile:
            json.dump(CONFIG, outfile)
        return func.HttpResponse(f"{add} has been added to group list")
    if remove:
        CONFIG["adGroupId"].append(add)
        if remove in test:
            CONFIG["adGroupId"].remove(remove)
            with open('config/config.json', 'w') as outfile:
                json.dump(CONFIG, outfile)
                return func.HttpResponse(f"{remove} has been removed from group list")
        else:
            return func.HttpResponse(f"{remove} was not found in group list")
    else:
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
