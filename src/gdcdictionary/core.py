from __future__ import annotations

import logging
import pathlib
from collections import namedtuple
from copy import deepcopy
from importlib import resources
from typing import Any

import yaml
from jsonschema import RefResolver

logger = logging.getLogger(__name__)
ResolverPair = namedtuple("ResolverPair", ["resolver", "source"])


def get_schema_directory(local_path: str | None = None) -> pathlib.Path:
    """Resolve the directory containing the schema definitions files.

    Args:
        local_path: custom location for the schema
    Returns:
        the schema directory as path object.
    """
    if local_path:
        path = pathlib.Path(local_path)

        if not path.exists():
            raise OSError("Specified template directory '%s' does not exist", path)
        return path

    # use default embedded location
    with resources.files("gdcdictionary").joinpath("schemas") as path:
        return path


class GDCDictionary:
    _metaschema_path = "metaschema.yaml"
    _definitions_paths = [
        "_definitions.yaml",
        "_terms.yaml",
        "_terms_enum.yaml",
    ]

    def __init__(
        self,
        lazy: bool = False,
        root_dir: str | None = None,
        definitions_paths: list[str] | None = None,
        metaschema_path: str | None = None,
    ):
        """Creates a new dictionary instance.

        :param root_dir: The directory to find schemas
        :param metaschema_path: The metaschema to validate schemas with
        :param definitions_paths: Paths to resolve $ref to
        :param lazy: If true, wait to load dictionary

        """

        self.loaded = False
        self.metaschema = None

        self.root_dir = get_schema_directory(root_dir)
        self.metaschema_path = metaschema_path or self._metaschema_path
        self.definitions_paths = definitions_paths or self._definitions_paths
        self.exclude = [self.metaschema_path] + self.definitions_paths
        self._schema = dict()
        self.resolvers = dict()
        if not lazy:
            self.load_directory(self.root_dir)

    def load_yaml(self, name):
        """Return contents of yaml file as dict"""
        # For DAT-1064 Bomb out hard if unicode is in a schema file
        # But allow unicode through the terms and definitions
        with open(name) as f:
            if name not in self.exclude:
                try:
                    f.read().encode("ascii")
                    f.seek(0)
                except Exception as e:
                    logger.error(f"Error in file: {name}")
                    raise e
            if yaml.__with_libyaml__:
                return yaml.load(f, Loader=yaml.CSafeLoader)
            logger.debug(
                "To enable CSafeLoader install libyaml. Falling back to yaml.safe_load()"
            )
            return yaml.safe_load(f)

    def load_schemas_from_dir(
        self, directory: pathlib.Path
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Returns all yamls and resolvers of those yamls from dir"""

        schemas, resolvers = {}, {}

        for path in directory.glob("*.yaml"):
            schema = self.load_yaml(path)
            schemas[path.name] = schema
            resolver = RefResolver(f"{path.name}#", schema)
            resolvers[path.name] = ResolverPair(resolver, schema)

        return schemas, resolvers

    def load_directory(self, directory: pathlib.Path) -> None:
        """Load and resolve all schemas from directory"""

        yamls, resolvers = self.load_schemas_from_dir(directory)

        self.metaschema = yamls[self.metaschema_path]
        self.resolvers.update(resolvers)

        schemas = {
            schema["id"]: self.resolve_schema(schema, deepcopy(schema))
            for path, schema in yamls.items()
            if path not in self.exclude
        }
        self._schema.update(schemas)
        self.loaded = True

    def resolve_reference(self, value, root):
        """Resolves a reference.

        :param value: The actual reference, e.g. ``_yaml.yaml#/def``
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: JSON Schema pointed to by :param:`value`

        """
        base, ref = value.split("#", 1)

        if base:
            resolver, new_root = self.resolvers[base]
            referrer, resolution = resolver.resolve(value)
            self.resolve_schema(resolution, new_root)
        else:
            resolver = RefResolver("#", root)
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

        if isinstance(obj, dict):
            for key in obj.copy().keys():
                if key == "$ref":
                    refs = obj.pop(key)
                    self.resolve_local_refs(refs, obj, root)
            return {k: self.resolve_schema(v, root) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.resolve_schema(item, root) for item in obj]
        else:
            return obj

    def resolve_local_refs(self, refs, obj, root):
        """Converts a string ref to list of refs & resolves the references"""
        if not isinstance(refs, list):
            refs = [refs]
        for ref in refs:
            obj.update(self.resolve_reference(ref, root))

    @property
    def schema(self) -> dict:
        if not self.loaded:
            self.load_directory(self.root_dir)
        return self._schema


gdcdictionary = GDCDictionary(lazy=True)
