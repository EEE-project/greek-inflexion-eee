"""Tests for the `lsj` (LSJ, Classical Attic) lexicon — name resolution, additive merge,
merge-conflict semantics, and a per-lemma correctness gate.

The correctness gate encodes the expected Attic surface forms (Smyth-standard; the
overlapping nouns match the independently-authored homer_nouns spot-checks). It both
documents the intended output and guards against stemming regressions.
"""
import unicodedata
import pytest
from greek_inflexion_eee import load_lexicons, load_noun_lexicons


@pytest.fixture(scope="module")
def gi_verbs():
    return load_lexicons("lsj")


@pytest.fixture(scope="module")
def gi_nouns():
    return load_noun_lexicons("lsj")


# --- name resolution ---------------------------------------------------------

def test_lsj_verbs_name_resolves(gi_verbs):
    assert set(gi_verbs.generate("μένω", "PAI.1S").keys()) == {"μένω"}


def test_lsj_nouns_name_resolves(gi_nouns):
    assert "πόλεμος" in gi_nouns.generate("πόλεμος", "NSM").keys()


# --- additive merge with the teaching sets (the Odyssey tab bundle) ----------
# (these load merged bundles, so they build their own engines rather than the fixtures)

def test_lsj_verbs_merge_with_pratt_ltrg():
    gi = load_lexicons(["pratt", "ltrg", "lsj"])
    assert "μένω" in gi.generate("μένω", "PAI.1S").keys()   # from lsj
    assert gi.generate("λύω", "PAI.1S").keys()               # still from pratt/ltrg


def test_lsj_nouns_merge_with_pratt():
    gi = load_noun_lexicons(["pratt", "lsj"])
    assert "πόλεμος" in gi.generate("πόλεμος", "NSM").keys()  # from lsj
    assert "λόγος" in gi.generate("λόγος", "NSM").keys()      # from pratt


# --- merge-conflict semantics: ADDITIVE (union of stems), order-independent ---

def test_merge_conflict_is_additive(tmp_path):
    """A lemma defined in two loaded lexicons yields the UNION of both lexicons'
    forms, regardless of order — not last-wins or first-wins. This backstops the
    rule that `lsj` must not redefine pratt/ltrg lemmas (a conflict emits a
    spurious extra form rather than overriding)."""
    import yaml
    custom = {"λύω": {"stems": {"1-": "παυ"}}}       # distinct present stem
    p = tmp_path / "custom_verbs.yaml"
    p.write_text(yaml.dump(custom, allow_unicode=True), encoding="utf-8")

    forms_ab = set(load_lexicons(["pratt", str(p)]).generate("λύω", "PAI.1S").keys())
    forms_ba = set(load_lexicons([str(p), "pratt"]).generate("λύω", "PAI.1S").keys())

    assert forms_ab == forms_ba          # order-independent
    assert "παύω" in forms_ab            # custom stem survived (additive, not overridden)
    assert len(forms_ab) >= 2            # union, not override


# --- correctness gate: expected Attic surface forms --------------------------

ATTIC_VERB_FORMS = [
    ("μένω",   "PAI.1S", "μένω"),    ("μένω",   "FAI.1S", "μενῶ"),
    ("μένω",   "AAI.1S", "ἔμεινα"),  ("μένω",   "AAN",    "μεῖναι"),
    ("κλίνω",  "PAI.1S", "κλίνω"),   ("κλίνω",  "AAI.1S", "ἔκλινα"),
    ("σφάζω",  "FAI.1S", "σφάξω"),   ("σφάζω",  "AAI.1S", "ἔσφαξα"),
    ("δαμάζω", "AAI.1S", "ἐδάμασα"), ("πελάζω", "FAI.1S", "πελάσω"),
    ("φεύγω",  "AAI.1S", "ἔφυγον"),  ("φεύγω",  "AAN",     "φυγεῖν"),
    ("φεύγω",  "AAP.NSM", "φυγών"),
    ("πάσχω",  "AAI.1S", "ἔπαθον"),  ("πάσχω",  "AAN",     "παθεῖν"),
    ("πίνω",   "AAI.1S", "ἔπιον"),   ("πίνω",   "AAP.NSM", "πιών"),
    ("ἐσθίω",  "AAI.1S", "ἔφαγον"),  ("ἐσθίω",  "AAN",     "φαγεῖν"),
]


@pytest.mark.parametrize("lemma,code,expected", ATTIC_VERB_FORMS)
def test_lsj_verb_form(gi_verbs, lemma, code, expected):
    assert expected in gi_verbs.generate(lemma, code).keys()


ATTIC_NOUN_FORMS = [
    # citation + oblique with the proparoxytone accent shift under a long ultima
    ("πόλεμος",  "NSM", "πόλεμος"),  ("πόλεμος",  "GSM", "πολέμου"),
    ("πόλεμος",  "GPM", "πολέμων"),
    ("θάνατος",  "NSM", "θάνατος"),  ("θάνατος",  "GSM", "θανάτου"),
    ("ἄνθρωπος", "NSM", "ἄνθρωπος"), ("ἄνθρωπος", "GSM", "ἀνθρώπου"),
    ("ἄνθρωπος", "DSM", "ἀνθρώπῳ"),
    ("ὄλεθρος",  "GSM", "ὀλέθρου"),
    ("δόλος",    "NSM", "δόλος"),    ("δόλος",    "GSM", "δόλου"),
    ("μέγαρον",  "NSN", "μέγαρον"),  ("μέγαρον",  "GSN", "μεγάρου"),
    ("μέγαρον",  "NPN", "μέγαρα"),
    ("μῆλον",    "NSN", "μῆλον"),    ("μῆλον",    "GPN", "μήλων"),
]


@pytest.mark.parametrize("lemma,code,expected", ATTIC_NOUN_FORMS)
def test_lsj_noun_form(gi_nouns, lemma, code, expected):
    assert expected in gi_nouns.generate(lemma, code).keys()


# --- accent policy: no macron in any citation form (the λύω→λῡ́ω rejection class) ---

def test_no_macron_in_verb_citations(gi_verbs):
    verbs = ["μένω", "κλίνω", "σφάζω", "δαμάζω", "πελάζω",
             "φεύγω", "πάσχω", "πίνω", "ἐσθίω"]
    for lem in verbs:
        for form in gi_verbs.generate(lem, "PAI.1S").keys():
            assert "̄" not in unicodedata.normalize("NFD", form), \
                f"macron in citation {lem} -> {form}"


def test_no_macron_in_noun_citations(gi_nouns):
    nouns = ["δόλος", "θάνατος", "πόλεμος", "ἄνθρωπος", "μέγαρον", "μῆλον", "φύλλον"]
    for lem in nouns:
        for code in ("NSM", "NSN"):
            for form in gi_nouns.generate(lem, code).keys():
                assert "̄" not in unicodedata.normalize("NFD", form), \
                    f"macron in citation {lem} -> {form}"
