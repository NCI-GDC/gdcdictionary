"""This is an example of json schema for the GDC using schemas defined
in local yaml files (see gdcdictionary/examples).

This test class is making sure the example jsons comply with the schema.

Note this is NOT testing that the schema is sane. Just that we adhere
to it

"""

import uuid

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


@pytest.mark.parametrize("partial", [False, True])
def test_validate_instances__invalid_types(partial: bool) -> None:
    """Test validating multiple documents at the same time.

    Test data is chosen to cover three scenarios:
        * missing `type` property
        * unexpected property
        * unknown type - type does not match a known schema

    The test does not cover every possible scenario that causes a violation.
    """
    instances = [
        {"type": "species"},
        {"type": "case", "submitter_id": "unsc-0", "python_version": "38"},
        {"type": "aliquot", "python_version": "38"},
        {"name": "species"},
    ]
    violations = gdcdictionary.validate_instances(instances, partial)
    print(violations)

    assert len(violations) > 2

    unknown_types = [v for v in violations if v.schema == ""]
    assert len(unknown_types) == 1

    case_required_field_violation = next(
        v for v in violations if v.schema == "aliquot" and v.keys == ["submitter_id", "id"]
    )
    assert case_required_field_violation.message == "one of ['submitter_id', 'id'] is required."

    case_extra_field_violation = next(
        v for v in violations if v.schema == "case" and v.keys == ["python_version"]
    )
    assert (
        case_extra_field_violation.message
        == "Key(s) ['python_version'] not a valid property for type 'case'"
    )


def test_partials_validation() -> None:
    # example missing required fields
    instances = [
        {"type": "case", "days_to_consent": 123, "submitter_id": "UNSC-2"},
        {"type": "case", "days_to_consent": 123, "id": str(uuid.uuid4())},
    ]
    violations = gdcdictionary.validate_instances(instances, partial=True)
    assert len(violations) == 0
