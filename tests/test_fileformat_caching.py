"""_load_bundled_yaml caching (fileformat.py)."""
import pytest

from greek_inflexion_eee.fileformat import _load_bundled_yaml, _load_lexicon_yaml


@pytest.mark.parametrize("filename", ["pratt_verbs_lexicon.yaml", "stemming.yaml"])
def test_bundled_yaml_is_cached(filename):
    first = _load_bundled_yaml(filename)
    second = _load_bundled_yaml(filename)
    assert first is second


def test_load_lexicon_yaml_routes_bundled_names_through_cache():
    first = _load_lexicon_yaml("pratt_verbs_lexicon.yaml")
    second = _load_lexicon_yaml("pratt_verbs_lexicon.yaml")
    assert first is second


def test_load_lexicon_yaml_absolute_path_not_cached(tmp_path):
    custom = tmp_path / "custom.yaml"
    custom.write_text("a:\n  stems:\n    noun: a-stem\n", encoding="utf-8")

    first = _load_lexicon_yaml(str(custom))
    custom.write_text("b:\n  stems:\n    noun: b-stem\n", encoding="utf-8")
    second = _load_lexicon_yaml(str(custom))

    assert first != second
    assert "b" in second
