import os
from zipfile import ZipFile
import re
from pathlib import Path
import hashlib
import logging
import boto3
from typing import List, Tuple
from tempfile import TemporaryDirectory
import csv
import base64


INBOUND_DIR = '/data/python/horsenet_2/inbound_horse_data'
BUCKET = 'horsenet-data-files'
ZIP_FOLDER = 'zip-files'
EXTRACTED_FOLDER = 'extracted-files'
s3 = boto3.client('s3')

def process_inbound_dir() -> None:
    # First get rid of duplicates in INBOUND_DIR
    dupe_files: List[Path] = get_file_list(INBOUND_DIR, dupes_only=True)
    for file in dupe_files:
        if is_a_duplicate(file):
            file.unlink()

    # Next unzip the remaining files and upload them along with the original zip
    s3 = boto3.client('s3')
    file_list: List[Path] = get_file_list(INBOUND_DIR)
    with TemporaryDirectory() as temp_dir:
        for file in file_list:
            
            assert False # FINISH THE THIS. PUT UNZIP PROCESS IN SEPARATE FUNCTION

def unzip_and_upload(dir: str, bucket: str) -> bool:
    # First process all the zip files
    files = get_file_list(dir)
    files = [file for file in files if file.suffix.lower() == '.zip']
    # Possible duplicates at end of list:
    files = put_dupes_at_end(files)

    with TemporaryDirectory() as temp_dir:
        for file in files:
            if check_for_s3_duplicate(file=file, bucket=bucket, destination_path=ZIP_FOLDER):
                print(f'Skipped duplicate: {file}')
                continue
            zip_file, unzipped_files = unzip(file, temp_dir)
            for unzipped_file in unzipped_files:
                #if s3_duplicate(file=unzipped_file.name, bucket=bucket, destination_path='extracted-files'):
                assert upload(file=unzipped_file, bucket=bucket, destination_path=EXTRACTED_FOLDER)
            assert upload(file=zip_file, bucket=bucket, destination_path=ZIP_FOLDER)

def check_for_s3_duplicate(file: Path, bucket: str, destination_path: str) -> bool:
    parts = get_possible_dupe(file)
    if parts is None:
        return False
    print(f'Checking out possible duplicate: {file}')

    plain_filename = Path(file.parents[0], parts.group(1) + file.suffix)
    print(f'Plain file: {plain_filename}')
    if not is_in_s3(file=plain_filename, bucket=bucket, destination_path=destination_path):
        print('Plain file not in s3')
        return False
    if not s3_duplicate(file=file, s3_filename=plain_filename.name, 
            bucket=bucket, destination_path=destination_path):
        print('Plain file doesn\'t match md5 hash')
        return False
    print('Plain file is a duplicate')
    return True


def get_file_list(dir: str, dupes_only=False) -> List[Path]:
    def return_file(file: Path) -> bool:
        if not file.is_file():
            return False
        elif dupes_only and re.search(r' ?\(\d\)', file.stem) is None:
            return False
        return True

    files: List[Path] = [Path(dir, file) for file in os.listdir(dir)]
    return [file for file in files if return_file(file)]

def put_dupes_at_end(file_list: List[Path]) -> List[Path]:
    """Put the files that look like a duplicate at the end of the file_list"""
    dupes: List[Path] = list()
    plains: List[Path] = list()
    for i in range(-1, -len(file_list) -1, -1):
        if _dupey_looking(file_list[i]):
            dupes.append(file_list[i])
        else:
            plains.append(file_list[i])

    plains.extend(dupes)
    return plains


def _dupey_looking(file: Path) -> bool:
    return re.search(r' ?\(\d+\)', file.stem)

def is_a_duplicate(file: Path) -> bool:
    """Checks whether potential duplicate file (format XXXXX(\\d+).XXX) is truly a dupe.

    First checks whether file without (\\d+) exists. If it does, checks whether they have the same file content."""
    possible_dupe = get_possible_dupe(file)
    if possible_dupe:
        possible_original = Path(file.parents[0], possible_dupe.group(1) + file.suffix)
        if possible_original.exists() and is_same_file(possible_original, file):
            return True
    return False

