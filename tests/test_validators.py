"""This is an example of json schema for the GDC using schemas defined
in local yaml files (see gdcdictionary/examples).

This test class is making sure the example jsons comply with the schema.

Note this is NOT testing that the schema is sane. Just that we adhere
to it

"""
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import json
import pytest

import gdcdictionary


def get_all_paths(subdir: str) -> str:
    with files("tests") as path:
        examples_path = path.parent / f"examples/{subdir}"
        yield from sorted(examples_path.glob("*.json"))


@pytest.mark.parametrize("path", get_all_paths("valid"))
def test_valid_examples(path, schema):
    with open(path) as f:
        doc = json.load(f)
        assert len(gdcdictionary.validate(doc)) == 0


@pytest.mark.parametrize("path", get_all_paths("invalid"))
def test_invalid_examples(path, schema):
    with open(path) as f:
        doc = json.load(f)
        violations = gdcdictionary.validate(doc)
        assert len(violations) > 0
        print(violations)


def test_validate_instances() -> None:
    paths = get_all_paths("valid")
    instances = []
    for path in paths:
        with open(path) as f:
            doc = json.load(f)
            instances.append(doc)
    violations = gdcdictionary.validate_instances(instances)
    assert len(violations) == 0


def test_validate_instances__invalid_types() -> None:
    instances = [
        {"type": "species"},
        {"type": "case", "python_version": "38"},
        {"name": "species"},
    ]
    violations = gdcdictionary.validate_instances(instances)
    print(violations)

    assert len(violations) > 2

    unknown_types = [v for v in violations if v.schema == ""]
    assert len(unknown_types) == 2

    case_required_field_violation = next(
        v for v in violations if v.schema == "case" and v.keys == ["submitter_id"]
    )
    assert (
        case_required_field_violation.message == "'submitter_id' is a required property"
    )

    case_extra_field_violation = next(
        v for v in violations if v.schema == "case" and v.keys == ["python_version"]
    )
    assert (
        case_extra_field_violation.message
        == "Key(s) ['python_version'] not a valid property for type 'case'"
    )
