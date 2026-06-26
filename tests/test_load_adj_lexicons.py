"""Tests for load_adj_lexicons()."""
import pytest
from greek_inflexion_eee import load_adj_lexicons

PRATT_ADJS = ["ἀγαθός", "ἄδικος", "δίκαιος"]


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
])
def test_spot_check(gi, lemma, key, expected):
    forms = gi.generate(lemma, key)
    assert expected in forms, f"{lemma} {key}: got {set(forms)!r}, expected {expected!r}"


def test_unknown_lexicon_name_ignored():
    gi = load_adj_lexicons(["pratt", "nonexistent"])
    assert "ἀγαθός" in gi.generate("ἀγαθός", "NSM")


@pytest.mark.parametrize("names", ["pratt", ["pratt"]])
def test_string_and_list_equivalent(names):
    gi = load_adj_lexicons(names)
    assert "ἀγαθός" in gi.generate("ἀγαθός", "NSM")
