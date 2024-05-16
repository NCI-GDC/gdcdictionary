try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import pytest

import gdcdictionary


def test_load_dictionary__invalid_location() -> None:
    with pytest.raises(IOError):
        gdcdictionary.GDCDictionary(root_dir="invalid/dir/path")


def test_load_dictionary() -> None:
    with files("tests") as path:
        dictionary = gdcdictionary.GDCDictionary(root_dir=str(path.parent / "src/gdcdictionary/schemas"), lazy=False)
        assert dictionary.loaded is True
