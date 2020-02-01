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

# DB-related imports
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator

# DB-related constants
DB_TEST_BUCKET = 'horsenet_testing'
DB_CLUSTER = 'couchbase://localhost'
DB_USER = 'horsenet'
DB_PASSWORD = 'ABCABC123'


# DB fixture for testing db functions outside of webapp
@pytest.fixture()
def db_fixture():
    cluster:Cluster = Cluster(DB_CLUSTER)
    authenticator:PasswordAuthenticator = PasswordAuthenticator(DB_USER, DB_PASSWORD)
    cluster.authenticate(authenticator)
    db = cluster.open_bucket(DB_TEST_BUCKET)
    return db
