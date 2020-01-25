import pytest

from test_pages.pages import HomePage
from tests.locators import LinkLocators

@pytest.mark.usefixtures('driver_setup')
class TestDatabaseAddFiles:
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.browser)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(LinkLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(LinkLocators.DATABASE_ADD_FILES_LINK)
        assert 'Add File' in linked_page.title

