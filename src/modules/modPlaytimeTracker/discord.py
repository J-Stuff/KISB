from discord.ext import commands
from _kisb import KISB
from discord import app_commands
from  modules.modPlaytimeTracker._database import Database
from  modules.modPlaytimeTracker._tasks import start
import discord, typing, logging, time

logger = logging.getLogger("main")


class Functions():

    @staticmethod
    def generate_single_mod_embed(user:str) -> discord.Embed:
        logger.debug(f"Generating mod embed for {user}")
        """ Generate an embed for a single mod """
        hit = Database().get_mod(user)
        if hit is None:
            return discord.Embed(title="Mod Playtime", color=discord.Color.dark_red(), description="This user is not in the database")
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
        logger.debug(f"Verifying game ID: {game_id}")
        """Verifiy a game ID is valid, and if its a NWID or STEAM64 ID

        Args:
            game_id (str): Game ID to verify

        Returns:
            tuple[bool, bool]: (is_valid, type)
        """
        # Contains 17 numbers then @steam
        # NWID contains only letters then @northwood
        if game_id.endswith("@northwood"):
            logger.debug("Valid NWID")
            return (True, "nwid")
        elif game_id.endswith("@steam"):
            if game_id.startswith("765611"):
                logger.debug("Valid Steam64 ID")
                return (True, "steam")
            else:
                logger.debug("Invalid Steam64 ID")
                return (False, "steam")
        else:
            logger.debug("Invalid Game ID")
            return (False, "steam")


class Checks():
    # Checked used in slash commands

    @staticmethod
    def is_mod():
        def check(i:discord.Interaction):
            logger.debug(f"Checking if {i.user} is a mod")
            result = i.user.id in Database().get_all_moderator_discord_ids()
            logger.debug(f"Result: {result}")
            return result
        return app_commands.check(check)
    

    # Called Checks
    @staticmethod
    def is_bot_owner(u:discord.Member):
        logger.debug(f"Checking if {u} is bot owner")
        """ STOP! Only pass discord.Member to this and include a check for DMs before this check!"""
        result = u.id == KISB.configs.owner
        logger.debug(f"Checking if {u} is bot owner: {result}")
        return result


    @staticmethod
    def is_bot_admin(u:discord.Member):
        logger.debug(f"Checking if {u} is bot admin")
        """ STOP! Only pass discord.Member to this and include a check for DMs before this check!"""
        result = any([KISB.configs.admin_roles.__contains__(role.id) for role in u.roles]) or KISB.configs.admin_users.__contains__(u.id)
        logger.debug(f"Checking if {u} is bot admin: {result}")
        return 


