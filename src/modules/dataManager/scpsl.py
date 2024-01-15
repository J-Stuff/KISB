import requests, json, logging, os, typing
from _kisb import KISB

logger = logging.getLogger("main")
# Module Version: 1.1.0 (22.9.2023)


class SL():
    class Exceptions():
        class BadRequest(Exception):
            def __init__(self, message:str):
                pass
        class BadCredentials(Exception):
            def __init__(self, message:str):
                pass
        class IPNotVerified(Exception):
            def __init__(self, message:str):
                pass
        class RateLimited(Exception):
            def __init__(self, message:str):
                pass
        class MiscError(Exception):
            def __init__(self, message:str):
                pass


    @classmethod
    def fetch(cls, id:str, key:str) -> dict|typing.Literal["OFFLINE"]:
        """Fetch the SCP:SL server info.

        Returns:
            dict: Raw SL response
        """
        logger.debug("Fetching SCP:SL Server Info")
        url = f"https://api.scpslgame.com/serverinfo.php?id={id}&key={key}&players=true&online=true&list=true&nicknames=true"
        x = requests.get(url)
        logger.debug(f"[SCP:SL] - Server data fetched \n {x.text}")
        servers:dict = json.loads(x.text)
        if servers["Success"] != True:
            logger.warn(f"[SCP:SL] - Server data fetch was not successful! - `http {x.status_code}`")
            raise cls.Exceptions.MiscError(f"Misc error! Status code: {x.status_code}")
        
        return servers