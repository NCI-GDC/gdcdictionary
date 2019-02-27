"""This is an example of json schema for the GDC using schemas defined
in local yaml files (see gdcdictionary/examples).

This test class is making sure the example jsons comply with the schema.

Note this is NOT testing that the schema is sane. Just that we adhere
to it

"""
from __future__ import print_function


from jsonschema import validate, ValidationError
import glob
import os
import json
from gdcdictionary import ROOT_DIR

from utils import validate_entity, BaseTest

DATA_DIR = os.path.join(ROOT_DIR, 'examples')

class JsonValidationTests(BaseTest):

    def test_valid_files(self):
        for path in glob.glob(os.path.join(DATA_DIR, 'valid', '*.json')):
            print("Validating {}".format(path))
            doc = json.load(open(path, 'r'))
            print(doc)
            if type(doc) == dict:
                self.add_system_props(doc)
                validate_entity(doc, self.dictionary.schema)
            elif type(doc) == list:
                for entity in doc:
                    self.add_system_props(entity)
                    validate_entity(entity, self.dictionary.schema)
            else:
                raise Exception("Invalid json")

    def test_invalid_files(self):
        for path in glob.glob(os.path.join(DATA_DIR, 'invalid', '*.json')):
            print("Validating {}".format(path))
            doc = json.load(open(path, 'r'))
            if type(doc) == dict:
                self.add_system_props(doc)
                with self.assertRaises(ValidationError):
                    validate_entity(doc, self.dictionary.schema)
            elif type(doc) == list:
                for entity in doc:
                    self.add_system_props(entity)
                    with self.assertRaises(ValidationError):
                        validate_entity(entity, self.dictionary.schema)
            else:
                raise Exception("Invalid json")

    def add_system_props(self, doc):
        schema = self.dictionary.schema[doc['type']]
        for key in schema['systemProperties']:
            use_def_default = (
                '$ref' in schema['properties'][key] and
                key in self.definitions and
                'default' in self.definitions[key]
            )
            if use_def_default:
                doc[key] = self.definitions[key]['default']
