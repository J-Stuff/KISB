import os, threading, logging, time
from ._manager import DataManager
from _kisb import KISB

logger = logging.getLogger("main")

LOCK = "./cache/locks/UPDATER.lock"

# STOP! Should only be used to tell if the updater thread is already running!
def _lock_check() -> bool:
    logger.debug("Updater Lock Check Called")
    """STOP! Should only be used to tell if the updater thread is already running!"""
    if os.path.exists(LOCK):
        logger.debug("Updater Lock Check: True")
        return True
    else:
        logger.debug("Updater Lock Check: False")
        return False
    
def _lock(toggle:bool):
    logger.debug(f"Updater Lock Toggled: {toggle}")
    """STOP! Should only be used to tell if the updater thread is already running!"""
    if toggle:
        if not os.path.exists(LOCK):
            logger.debug("Creating LOCK")
            open(LOCK, 'w').close()
        else:
            logger.debug("LOCK already exists!")
    else:
        if os.path.exists(LOCK):
            logger.debug("Removing LOCK")
            os.remove(LOCK)
        else:
            logger.debug("LOCK doesn't exist!")

def start():
    logger.debug("Starting Updater")
    if not _lock_check():
        _lock(True)
        logger.debug("Setting up scheduled loop")
        threading.Thread(target=_runner).start() # Start the updater clock
    else:
        logger.debug("Updater is already running!")
        return

def _updater():
    logger.debug("API Updater Triggered")
    try:
        DataManager().update_cache()
    except Exception as e:
        logger.error(f"Updater Error:\n {e}")
    logger.debug("API Updater Finished a loop")
    return

def _runner():
    while True:
        logger.debug("Updater Timer Run (API)")
        threading.Thread(target=_updater).start()
        time.sleep(60)


# For literal days there was a bug where using the schedule module would cause the bot to run the API update twice, I have no clue why..
# Just use a thread instead of schedule, Save yourself the headache