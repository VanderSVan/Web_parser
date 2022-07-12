#  ---------------------------------------------------------------------------
#   JUST EXAMPLE
#  ---------------------------------------------------------------------------
# (This is a sample to improve your understanding of how to work this package)

import os
import time
from pathlib import Path
from enum import Enum
from dotenv import load_dotenv

from selenium_drivers.google_chrome import create_google_chrome_driver

from parsing.general_methods import (
    Page,
    PageParser,
    Authentication
)
from parsing.auth import Authenticator
from utils.for_building_input_data import HtmlElem, LinkElem, ButtonElem


load_dotenv()

# [Paths]
project_dir = Path(__file__).parent
cookies_dir = project_dir.joinpath("cookies")
cookies_file = cookies_dir.joinpath(f"{os.getenv('LOGIN')}_cookies")


class PageAuthData(Enum):
    auth_block = HtmlElem(
        xpath="//form [@class='xdget-block xdget-loginUserForm standard-form container-center "
              "xdget-common-container xdget-common-user-form state-login  form']"
    )
    login_field = HtmlElem(
        xpath="//input [@class='form-control form-field-email'][@placeholder='Введите ваш эл. адрес'][1]"
    )
    password_field = HtmlElem(
        xpath="//input [@class='form-control form-field-password'][@placeholder='Введите пароль']"
    )
    enter_button_login_password = ButtonElem(
        xpath="//button [@class='xdget-block xdget-button btn btn-success' and normalize-space()='Войти']"
    )
    enter_button_cookies = ButtonElem(
        xpath="//button [@class='xdget-block xdget-button btn btn-primary btn-enter']"
    )
    invalid_auth_message = ButtonElem(
        xpath="//button [@class='xdget-block xdget-button btn btn-success btn-error'"
              " and (normalize-space()='Неверный пароль' or normalize-space()='Неверный формат e-mail')]"
    )
    end_of_page = LinkElem(
        xpath="//hr [@class='xdget-block xdget-separator '][@id='xdgetr8009_1_1_1_1']"
    )


# init data
google_driver = create_google_chrome_driver()

parser = PageParser(driver=google_driver)

authentication = Authentication(
    authentication_elem=PageAuthData.auth_block,
    login_field=PageAuthData.login_field,
    password_field=PageAuthData.password_field,
    enter_button_login_password=PageAuthData.enter_button_login_password,
    enter_button_cookies=PageAuthData.enter_button_cookies,
    err_message=PageAuthData.invalid_auth_message
)

authentication_page = Page(elements=[],
                           authentication=authentication,
                           pagination=None,
                           end_of_page=PageAuthData.end_of_page)

auth_page = Authenticator(
    parser=parser,
    url=os.getenv("AUTH_PAGE"),
    page=authentication_page,
    login=os.getenv("LOGIN"),
    password=os.getenv("PASSWORD"),
    cookies_file=cookies_file
)

if __name__ == '__main__':
    # data collection
    try:
        auth_page.get_authenticated()
        time.sleep(3)
    except Exception as error_message:
        print(f"{error_message=}")
    else:
        auth_page.parser.close_browser_window()
