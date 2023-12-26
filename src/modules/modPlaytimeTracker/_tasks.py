import time, logging, threading, schedule, os, datetime

from dataManager._manager import DataManager as DM
from ._database import Database
from _kisb import KISB

# Lock check for API data
def data_lock_check() -> bool:
    return DM.lock_check()

class _Lock():
    MOD_DB_LOCK = "./cache/locks/MOD_UPDATER.lock"

    @classmethod
    def mod_updater_lock_check(cls) -> bool:
        if os.path.exists(cls.MOD_DB_LOCK):
            return True
        else:
            return False
        
    @classmethod
    def mod_updater_lock(cls, toggle:bool):
        if toggle:
            if not os.path.exists(cls.MOD_DB_LOCK):
                open(cls.MOD_DB_LOCK, 'w').close()
        else:
            if os.path.exists(cls.MOD_DB_LOCK):
                os.remove(cls.MOD_DB_LOCK)


def update_online_mods():
    logging.debug("Updating Online Mods")
    """
    THIS MUST BE RUN ONCE EVERY 60 SECONDS || This function will check it's metadata to ensure it is not run too much
    """
    while data_lock_check():
        time.sleep(1)
    try:
        latest_data = DM.read_cache()['sl']
    except Exception as e:
        logging.error(f"Error reading cache: {e}")
        return
    SL_TRANSLATIONS = KISB.configs.servers
    DB = Database()
    mods_ids = DB.get_all_moderator_game_ids()
    for server in latest_data['Servers']:
        if str(server['ID']) in SL_TRANSLATIONS.keys():
            for player in server['PlayersList']:
                if player['ID'] in mods_ids:
                    logging.info(f"Updating playtime for {player['Nickname']} ({player['ID']})")
                    DB.add_playtime(player['ID']) # Meta run check is done here
                    DB.update_last_seen(player['ID'])
                    if player["Nickname"] == None:
                        DB.update_last_nick(player['ID'], player['ID'])
                    else:
                        DB.update_last_nick(player['ID'], player['Nickname'])

def day_tickover_runner():
    """This function should be run every day at 6:00AM"""
    logging.debug("Running Tickover Check for Day")
    while data_lock_check():
        time.sleep(1)
    DB = Database()
    DB.reset_playtime_today()

def week_tickover_runner():
    """This function should be run every week at 6:00AM on Monday"""
    logging.debug("Running Tickover Check for Week")
    while data_lock_check():
        time.sleep(1)
    DB = Database()
    DB.tickover_playtime_week()

def month_tickover_runner():
    """This function should be run every month at 6:00AM on the 1st -- THIS FUNCTION CHECKS THE DATE OF THE MONTH"""
    logging.debug("Running Tickover Check for Month")
    while data_lock_check():
        time.sleep(1)
    if not datetime.datetime.today().day == 1:
        logging.debug("Not the 1st of the month! Skipping...")
        return
    DB = Database()
    DB.tickover_playtime_month()




def start():
    logging.info("Starting Playtime Tracker")
    if _Lock.mod_updater_lock_check():
        logging.info("Playtime Tracker is already running!")
        return
    _Lock.mod_updater_lock(True)
    
    threading.Thread(target=update_online_mods).start() # Update the db initially

    schedule.every(60).seconds.do(update_online_mods) # Update the db every 60 seconds - Prepare the updater clock
    schedule.every().day.at("06:00").do(day_tickover_runner) # Run the day tickover at 6:00AM
    schedule.every().monday.at("06:00").do(week_tickover_runner) # Run the week tickover at 6:00AM on Monday
    schedule.every().day.at("06:00").do(month_tickover_runner) # Run the month tickover at 6:00AM 
    threading.Thread(target=runner).start() # Start the updater clock


def runner():
    while True:
        # logging.debug("Updater Timer Run") # Do not enable in prod
        schedule.run_pending()
        time.sleep(1)