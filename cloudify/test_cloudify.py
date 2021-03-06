import logging
import pytest
import boto3
from tempfile import TemporaryDirectory
from pathlib import Path
import re

from cloudify import is_a_duplicate, unzip, upload, already_in_bucket
from cloudify import s3_duplicate, unzip_and_upload, is_in_s3, get_year_info
from cloudify import get_file_list, put_dupes_at_end, _dupey_looking
from cloudify import get_plain_filename

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

    def test_uploads_file_to_s3(self, plain_test_file: Path):
        test_bucket = 'horsenet-testing'
        destination_folder = ''
        upload_path = ''
        s3 = boto3.client('s3')
        
        upload(plain_test_file, test_bucket, destination_folder)

        if destination_folder:
            upload_path += destination_folder + '/'
        
        # Will throw a botocore.errorfactory.ClientError
        s3.head_object(Bucket=test_bucket, Key=upload_path + plain_test_file.name)
        
        s3.delete_object(Bucket=test_bucket, Key=upload_path + plain_test_file.name)

    def test_sends_md5_hash_with_file(self, plain_test_file):
        test_bucket = 'horsenet-testing'
        s3 = boto3.client('s3')
        
        assert upload(plain_test_file, test_bucket)

        response = s3.head_object(Bucket=test_bucket, Key=plain_test_file.name)

        assert 'md5chksum' in response['Metadata']

        try:
            s3.delete_object(Bucket=test_bucket, Key=plain_test_file.name)
        except:
            pass
        
    @pytest.mark.skip()
    def test_can_scan_for_duplicate_md5_hashes(self):
        assert False

    def test_recognizes_duplicate_in_bucket(self, plain_test_file):
        upload_path = plain_test_file.name
        test_bucket = 'horsenet-testing'

        s3 = boto3.client('s3')
        try:
            s3.upload_file(str(plain_test_file), Bucket=test_bucket, Key=upload_path)
        except Exception as e:
            assert False, 'Error setting up test file in S3'
        
        assert already_in_bucket(upload_path, test_bucket)

        try: 
            s3.delete_object(Bucket=test_bucket, Key=upload_path)
        except Exception as e:
            logging.error(e)

        assert not already_in_bucket(s3_path=upload_path, bucket=test_bucket)

    def test_recognizes_s3_duplicate(self, plain_test_file):
        test_bucket = 'horsenet-testing'
        s3 = boto3.client('s3')

        assert not is_in_s3(file=plain_test_file, bucket=test_bucket)
        assert upload(file=plain_test_file, bucket=test_bucket)
        assert is_in_s3(file=plain_test_file, bucket=test_bucket)

        try:
            s3.delete_object(Bucket=test_bucket, Key=plain_test_file.name)
        except:
            pass

    def test_recognizes_s3_nonduplicate(self, same_name_diff_contents):
        test_bucket = 'horsenet-testing'
        s3 = boto3.client('s3')

        file_1, file_2 = same_name_diff_contents
        assert file_1.name == file_2.name
        assert upload(file=file_1, bucket=test_bucket)
        assert not s3_duplicate(file=file_2, s3_filename=file_2.name, bucket=test_bucket)

        try:
            s3.delete_object(Bucket=test_bucket, Key=file_1.name)
        except:
            pass

    def test_will_not_upload_duplicate(self, plain_test_file):
        test_bucket = 'horsenet-testing'
        
        assert upload(file=plain_test_file, bucket=test_bucket)
        assert not upload(file=plain_test_file, bucket=test_bucket)

        try:
            boto3.client('s3').delete_object(Bucket=test_bucket, Key=plain_test_file.name)
        except:
            pass

    def test_uploads_all_files_in_folder(self, folder_of_files):
        def fix_file_name(file: Path) -> Path:
            if file.stem.endswith('k'):
                year = get_year_info(file)
                return Path(file.parents[0], file.stem + year + file.suffix)
            return file

        test_bucket = 'horsenet-testing'
        test_dir, zip_files, zipped_files = folder_of_files
        s3 = boto3.client('s3')

        # Fix up files names to reflect year that will be added
        zip_files = [fix_file_name(file) for file in zip_files]

        # Run the unzip/upload function
        unzip_and_upload(dir=test_dir, bucket=test_bucket)

        # See if it worked
        for file in zip_files:
            assert is_in_s3(file=file, bucket=test_bucket, destination_path='zip-files')
            s3.delete_object(Bucket=test_bucket, Key='zip-files/'+file.name)
        
        for file in zipped_files:
            assert is_in_s3(file=file, bucket=test_bucket, destination_path='extracted-files')
            s3.delete_object(Bucket=test_bucket, Key='extracted-files/'+file.name)

    def test_doesnt_upload_duplicate_zip_file(self, folder_of_files_with_dupes):
        test_bucket = 'horsenet-testing'
        dir, zip_files, zipped_files, dupe_zips = folder_of_files_with_dupes

        print(f'Dir {dir}')
        print(f'Zip files: {zip_files}')
        print(f'Dupes: {dupe_zips}')
        unzip_and_upload(dir=dir, bucket=test_bucket)

        for file in dupe_zips:
            assert not is_in_s3(file=file, bucket=test_bucket, destination_path='zip-files')
        
        s3 = boto3.client('s3')
        for file in zip_files:
            try:
                s3.delete_object(Bucket=test_bucket, Key='zip-files/' + file.name)
            except Exception as e:
                logging.error(e)
        for file in zipped_files:
            try:
                s3.delete_object(Bucket=test_bucket, Key='extracted-files/' + file.name)
            except Exception as e:
                logging.error(e)

    def test_doesnt_upload_duplicate_unzipped_files(self, zipped_files):
        zip_file, zipped_files = zipped_files
        test_bucket = 'horsenet-testing'

        for file in zipped_files:
            assert upload(file=file, bucket=test_bucket, destination_path='extracted-files')

        for file in zipped_files:
            assert not upload(file=file, bucket=test_bucket, destination_path='extracted-files')

        for file in zipped_files:
            try:
                s3.delete_object(Bucket=test_bucket, Key='extracted-files/' + file.name)
            except Exception as e:
                logging.error(e)

    def test_puts_possible_dupes_at_end_of_file_list(self, folder_of_files_with_dupes):
        test_bucket = 'horsenet-testing'
        dir, zip_files, zipped_files, dupe_zips = folder_of_files_with_dupes

        file_list = get_file_list(dir)
        correct_list = zip_files
        correct_list.extend(dupe_zips)

        file_list = put_dupes_at_end(file_list)
        cutoff_index: int = 0
        while not _dupey_looking(file_list[cutoff_index]):
            cutoff_index += 1

        print(f'File list: {file_list}')
        assert all([_dupey_looking(file) for file in file_list[cutoff_index:]])

    def test_renames_nonduplicate_files_on_upload(self, folder_of_files_with_nondupes):
        temp_dir, zip_files, zipped_files, dupe_files = folder_of_files_with_nondupes
        test_bucket = 'horsenet-testing'
        s3 = boto3.client('s3')

        unzip_and_upload(dir=temp_dir, bucket=test_bucket)

        for file in dupe_files:
            stem = re.search(r'(\w*) ?\(\d+\)', file.stem).group(1)
            corrected_name = Path(temp_dir, stem + file.suffix)

            assert is_in_s3(file=corrected_name, bucket=test_bucket, destination_path='zip-files')

            try:
                s3.delete_object(Bucket=test_bucket, Key='zip-files/' + corrected_name.name)
            except Exception as e:
                logging.error(e)

        for file in zip_files:
            try: s3.delete_object(Bucket=test_bucket, Key='zip-files/' + file.name)
            except: pass

        for file in zipped_files:
            try: s3.delete_object(Bucket=test_bucket, Key='extracted-files/' + file.name)
            except: pass

    def test_deletes_files_after_upload(self, folder_of_files):
        temp_dir, zip_files, zipped_files = folder_of_files
        test_bucket = 'horsenet-testing'
        s3 = boto3.client('s3')

        unzip_and_upload(temp_dir, bucket=test_bucket)

        for file in zip_files:
            assert not file.exists()

        for file in zip_files:
            try:
                s3.delete_object(Bucket=test_bucket, Key='zip-files/'+file.name)
            except Exception as e:
                logging.error(e)

        for file in zipped_files:
            try:
                s3.delete_object(Bucket=test_bucket, Key='extracted-files/'+file.name)
            except Exception as e:
                logging.error(e)

    @pytest.mark.skip()
    def test_deletes_duplicates_in_upload_folder(self, folder_of_files):
        pass
