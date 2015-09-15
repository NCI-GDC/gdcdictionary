"""This is an example of json schema for the GDC using schemas defined
in local yaml files.

Included are a few functions to augment jsonschema and the python
validator.

Examples are at the end.

"""


from jsonschema import validate, RefResolver, ValidationError
import copy
import yaml
import argparse
import json
from python import GDCDictionary


def load_yaml_schema(path):
    with open(path, 'r') as f:
        return yaml.load(f)


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


def validate_entity(entity, schemata, resolver=None, project=None, name=''):
    """Validate an entity by looking up the core schema for its type and
    overriding it with any project level overrides

    """
    local_schema = get_project_specific_schema(
        projects, project, schemata[entity['type']], entity['type'])
    result = validate(entity, local_schema, resolver=resolver)
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

    print('ok.')


if __name__ == '__main__':

    ####################
    # Setup
    ####################
    project1 = load_yaml_schema('schemas/projects/project1.yaml')
    projects = {'project1': project1}

    parser = argparse.ArgumentParser(description='Validate JSON')
    parser.add_argument('jsonfiles', metavar='file',
                        type=argparse.FileType('r'), nargs='*',
                        help='json files to test if (in)valid')

    parser.add_argument('--invalid', action='store_true', default=False,
                        help='expect the files to be invalid instead of valid')

    args = parser.parse_args()

    ####################
    # Example validation
    ####################

    # Load schemata
    dictionary = GDCDictionary()
    resolver = RefResolver('definitions.yaml#', dictionary.definitions)
    validate_schemata(dictionary.schema, dictionary.metaschema)

    for f in args.jsonfiles:
        doc = json.load(f)
        if args.invalid:
            try:
                print("CHECK if {0} is invalid:".format(f.name)),
                validate_entity(doc, dictionary.schema, resolver)
            except ValidationError as e:
                print("Invalid as expected.")
                pass
            else:
                raise Exception("Expected invalid, but validated.")
        else:
            print ("CHECK if {0} is valid:".format(f.name)),
            validate_entity(doc, dictionary.schema, resolver)
            print("Valid as expected")
