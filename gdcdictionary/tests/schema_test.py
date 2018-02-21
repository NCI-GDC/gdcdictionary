"""This test verifies the schema contains no errors.

"""

from utils import validate_schemata, BaseTest


class SchemaTest(BaseTest):

    def traverse_schema_with_conditional(self, root, conditional_func, test_func):
        pass

    def test_enum_is_string(self):

        def trigger(root):
            if root == 'enum':
                return True
            return False

        def test_enum(children):
            assert isinstance(children, list), "Enums children wasn't a list"
            for child in children:
                assert isinstance(child, str), "Child of enum wasn't a string"

        self.traverse_schema_with_conditional(self.dictionary.schema, trigger, test_enum)

    def test_schemas(self):
        validate_schemata(self.dictionary.schema, self.dictionary.metaschema)

