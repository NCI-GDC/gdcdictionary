from copy import deepcopy
from collections import namedtuple
from contextlib import contextmanager
from jsonschema import RefResolver

import glob
import logging
import os
import yaml

MOD_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


@contextmanager
def visit_directory(path):
    """Perform contained actions with current working directory at
    :param:``path``.  Always return to previous directory when done.

    """

    cdir = os.getcwd()
    try:
        os.chdir(path)
        yield os.getcwd()
    finally:
        os.chdir(cdir)


def load_yaml(name):
    """Return contents of yaml file as dict"""
    with open(name, 'r') as f:
        return yaml.safe_load(f)


def load_schemas_from_dir(directory):
    """Returns all yamls and resolvers of those yamls from dir"""

    schemas, resolvers = {}, {}

    with visit_directory(directory):
        for path in glob.glob("*.yaml"):
            schema = load_yaml(path)
            schemas[path] = schema
            resolver = RefResolver('{}#'.format(path), schema)
            resolvers[path] = ResolverPair(resolver, schema)

    return schemas, resolvers


class GDCDictionary(object):

    _metaschema_path = 'metaschema.yaml'
    _definitions_paths = [
        '_definitions.yaml',
        '_terms.yaml',
    ]
    settings_path = '_settings.yaml'

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
        self.exclude = (
            [self.metaschema_path] + self.definitions_paths
            + [self.settings_path])
        self.schema = dict()
        self.resolvers = dict()
        if not lazy:
            self.load_directory(self.root_dir)

    def load_directory(self, directory):
        """Load and reslove all schemas from directory"""

        yamls, resolvers = load_schemas_from_dir(directory)

        self.metaschema = yamls[self.metaschema_path]
        self.settings = yamls[self.settings_path]
        self.resolvers.update(resolvers)

        schemas = {
            schema['id']: self.resolve_schema(schema, deepcopy(schema))
            for path, schema in yamls.iteritems()
            if path not in self.exclude
        }
        self.schema.update(schemas)

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
        """Recursively resolves all references in a schema against
        ``self.resolvers``.

        :param obj: The object to recursively resolve.
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: A denormalized/resolved version of :param:`obj`.

        """
        refkey = '$ref'
        if isinstance(obj, dict):
            all_refkeys = [k for k in obj.keys() if k.startswith(refkey)]
            for key in all_refkeys:
                val = obj.pop(key)
                obj.update(self.resolve_reference(val, root))
            return {k: self.resolve_schema(v, root) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.resolve_schema(item, root) for item in obj]
        else:
            return obj


gdcdictionary = GDCDictionary()
