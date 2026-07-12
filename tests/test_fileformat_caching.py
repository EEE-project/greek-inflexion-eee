"""_load_bundled_lexicon_yaml / _load_stemming_yaml caching (fileformat.py)."""
from greek_inflexion_eee.fileformat import (
    _load_bundled_lexicon_yaml,
    _load_lexicon_yaml,
    _load_stemming_yaml,
)


def test_bundled_lexicon_yaml_is_cached():
    first = _load_bundled_lexicon_yaml("pratt_verbs_lexicon.yaml")
    second = _load_bundled_lexicon_yaml("pratt_verbs_lexicon.yaml")
    assert first is second


def test_bundled_stemming_yaml_is_cached():
    first = _load_stemming_yaml("stemming.yaml")
    second = _load_stemming_yaml("stemming.yaml")
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
