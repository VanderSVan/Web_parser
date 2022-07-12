import inspect
from typing import Any, NoReturn

from selenium.common.exceptions import NoSuchElementException
from rich.console import Console

from page_parser_logger.main import logger

console = Console()


def handle_func_errors(func):
    def inner_wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except NoSuchElementException:
            message = (
                f"NoSuchElementException from function '{func.__name__}': "
                f"Element '{args[0].name}' does not exists.\n"
            )
            logger.exception(message)
            console.print_exception()
        except Exception as ex:
            message = f"{ex.__class__.__name__} from '{func.__name__}': {ex}"
            logger.exception(message)
            console.print_exception()

    return inner_wrapper


def handle_page_parser_exceptions(cls):
    # Get all callable attributes of the class
    callable_attributes = {k: v for k, v in cls.__dict__.items()
                           if callable(v)}
    # Decorate each callable attribute of to the input class
    for name, func in callable_attributes.items():
        decorated = handle_func_errors(func)
        setattr(cls, name, decorated)
    return cls


def get_logger(level: str):
    match level.upper():
        case 'SUCCESS':
            logger_output = logger.success
        case 'INFO':
            logger_output = logger.info
        case 'WARNING':
            logger_output = logger.warning
        case 'ERROR':
            logger_output = logger.error
        case 'EXCEPTION':
            logger_output = logger.exception
        case 'CRITICAL':
            logger_output = logger.critical
        case _:
            logger_output = logger.debug
    return logger_output


def write_log(before_msg: str, after_msg: str,
              before_level: str = 'DEBUG',
              after_level: str = 'SUCCESS') -> Any | NoReturn:
    def decorator(func):
        logger_before = get_logger(before_level)
        logger_after = get_logger(after_level)

        def gen_wrapper(*args, **kwargs):
            logger_before(before_msg)
            for output in func(*args, **kwargs):
                yield output
            logger_after(after_msg)

        def func_wrapper(self, *args, **kwargs):
            logger_before(before_msg)
            result = func(self, *args, **kwargs)
            logger_after(after_msg)
            return result

        return gen_wrapper if inspect.isgeneratorfunction(func) else func_wrapper

    return decorator
