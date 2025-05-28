import logging
import os
from datetime import datetime
import tomllib

home_folder = os.path.expanduser("~")
os.makedirs(os.path.join(home_folder, ".pymprisence", "logs"), exist_ok=True)

try:
    with open(os.path.join(home_folder, ".config", "pymprisence", "config.toml"), "rb") as cfg:
        cfg_file = tomllib.load(cfg)

    file_logger_level = cfg_file["logger"]["file_logging_level"]
    console_logger_level = cfg_file["logger"]["console_logging_level"]
except FileNotFoundError:
    logger_level = "INFO"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M")
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
if console_logger_level == "DEBUG":
    console_handler.setLevel(logging.DEBUG)
elif console_logger_level == "INFO":
    console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


file_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
file_handler = logging.FileHandler(f"{home_folder}/.pymprisence/logs/{datetime.now().replace(microsecond=0).strftime("%d-%m-%Y-%H-%M-%S")}.log", mode="w", encoding="utf-8")
file_handler.setFormatter(file_formatter)
if file_logger_level == "DEBUG":
    file_handler.setLevel(logging.DEBUG)
elif file_logger_level == "INFO":
    file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
