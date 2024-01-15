import logging, os
from _kisb import KISB
from dotenv import load_dotenv
from modules.setup.logging import init_logging

if os.path.exists("../.env"):
    load_dotenv("../.env") # Used for development

init_logging()
logger = logging.getLogger("main")

logger.debug("Clearing Cache & LOCKS")
if os.path.exists('./cache/CACHE'):
    logger.debug("Removing CACHE")
    os.remove('./cache/CACHE')

if os.path.exists('./cache/locks/UPDATER.lock'):
    logger.debug("Removing UPDATER.lock")
    os.remove('./cache/locks/UPDATER.lock')

if os.path.exists('./cache/locks/MOD_UPDATER.lock'):
    logger.debug("Removing MOD_UPDATER.lock")
    os.remove('./cache/locks/MOD_UPDATER.lock')



logger.info("Starting KISB")
# Booting into the bot
bot = KISB()
token = os.getenv('TOKEN')
if not token:
    logger.critical("No token provided!")
    exit()
bot.run(token)