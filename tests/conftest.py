"""
    Conftest.py a configuration file for pytest
"""

import pytest

from gdcdictionary import GDCDictionary
from tests.utils import load_yaml


@pytest.fixture(scope="session")
def dictionary():
    return GDCDictionary()


@pytest.fixture(scope="session")
def definitions(dictionary):
    return load_yaml("_definitions.yaml")


@pytest.fixture(scope="session")
def schema(dictionary):
    return dictionary.schema
