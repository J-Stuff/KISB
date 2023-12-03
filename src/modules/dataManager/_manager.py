import os, json, time, logging
from .scpsl import SL
from _kisb import KISB


class DataManager():
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
            logging.warn("Cache has not been written!")
            raise Exception()
        else:
            logging.debug("Cache has been written!")

    @staticmethod
    def lock(toggle:bool):
        LOCKFILE = './cache/kisb.lock'
        if toggle:
            if not os.path.exists(LOCKFILE):
                open(LOCKFILE, 'w').close()
        else:
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)

    @staticmethod
    def lock_check() -> bool:
        LOCKFILE = './cache/kisb.lock'
        if os.path.exists(LOCKFILE):
            return True
        else:
            return False

    
    
    @classmethod
    async def checkIfCacheExpired(cls) -> bool:
        """Check if the internal cache is expired or not

        Returns:
            bool: True if cache is expired, else false if cache is fresh
        """
        logging.debug("Checking if cache is expired...")
        cacheExpiry = 20 # Cache Expiry value in seconds DO NOT SET BELOW 20 EVER
        if cls.checkIfCacheExists():
            cache = cls.read_cache()
            if time.time() - cache['updated'] > cacheExpiry:
                logging.debug("Cache is expired - TRUE")
                return True
            else:
                logging.debug("Cache is not expired - FALSE")
                return False
        else:
            logging.debug("Cache does not exist - TRUE")
            return True
        
