"""JSON validator module for validating user supplied json documents."""
from __future__ import annotations

import logging
import re
from typing import Any, List, NamedTuple, Dict, Optional, Iterable

from gdcdictionary import gdcdictionary
from jsonschema import Draft4Validator


logger = logging.getLogger(__name__)
missing_prop_re = re.compile(r"('[a-zA-Z_-]+')+")
_validators: Dict[str, SchemaValidator] = {}


def _parse_keys_from_error_message(error_msg: str) -> List[str]:
    missing_prop = missing_prop_re.findall(error_msg)
    return [m.replace("\'", "") for m in missing_prop]


class SchemaValidationError(NamedTuple):
    schema: str
    message: str
    keys: List[str]


class SchemaValidator:
    """Validator for individual schemas in the dictionary.

    Properties:
        name: name of specific dictionary schema
        validator: json validator initialized with the schema
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.validator = Draft4Validator(gdcdictionary.schema[name])

    def post_validate(self, violations: List[SchemaValidationError]):
        ...

    def iter_errors(self, json_instance: Any) -> List[SchemaValidationError]:
        violations: List[SchemaValidationError] = []
        for error in self.validator.iter_errors(instance=json_instance):
            # the key will be  property.sub property for nested properties
            errors = [str(e) for e in error.path if error.path]
            keys = [".".join(errors)] if errors else []
            if not keys:
                keys = _parse_keys_from_error_message(error.message)
            message = error.message
            if error.context:
                message += ": {}".format(
                    " and ".join([c.message for c in error.context])
                )
            violations.append(SchemaValidationError(self.name, message, keys))
        self.post_validate(violations)
        return violations


def _get_validator(schema_name: str) -> Optional[SchemaValidator]:
    if schema_name not in _validators and schema_name not in gdcdictionary.schema:
        logger.warning("Unknown schema name specified %s", schema_name)
        return None
    _validators[schema_name] = SchemaValidator(schema_name)
    return _validators[schema_name]


def validate(instance: dict) -> List[SchemaValidationError]:
    if "type" not in instance:
        return [
            SchemaValidationError(
                schema="", message="'type' is a required property", keys=["type"]
            )
        ]
    validator = _get_validator(instance["type"])
    if not validator:
        return [
            SchemaValidationError(
                schema="",
                message=f"specified type: {instance['type']} is not in the current data model",
                keys=["type"],
            )
        ]
    return validator.iter_errors(instance)


def validate_instances(instances: Iterable[dict]) -> List[SchemaValidationError]:
    violations: List[SchemaValidationError] = []
    for instance in instances:
        violations += validate(instance)
    return violations
