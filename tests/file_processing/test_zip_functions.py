import pytest
from zipfile import ZipFile
import tempfile
from pathlib import Path
import random
import os

from webapp.zip_functions import get_file_list, unzip_files, extract_file, same_file
from webapp.zip_functions import file_already_in_uploads, get_unique_filename
from webapp.zip_functions import extract_and_check_if_same
from webapp.app_settings import UPLOAD_FOLDER

class TestZipFunctions:
    def test_gets_zipped_file_names(self, zipped_files):
        zip_file, zipped_file_names = zipped_files

        file_list = get_file_list(zip_file)

        assert all([file in zipped_file_names for file in file_list])
        assert all([file in file_list for file in zipped_file_names])

    def test_unzips_files_to_upload_dir(self, zipped_files):
        """Tests that files are unloaded into the UPLOAD_FOLDER"""
        zip_file, zipped_file_names = zipped_files
        unzip_files(zip_file)
        
        try:
            for file in zipped_file_names:
                assert Path(UPLOAD_FOLDER, file).exists()

        # Delete test files from upload folder once we're done.
        finally:
            for file in zipped_file_names:
                Path(UPLOAD_FOLDER, file).unlink()

    def test_unzips_single_file_to_upload_fie(self, zipped_files):
        """Tests ability to extract a single file from a zip into the UPLOAD_FOLDER"""
        zip_file, zipped_file_names = zipped_files
        file_to_get = zipped_file_names[random.randrange(3)]

        extract_file(zip_file, file_to_get)
        extracted_file = Path(UPLOAD_FOLDER, file_to_get)

        try:
            assert extracted_file.exists()
        finally:
            if extracted_file.exists():
                extracted_file.unlink()

    def test_extracts_and_identifies_duplicate_files(self, duplicate_in_zip):
        """Tests ability to extract file from ZipFile and compare it to an existing file"""
        zip_file, duplicate_file, zip_contents = duplicate_in_zip

        assert extract_and_check_if_same(zip_file, zip_contents[random.randrange(3)], duplicate_file)

    def test_identifies_duplicate_files(self, duplicate_files, nonduplicate_files):
        """Tests ability to distinguish files that have the same or different contents."""
        same_file1, same_file2 = duplicate_files
        diff_file1, diff_file2 = nonduplicate_files

        assert same_file(same_file1, same_file2)
        assert not same_file(diff_file1, diff_file2)

    def test_identifies_same_file_name(self, plain_test_file):
        """Tests ability to identify when file name already exists in UPLOAD_FOLDER"""
        dummy_file = Path(UPLOAD_FOLDER, plain_test_file.name)
        with open(dummy_file, 'w') as file:
            file.write('This is a test')

        try:
            assert file_already_in_uploads(plain_test_file)
        finally:
            dummy_file.unlink()

    def test_finds_unique_file_name(self, plain_test_file):
        """Tests ability to find unique file name in UPLOAD_FOLDER."""
        stem = plain_test_file.stem
        suffix = plain_test_file.suffix

        dummy_file1 = Path(UPLOAD_FOLDER, plain_test_file.name)
        dummy_file2 = Path(UPLOAD_FOLDER, stem + '_0' + suffix)
        dummy_file3 = Path(UPLOAD_FOLDER, stem + '_1' + suffix)
        target_file = Path(UPLOAD_FOLDER, stem + '_2' + suffix)

        for file in [dummy_file1, dummy_file2, dummy_file3]:
            with open(file, 'w') as f:
                f.write('This is a test file.')

        assert get_unique_filename(plain_test_file) == target_file


