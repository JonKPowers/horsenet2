import pytest
import os

from webapp.add_files import add_file
import couchbase.subdocument as SD

TEST_FILE_PATH = '/data/python/horsenet_2/test_files/add_file_test.1'
TEST_FILE_DOCID = 'add_file_test_1'

TEST_ZIP_FILE_PATH = '/data/python/horsenet_2/test_files/add_zip_file_test.zip'
TEST_ZIP_FILE_DOCID = 'add_zip_file_test_zip'

class TestAddFiles():
    def test_creates_db_record(self, db_fixture):
        add_file(TEST_FILE_PATH, db_fixture)

        result = db_fixture.get(TEST_FILE_DOCID, quiet=True)
        assert result.success is True

        db_fixture.remove(TEST_FILE_DOCID, quiet=True)

    def test_db_record_for_zip(self, db_fixture):
        add_file(TEST_ZIP_FILE_PATH, db_fixture)
        result = db_fixture.lookup_in(TEST_ZIP_FILE_DOCID, SD.get('zip_file'))
        try:
            assert result[0] is True
        finally:
            db_fixture.remove(TEST_ZIP_FILE_DOCID, quiet=True)









