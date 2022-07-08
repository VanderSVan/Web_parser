from dataclasses import dataclass


@dataclass
class UnsupportedType(TypeError):
    """Raises if it gets unsupported type"""
    text_err: str


class ListCannotBeEmpty(ValueError):
    """Raises if it gets empty list"""


class NotSupportedAttribute(AttributeError):
    """Raises if it gets unsupported attribute"""


@dataclass
class ElementNotFound(ValueError):
    """Raises if it gets wrong element value"""
    text_err: str


@dataclass
class ValueIsEmpty(ValueError):
    """Raises if it gets empty value"""
    text_err: str


@dataclass
class ValueIsWrong(ValueError):
    """Raises if it gets wrong value"""
    text_err: str
