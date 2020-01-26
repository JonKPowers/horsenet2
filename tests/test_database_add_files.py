import pytest
import tempfile

from selenium.webdriver.common.by import By

from test_pages.pages import HomePage, DatabaseAddFilesPage
from tests.locators import LinkLocators, DatabaseAddFileLocators

@pytest.mark.usefixtures('driver_setup')
class TestDatabaseAddFiles:
    def test_page_links_from_homepage(self):
        home_page = HomePage(self.browser)
        home_page.load()
        # Click dropdown to expose link
        home_page.click_link(LinkLocators.DATABASE_DROPDOWN)
        linked_page = home_page.click_link(LinkLocators.DATABASE_ADD_FILES_LINK)
        assert 'Add File' in linked_page.title

    def test_page_links_directly(self):
        add_files_page = DatabaseAddFilesPage(self.browser)
        add_files_page.load()

        assert 'add file' in add_files_page.get_title().lower()

    def test_can_upload_file_and_rejects_duplicate_upload(self):
        self.tempfile, self.tempfile_path = tempfile.mkstemp(suffix='.1')

        add_files_page = DatabaseAddFilesPage(self.browser)
        add_files_page.load()

        upload_file = add_files_page.get_element(DatabaseAddFileLocators.FILE_TO_UPLOAD)
        upload_file.send_keys(self.tempfile_path)

        submit_button = add_files_page.get_element(DatabaseAddFileLocators.SUBMIT_BUTTON)
        submit_button.click()

        # First check that file can upload
        assert 'file saved' in self.browser.find_element(By.ID, 'flash_messages').text.lower()

        add_files_page.load()

        upload_file = add_files_page.get_element(DatabaseAddFileLocators.FILE_TO_UPLOAD)
        upload_file.send_keys(self.tempfile_path)

        submit_button = add_files_page.get_element(DatabaseAddFileLocators.SUBMIT_BUTTON)
        submit_button.click()

        # Then check that upload of file with same file name is rejected
        assert 'duplicate file' in self.browser.find_element(By.ID, 'flash_messages').text.lower()


