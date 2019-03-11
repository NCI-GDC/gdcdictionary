"""This is an example of json schema for the GDC using schemas defined
in local yaml files (see gdcdictionary/examples).

This test class is making sure the example jsons comply with the schema.

Note this is NOT testing that the schema is sane. Just that we adhere
to it

"""

from utils import DATA_DIR
from jsonschema import validate, ValidationError

import json
import glob
import os
import pytest


def get_all_docs(subdir):
    for path in sorted(glob.glob(os.path.join(DATA_DIR, subdir, '*.json'))):
        with open(path, 'r') as f:
            doc = json.load(f)
            if isinstance(doc, dict):
                yield doc
            elif isinstance(doc, list):
                if len(doc) != 1:
                    assert False, "Mismatch between files and documents in {}".format(f.name)
                for entity in doc:
                    yield entity
            else:
                assert False, "Error collecting file: {}".format(f)

def get_all_files(subdir):
    file_names = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, subdir, '*.json'))):
        with open(path, 'r') as f:
            file_names.append(f.name)
    return file_names


@pytest.mark.parametrize("doc", get_all_docs("valid"), ids=get_all_files("valid"))
def test_valid_examples(doc, schema):
    validate(doc, schema[doc["type"]])

@pytest.mark.parametrize("doc", get_all_docs("invalid"), ids=get_all_files("invalid"))
def test_invalid_examples(doc, schema):
    with pytest.raises(ValidationError):
        validate(doc, schema[doc["type"]])
