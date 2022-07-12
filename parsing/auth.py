from pathlib import Path
from dataclasses import dataclass

from selenium.webdriver.remote.errorhandler import ElementNotInteractableException

from parsing.general_methods import PageParser, Page
from parsing.exceptions import (
    AuthCookiesIncorrect,
    AuthLoginPasswordIncorrect,
    BreakOut
)
from utils.helpers import read_cookies_from_file, write_cookies_to_file
from utils.decorators import write_log


@dataclass()
class Authenticator:
    parser: PageParser
    url: str
    page: Page
    login: str
    password: str
    cookies_file: Path

    @write_log(before_msg="Passing authentication...", after_msg="Authentication successful.")
    def get_authenticated(self):
        """
        Main function.
        Authentication user on the website page.
        For beginning tries to authentication through cookies if they not exist, then
        authentication through login and password.
        """
        self.parser.open_page(page_url=self.url, delay_after=1)

        try:
            if self.cookies_file.exists():
                self._auth_via_cookies()
            else:
                self._auth_via_login_password()
        except AuthCookiesIncorrect:
            raise BreakOut("Authentication is not successful. Please delete the cookies.")
        except AuthLoginPasswordIncorrect:
            raise BreakOut("Authentication is not successful. Please check your login and password")

    @write_log(before_msg="Authentication through cookies...",
               after_msg="Cookie authentication completed.")
    def _auth_via_cookies(self):
        """Authentication through cookies"""
        read_cookies_from_file(self.parser.driver, self.cookies_file)
        self.parser.driver.refresh()
        try:
            self.parser.click_element(self.page.authentication.enter_button_cookies)
        except ElementNotInteractableException:
            raise AuthCookiesIncorrect("Incorrect cookies")

    @write_log(before_msg="Authentication through login and password...",
               after_msg="Login/password authentication completed.")
    def _auth_via_login_password(self):
        """Authentication through login and password"""
        self.parser.fill_in_field(field=self.page.authentication.login_field,
                                  data=self.login,
                                  delay_after=1)

        self.parser.fill_in_field(field=self.page.authentication.password_field,
                                  data=self.password,
                                  delay_after=1)

        self.parser.click_element(self.page.authentication.enter_button_login_password)
        error_message = self.parser.find_arising_element(elem=self.page.authentication.err_message,
                                                         appearance_delay=3)
        if not error_message:
            write_cookies_to_file(self.parser.driver, self.cookies_file)
        else:
            raise AuthLoginPasswordIncorrect("wrong login or password")
