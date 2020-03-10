"""
    Conftest.py a configuration file for pytest
"""
import os

import pytest
from gdcdictionary import ROOT_DIR, GDCDictionary
from tests.utils import load_yaml


@pytest.fixture(scope="session")
def dictionary():
    return GDCDictionary()


@pytest.fixture(scope="session")
def definitions(dictionary):
    # TODO why not pkg_resources
    return load_yaml(os.path.join(ROOT_DIR, 'schemas', '_definitions.yaml'))


@pytest.fixture(scope="session")
def schema(dictionary):
    return dictionary.schema
