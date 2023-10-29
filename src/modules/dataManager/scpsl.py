import requests, json, logging, os, typing
from _kisb import KISB

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
    async def fetch(cls, bot:KISB, id:str, key:str) -> dict|typing.Literal["OFFLINE"]:
        """Fetch the SCP:SL server info.

        Raises:
            Any raised exception will terminate the bot.

        Returns:
            dict: Raw SL response
        """
        logging.debug("Fetching SCP:SL Server Info")
        url = f"https://api.scpslgame.com/serverinfo.php?id={id}&key={key}&players=true&online=true"
        x = requests.get(url)
        if x.status_code == 400:
            logging.warn("[SCP:SL] - Bad request!")
            raise cls.Exceptions.BadRequest("Bad request!")
        elif x.status_code == 401:
            logging.warn("[SCP:SL] - Bad credentials!")
            raise cls.Exceptions.BadCredentials("Bad credentials!")
        elif x.status_code == 404:
            logging.warn("[SCP:SL] - IP not verified!")
            raise cls.Exceptions.IPNotVerified("IP not verified!")
        elif x.status_code == 503:
            logging.warn("[SCP:SL] - Rate limited!")
            raise cls.Exceptions.RateLimited("Rate limited!")
        elif x.status_code != 200:
            logging.warn(f"[SCP:SL] - Misc error! Status code: {x.status_code}")
            raise cls.Exceptions.MiscError(f"Misc error! Status code: {x.status_code}")
        logging.debug(f"[SCP:SL] - Server data fetched successfully! \n {x.text}")
        servers:dict = json.loads(x.text)
        if servers["Success"] != True:
            logging.warn(bot, f"[SCP:SL] - Server data fetch was not successful! - `http {x.status_code}`")
            raise cls.Exceptions.MiscError(f"Misc error! Status code: {x.status_code}")
        
        return servers