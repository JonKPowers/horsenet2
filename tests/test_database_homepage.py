import pytest

from test_pages.pages import DatabasePage, HomePage
from tests.locators import LinkLocators

@pytest.mark.usefixtures("driver_setup")
class TestDatabasePage:
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.browser)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(LinkLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(LinkLocators.DATABASE_PAGE_LINK)
        assert 'Database' in linked_page.title

    def test_opens_directly(self):
        database_page = DatabasePage(self.browser)
        database_page.load()
        assert '404' not in database_page.get_title()

        print(f'Title: {self.browser.title}')

    def test_page_has_title(self):
        database_page = DatabasePage(self.browser)
        database_page.load()
        
        assert 'Database' in database_page.get_title()

