from steam import SteamQuery
import logging, json

class Exceptions():
    class FailedToConnect(Exception):
        pass

class PZ():
    def __init__(self) -> None:
        self.ip = "51.161.196.138"
        self.port = 8770
    
    async def fetch(self) -> tuple:
        """Fetch server info

        Returns:
            tuple: 
            ```
            online: bool
            game: str
            name: str
            players: int
            max_players: int
            map: str
            vac_secure: bool
            server_type: str
            os: str
            password_required: bool
            ```
        """
        logging.info("Fetching PZ server info...")
        logging.debug(f"IP: {self.ip}")
        logging.debug(f"Port: {self.port}")
        server = SteamQuery(self.ip, self.port)
        logging.debug("Querying server...")
        server_info = server.query_server_info()
        logging.debug("Querying server... Done!")
        logging.debug("Server response:")
        logging.debug(json.dumps(server_info, indent=4))
        logging.info("Fetching PZ server info... Done!")
        if server_info == {"error": "Request timed out"}:
            raise Exceptions.FailedToConnect("Failed to connect to the server.")
        return server_info['online'], server_info['game'], server_info['name'], server_info['players'], server_info['max_players'], server_info['map'], server_info['vac_secure'], server_info['server_type'], server_info['os'], server_info['password_required']
