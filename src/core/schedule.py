import schedule
import threading
import time
import logging
import datetime

from modules.slAPI.main import blind_update_cache

logger = logging.getLogger("schedule")

def main():

    # Check to ensure the script isn't being started too close to the top of the minute (ratelimit precaution)
    second = datetime.datetime.now().second
    if second > 40:
        logger.debug(f"Schedule thread is holding to avoid rate-limiting the API ({(60-second) + 1} second(s))")
        time.sleep((60-second) + 1) # Sleep to past the top of the second
    


    def spinup_thread(func):
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()

    
    schedule.every().minute.at(":00").do(spinup_thread, blind_update_cache)

    logger.info("3/3 - Schedules configured.")

    while True:
        schedule.run_pending()
        time.sleep(1)
