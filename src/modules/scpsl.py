import requests, json, logging, os

class Exceptions():
    class BadRequest(Exception):
        pass
    class BadCredentials(Exception):
        pass
    class IPNotVerified(Exception):
        pass
    class RateLimited(Exception):
        pass
    class MiscError(Exception):
        pass

class SCPSL():
    def __init__(self):
        self.id = os.getenv("SCPSL_ID")
        self.key = os.getenv("SCPSL_KEY")
        if not self.id:
            logging.critical("SCPSL_ID is not set!")
            exit(1)
        if not self.key:
            logging.critical("SCPSL_KEY is not set!")
            exit(1)
        self.url = f"https://api.scpslgame.com/serverinfo.php?id={self.id}&key={self.key}&players=true&online=true"
    
    async def fetch(self) -> dict:
        """Fetch the SCP:SL server info.

        Raises:
            Exceptions.BadRequest: Bad Request!
            Exceptions.BadCredentials: Bad Credentials!
            Exceptions.IPNotVerified: Non Verified IP!
            Exceptions.RateLimited: Ratelimted!
            Exceptions.MiscError: Misc Error occurred.

        Returns:
            dict: The JSON response. (See https://api.scpslgame.com/#/default/Get%20Server%20Info)
        """
        logging.debug("Fetching SCP:SL Server Info")
        x = requests.get(self.url)
        if x.status_code == 400:
            raise Exceptions.BadRequest("Bad request!")
        elif x.status_code == 401:
            raise Exceptions.BadCredentials("Bad credentials!")
        elif x.status_code == 404:
            raise Exceptions.IPNotVerified("IP not verified!")
        elif x.status_code == 503:
            raise Exceptions.RateLimited("Rate limited!")
        elif x.status_code != 200:
            raise Exceptions.MiscError(f"Misc error! Status code: {x.status_code}")
        logging.debug("Fetched SCP:SL Server Info")
        logging.debug(x.text)
        return json.loads(x.text)
