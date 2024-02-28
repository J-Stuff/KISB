import discord, logging, datetime, asyncio
from discord.ext import commands
from enum import StrEnum

logger = logging.getLogger("main")

cogs = [
    'bot',
    'modules.commands.user',
    'modules.commands.admin',
    'modules.modPlaytimeTracker.discord',
]

class Build(StrEnum):
    VERSION = "1.3.0"
    DATE = "30.12.2023"
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
    guilds = [1136504183948857397, ] # [KI Bakery]


class KISB(commands.Bot):
    configs = CONFIGS
    cogList = cogs
    buildInfo = Build
    def __init__(self):
        self.uptime = datetime.datetime.now()
        super().__init__(";", help_command=None, intents=discord.Intents.default())
    
    async def on_ready(self):
        logger.info("KISB is ready!")
        logger.info(f"Logged in as {self.user}")
        logger.info("Loading cogs...")
        for cog in self.cogList:
            logger.info(f"Loading cog: {cog}")
            await asyncio.sleep(3)
            await self.load_extension(f"{cog}")
            # A log should be made by the cog itself announcing it's loaded