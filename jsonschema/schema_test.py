"""This is an example of json schema for the GDC using schemas defined
in local yaml files.

Included are a few functions to augment jsonschema and the python
validator.

Examples are at the end.

"""


from jsonschema import validate, RefResolver
import copy
import uuid
import yaml


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


def validate_entity(entity, schemata, resolver=None, project=None):
    """Validate an entity by looking up the core schema for its type and
    overriding it with any project level overrides

    """
    local_schema = get_project_specific_schema(
        projects, project, schemata[entity['type']], entity['type'])
    return validate(entity, local_schema, resolver=resolver)


if __name__ == '__main__':

    ####################
    # Setup
    ####################

    # Load schemata
    metaschema = load_yaml_schema('metaschema.yaml')
    definitions = load_yaml_schema('definitions.yaml')
    project1 = load_yaml_schema('projects/project1.yaml')
    projects = {'project1': project1}
    resolver = RefResolver('definitions.yaml#', definitions)

    schemata = {
        "aliquot": load_yaml_schema('aliquot.yaml'),
        "case": load_yaml_schema('case.yaml'),
        "sample": load_yaml_schema('sample.yaml')
    }

    # validate schemata
    map(lambda s: validate(s, metaschema['entity']), schemata.values())

    ####################
    # Example validation
    ####################

    aliquot1 = {
        "type": "aliquot",
        "submitter_aliquot_id": 'aliquot_1',
        "amount": 5.0,
        "parents": {
            "analyte_ids": [str(uuid.uuid4())]
        },
        "project_1_specific_thing": 'test string',
    }

    case1 = {
        "type": "case",
        "submitter_case_id": 'case_1',
        "parents": {
            "project_id": str(uuid.uuid4())
        },
        "gender": "female",
        "race": "Unknown"
    }

    # These should pass
    validate_entity(case1, schemata, resolver)
    validate_entity(aliquot1, schemata, resolver, 'project1')

    # These should fail
    try:
        validate_entity(aliquot1, schemata, resolver)
    except:
        pass
    else:
        raise Exception('Expected to fail')

    print('\nsuccess.')
