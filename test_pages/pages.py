from test_pages.urls import URLs

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
