from __future__ import annotations

import copy
import logging
import pathlib
from importlib import abc, resources
from typing import NamedTuple

import jsonschema
import yaml

logger = logging.getLogger(__name__)


class ResolverPair(NamedTuple):
    resolver: jsonschema.RefResolver
    source: dict


def get_schema_directory(
    local_path: str | abc.Traversable | None = None,
) -> abc.Traversable:
    """Resolve the directory containing the schema definitions files.

    Args:
        local_path: custom location for the schema
    Returns:
        the schema directory as a generic traversable.
    """
    if local_path is None:
        return resources.files("gdcdictionary") / "schemas"

    if isinstance(local_path, str):
        local_path = pathlib.Path(local_path)

    if not local_path.is_dir():
        raise OSError("Specified template directory '%s' does not exist", local_path)

    return local_path


class GDCDictionary:
    _metaschema_path = "metaschema.yaml"
    _definitions_paths = (
        "_definitions.yaml",
        "_terms.yaml",
        "_terms_enum.yaml",
    )

    def __init__(
        self,
        lazy: bool = False,
        root_dir: str | abc.Traversable | None = None,
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
        self.exclude = frozenset((self.metaschema_path, *self.definitions_paths))
        self._schema = dict()
        self.resolvers: dict[str, ResolverPair] = dict()
        self._yaml_loader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

        if not lazy:
            self.load_directory(self.root_dir)

    def load_yaml(self, file: abc.Traversable) -> dict:
        """Return contents of yaml file as dict"""
        # For DAT-1064 Bomb out hard if unicode is in a schema file
        # But allow unicode through the terms and definitions
        if file.name not in self.exclude:
            try:
                file.read_text(encoding="ascii")
            except Exception as e:
                logger.error(f"Error in file: {file}")
                raise e

        with file.open("rb") as fp:
            return yaml.load(fp, Loader=self._yaml_loader)

    def load_schemas_from_dir(
        self, directory: abc.Traversable
    ) -> tuple[dict[str, dict], dict[str, ResolverPair]]:
        """Returns all yamls and resolvers of those yamls from dir"""

        schemas, resolvers = {}, {}
        paths = (p for p in directory.iterdir() if p.name.endswith(".yaml"))

        for path in paths:
            schema = self.load_yaml(path)
            schemas[path.name] = schema
            resolver = jsonschema.RefResolver(f"{path.name}#", schema)
            resolvers[path.name] = ResolverPair(resolver, schema)

        return schemas, resolvers

    def load_directory(self, directory: abc.Traversable) -> None:
        """Load and resolve all schemas from directory"""

        yamls, resolvers = self.load_schemas_from_dir(directory)

        self.metaschema = yamls[self.metaschema_path]
        self.resolvers.update(resolvers)

        schemas = {
            schema["id"]: self.resolve_schema(schema, copy.deepcopy(schema))
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
            resolver = jsonschema.RefResolver("#", root)
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
