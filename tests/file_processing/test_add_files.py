import pytest
import os
import tempfile
from pathlib import Path

from webapp.add_files import add_db_record, allowed_filetype, check_for_duplicate
from webapp.add_files import get_formatted_record
import webapp.app_settings
import couchbase.subdocument as SD
from werkzeug.utils import secure_filename

@pytest.fixture()
def plain_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.1')

    yield Path(file_path)

    os.close(fd)
    os.remove(file_path)

@pytest.fixture()
def zip_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.zip')

    yield Path(file_path)

    os.close(fd)
    os.remove(file_path)

@pytest.fixture()
def nonpermitted_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.exe')
    yield Path(file_path)
    os.close(fd)
    os.remove(file_path)

class TestAddFiles():
    def test_creates_db_record(self, plain_test_file, db_fixture):
        add_db_record(str(plain_test_file), db_fixture)
        doc_id = secure_filename(str(plain_test_file.name))

        result = db_fixture.get(doc_id, quiet=True)
        try:
            assert result.success is True
        finally:
            db_fixture.remove(doc_id, quiet=True)

    @pytest.mark.skip()
    def test_marks_db_record_for_zip(self, zip_test_file, db_fixture):
        add_db_record(str(zip_test_file), db_fixture)
        doc_id = secure_filename(str(zip_test_file.name))

        result = db_fixture.lookup_in(doc_id, SD.get('zip_file'))
        try:
            assert result[0] is True
        finally:
            db_fixture.remove(doc_id, quiet=True)

    def test_adds_zip_file_contents_to_record(self, zipped_files):
        zip_file, zip_contents = zipped_files
        record = get_formatted_record(zip_file)

        assert record['zip_contents'] == zip_contents

    def test_rejects_nonpermitted_file_type(self, nonpermitted_test_file, db_fixture):
        assert allowed_filetype(str(nonpermitted_test_file)) == False

    def test_checks_for_duplicate_file(self, plain_test_file, db_fixture):
        assert check_for_duplicate(str(plain_test_file)) == True




