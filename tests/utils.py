""" A file to hold all test utilities. Note the project
specific overrrides are not being used in the GDC currently.

"""

from collections import defaultdict
import copy
import os
import yaml
import unittest

from jsonschema import validate

from gdcdictionary import ROOT_DIR, GDCDictionary


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


DATA_DIR = os.path.join(ROOT_DIR, 'examples')
project1 = load_yaml(os.path.join(ROOT_DIR, 'schemas/projects/project1.yaml'))
projects = {'project1': project1}


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.dictionary = GDCDictionary()
        self.definitions = load_yaml(os.path.join(ROOT_DIR, 'schemas', '_definitions.yaml'))


def merge_schemas(a, b, path=None):
    """Recursively zip schemas together

    """
    path = path if path is not None else []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_schemas(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                print("Overriding '{}':\n\t- {}\n\t+ {}".format(
                    '.'.join(path + [str(key)]), a[key], b[key]))
                a[key] = b[key]
        else:
            print("Adding '{}':\n\t+ {}".format(
                '.'.join(path + [str(key)]), b[key]))
            a[key] = b[key]
    return a


def get_project_specific_schema(projects, project, schema, entity_type):
    """Look up the core schema for its type and override it with any
    project level overrides

    """
    root = copy.deepcopy(schema)
    project_overrides = projects.get(project)
    if project_overrides:
        overrides = project_overrides.get(entity_type)
        if overrides:
            merge_schemas(root, overrides, [entity_type])
    return root


def validate_entity(entity, schemata, project=None, name=''):
    """Validate an entity by looking up the core schema for its type and
    overriding it with any project level overrides

    """
    local_schema = get_project_specific_schema(
        projects, project, schemata[entity['type']], entity['type'])
    result = validate(entity, local_schema)
    return result


def validate_schemata(schemata, metaschema):
    # validate schemata
    print('Validating schemas against metaschema... '),
    for s in schemata.values():
        validate(s, metaschema)

        def assert_link_is_also_prop(link):
            assert link in s['properties'],\
                "Entity '{}' has '{}' as a link but not property".format(
                    s['id'], link)

        for link in [l['name'] for l in s['links'] if 'name' in l]:
            assert_link_is_also_prop(link)
        for subgroup in [l['subgroup'] for l in s['links'] if 'name' not in l]:
            for link in [l['name'] for l in subgroup if 'name' in l]:
                assert_link_is_also_prop(link)


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

        for link in schema.get('links', []):
            if 'subgroup' in link:
                target_types = [g['target_type'] for g in link['subgroup']]
            else:
                target_types = [link['target_type']]

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
    removable_types = [
        schema_type for schema_type in forward
        if schema_type not in backward
    ]

    while removable_types:
        schema_type = removable_types.pop()
        for target_type in forward[schema_type]:
            backward[target_type].remove(schema_type)
            if not backward[target_type]:
                removable_types.append(target_type)
                del backward[target_type]

    assert not backward, 'cycle detected among {}'.format(backward.keys())
