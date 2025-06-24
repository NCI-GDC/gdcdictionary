"""A file to hold all test utilities. Note the project
specific overrrides are not being used in the GDC currently.

"""

from __future__ import annotations

import unittest
from collections import defaultdict
from collections.abc import Iterator

import jsonschema
import yaml

import gdcdictionary
from gdcdictionary import GDCDictionary


def load_yaml(path, root: str | None = None):
    schema_path = gdcdictionary.get_schema_directory(root) / path
    with schema_path.open() as f:
        return yaml.safe_load(f)


project1 = load_yaml("projects/project1.yaml")
projects = {"project1": project1}


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.dictionary = GDCDictionary()
        self.definitions = load_yaml("_definitions.yaml")


def _get_link_names(schema: dict) -> Iterator[str]:
    for link in schema.get("links", ()):
        if "name" in link:
            yield link["name"]

        for sublink in link.get("subgroup", ()):
            yield sublink["name"]


def validate_schemata(schemata, metaschema):
    # validate schemata
    print("Validating schemas against metaschema...")

    for schema in schemata.values():
        jsonschema.validate(schema, metaschema)

        for link_name in _get_link_names(schema):
            assert link_name in schema["properties"], (
                f"Entity '{schema['id']}' has '{link_name}' as a link but not property"
            )


def check_for_cycles(schemata, ignored_types=None):
    """Assert the given schemata contain no cycles (outside ignored types)."""
    if ignored_types is None:
        ignored_types = []

    # Build a bidirectional map representing the links between schema types.
    forward = defaultdict(set)
    backward = defaultdict(set)
    for schema_type, schema in schemata.items():
        # Ignore cycles involving types that we know don't hurt anything so we
        # can detect new cycles that might actually hurt.
        if schema_type in ignored_types:
            continue

        for link in schema.get("links", []):
            if "subgroup" in link:
                target_types = [g["target_type"] for g in link["subgroup"]]
            else:
                target_types = [link["target_type"]]

            for target_type in target_types:
                # It's fine for a type to link to itself. Ignore such links
                # to avoid confusing the below cycle detection algorithm.
                if target_type != schema_type:
                    forward[schema_type].add(target_type)
                    backward[target_type].add(schema_type)

    # Iteratively remove types that have no links pointing to them.
    # If there are no cycles, this will continue to free up types without
    # any links until the entire map is cleared out. If a cycle exists,
    # this process will fail to remove all of the links.
    removable_types = [schema_type for schema_type in forward if schema_type not in backward]

    while removable_types:
        schema_type = removable_types.pop()
        for target_type in forward[schema_type]:
            backward[target_type].remove(schema_type)
            if not backward[target_type]:
                removable_types.append(target_type)
                del backward[target_type]

    assert not backward, f"cycle detected among {backward.keys()}"
