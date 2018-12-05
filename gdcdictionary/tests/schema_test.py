"""This test verifies the schema contains no errors.

Note the kinda weird trigger and test functions getting passed around.
This is a mechanism that can easily be expanded upon if
have more tests later that need to validate new errors found within the
schema.

"""

from utils import validate_schemata, BaseTest


class SchemaTest(BaseTest):

    def traverse_schema_with_conditional(self, root, conditional_func, test_func):
        if conditional_func(root):
            test_func(root)
            return

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
        try:
            # Want to traverse the whole thing
            validate_schemata(self.dictionary.schema, self.dictionary.metaschema)
        except Exception as e:
            self.errors.add(e.message)
