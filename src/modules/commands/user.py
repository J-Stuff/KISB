import discord, logging, datetime, typing, fractions
from discord.ext import commands
from discord import app_commands
from modules.dataManager._manager import DataManager as DM
from bot import CustomFunctions
from _kisb import KISB



class UserCommands(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        super().__init__()


     # ==== USER SLASH COMMANDS ====

    @app_commands.command(name="status", description="Get the status of the servers")
    async def status(self, i:discord.Interaction):
        logging.info(f"{i.user} [{i.user.id}] ran `status` slash command")
        if not DM.checkIfCacheExists():
            logging.warn("Cache doesn't exist! Skipping...")
            await i.response.send_message(f"Oops, Looks like you've caught me while I'm not quite ready yet... Try again in a few seconds. Or, if this continues. Something has gone desperately wrong and you should inform my developer `{self.bot.buildInfo.AUTHOR}`\nQuote this error message: `ERR-MANUALSTATUS-NOCACHE`", ephemeral=False)
            return
        await i.response.defer(thinking=True, ephemeral=True)
        embeds = CustomFunctions.generate_embeds(False)
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
        embed.add_field(name="Gateway Ping", value=f"`{await CustomFunctions.ping(self.bot)}ms`", inline=False)
        await i.followup.send(embed=embed, ephemeral=True)


        
        


async def setup(bot:KISB):
    await bot.add_cog(UserCommands(bot))
    logging.info("User commands loaded!")