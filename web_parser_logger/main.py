import logging.config
from typing import NoReturn

from web_parser_logger.settings import logger_config


def set_level_for_other_loggers(level_name: str = 'CRITICAL') -> NoReturn:
    level_names: tuple = ('DEBUG', 'SUCCESS', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    if level_name.upper() in level_names:
        processed_level_name = level_name.upper()
    else:
        processed_level_name = 'CRITICAL'

    for logger_name in logging.Logger.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(processed_level_name)


set_level_for_other_loggers('CRITICAL')
logging.config.dictConfig(logger_config)
logger = logging.getLogger('pages_parser_files')


if __name__ == '__main__':
    logger.debug(f"Debug message with level number is {logging.DEBUG}")
    logger.success(f"Success message with level number is {logging.SUCCESS}")
    logger.info(f"Info message with level number is {logging.INFO}")
    logger.warning(f"Warning message with level number is {logging.WARNING}")
    logger.error(f"Error message with level number is {logging.ERROR}")
    logger.exception(f"Exception message with level number is {logging.ERROR}")
    logger.critical(f"Critical message with level number is {logging.CRITICAL}")
