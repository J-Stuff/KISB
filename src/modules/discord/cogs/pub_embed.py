from discord.ext import commands, tasks
from discord import app_commands
from modules.discord._kisb import KISB
from core.configs import Config
from modules.slAPI.data import read_cache
from fractions import Fraction
import json
import logging
import os
import discord
import datetime

logger = logging.getLogger("bot")



class Functions:
    # database schema
    # {"channel":12346789, "message":123456789}


    path = f"{Config.Paths.get_data_path()}/discord/database.json"
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

    
    @app_commands.command(name="update-public-embed")
    @app_commands.dm_only()
    @app_commands.describe(channel_id="The new channel ID you want to set")
    async def update_embed_channel(self, i:discord.Interaction, channel_id:str):
        if i.user.id not in Config.DiscordUsers.authorized_users:
            await i.response.send_message("You don't have permission to do this!", ephemeral=True, delete_after=30)
            return
        
        try:
            channel = int(channel_id)
        except:
            await i.response.send_message("I could not parse the string you gave me into an int!", ephemeral=True)
            return
        
        await i.response.defer(ephemeral=True, thinking=True)
        
        
        try:
            new_channel = await self.bot.fetch_channel(channel)
        except discord.errors.NotFound:
            await i.followup.send(f"I could not find a channel with that ID ({channel})")
            return
        except discord.errors.Forbidden:
            await i.followup.send(f"I do not have access to that channel ({channel})")
            return
        except:
            await i.followup.send("Something went wrong!", ephemeral=True)
            return
        
        if type(new_channel) != discord.TextChannel:
            await i.followup.send("You provided me a channel which is not of type `discord.TextChanel`", ephemeral=True)
            return
        
        placeholder = await new_channel.send("<:Online:1196591854624444458>")


        payload = {"channel": new_channel.id, "message": placeholder.id}

        Functions.write_discord_database(payload=payload)

        await i.followup.send("Done! The placeholder should update within 30 seconds.", ephemeral=True)
        
        




    @tasks.loop(seconds=15, reconnect=True)
    async def updateEmbed(self):
        db = Functions.read_discord_database()
        if db == {}:
            logger.info("KISB has not had its public embed initialized yet!")
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
        await message.edit(content="", embed=embed)


async def setup(bot:KISB):
    await bot.add_cog(PublicEmbed(bot))