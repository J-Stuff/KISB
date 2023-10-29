import logging, os
from _kisb import KISB
from dotenv import load_dotenv

if os.path.exists("../.env"):
    load_dotenv("../.env") # Used for development

if os.path.exists('./cache/CACHE'):
    os.remove('./cache/CACHE')

if os.path.exists('./cache/UPDATER.lock'):
    os.remove('./cache/UPDATER.lock')

# Logging
if os.path.exists('./data/logs/kisb.old.log'):
    os.remove('./data/logs/kisb.old.log')
if os.path.exists('./data/logs/kisb.log'):
    os.rename('./data/logs/kisb.log', './data/logs/kisb.old.log')

FORMAT = '[%(asctime)s] [%(levelname)s] [%(funcName)s @ %(module)s] %(message)s'

logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(logging.Formatter(FORMAT, datefmt='%d/%m/%Y %H:%M:%S'))
logger.addHandler(streamHandler)

fileHandler = logging.FileHandler(filename='./data/logs/kisb.log', encoding='utf-8', mode='w')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(logging.Formatter(FORMAT, datefmt='%d/%m/%Y %H:%M:%S'))
logger.addHandler(fileHandler)


# Booting into the bot
bot = KISB()
token = os.getenv('TOKEN')
if not token:
    logging.critical("No token provided!")
    exit()
bot.run(token)