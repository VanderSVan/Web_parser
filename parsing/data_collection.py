from dataclasses import dataclass
from typing import Iterator

from parsing.general_methods import PageParser, Page, Pagination
from parsing.exceptions import (
    ElementNotFound,
    ValueIsEmpty,
    ValueIsWrong
)
from utils.type_hinting import Link
from utils.decorators import write_log
from utils.progress_bars import set_progress_bar


@dataclass
class PageDataCollector:
    """
    Class for collecting data from identical pages.
    """
    parser: PageParser
    page: Page
    pages_count: int = None

    @set_progress_bar(known_amount=True)
    @write_log(before_msg="Collecting data by URLs...",
               after_msg="Data collection by URLs completed.\n")
    def collect_data_from_links(self, page_links: list[Link]) -> Iterator[dict[str, dict | str]]:
        """
        This is links iterator.
        Iterate URLs, collecting data from them.
        Returns data from one page and waits for the execution of the higher function.
        """
        number_of_pages = (len(page_links) and self.pages_count) or len(page_links)
        if number_of_pages == 0:
            raise ValueIsEmpty("'PageDataCollector.collect_data_by_urls.page_links' cannot be empty")

        for page_number, url in enumerate(page_links, start=1):
            if page_number > number_of_pages:
                break
            self.parser.open_page(page_url=url, delay_after=2)
            self.parser.find_element_by_scroll(elem=self.page.end_of_page,
                                               stop_scroll_elem=self.page.end_of_page,
                                               delay_after=1)
            yield self.parser.get_data_from_page_elements(elements=self.page.elements)

    @set_progress_bar()
    @write_log(before_msg="Collecting data by click 'next page'...",
               after_msg="Data collection by click 'next page' completed.\n")
    def collect_data_by_click_next_page(self, start_page: Link) -> Iterator[dict[str, dict | str]]:
        """
        This is paginator.
        Iterates through pages by clicking the "next page" button, while collecting data from them.
        Returns data from one page and waits for the execution of the higher function.
        """
        if not isinstance(self.page.pagination, Pagination):
            raise ValueIsWrong("Attribute 'page.pagination' must be an instance of the class Pagination")

        if not self.page.pagination.next_page_button:
            raise ValueIsEmpty("Attribute 'page.pagination.next_page_button' cannot be empty")

        for page_number, _ in enumerate(self._paginate(start_page, self.page.pagination), start=1):
            yield self.parser.get_data_from_page_elements(elements=self.page.elements)

    def _paginate(self, start_page: Link, pagination: Pagination) -> Iterator:
        """
        This is paginator.
        Iterates through pages by clicking the "next page" button.
        Returns None and waits for the execution of the higher function.
        """
        self.parser.open_page(page_url=start_page, delay_after=2)
        page_counter = 0

        while True:
            if not self.parser.find_element_by_scroll(elem=pagination.pagination_elem,
                                                      stop_scroll_elem=self.page.end_of_page,
                                                      delay_after=1):
                raise ElementNotFound(f"Element '{pagination.pagination_elem}' not found.")

            yield

            page_counter += 1

            if not self.parser.find_element_by_scroll(elem=pagination.next_page_button,
                                                      stop_scroll_elem=self.page.end_of_page,
                                                      delay_after=1):
                print("Reached the last page")
                break

            elif self.pages_count and (self.pages_count == page_counter):
                break

            else:
                self.parser.click_element(elem=pagination.next_page_button)
