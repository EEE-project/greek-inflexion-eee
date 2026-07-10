"""Tests for the `morpheus` lexicon — name resolution, additive merge with
other lexicons, override-vs-stems merge semantics, and a per-lemma
correctness gate.

Unlike lsj/pratt/homer (stem-based: `stems:` + endings, generated on demand),
every morpheus entry is a `forms:` block — a verbatim attested surface form,
independently confirmed via Morpheus. The correctness gate below encodes
that exact attested spelling; it both documents the intended output and
guards against a future re-generation accidentally changing it.
"""
import pytest
from greek_inflexion_eee import load_lexicons, load_noun_lexicons


@pytest.fixture(scope="module")
def gi_verbs():
    return load_lexicons("morpheus")


@pytest.fixture(scope="module")
def gi_nouns():
    return load_noun_lexicons("morpheus")


# --- name resolution ---------------------------------------------------------

def test_morpheus_verbs_name_resolves(gi_verbs):
    assert set(gi_verbs.generate("αἱρέω", "PAI.3S").keys()) == {"αἱρέει"}


def test_morpheus_nouns_name_resolves(gi_nouns):
    assert "Δία" in gi_nouns.generate("Ζεύς", "ASM").keys()


# --- additive merge with the corpus/teaching lexicons -------------------------

def test_morpheus_verbs_merge_with_homer():
    gi = load_lexicons(["homer", "morpheus"])
    assert "αἱρέει" in gi.generate("αἱρέω", "PAI.3S").keys()   # from morpheus
    assert gi.generate("μένω", "PAI.1S").keys()                 # still from homer


def test_morpheus_nouns_merge_with_pratt():
    gi = load_noun_lexicons(["pratt", "morpheus"])
    assert "Διός" in gi.generate("Ζεύς", "GSM").keys()   # from morpheus
    assert "λόγος" in gi.generate("λόγος", "NSM").keys()  # from pratt


# --- merge semantics: forms: is an OVERRIDE (last-loaded wins), unlike the ---
# --- additive union of stems: (see test_lsj_lexicon.py's equivalent test) ---

def test_form_override_is_last_loaded_wins(tmp_path):
    """Two lexicons both defining a forms: entry for the same (lemma, key):
    the later-loaded one wins outright -- not a union, unlike stems:. This is
    inherent to generate()'s form_override.get() check (a plain dict lookup),
    not something the loading order of morpheus vs. another lexicon changes:
    whichever lexicon's forms: entry for that exact key loads LAST is what a
    caller sees, regardless of which file it came from."""
    import yaml
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(yaml.dump({"φημί": {"forms": {"PAI.1S": "ΑΠΟ-Α"}}}, allow_unicode=True), encoding="utf-8")
    b.write_text(yaml.dump({"φημί": {"forms": {"PAI.1S": "ΑΠΟ-Β"}}}, allow_unicode=True), encoding="utf-8")

    gi_ab = load_lexicons([str(a), str(b)])
    gi_ba = load_lexicons([str(b), str(a)])
    assert gi_ab.generate("φημί", "PAI.1S").keys() == {"ΑΠΟ-Β"}
    assert gi_ba.generate("φημί", "PAI.1S").keys() == {"ΑΠΟ-Α"}


# --- correctness gate: exact attested forms (a representative sample) --------

MORPHEUS_VERB_FORMS = [
    # contract verb -- real uncontracted Epic forms, not the Attic-contracted
    # forms a stems:-based lexicon would mechanically generate
    ("αἱρέω",   "PAI.3S", "αἱρέει"),    ("αἱρέω",   "PMN",    "αἱρέεσθαι"),
    # deponent (middle-only) verb
    ("βούλομαι", "PMI.1S", "βούλομαι"), ("βούλομαι", "FMI.1S", "βουλήσομαι"),
    # athematic -μι compound
    ("καθίημι", "AAI.3S", "καθῆκεν"),
    # root-ablaut aorist, confirmed-buggy in the earlier stem-extraction
    # pipeline (λαθ instead of λανθαν) -- morpheus data sidesteps the
    # extraction step entirely, so there's nothing to get wrong the same way
    ("λανθάνω", "AAI.3S", "λάθε"),
    # dual number -- stored correctly even though AncientGreekBackend's own
    # paradigm-table builder doesn't currently enumerate dual (a limitation
    # of that consumer, not this lexicon; see ancient-greek-backend-eee)
    ("ῥύομαι",  "AMI.3D", "ῥυσάσθην"),
]


@pytest.mark.parametrize("lemma,code,expected", MORPHEUS_VERB_FORMS)
def test_morpheus_verb_form(gi_verbs, lemma, code, expected):
    assert expected in gi_verbs.generate(lemma, code).keys()


MORPHEUS_NOUN_FORMS = [
    # suppletive noun -- a stems:-based lexicon can only get this right with
    # extensive stem_overrides band-aids per cell (see the ancient-greek-
    # backend-eee fix); morpheus just has the real attested forms
    ("Ζεύς", "NSM", "Ζεύς"), ("Ζεύς", "GSM", "Διός"),
    ("Ζεύς", "DSM", "Διί"),  ("Ζεύς", "ASM", "Δία"),
    # genuinely dual-gender noun ("neighbor") -- both attested
    ("γείτων", "ASM", "γείτονα"), ("γείτων", "APF", "γείτονας"),
    # oxytone noun -- Epic genitive -οιο, not Attic-contracted -ου
    ("θεός", "GSM", "θεοῖο"),
]


@pytest.mark.parametrize("lemma,code,expected", MORPHEUS_NOUN_FORMS)
def test_morpheus_noun_form(gi_nouns, lemma, code, expected):
    assert expected in gi_nouns.generate(lemma, code).keys()


# --- structural guard: every entry is forms:, never stems: -------------------

def test_all_entries_use_forms_not_stems():
    """morpheus's whole reason to exist is verbatim attested forms with zero
    stem-extraction/re-inflection risk; a stems: entry slipping in would
    silently reintroduce that risk for whichever lemma it's on."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    for filename in ("morpheus_verbs_lexicon.yaml", "morpheus_nouns_lexicon.yaml"):
        data = _load_lexicon_yaml(filename)
        for lemma, entry in data.items():
            assert "stems" not in entry, f"{filename}: {lemma!r} has a stems: entry"
            assert "forms" in entry and entry["forms"], f"{filename}: {lemma!r} has no forms:"
