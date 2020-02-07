import os
import zipfile
import re
from pathlib import Path
import hashlib

INBOUND_DIR = '/data/python/horsenet_2/inbound_horse_data'
STORAGE_BUCKET = 'horsenet-data-files'
ZIP_FOLDER = 'zip-files'
EXTRACTED_FOLDER = 'extracted-files'

def process_inbound_dir() -> None:
    # First get rid of duplicates in INBOUND_DIR
    dupe_files: List[Path] = get_file_list(INBOUND_DIR, dupes_only=True)
    for file in dupe_files:
        if is_a_duplicate(file):
            file.unlink()

    # Next unzip the remaining files and upload them along with the original zip
    file_list: List[Path] = get_file_list(INBOUND_DIR)
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in file_list:
            
            assert False # FINISH THE THIS. PUT UNZIP PROCESS IN SEPARATE FUNCTION


def is_a_duplicate(file: Path) -> bool:
    possible_dupe = re.search(r'(\w*) ?\(\d\)', file.name)
    if possible_dupe:
        possible_original = Path(file.parents, possible_dupe.group(1))
        if possible_original.exists() and is_same_file(possible_original, possible_dupe):
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


