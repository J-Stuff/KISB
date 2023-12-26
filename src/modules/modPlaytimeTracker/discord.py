from discord.ext import commands
from _kisb import KISB
from discord import app_commands
from ._database import Database
import discord



class Checks():
    # Checked used in slash commands

    @staticmethod
    def is_mod():
        def check(i:discord.Interaction):
            return i.user.id in Database().get_all_moderator_discord_ids()
        return app_commands.check(check)
    

    # Called Checks
    @staticmethod
    def is_bot_admin(u:discord.Member):
        """ STOP! Only pass discord.Member to this and include a check for DMs before this check!"""
        return u.id == KISB.configs.owner or u.guild_permissions.administrator


class PlaytimeTracker(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="add-mod", description="Add a user to the database")
    async def add_user(self, i:discord.Interaction, steamID:str, user:discord.User|discord.Member):
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=True)
        
        if Database().get_all_moderator_game_ids().__contains__(steamID):
            await i.followup.send("This user is already in the database. If you need to update a user use the `update-mod` slash command.", ephemeral=True)
            return
        
        Database().add_mod(steamID, str(user.id))
