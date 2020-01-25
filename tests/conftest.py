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

