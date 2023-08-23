"""This is an example of json schema for the GDC using schemas defined
in local yaml files (see gdcdictionary/examples).

This test class is making sure the example jsons comply with the schema.

Note this is NOT testing that the schema is sane. Just that we adhere
to it

"""

from tests.utils import DATA_DIR
from jsonschema import validate, ValidationError

import json
import glob
import os
import pytest


def get_all_paths(subdir):
    yield from sorted(glob.glob(os.path.join(DATA_DIR, subdir, '*.json')))


@pytest.mark.parametrize("path", get_all_paths("valid"))
def test_valid_examples(path, schema):
    with open(path) as f:
        doc = json.load(f)
        validate(doc, schema[doc["type"]])


@pytest.mark.parametrize("path", get_all_paths("invalid"))
def test_invalid_examples(path, schema):
    with open(path) as f:
        doc = json.load(f)
        with pytest.raises(ValidationError):
            validate(doc, schema[doc["type"]])
