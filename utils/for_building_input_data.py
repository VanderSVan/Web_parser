from dataclasses import dataclass


@dataclass
class HtmlElem:
    xpath: str
    extracted_data_type: str = 'html'
    extracted_tag: str = None
    many: bool = False


@dataclass
class TextElem(HtmlElem):
    extracted_data_type: str = 'text'


@dataclass
class LinkElem(HtmlElem):
    extracted_data_type: str = 'url'
    extracted_tag: str = 'href'


@dataclass
class ButtonElem(HtmlElem):
    extracted_data_type: str = 'html'
