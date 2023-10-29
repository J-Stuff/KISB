import os, schedule, json, time, logging
from modules.logging import Logging as Log
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
        return json.load(open(cls.cache_location, 'r'))
    
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
            await Log.warn(self.bot, "Cache has not been written! - TERMINATING")
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
    async def checkIfCacheExpired(cls, bot:KISB) -> bool:
        """Check if the internal cache is expired or not

        Args:
            bot (KISB): Bot

        Returns:
            bool: True if cache is expired, else false if cache is fresh
        """
        logging.debug("Checking if cache is expired...")
        await Log.debug(bot, "Checking if cache is expired...")
        cacheExpiry = 20 # Cache Expiry value in seconds DO NOT SET BELOW 20 EVER
        try:
            cache = cls.read_cache()
        except:
            await Log.debug(bot, "Cache does not exist or is malformed - TRUE")
            return True
        updated = cache['updated']
        if time.time() - updated >= cacheExpiry:
            await Log.debug(bot, f"Cache is expired (>= {cacheExpiry}s) - TRUE")
            return True
        else:
            await Log.debug(bot, f"Cache is still fresh (< {cacheExpiry}s) - FALSE")
            return False
        
