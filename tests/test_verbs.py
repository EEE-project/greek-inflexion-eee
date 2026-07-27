"""Verb tests converted from upstream data_test.py (pratt_test.yaml)."""
from pathlib import Path

import pytest
import yaml

from greek_accentuation.characters import strip_length
from greek_inflexion_eee import load_default, load_lexicons

_TEST_DATA = Path(__file__).parent / "test_data" / "pratt_test.yaml"


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
    return load_default()


@pytest.mark.parametrize("lemma,key,tags,expected", _CASES)
def test_verb_form(gi, lemma, key, tags, expected):
    generated = gi.generate(lemma, key, tags or None)
    got = sorted(strip_length(w) for w in generated)
    want = sorted(strip_length(w) for w in expected.split("/"))
    assert got == want, (
        f"{lemma} {key}: generated {set(generated.keys())!r}, expected {expected!r}"
    )


def test_generate_never_returns_unsubstituted_template_marker():
    """Regression test (2026-07-27): a stem whose principal-part marker
    (e.g. "{root}", "{athematic}") has no matching stemming rule for a
    given key falls through to the rule engine's own stem-unchanged
    default rule, leaking the literal marker into the "generated" surface
    form -- e.g. βαίνω's alternate perfect-system stem "ἐβεβα{root}" against
    YAI.1S (pluperfect active indicative 1st singular), which has {root}
    rules for plural persons but not singular. No legitimate Greek form
    ever contains "{"; generate() must never surface one. βαίνω lives in
    the homer lexicon, not the small pratt one load_default() loads."""
    gi_homer = load_lexicons("homer")
    generated = gi_homer.generate("βαίνω", "YAI.1S")
    assert generated
    assert all("{" not in form for form in generated)
    assert "ἐβεβήκη" in {strip_length(w) for w in generated}
