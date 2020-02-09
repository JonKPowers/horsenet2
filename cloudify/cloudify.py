import os
from zipfile import ZipFile
import re
from pathlib import Path
import hashlib
import logging
import boto3
from typing import List
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
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in file_list:
            
            assert False # FINISH THE THIS. PUT UNZIP PROCESS IN SEPARATE FUNCTION

def get_file_list(dir: str, dupes_only=False) -> List[Path]:
    def return_file(file: Path) -> bool:
        if not file.is_file():
            return False
        elif dupes_only and re.search(r' ?\(\d\)', file.stem) is None:
            return False
        return True

    files: List[Path] = [Path(dir, file) for file in os.listdir(dir)]
    return [file for file in file_list if return_file(file)]

def is_a_duplicate(file: Path) -> bool:
    """Checks whether potential duplicate file (format XXXXX(\\d+).XXX) is truly a dupe.

    First checks whether file without (\\d+) exists. If it does, checks whether they have the same file content."""
    possible_dupe = re.search(r'(\w*) ?\(\d+\)', file.name)
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

def unzip(zip_file: Path, dir: str) -> List[Path]:
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

    return unzipped_files

def upload(file: Path, bucket: str, destination_path: str=''):
    upload_path: str = ''
    if destination_path:
        upload_path += destination_path + '/'
    try:
        md5 = get_md5(file)
        with open(file, 'rb') as data:
            s3.put_object(Bucket=bucket, Key=upload_path + file.name, 
                    Body=data, ContentMD5=md5, Metadata={'md5chksum': md5})
    except Exception as e:
        logging.error(f'Upload failed: {file}: {e}')

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
