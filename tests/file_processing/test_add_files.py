import pytest
import os
import tempfile
from pathlib import Path

from webapp.add_files import add_db_record
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

class TestAddFiles():
    def test_creates_db_record(self, plain_test_file, db_fixture):
        add_db_record(str(plain_test_file), db_fixture)
        doc_id = secure_filename(str(plain_test_file.name))

        result = db_fixture.get(doc_id, quiet=True)
        try:
            assert result.success is True
        finally:
            db_fixture.remove(doc_id, quiet=True)

    def test_marks_db_record_for_zip(self, zip_test_file, db_fixture):
        add_db_record(str(zip_test_file), db_fixture)
        doc_id = secure_filename(str(zip_test_file.name))

        result = db_fixture.lookup_in(doc_id, SD.get('zip_file'))
        try:
            assert result[0] is True
        finally:
            db_fixture.remove(doc_id, quiet=True)









