"""Dual forms of nouns and adjectives.

The expected forms are in tests/test_data/noun_dual_test.yaml. Each one was checked against Perseids Morpheus, or against the Wiktionary
inflection table where the entry's `source` says so. The rule file itself is checked too: A and V refer to N, D refers to G.
"""
import unicodedata
from pathlib import Path

import pytest
import yaml

from greek_accentuation.characters import strip_length
from greek_inflexion_eee import load_adj_default, load_noun_default, load_noun_lexicons
from greek_inflexion_eee.accent import _NAV_DUAL
from greek_inflexion_eee.fileformat import _load_lexicon_yaml

_TEST_DATA = Path(__file__).parent / "test_data" / "noun_dual_test.yaml"
_META_KEYS = {"source", "kind", "lexicon", "lemma"}
_ENTRIES = yaml.safe_load(_TEST_DATA.read_text(encoding="utf-8"))


def _cases():
    return [(e["kind"], e["lexicon"], e["lemma"], key, expected)
            for e in _ENTRIES for key, expected in e.items() if key not in _META_KEYS]


@pytest.fixture(scope="module")
def inflexions():
    return {
        ("noun", "default"): load_noun_default(),
        ("noun", "homer"): load_noun_lexicons("homer"),
        ("noun", "morpheus"): load_noun_lexicons("morpheus"),
        ("adj", "default"): load_adj_default(),
    }


@pytest.mark.parametrize("kind,lexicon,lemma,key,expected", _cases())
def test_dual_form(inflexions, kind, lexicon, lemma, key, expected):
    generated = inflexions[(kind, lexicon)].generate(lemma, key)
    got = sorted(strip_length(w) for w in generated)
    want = [] if expected is None else sorted(expected.split("/"))
    assert got == want, f"{lemma} {key}: generated {got!r}, expected {want!r}"


@pytest.mark.parametrize("gender", "MFN")
def test_dual_cells_share_forms(gender):
    """Nominative, accusative and vocative dual are one form, and so are genitive and dative dual."""
    rules = _load_lexicon_yaml("noun_stemming.yaml")
    assert rules[f"AD{gender}"] == {"ref": f"ND{gender}"}
    assert rules[f"VD{gender}"] == {"ref": f"ND{gender}"}
    assert rules[f"DD{gender}"] == {"ref": f"GD{gender}"}
    assert isinstance(rules[f"ND{gender}"], list) and isinstance(rules[f"GD{gender}"], list)


def test_rule_files_have_no_duplicate_keys():
    """yaml.safe_load keeps only the last of a duplicate top-level key, so a second block for one dual key would silently drop the first."""
    from conftest import assert_no_duplicate_yaml_keys
    assert_no_duplicate_yaml_keys("noun_stemming.yaml", "adj_stemming.yaml")


def test_accent_dual_keys_match_the_rule_file():
    """The accent rule for the nominative, accusative and vocative dual names exactly the dual keys that the rule file has."""
    rules = _load_lexicon_yaml("noun_stemming.yaml")
    assert _NAV_DUAL == {key for key in rules if key[1:2] == "D" and key[0] in "NAV"}


def test_custom_lexicon_noun_stem_gets_dual_forms(tmp_path):
    """A `noun:` stem in a lexicon file of the user (a course YAML) reaches the dual keys, not only singular and plural."""
    entry = next(e for e in _ENTRIES if e["kind"] == "noun" and e["lexicon"] == "default" and "ADM" in e)
    unaccented = "".join(c for c in unicodedata.normalize("NFD", entry["lemma"]) if unicodedata.category(c) != "Mn")
    fake, stem = "β" + entry["lemma"][1:], "β" + unaccented[1:-1]   # a made-up lemma, so Pratt's own entry plays no part
    path = tmp_path / "course.yaml"
    path.write_text(yaml.safe_dump({fake: {"stems": {"noun": stem}}}, allow_unicode=True), encoding="utf-8")
    gi = load_noun_lexicons(["pratt", str(path)])
    for key in ("NDM", "GDM"):
        assert sorted(gi.generate(fake, key)) == ["β" + entry[key][1:]]
