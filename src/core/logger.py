import logging
import sys
import os
from core.configs import Config

# KISB should only log to console & to a file. However the file will be truncated every hour if the file size exceeds 10MB.

# If logging must be done in this file or any earlier in the boot process, use print() instead of logging.

# ######################################
# LOG DIRECTORY STRUCTURE              #
#                                      #
# .                                    #
# ├── kisb.log (current log file)      #
# └── kisb.old.log (previous log file) #
# ######################################

def prep_log_files(LOG_DIR:str):

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logFiles = os.listdir(LOG_DIR)

    if "kisb.old.log" in logFiles:
        os.remove(LOG_DIR + "/kisb.old.log")
    
    if "kisb.log" in logFiles:
        os.rename(LOG_DIR + "/kisb.log", LOG_DIR + "/kisb.old.log")
    


def setup_logging():

    loggersRequired = Config.Static.required_loggers
    DATA_DIR = Config.Paths.get_data_path()
    if not DATA_DIR:
        print("Data directory not set by boot process! Terminating.")
        exit(101)
    LOG_DIR = DATA_DIR + "/logs"

    prep_log_files(LOG_DIR)


    PROD_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    if PROD_LEVEL.lower() == "debug":
        PROD_LEVEL = logging.DEBUG
        print("Logging level set to DEBUG")
    else:
        PROD_LEVEL = logging.INFO

    for loggerToSetup in loggersRequired:




        class CustomFormatter(logging.Formatter):
            
            if PROD_LEVEL == logging.DEBUG:
                FORMAT = '[%(levelname)s] [%(asctime)s]  [%(funcName)s @ %(module)s] %(message)s'
            else:
                FORMAT = '[%(levelname)s] [%(asctime)s] %(message)s'

            FORMATS = {
                logging.DEBUG: f"[{loggerToSetup.upper()}] {FORMAT}",
                logging.INFO: f"[{loggerToSetup.upper()}] {FORMAT}",
                logging.WARNING: f"[{loggerToSetup.upper()}] {FORMAT}",
                logging.ERROR: f"[{loggerToSetup.upper()}] {FORMAT}",
                logging.CRITICAL: f"[{loggerToSetup.upper()}] {FORMAT}",
            }

            def format(self, record):
                log_fmt = self.FORMATS.get(record.levelno)
                formatter = logging.Formatter(log_fmt)
                return formatter.format(record)
        
        logger = logging.getLogger(loggerToSetup)
        logger.handlers.clear() # Ghosting of loggers sometimes(?) happens. Otherwise just a precaution
        # PS - If this is happening check theres nothing using the default logger (logging.info, logging.debug, etc)
        logger.setLevel(PROD_LEVEL)
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(PROD_LEVEL)
        consoleHandler.setFormatter(CustomFormatter())
        logger.addHandler(consoleHandler)

        fileHandler = logging.FileHandler(LOG_DIR + "/kisb.log")
        fileHandler.setLevel(PROD_LEVEL)
        fileHandler.setFormatter(CustomFormatter())
        logger.addHandler(fileHandler)

        logger.debug(f"Logger {loggerToSetup} setup with level DEBUG")
        