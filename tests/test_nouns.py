"""Noun tests converted from upstream noun_data_test.py (pratt_noun_test.yaml)."""
from pathlib import Path

import pytest
import yaml

from greek_accentuation.characters import strip_length
from greek_inflexion_eee import load_noun_default

_TEST_DATA = Path(__file__).parent / "test_data" / "pratt_noun_test.yaml"


def _load_cases():
    with open(_TEST_DATA, encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    cases = []
    for entry in entries:
        entry.pop("source", None)
        entry.pop("test_length", None)
        lemma = entry.pop("lemma")
        tags = frozenset(entry.pop("tags", []))
        for key, expected in entry.items():
            cases.append((lemma, key, tags, expected))
    return cases


_CASES = _load_cases()


@pytest.fixture(scope="module")
def gi():
    return load_noun_default()


@pytest.mark.parametrize("lemma,key,tags,expected", _CASES)
def test_noun_form(gi, lemma, key, tags, expected):
    generated = gi.generate(lemma, key, tags or None)
    got = sorted(strip_length(w) for w in generated)
    want = sorted(strip_length(w) for w in expected.split("/"))
    assert got == want, (
        f"{lemma} {key}: generated {set(generated.keys())!r}, expected {expected!r}"
    )
