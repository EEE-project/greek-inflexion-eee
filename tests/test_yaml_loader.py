"""The YAML loader of fileformat.py (libyaml's loader when PyYAML has one)."""
from importlib.resources import files

import pytest
import yaml

from greek_inflexion_eee.fileformat import _DATA_PKG, _yaml_load

_BUNDLED = sorted(p.name for p in files(_DATA_PKG).iterdir() if p.name.endswith(".yaml"))


@pytest.mark.parametrize("filename", _BUNDLED)
def test_builds_the_same_data_as_safe_load(filename):
    text = (files(_DATA_PKG) / filename).read_text(encoding="utf-8")
    # repr, not ==: it also compares the order of the keys and the types of the values
    assert repr(_yaml_load(text)) == repr(yaml.safe_load(text)), filename


def test_refuses_python_object_tags():
    with pytest.raises(yaml.YAMLError):
        _yaml_load("!!python/object/apply:os.getcwd []")
