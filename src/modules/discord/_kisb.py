from discord import Intents
import logging
import datetime
from discord.ext import commands

cogs = [
    "modules.discord.cogs.pub_embed"
]

logger = logging.getLogger("bot")

class KISB(commands.Bot):
    def __init__(self):
        self.cogList = cogs
        self.uptime = datetime.datetime.now()
        super().__init__(";", help_command=None, intents=Intents.all())


    async def on_ready(self):
        logger.info("KISB is ready!")
        logger.info(f"Logged in as {self.user}")
        logger.info("Loading cogs...")
        for cog in self.cogList:
            logger.info(f"Loading cog: {cog}")
            await self.load_extension(f"{cog}")