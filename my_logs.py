from datetime import datetime
from enum import Enum
import os

from constants import LOGS_DIR


class LogServices(Enum):
    SCRAP = "scrap"


LOGS_PATHS = {
    LogServices.SCRAP: os.path.join(LOGS_DIR, "scrap.log")
}


def log_err(service: LogServices, message: str):
    """
    Prints the error message and saves it in its
    proper log file.
    """
    print(message)
    logpath = LOGS_PATHS.get(service, "")
    with open(logpath, "a") as f:
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"{now} - {message}\n")
