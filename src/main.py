# For the record I hate having to do this. Version tracking will be fixed in a later update
# TODO: Fix version tracking
import shutil
try:
    shutil.copyfile("/KISB/version.json", "./version.json")
except:
    pass



import os
from core.configs import Config
if str(os.getenv("IS_DOCKER", "false")).lower() == "true":
    # V2.1.0 - Update data directories for Pterodactyl
    Config.Paths.set_data_path("/home/container/data")
    Config.Paths.set_cache_path("/home/container/cache")
else:
    Config.Paths.set_data_path("../data")
    Config.Paths.set_cache_path("../cache")


if os.path.exists("../.env"):
    print("Loading .env file...")
    from dotenv import load_dotenv
    load_dotenv("../.env")


from core.logger import setup_logging
setup_logging()
# Logging can now be used!

import logging
import sys
import time
import threading

from modules.slAPI.main import update_cache
from core.schedule import main as schedule_mainloop

from modules.discord.main import start as discord_start

from modules.discord.aio_files.channel_check import run as _aio_channelCheck_run

logger = logging.getLogger("boot")

# CONFIG DUMP
logger.debug(f"Data DIR: {Config.Paths.get_data_path()}")
logger.debug(f"Cache DIR: {Config.Paths.get_cache_path()}")

logger.info("Welcome to KISB!")

if not os.getenv("TOKEN", None):
    logger.error("No token found in environment variables! Terminating.")
    exit(201)
logger.debug(f"Discord Bot token: {os.getenv('TOKEN', None)}")

if not os.getenv("SCPSL_ID", None):
    logger.error("No SCP:SL ID found in environment variables! Terminating.")
    exit(202)
logger.debug(f"SCP:SL API ID: {os.getenv('SCPSL_ID', None)}")

if not os.getenv("SCPSL_KEY", None):
    logger.error("No SCP:SL Key found in environment variables! Terminating.")
    exit(203)
logger.debug(f"SCP:SL API Key: {os.getenv('SCPSL_KEY', None)}")

# slAPI should hold the main thread until it has downloaded a fresh cache. Also so it can stop the main thread from starting if it fails to do so.


logger.info("Preparing...")

# KISB will now make sure the directory structure it requires is present and will create it if not (The logging one was made earlier (logger.py, line 20))

if not os.path.exists(f"{Config.Paths.data_path}"):
    os.makedirs(f"{Config.Paths.data_path}")
    logger.debug("Root DataDir has been generated")
else:
    logger.debug(f"Root DataDir already exists at ({Config.Paths.data_path})")

if not os.path.exists(f"{Config.Paths.data_path}/discord"):
    os.makedirs(f"{Config.Paths.data_path}/discord")
    logger.debug("Discord DataDir has been generated")
else:
    logger.debug(f"Discord DataDir already exists at ({Config.Paths.data_path}/discord)")

if not os.path.exists(f"{Config.Paths.cache_path}"):
    os.makedirs(f"{Config.Paths.cache_path}")
    logger.debug("Cache Directory has been generated")
else:
    logger.debug(f"Cache Directory already exists at ({Config.Paths.cache_path})")

# KISB should look for any files in its cache directory and remove them.
# Should only really ever be needed when running in the development environment - Edit: Nope, now in petro it needs to always run as cache is persistent

cache_dir_files = os.listdir(Config.Paths.get_cache_path())
if len(cache_dir_files) > 0:
    logger.debug("KISB is purging leftover files in its Cache directory")
else:
    logger.debug("KISB has no files left in it's cache dir to purge.")
for file in cache_dir_files:
    os.remove(f"{Config.Paths.get_cache_path()}/{file}")

# KISB will now log into discord temporarily
# If first boot or the public embed channel id config has changed it will place a placeholder message in the channel until the updater loop updates it during normal runtime
# If not first boot, It will ensure the message exists and can still be edited.
# (This is done before the first SCP:SL API request is made due to the SL API having a harsher rate-limit)
logger.debug("_aio_channelCheck is being called now")
_aio_channelCheck_run()
logger.debug("_aio_channelCheck is finished")

# KISB will now attempt to get the API response for the first time. This is done so if there is an error in fetching for the first time (bad/malformed credentials)
# it prevents the bot from booting and making further requests to the API

try_cache = True
while try_cache:
    try:
        update_cache()
        try_cache = False
    except Exception as e:
        logger.error(f"Failed to update cache: {e}")
        logger.info("Retrying in 10 seconds...")
        time.sleep(10)
logger.info("1/3 - Cache prepared.")

# Spin up new threads for other modules here.
# Keep in mind these need to be daemon threads, or they will prevent the main thread from exiting.

time.sleep(10) # Required to allow multithreaded operations to spread out (lets not kill the 1 CPU core this program will probably be given)

def spinup_thread(func):
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()

spinup_thread(discord_start)

time.sleep(10)

logger.info("2/3 - Modules started.")

# Finally hand off the main thread to schedule.
# Also needs to run a check for exit calls from the other threads. Before continuing 

schedule_mainloop() # <- Blocking