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


INBOUND_DIR = '/data/python/horsenet_2/inbound_horse_data'
BUCKET = 'horsenet-data-files'
ZIP_FOLDER = 'zip-files'
EXTRACTED_FOLDER = 'extracted-files'

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


def is_a_duplicate(file: Path) -> bool:
    possible_dupe = re.search(r'(\w*) ?\(\d+\)', file.name)
    if possible_dupe:
        possible_original = Path(file.parents[0], possible_dupe.group(1) + file.suffix)
        if possible_original.exists() and is_same_file(possible_original, file):
            return True
    return False

def is_same_file(file1: Path, file2: Path) -> bool:
    file1_hash: str = None
    file2_hash: str = None
    with open(file1, 'rb') as file:
        file1_hash = hashlib.md5(file.read()).hexdigest()
    with open(file2, 'rb') as file:
        file2_hash = hashlib.md5(file.read()).hexdigest()

    return file1_hash == file2_hash


def get_file_list(dir: str, dupes_only=False) -> List[Path]:
    files: List[Path] = [Path(dir, file) for file in os.listdir(dir)]
    file_list = [file for file in file_list if file.is_file()]
    if dupes_only:
        file_list = [file for file in file_list if re.search(r' ?\(\d\)', file.stem)]
    return file_list

def unzip_add_year(zip_file: Path, dir: str, s3) -> None:
    zipf = ZipFile(zip_file)
    zipped_files = zipf.namelist()
    year = get_year_info(zip_file)

    for file in zipped_files:
        path = zipf.extract(file, path=dir)
        file_parts = file.split('.')
        fixed_file = file_parts[0] + year + '.' + file_parts[1]
        try:
            s3.upload_file(path, BUCKET, EXTRACTED_FOLDER + '/' + fixed_file)
        except:
            logging.error(f'Upload failed: {fixed_File}')

    fixed_zip_file = zip_file.stem + year + zip_file.suffix
    try:
        s3.upload_file(str(zip_file), BUCKET, ZIP_FOLDER + '/' + fixed_zip_file)
    except:
        logging.error(f'Upload failed: {zip_file}')

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

def upload(file_path: str, bucket: str, destination_path: str, s3):
    try:
        s3.upload_file(path, BUCKET, EXTRACTED_FOLDER + '/' + file)
    except Exception as e:
        logging.error(f'Upload failed: {file}: {e}')
    try:
        s3.upload_file(str(zip_file), BUCKET, ZIP_FOLDER + '/' + zip_file.name)
    except Exception as e:
        logging.error(f'Upload failed: {zip_file.name}: {e}')

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
