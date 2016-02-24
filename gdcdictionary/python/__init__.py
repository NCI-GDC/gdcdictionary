from copy import deepcopy
from collections import namedtuple
from jsonschema import RefResolver

import glob
import logging
import os
import yaml

MOD_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


class GDCDictionary(object):

    _metaschema_path = 'metaschema.yaml'
    _definitions_paths = [
        '_definitions.yaml',
        '_terms.yaml',
    ]

    logger = logging.getLogger("GDCDictionary")

    def __init__(self, lazy=False, root_dir=None, definitions_paths=None,
                 metaschema_path=None):
        """Creates a new dictionary instance.

        :param root_dir: The directory to find schemas
        :param metaschema_path: The metaschema to validate schemas with
        :param definitions_paths: Paths to resolve $ref to
        :param lazy: If true, wait to load dictionary

        """

        self.root_dir = (root_dir or os.path.join(MOD_DIR, 'schemas'))
        self.metaschema_path = metaschema_path or self._metaschema_path
        self.definitions_paths = definitions_paths or self._definitions_paths
        self.exclude = [self.metaschema_path] + self.definitions_paths
        self.schema = dict()
        self.resolvers = dict()
        if not lazy:
            self.load()

    def load(self):
        """Load and reslove all schemas"""

        self.metaschema = self.load_yaml_schema(self.metaschema_path)
        self.resolvers = self.get_resolvers()
        self.load_root_dir()
        self.schema = {
            key: self.resolve_schema(schema, deepcopy(schema))
            for key, schema in self.schema.iteritems()
        }

    def resolve_reference(self, value, root):
        """Resolves a reference.

        :param value: The actual reference, e.g. ``_yaml.yaml#/def``
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: JSON Schema pointed to by :param:`value`

        """
        base, ref = value.split('#', 1)

        if base:
            resolver, new_root = self.resolvers[base]
            referrer, resolution = resolver.resolve(value)
            self.resolve_schema(resolution, new_root)
        else:
            resolver = RefResolver('#', root)
            referrer, resolution = resolver.resolve(value)

        return resolution

    def resolve_schema(self, obj, root):
        """REcursively resolves all references in a schema against
        ``self.resolvers``.

        :param obj: The object to recursively resolve.
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: A denormalized/resolved version of :param:`obj`.

        """

        if isinstance(obj, dict):
            for key in obj.keys():
                if key == '$ref':
                    val = obj.pop(key)
                    obj.update(self.resolve_reference(val, root))
            return {k: self.resolve_schema(v, root) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.resolve_schema(item, root) for item in obj]
        else:
            return obj

    def get_resolvers(self):
        resolvers = {}
        for path in self.definitions_paths:
            source = self.load_yaml_schema(path)
            resolver = RefResolver('{}#'.format(path), source)
            resolvers[path] = ResolverPair(resolver, source)
        return resolvers

    def load_root_dir(self):
        cdir = os.getcwd()
        os.chdir(self.root_dir)
        for name in glob.glob("*.yaml"):
            if name not in self.exclude:
                schema = self.load_yaml_schema(name)
                self.schema[schema['id']] = schema
        os.chdir(cdir)

    def load_yaml_schema(self, name):
        full_path = os.path.join(self.root_dir, name)
        with open(full_path, 'r') as f:
            return yaml.load(f)


gdcdictionary = GDCDictionary()
