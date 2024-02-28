import os, logging
from termcolor import colored
from logging import LogRecord

"""
Logging setup for the logger 'main'
"""


def init_logging():
    """Initializes logging for the web interface, using the logger 'web'"""
    if os.getenv("PROD_LEVEL") is not None:
        logLevel = os.getenv("PROD_LEVEL")
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
            logging.DEBUG: "[WEB] " + colored("[%(levelname)s]", "light_cyan", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "white"),
            logging.INFO: "[WEB] " + colored("[%(levelname)s]", "cyan", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "white"),
            logging.WARNING: "[WEB] " + colored("[%(levelname)s]", "yellow", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "yellow"),
            logging.ERROR: "[WEB] " + colored("[%(levelname)s]", "red", attrs=["bold"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "red"),
            logging.CRITICAL: "[WEB] " + colored("[%(levelname)s]", "red", attrs=["bold", "underline"]) + colored(" - ", attrs=["bold"]) + colored(FORMAT, "red", attrs=["bold"])
        }

        def format(self, record: LogRecord) -> str:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
        
    logger = logging.getLogger("web")
    logger.setLevel(logLevel)

    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    logger.debug("Debug mode enabled")