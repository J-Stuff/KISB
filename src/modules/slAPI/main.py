# This module should be entirely self contained. And nothing except the run functions should be exported. Anything else should be exported and written in the data.py file.

import os
import logging
import requests
import json
import time
from filelock import FileLock
from typing import Never
from core.configs import Config as CoreConfig

logger = logging.getLogger("slapi")

class Exceptions:


    class APIError(Exception):
        pass

    class APIRateLimited(Exception):
        pass

    class APIBadCredentials(Exception):
        pass

    class APINoCredentials(Exception):
        pass


class Config:
    base = "https://api.scpslgame.com/serverinfo.php"
    id_param = "id="
    key_param = "key="
    params = ["players=true", "list=true", "nicknames=true", "online=true"]


    


def _get_credentials() -> tuple:
    ID = os.getenv('SCPSL_ID', None)
    KEY = os.getenv('SCPSL_KEY', None)

    if ID is None or KEY is None:
        raise Exceptions.APINoCredentials('No API credentials found')
    logger.debug(f"API ID: {ID}")
    logger.debug(f"API KEY: {KEY}")
    return ID, KEY


def _create_exception(response: requests.Response) -> Never:
    if response.json().get("error", None) == "ID must be Numeric":
        raise Exceptions.APIBadCredentials("API ID must be numeric")
    if response.json().get("error", None) == "Access denied":
        raise Exceptions.APIBadCredentials("API key is invalid")
    
    elif response.status_code == 429:
        raise Exceptions.APIRateLimited("API rate limited")
    
    else:
        raise Exceptions.APIError(f"API returned an unknown error: {response.json()}")
    


def _make_request() -> dict: # type:ignore
    ID, KEY = _get_credentials()
    URL = f"{Config.base}?{Config.id_param}{int(ID)}&{Config.key_param}{str(KEY)}"
    for param in Config.params:
        URL += f"&{param}"
    logger.debug(f"Requesting URL: {URL}")
    response = requests.get(URL)
    if response.status_code != 200:
        _create_exception(response)
    elif response.json().get("Success", None) != True:
        _create_exception(response)
    elif response.json().get("Success", None):
        return response.json()
    
def _store_cache(data: dict):
    cacheDir = CoreConfig.Paths().get_cache_path()
    lock = FileLock(f"{cacheDir}/slapi_cache.json.lock")
    with lock:
        data["Updated"] = time.time()
        logger.debug(f"Storing cache in {cacheDir}/slapi_cache.json")
        with open(f"{cacheDir}/slapi_cache.json", "w") as f:
            json.dump(data, f)


def update_cache():
    data = _make_request()
    _store_cache(data)
    logger.info("Cache updated successfully")


def blind_update_cache():
    success = False
    retries = 0
    while not success and retries < 6:
        try:
            update_cache()
            success = True
        except Exception as e:
            retries += 1
            logger.error(f"Failed to update cache - ({retries} / 6): {e}")
            time.sleep(5)