class ModPlaytimeTracker(commands.Cog):
    def __init__(self, bot:KISB) -> None:
        self.bot = bot
        logger.debug("ModPlaytimeTracker cog has init-ed")
        time.sleep(5)
        start()
        logger.debug("ModPlaytimeTracker tasks have started")
        super().__init__()

    @app_commands.command(name="add-mod", description="Add a user to the database - Locked to Admins")
    @app_commands.rename(steamID="game-id", user="discord-user")
    @app_commands.describe(steamID="The game ID (steam64 or northwood ID) of the user you want to add. Example: 76561199055339273@steam", user="The discord user you want to add")
    async def add_user(self, i:discord.Interaction, steamID:str, user:discord.User|discord.Member):
        logger.info(f"{i.user} [{i.user.id}] ran `add-mod` slash command: {steamID}")
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `add-mod` slash command for: FAILED CHANNEL CHECK")
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `add-mod` slash command for: FAILED MEMBER CHECK")
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `add-mod` slash command for: FAILED PERMISSION CHECK")
            return
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `add-mod` slash command for: FAILED GAME ID CHECK")
            return
        
        logger.debug("Passed quick checks")
        await i.response.defer(thinking=True, ephemeral=True)
        logger.debug("Deferring response...")
        
        if Database().get_all_moderator_game_ids().__contains__(steamID):
            logger.debug("Game ID already in database")
            hit = Database().get_mod(steamID)
            if hit == None:
                await i.followup.send("This ID is in the database, but the user is not. This should technically never be able to happen but it somehow has. Please contact the bot owner.", ephemeral=False)
                logger.error("Game ID in database but user is not!")
                return
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
            logger.info(f"{i.user} [{i.user.id}] failed `add-mod` slash command for: GAME ID ALREADY IN DATABASE")
            return
        
        Database().add_mod(steamID, str(user.id))

        await i.followup.send("Done! I'll update them the next time they're seen in a server. At the moment this is what their user-profile looks like:", embed=Functions.generate_single_mod_embed(steamID), ephemeral=True)



    @app_commands.command(name="update-mod", description="Update a user in the database - Locked to Admins")
    @app_commands.rename(steamID="game-id")
    async def update_user(self, i:discord.Interaction, steamID:str, new_discord:discord.User|discord.Member|None=None, new_gameID:str|None=None):
        logger.info(f"{i.user} [{i.user.id}] ran `update-mod` slash command: {steamID}")
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `update-mod` slash command for: FAILED CHANNEL CHECK")
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `update-mod` slash command for: FAILED MEMBER CHECK")
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `update-mod` slash command for: FAILED PERMISSION CHECK")
            return
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `update-mod` slash command for: FAILED GAME ID CHECK")
            return
        
        logger.debug("Passed quick checks")
        await i.response.defer(thinking=True, ephemeral=True)
        logger.debug("Deferring response...")
        
        if not Database().get_all_moderator_game_ids().__contains__(steamID):
            await i.followup.send("This ID is not in the database. Use the `add-mod` slash command to add a user to the database.", ephemeral=True)
            logger.debug(f"{i.user} [{i.user.id}] failed `update-mod` slash command for: GAME ID NOT IN DATABASE")
            return
        
        if new_discord != None:
            Database().update_mod_discord_id(steamID, str(new_discord.id))
            logger.debug(f"Updated discord ID for user {steamID} to {new_discord.id}")
        
        if new_gameID != None:
            Database().update_mod_game_id(steamID, new_gameID)
            logger.debug(f"Updated game ID for user {steamID} to {new_gameID}")
        
        await i.followup.send("Done! I'll update them the next time they're seen in a server. At the moment this is what their user-profile looks like:", embed=Functions.generate_single_mod_embed(steamID), ephemeral=True)


    @app_commands.command(name="remove-mod", description="Remove a user from the database - Locked to Admins")
    @app_commands.rename(steamID="game-id")
    async def remove_user(self, i:discord.Interaction, steamID:str):
        logger.info(f"{i.user} [{i.user.id}] ran `remove-mod` slash command: {steamID}")
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `remove-mod` slash command for: FAILED CHANNEL CHECK")
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `remove-mod` slash command for: FAILED MEMBER CHECK")
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `remove-mod` slash command for: FAILED PERMISSION CHECK")
            return
        
        valid, id_type = Functions.verify_game_id(steamID)
        if not valid:
            await i.response.send_message("Invalid Game ID. Please format as: `76561199055339273@steam` or `jstuff@northwood`", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `remove-mod` slash command for: FAILED GAME ID CHECK")
            return
        
        logger.debug("Passed quick checks")
        await i.response.defer(thinking=True, ephemeral=True)
        logger.debug("Deferring response...")
        
        if not Database().get_all_moderator_game_ids().__contains__(steamID):
            await i.followup.send("This ID is not in the database.", ephemeral=True)
            logger.debug(f"{i.user} [{i.user.id}] failed `remove-mod` slash command for: GAME ID NOT IN DATABASE")
            return
        
        Database().remove_mod(steamID)
        await i.followup.send("Done! This user will no longer be updated. All their data has been purged from the mod database.", ephemeral=True)

    
    @app_commands.command(name="my-playtime", description="Get your playtime - Locked to mods+")
    @Checks.is_mod()
    async def my_playtime(self, i:discord.Interaction):
        logger.info(f"{i.user} [{i.user.id}] ran `my-playtime` slash command")
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `my-playtime` slash command for: FAILED CHANNEL CHECK")
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `my-playtime` slash command for: FAILED MEMBER CHECK")
            return
        
        logger.debug("Passed quick checks")
        await i.response.defer(thinking=True, ephemeral=True)
        logger.debug("Deferring response...")
        hit = Database().get_mod(str(i.user.id))
        if hit is None:
            await i.followup.send("You are not in the database", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `my-playtime` slash command for: USER NOT IN DATABASE")
            return
        await i.followup.send(embed=Functions.generate_single_mod_embed(hit[0]), ephemeral=False)

    @my_playtime.error
    async def my_playtime_error(self, i:discord.Interaction, error):
        if isinstance(error, commands.CheckFailure):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `my-playtime` slash command for: FAILED PERMISSION CHECK")
        else:
            raise error
        

    @app_commands.command(name="target-playtime", description="Get a user's playtime - Locked to Admins")
    @app_commands.rename(user="discord-user")
    async def target_playtime(self, i:discord.Interaction, user:discord.User|discord.Member):
        logger.info(f"{i.user} [{i.user.id}] ran `target-playtime` slash command: {user}")
        if type(i.channel) == discord.DMChannel:
            await i.response.send_message("This command can only be used in a server", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `target-playtime` slash command for: FAILED CHANNEL CHECK")
            return
        if type (i.user) is not discord.Member:
            await i.response.send_message("This command can only be used by a server member", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `target-playtime` slash command for: FAILED MEMBER CHECK")
            return
        
        if not Checks.is_bot_admin(i.user):
            await i.response.send_message("You do not have permission to use this command", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `target-playtime` slash command for: FAILED PERMISSION CHECK")
            return
        
        logger.debug("Passed quick checks")
        await i.response.defer(thinking=True, ephemeral=True)
        logger.debug("Deferring response...")
        hit = Database().get_mod_from_discord_id(str(user.id))
        if hit is None:
            await i.followup.send("This user is not in the database", ephemeral=True)
            logger.info(f"{i.user} [{i.user.id}] failed `target-playtime` slash command for: USER NOT IN DATABASE")
            return
        await i.followup.send(embed=Functions.generate_single_mod_embed(hit[0]), ephemeral=False)

async def setup(bot:KISB):
    await bot.add_cog(ModPlaytimeTracker(bot))
    logger.info("Cog loaded: Admin Cog")