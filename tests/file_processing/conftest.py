import pytest
from zipfile import ZipFile
import tempfile
import random
from pathlib import Path
import os

@pytest.fixture()
def zipped_files():
    zipped_file_paths: list = list()
    zipped_file_descriptors: list = list()

    for _ in range(3):
        fd, fp = tempfile.mkstemp()
        zipped_file_descriptors.append(fd)
        zipped_file_paths.append(Path(fp))

    fd, zip_file_path = tempfile.mkstemp(suffix='.zip')
    zipped_file_descriptors.append(fd)

    with ZipFile(zip_file_path, mode='w') as zip_file:
        for item in zipped_file_paths:
            zip_file.write(item, arcname=item.name)

    yield Path(zip_file_path), [file.name for file in zipped_file_paths]

    # Cleanup
    for descriptor in zipped_file_descriptors:
        os.close(descriptor)
    os.remove(zip_file_path)
    for file in zipped_file_paths:
        os.remove(str(file))

@pytest.fixture()
def duplicate_in_zip():
    """Provide a zip file, a list of the contents of the zip file, and a file that will generate the same hash as one of the zipped files."""
    zipped_file_paths: list = list()
    zipped_file_descriptors: list = list()
    random_data = random.getrandbits(2048)

    for _ in range(3):
        fd, fp = tempfile.mkstemp()
        zipped_file_descriptors.append(fd)
        zipped_file_paths.append(Path(fp))
        with open(fp, 'w') as f:
            f.write(str(random_data))

    fd, zip_file_path = tempfile.mkstemp(suffix='.zip')
    zipped_file_descriptors.append(fd)

    with ZipFile(zip_file_path, mode='w') as zip_file:
        for item in zipped_file_paths:
            zip_file.write(item, arcname=item.name)

    yield Path(zip_file_path), Path(zipped_file_paths[0]), [file.name for file in zipped_file_paths]

    # Cleanup
    for descriptor in zipped_file_descriptors:
        os.close(descriptor)
    os.remove(zip_file_path)
    for file in zipped_file_paths:
        os.remove(str(file))


@pytest.fixture()
def duplicate_files():
    fd1, file_path1 = tempfile.mkstemp()
    fd2, file_path2 = tempfile.mkstemp()

    random_data = str(random.getrandbits(2048))

    with open(file_path1, 'w') as file:
        file.write(random_data)

    with open(file_path2, 'w') as file:
        file.write(random_data)

    yield Path(file_path1), Path(file_path2)

    os.close(fd1)
    os.close(fd2)
    os.remove(file_path1)
    os.remove(file_path2)

@pytest.fixture()
def nonduplicate_files():
    fd1, file_path1 = tempfile.mkstemp()
    fd2, file_path2 = tempfile.mkstemp()

    with open(file_path1, 'w') as file:
        file.write(str(random.getrandbits(2048)))

    with open(file_path2, 'w') as file:
        file.write(str(random.getrandbits(2048)))

    yield Path(file_path1), Path(file_path2)

    os.close(fd1)
    os.close(fd2)
    os.remove(file_path1)
    os.remove(file_path2)

@pytest.fixture()
def plain_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.1')

    yield Path(file_path)

    os.close(fd)
    os.remove(file_path)

@pytest.fixture()
def zip_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.zip')

    yield Path(file_path)

    os.close(fd)
    os.remove(file_path)

@pytest.fixture()
def nonpermitted_test_file():
    fd, file_path = tempfile.mkstemp(suffix='.exe')
    yield Path(file_path)
    os.close(fd)
    os.remove(file_path)
