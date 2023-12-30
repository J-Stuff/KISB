import os, logging
from termcolor import colored
from logging import LogRecord

"""
Logging setup for the logger 'main'
"""


def init_logging():
    """Initializes logging for the bot, using the logger 'main'"""
    if os.getenv("LOGGING_LEVEL") is not None:
        logLevel = os.getenv("LOGGING_LEVEL")
        if logLevel == 'debug':
            logLevel = logging.DEBUG
        elif logLevel == 'DEBUG':
            logLevel = logging.DEBUG
        elif logLevel == 'info':
            logLevel = logging.INFO
        else:
            logLevel = logging.INFO
    else:
        logLevel = logging.INFO

    class CustomFormatter(logging.Formatter):
        if logLevel == logging.DEBUG:
            FORMAT = '[%(asctime)s]  [%(funcName)s @ %(module)s] %(message)s'
        else:
            FORMAT = '[%(asctime)s] %(message)s'
        FORMATS = {
            logging.DEBUG: colored("[%(levelname)s]", "light_cyan", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "white"),
            logging.INFO: colored("[%(levelname)s]", "cyan", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "white"),
            logging.WARNING: colored("[%(levelname)s]", "yellow", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "yellow"),
            logging.ERROR: colored("[%(levelname)s]", "red", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "red"),
            logging.CRITICAL: colored("[%(levelname)s]", "red", attrs=["bold", "underline"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "red", attrs=["bold"])
        }

        def format(self, record: LogRecord) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
        
    # Basically the same as the formatter above but without the colors
    class CustomFileFormatter(logging.Formatter):
        if logLevel == logging.DEBUG:
            FORMAT = '[%(asctime)s]  [%(funcName)s @ %(module)s] %(message)s'
        else:
            FORMAT = '[%(asctime)s] %(message)s'
        FORMATS = {
            logging.DEBUG: "[%(levelname)s] - " + FORMAT,
            logging.INFO: "[%(levelname)s] - " + FORMAT,
            logging.WARNING: "[%(levelname)s] - " + FORMAT,
            logging.ERROR: "[%(levelname)s] - " + FORMAT,
            logging.CRITICAL: "[%(levelname)s] - " + FORMAT
        }

        def format(self, record: LogRecord) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
        


    logger = logging.getLogger("main")
    logger.setLevel(logLevel)

    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)


    if os.path.exists('./data/logs/kisb.old.log'):
        os.remove('./data/logs/kisb.old.log')
    if os.path.exists('./data/logs/kisb.log'):
        os.rename('./data/logs/kisb.log', './data/logs/kisb.old.log')

    fileHandler = logging.FileHandler(filename='./data/logs/kisb.log', encoding='utf-8', mode='w')
    fileHandler.setLevel(logLevel)
    fileHandler.setFormatter(CustomFileFormatter())
    logger.addHandler(fileHandler)

    logger.debug("Debug mode enabled")