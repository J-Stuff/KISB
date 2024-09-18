import os
from core.configs import Config
if str(os.getenv("IS_DOCKER", "false")).lower() == "true":
    Config.Paths.set_data_path("/data")
    Config.Paths.set_cache_path("/cache")
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

logger = logging.getLogger("boot")

# CONFIG DUMP
logger.debug(f"Data DIR: {Config.Paths.get_data_path()}")
logger.debug(f"Cache DIR: {Config.Paths.get_cache_path()}")

logger.info("Welcome to KISB!")

if not os.getenv("TOKEN", None):
    logger.error("No token found in environment variables! Terminating.")
    exit(201)

if not os.getenv("SCPSL_ID", None):
    logger.error("No SCP:SL ID found in environment variables! Terminating.")
    exit(202)

if not os.getenv("SCPSL_KEY", None):
    logger.error("No SCP:SL Key found in environment variables! Terminating.")
    exit(203)

# slAPI should hold the main thread until it has downloaded a fresh cache. Also so it can stop the main thread if it fails to do so.


logger.info("Preparing...")

# KISB will now make sure the directory structure it requires is present and will create it if not (The logging one was made earlier (logger.py, line 20))

if not os.path.exists(f"{Config.Paths.data_path}/discord"):
    os.makedirs(f"{Config.Paths.data_path}/discord")
    logger.debug("Discord DataDir has been generated")


# KISB should look for any files in its cache directory and remove them.
# Should only really ever be needed when running in the development environment

cache_dir_files = os.listdir(Config.Paths.get_cache_path())
if len(cache_dir_files) > 0:
    logger.debug("KISB is purging leftover files in its Cache directory")
for file in cache_dir_files:
    os.remove(f"{Config.Paths.get_cache_path()}/{file}")


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