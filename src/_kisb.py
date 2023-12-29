import discord, logging, datetime
from discord.ext import commands
from enum import StrEnum

cogs = [
    'bot',
    'modules.commands.user',
    'modules.commands.admin',
]

class Build(StrEnum):
    VERSION = "1.2.6"
    DATE = "3.12.2023"
    AUTHOR = "J Stuff"
    REPOSITORY = "https://github.com/J-Stuff/KISB"


class CONFIGS():
    servers = {
        "60048": "Official 1",
        "68070": "Official 2",
        "70516": "Community Server 3"
    }
    owner = 946234576538304603 # J Stuff
    admin_roles = []
    admin_users = [336678934639017985] # [aHarmlessSpoon]


class KISB(commands.Bot):
    configs = CONFIGS
    cogList = cogs
    buildInfo = Build
    def __init__(self):
        self.uptime = datetime.datetime.now()
        super().__init__(";", help_command=None, intents=discord.Intents.default())
    
    async def on_ready(self):
        logging.info("KISB is ready!")
        logging.info(f"Logged in as {self.user}")
        logging.info("Loading cogs...")
        for cog in self.cogList:
            logging.info(f"Loading cog: {cog}")
            await self.load_extension(f"{cog}")