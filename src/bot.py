import discord, json, time, datetime, logging, asyncio, typing
from discord.ext import commands, tasks
from _kisb import KISB
from fractions import Fraction
from modules.dataManager._manager import DataManager as DM
from modules.dataManager._loop import start as updater


class CustomFunctions():


    class database():
        database_location = './data/database/database.json'
        notify_database_location = './data/database/notify.json'
        
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



    @staticmethod
    def generate_embeds(updateNotice:bool = False) -> list[discord.Embed]:
        SL_TRANSLATIONS = {"60048": "Official 1", "68070": "Official 2", "70516":"Community Server 3"} # These need to be the {"SERVER ID": "DISPLAY NAME"}

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


    @staticmethod
    # Get the bots gateway ping to discord servers
    async def ping(bot:KISB) -> float:
        logging.debug("Getting gateway ping...")
        return round(bot.latency * 1000)






class mainCog(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        logging.debug("Main cog has init-ed")
        self.bot = bot
        updater(bot)
        time.sleep(5)
        self.updateEmbed.start()
        super().__init__()

        


    @tasks.loop(seconds=20) # Don't set this below 20 seconds
    async def updateEmbed(self):
        logging.info("Updating embed...")
        while DM.lock_check():
            logging.info("LOCKED! Waiting 1 second...")
            await asyncio.sleep(1)
        if not DM.checkIfCacheExists():
            logging.info("Cache doesn't exist! The bot likely hasn't finished booting yet...")
            return
        embeds = CustomFunctions.generate_embeds(True)
        try:
            data = CustomFunctions.database.read()
        except:
            logging.warn("Database read failed! The bot probably hasn't been initialized yet.")
            return
        try:
            CHANNEL = await self.bot.fetch_channel(data['channel'])
            MESSAGE = await CHANNEL.fetch_message(data['message']) #type:ignore
            await MESSAGE.edit(embeds=embeds)
        except Exception as e:
            logging.warn("Something went wrong when trying to update the embed, I'll try again when the next schedule runs.")
            logging.warn(e)
        
    
async def setup(bot:KISB):
    await bot.add_cog(mainCog(bot))
    logging.info("Cog loaded: Main Cog")