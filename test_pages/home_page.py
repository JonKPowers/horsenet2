class HomePage:
    URL = 'http://localhost:5000'

    def __init__(self, browser):
        self.browser = browser

    def load(self, url=URL):
        self.browser.get(url)

    def get_title(self):
        return self.browser.title
