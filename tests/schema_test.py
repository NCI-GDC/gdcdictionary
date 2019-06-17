"""This test verifies the schema contains no errors.

Note the kinda weird trigger and test functions getting passed around.
This is a mechanism that can easily be expanded upon if
have more tests later that need to validate new errors found within the
schema.

"""

from .utils import BaseTest, check_for_cycles, validate_schemata


class SchemaTest(BaseTest):

    def traverse_schema_with_conditional(self, root, conditional_func, test_func):
        if conditional_func(root):
            test_func(root)

        if isinstance(root, list):
            for child in root:
                self.traverse_schema_with_conditional(child, conditional_func, test_func)
        elif isinstance(root, dict):
            for child in root.keys():
                self.traverse_schema_with_conditional(root[child], conditional_func, test_func)

    def test_enum_is_string(self):

        def trigger(root):
            if isinstance(root, dict) and 'enum' in root.keys():
                return True
            return False

        def test_enum(root):
            children = root['enum']
            assert isinstance(children, list), "Enums children wasn't a list"
            for child in children:
                assert isinstance(child, str), "Offending enum found:" + str(child)

        self.traverse_schema_with_conditional(self.dictionary.schema, trigger, test_enum)

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
