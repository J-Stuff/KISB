import discord, json, time, datetime, os, logging, asyncio
from discord.ext import commands, tasks
from discord import app_commands
from _kisb import KISB
from fractions import Fraction
from modules.dataManager._manager import DataManager as DM
from modules.logging import Logging as Log

class mainCog(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        logging.debug("Main cog has init-ed")
        self.bot = bot
        self.update_cache.start()
        time.sleep(5)
        self.updateEmbed.start()
        super().__init__()

    class database():
        database_location = './data/database/database.json'
        
        @classmethod
        def read(cls) -> dict:
            logging.debug("DATABASE READ CALLED")
            with open(cls.database_location, 'r') as db:
                return json.load(db)
        

        @classmethod
        def write(cls, data:dict) -> None:
            logging.debug(f"DATABASE WRITE CALLED! - {data}")
            with open(cls.database_location, 'w') as db:
                json.dump(data, db)
        




    async def safe_restart(self):
        logging.info("Restarting...")
        self.updateEmbed.stop()
        self.update_cache.stop()
        logging.debug("All Services Stopped - Waiting 5 seconds and cleaning up any locks...")
        DM.lock(False)
        await asyncio.sleep(5)

        logging.debug("Cleanup & wait complete! Starting services back up!")
        self.update_cache.start()
        await asyncio.sleep(5)
        self.updateEmbed.start()
        logging.info("Restart complete!")




    def generate_embeds(self, updateNotice:bool = False) -> list[discord.Embed]:
        cache = DM.read_cache()
        embeds = []
        serverNames = {"60048": "Official 1", "68070": "Official 2"} # These need to be the {"SERVER ID": "DISPLAY NAME"}

        # SL Embed Processing
        slEmbed = discord.Embed(color=discord.Color.blurple(), title="KI Status: SCP:SL Servers", description="Connect: `via the playerlist ingame`", timestamp=datetime.datetime.fromtimestamp(cache['updated']))
        slEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        slEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583568475291648/vn5K5O6d_400x400.jpg")
        if updateNotice:
            slEmbed.set_footer(text="Updates every Minute - Last Updated")
        else:
            slEmbed.set_footer(text="Last updated")
        
        slServers = cache['sl']['Servers']
        for server in slServers:
            serverID = str(server['ID'])
            try:
                name = serverNames[serverID]
            except:
                continue
            playercount = Fraction(server['Players']).as_integer_ratio()
            if playercount[0] >= playercount[1] and server['Online']:
                slEmbed.add_field(name=name, value=f"<:ServerFull:1137640034439286826> - `{server['Players']} Players Online`", inline=False)
            
            elif playercount[0] < playercount[1] and server['Online']:
                slEmbed.add_field(name=name, value=f"<:HighConnection:1136504263204421732> - `{server['Players']} Players Online`", inline=False)
            
            elif not server['Online']:
                slEmbed.add_field(name=name, value="<:NoConnection:1136504297853550744> - `Offline`", inline=False)
        embeds.append(slEmbed)

        return embeds
        

    # Get the bots gateway ping to discord servers
    async def ping(self) -> float:
        await Log.info(self.bot, "Getting ping...")
        return round(self.bot.latency * 1000)
    


    @tasks.loop(seconds=30)
    async def update_cache(self):
        DM.lock(True)
        if await DM.checkIfCacheExpired(self.bot):
            await DM(self.bot).update_cache()
        else:
            logging.warn("Attempted to update Cache while it was still fresh!")
            await Log.warn(self.bot, "Attempted to update Cache while it was still fresh!")
        DM.lock(False)

    @tasks.loop(seconds=60)
    async def updateEmbed(self):
        await Log.info(self.bot, "Updating embed...")
        while DM.lock_check():
            logging.info("LOCKED! Waiting 1 second...")
            await asyncio.sleep(1)
        if not os.path.exists('./cache/cache'):
            logging.info("Cache doesn't exist! Skipping...")
            return
        embeds = self.generate_embeds(True)
        data = self.database.read()
        CHANNEL = await self.bot.fetch_channel(data['channel'])
        MESSAGE = await CHANNEL.fetch_message(data['message']) #type:ignore
        await MESSAGE.edit(embeds=embeds)



    # ==== ADMIN SLASH COMMANDS ====

    @app_commands.command(name="reload")
    async def restart(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `reload` slash command")
        if not self.bot.is_owner(i.user):
            logging.info(f"{i.user} [{i.user.id}] failed `reload` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        await i.response.defer(thinking=True, ephemeral=False)
        await Log.info(self.bot, "Reloading cogs...", i.user)
        await self.safe_restart()
        await i.followup.send(content="Done!")


    @app_commands.command(name="export-logs")
    async def exportLogs(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `export-logs` slash command")
        if not self.bot.is_owner(i.user):
            logging.info(f"{i.user} [{i.user.id}] failed `export-logs` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=False)
        await Log.info(self.bot, "Ran export-logs command", i.user)
        logging.info("Exporting logs...", i.user)
        try:
            await i.user.send(files=[discord.File('./data/logs/kisb.log'), discord.File('./data/logs/kisb.log.old')])
        except discord.Forbidden:
            await i.followup.send(content="I can't DM you!")
            logging.warn("I can't DM you!")
            return
        except discord.errors.HTTPException:
            await i.followup.send(content="Logs are too big to send! - HTTPException")
            logging.warn("Logs too big to send!")
            return
        logging.info("Logs Exported!")
        await i.followup.send(content="Done!")

    
    @app_commands.command(name='debug')
    async def debug(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `debug` slash command")
        if not self.bot.is_owner(i.user):
            logging.info(f"{i.user} [{i.user.id}] failed `debug` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(ephemeral=False, thinking=True)
        await Log.info(self.bot, "Ran debug command", i.user)
        try:
            await i.followup.send(files=[discord.File('./cache/cache'), discord.File('./data/database/database.json')], ephemeral=False)
            logging.debug("Sent debug files")
        except discord.Forbidden:
            await i.followup.send(content="I lack permission to send files here!", ephemeral=False)
            logging.warn(f"I don't have permission to send files in [{i.channel_id}]")
            return
        

    # ==== USER SLASH COMMANDS ====

    @app_commands.command(name="status", description="Get the status of the servers")
    async def status(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `status` slash command")
        if not os.path.exists('./cache/cache'):
            logging.warn("Cache doesn't exist! Skipping...")
            await i.response.send_message(f"Oops, Looks like you've caught me while I'm not quite ready yet... Try again in a few seconds. Or, if this continues. Something has gone desperately wrong and you should inform my developer `{self.bot.buildInfo.AUTHOR}`\nQuote this error message: `ERR-MANUALSTATUS-NOCACHE`", ephemeral=False)
            return
        await i.response.defer(thinking=True, ephemeral=True)
        await Log.info(self.bot, "Ran status command", i.user)
        embeds = self.generate_embeds(False)
        logging.debug(f"Embeds generated for manual status command: {embeds}")
        await i.followup.send(embeds=embeds, ephemeral=True)


    @app_commands.command(name="about", description="Get information about the bot")
    async def about(self, i:discord.Interaction):
        await Log.info(self.bot, "Ran about command", i.user)
        logging.info(f"{i.user} [{i.user.id}] ran `status` slash command")
        await i.response.defer(thinking=True, ephemeral=True)
        embed = discord.Embed(title="About KISB", description=f"Hi, I'm KISB (Kitchen Island Status Bot) I'm a monitoring bot used to display player counts for the KI game servers.\nI'm fully coded from the ground up by my author `{self.bot.buildInfo.AUTHOR}` with some help from a few open source libraries.\nSee my source code at: {self.bot.buildInfo.REPOSITORY}", color=discord.Color.from_str("#4A6F28"))
        embed.set_author(name="KISB")
        embed.add_field(name="Version", value=self.bot.buildInfo.VERSION, inline=False)
        embed.add_field(name="Build Date", value=self.bot.buildInfo.DATE, inline=False)
        embed.add_field(name="Uptime", value=str(datetime.datetime.now() - self.bot.uptime).split(".")[0], inline=False)
        embed.add_field(name="Gateway Ping", value=f"`{await self.ping()}ms`", inline=False)
        await i.followup.send(embed=embed, ephemeral=True)



    # ==== ADMIN TEXT COMMANDS ====

    @commands.command(name="init-here")
    @commands.is_owner()
    async def initHere(self, ctx:commands.Context):
        await Log.warn(self.bot, "Initializing!", ctx.author)
        # await ctx.message.delete()
        response = await ctx.send("Initializing...")
        try:
            OLD_DATA = self.database.read()

            old_EMBED_CHANNEL = await self.bot.fetch_channel(OLD_DATA["channel"])
            old_EMBED_MESSAGE = await old_EMBED_CHANNEL.fetch_message(OLD_DATA["message"]) #type:ignore
            await old_EMBED_MESSAGE.delete()
        except Exception as e:
            await Log.warn(self.bot, f"Error while deleting old embed: {e}")
            await ctx.send("Error while deleting old embed! Forcing to continue...", delete_after=5)


        open('./data/database/database.json', 'w').close()
        await Log.warn(self.bot, "Database reset!")
        open('./cache/cache', 'w').close()
        await Log.warn(self.bot, "Cache reset!")
        placeholder = discord.Embed(title="Placeholder...")
        message = await ctx.send(embed=placeholder)
        await Log.warn(self.bot, "Embed created!")
        payload = {
            "message": message.id,
            "channel": message.channel.id,
        }
        await Log.warn(self.bot, "Writing to database...")
        await Log.debug(self.bot, str(payload))
        self.database.write(payload)
        await Log.info(self.bot, "Reloading cogs...")
        await self.safe_restart()
        await response.edit(content="Done!\n(This message self destructs in 10 seconds)", delete_after=10)


    @commands.command(name='sync')
    @commands.is_owner()
    async def sync(self, ctx:commands.Context):
        await ctx.reply("Syncing...")
        logging.debug(str(await self.bot.tree.sync()))
        await ctx.reply("Synced!")
        
    
async def setup(bot:KISB):
    await bot.add_cog(mainCog(bot))
    logging.info("Cog loaded: Main Cog")