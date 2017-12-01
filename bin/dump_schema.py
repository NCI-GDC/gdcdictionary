"""
This script dumps all schema files in currently installed gdcdictionary
to one json schema to ./artifacts folder.

"""
from exceptions import OSError
import json
import os

from gdcdictionary import SCHEMA_DIR
from dictionaryutils import dump_schemas_from_dir
try:
    os.mkdir('artifacts')
except OSError:
    pass

with open(os.path.join('artifacts', 'schema.json'), 'w') as f:
    json.dump(
        dump_schemas_from_dir(SCHEMA_DIR), f)
