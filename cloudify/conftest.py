import pytest
from zipfile import ZipFile
import tempfile
import random
from pathlib import Path
import os
from typing import List, Tuple
import hashlib 

FILE_CONTENTS: str = f'"Test","20201234","Test","Test","Test",\n' \
                    f'"Test","20205678","Test","Test","Test",'
class FileCounter:
    def __init__(self):
        self._count = 0

    def use(self) -> int:
        self._count += 1
        return self._count - 1

    def get(self) -> int:
        return self._count

    def rewind(self, num: int) -> bool:
        self._count -= num
        return True

def make_random_files(num_files: int) -> Tuple[list, List[Path]]:
    file_descriptors: list = list()
    file_list: List[Path] = list()

    for _ in range(num_files):
        fd, fp = tempfile.mkstemp(suffix='.'+str(random.randint(1, 6)))
        file_descriptors.append(fd)
        file_list.append(Path(fp))
        with open(fp, 'w') as f:
            f.write(FILE_CONTENTS)

    return file_descriptors, file_list

def add_to_zip(zip_file: Path, file_to_add:Path):
    # print(f'Zipfile {zip_file} added {file_to_add}')
    with ZipFile(zip_file, mode='a') as zf:
        zf.write(file_to_add, arcname=file_to_add.name)

def make_a_zip(zip_file: Path, files_to_zip: List[Path], num_to_zip: int, counter: FileCounter):
    for _ in range(num_to_zip):
        file_to_add = files_to_zip[counter.use()]
        add_to_zip(zip_file, file_to_add)

@pytest.fixture
def folder_of_files_with_nondupes():
    num_files = random.randint(10, 20)
    file_descriptors: list = None
    zip_files: List[Path] = list()
    zipped_files: List[Path] = None
    dupe_files: List[Path] = list()

    file_descriptors, zipped_files = make_random_files(num_files)

    # Zip up the files, 1-6 files per zip
    with tempfile.TemporaryDirectory() as temp_dir:
        file_counter = FileCounter()
        assert num_files == len(zipped_files)
        while file_counter.get() < num_files:
            finish_up = num_files - file_counter.get() <= 7
            num_to_zip = num_files - file_counter.get() - 1 if finish_up else random.randint(1, 6)

            # Base zip file
            if num_to_zip != 0:
                fd, fp = tempfile.mkstemp(suffix='a.zip', dir=temp_dir)
                file_descriptors.append(fd)
                file_path = Path(fp)
                zip_files.append(file_path)

            make_a_zip(file_path, zipped_files, num_to_zip, file_counter)

            # Make fake dupe if make_dupes
            make_dupes = random.choice([True, False])
            if make_dupes:
                fd, fp = tempfile.mkstemp(suffix='a(' + str(random.randint(1,6)) + ').zip', dir=temp_dir)
                file_descriptors.append(fd)
                dupe_files.append(Path(fp))

                file_to_add = zipped_files[file_counter.use()]
                add_to_zip(dupe_files[-1], file_to_add)

        assert file_counter.get() == num_files

        yield temp_dir, zip_files, zipped_files, dupe_files

    for fd in file_descriptors:
        os.close(fd)

    for fp in zipped_files:
        try:
            fp.unlink()
        except:
            pass

@pytest.fixture()
def folder_of_files_with_dupes():
    num_files = random.randint(10, 20)
    file_descriptors: list = list()
    zip_files: List[Path] = list()
    zipped_files: List[Path] = list()
    dupe_files: List[Path] = list()
    make_dupes = True

    file_descriptors, zipped_files = make_random_files(num_files)

    # Zip up the files, 1-6 files per zip
    with tempfile.TemporaryDirectory() as temp_dir:
        file_counter = FileCounter()
        assert num_files == len(zipped_files)
        while file_counter.get() < num_files:
            finish_up = num_files - file_counter.get() <= 6
            num_to_zip = num_files - file_counter.get() if finish_up else random.randint(1, 6)

            # Base zip file
            fd, fp = tempfile.mkstemp(suffix='a.zip', dir=temp_dir)
            file_descriptors.append(fd)
            file_path = Path(fp)
            zip_files.append(file_path)

            make_a_zip(file_path, zipped_files, num_to_zip, file_counter)

            # Duplicate zip file
            num: int = None
            dup_zip: Path = None
            if make_dupes:
                num = random.randint(1, 6)
                dup_zip = Path(temp_dir, file_path.stem + f'({num})' + file_path.suffix)
                dupe_files.append(dup_zip)

                file_counter.rewind(num_to_zip) # Rewind the counter for the dupe zip
                make_a_zip(dup_zip, zipped_files, num_to_zip, file_counter)

                assert hashlib.md5(open(file_path, 'rb').read()).digest() == hashlib.md5(open(dup_zip, 'rb').read()).digest()

            make_dupes = random.choice([True, False])

        assert file_counter.get() == num_files
        assert len(dupe_files) != 0
        print(f'Nondupes: {dupe_files}')

        yield temp_dir, zip_files, zipped_files, dupe_files

    for fd in file_descriptors:
        os.close(fd)

    for fp in zipped_files:
        try:
            fp.unlink()
        except:
            pass

@pytest.fixture()
def folder_of_files():
    num_files = random.randint(10, 20)
    file_descriptors: list = list()
    zip_files: List[Path] = list()
    zipped_files: List[Path] = list()

    file_descriptors, zipped_files = make_random_files(num_files)

    # Zip up the files, 1-6 files per zip
    with tempfile.TemporaryDirectory() as temp_dir:
        file_counter = 0
        assert num_files == len(zipped_files)
        while file_counter < num_files:
            finish_up = num_files - file_counter <= 6
            num_to_zip = num_files - file_counter if finish_up else random.randint(1, 6)
            fd, fp = tempfile.mkstemp(suffix='a.zip', dir=temp_dir)
            file_descriptors.append(fd)
            file_path = Path(fp)
            zip_files.append(file_path)
            for _ in range(num_to_zip):
                file_to_add = zipped_files[file_counter]
                file_counter += 1
                add_to_zip(file_path, file_to_add)
        assert file_counter == num_files

        yield temp_dir, zip_files, zipped_files

    for fd in file_descriptors:
        os.close(fd)

    for fp in zipped_files:
        try:
            fp.unlink()
        except:
            pass


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

@pytest.fixture()
def same_name_diff_contents():
    file_descriptors: list = list()
    files: List[Path] = list()

    fd, fp = tempfile.mkstemp()
    file_1 = Path(fp)
    file_descriptors.append(fd)
    files.append(file_1)

    with tempfile.TemporaryDirectory() as temp_dir:
        file_2 = Path(temp_dir, file_1.name)
        files.append(file_2)
        for file in files:
            with open(file, 'w') as f:
                f.write(str(random.getrandbits(512)))
        yield file_1, file_2

    for descriptor in file_descriptors:
        os.close(descriptor)
    for file in files:
        try:
            file.unlink()
        except:
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
    for item in temp_paths[1:]:
        add_to_zip(zip_file, item)

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
    num_files = random.randrange(1, 20)
    print(num_files)

    for _ in range(num_files):
        fd, fp = tempfile.mkstemp()
        zipped_file_descriptors.append(fd)
        zipped_file_paths.append(Path(fp))

    fd, zip_file_path = tempfile.mkstemp(suffix='a.zip')
    zipped_file_descriptors.append(fd)

    for item in zipped_file_paths:
        add_to_zip(zip_file_path, item)

    yield Path(zip_file_path), zipped_file_paths

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
