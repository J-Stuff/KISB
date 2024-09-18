# Functions to be used by the wider application for reading the slAPI cache

import json
import logging
import os
from filelock import FileLock, Timeout
from core.configs import Config

logger = logging.getLogger("slapi")

class Exceptions():

    class cacheDirNotSet(Exception):
        pass

    class cacheFileNotPresent(Exception):
        pass


def _cacheCheck() -> tuple[str, str]:
    cacheDir = Config.Paths.get_cache_path()
    if not cacheDir:
        raise Exceptions.cacheDirNotSet
    cacheFile =  cacheDir + "/slapi_cache.json"
    if not os.path.exists(cacheFile):
        raise Exceptions.cacheFileNotPresent
    return cacheDir, cacheFile

def read_cache():
    
    try:
        cacheDir, cacheFile = _cacheCheck()
    except:
        return {}
    
    lock = FileLock(f"{cacheDir}/slapi_cache.json.lock", timeout=2, blocking=False)

    try:
        while lock:
            with open(cacheFile, 'r') as fp:
                return json.load(fp)
    except Timeout:
        logger.exception("The cache failed to read because it was locked for more than 2 seconds!")
        raise Exception
    