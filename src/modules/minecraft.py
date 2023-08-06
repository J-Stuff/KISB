from mcstatus import JavaServer
import logging, asyncio
from timeout_decorator import timeout, TimeoutError

class Exceptions():
    class FailedToConnect(Exception):
        pass


class Server():
    def __init__(self):
        self.serverLocation = "mc.kitchenisland.org"
        self.serverPort = 25565
    
    async def fetchServer(self) -> JavaServer:
        """Fetch the Minecraft Server object.

        Returns:
            JavaServer: The Server object.
        """
        logging.debug("Fetching Minecraft Server Object")
        return JavaServer(self.serverLocation, self.serverPort, timeout=5)
    
    async def fetch(self, server:JavaServer) -> int:
        """Fetch the server playercount

        Args:
            server (JavaServer): The Server Object.

        Returns:
            int: The online playercount.
        """
        logging.debug("Fetching Minecraft Server Playercount")
        attempts = 0
        while True:
            logging.debug("Attempting to fetch playercount")
            result = server.status().players.online
            if type(result) == int:
                break
            attempts += 1
            await asyncio.sleep(1)
            
            if attempts >= 5:
                raise Exceptions.FailedToConnect("Failed to connect to the server.")
            
        logging.debug(result)
        return result

