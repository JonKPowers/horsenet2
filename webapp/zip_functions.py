from zipfile import ZipFile
from pathlib import Path

from webapp.app_settings import UPLOAD_FOLDER
from webapp import add_files 

def get_file_list(zip_file: Path) -> list:
    file_list: list = None
    with ZipFile(zip_file) as zip:
        file_list = zip.namelist()
    return file_list

def unzip_file(zip_file: Path) -> None:
    """Unzips zip_file to the upload directory"""
    with ZipFile(zip_file) as zip:
        zip.extractall(path=UPLOAD_FOLDER)

def same_file(file1: Path, file2: Path) -> bool:
    return add_files.get_hash(file1) == add_files.get_hash(file2)

def file_already_in_uploads(file: Path):
    return Path(UPLOAD_FOLDER, file.name).exists()

def get_unique_filename(file: Path):
    file_name = file.name
    i: int = 0
    while(Path(UPLOAD_FOLDER, file_name).exists()):
        file_name = file.stem + "_" + str(i) + file.suffix
        i += 1
    return Path(UPLOAD_FOLDER, file_name)
