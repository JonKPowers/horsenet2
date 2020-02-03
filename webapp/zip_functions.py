from zipfile import ZipFile
from pathlib import Path
from tempfile import TemporaryDirectory

from webapp.app_settings import UPLOAD_FOLDER
from webapp import add_files 

from webapp.db import get_db

def web_unzip(doc_id: str) -> None:
    # For each file in the zip:
    # (1) Check if it's already in upload_folder
    # (2) If it's in the upload folder, check if it's the same file
    #   (2.1) If it's the same file [________________]
    #   (2.2) If it's not the same file get a unique name for the file
    # (3) Unzip the file into UPLOAD_FOLDER
    # (4) Make record for the file
    # (5) Add record to DB
    # (6) Mark zip file as extracted.
    flash_messages:list = list()
    db = get_db()
    record: dict = db.get(doc_id)
    zip_file: Path = Path(record['file_path'])
    for file in get_file_list(zip_file):
        target_file = Path(UPLOAD_FOLDER, file)
        if target_file.exists():
            assert False
            # FINISH THIS
            pass


def get_file_list(zip_file: Path) -> list:
    file_list: list = None
    with ZipFile(zip_file) as zip:
        file_list = zip.namelist()
    return file_list

def unzip_files(zip_file: Path) -> None:
    """Unzips entire contents of zip_file to the upload directory"""
    with ZipFile(zip_file) as zip:
        zip.extractall(path=UPLOAD_FOLDER)

def extract_file(zip_file: Path, file_to_get: str) -> None:
    """Extracts single file from zip_file to the upload directory"""
    with ZipFile(zip_file) as zip:
        zip.extract(file_to_get, path=UPLOAD_FOLDER)

def same_file(file1: Path, file2: Path) -> bool:
    return add_files.get_hash(file1) == add_files.get_hash(file2)

def extract_and_check_if_same(zip_file: Path, target_file: str, existing_file: Path) -> bool:
    """Extracts target_file into a temp directory and checks to see if hash matches existing_file"""
    files_are_same: bool = None
    with TemporaryDirectory() as temp_dir:
        ZipFile(zip_file).extract(target_file, path=temp_dir)
        files_are_same = same_file(Path(temp_dir, target_file), existing_file)
    return files_are_same

def file_already_in_uploads(file: Path):
    return Path(UPLOAD_FOLDER, file.name).exists()

def get_unique_filename(file: Path):
    file_name = file.name
    i: int = 0
    while(Path(UPLOAD_FOLDER, file_name).exists()):
        file_name = file.stem + "_" + str(i) + file.suffix
        i += 1
    return Path(UPLOAD_FOLDER, file_name)
