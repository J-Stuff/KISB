import asyncio, os, threading, logging, schedule, time
from ._manager import DataManager
from _kisb import KISB

LOCK = "./cache/UPDATER.lock"

def _lock_check() -> bool:
    if os.path.exists(LOCK):
        return True
    else:
        return False
    
def _lock(toggle:bool):
    if toggle:
        if not os.path.exists(LOCK):
            open(LOCK, 'w').close()
    else:
        if os.path.exists(LOCK):
            os.remove(LOCK)

def start(bot:KISB):
    logging.debug("Starting Updater")
    if not _lock_check():
        _lock(True)
        threading.Thread(target=updater, args=[bot]).start() # Give the bot an initial cache
        schedule.every(60).seconds.do(updater, bot) # Update the cache every 60 seconds
        threading.Thread(target=runner).start()
    else:
        logging.debug("Updater is already running!")
        return

def updater(bot:KISB):
    logging.debug("Updater Run")
    asyncio.run(DataManager(bot).update_cache())

def runner():
    while True:
        # logging.debug("Updater Timer Run") # DO NOT ENABLE THIS OR YOUR LOGS WILL BE SPAMMED
        schedule.run_pending()
        time.sleep(1)