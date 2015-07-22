from jsonschema import validate, RefResolver
import yaml
import uuid
import copy
from pprint import pprint


def load_yaml_schema(path):
    with open(path, 'r') as f:
        return yaml.load(f)


def merge_schemas(a, b, path=None):
    "merges b into a"
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


def get_project_specific_schema(project, entity_type):
    root = copy.deepcopy(schema[entity_type])
    project_overrides = projects.get(project)
    if project_overrides:
        overrides = project_overrides.get(entity_type)
        if overrides:
            merge_schemas(root, overrides, [entity_type])
    return root


if __name__ == '__main__':

    # Load schemata
    metaschema = load_yaml_schema('metaschema.yaml')
    definitions = load_yaml_schema('definitions.yaml')
    schema = load_yaml_schema('schema.yaml')
    project1 = load_yaml_schema('project1.yaml')
    projects = {'project1': project1}
    resolver = RefResolver('definitions.yaml#', definitions)

    # validate aliquot schema
    validate(schema['aliquot'], metaschema['entity'])

    # # Example document
    # doc = {
    #     "type": "aliquot",
    #     "submitter_aliquot_id": 'aliquot_1',
    #     "parents": {
    #         "analyte_ids": [str(uuid.uuid4())]
    #     },
    #     "project_1_specific_thing": 'test string',
    # }

    # # Example validation
    # local_schema = get_project_specific_schema('project1', doc['type'])
    # validate(doc, local_schema, resolver=resolver)
    # print('\nsuccess.')
