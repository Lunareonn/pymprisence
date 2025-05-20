import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M")
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


file_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
file_handler = logging.FileHandler("test.log", mode="w", encoding="utf-8")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
