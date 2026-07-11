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
    # 2026-07-11: second pattern, 3rd plural imperfect/2nd-aorist active
    # in -οσαν (see the lexicon file's own header for the mining/
    # verification discipline for this pattern specifically).
    ("αἴρω", "AAI.3P", "ἤροσαν"),
    ("ἁμαρτάνω", "AAI.3P", "ἡμάρτοσαν"),
    ("λέγω", "AAI.3P", "εἴποσαν"),
    ("ἐσθίω", "AAI.3P", "ἐφάγοσαν"),
    ("εὑρίσκω", "AAI.3P", "εὕροσαν"),
    ("ἔχω", "IAI.3P", "εἴχοσαν"),
    ("ἔχω", "AAI.3P", "ἔσχοσαν"),
    ("κρίνω", "AAI.3P", "ἐκρίνοσαν"),
    ("λαμβάνω", "IAI.3P", "ἐλαμβάνοσαν"),
    ("λαμβάνω", "AAI.3P", "ἐλάβοσαν"),
    ("μανθάνω", "AAI.3P", "ἐμάθοσαν"),
    # ὁράω/AAI.3P has two attested variants (augmented and unaugmented) --
    # both checked as separate rows, same (lemma, code) pair.
    ("ὁράω", "AAI.3P", "ἴδοσαν"),
    ("ὁράω", "AAI.3P", "εἴδοσαν"),
    ("πίνω", "AAI.3P", "ἐπίοσαν"),
    ("φαίνω", "IAI.3P", "ἐφαίνοσαν"),
    ("φέρω", "IAI.3P", "ἐφέροσαν"),
    # 2026-07-11: third pattern, contract-verb imperfect 3rd plural in
    # -αοσαν->-ῶσαν / -εοσαν,-οοσαν->-ουσαν (see the lexicon file's own
    # header for the mining/verification discipline for this pattern).
    ("ἀνομέω", "IAI.3P", "ἠνομοῦσαν"),
    ("γεννάω", "IAI.3P", "ἐγεννῶσαν"),
    ("δολιόω", "IAI.3P", "ἐδολιοῦσαν"),
    ("ἐάω", "IAI.3P", "ἐῶσαν"),
    ("θορυβέω", "IAI.3P", "ἐθορυβοῦσαν"),
    ("θυμιάω", "IAI.3P", "ἐθυμιῶσαν"),
    ("νικάω", "IAI.3P", "ἐνικῶσαν"),
    ("νοέω", "IAI.3P", "ἐνοοῦσαν"),
    ("οἰκοδομέω", "IAI.3P", "ᾠκοδομοῦσαν"),
    ("ποιέω", "IAI.3P", "ἐποιοῦσαν"),
    # 2026-07-11: fourth pattern, -ασι replacing -ον/-αν in imperfect or
    # aorist active (see the lexicon file's own header for the mining/
    # verification discipline for this pattern).
    ("δίδωμι", "AAI.3P", "ἐδώκασι(ν)"),
    # λέγω/AAI.3P has two attested variants (-οσαν from the second pattern,
    # already a row above; -ασι from this one, added here).
    ("λέγω", "AAI.3P", "εἴπασι"),
    ("τίθημι", "IAI.3P", "ἐτιθέασι"),
    ("ποιέω", "AAI.3P", "ἐποιήσασι"),
    # 2026-07-11: fifth pattern, Optative 3rd plural -σαν (see the lexicon
    # file's own header for the mining/verification discipline).
    ("αἰνέω", "AAO.3P", "αἰνέσαισαν"),
    ("ποιέω", "AAO.3P", "ποιήσαισαν"),
    ("ψηλαφάω", "AAO.3P", "ψηλαφήσαισαν"),
    ("θηρεύω", "AAO.3P", "θηρεύσαισαν"),
    ("ἔρχομαι", "AAO.3P", "ἔλθοισαν"),
    ("ὄλλυμι", "AAO.3P", "ὀλέσαισαν"),
    ("λέγω", "AAO.3P", "εἴποισαν"),
    ("λέγω", "AAO.3P", "εἴπαισαν"),
    ("εὐλογέω", "AAO.3P", "εὐλογήσαισαν"),
    ("εὑρίσκω", "AAO.3P", "εὕροισαν"),
    # 2026-07-11: sixth pattern, Imperative -τωσαν/-σθωσαν (plus the
    # perfect-as-3rd-person-imperative sub-pattern) -- see the lexicon
    # file's own header for the mining/verification discipline.
    ("ἐπίσταμαι", "PMD.3P", "ἐπιστάσθωσαν"),
    ("εἶμι", "PAD.3P", "ἴτωσαν"),
    ("θεραπεύω", "AAD.3P", "θεραπευσάτωσαν"),
    ("δίδωμι", "AAD.3P", "δότωσαν"),
    ("ποιέω", "PAD.3P", "ποιείτωσαν"),
    ("διώκω", "PAD.3P", "διωκέτωσαν"),
    ("ἄγω", "PMD.3P", "ἀγέσθωσαν"),
    ("ἔχω", "PAD.3P", "ἐχέτωσαν"),
    ("εἰμί", "PAD.3P", "ἔστωσαν"),
    ("φωνέω", "XAD.3S", "πεφωνηκέτω"),
    ("θεωρέω", "XAD.3S", "τεθεωρηκέτω"),
    # 2026-07-11: seventh (last) pattern, Passive/Middle 2nd singular
    # original -σαι (see the lexicon file's own header for the mining/
    # verification discipline).
    ("βούλομαι", "PMI.2S", "βούλεσαι"),
    ("ἐπείγω", "PMI.2S", "ἐπείγεσαι"),
    ("ἐσθίω", "FMI.2S", "φάγεσαι"),
    ("ἰάομαι", "PMI.2S", "ἰᾶσαι"),
    ("καυχάομαι", "PMI.2S", "καυχᾶσαι"),
    ("κοιμάομαι", "PMI.2S", "κοιμᾶσαι"),
    ("κομίζω", "PMI.2S", "κομίζεσαι"),
    ("κτάομαι", "PMI.2S", "κτᾶσαι"),
    ("λυτρόω", "PMI.2S", "λυτροῦσαι"),
    ("ὀδυνάομαι", "PMI.2S", "ὀδυνᾶσαι"),
    ("πίνω", "PMI.2S", "πίεσαι"),
    ("πλανάω", "PMI.2S", "πλανᾶσαι"),
    ("πολεμέω", "PMI.2S", "πολεμεῖσαι"),
    ("στεφανόω", "PMI.2S", "στεφανοῦσαι"),
    ("φοβέομαι", "PMI.2S", "φοβεῖσαι"),
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


