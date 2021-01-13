"""This test verifies the schema contains no errors.

Note the kinda weird trigger and test functions getting passed around.
This is a mechanism that can easily be expanded upon if
have more tests later that need to validate new errors found within the
schema.

"""
import collections
import unittest

from .utils import BaseTest, check_for_cycles, validate_schemata


class SchemaTest(BaseTest):

    @unittest.expectedFailure
    def test_enum(self):
        stack = collections.deque()
        res = collections.defaultdict(list)

        def _get_path_str(path_stack):
            return '->'.join(path_stack)

        def bfs_with_enum_test(root, test_func, path):
            if isinstance(root, dict) and 'enum' in root.keys():
                test_func(root, path)

            if isinstance(root, list):
                for child in root:
                    bfs_with_enum_test(child, test_func, path)
            elif isinstance(root, dict):
                for child in root.keys():
                    path.append(child)
                    bfs_with_enum_test(root[child], test_func, path)
                    path.pop()

        def check_enum(property_name, current_path):
            enum_list = property_name['enum']
            if not isinstance(enum_list, list):
                res["property enums is not a list"].append(_get_path_str(current_path))

            for item in enum_list:
                if not isinstance(item, str):
                    res["enum item is not a string"].append("{}: {}".format(_get_path_str(current_path), item))

            if len(set(enum_list)) < len(enum_list):
                res["duplicates in enum"].append(_get_path_str(current_path))
                duplicates = [item for item, count in collections.Counter(enum_list).items() if count > 1]
                for item in duplicates:
                    res["duplicates in enum"].append("\t{}".format(item))

        def generate_error_message_for_enum(res_dict):
            message_lines = ["Errors in enum checks:"]
            for error_name, lines in res_dict.items():
                message_lines.append(error_name)
                for line in lines:
                    message_lines.append("\t{}".format(line))
            return "\n".join(message_lines)

        bfs_with_enum_test(self.dictionary.schema, check_enum, stack)
        assert len(res) == 0, generate_error_message_for_enum(res)

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
