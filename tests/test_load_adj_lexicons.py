"""Tests for load_adj_lexicons()."""
import pytest
from greek_inflexion_eee import load_adj_lexicons

PRATT_ADJS = ["ἀγαθός", "ἄδικος", "δίκαιος", "αὐτός"]


@pytest.fixture(scope="module")
def gi():
    return load_adj_lexicons("pratt")


@pytest.mark.parametrize("lemma", PRATT_ADJS)
def test_pratt_adj_has_forms(gi, lemma):
    all_keys = [c + n + g for c in "NGDA" for n in "SP" for g in "MFN"]
    assert any(gi.generate(lemma, k) for k in all_keys), f"{lemma!r} produced no forms"


@pytest.mark.parametrize("lemma,key,expected", [
    ("ἀγαθός", "NSM", "ἀγαθός"),
    ("ἀγαθός", "NSF", "ἀγαθή"),
    ("ἀγαθός", "NSN", "ἀγαθόν"),
    ("ἄδικος", "GSM", "ἀδίκου"),
    ("αὐτός", "NSM", "αὐτός"),
    ("αὐτός", "GSM", "αὐτοῦ"),
    ("αὐτός", "NSF", "αὐτή"),
    ("αὐτός", "GSF", "αὐτῆς"),
    ("αὐτός", "NSN", "αὐτό"),
    ("αὐτός", "GSN", "αὐτοῦ"),
    ("αὐτός", "ASN", "αὐτό"),
    ("αὐτός", "DSN", "αὐτῷ"),
    ("αὐτός", "NPM", "αὐτοί"),
])
def test_spot_check(gi, lemma, key, expected):
    forms = gi.generate(lemma, key)
    assert expected in forms, f"{lemma} {key}: got {set(forms)!r}, expected {expected!r}"


def test_unknown_lexicon_name_raises():
    """2026-07-31: previously silently skipped (see the module-level
    _resolve_lexicon_name() docstring for why that changed)."""
    with pytest.raises(ValueError, match="nonexistent"):
        load_adj_lexicons(["pratt", "nonexistent"])


@pytest.mark.parametrize("names", ["pratt", ["pratt"]])
def test_string_and_list_equivalent(names):
    gi = load_adj_lexicons(names)
    assert "ἀγαθός" in gi.generate("ἀγαθός", "NSM")


def test_absolute_path_custom_lexicon_loaded(tmp_path):
    custom_yaml = tmp_path / "custom_adjs.yaml"
    custom_yaml.write_text(
        "νεαρός:\n    stems:\n        M: νεαρο\n        F: νεαρα\n        N: νεαρο\n",
        encoding="utf-8",
    )
    gi = load_adj_lexicons(["pratt", str(custom_yaml)])
    assert "νεαρός" in gi.generate("νεαρός", "NSM")
