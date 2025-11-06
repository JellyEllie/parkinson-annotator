import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

#instantiate logger class
logger = logging.getLogger("parkinsons_annotator_logger")
logger.setLevel(logging.DEBUG)

#set formatting for loggers
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M"
    )

# find filepaths for current and parent directories
current_directory = Path(__file__).resolve().parent
parent_directory = current_directory.parent

# ensure logs dir exists
log_dir = parent_directory / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# create handlers
console_handler = logging.StreamHandler() #outputs logs to console
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)


file_handler = RotatingFileHandler(
    log_dir/"parksinsons_annotator.log",
    mode="a", #locates log file via parent directory
    maxBytes=500000,  # 500 KB
    backupCount=2
    )

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)