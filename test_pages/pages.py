from selenium.webdriver.common.by import By

from test_pages.urls import URLs

from test_pages.locators import DatabaseAddFileLocators

class Page:
    def click_link(self, locator_tuple):
        link = self.browser.find_element(*locator_tuple)
        link.click()
        return self.browser

class HomePage(Page):
    URL = URLs.HOME_PAGE

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_title(self):
        return self.browser.title

class DatabasePage(Page):
    URL = URLs.DATABASE_HOME_PAGE

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_title(self):
        return self.browser.title

class DatabaseAddFilesPage(Page):
    URL = URLs.DATABASE_ADD_FILES

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_element(self, locator_tuple):
        return self.browser.find_element(*locator_tuple)

    def get_title(self):
        return self.browser.title

    def get_upload_box(self):
        return self.browser.find_element(*DatabaseAddFileLocators.FILE_TO_UPLOAD_BOX)

    def get_submit_button(self):
        return self.browser.find_element(*DatabaseAddFileLocators.SUBMIT_BUTTON)
    

