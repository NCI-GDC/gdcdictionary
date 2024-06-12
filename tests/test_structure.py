import dataclasses

from gdcdictionary import gdcdictionary


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
    """"""
    def insert(self, association: Association) -> None:
        """Raise duplicate error"""
        if association in self:
            raise ValueError(
                f"{association} already exists - Duplicate links not allowed."
            )
        super().add(association)

    def merge(self, associations: "Associations") -> None:
        for association in associations:
            if association in self:
                raise ValueError(
                    f"{association} already exists - Duplicate links not allowed."
                )
        super().update(associations)


def extract_links(source, links) -> Associations:
    associations = Associations()
    for link in links:
        if "subgroup" in link:
            associations.merge(extract_links(source, link["subgroup"]))
            continue
        left = Association(name=link["name"], source=source, target=link["target_type"])
        right = Association(
            name=link["backref"], target=source, source=link["target_type"]
        )

        associations.insert(left)
        associations.insert(right)
    return associations


def read_associations():
    associations = Associations()
    for schema in gdcdictionary.schema.values():
        name = schema["id"]
        associations.merge(extract_links(name, schema["links"]))
    return associations


def test_associations():
    """passes if no exception is raised"""
    read_associations()
