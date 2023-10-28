import discord, logging, datetime, asyncio
from discord.ext import commands
from enum import StrEnum
from modules.dataManager._manager import DataManager as DM

cogs = [
    'bot'
]

class Build(StrEnum):
    VERSION = "1.1.3"
    DATE = "29.10.2023"
    AUTHOR = "J Stuff"
    REPOSITORY = "https://github.com/J-Stuff/KISB"

IP = ""


class KISB(commands.Bot):
    def __init__(self):
        self.cogList = cogs
        self.buildInfo = Build
        self.uptime = datetime.datetime.now()
        self.ip = IP
        super().__init__(";", help_command=None, intents=discord.Intents.default())
    
    async def on_ready(self):
        logging.info("KISB is ready!")
        logging.info(f"Logged in as {self.user}")
        logging.info("Loading cogs...")
        for cog in self.cogList:
            logging.info(f"Loading cog: {cog}")
            await self.load_extension(f"{cog}")

async def restart(bot:KISB):
    await bot.unload_extension("bot")
    logging.debug("All Services Stopped - Waiting 5 seconds and cleaning up any locks...")
    DM.lock(False)
    await asyncio.sleep(5)
    logging.debug("Starting Services...")
    await bot.load_extension("bot")
