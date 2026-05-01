"""
Define fixtures.

Author: Nikolay Lysenko
"""


from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest


@pytest.fixture()
def path_to_tmp_file() -> str:
    """Get path to empty temporary file."""
    with NamedTemporaryFile() as tmp_file:
        yield tmp_file.name


@pytest.fixture()
def path_to_tmp_dir() -> str:
    """Get path to empty temporary file."""
    with TemporaryDirectory() as tmp_dir:
        yield tmp_dir
