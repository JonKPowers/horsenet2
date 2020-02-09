import pytest
from zipfile import ZipFile
import tempfile
import random
from pathlib import Path
import os
from typing import List

@pytest.fixture()
def horse_duplicates_same_contents():
    zipped_file_descriptors: list = list()
    zipped_file_paths: List[Path] = list()
    random_data = str(random.getrandbits(2048))

    with tempfile.TemporaryDirectory() as temp_dir:
        fd_1, file_1 = tempfile.mkstemp(suffix='.zip', dir=temp_dir)
        file_1 = Path(file_1)
        zipped_file_descriptors.append(fd_1)
        zipped_file_paths.append(file_1)

        file_2 = Path(temp_dir, file_1.stem + '(' + str(random.randrange(2000)) + ')' + file_1.suffix)
        zipped_file_paths.append(file_2)

        for file in zipped_file_paths:
            with open(file, 'w') as f:
                f.write(random_data)
        yield file_1, file_2

    pass

@pytest.fixture()
def horse_looks_like_dupe():
    fd, fp = tempfile.mkstemp(suffix= '(' + str(random.randrange(2000)) + ').zip')
    yield Path(fp)

    os.close(fd)
    os.remove(fp)

@pytest.fixture()
def horse_looks_dupe_diff_contents():
    zipped_file_descriptors: list = list()
    zipped_file_paths: List[Path] = list()

    with tempfile.TemporaryDirectory() as temp_dir:
        fd_1, file_1 = tempfile.mkstemp(suffix='.zip', dir=temp_dir)
        file_1 = Path(file_1)
        zipped_file_descriptors.append(fd_1)
        zipped_file_paths.append(file_1)

        file_2 = Path(temp_dir, file_1.stem + '(' + str(random.randrange(2000)) + ')' + file_1.suffix)
        zipped_file_paths.append(file_2)

        for file in zipped_file_paths:
            with open(file, 'w') as f:
                f.write(str(random.getrandbits(2048)))
        yield file_1, file_2

    pass

@pytest.fixture()
def zipped_needs_years_file():
    year: str = str(random.randrange(2000, 2040))
    file_contents: str = f'"Test","{year}1234","Test","Test","Test",\n' \
                         f'"Test","{year}5678","Test","Test","Test",'
    temp_descriptors: list = list()
    temp_paths: List[Path] = list()

    # Create and set up the zip file
    z_fd, z_fp = tempfile.mkstemp(suffix='123k.zip')
    zip_file = Path(z_fp)
    temp_descriptors.append(z_fd)
    temp_paths.append(zip_file)

    # Create and set up the zipped files (should be just one but want to be able to handle multiple)
    for _ in range(random.randrange(1, 10)):
        fd, fp = tempfile.mkstemp(suffix='123.DRF')
        temp_descriptors.append(fd)
        temp_paths.append(Path(fp))
        # Drop in dummy file contents
        with open(fp, 'w') as file:
            file.write(file_contents)

    # Zip up the files and return the zip, a list of contents, and the target year
    with ZipFile(zip_file, mode='w') as z:
        for item in temp_paths[1:]:
            z.write(item, arcname=item.name)

    yield zip_file, temp_paths[1:], year

    # Cleanup
    for fd in temp_descriptors:
        os.close(fd)

    for file in temp_paths:
        try:
            file.unlink()
        except:
            pass

    
@pytest.fixture()
def zipped_files():
    zipped_file_paths: List[Path] = list()
    zipped_file_descriptors: list = list()
    num_files = random.randrange(1, 200)
    print(num_files)

    for _ in range(num_files):
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

    with open(file_path, 'w') as file:
        file.write(str(random.getrandbits(128)))

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
