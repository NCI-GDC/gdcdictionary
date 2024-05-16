"""JSON validator module for validating user supplied json documents.

Example:
    .. code-block:: python
        import gdcdictionary

        # single
        instance = {'type': 'case', 'disease_type': 'bad disease'}
        for violation in gdcdictionary.validate(instance):
           print(violation.message, violation.keys)

        # multiple
        for violation in gdcdictionary.validate_instances([instance]):
            ...

"""
from __future__ import annotations

import logging
import re
from typing import Any, List, NamedTuple, Dict, Optional, Iterable

from gdcdictionary import gdcdictionary
from jsonschema import Draft4Validator


logger = logging.getLogger(__name__)
invalid_property_regex = re.compile(r"('[a-zA-Z_-]+')+")
_validators: Dict[str, SchemaValidator] = {}


def _parse_keys_from_error_message(error_msg: str) -> List[str]:
    missing_prop = invalid_property_regex.findall(error_msg)
    return [m.replace("'", "") for m in missing_prop]


class SchemaValidationError(NamedTuple):
    """A single schema violation representation.

    Properties:
        schema: the name of the json schema e.g. aliquot
        message: the error message describing the violation
        keys: the list of keys whose constraints were violated.
    """

    schema: str
    message: str
    keys: List[str]

    @classmethod
    def from_values(
        cls, schema: str, message: str, keys: List[str]
    ) -> SchemaValidationError:
        if "Additional properties are not allowed" in message:
            message = f"Key(s) {keys} not a valid property for type '{schema}'"
        logger.debug(
            "json schema violation for '%s'",
            schema,
            extra={"keys": keys, "message": message},
        )
        return SchemaValidationError(schema, message, keys)


class SchemaValidator:
    """Validator for individual schemas in the dictionary.

    Properties:
        name: name of specific dictionary schema
        validator: json validator initialized with the schema
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.validator = Draft4Validator(gdcdictionary.schema[name])

    def post_validate(self, violations: List[SchemaValidationError]) -> None:
        """Implements further validations and/or filtering here."""
        ...

    def pre_validate(self, json_instance: Any) -> None:
        """Implements any prior work to be done on the json before validation."""
        ...

    def iter_errors(self, json_instance: Any) -> List[SchemaValidationError]:
        violations: List[SchemaValidationError] = []
        self.pre_validate(json_instance)
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
            violations.append(
                SchemaValidationError.from_values(self.name, message, keys)
            )
        self.post_validate(violations)
        return violations


def _get_validator(schema_name: str) -> Optional[SchemaValidator]:
    if schema_name not in _validators and schema_name not in gdcdictionary.schema:
        logger.warning("Unknown schema name specified %s", schema_name)
        return None
    _validators[schema_name] = SchemaValidator(schema_name)
    return _validators[schema_name]


def validate(instance: dict) -> List[SchemaValidationError]:
    """Validate a single json instance.

    `type` is handled specially as it is not defined as a required field in
    the dictionary, but is required to correctly figure out the target schema.

    Args:
        instance: json instance

    Returns:
        a list of errors
    """
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
    """Validate multiple json instances.

    Args:
        instances: list of json documents.

    Returns:
        list of errors
    """
    violations: List[SchemaValidationError] = []
    for instance in instances:
        violations += validate(instance)
    return violations
