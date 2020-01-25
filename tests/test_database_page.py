import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from time import sleep

from test_pages.pages import DatabasePage, HomePage
from tests.locators import LinkLocators

# GLOBAL CONSTANTS
HEADLESS = True

# Options for the Chrome test browser
chrome_options: ChromeOptions = ChromeOptions()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.headless = HEADLESS


# Parameterized fixture for Firefox and Chrome
@pytest.fixture()
def driver_setup(request):
    web_driver = webdriver.Chrome(options=chrome_options)
    request.instance.browser = web_driver
    yield web_driver
    web_driver.quit()

@pytest.mark.usefixtures("driver_setup")
class TestDatabasePage:
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.browser)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(LinkLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(LinkLocators.DATABASE_PAGE_LINK)
        assert 'Database' in linked_page.title

    def test_open_url(self):
        database_page = DatabasePage(self.browser)
        database_page.load()
        assert '404' not in database_page.get_title()

        print(f'Title: {self.browser.title}')
        sleep(2)

    def test_page_has_title(self):
        database_page = DatabasePage(self.browser)
        database_page.load()
        
        assert 'Database' in database_page.get_title()

@pytest.mark.usefixtures("driver_setup")
class TestDataBaseAddFilesPage:
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.browser)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(LinkLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(LinkLocators.DATABASE_ADD_FILES_LINK)
        assert 'Add File' in linked_page.title

