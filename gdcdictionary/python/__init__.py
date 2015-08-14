import yaml
import os
import glob

MOD_DIR = os.path.abspath(os.path.dirname(__file__))


class GDCDictionary(object):

    def __init__(self, lazy=False):
        self.root_dir = os.path.join(os.path.dirname(MOD_DIR), 'schemas')
        self.metaschema_path = 'metaschema.yaml'
        self.definitions_path = 'definitions.yaml'
        self.exclude = [self.metaschema_path, self.definitions_path]
        self.schema = dict()
        if not lazy:
            self.load()

    def load(self):
        self.metaschema = self.load_yaml_schema(self.metaschema_path)
        self.definitions = self.load_yaml_schema(self.definitions_path)
        self.load_root_dir()

    def load_root_dir(self):
        os.chdir(self.root_dir)
        for name in glob.glob("*.yaml"):
            if name not in self.exclude:
                schema = self.load_yaml_schema(name)
                self.schema[schema['id']] = schema

    def load_yaml_schema(self, name):
        full_path = os.path.join(self.root_dir, name)
        with open(full_path, 'r') as f:
            return yaml.load(f)
