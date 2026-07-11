"""Tests for the `byzantine` lexicon -- name resolution, additive merge with
other lexicons, and a correctness gate for its entries.

Like `morpheus` (see test_morpheus_lexicon.py), every byzantine entry is a
`forms:` block -- a verbatim attested surface form, not a stems:-based
generation. Every entry is deliberately NOT already reachable via any other
bundled lexicon's stem-based generation (see the lexicon file's own header for
how that was confirmed) -- the merge test below also documents that: without
`byzantine` merged in, the other lexicons only produce the classical
-ασι(ν)/-ομεν/-ον-style endings, never the attested innovative ones.
"""
import pytest
from greek_inflexion_eee import load_lexicons


@pytest.fixture(scope="module")
def gi():
    return load_lexicons("byzantine")


# --- name resolution ---------------------------------------------------------

def test_byzantine_name_resolves(gi):
    assert set(gi.generate("γιγνώσκω", "XAI.3P").keys()) == {"ἔγνωκαν"}


# --- additive merge: byzantine's override wins over the base lexicon's own ---
# --- classically-generated form for the same slot ----------------------------

def test_byzantine_merge_with_morphgnt_overrides_classical_ending():
    gi_base = load_lexicons("morphgnt")
    # morphgnt has γιγνώσκω only under the Koine spelling, and even then only
    # the classical -ασι(ν) ending -- documents the gap byzantine fills.
    assert "ἔγνωκαν" not in gi_base.generate("γινώσκω", "XAI.3P").keys()

    gi_merged = load_lexicons(["morphgnt", "byzantine"])
    assert "ἔγνωκαν" in gi_merged.generate("γιγνώσκω", "XAI.3P").keys()


def test_byzantine_merge_with_ltrg():
    gi_merged = load_lexicons(["ltrg", "byzantine"])
    # byzantine's override
    assert "ἔγνωκαν" in gi_merged.generate("γιγνώσκω", "XAI.3P").keys()
    # ltrg still provides its own unrelated verbs (παύω isn't in byzantine)
    assert gi_merged.generate("παύω", "PAI.1S").keys()


def test_byzantine_merge_does_not_disturb_lexicon_own_other_slots():
    """byzantine's ἄγω entry is IAI.3P only -- merging must not affect ltrg's
    own PAI.1S generation for the same lemma (form_override is per-slot, not
    per-lemma)."""
    gi_merged = load_lexicons(["ltrg", "byzantine"])
    assert "ἦγαν" in gi_merged.generate("ἄγω", "IAI.3P").keys()
    assert gi_merged.generate("ἄγω", "PAI.1S").keys()  # still ltrg's own


# --- correctness gate: exact attested forms -----------------------------------
# --- (see the lexicon file's own header for the verification discipline) -----

BYZANTINE_VERB_FORMS = [
    # John 17:7 / Colossians 2:1 -- cross-verified against the Westcott-Hort/
    # Nestle 1904 critical NT text, not just the 1887 OCR.
    ("γιγνώσκω", "XAI.3P", "ἔγνωκαν"),
    ("ὁράω", "XAI.3P", "ἑόρακαν"),
    # The remaining entries are the same -αν/-αμεν/-α leveling phenomenon,
    # sourced from the same Sophocles section, patristic/Byzantine citations.
    ("γίγνομαι", "XAI.3P", "γέγοναν"),
    ("δίδωμι", "XAI.3P", "δέδωκαν"),
    ("δοξάζω", "XAI.3P", "δεδόξακαν"),
    ("ἔρδω", "XAI.3P", "ἔοργαν"),
    ("ἔχω", "XAI.3P", "ἔσχηκαν"),
    ("ἔχω", "IAI.1P", "εἴχαμεν"),
    ("οἶδα", "XAI.3P", "οἶδαν"),
    ("πίνω", "XAI.3P", "πέπωκαν"),
    ("τηρέω", "XAI.3P", "τετήρηκαν"),
    ("φανερόω", "XAI.3P", "πεφανέρωκαν"),
    ("φρίσσω", "XAI.3P", "πέφρικαν"),
    ("ἄγω", "IAI.3P", "ἦγαν"),
    ("φέρω", "AAI.1S", "ἔφερα"),
    ("γράφω", "AAI.2S", "ἔγραψες"),
]


@pytest.mark.parametrize("lemma,code,expected", BYZANTINE_VERB_FORMS)
def test_byzantine_verb_form(gi, lemma, code, expected):
    assert expected in gi.generate(lemma, code).keys()


def test_byzantine_covers_all_expected_lemmas(gi):
    """Guards the lexicon's actual size -- catches an entry silently
    dropped (or one accidentally left out of the correctness gate above)."""
    expected_lemmas = {lemma for lemma, _, _ in BYZANTINE_VERB_FORMS}
    actual_lemmas = {lemma for lemma, _key in gi.form_override.keys()}
    assert expected_lemmas == actual_lemmas


# --- structural guard: every entry is forms:, never stems: -------------------

def test_all_entries_use_forms_not_stems():
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    data = _load_lexicon_yaml("byzantine_verbs_lexicon.yaml")
    for lemma, entry in data.items():
        assert "stems" not in entry, f"{lemma!r} has a stems: entry"
        assert "forms" in entry and entry["forms"], f"{lemma!r} has no forms:"


def test_byzantine_lexicon_has_15_lemmas():
    """Documents the lexicon's actual scope -- update deliberately, not by
    accident, if this changes."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    data = _load_lexicon_yaml("byzantine_verbs_lexicon.yaml")
    assert len(data) == 15
