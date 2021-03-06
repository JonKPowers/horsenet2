import os
import hashlib
from pathlib import Path
from webapp.db import get_db
from webapp.app_settings import ALLOWED_UPLOAD_EXTENSIONS
from webapp import zip_functions

from flask import current_app, flash, g
from werkzeug.utils import secure_filename

from couchbase.exceptions import KeyExistsError

def add_file(upload_file, db=None):
    file_name = secure_filename(upload_file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
    if check_for_duplicate(file_path):
        flash('Duplicate file found')
    else:
        upload_file.save(file_path)
        flash('File saved to upload folder')
        try:
            add_db_record(file_path, db)
            flash('DB file record added')
        except KeyExistsError:
            flash('Duplicate DB file record found')

def check_for_duplicate(file_path):
    return os.path.exists(file_path)

def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOAD_EXTENSIONS

def add_db_record(file_path: str, db=None) -> None:
    if db is None:
        db = get_db()
    file = Path(file_path)
    record = get_formatted_record(file)
    db.insert(secure_filename(file.name), record)

def get_formatted_record(file: Path) -> dict:
    is_zip = file.suffix == '.zip'
    record = {
            'doc_type': 'file',
            'zip_file': is_zip,
            'file_name': file.name,
            'file_path': str(file),
            'file_hash': get_hash(file),
            'preprocessed': False,
            'processed': False,
            }
    if is_zip:
        record['unzipped'] = False
        record['zip_contents'] = zip_functions.get_file_list(file)
    return record

def get_hash(file: Path) -> str:
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(file, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()
