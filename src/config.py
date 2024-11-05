# This file is used to configure KISB from the command line. Migrated from the old system of configuring from the bot

# NOTE: The entire script should be self-sufficient and should only rely on the config.py file itself (aside from any files the script configures)

import time
import os
import json
import discord
import asyncio

if str(os.getenv("IS_DOCKER", "false")).lower() == "true":
    DATA = "/data"
    CACHE = "/cache"
else:
    DATA = "../data"
    CACHE = "../cache"

if os.path.exists("../.env"):
    print("Loading .env file...")
    from dotenv import load_dotenv
    load_dotenv("../.env")


print("Welcome")
print("KISB Config loading...")


def cls():
    if os.name == 'nt':
       os.system("cls")
    else:
        os.system("clear")


async def _send_placeholder(client:discord.Client, channel_id:int):
    channel = client.get_channel(channel_id)
    if not channel:
        print("Channel not found!")
        return None
    
    message = await channel.send("Hello world!") #type:ignore <- Type Checking overreacting

    return message.id

async def _boot_bot(client:discord.Client, token:str, channel_id:int, db_path:str):
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")
        print("Bot started!")
        message_id = await _send_placeholder(client, channel_id)
        print(message_id)
        if not message_id:
            print("Something went wrong when sending the placeholder message! Check your channel ID!")
            await client.close()
        payload = {"message": message_id, "channel": channel_id}
        with open(db_path, 'w') as J:
            json.dump(payload, J)
            print("Done!")
        await client.close()
    
    await client.start(token=token)

    


        



def public_emb_config():
    cls()
    print("KISB Config Menu > Public Embed Config")
    discord_db_path = f"{DATA}/discord/database.json"
    try:
        with open(discord_db_path, 'r') as J:
            discord_db = json.load(J)
    except FileNotFoundError:
        print("Could not find the public embed data file. This is probably the first time you are running KISB.")
        discord_db = {}
    except Exception as e:
        print("Something went wrong when trying to open the public embed data file!")
        print(e)
        discord_db = {}

    print("\n")
    if discord_db == {}:
        print("Channel ID: ...")
        print("Message ID: ...")
    else:
        print(f"Channel ID: {discord_db['channel']}")
        print(f"Message ID: {discord_db['message']}")
    
    print("\n")
    print("0. Return to main menu")
    print("1. Edit channel")
    response = input("Input: ")

    if not response.isdigit():
        print("Not an Integer!")
        time.sleep(2)
        public_emb_config()
    try:
        response = int(response)
    except Exception as e:
        print(e)
        time.sleep(4)
        public_emb_config()
    
    if response == 0:
        main_menu()
    elif response == 1:
        pass
    else:
        public_emb_config()

    channel_id = int(input("[Public Embed] Please supply me the new channel ID you would like me to use: "))
    
    cls()
    print("Please wait...")
    print("Logging into Discord...")

    intents = discord.Intents.all()
    token = os.getenv("TOKEN", None)
    if not token:
        print("FAILED!")
        print("Could not log in to Discord. No Token present in environment!")
        time.sleep(5)
        exit()
    client = discord.Client(intents=intents)
    asyncio.run(_boot_bot(client, token, channel_id, discord_db_path))
    time.sleep(5)
    public_emb_config()


async def private_embed_edit(client:discord.Client, token:str, channel_id:int, db_path:str):
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")
        print("Bot Started!")
        
        channel = client.get_channel(channel_id)
        if not channel:
            print("Channel not found!")
            print(f"Check your channel ID! ({channel_id})")
            print("Check for missing numbers or stray spaces at the start or end!")
            await client.close()
        
        try:
            message = await channel.send("Placeholder") #type:ignore
        except Exception as e:
            print(e)
            await client.close()
        

        message_id = message.id
        if not message_id:
            print(f"Something went wrong when sending the placeholder message! Check your channel ID! ({channel_id})")
            await client.close()
        
        payload = {"message": message_id, "channel": channel_id}
        with open(db_path, 'w') as J:
            json.dump(payload, J)
            print("Done!")
        await client.close()
    
    await client.start(token)



def private_emb_config():
    cls()
    print("KISB Config Menu > Private Embed Config")
    private_db_path = f"{DATA}/discord/private-database.json"
    try:
        with open(private_db_path, 'r') as J:
            private_db = json.load(J)
    except FileNotFoundError:
        print("Could not find the private embed data file. This is probably the first time you are running KISB.")
        private_db = {}
    except Exception as e:
        print("Something went wrong when trying to open the private embed data file!")
        print(e)
        private_db = {}
    
    print("\n")
    if private_db == {}:
        print("Channel ID: ...")
        print("Message ID: ...")
    else:
        print(f"Channel ID: {private_db['channel']}")
        print(f"Message ID: {private_db['message']}")

    print("\n")
    print("0. Return to main menu")
    print("1. Edit channel")
    response = input("Input: ")

    if not response.isdigit():
        print("Not an Integer!")
        time.sleep(2)
        private_emb_config()
    try:
        response = int(response)
    except Exception as e:
        print(e)
        time.sleep(4)
        private_emb_config()

    if response == 0:
        main_menu()
    elif response == 1:
        pass
    else:
        private_emb_config()

    channel_id = int(input("[Mod Embed] Please supply me the new channel ID you would like me to use: "))

    cls()
    print("Please wait...")
    print("Logging into Discord...")

    intents = discord.Intents.all()
    token = os.getenv("TOKEN", None)
    if not token:
        print("FAILED!")
        print("Could not log in to Discord. No Token present in environment!")
        time.sleep(5)
        exit()
    client = discord.Client(intents=intents)
    asyncio.run(private_embed_edit(client, token, channel_id, private_db_path))
    time.sleep(5)
    private_emb_config()




def main_menu():

    cls()
    print("KISB Config Menu")
    print("Please choose from the following options")
    print("\n")
    print("0. Quit")
    print("1. Public Embed Config")
    print("2. Private Embed Config")
    response = input("Input: ")

    if not response.isdigit():
        print("Not an Integer!")
        time.sleep(2)
        main_menu()
    try:
        response = int(response)
    except Exception as e:
        print(e)
        time.sleep(4)
        main_menu()

    if response == 0:
        cls()
        print("Goodbye!")
        time.sleep(1)
        exit()
    elif response == 1:
        public_emb_config()
    elif response == 2:
        private_emb_config()
    else:
        main_menu()

main_menu()