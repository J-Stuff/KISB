import discord
import logging
import asyncio
import sys
import os
import json


from core.configs import Config
# Manual discord auth > check if channel exists > check if message exists (make one if not) > close cleanly back to boot thread

logger = logging.getLogger("bot") # This must be run on boot AFTER logging init

def load_message_id():
    return json.load(open(f"{Config.Paths.get_data_path()}/discord/database.json", 'r'))["message"]

def update_message_id(id:int):
    json.dump({"message": id}, open(f"{Config.Paths.get_data_path()}/discord/database.json", 'w'))

async def create_placeholder(client:discord.Client):
    logger.debug("Creating placeholder for public embed...")
    channel = await client.fetch_channel(int(os.getenv("PUB_EMBED_CHANNEL_ID", "")))
    logger.debug(f"Got channel with id: {channel.id}")
    logger.debug("Sending message in channel...")
    message = await channel.send("Placeholder...") #type:ignore
    logger.debug(f"Sent message with ID: {message.id}")
    message_id = message.id
    logger.debug("Storing new message ID in local db")
    update_message_id(message_id)


async def login_and_check_channel(client:discord.Client):
    channel_id = int(os.getenv("PUB_EMBED_CHANNEL_ID", ""))
    logger.debug(f"Running check on {channel_id}")
    try:
        channel:discord.TextChannel = await client.fetch_channel(channel_id) #type:ignore
    except:
        logger.exception("I couldn't load the channel ID you provided me for the public embed!")
        sys.exit(999)


    try:
        message_id = load_message_id()
    except:
        message_id = None
    
    logger.debug(f"Got message ID ({message_id}) from local db file.")

    if message_id == None or message_id == "":
        logger.info("Could not find a message ID stored in the database!")
        await create_placeholder(client)
    
    try:
        message_id = load_message_id()
    except:
        logger.critical("I attempted to set a new message ID in my database after a channel ID change (or initial boot) and failed.")
        sys.exit(999)

    try:
        message = await channel.fetch_message(message_id)
    except:
        logger.info(f"Failed to find old embed message from id ({message_id}) - Creating a new one now...")
        await create_placeholder(client)

    try:
        message_id = load_message_id()
        message = await channel.fetch_message(message_id)
    except:
        logger.critical("I attempted to load a new message for the public embed after a channel ID change (or initial boot) and failed.")
        sys.exit(999)


    # Update the embed to a booting notice so we know the bot can still access it!
    embed = discord.Embed(title="Boot...", color=discord.Color.red())
    embed.set_author(name="KISB", url="https://github.com/J-Stuff/KISB")
    embed.description = f"KISB {Config.Build.Version} booting..."

    await message.edit(content="", embed=embed)




async def channel_test():
    intents = discord.Intents.all()
    logger.debug(f"Intents stated as {intents}")
    client = discord.Client(intents=intents)
    logger.debug("Client created")
    
    try:
        logger.debug("Logging into Discord...")
        await client.login(os.getenv("TOKEN", "NONE"))
        logger.debug("Running check...")
        await login_and_check_channel(client)
    except:
        logger.critical("Channel check failure!")
        sys.exit(999)
    finally:
        await client.close()
        logger.info("Channel Check Successful!")


def run():
    logger.debug("AIO test running...")
    asyncio.run(channel_test())
    logger.debug("AIO test done!")