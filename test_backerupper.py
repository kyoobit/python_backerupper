import logging

from datetime import datetime
from pathlib import Path

import pytest

from backerupper import BackerUpper


def test_no_arguments():
    """Test what happens when no arguments are passed to the class instance"""
    backerupper = BackerUpper()
    with pytest.raises(ValueError):
        backerupper()


def test_source_does_not_exist(tmp_path):
    """Test what happens when a source path does not exist"""
    backerupper = BackerUpper()
    with pytest.raises(FileNotFoundError):
        backerupper(source="test-does-not-exist")


def test_file_using_defaults(tmp_path, caplog):
    """Test what happens when defaults are used with a file"""
    # https://docs.pytest.org/en/stable/how-to/logging.html
    caplog.set_level(logging.DEBUG)
    backerupper = BackerUpper()

    # Use a temporary path provided by pytest builtin fixtures
    # https://docs.pytest.org/en/stable/builtin.html
    print(f"tmp_path: {tmp_path}")

    # Create a test file in the tmp_path
    with Path(f"{tmp_path}/test.txt").open(mode="w") as f:
        f.write(f"Created at: {datetime.now()}\n")

    # Iterate to assert the retention count is enforced
    for i in range(1, 12):
        # Create a backup of the test file
        backerupper(source=f"{tmp_path}/test.txt")
        # The tmp_path should not exceed 10 archives
        total = i
        if i > 10:
            total = 10
        archives = len(list(Path(tmp_path).glob("test.txt.*.tgz")))
        print(f"archives count: {archives}")
        assert archives == total


def test_file_using_sequential(tmp_path, caplog):
    """Test what happens when sequential is used with a file"""
    # https://docs.pytest.org/en/stable/how-to/logging.html
    caplog.set_level(logging.DEBUG)
    backerupper = BackerUpper()

    # Use a temporary path provided by pytest builtin fixtures
    # https://docs.pytest.org/en/stable/builtin.html
    print(f"tmp_path: {tmp_path}")

    # Create a test file in the tmp_path
    with Path(f"{tmp_path}/test.txt").open(mode="w") as f:
        f.write(f"Created at: {datetime.now()}\n")

    # Iterate to assert the retention count is enforced
    for i in range(1, 12):
        # Create a backup of the test file
        backerupper(source=f"{tmp_path}/test.txt", sequential=True)
        # The tmp_path should not exceed 10 archives (original + archives)
        total = i
        if i > 10:
            total = 10
        archives = len(list(Path(tmp_path).glob("test.txt.*.tgz")))
        print(f"archives count: {archives}")
        assert archives == total

    # Assert the end state of the archives is what is expected
    items_in_tmp_path = []
    print(f"Iteration {i} - items in tmp_path:")
    for item in Path(tmp_path).iterdir():
        print(item.name)
        items_in_tmp_path.append(item.name)

    assert sorted(items_in_tmp_path) == [
        "test.txt",
        "test.txt.1.tgz",
        "test.txt.10.tgz",
        "test.txt.2.tgz",
        "test.txt.3.tgz",
        "test.txt.4.tgz",
        "test.txt.5.tgz",
        "test.txt.6.tgz",
        "test.txt.7.tgz",
        "test.txt.8.tgz",
        "test.txt.9.tgz",
    ]


def test_directory_using_defaults(tmp_path, caplog):
    """Test what happens when defaults are used with a directory"""
    # https://docs.pytest.org/en/stable/how-to/logging.html
    caplog.set_level(logging.DEBUG)
    backerupper = BackerUpper()

    # Use a temporary path provided by pytest builtin fixtures
    # https://docs.pytest.org/en/stable/builtin.html
    print(f"tmp_path: {tmp_path}")

    # Create a test directory in the tmp_path
    Path(f"{tmp_path}/test").mkdir()

    # Create a test directory in the tmp_path/test directory
    with Path(f"{tmp_path}/test/test.txt").open(mode="w") as f:
        f.write(f"Created at: {datetime.now()}\n")

    # Iterate to assert the retention count is enforced
    for i in range(1, 12):
        # Create a backup of the test directory
        backerupper(source=f"{tmp_path}/test")
        # The tmp_path should not exceed 10 archives
        total = i
        if i > 10:
            total = 10
        archives = len(list(Path(tmp_path).glob("test.*.tgz")))
        print(f"archives count: {archives}")
        assert archives == total


def test_directory_using_sequential(tmp_path, caplog):
    """Test what happens when defaults are used with a directory"""
    # https://docs.pytest.org/en/stable/how-to/logging.html
    caplog.set_level(logging.DEBUG)
    backerupper = BackerUpper()

    # Use a temporary path provided by pytest builtin fixtures
    # https://docs.pytest.org/en/stable/builtin.html
    print(f"tmp_path: {tmp_path}")

    # Create a test directory in the tmp_path
    Path(f"{tmp_path}/test").mkdir()

    # Create a test directory in the tmp_path/test directory
    with Path(f"{tmp_path}/test/test.txt").open(mode="w") as f:
        f.write(f"Created at: {datetime.now()}\n")

    # Iterate to assert the retention count is enforced
    for i in range(1, 12):
        # Create a backup of the test directory
        backerupper(source=f"{tmp_path}/test", sequential=True)
        # The tmp_path should not exceed 10 archives
        total = i
        if i > 10:
            total = 10
        archives = len(list(Path(tmp_path).glob("test.*.tgz")))
        print(f"archives count: {archives}")
        assert archives == total

    # Assert the end state of the archives is what is expected
    items_in_tmp_path = []
    print(f"Iteration {i} - items in tmp_path:")
    for item in Path(tmp_path).iterdir():
        print(item.name)
        items_in_tmp_path.append(item.name)

    assert sorted(items_in_tmp_path) == [
        "test",
        "test.1.tgz",
        "test.10.tgz",
        "test.2.tgz",
        "test.3.tgz",
        "test.4.tgz",
        "test.5.tgz",
        "test.6.tgz",
        "test.7.tgz",
        "test.8.tgz",
        "test.9.tgz",
    ]
