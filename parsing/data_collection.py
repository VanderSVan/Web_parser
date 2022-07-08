import time
from dataclasses import dataclass
from typing import Iterator, NoReturn, Sequence

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from parsing.exceptions import (
    NotSupportedAttribute,
    ElementNotFound,
    ValueIsEmpty,
    ValueIsWrong
)
from utils.type_hinting import (
    Second,
    Link,
    Element_for_parsing,
)
from utils.decorators import handle_page_parser_exceptions, write_log


@dataclass
class Pagination:
    """
    Pagination block, that contains:
    - pagination block
    - buttons:
        - next page,
        - first_page,
        - previous page,
        - page number.
    """
    pagination_elem: Element_for_parsing
    next_page_button: Element_for_parsing = None
    first_page_button: Element_for_parsing = None
    prev_page_button: Element_for_parsing = None
    page_number_button: Element_for_parsing = None


@dataclass
class Page:
    """
    Page model/sample, that contains:
    - page elements,
    - pagination block,
    - end of page.
    """
    elements: list[Element_for_parsing]
    pagination: Pagination | None
    end_of_page: Element_for_parsing


@handle_page_parser_exceptions
@dataclass
class PageParser:
    driver: webdriver

    @write_log(before_msg="Page opening...", after_msg="Page opened.")
    def open_page(self, page_url: Link, delay_after: Second = 0) -> NoReturn:
        """
        Open website page by link.
        You can set a delay after opening the page.
        """
        self.driver.get(url=page_url)
        time.sleep(delay_after)

    @write_log(before_msg="Closing browser window...", after_msg="Browser window has been closed.")
    def close_browser_window(self) -> NoReturn:
        """Closes the browser window and the selenium driver"""
        self.driver.close()
        self.driver.quit()

    @write_log(before_msg="Looking for element...", after_msg="Element found.")
    def find_element(self, elem: Element_for_parsing) -> WebElement | None:
        """
        Looks for element on a website page by xpath.
        If element not found returns None.
        """
        if hasattr(elem.value, 'xpath'):
            return self.driver.find_element(by=By.XPATH, value=elem.value.xpath)
        else:
            print(f" {elem.name} has no 'xpath' attribute")
            raise NotSupportedAttribute

    @write_log(before_msg="Looking for elements...", after_msg="Elements found.")
    def find_elements(self, elem: Element_for_parsing) -> list[WebElement] | list[None]:
        """
        Looks for identical elements on a website page by xpath.
        If no elements are found, empty list is returned.
        """
        if hasattr(elem.value, 'xpath'):
            return self.driver.find_elements(by=By.XPATH, value=elem.value.xpath)
        else:
            print(f" {elem.name} has no 'xpath' attribute")
            raise NotSupportedAttribute

    @write_log(before_msg="Looking for elements by scroll...", after_msg="Element found by scrolling.")
    def find_element_by_scroll(self, elem: Element_for_parsing,
                               stop_scroll_elem: Element_for_parsing,
                               delay_after: Second = 0) -> WebElement | None:
        """
        Scrolls page until find stop_scroll_elem or elem.
        If stop_scroll_elem is found then the loop is stops.
        So stop_scroll_elem always has to be on the page, otherwise the loop will continue indefinitely.
        Stop_scroll_elem must be below the elem.
        Most often elements stop_scroll_elem and elem are match.
        You can set a delay after the element is found.
        """
        actions = ActionChains(self.driver)
        stop_block: WebElement = self.find_element(elem=stop_scroll_elem)
        block: WebElement = self.find_element(elem=elem)
        while not stop_block:
            if block:
                actions.scroll_to_element(block).perform()
                break
            else:
                self.driver.execute_script(
                    'window.scrollTo(0, window.scrollY + 1000)'
                )
        else:
            if block:
                actions.scroll_to_element(block).perform()
            elif stop_block:
                actions.scroll_to_element(stop_block).perform()
            else:
                raise ElementNotFound
            time.sleep(delay_after)
        return block if block else None

    @write_log(before_msg="Clicking on element...", after_msg="Click completed.")
    def click_element(self, elem: Element_for_parsing) -> NoReturn:
        """Looks for element on a website page and then clicks on it."""
        element = self.find_element(elem=elem)
        element.click()

    @write_log(before_msg="Collecting data from element...", after_msg="Element data has been collected.")
    def get_data_from_identical_elements(self, elem: Element_for_parsing) -> dict[int, str] | str:
        """
        Gets data from page element.
        :return: dict if there are many elements, str if there is one element.
        """
        if elem.value.many:
            result = self._extract_data_from_elements(elem)
        else:
            result = self._extract_data_from_element(elem)
        return result

    @write_log(before_msg="Collecting data from elements...", after_msg="Elements data has been collected..")
    def get_data_from_page_elements(self, elements: Sequence[Element_for_parsing]
                                    ) -> dict[str, dict | str]:
        """Gets data for each element from a sequence."""
        return {elem.name: self.get_data_from_identical_elements(elem) for elem in elements}

    def _extract_data_from_element(self, elem: Element_for_parsing) -> str:
        """
        Extracts data from element in depending on data type
        specified in the element.value.extracted_data_type.
        """
        match elem.value.extracted_data_type:
            case 'text':
                selenium_elem: WebElement = self.find_element(elem)
                return selenium_elem.text
            case 'url':
                selenium_elem: WebElement = self.find_element(elem)
                return selenium_elem.get_attribute(elem.value.extracted_tag)
            case _:
                selenium_elem: WebElement = self.find_element(elem)
                return selenium_elem.get_attribute("innerHTML")

    def _extract_data_from_elements(self, elem: Element_for_parsing) -> dict[int, str]:
        """
        Extracts data from element in depending on data type
        specified in the element.value.extracted_data_type.
        """
        match elem.value.extracted_data_type:
            case 'text':
                selenium_elements: list[WebElement] = self.find_elements(elem)
                return {number: selenium_elem.text
                        for number, selenium_elem in enumerate(selenium_elements, start=1)}
            case 'url':
                selenium_elements: list[WebElement] = self.find_elements(elem)
                return {number: selenium_elem.get_attribute(elem.value.extracted_tag)
                        for number, selenium_elem in enumerate(selenium_elements, start=1)}
            case _:
                selenium_elements: list[WebElement] = self.find_elements(elem)
                return {number: selenium_elem.get_attribute("innerHTML")
                        for number, selenium_elem in enumerate(selenium_elements, start=1)}


@dataclass
class PageDataCollector:
    parser: PageParser
    page: Page
    page_count: int = None

    @write_log(before_msg="Collecting data by URLs...",
               after_msg="Data collection by URLs completed.\n")
    def collect_data_by_urls(self, page_links: list[Link]) -> Iterator[dict[str, dict | str]]:
        """
        This is links iterator.
        Iterate URLs, collecting data from them.
        Returns data from one page and waits for the execution of the higher function.
        """
        page_counter = 0
        for url in page_links:
            if page_counter == self.page_count:
                break
            self.parser.open_page(page_url=url, delay_after=2)
            self.parser.find_element_by_scroll(elem=self.page.end_of_page,
                                               stop_scroll_elem=self.page.end_of_page,
                                               delay_after=1)
            yield self.parser.get_data_from_page_elements(elements=self.page.elements)
            page_counter += 1

        print(f"{page_counter} pages collected")

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

        for _ in self._paginate(start_page, self.page.pagination):
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

            elif self.page_count and (self.page_count == page_counter):
                break

            else:
                self.parser.click_element(elem=pagination.next_page_button)
        print(f"{page_counter} pages collected")
