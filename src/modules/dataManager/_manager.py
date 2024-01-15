import os, json, time, logging
from .scpsl import SL
from _kisb import KISB

logger = logging.getLogger("main")

class DataManager():
    LOCK = "./cahce/locks/API_DATA.lock"
    cache_location = './cache/CACHE'
    def __init__(self) -> None:
        self.scpslid = os.getenv("SCPSL_ID")
        self.scpslkey = os.getenv("SCPSL_KEY")
        if self.scpslid is None or self.scpslkey is None:
            exit("SCPSL_ID or SCPSL_KEY is not defined in system environment variables!")

    @staticmethod
    def checkIfCacheExists() -> bool:
        """Check if the internal cache exists or not

        Returns:
            bool: True if cache exists, else false if cache does not exist
        """
        logger.debug("Checking if cache exists...")
        if os.path.exists(DataManager.cache_location):
            logger.debug("Cache exists - TRUE")
            return True
        else:
            logger.debug("Cache does not exist - FALSE")
            return False

    
    @classmethod
    def read_cache(cls) -> dict:
        while cls.lock_check():
            logger.debug("Cache is locked, waiting...")
            time.sleep(1)
        cache = json.load(open(cls.cache_location, 'r'))
        logger.debug("Cache Read")
        logger.debug(cache)
        return cache
    
    def _write_cache(self, data:dict) -> None:
        cache = open(self.cache_location, 'w')
        json.dump(data, cache)
        cache.close()
        return

    def update_cache(self) -> None:
        self.lock(False)
        if self.scpslid is None or self.scpslkey is None:
            exit("SCPSL_ID or SCPSL_KEY is not defined in system environment variables!")

        logger.debug("Attempting to update cache...")
        self.lock(True)
        
        scpsl = SL.fetch(self.scpslid, self.scpslkey)
        logger.debug("New Data Fetched!")
        self._write_cache({"sl": scpsl, "updated": time.time()})
        logger.debug("Cache Updated!")

        logger.debug("Checking if cache has been written...")
        if not self.checkIfCacheExists():
            logger.exception("Cache has not been written!")
            raise Exception()
        else:
            logger.debug("Cache has been written!")
        self.lock(False)

    
    # STOP! This should only be used to lock reads from the database while it is updating
    @classmethod
    def lock(cls, toggle:bool):
        """STOP! This should only be used to lock reads from the database while it is updating"""
        logger.info(f"Locking Cache: {toggle}")
        if toggle:
            if not os.path.exists(cls.LOCK):
                open(cls.LOCK, 'w').close()
        else:
            if os.path.exists(cls.LOCK):
                os.remove(cls.LOCK)

    @classmethod
    def lock_check(cls) -> bool:
        """STOP! This should only be used to lock reads from the database while it is updating"""
        logger.debug("Checking if cache is locked...")
        if os.path.exists(cls.LOCK):
            logger.debug("Cache is locked - TRUE")
            return True
        else:
            logger.debug("Cache is not locked - FALSE")
            return False

    

        
