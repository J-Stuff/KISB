from discord.ext import commands
from modules.discord._kisb import KISB
from core.configs import Config
import os

bot = KISB()

@bot.command(name="sync")
async def update_tree(ctx:commands.Context):
    if ctx.author.id not in Config.DiscordUsers.authorized_users:
        return
    await ctx.bot.tree.sync()
    await ctx.reply("Synced!")

def start():
    bot.run(os.getenv("TOKEN", "This should never happen but it probably will one day and until then i will add a huge default env here and nobody will notice if you ever see this send me a dm on discord and you win a prize"))
