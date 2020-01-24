import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from time import sleep

from test_pages.pages import DatabasePage, HomePage
from tests.locators import MainPageLocators

# GLOBAL CONSTANTS
HEADLESS = True

# Options for the Chrome test browser
chrome_options: ChromeOptions = ChromeOptions()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.headless = HEADLESS

#Options for the Firefox test browser
firefox_options: FirefoxOptions = FirefoxOptions()
firefox_options.headless = HEADLESS

# Parameterized fixture for Firefox and Chrome
@pytest.fixture(params=['chrome', 'firefox'], scope='class')
def driver_init(request):
    if request.param == 'chrome':
        web_driver = webdriver.Chrome(options=chrome_options)
    if request.param == 'firefox':
        web_driver = webdriver.Firefox(options=firefox_options)
    request.cls.driver = web_driver
    yield
    web_driver.close()

@pytest.mark.usefixtures("driver_init")
class BasicTest:
    pass
class TestDatabasePage(BasicTest):
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.driver)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(MainPageLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(MainPageLocators.DATABASE_PAGE_LINK)
        assert 'Database' in linked_page.title

    def test_open_url(self):
        database_page = DatabasePage(self.driver)
        database_page.load()
        assert '404' not in database_page.get_title()

        print(f'Title: {self.driver.title}')
        sleep(2)

    def test_page_has_title(self):
        database_page = DatabasePage(self.driver)
        database_page.load()
        
        assert 'Database' in database_page.get_title()

class TestDatabaseAddFilesPage(BasicTest):
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.driver)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(MainPageLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(MainPageLocators.DATABASE_ADD_FILES_LINK)
        assert 'Add File' in linked_page.title

