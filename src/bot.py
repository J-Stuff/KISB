import discord, json, time, datetime, os, logging, asyncio, typing
from discord.ext import commands, tasks
from discord import app_commands
from _kisb import KISB
from fractions import Fraction
from modules.dataManager._manager import DataManager as DM
from modules.dataManager._loop import start as updater

class mainCog(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        logging.debug("Main cog has init-ed")
        self.bot = bot
        updater(bot)
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
        





    def generate_embeds(self, updateNotice:bool = False) -> list[discord.Embed]:
        SL_TRANSLATIONS = {"60048": "Official 1", "68070": "Official 2"} # These need to be the {"SERVER ID": "DISPLAY NAME"}

        def filter_sl_server(ID:int) -> bool:
            logging.debug(f"Filtering server: {ID}")
            if str(ID) in SL_TRANSLATIONS.keys():
                logging.debug(f"Server {ID} is in the list!")
                return True
            else:
                logging.debug(f"Server {ID} is not in the list!")
                return False
            


        logging.info("Generating embeds...")
        logging.debug(f"Showing Live update Notice: {updateNotice}")
        cache = DM.read_cache()
        logging.debug(f"Cache read! - {cache}")
        embeds = []
        

        # SL Embed Processing
        logging.debug("Processing SL Embed...")
        slServers = cache['sl']['Servers']
        logging.debug(f"SL Server Data: {slServers}")
        
        slEmbed = discord.Embed(title="SCP:SL Server Stats", description="Connect: `via the server list`", color=discord.Color.blurple(), timestamp=datetime.datetime.fromtimestamp(cache['updated']))
        slEmbed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
        slEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1136583178191114270/1136583568475291648/vn5K5O6d_400x400.jpg")
        if updateNotice:
            slEmbed.set_footer(text="Updates every Minute - Last Updated")
        else:
            slEmbed.set_footer(text="Last updated")
        logging.debug("SL Main Embed Created! Starting work on dynamic data...")

        for server in slServers:
            logging.debug(f"Processing Server: {server['ID']}")
            if not filter_sl_server(server['ID']):
                logging.debug(f"Skipping server: {server['ID']}")
                continue
            logging.debug(f"Continuing with server: {server['ID']}")
            serverID = str(server['ID'])
            name = SL_TRANSLATIONS[serverID]

            try:
                if not server['Online']:
                    slEmbed.add_field(name=name, value="<:NoConnection:1136504297853550744> - `Offline`", inline=False)
                    continue
            except KeyError:
                logging.warn(f"KeyError while processing server: {server['ID']} - {server}")
                continue

            playercount = Fraction(server['Players']).as_integer_ratio()
            
            if playercount[0] >= playercount[1] and server['Online']:
                slEmbed.add_field(name=name, value=f"<:ServerFull:1137640034439286826> - `{server['Players']} Players Online`", inline=False)
            
            elif playercount[0] < playercount[1] and server['Online']:
                slEmbed.add_field(name=name, value=f"<:HighConnection:1136504263204421732> - `{server['Players']} Players Online`", inline=False)

        embeds.append(slEmbed)

        logging.info("All Done! Number of embeds: " + str(len(embeds)))
        return embeds
        

    # Get the bots gateway ping to discord servers
    async def ping(self) -> float:
        logging.debug("Getting gateway ping...")
        return round(self.bot.latency * 1000)
    


    @tasks.loop(seconds=60)
    async def updateEmbed(self):
        logging.info("Updating embed...")
        while DM.lock_check():
            logging.info("LOCKED! Waiting 1 second...")
            await asyncio.sleep(1)
        if not DM.checkIfCacheExists():
            logging.info("Cache doesn't exist! The bot likely hasn't finished booting yet...")
            return
        embeds = self.generate_embeds(True)
        try:
            data = self.database.read()
        except:
            logging.warn("Database read failed! The bot probably hasn't been initialized yet.")
            return
        CHANNEL = await self.bot.fetch_channel(data['channel'])
        MESSAGE = await CHANNEL.fetch_message(data['message']) #type:ignore
        await MESSAGE.edit(embeds=embeds)



    # ==== ADMIN SLASH COMMANDS ====

    @app_commands.command(name="export-logs")
    async def exportLogs(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `export-logs` slash command")
        if not await self.bot.is_owner(i.user):
            logging.info(f"{i.user} [{i.user.id}] failed `export-logs` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=False)
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
        if not await self.bot.is_owner(i.user):
            logging.info(f"{i.user} [{i.user.id}] failed `debug` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(ephemeral=False, thinking=True)
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
        if not DM.checkIfCacheExists():
            logging.warn("Cache doesn't exist! Skipping...")
            await i.response.send_message(f"Oops, Looks like you've caught me while I'm not quite ready yet... Try again in a few seconds. Or, if this continues. Something has gone desperately wrong and you should inform my developer `{self.bot.buildInfo.AUTHOR}`\nQuote this error message: `ERR-MANUALSTATUS-NOCACHE`", ephemeral=False)
            return
        await i.response.defer(thinking=True, ephemeral=True)
        embeds = self.generate_embeds(False)
        logging.debug(f"Embeds generated for manual status command: {embeds}")
        await i.followup.send(embeds=embeds, ephemeral=True)


    @app_commands.command(name="about", description="Get information about the bot")
    async def about(self, i:discord.Interaction):
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
        logging.info(f"{ctx.author} [{ctx.author.id}] ran `init-here` command")
        response = await ctx.send("Initializing...", delete_after=10)
        try:
            OLD_DATA = self.database.read()
            old_EMBED_CHANNEL = await self.bot.fetch_channel(OLD_DATA["channel"])
            old_EMBED_MESSAGE = await old_EMBED_CHANNEL.fetch_message(OLD_DATA["message"]) #type:ignore
            await old_EMBED_MESSAGE.delete()
        except Exception as e:
            await ctx.send("Error while deleting old embed! Forcing to continue...", delete_after=5)

        open('./data/database/database.json', 'w').close()
        open('./cache/cache', 'w').close()
        placeholder = discord.Embed(title="Placeholder...")
        message = await ctx.send(embed=placeholder)
        payload = {
            "message": message.id,
            "channel": message.channel.id,
        }
        self.database.write(payload)
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