import discord, datetime, os, logging
from _kisb import KISB





class Logging():
    @staticmethod
    async def debug(bot:KISB, message:str, author:discord.User|discord.Member|None=None):
        embed = discord.Embed(color=discord.Color.greyple(), title="🐛 Debug", timestamp=datetime.datetime.now())
        if author is not None:
            embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.description = f"```{message}```"
        logChanneID = os.getenv("LOG_CHANNEL_ID")
        if logChanneID is not None:
            try:
                logChannel = await bot.fetch_channel(int(logChanneID))
            except discord.NotFound:
                logging.warning(f"Log channel not found! ({logChanneID})")
                return
            if type(logChannel) == discord.TextChannel:
                await logChannel.send(embed=embed)
            else:
                logging.warning(f"Log channel is not a text channel! ({logChannel})")

    @staticmethod
    async def info(bot:KISB, message:str, author:discord.User|discord.Member|None=None):
        embed = discord.Embed(color=discord.Color.blue(), title="ℹ️ Info", timestamp=datetime.datetime.now())
        if author is not None:
            embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.description = f"```{message}```"
        logChanneID = os.getenv("LOG_CHANNEL_ID")
        if logChanneID is not None:
            try:
                logChannel = await bot.fetch_channel(int(logChanneID))
            except discord.NotFound:
                logging.warning(f"Log channel not found! ({logChanneID})")
                return
            if type(logChannel) == discord.TextChannel:
                await logChannel.send(embed=embed)
            else:
                logging.warning(f"Log channel is not a text channel! ({logChannel})")

    @staticmethod
    async def warn(bot:KISB, message:str, author:discord.User|discord.Member|None=None):
        embed = discord.Embed(color=discord.Color.gold(), title="⚠️ Warn", timestamp=datetime.datetime.now())
        if author is not None:
            embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.description = f"```{message}```"
        logChanneID = os.getenv("LOG_CHANNEL_ID")
        if logChanneID is not None:
            try:
                logChannel = await bot.fetch_channel(int(logChanneID))
            except discord.NotFound:
                logging.warning(f"Log channel not found! ({logChanneID})")
                return
            if type(logChannel) == discord.TextChannel:
                await logChannel.send(embed=embed)
            else:
                logging.warning(f"Log channel is not a text channel! ({logChannel})")