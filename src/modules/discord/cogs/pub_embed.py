from discord.ext import commands, tasks
from discord import app_commands
from modules.discord._kisb import KISB
from core.configs import Config
from modules.slAPI.data import read_cache
from fractions import Fraction
from typing import Literal
import json
import logging
import os
import discord
import datetime

logger = logging.getLogger("bot")



class Functions:
    path = f"{Config.Paths.get_data_path()}/discord/database.json"
    # database schema
    # {"channel":12346789, "message":123456789,}

    
    @classmethod
    def read_discord_database(cls):
        if not os.path.exists(cls.path):
            return {}
        with open(cls.path, 'r') as fp:
            data = json.load(fp)
        logger.debug(f"Reading from discord DB: {data}")
        return data
    
    @classmethod
    def write_discord_database(cls, payload:dict):
        logger.debug(f"Writing to discord DB: {payload}")
        with open(cls.path, 'w') as fp:
            json.dump(payload, fp)

class PublicEmbed(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.updateEmbed.start()
        super().__init__()


    @tasks.loop(seconds=15, reconnect=True)
    async def updateEmbed(self):
        try:
            db = Functions.read_discord_database()
            if db == {}:
                logger.info("KISB has not had its public embed initialized yet! I will stop the update loop until it is initialized.")
                self.updateEmbed.stop()
                return

            channel_id = db["channel"]
            message_id = db["message"]
            
            channel = self.bot.get_channel(int(channel_id))
            message = await channel.fetch_message(int(message_id)) #type:ignore <- Type checking being an arse

            embed = discord.Embed(title="SCP:SL Server Stats", color=0x5865f2)
            embed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
            embed.set_thumbnail(url=Config.Discord.asset_SCPslLogo)

            slData = read_cache()

            if type(slData) != dict:
                logger.exception("Cache was poisoned and is invalid when I attempted to read it!")
                raise Exception
            if slData == {}:
                logger.warning("The Cache is blank! Public embed will skip updating and retry in 30 seconds.")
                return

            slServers = slData["Servers"]
            serverNames = Config.Static.server_translations

            for server in slServers:
                serverID = str(server["ID"])
                if serverID not in serverNames.keys():
                    continue

                name = serverNames[serverID]

                playerRatio = Fraction(server["Players"]).as_integer_ratio()
                serverFull = playerRatio[0] >= playerRatio[1]

                if not server["Online"]:
                    embed.add_field(name=name, value=f"⚠️ {Config.Discord.emoji_NoConnection} **Offline!** - `0/0 Players Online`", inline=False)
                elif not serverFull:
                    embed.add_field(name=name, value=f"{Config.Discord.emoji_HighConnection} **Online** - `{server['Players']} Players Online`", inline=False)
                elif serverFull:
                    embed.add_field(name=name, value=f"{Config.Discord.emoji_ServerFull} **Full** - `{server['Players']} Players Online`", inline=False)
                else:
                    embed.add_field(name=name, value=f"🔘 {Config.Discord.emoji_NoConnection} **Unknown** - `0/0 Players Online`", inline=False)
            
            embed.set_footer(text=f"KISB {Config.Build.Version} | Last Updated")
            embed.timestamp = datetime.datetime.fromtimestamp(slData["Updated"])
            try:
                await message.edit(content="", embed=embed)
            except:
                logger.exception("Discord Failed to update the embed. Trying again on the next scheduled loop.")
        
        
        except Exception as e: 
            # You may be here asking yourself, why the fuck I added a catch all here. The simple answer is because Discord's API is a BITCH and will sometimes 502 for no reason.
            # And this runs every 15 seconds anyways so if an execution is missed it will be caught up by the time the next update is ran.
            logger.warning("Something went wrong while trying to update the Public Embed")
            logger.exception(e)


async def setup(bot:KISB):
    await bot.add_cog(PublicEmbed(bot))