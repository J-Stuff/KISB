import os, json, time, logging
from .scpsl import SL
from _kisb import KISB


class DataManager():
    LOCK = "./cahce/locks/API_DATA.lock"
    cache_location = './cache/CACHE'
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
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
        logging.debug("Checking if cache exists...")
        if os.path.exists(DataManager.cache_location):
            logging.debug("Cache exists - TRUE")
            return True
        else:
            logging.debug("Cache does not exist - FALSE")
            return False

    
    @classmethod
    def read_cache(cls) -> dict:
        cache = json.load(open(cls.cache_location, 'r'))
        logging.debug("Cache Read")
        logging.debug(cache)
        return cache
    
    async def _write_cache(self, data:dict) -> None:
        cache = open(self.cache_location, 'w')
        json.dump(data, cache)
        cache.close()
        return

    async def update_cache(self) -> None:
        if self.scpslid is None or self.scpslkey is None:
            exit("SCPSL_ID or SCPSL_KEY is not defined in system environment variables!")

        logging.debug("Attempting to update cache...")
        
        scpsl = await SL.fetch(self.bot, self.scpslid, self.scpslkey)
        logging.debug("New Data Fetched!")
        await self._write_cache({"sl": scpsl, "updated": time.time()})
        logging.debug("Cache Updated!")

        logging.debug("Checking if cache has been written...")
        if not self.checkIfCacheExists():
            logging.exception("Cache has not been written!")
            raise Exception()
        else:
            logging.debug("Cache has been written!")

    
    # STOP! This should only be used to lock reads from the database while it is updating
    @classmethod
    def lock(cls, toggle:bool):
        """STOP! This should only be used to lock reads from the database while it is updating"""
        if toggle:
            if not os.path.exists(cls.LOCK):
                open(cls.LOCK, 'w').close()
        else:
            if os.path.exists(cls.LOCK):
                os.remove(cls.LOCK)

    @classmethod
    def lock_check(cls) -> bool:
        """STOP! This should only be used to lock reads from the database while it is updating"""
        if os.path.exists(cls.LOCK):
            return True
        else:
            return False

    

        
