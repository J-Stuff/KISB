from discord.ext import commands
from _kisb import KISB
from discord import app_commands
from ._database import Database
import discord, typing


class Functions():

    @staticmethod
    def generate_single_mod_embed(user:str) -> discord.Embed:
        """ Generate an embed for a single mod """
        hit = Database().get_mod(user)
        embed = discord.Embed(title=f"Mod Playtime", color=discord.Color.dark_purple())
        embed.description = f"Showing info for <@{hit[2]}> (`{hit[0]}`)"
       
        if hit[1] == "":
            embed.add_field(name="User:", value=f"**This user has not been seen in a server yet** (`{hit[0]}`)", inline=False)
        else:
            embed.add_field(name="User:", value=f"`{hit[1]}` (`{hit[0]}`)", inline=False)

        if hit[3] == 0:
            embed.add_field(name="Last Seen on a KI SCPSL Server:", value="**This user has not been seen in a server yet**", inline=False)
        else:
            embed.add_field(name="Last Seen on a KI SCPSL Server:", value=f"<t:{hit[3]}:R>", inline=False) 

        if hit[4] == 0:
            embed.add_field(name="Playtime on KI SCPSL Servers Today:", value="**This user has not been seen online today**", inline=False)
        else:
            embed.add_field(name="Playtime on KI SCPSL Servers Today:", value=f"**{hit[4] // 60}:{hit[4] % 60}** (`{hit[4]} minutes`)", inline=False)
        
        if hit[5] == 0:
            embed.add_field(name="Playtime on KI SCPSL Servers This Week:", value="**This user has not been seen online this week**", inline=False)
        else:
            embed.add_field(name="Playtime on KI SCPSL Servers This Week:", value=f"**{hit[5] // 60}:{hit[5] % 60}** (`{hit[5]} minutes`)", inline=False)

        if hit[6] == 0:
            embed.add_field(name="Playtime on KI SCPSL Servers Last Week:", value="**This user has not been seen online last week**", inline=False)
        else:
            embed.add_field(name="Playtime on KI SCPSL Servers Last Week:", value=f"**{hit[6] // 60}:{hit[6] % 60}** (`{hit[6]} minutes`)", inline=False)
        
        if hit[7] == 0:
            embed.add_field(name="Playtime on KI SCPSL Servers This Month:", value="**This user has not been seen online this month**", inline=False)
        else:
            embed.add_field(name="Playtime on KI SCPSL Servers This Month:", value=f"**{hit[7] // 60}:{hit[7] % 60}** (`{hit[7]} minutes`)", inline=False)
        
        if hit[8] == 0:
            embed.add_field(name="Playtime on KI SCPSL Servers Last Month:", value="**This user has not been seen online last month**", inline=False)
        else:
            embed.add_field(name="Playtime on KI SCPSL Servers Last Month:", value=f"**{hit[8] // 60}:{hit[8] % 60}** (`{hit[8]} minutes`)", inline=False)

        return embed
    

    @staticmethod
    def verify_game_id(game_id:str) -> tuple[bool, typing.Literal["steam", "nwid"]]:
        """Verifiy a game ID is valid, and if its a NWID or STEAM64 ID

        Args:
            game_id (str): Game ID to verify

        Returns:
            tuple[bool, bool]: (is_valid, type)
        """
        # Contains 17 numbers then @steam
        # NWID contains only letters then @northwood
        if game_id.endswith("@northwood"):
            return (True, "nwid")
        elif game_id.endswith("@steam"):
            if game_id.startswith("765611"):
                return (True, "steam")
            else:
                return (False, "steam")
        else:
            return (False, "steam")


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
    @app_commands.rename(steamID="Game ID", user="Discord User")
    @app_commands.describe(steamID="The game ID (steam64 or northwood ID) of the user you want to add. Example: 76561199055339273@steam", user="The discord user you want to add")
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
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=True)
        
        if Database().get_all_moderator_game_ids().__contains__(steamID):
            hit = Database().get_mod(steamID)
            await i.followup.send(f"""This steam64 is already in the database. If you need to update a user use the `update-mod` slash command.\n
                                    ```\n
                                    Found this user in the Database:\n
                                    GAME_ID: {hit[0]}\n
                                    LAST_NICK: {hit[1]}\n
                                    DISCORD_ID: {hit[2]}\n
                                    LAST_SEEN: {hit[3]}\n
                                    PLAYTIME_TODAY: {hit[4]}\n
                                    PLAYTIME_THIS_WEEK: {hit[5]}\n
                                    PLAYTIME_LAST_WEEK: {hit[6]}\n
                                    PLAYTIME_THIS_MONTH: {hit[7]}\n
                                    PLAYTIME_LAST_MONTH: {hit[8]}\n
                                    ```
                                    """, 
                                    ephemeral=True)
            return
        
        Database().add_mod(steamID, str(user.id))

        await i.followup.send("Done! I'll update them the next time they're seen in a server. At the moment this is what their user-profile looks like:", embed=Functions.generate_single_mod_embed(steamID), ephemeral=True)



    @app_commands.command(name="update-mod", description="Update a user in the database")
    @app_commands.rename(steamID="Game ID")
    async def update_user(self, i:discord.Interaction, steamID:str, new_discord:discord.User|discord.Member|None=None, new_gameID:str|None=None):
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            return
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=True)
        
        if not Database().get_all_moderator_game_ids().__contains__(steamID):
            await i.followup.send("This ID is not in the database. Use the `add-mod` slash command to add a user to the database.", ephemeral=True)
            return
        
        if new_discord != None:
            Database().update_mod_discord_id(steamID, str(new_discord.id))
        
        if new_gameID != None:
            Database().update_mod_game_id(steamID, new_gameID)
        
        await i.followup.send("Done! I'll update them the next time they're seen in a server. At the moment this is what their user-profile looks like:", embed=Functions.generate_single_mod_embed(steamID), ephemeral=True)


    @app_commands.command(name="remove-mod", description="Remove a user from the database")
    @app_commands.rename(steamID="Game ID")
    async def remove_user(self, i:discord.Interaction, steamID:str):
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            return
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            return
        
        await i.response.defer(thinking=True, ephemeral=True)
        
        if not Database().get_all_moderator_game_ids().__contains__(steamID):
            await i.followup.send("This ID is not in the database.", ephemeral=True)
            return
        
        Database().remove_mod(steamID)
        await i.followup.send("Done! This user will no longer be updated. All their data has been purged from the database.", ephemeral=True)