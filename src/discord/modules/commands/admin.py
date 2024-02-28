import discord, logging, typing, asyncio
from discord.ext import commands
from discord import app_commands
from _kisb import KISB
from bot import CustomFunctions
from modules.dataManager._manager import DataManager as DM
from modules.modPlaytimeTracker._database import Database as MDB
logger = logging.getLogger("main")
class AdminCommands(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        super().__init__()
    
    # ==== ADMIN SLASH COMMANDS ====

    @app_commands.command(name="export-logs")
    async def exportLogs(self, i:discord.Interaction):
        logger.info(f"{i.user} [{i.user.id}] ran `export-logs` slash command")
        if not await self.bot.is_owner(i.user):
            logger.info(f"{i.user} [{i.user.id}] failed `export-logs` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=False)
        try:
            await i.user.send(files=[discord.File('./data/logs/kisb.log'), discord.File('./data/logs/kisb.log.old')])
        except discord.Forbidden:
            await i.followup.send(content="I can't DM you!")
            logger.warn("I can't DM you!")
            return
        except discord.errors.HTTPException:
            await i.followup.send(content="Logs are too big to send! - HTTPException")
            logger.warn("Logs too big to send!")
            return
        logger.info("Logs Exported!")
        await i.followup.send(content="Done!")

    
    @app_commands.command(name='debug')
    async def debug(self, i:discord.Interaction):
        logger.info(f"{i.user} [{i.user.id}] ran `debug` slash command")
        if not await self.bot.is_owner(i.user):
            logger.info(f"{i.user} [{i.user.id}] failed `debug` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner.id```", ephemeral=True)
            return
        
        await i.response.defer(ephemeral=False, thinking=True)
        try:
            await i.followup.send(files=[discord.File(DM.cache_location), discord.File(CustomFunctions.mod_board_database.database_location), discord.File(CustomFunctions.mod_board_database.database_location)], ephemeral=False)
            logger.debug("Sent debug files")
        except discord.Forbidden:
            await i.followup.send(content="I lack permission to send files here!", ephemeral=False)
            logger.warn(f"I don't have permission to send files in [{i.channel_id}]")
            return
        

    @app_commands.command(name="init-public-board")
    async def initHere(self, i:discord.Interaction):
        logger.info(f"{i.user} [{i.user.id}] ran `init-public-board` command")
        if not await self.bot.is_owner(i.user):
            logger.info(f"{i.user} [{i.user.id}] failed `init-public-board` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner```", ephemeral=True)
            return
        if type(i.channel) != discord.channel.TextChannel:
            logger.info(f"{i.user} [{i.user.id}] failed `init-public-board` slash command for: FAILED CHANNEL TYPE CHECK")
            await i.response.send_message("You can't run this command here!\n`FAILED CHANNEL TYPE CHECK`", ephemeral=True)
            return
        await i.response.defer(ephemeral=True, thinking=True)
        try:
            OLD_DATA = CustomFunctions.user_board_database.read()
            old_EMBED_CHANNEL = await self.bot.fetch_channel(OLD_DATA["channel"])
            old_EMBED_MESSAGE = await old_EMBED_CHANNEL.fetch_message(OLD_DATA["message"]) #type:ignore
            await old_EMBED_MESSAGE.delete()
        except Exception as e:
            logger.warn("Error while deleting old embed! Forcing to continue...")

        open(CustomFunctions.user_board_database.database_location, 'w').close()
        placeholder = discord.Embed(title="Placeholder...", description="PUBLIC BOARD")
        message = await i.channel.send(embed=placeholder)
        payload = {
            "message": message.id,
            "channel": message.channel.id,
        }
        CustomFunctions.user_board_database.write(payload)
        await i.followup.send(content="Done!")

    @app_commands.command(name="init-mod-board")
    async def initModBoard(self, i:discord.Interaction):
        logger.info(f"{i.user} [{i.user.id}] ran `init-mod-board` command")
        if not await self.bot.is_owner(i.user):
            logger.info(f"{i.user} [{i.user.id}] failed `init-mod-board` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner```", ephemeral=True)
            return
        if type(i.channel) != discord.channel.TextChannel:
            logger.info(f"{i.user} [{i.user.id}] failed `init-mod-board` slash command for: FAILED CHANNEL TYPE CHECK")
            await i.response.send_message("You can't run this command here!\n`FAILED CHANNEL TYPE CHECK`", ephemeral=True)
            return
        await i.response.defer(ephemeral=True, thinking=True)

        try:
            OLD_DATA = CustomFunctions.mod_board_database.read()
            old_EMBED_CHANNEL = await self.bot.fetch_channel(OLD_DATA["channel"])
            old_EMBED_MESSAGE = await old_EMBED_CHANNEL.fetch_message(OLD_DATA["message"]) #type:ignore
            await old_EMBED_MESSAGE.delete()
        except Exception as e:
            logger.warn("Error while deleting old embed! Forcing to continue...")

        open(CustomFunctions.mod_board_database.database_location, 'w').close()
        placeholder = discord.Embed(title="Placeholder...", description="MOD BOARD")
        message = await i.channel.send(embed=placeholder)
        payload = {
            "message": message.id,
            "channel": message.channel.id,
        }
        CustomFunctions.mod_board_database.write(payload)
        await i.followup.send(content="Done!")

    @app_commands.command(name="rollover-playtime")
    async def manualRollover(self, i:discord.Interaction, date_to_rollover:typing.Literal["d", "w", "m"]):
        logger.info(f"{i.user} [{i.user.id}] ran `rollover-playtime` command")
        if not await self.bot.is_owner(i.user):
            logger.info(f"{i.user} [{i.user.id}] failed `rollover-playtime` slash command for: FAILED PERMISSION CHECK")
            await i.response.send_message("You don't have permission to do that!\n```REQUIRES: bot.owner```", ephemeral=True)
            return
    
        await i.response.defer(ephemeral=False, thinking=True)
        
        if date_to_rollover == "d":
            MDB().reset_playtime_today()
            await i.followup.send(content="Done!")
        elif date_to_rollover == "w":
            MDB().tickover_playtime_month()
            await i.followup.send(content="Done!")
        elif date_to_rollover == "m":
            MDB().tickover_playtime_month()
            await i.followup.send(content="Done!")
        else:
            await i.followup.send(content="Invalid timeframe to rollover!")
            return
        

            


    # ==== ADMIN TEXT COMMANDS ====


    @commands.command(name='sync')
    @commands.is_owner()
    async def sync(self, ctx:commands.Context):
        await ctx.reply("Syncing...")
        logger.debug(str(await self.bot.tree.sync()))
        await ctx.reply("Synced!")



async def setup(bot:KISB):
    await bot.add_cog(AdminCommands(bot))
    logger.info("User commands loaded!")