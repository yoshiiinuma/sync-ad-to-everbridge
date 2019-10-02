"""
Function that gets called from Azure Function
"""
import logging
import json
import azure.functions as func
from .api import sync_runner 
import pathlib
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Does the same function as main.py with a optional parameter to include additional groups
    """
    runner = sync_runner.SyncRunner((pathlib.Path(__file__).parent / 'config.json', 'rb'))
    runner.run()
    return func.HttpResponse(
            json.dumps("Sync has been completed"),
            status_code=200
    )