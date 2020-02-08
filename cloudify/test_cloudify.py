import pytest
import boto3
from tempfile import TemporaryDirectory
from pathlib import Path

from cloudify import is_a_duplicate, unzip

class TestCloudFunctions():
    def test_recognizes_duplicate_files(self, horse_duplicates_same_contents):
        """Checks that the file is identified as a duplicate if its file name looks like a duplicate and there is a file that looks like its original that has the same contents as the duplicate file."""
        file_1, file_2 = horse_duplicates_same_contents

        assert is_a_duplicate(file_2)

    def test_looks_like_dupe_but_no_original_file(self, horse_looks_like_dupe):
        """Checks that file is identified as NOT a duplicate even if its file name makes it look like a duplicate if there is no file that looks like it could be the original."""
        assert not is_a_duplicate(horse_looks_like_dupe)

    def test_looks_like_dupe_but_diff_contents(self, horse_looks_dupe_diff_contents):
        """Checks that file is identified as NOT a duplicate even if its file name makes it look like a duplicate if the contents of the file don't match the file that looks like the original"""
        file_1, file_2 = horse_looks_dupe_diff_contents

        assert not is_a_duplicate(file_2)

    def test_unzips_all_files(self, zipped_files):
        """Checks that all of the files in a zip file are unzipped to the destination folder"""
        zip_file, list_of_files = zipped_files

        with TemporaryDirectory() as temp_dir:
            unzip(zip_file, temp_dir)

            for file in list_of_files:
                assert Path(zip_file.parents[0], file).exists()

    def test_adds_year_to_unzipped_drf_file(self, zipped_needs_years_file):
        """Checks that when a .DRF file is unzipped that a year is added to the unzipped file name.

        The zip file has the format TRACKMMDDk.zip. The zipped file has the format
        TRACKMMDD.DRF. To make the filename unique for storage purposes, the output
        unzipped file should have the format TRACKMMDDkYYYY.DRF."""
        zip_file, zipped_files, year = zipped_needs_years_file

        with TemporaryDirectory() as temp_dir:
            unzip(zip_file, temp_dir)

            for file in zipped_files:
                assert Path(temp_dir, file.stem + year + file.suffix).exists()
                assert not Path(temp_dir, file.name).exists()

    def test_adds_year_to_drf_zip_file_after_unzip(self, zipped_needs_years_file):
        zip_file, _, year = zipped_needs_years_file
        corrected_name: str = zip_file.stem + year + zip_file.suffix

        with TemporaryDirectory() as temp_dir:
            unzip(zip_file, temp_dir)
            corrected_zip_file = Path(zip_file.parents[0], corrected_name)

            # After test assertions, put zip_file back to original name
            try:
                assert corrected_zip_file.exists()
                assert not zip_file.exists()
            finally:
                try:
                    corrected_zip_file.rename(zip_file)
                except:
                    pass

    def test_uploads_file_to_s3(self):
        assert False

    @pytest.mark.skip()
    def test_sends_md5_hash_with_file(self):
        assert False

    @pytest.mark.skip()
    def test_can_scan_for_duplicate_md5_hashes(self):
        assert False

    @pytest.mark.skip()
    def test_recognizes_duplicate_in_bucket(self):
        assert False

    @pytest.mark.skip()
    def test_will_not_upload_duplicate(self):
        assert False

    @pytest.mark.skip()
    def test_adds_year_to_drf_files(self):
        assert False

    @pytest.mark.skip()
    def test_gets_year_from_csv(self):
        assert False
