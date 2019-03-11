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
    for path in glob.glob(os.path.join(DATA_DIR, subdir, '*.json')):
        with open(path, 'r') as f:
            doc = json.load(f)
            if isinstance(doc, dict):
                yield doc
            elif isinstance(doc, list):
                for entity in doc:
                    yield entity
            else:
                assert False, "Error collecting file: {}".format(f)


@pytest.mark.parametrize("doc", get_all_docs("valid"))
def test_valid_examples(doc, schema):
    validate(doc,schema)

@pytest.mark.parametrize("doc", get_all_docs("invalid"))
def test_invalid_examples(doc, schema):
    with pytest.raises(ValidationError):
        validate(doc, schema)

#class JsonValidationTests(BaseTest):
#
#    def test_valid_files(self):
#        for path in glob.glob(os.path.join(DATA_DIR, 'valid', '*.json')):
#            if type(doc) == dict:
#                self.add_system_props(doc)
#            elif type(doc) == list:
#                for entity in doc:
#                    self.add_system_props(entity)
#                    validate_entity(entity, self.dictionary.schema)
#            else:
#                raise Exception("Invalid json")
#
#    def test_invalid_files(self):
#        for path in glob.glob(os.path.join(DATA_DIR, 'invalid', '*.json')):
#            print "Validating {}".format(path)
#            doc = json.load(open(path, 'r'))
#            if type(doc) == dict:
#                self.add_system_props(doc)
#                with self.assertRaises(ValidationError):
#                    validate_entity(doc, self.dictionary.schema)
#            elif type(doc) == list:
#                for entity in doc:
#                    self.add_system_props(entity)
#                    with self.assertRaises(ValidationError):
#                        validate_entity(entity, self.dictionary.schema)
#            else:
#                raise Exception("Invalid json")
#
#    def add_system_props(self, doc):
#        schema = self.dictionary.schema[doc['type']]
#        for key in schema['systemProperties']:
#            use_def_default = (
#                '$ref' in schema['properties'][key] and
#                key in self.definitions and
#                'default' in self.definitions[key]
#            )
#            if use_def_default:
#                doc[key] = self.definitions[key]['default']
#
