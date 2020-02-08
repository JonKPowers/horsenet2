import pytest
import boto3

from cloudify import is_a_duplicate

class TestCloudFunctions():
    def test_recognizes_duplicate_files(self, horse_duplicates_same_contents):
        file_1, file_2 = horse_duplicates_same_contents

        assert is_a_duplicate(file_2)

    def test_looks_like_dupe_but_no_original_file(self, horse_looks_like_dupe):
        assert not is_a_duplicate(horse_looks_like_dupe)

    def test_looks_like_dupe_but_diff_contents(self, horse_looks_dupe_diff_contents):
        file_1, file_2 = horse_looks_dupe_diff_contents

        assert not is_a_duplicate(file_2)

    def test_unzips_all_files():
        assert False

    def test_uploads_file_to_s3():
        assert False

    def test_sends_md5_hash_with_file():
        assert False

    def test_can_scan_for_duplicate_md5_hashes():
        assert False

    def test_recognizes_duplicate_in_bucket():
        assert False

    def test_will_not_upload_duplicate():
        assert False

    def test_adds_year_to_drf_files():
        assert False

    def test_gets_year_from_csv():
        assert False
