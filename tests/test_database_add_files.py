import os
import pytest
import tempfile

from selenium.webdriver.common.by import By

from test_pages.pages import HomePage, DatabaseAddFilesPage
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

    def test_page_links_directly(self):
        add_files_page = DatabaseAddFilesPage(self.browser)
        add_files_page.load()

        assert 'add file' in add_files_page.get_title().lower()

    def test_can_add_a_file(self):
        fd, temp_file = tempfile.mkstemp(suffix='.1')

        add_files_page = DatabaseAddFilesPage(self.browser)
        add_files_page.load()

        upload_box = add_files_page.get_upload_box()
        upload_box.send_keys(temp_file)

        submit_button = add_files_page.get_submit_button()
        submit_button.click()

        assert 'File saved' in self.browser.find_element(By.ID, 'flash_messages').text

        # Cleanup the temporary file
        os.close(fd)
        os.remove(temp_file)

    def test_rejects_duplicate_file(self):
        fd, temp_file = tempfile.mkstemp(suffix='.1')

        add_files_page = DatabaseAddFilesPage(self.browser)
        add_files_page.load()

        # First upload should go through with no problem
        upload_box = add_files_page.get_upload_box()
        upload_box.send_keys(temp_file)

        submit_button = add_files_page.get_submit_button()
        submit_button.click()

        assert 'File saved' in self.browser.find_element(By.ID, 'flash_messages').text

        # Uploading a second file should be rejected
        upload_box = add_files_page.get_upload_box()
        upload_box.send_keys(temp_file)

        submit_button = add_files_page.get_submit_button()
        submit_button.click()

        assert 'Duplicate file' in self.browser.find_element(By.ID, 'flash_messages').text

        # Cleanup temporary file
        os.close(fd)
        os.remove(temp_file)
        

