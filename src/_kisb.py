import discord, logging, datetime
from discord.ext import commands
from enum import StrEnum

cogs = [
    'bot'
]

class Build(StrEnum):
    VERSION = "1.0.2"
    DATE = "12.08.2023"
    AUTHOR = "J Stuff"
    REPOSITORY = "https://github.com/J-Stuff/KISB"

class KISB(commands.Bot):
    def __init__(self):
        self.cogList = cogs
        self.buildInfo = Build
        self.uptime = datetime.datetime.now()
        super().__init__(";", help_command=None, intents=discord.Intents.default())
    
    async def on_ready(self):
        logging.info("KISB is ready!")
        logging.info(f"Logged in as {self.user}")
        logging.info("Loading cogs...")
        for cog in self.cogList:
            logging.info(f"Loading cog: {cog}")
            await self.load_extension(f"{cog}")