import discord, logging
from discord.ext import commands

cogs = [
    'bot'
]


class KISB(commands.Bot):
    def __init__(self):
        self.cogList = cogs
        super().__init__(";", help_command=None, intents=discord.Intents.default())
    
    async def on_ready(self):
        logging.info("KISB is ready!")
        logging.info(f"Logged in as {self.user}")
        logging.info("Loading cogs...")
        for cog in self.cogList:
            logging.info(f"Loading cog: {cog}")
            await self.load_extension(f"{cog}")