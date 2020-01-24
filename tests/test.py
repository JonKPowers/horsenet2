import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from time import sleep

from test_pages.home_page import HomePage

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
class Test_URL(BasicTest):
    def test_open_url(self):
        home_page = HomePage(self.driver)
        home_page.load()

        print(f'Title: {self.driver.title}')
        sleep(2)

    def test_page_has_title(self):
        home_page = HomePage(self.driver)
        home_page.load()
        
        assert 'HorseNet' in home_page.get_title()

