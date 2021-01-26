"""This test verifies the schema contains no errors.

Note the kinda weird trigger and test functions getting passed around.
This is a mechanism that can easily be expanded upon if
have more tests later that need to validate new errors found within the
schema.

"""
import collections
import unittest

from .utils import BaseTest, check_for_cycles, validate_schemata


def _check_enum(enums):
    check_result = collections.defaultdict(list)
    for path, enum_list in enums.items():
        if not isinstance(enum_list, list):
            check_result["enum not a list"].append(path)

        for item in enum_list:
            if not isinstance(item, str):
                check_result["enum item is not a string"].append("{}: {}".format(path, item))

        if len(set(enum_list)) < len(enum_list):
            check_result["duplicates in enum"].append(path)
            duplicates = [item for item, count in collections.Counter(enum_list).items() if count > 1]
            for item in duplicates:
                check_result["duplicates in enum"].append("\t{}".format(item))
    return check_result


def _generate_error_message_for_enum(res_dict):
    message_lines = ["Errors in enum checks:"]
    for error_name, lines in res_dict.items():
        message_lines.append(error_name)
        for line in lines:
            message_lines.append("\t{}".format(line))
    return "\n".join(message_lines)


class SchemaTest(BaseTest):

    @unittest.expectedFailure
    def test_properties_enum(self):
        """Check the enums of node properties"""
        # The enums in _definitions.yaml, _terms.yaml and metaschema.yaml are not checked

        enum_dict = {}
        for node_name, node_schema in self.dictionary.schema.items():
            for prop_name, prop_schema in node_schema["properties"].items():
                if "enum" in prop_schema:
                    path_str = '{}->{}'.format(node_name, prop_name)
                    enum_dict[path_str] = prop_schema["enum"]

        res = _check_enum(enum_dict)
        assert len(res) == 0, _generate_error_message_for_enum(res)

    def test_schemas(self):
        validate_schemata(self.dictionary.schema, self.dictionary.metaschema)

    def test_acyclicality(self):
        """Confirm the dictionary has no (unexpected) cycles."""
        # File and archive both point to each other. Ignore archive since it's
        # less relevant than file. The other types should be acyclic.
        check_for_cycles(self.dictionary.schema, ['archive'])

    def test_acyclicalty_without_ignored_types(self):
        """
        Confirm the dictionary has cycles involving the expected type(s).

        If the acyclicality check passes like this, either the algorithm is
        missing something or we're ignoring types that we shouldn't.
        """
        with self.assertRaisesRegexp(AssertionError, 'cycle detected'):
            check_for_cycles(self.dictionary.schema)

    def test_check_for_cycles_positive(self):
        """Test the cycle detection logic with a synthetic positive case."""

        # The below schemata cover a few real edge cases; e.g., subgroups,
        # schemata with no incoming links, schemata with no outgoing links,
        # and schemata that link back to themselves.
        schemata = {
            'analyte': {
                'links': [
                    {
                        'subgroup': [
                            {'target_type': 'portion'},
                            {'target_type': 'sample'},
                        ]
                    }
                ]
            },
            'case': {
                'links': [
                    {'target_type': 'tissue_source_site'},
                ]
            },
            'portion': {
                'links': [
                    {'target_type': 'sample'},
                ]
            },
            'sample': {
                'links': [
                    {'target_type': 'case'},
                    {'target_type': 'sample'},
                    {'target_type': 'tissue_source_site'},
                ]
            },
            'slide': {
                'links': [
                    {
                        'subgroup': [
                            {'target_type': 'portion'},
                            {'target_type': 'sample'},
                        ]
                    }
                ]
            },
            'tissue_source_site': {'links': []},
        }

        check_for_cycles(schemata)

    def test_check_for_cycles_negative(self):
        """Test the cycle detection logic with a synthetic negative case."""

        # There is one cycle involving case, sample, and analyte, and a second
        # cycle that also includes portion.
        schemata = {
            'analyte': {
                'links': [
                    {
                        'subgroup': [
                            {'target_type': 'portion'},
                            {'target_type': 'sample'},
                        ]
                    }
                ]
            },
            'case': {
                'links': [
                    {'target_type': 'analyte'},
                ]
            },
            'portion': {
                'links': [
                    {'target_type': 'sample'},
                ]
            },
            'sample': {
                'links': [
                    {'target_type': 'case'},
                    {'target_type': 'sample'},
                    {'target_type': 'tissue_source_site'},
                ]
            },
            'slide': {
                'links': [
                    {
                        'subgroup': [
                            {'target_type': 'portion'},
                            {'target_type': 'sample'},
                        ]
                    }
                ]
            },
            'tissue_source_site': {'links': []},
        }

        with self.assertRaisesRegexp(AssertionError, 'cycle detected'):
            check_for_cycles(schemata)
