import discord, logging, json, asyncio, time, datetime, os
from enum import IntEnum
from discord.ext import commands, tasks
from discord import app_commands
from _kisb import KISB
from fractions import Fraction

from modules.minecraft import Server, Exceptions as mcExceptions
from modules.pz import PZ, Exceptions as pzExceptions
from modules.rust import Rust, Exceptions as rustExceptions
from modules.scpsl import SCPSL
from modules.logging import Logging as Log

class mainCog(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        self.updateEmbed.start()
        super().__init__()

    async def updateCache(self):
        if not self.checkIfCacheExpired():
            return
        logging.info("Updating cache...")
        logging.debug("Clearing cache...")
        open('./cache/cache', 'w').close()
        logging.debug("Cache Cleared.")

        logging.debug("Fetching Minecraft Server...")
        mcServer = await Server().fetchServer()
        logging.debug("Fetched Minecraft Server.")
        logging.debug("Fetching Minecraft Player Count...")
        asyncio.run
        try:
            mcPlayerCount = await asyncio.wait_for(Server().fetch(mcServer), timeout=5)
        except:
            logging.debug("Failed to connect to the server.")
            mcPlayerCount = "OFFLINE"
        logging.debug("Fetched Minecraft Player Count.")
        logging.debug(mcPlayerCount)

        logging.debug("Fetching PZ Server Info...")
        try:
            pzServer = await PZ().fetch()
        except:
            pzServer = ["OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE"]
        logging.debug("Fetched PZ Server Info.")
        logging.debug(pzServer)

        logging.debug("Fetching Rust Server Info...")
        try:
            rustServer = await Rust().fetch()
        except:
            rustServer = ["OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE", "OFFLINE"]
        logging.debug("Fetched Rust Server Info.")
        logging.debug(rustServer)



        scpslServer = await SCPSL().fetch()
        logging.debug(scpslServer)
        await asyncio.sleep(2)

        slPayload = []
        class ServerBoundPorts(IntEnum):
            OFFICIAL = 7777
        
        slServerList = scpslServer['Servers']
        for server in slServerList:
            if server["Port"] == ServerBoundPorts.OFFICIAL:
                serverSize = Fraction(server['Players']).as_integer_ratio()
                if server["Online"]:
                    if serverSize[0] >= serverSize[1]:
                        slPayload.append(f"<:ServerFull:1137640034439286826> **-** Official - Online! (Full) - {server['Players']} online")
                    else:
                        slPayload.append(f"<:HighConnection:1136504263204421732> **-** Official - Online! - {server['Players']} online")
                else:
                    slPayload.append("<:LowConnection:1136504263204421731> **-** Official - Offline")

        payload = {
            "minecraft": {
                "playercount": mcPlayerCount,
            },
            "pz": {
                "online": pzServer[0],
                "game": pzServer[1],
                "name": pzServer[2],
                "players": pzServer[3],
                "max_players": pzServer[4],
                "map": pzServer[5],
                "vac_secure": pzServer[6],
                "server_type": pzServer[7],
                "os": pzServer[8],
                "password_required": pzServer[9]
            },
            "rust": {
                "online": rustServer[0],
                "game": rustServer[1],
                "name": rustServer[2],
                "players": rustServer[3],
                "max_players": rustServer[4],
                "map": rustServer[5],
                "vac_secure": rustServer[6],
                "server_type": rustServer[7],
                "os": rustServer[8],
                "password_required": rustServer[9]
            },
            "scpsl": slPayload
        }
        logging.debug("New Cache:")
        logging.debug(payload)

        with open('./cache/cache', 'w') as f:
            json.dump(payload, f)

        dataStore = json.load(open('./data/database/database.json', 'r'))
        dataStore["minecraftLU"] = int(time.time())
        dataStore["zomboidLU"] = int(time.time())
        dataStore["rustLU"] = int(time.time())
        dataStore["scpslLU"] = int(time.time())
        logging.debug("Updating database...")
        logging.debug(dataStore)
        json.dump(dataStore, open('./data/database/database.json', 'w'))

    def checkIfCacheExpired(self):
        logging.info("Checking if cache is expired...")
        cacheExpiry = 20 # Cache Expiry value in seconds (I would really discourage changing this to a value lower than 15)
        dataStore = json.load(open('./data/database/database.json', 'r'))
        if int(time.time()) - dataStore["minecraftLU"] > cacheExpiry:
            logging.debug("Cache expired!")
            return True
        if int(time.time()) - dataStore["zomboidLU"] > cacheExpiry:
            logging.debug("Cache expired!")
            return True
        if int(time.time()) - dataStore["rustLU"] > cacheExpiry:
            logging.debug("Cache expired!")
            return True
        if int(time.time()) - dataStore["scpslLU"] > cacheExpiry:
            logging.debug("Cache expired!")
            return True
        logging.debug("Cache not expired!")
        return False

    def readCache(self) -> dict:
        logging.info("Reading cache...")
        with open('./cache/cache', 'r') as f:
            return json.load(f)

    # Get the bots gateway ping to discord servers
    async def ping(self) -> float:
        logging.info("Getting ping...")
        return round(self.bot.latency * 1000)
        





    @commands.command(name="init-here")
    @commands.is_owner()
    async def initHere(self, ctx:commands.Context):
        logging.warning("Initializing!")
        # await ctx.message.delete()
        response = await ctx.send("Initializing...")
        try:
            with open('./data/database/database.json', 'r') as f:
                dataStore = json.load(f)
            old_EMBED_MESSAGE_ID = dataStore["embedMessage"]
            old_EMBED_CHANNEL_ID = dataStore["embedChannel"]

            old_EMBED_CHANNEL = await self.bot.fetch_channel(old_EMBED_CHANNEL_ID)
            old_EMBED_MESSAGE = await old_EMBED_CHANNEL.fetch_message(old_EMBED_MESSAGE_ID) #type:ignore
            await old_EMBED_MESSAGE.delete()
        except Exception as e:
            logging.error(f"Error while deleting old embed: {e}")
            await ctx.send("Error while deleting old embed! Forcing to continue...")
            await ctx.send(f"```{e}```")


        open('./data/database/database.json', 'w').close()
        logging.warning("Database reset!")
        open('./cache/cache', 'w').close()
        logging.warning("Cache reset!")
        placeholder = discord.Embed(title="Placeholder...")
        message = await ctx.send(embed=placeholder)
        logging.warning("Embed created!")
        payload = {
            "embedMessage": message.id,
            "embedChannel": message.channel.id,
            "minecraftLU": 0,
            "zomboidLU": 0,
            "rustLU": 0,
            "scpslLU": 0
        }
        logging.warning("Writing to database...")
        logging.debug(payload)
        with open('./data/database/database.json', 'w') as f:
            json.dump(payload, f)
            f.close()
        logging.info("Reloading cogs...")
        for cog in self.bot.cogList:
            await self.bot.reload_extension(f"{cog}")
        await response.edit(content="Done!\n(This message self destructs in 10 seconds)", delete_after=10)


    @commands.command(name="reload")
    @commands.is_owner()
    async def restart(self, ctx:commands.Context):
        logging.info("Reloading cogs...")
        response = await ctx.reply("Restarting...")
        for cog in self.bot.cogList:
            await self.bot.reload_extension(f"{cog}")
        logging.info("Cogs reloaded!")
        await response.edit(content="Done!")


    @commands.command(name="export-logs")
    @commands.is_owner()
    async def exportLogs(self, ctx:commands.Context):
        logging.info("Exporting logs...")
        response = await ctx.reply("Exporting logs...")
        try:
            await ctx.author.send(files=[discord.File('./data/logs/kisb.log'), discord.File('./data/logs/kisb.log.old')])
        except discord.Forbidden:
            await response.edit(content="I can't DM you!")
            logging.warning("I can't DM you!")
            return
        logging.info("Logs exported!")
        await response.edit(content="Done!")

    @tasks.loop(minutes=10)
    async def healthCheck(self):
        deathTimeout = 120 # Number of seconds before the bot is considered dead - MAKE SURE THIS IS HIGHER THAN THE EMBED LOOP INTERVAL
        logging.info("Running health check...")
        if not os.path.exists('./cache/cache'):
            logging.warning("Cache doesn't exist! Bot is likely awaiting initialization. Skipping...")
            return
        dataStore = json.load(open('./data/database/database.json', 'r'))
        if int(time.time()) - dataStore["minecraftLU"] > deathTimeout:
            await Log.warn(self.bot, "Bot found dead!")
            for cog in self.bot.cogList:
                await self.bot.reload_extension(f"{cog}")
        else:
            logging.info("Bot is alive!")


    @tasks.loop(minutes=1)
    async def updateEmbed(self):
        logging.info("Updating embed...")
        if not os.path.exists('./cache/cache'):
            logging.warning("Cache doesn't exist! Skipping...")
            return
        await self.updateCache()
        cachedData = self.readCache()

        minecraftEmbed = discord.Embed(title="KI - Minecraft Server Status", description="Connect - `mc.kitchenisland.org`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#4A6F28"))
        minecraftEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        minecraftEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583254028333136/GrassNew.webp")
        if cachedData['minecraft']['playercount'] != "OFFLINE":
            minecraftEmbed.add_field(name="Server Status:", value=f"<:HighConnection:1136504263204421732> **-** Players: {cachedData['minecraft']['playercount']}", inline=False)
        else:
            minecraftEmbed.add_field(name="Server Status:", value="<:NoConnection:1136504297853550744> **-** Offline!", inline=False)
        minecraftEmbed.set_footer(text="Updates every minute. Last updated:")
        
        rustEmbed = discord.Embed(title="KI - Rust Server Status", description="Connect - `51.161.196.138:28015`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#CE422B"))
        rustEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        rustEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583483490308197/cc406a8382d8df7eb5f395ec884d3c95.png")
        if cachedData['rust']['online'] != "OFFLINE":
            if cachedData['rust']['players'] >= cachedData['rust']['max_players']:
                rustEmbed.add_field(name="Server Status", value="<:ServerFull:1137640034439286826> **-** Online - Server full", inline=False)
            else:
                rustEmbed.add_field(name="Server Status", value="<:HighConnection:1136504263204421732> **-** Online", inline=False)
            rustEmbed.add_field(name="Player count", value=f"{cachedData['rust']['players']}/{cachedData['rust']['max_players']}", inline=False)
        else:
            rustEmbed.add_field(name="Server Status", value="<:NoConnection:1136504297853550744> **-** Offline!", inline=False)
        rustEmbed.set_footer(text="Updates every minute. Last updated:")

        zomboidEmbed = discord.Embed(title="KI - Project Zomboid Server Status", description="Connect - `51.161.196.138:8770`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#111111"))
        zomboidEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        zomboidEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583191919083573/logo.png")
        if cachedData['pz']['online'] != "OFFLINE":
            if cachedData['pz']['players'] >= cachedData['pz']['max_players']:
                zomboidEmbed.add_field(name="Server Status", value="<:ServerFull:1137640034439286826> **-** Online - Server full", inline=False)
            else:
                zomboidEmbed.add_field(name="Server Status", value="<:HighConnection:1136504263204421732> **-** Online", inline=False)
            zomboidEmbed.add_field(name="Player count", value=f"{cachedData['pz']['players']}/{cachedData['pz']['max_players']}", inline=False)
        else:
            zomboidEmbed.add_field(name="Server Status", value="<:NoConnection:1136504297853550744> Offline!", inline=False)
        zomboidEmbed.set_footer(text="Updates every minute. Last updated:")

        scpslEmbed = discord.Embed(title="KI - SCP: Secret Laboratory Server Status", description="Connect - Via the playerlist in-game", timestamp=datetime.datetime.now(), color=discord.Color.teal())
        scpslEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        scpslEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583568475291648/vn5K5O6d_400x400.jpg")
        for server in cachedData['scpsl']:
            scpslEmbed.add_field(name=">", value=server, inline=False)
        scpslEmbed.set_footer(text="Updates every minute. Last updated:")

        dataStore = json.load(open('./data/database/database.json', 'r'))
        logging.info("Fetching embed channel...")
        channel = await self.bot.fetch_channel(dataStore['embedChannel'])
        if type(channel) != discord.TextChannel:
            logging.error("Embed channel not found!")
            exit()
        logging.info("Fetching embed message...")
        message = await channel.fetch_message(dataStore['embedMessage']) 
        logging.info("Editing embed...")
        await message.edit(embeds=[minecraftEmbed, rustEmbed, zomboidEmbed, scpslEmbed])
        logging.info("Embed updated!")



    @app_commands.command(name="status", description="Get the status of the servers")
    async def status(self, i:discord.Interaction):
        if not os.path.exists('./cache/cache'):
            logging.warning("Cache doesn't exist! Skipping...")
            return
        await i.response.defer(thinking=True, ephemeral=True)
        await self.updateCache()
        cachedData = self.readCache()

        minecraftEmbed = discord.Embed(title="KI - Minecraft Server Status", description="Connect - `mc.kitchenisland.org`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#4A6F28"))
        minecraftEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        minecraftEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583254028333136/GrassNew.webp")
        if cachedData['minecraft']['playercount'] != "OFFLINE":
            minecraftEmbed.add_field(name="Server Status:", value=f"<:HighConnection:1136504263204421732> **-** Players: {cachedData['minecraft']['playercount']}", inline=False)
        else:
            minecraftEmbed.add_field(name="Server Status:", value="<:NoConnection:1136504297853550744> **-** Offline!", inline=False)
        
        rustEmbed = discord.Embed(title="KI - Rust Server Status", description="Connect - `51.161.196.138:28015`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#CE422B"))
        rustEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        rustEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583483490308197/cc406a8382d8df7eb5f395ec884d3c95.png")
        if cachedData['rust']['online'] != "OFFLINE":
            if cachedData['rust']['players'] >= cachedData['rust']['max_players']:
                rustEmbed.add_field(name="Server Status", value="<:ServerFull:1137640034439286826> **-** Online - Server full", inline=False)
            else:
                rustEmbed.add_field(name="Server Status", value="<:HighConnection:1136504263204421732> **-** Online", inline=False)
            rustEmbed.add_field(name="Player count", value=f"{cachedData['rust']['players']}/{cachedData['rust']['max_players']}", inline=False)
        else:
            rustEmbed.add_field(name="Server Status", value="<:NoConnection:1136504297853550744> **-** Offline!", inline=False)

        zomboidEmbed = discord.Embed(title="KI - Project Zomboid Server Status", description="Connect - `51.161.196.138:8770`", timestamp=datetime.datetime.now(), color=discord.Color.from_str("#111111"))
        zomboidEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        zomboidEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583191919083573/logo.png")
        if cachedData['pz']['online'] != "OFFLINE":
            if cachedData['pz']['players'] >= cachedData['pz']['max_players']:
                zomboidEmbed.add_field(name="Server Status", value="<:ServerFull:1137640034439286826> **-** Online - Server full", inline=False)
            else:
                zomboidEmbed.add_field(name="Server Status", value="<:HighConnection:1136504263204421732> **-** Online", inline=False)
            zomboidEmbed.add_field(name="Player count", value=f"{cachedData['pz']['players']}/{cachedData['pz']['max_players']}", inline=False)
        else:
            zomboidEmbed.add_field(name="Server Status", value="<:NoConnection:1136504297853550744> Offline!", inline=False)

        scpslEmbed = discord.Embed(title="KI - SCP: Secret Laboratory Server Status", description="Connect - Via the playerlist in-game", timestamp=datetime.datetime.now(), color=discord.Color.teal())
        scpslEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        scpslEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583568475291648/vn5K5O6d_400x400.jpg")
        for server in cachedData['scpsl']:
            scpslEmbed.add_field(name=">", value=server, inline=False)


        await i.followup.send(embeds=[minecraftEmbed, rustEmbed, zomboidEmbed, scpslEmbed], ephemeral=True)


    @app_commands.command(name="about", description="Get information about the bot")
    async def about(self, i:discord.Interaction):
        await i.response.defer(thinking=True, ephemeral=True)
        embed = discord.Embed(title="About KISB", description=f"Hi, I'm KISB (Kitchen Island Status Bot) I'm a monitoring bot used to display player counts for the KI game servers.\nI'm fully coded from the ground up by my author `{self.bot.buildInfo.AUTHOR}` with some help from a few open source libraries.\nSee my source code at: {self.bot.buildInfo.REPOSITORY}", color=discord.Color.from_str("#4A6F28"))
        embed.set_author(name="KISB")
        embed.add_field(name="Version", value=self.bot.buildInfo.VERSION, inline=False)
        embed.add_field(name="Build Date", value=self.bot.buildInfo.DATE, inline=False)
        embed.add_field(name="Uptime", value=str(datetime.datetime.now() - self.bot.uptime).split(".")[0], inline=False)
        embed.add_field(name="Gateway Ping", value=f"{await self.ping()}ms", inline=False)
        await i.followup.send(embed=embed, ephemeral=True)


    @commands.command(name='sync')
    @commands.is_owner()
    @commands.dm_only()
    async def sync(self, ctx:commands.Context):
        await ctx.reply("Syncing...")
        logging.info(await self.bot.tree.sync())
        await ctx.reply("Synced!")

    @commands.command(name='debug')
    @commands.is_owner()
    async def debug(self, ctx:commands.Context):
        status = await ctx.reply("Dumping...")
        try:
            await ctx.reply(file=discord.File('./cache/cache'))
            await ctx.reply(file=discord.File('./data/database/database.json'))
        except discord.Forbidden:
            await status.edit(content="I lack permissions to send files here!")
            return
        else:
            await status.edit(content="Done!")


    
async def setup(bot:KISB):
    await bot.add_cog(mainCog(bot))
    logging.info("Cog loaded: Main Cog")