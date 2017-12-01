import os
from dictionaryutils import DataDictionary as GDCDictionary

MOD_DIR = os.path.abspath(os.path.dirname(__file__))
gdcdictionary = GDCDictionary(
    root_dir=os.path.join(MOD_DIR, 'schemas'))
