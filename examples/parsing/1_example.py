#  ---------------------------------------------------------------------------
#   JUST EXAMPLE
#  ---------------------------------------------------------------------------
# (This is a sample to improve your understanding of how to work this package)

from pathlib import Path
from enum import Enum

from selenium_drivers.google_chrome import create_google_chrome_driver

from parsing.data_collection import (
    Page,
    PageParser,
    Pagination,
    PageDataCollector
)
from utils.for_building_input_data import HtmlElem, TextElem, LinkElem, ButtonElem
from utils.helpers import save_data_to_json_file

# init folder:
current_folder = Path(__file__).parent
collected_data_folder = current_folder.joinpath('collected_data')


# Elements from the website hh.ru
class PageData(Enum):
    vacancy_block = HtmlElem(xpath="//div [@class='vacancy-serp-item']",
                             many=True)
    title = TextElem(xpath="//a [@data-qa='vacancy-serp__vacancy-title']",
                     many=True)
    url = LinkElem(xpath="//a [@data-qa='vacancy-serp__vacancy-title'][@href]",
                   many=True)
    address = TextElem(xpath="//div [@data-qa='vacancy-serp__vacancy-address']",
                       many=True)
    pagination_block = HtmlElem(xpath="//div [@class='pager'][@data-qa='pager-block']")
    next_page = ButtonElem(xpath="//a [@class='bloko-button'][@data-qa='pager-next']")
    previous_page = ButtonElem(xpath="//a [@class='bloko-button'][@data-qa='first-page']")
    end_of_page = HtmlElem(xpath="//div [@class='bloko-gap bloko-gap_bottom']")
    wrong_value = HtmlElem(xpath="//div [@class='bloko-gap bloko-gap_bottodfdfsm']")


# init data
google_driver = create_google_chrome_driver()

parser = PageParser(driver=google_driver)

search_page_pagination = Pagination(pagination_elem=PageData.pagination_block,
                                    next_page_button=PageData.next_page)

search_page_sample = Page(elements=[PageData.title, PageData.url, PageData.address],
                          end_of_page=PageData.end_of_page,
                          pagination=search_page_pagination,
                          authentication=None)

hh_search_pages_data = PageDataCollector(parser=parser,
                                         page=search_page_sample,
                                         pages_count=2)

if __name__ == '__main__':
    # data collection
    try:
        for page_number, data in enumerate(
                hh_search_pages_data.collect_data_by_click_next_page(
                    start_page="https://hh.ru/search/vacancy?area=113&text=python&page=0"
                ),
                start=1
        ):
            json_file_name: str = f"data_from_page_{page_number}.json"
            json_file: Path = collected_data_folder.joinpath(json_file_name)
            save_data_to_json_file(json_file, data)
    except Exception as error_message:
        print(f"{error_message=}")
    else:
        hh_search_pages_data.parser.close_browser_window()
