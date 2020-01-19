class Page:
    def click_link(self, locator_tuple):
        link = self.browser.find_element(*locator_tuple)
        link.click()
        return self.browser

class HomePage(Page):
    URL = 'http://localhost:5000'

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_title(self):
        return self.browser.title

class DatabasePage(Page):
    URL = 'http://localhost:5000/database.html'

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_title(self):
        return self.browser.title
