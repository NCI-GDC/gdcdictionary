import dataclasses
from collections.abc import Mapping, Sequence
from importlib import resources
from typing import Any

import pytest

import gdcdictionary


@dataclasses.dataclass(frozen=True)
class Association:
    """Represents a directed link between source and target.

    A single link definition in a node will expand into two
    associations, one for each direction.

    For example, the definition below on the node `aliquot`
    ```
        id: aliquot
        links:
          - exclusive: true
            required: true
            subgroup:
              - name: analytes
                backref: aliquots
                label: derived_from
                target_type: analyte
                multiplicity: many_to_one
                required: false
              - name: samples
                backref: aliquots
                label: derived_from
                target_type: sample
                multiplicity: many_to_many
                required: false
          - name: centers
            backref: aliquots
            label: shipped_to
            target_type: center
            multiplicity: many_to_one
            required: false
    ```
    This results in 6 possible associations
        centers: aliquot --> center
        aliquots: center --> aliquot
        analytes: aliquot --> analyte
        aliquots: analyte --> aliquot
        samples: aliquot --> sample
        aliquots: sample --> aliquot

    Within a source node, the association name should be unique.
    For example, on aliquot there should be only one association named `centers`
    """

    name: str
    source: str
    target: str = dataclasses.field(compare=False, hash=False)


class Associations(set):
    """An unordered collection of unique association."""

    def add(self, association: Association) -> None:
        """Raise key error if entry already exists."""
        if association in self:
            raise KeyError(f"{association} already exists - Duplicate links not allowed.")
        super().add(association)

    def update(self, associations: "Associations") -> None:
        """Raise key error if entry already exists."""
        for association in associations:
            if association in self:
                raise ValueError(
                    f"{association} already exists - Duplicate links not allowed."
                )
        super().update(associations)


def extract_links(source: str, links: Sequence[Mapping[str, Any]]) -> Associations:
    """Inspect links collected from the schema of a node and generate Associations."""
    associations = Associations()
    for link in links:
        if "subgroup" in link:
            associations.update(extract_links(source, link["subgroup"]))
            continue
        forward = Association(name=link["name"], source=source, target=link["target_type"])
        reverse = Association(name=link["backref"], target=source, source=link["target_type"])

        associations.add(forward)
        associations.add(reverse)
    return associations


def read_associations(dictionary: gdcdictionary.GDCDictionary) -> Associations:
    """Read all association in the dictionary."""
    associations = Associations()
    for schema in dictionary.schema.values():
        name = schema["id"]
        associations.update(extract_links(name, schema["links"]))
    return associations


def test_load_dictionary__invalid_location() -> None:
    with pytest.raises(IOError):
        gdcdictionary.GDCDictionary(root_dir="invalid/dir/path")


def test_load_dictionary() -> None:
    schemas_resource = resources.files("gdcdictionary") / "schemas"
    dictionary = gdcdictionary.GDCDictionary(root_dir=schemas_resource, lazy=False)

    assert dictionary.loaded is True


def test_unique_associations():
    """passes if no exception is raised"""
    read_associations(gdcdictionary.gdcdictionary)
