import logging.config

from pages_parser_logger.settings import logger_config

for logger_name in logging.Logger.manager.loggerDict:
    logging.getLogger(logger_name).setLevel('CRITICAL')

logging.config.dictConfig(logger_config)
logger = logging.getLogger('pages_parser_full')


if __name__ == '__main__':
    logger.debug(f"Debug message with level number is {logging.DEBUG}")
    logger.success(f"Success message with level number is {logging.SUCCESS}")
    logger.info(f"Info message with level number is {logging.INFO}")
    logger.warning(f"Warning message with level number is {logging.WARNING}")
    logger.error(f"Error message with level number is {logging.ERROR}")
    logger.exception(f"Exception message with level number is {logging.ERROR}")
    logger.critical(f"Critical message with level number is {logging.CRITICAL}")
