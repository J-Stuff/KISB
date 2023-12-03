import discord, logging
from discord.ext import commands
from discord import app_commands
from _kisb import KISB
from bot import CustomFunctions
from modules.dataManager._manager import DataManager as DM

class AdminCommands(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        super().__init__()
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
            await i.followup.send(files=[discord.File(DM.cache_location), discord.File(CustomFunctions.database.database_location)], ephemeral=False)
            logging.debug("Sent debug files")
        except discord.Forbidden:
            await i.followup.send(content="I lack permission to send files here!", ephemeral=False)
            logging.warn(f"I don't have permission to send files in [{i.channel_id}]")
            return
        




    # ==== ADMIN TEXT COMMANDS ====

    @commands.command(name="init-here")
    @commands.is_owner()
    async def initHere(self, ctx:commands.Context):
        logging.info(f"{ctx.author} [{ctx.author.id}] ran `init-here` command")
        response = await ctx.send("Initializing...", delete_after=10)
        try:
            OLD_DATA = CustomFunctions.database.read()
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
        CustomFunctions.database.write(payload)
        await response.edit(content="Done!\n(This message self destructs in 10 seconds)", delete_after=10)


    @commands.command(name='sync')
    @commands.is_owner()
    async def sync(self, ctx:commands.Context):
        await ctx.reply("Syncing...")
        logging.debug(str(await self.bot.tree.sync()))
        await ctx.reply("Synced!")



async def setup(bot:KISB):
    await bot.add_cog(AdminCommands(bot))
    logging.info("Cog loaded: Admin Cog")