def test_no_duplicate_lemma_keys():
    """yaml.safe_load silently keeps only the last of a duplicate top-level
    key, so a lemma mined in an earlier pattern and extended in a later one
    (without noticing it already has a block further up the file) would
    silently lose its earlier entries -- caught once for ἐσθίω during
    authoring (see test_esthio_has_both_slots_from_separate_patterns).
    Parses the raw YAML source with a duplicate-key-aware loader rather than
    the standard one, which would just hide the problem."""
    import yaml
    from greek_inflexion_eee.fileformat import _DATA_PKG
    from importlib.resources import files

    class _DupeCheckLoader(yaml.SafeLoader):
        pass

    def _construct_mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            assert key not in seen, f"duplicate top-level key: {key!r}"
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)

    _DupeCheckLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

    resource = files(_DATA_PKG) / "byzantine_verbs_lexicon.yaml"
    with resource.open("r", encoding="utf-8") as f:
        yaml.load(f, Loader=_DupeCheckLoader)


def test_byzantine_lexicon_has_61_lemmas():
    """Documents the lexicon's actual scope -- update deliberately, not by
    accident, if this changes."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    data = _load_lexicon_yaml("byzantine_verbs_lexicon.yaml")
    assert len(data) == 61


def test_esthio_has_both_slots_from_separate_patterns():
    """Regression guard: ἐσθίω was added in the second pattern (AAI.3P) and
    extended in the seventh (FMI.2S) -- a duplicate top-level YAML key for
    the same lemma would have YAML silently keep only the last one, dropping
    AAI.3P. Caught once during authoring; guarded here so it can't regress."""
    from greek_inflexion_eee import load_lexicons
    gi = load_lexicons("byzantine")
    assert gi.form_override.get(("ἐσθίω", "AAI.3P")) == "ἐφάγοσαν"
    assert gi.form_override.get(("ἐσθίω", "FMI.2S")) == "φάγεσαι"
