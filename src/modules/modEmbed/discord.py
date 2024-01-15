import discord, json, logging
from discord.ext import commands, tasks
from _kisb import KISB
from modules.dataManager._manager import DataManager

logger = logging.getLogger("main")

class ModBoard(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        super().__init__()


    async def check_if_board_exists(self) -> bool:
        try:
            data = json.loads("/data/modBoard/meta.json")
            channel = await self.bot.fetch_channel(int(data["channel"]))
            message = channel.fetch_message(int(data["message"])) #type:ignore
        except:
            return False
        else:
            return True
        

    async def get_server_data(self):
        DM = DataManager()
        data = DM.read_cache()
        

    @tasks.loop(minutes=1)
    async def modboard(self):
        if not await self.check_if_board_exists():
            logger.warn("ModBoard does not exist, skipping")
            return