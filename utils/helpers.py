import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import ParseResult, urlparse, parse_qs, urlencode
from typing import NoReturn

from utils.type_hinting import Link

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


def save_data_to_json_file(json_file: Path, data: dict) -> NoReturn:
    try:
        parent_dir = json_file.parent
        parent_dir.mkdir(parents=True, exist_ok=True)
        with json_file.open(mode="w") as file:
            json.dump(data, file, indent=2)
    except Exception as err:
        print(f"Got EXCEPTION: "
              f"{err}.\n")
