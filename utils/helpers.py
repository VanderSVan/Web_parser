import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import ParseResult, urlparse, parse_qs, urlencode
from typing import NoReturn

import pickle  # package for load/dump cookies
from selenium import webdriver

from utils.type_hinting import Link
from utils.decorators import try_except_decorator
from utils.decorators import write_log


#  ---------------------------------------------------------------------------
#   Helper classes
#  ---------------------------------------------------------------------------
@dataclass
class Url:
    sample_link: Link
    scheme: str = None
    netloc: str = None
    path: str = None
    query: dict = None

    @property
    def parsed_link(self) -> ParseResult:
        return urlparse(self.sample_link)

    @property
    def url(self) -> str:
        new_parsed_link: ParseResult = self.parsed_link._replace(
            scheme=self.scheme if self.scheme else self.parsed_link.scheme,
            netloc=self.netloc if self.netloc else self.parsed_link.netloc,
            path=self.path if self.path else self.parsed_link.path,
            query=self._add_query() if self.query else self.parsed_link.query
        )
        return new_parsed_link.geturl()

    def _add_query(self):
        query_from_sample_link = parse_qs(self.parsed_link.query)
        for key, value in self.query.items():
            query_from_sample_link[key] = [value]
        query_pairs: [tuple] = [(key, value)
                                for key, value_list in query_from_sample_link.items()
                                for value in value_list]
        return urlencode(query_pairs)


#  ---------------------------------------------------------------------------
#   Helper functions
#  ---------------------------------------------------------------------------
@write_log(before_msg="Saving data to json file...",
           after_msg="Data successfully saved.")
@try_except_decorator
def save_data_to_json_file(json_file: Path, data: dict) -> NoReturn:
    """Writes data to json file"""
    parent_dir = json_file.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    with json_file.open(mode="w") as file:
        json.dump(data, file, indent=2)


@write_log(before_msg="Reading cookies from file...",
           after_msg="Cookies have been successfully read.")
@try_except_decorator
def read_cookies_from_file(driver: webdriver, cookies_file: Path) -> NoReturn:
    """Reads cookies from binary file and add them to webdriver session"""
    with cookies_file.open(mode="rb") as cookies:
        for cookie in pickle.load(cookies):
            driver.add_cookie(cookie)


@write_log(before_msg="Saving cookies to file...",
           after_msg="Cookies successfully saved.")
@try_except_decorator
def write_cookies_to_file(driver: webdriver, cookies_file: Path) -> NoReturn:
    """Writes cookies to binary file from a webdriver session"""
    cookies_file.parent.mkdir(parents=True, exist_ok=True)
    with cookies_file.open(mode="wb") as cookies:
        pickle.dump(driver.get_cookies(), cookies)