def is_same_file(file1: Path, file2: Path) -> bool:
    file1_hash: str = get_md5(file1)
    file2_hash: str = get_md5(file2)
    return file1_hash == file2_hash

def get_md5(file: Path) -> str:
    hash:str = None
    with open(file, 'rb') as f:
        hash = hashlib.md5(f.read()).digest()
    return base64.b64encode(hash).decode('utf-8')

def unzip(zip_file: Path, dir: str) -> Tuple[Path, List[Path]]:
    """Unzips file contents into specified directory. Adds year identifier to DRF files."""

    year = ''
    if zip_file.stem.endswith('k'):
        year = get_year_info(zip_file)
    corrected_zip_file = Path(zip_file.parents[0], zip_file.stem + year + zip_file.suffix)

    zipf = ZipFile(zip_file)
    zipped_files = zipf.namelist()
    unzipped_files: List[Path] = list()

    for file in zipped_files:
        unzipped_file = zipf.extract(file, path=dir)
        unzipped_file = Path(unzipped_file)
        correct_path = Path(dir, unzipped_file.stem + year + unzipped_file.suffix)
        if not correct_path.exists():
            unzipped_file.rename(correct_path)
        unzipped_files.append(correct_path)

    if not corrected_zip_file.exists():
        zip_file.rename(corrected_zip_file)

    return corrected_zip_file, unzipped_files

def upload(file: Path, bucket: str, destination_path: str=''):
    assert isinstance(file, Path)
    upload_path: str = ''
    if destination_path:
        upload_path += destination_path + '/'
    if is_in_s3(file=file, bucket=bucket, destination_path=upload_path):
        return False
    try:
        md5 = get_md5(file)
        with open(file, 'rb') as data:
            s3.put_object(Bucket=bucket, Key=upload_path + file.name, 
                    Body=data, ContentMD5=md5, Metadata={'md5chksum': md5})
        print(f'Uploaded {file}')
        return True

    except Exception as e:
        logging.error(f'Upload failed: {file}: {e}')
        return False

def s3_duplicate(file: Path, s3_filename: str,  bucket: str, destination_path: str=''):
    s3_path: str = ''
    if destination_path:
        s3_path += destination_path + '/'
    assert isinstance(s3_filename, str)
    assert isinstance(s3_path, str)
    try:
        response = s3.head_object(Bucket=bucket, Key=s3_path+s3_filename)
        if get_md5(file) == response['Metadata']['md5chksum']:
            return True
    except Exception as e:
        logging.error(e)

    return False

def is_in_s3(file: Path, bucket: str, destination_path: str='') -> bool:
    s3_path: str = ''
    if destination_path:
        s3_path += destination_path + '/'

    try:
        # print(f'Checking for {s3_path+file.name} in bucket {bucket}')
        response = s3.head_object(Bucket=bucket, Key=s3_path+file.name)
        if get_md5(file) == response['Metadata']['md5chksum']:
            return True
    except Exception as e:
        if '404' in str(e): # Ignore not found errors, which we expect if file not in bucket
            pass
        else:
            logging.error(e)
            logging.error(e.__traceback__)

    return False

def get_year_info(zip_file: Path) -> str:
    zipped_files: list = ZipFile(zip_file).namelist()
    csv_line: list = None
    with TemporaryDirectory() as temp_dir:
        ZipFile(zip_file).extract(zipped_files[0], path=temp_dir)
        with open(temp_dir + '/' + zipped_files[0], newline='') as file:
            csv_line = csv.reader(file).__next__()
    date_string = csv_line[1] # Date string is in 2nd position
    year = date_string[0:4] # Format will be YYYYMMDD
    return year

def already_in_bucket(s3_path: str, bucket: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=s3_path)
        return True
    except Exception as e:
        logging.error(e)
        return False

def get_possible_dupe(file: Path) -> re.Match:
    return re.search(r'(\w*) ?\(\d+\)', file.name)
        


