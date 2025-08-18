import os
from loguru import logger

from dotenv import load_dotenv

load_dotenv()


LOGGER_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {name} {function} {line} {message}"

logger.add(
        os.path.dirname(os.path.realpath(__file__)) + '/logger.log',
        format=LOGGER_FORMAT,
        level='DEBUG',
        rotation='30 MB',
        compression='zip',
        colorize=True
    )
