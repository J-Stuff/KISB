import asyncio, os, threading, logging, schedule, time
from ._manager import DataManager
from _kisb import KISB

logger = logging.getLogger("main")

LOCK = "./cache/locks/UPDATER.lock"

# STOP! Should only be used to tell if the updater thread is already running!
def _lock_check() -> bool:
    """STOP! Should only be used to tell if the updater thread is already running!"""
    if os.path.exists(LOCK):
        return True
    else:
        return False
    
def _lock(toggle:bool):
    """STOP! Should only be used to tell if the updater thread is already running!"""
    if toggle:
        if not os.path.exists(LOCK):
            open(LOCK, 'w').close()
    else:
        if os.path.exists(LOCK):
            os.remove(LOCK)

def start(bot:KISB):
    logger.debug("Starting Updater")
    if not _lock_check():
        _lock(True)
        threading.Thread(target=_updater, args=[bot]).start() # Give the bot an initial cache

        schedule.every(60).seconds.do(_updater, bot) # Update the cache every 60 seconds - Prepare the updater clock
        threading.Thread(target=runner).start() # Start the updater clock
    else:
        logger.debug("Updater is already running!")
        return

def _updater(bot:KISB):
    logger.debug("Updater Run")
    try:
        asyncio.run(DataManager(bot).update_cache())
    except Exception as e:
        logger.error(f"Updater Error:\n {e}")

def runner():
    while True:
        # logger.debug("Updater Timer Run") # Do not enable in prod
        schedule.run_pending()
        time.sleep(1)