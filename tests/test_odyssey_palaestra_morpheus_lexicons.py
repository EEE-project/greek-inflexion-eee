"""Tests for the four course-specific Morpheus lexicons: name resolution,
additive merge, a per-lemma correctness gate, and structural guards.

Distinct provenance from "morpheus" (see test_morpheus_lexicon.py) — these
start from course vocabulary (Odyssey: attested-in-text forms; Palaestra:
synthetic candidates from known declension patterns, Morpheus-verified) and
keep only cells the existing lexicon chain doesn't already generate. See
each lexicon file's own header for the full methodology.
"""
import pytest
from greek_inflexion_eee import load_lexicons, load_noun_lexicons, load_adj_lexicons


@pytest.fixture(scope="module")
def gi_odyssey_verbs():
    return load_lexicons(["homer", "odyssey_morpheus"])


@pytest.fixture(scope="module")
def gi_odyssey_nouns():
    return load_noun_lexicons(["homer", "odyssey_morpheus"])


@pytest.fixture(scope="module")
def gi_odyssey_adjs():
    return load_adj_lexicons("odyssey_morpheus")


@pytest.fixture(scope="module")
def gi_palaestra_nouns():
    return load_noun_lexicons("palaestra_morpheus")


# --- name resolution ---------------------------------------------------------

def test_odyssey_morpheus_verbs_name_resolves(gi_odyssey_verbs):
    assert "βάλλον" in gi_odyssey_verbs.generate("βάλλω", "IAI.1S").keys()


def test_odyssey_morpheus_nouns_name_resolves(gi_odyssey_nouns):
    assert "βοῦς" in gi_odyssey_nouns.generate("βοῦς", "NPM").keys()


def test_odyssey_morpheus_adjs_name_resolves(gi_odyssey_adjs):
    assert "πολύτροπον" in gi_odyssey_adjs.generate("πολύτροπος", "ASM").keys()


def test_palaestra_morpheus_name_resolves(gi_palaestra_nouns):
    assert "σκιά" in gi_palaestra_nouns.generate("σκιά", "NSF").keys()


# --- additive merge ------------------------------------------------------

def test_odyssey_morpheus_verbs_merge_with_homer():
    gi = load_lexicons(["homer", "odyssey_morpheus"])
    assert "βάλλον" in gi.generate("βάλλω", "IAI.3P").keys()   # from odyssey_morpheus
    assert gi.generate("μένω", "PAI.1S").keys()                 # still from homer


def test_palaestra_morpheus_usable_standalone():
    """Unlike the odyssey_morpheus lexicons (documented cells only, meant to
    merge alongside a full paradigm source), palaestra_morpheus nouns were
    entirely absent from the existing chain -- this lexicon alone covers
    their full 8-cell paradigm."""
    gi = load_noun_lexicons("palaestra_morpheus")
    cells = {"NSM", "ASM", "GSM", "DSM", "NPM", "APM", "GPM", "DPM"}
    generated_cells = set()
    for cell in cells:
        if gi.generate("δεσπότης", cell):
            generated_cells.add(cell)
    assert generated_cells == cells


# --- correctness gate: exact attested/verified forms (a representative sample) --

ODYSSEY_VERB_FORMS = [
    # archaic bare-stem vocative participle, distinct from the nominative-
    # leveled -ων vocative a regularized Attic teaching paradigm would show
    ("βάλλω", "PAP.VSM", "βάλλον"),
    # multi-value cell: two independently Morpheus-confirmed 3rd-plural
    # imperfect readings for εἰμί
    ("εἰμί", "IAI.3P", "ἔσαν"), ("εἰμί", "IAI.3P", "ἦν"),
]


@pytest.mark.parametrize("lemma,code,expected", ODYSSEY_VERB_FORMS)
def test_odyssey_morpheus_verb_form(gi_odyssey_verbs, lemma, code, expected):
    assert expected in gi_odyssey_verbs.generate(lemma, code).keys()


ODYSSEY_NOUN_FORMS = [
    # common-gender noun -- same surface form serves as both masculine and
    # feminine nominative plural
    ("βοῦς", "NPM", "βοῦς"), ("βοῦς", "NPF", "βοῦς"),
]


@pytest.mark.parametrize("lemma,code,expected", ODYSSEY_NOUN_FORMS)
def test_odyssey_morpheus_noun_form(gi_odyssey_nouns, lemma, code, expected):
    assert expected in gi_odyssey_nouns.generate(lemma, code).keys()


ODYSSEY_ADJ_FORMS = [
    # suppletive adjective -- distinct stems by gender/case, not a stems:-
    # based generator's regular pattern
    ("πολύς", "GPM", "πολλῶν"),
    ("πολύς", "NSN", "πολλόν"),
]


@pytest.mark.parametrize("lemma,code,expected", ODYSSEY_ADJ_FORMS)
def test_odyssey_morpheus_adj_form(gi_odyssey_adjs, lemma, code, expected):
    assert expected in gi_odyssey_adjs.generate(lemma, code).keys()


PALAESTRA_NOUN_FORMS = [
    # 3rd declension -ις/-εως (πόλις-type), identified from the course's own
    # stated genitive "ἡ δύσις, -εως"
    ("δύσις", "GSF", "δύσεως"), ("δύσις", "DPF", "δύσεσι(ν)"),
    # compound -ος agent-noun the course glosses as a noun (article ὁ) that
    # Morpheus's own citation dictionary classes as adjective-used-
    # substantively
    ("δοῦλος", "NPM", "δοῦλοι"),
]


@pytest.mark.parametrize("lemma,code,expected", PALAESTRA_NOUN_FORMS)
def test_palaestra_morpheus_noun_form(gi_palaestra_nouns, lemma, code, expected):
    assert expected in gi_palaestra_nouns.generate(lemma, code).keys()


# --- structural guards --------------------------------------------------------

_NEW_LEXICON_FILES = (
    "odyssey_morpheus_verbs_lexicon.yaml",
    "odyssey_morpheus_nouns_lexicon.yaml",
    "odyssey_morpheus_adjs_lexicon.yaml",
    "palaestra_morpheus_nouns_lexicon.yaml",
)


def test_all_entries_use_forms_not_stems():
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    for filename in _NEW_LEXICON_FILES:
        data = _load_lexicon_yaml(filename)
        for lemma, entry in data.items():
            assert "stems" not in entry, f"{filename}: {lemma!r} has a stems: entry"
            assert "forms" in entry and entry["forms"], f"{filename}: {lemma!r} has no forms:"


def test_no_duplicate_lemma_keys():
    """yaml.safe_load silently keeps only the last of a duplicate top-level
    key (see test_byzantine_lexicon.py's identical guard, added after that
    file actually hit this bug). These 4 files are machine-generated from a
    Python dict so the bug class can't occur at generation time, but a
    future hand-edit could reintroduce it -- keep the guard."""
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

    for filename in _NEW_LEXICON_FILES:
        resource = files(_DATA_PKG) / filename
        with resource.open("r", encoding="utf-8") as f:
            yaml.load(f, Loader=_DupeCheckLoader)


def test_lexicon_sizes():
    """Documents each lexicon's actual scope -- update deliberately, not by
    accident, if this changes."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    assert len(_load_lexicon_yaml("odyssey_morpheus_verbs_lexicon.yaml")) == 56
    assert len(_load_lexicon_yaml("odyssey_morpheus_nouns_lexicon.yaml")) == 59
    assert len(_load_lexicon_yaml("odyssey_morpheus_adjs_lexicon.yaml")) == 57
    assert len(_load_lexicon_yaml("palaestra_morpheus_nouns_lexicon.yaml")) == 26


def test_dialect_mismatched_cells_excluded():
    """The original build (query_morpheus.py) never captured Morpheus's own
    `dial` field, so 5 cells shipped from Doric/Doric-Aeolic-only readings --
    inappropriate for an Epic/Ionic (Homeric) course lexicon, caught via a
    follow-up audit against the raw cached responses. λανθάνω and ἠώς each
    keep their other, dialect-neutral cell for the same surface form;
    ὑλήεις had no other cell and was dropped entirely (49 -> 48 adjective
    lemmas)."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml
    verbs = _load_lexicon_yaml("odyssey_morpheus_verbs_lexicon.yaml")
    assert "PMS.3S" not in verbs["λανθάνω"]["forms"]
    assert verbs["λανθάνω"]["forms"]["APS.3S"] == "λάθηται"

    nouns = _load_lexicon_yaml("odyssey_morpheus_nouns_lexicon.yaml")
    assert "NDF" not in nouns["ἠώς"]["forms"]
    assert "VDF" not in nouns["ἠώς"]["forms"]
    assert nouns["ἠώς"]["forms"]["ASF"] == "ἠῶ"

    adjs = _load_lexicon_yaml("odyssey_morpheus_adjs_lexicon.yaml")
    assert "ὑλήεις" not in adjs


def test_cross_lemma_contamination_excluded():
    """A second, more serious bug found by the same audit: the original
    build script (odyssey_gaps.py) iterated over *every* Morpheus reading
    for a surface form without re-filtering to the ones whose lemma matched
    the target lemma before computing a tag code -- so a tag code correctly
    derived from lemma A's grammatical features could get shipped under
    lemma B's entry, if both happened to share a surface form (e.g. Morpheus
    returns both κέω-optative and κεῖμαι-indicative for "κείμεθ᾽"; the
    optative tag was wrongly filed under κεῖμαι, which has no optative
    reading at all). 26 cells across 21 lemmas were affected (8 verb cells /
    6 lemmas, 15 noun cells / 7 lemmas, 3 adjective cells / 2 lemmas);
    2 lemmas lost all their cells and were dropped entirely from each of
    verbs (ἐπίσταμαι, ῥύομαι: 58 -> 56) and nouns (μόρος, πούς: 60 -> 58).
    Two more πολύς cells (NSF/VSF) turned out to be a second, unrelated
    Doric-Aeolic dial mismatch missed by the first audit pass, which only
    checked entries where lemma+tag both already matched cleanly."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml

    verbs = _load_lexicon_yaml("odyssey_morpheus_verbs_lexicon.yaml")
    assert "ἐπίσταμαι" not in verbs
    assert "ῥύομαι" not in verbs
    assert "PMO.1P" not in verbs["κεῖμαι"]["forms"]
    assert verbs["κεῖμαι"]["forms"]["PMI.1P"] == "κείμεθ᾽"
    assert "IAI.3S" not in verbs["φεύγω"]["forms"]
    assert "API.1P" not in verbs["ἐπιβαίνω"]["forms"]
    assert verbs["ἐπιβαίνω"]["forms"] == {"PAN": "ἐπιβαινέμεν"}

    nouns = _load_lexicon_yaml("odyssey_morpheus_nouns_lexicon.yaml")
    assert "μόρος" not in nouns
    assert "πούς" not in nouns
    # ζυγόν and ἱστίον are unambiguously neuter -- the 5 feminine-case cells
    # each shipped (belonging to unrelated lemmas ζυγή / ἑστία) are gone;
    # their genuine neuter cells survive untouched.
    assert set(nouns["ζυγόν"]["forms"]) == {"APN", "NPN", "VPN"}
    assert set(nouns["ἱστίον"]["forms"]) == {"NPN", "VPN"}
    assert "NSM" not in nouns["ναῦς"]["forms"]  # was ναός's reading, wrong gender too
    assert "VSF" not in nouns["ἅλς"]["forms"]
    assert "DPN" not in nouns["ἐρετμός"]["forms"]

    adjs = _load_lexicon_yaml("odyssey_morpheus_adjs_lexicon.yaml")
    assert "NSF" not in adjs["πολύς"]["forms"]
    assert "VSF" not in adjs["πολύς"]["forms"]
    assert "ASM" not in adjs["γλυκύς"]["forms"]
    assert "NPF" not in adjs["ἠέριος"]["forms"]
    assert "VPF" not in adjs["ἠέριος"]["forms"]
    assert set(adjs["ἠέριος"]["forms"]) == {"NPM", "VPM"}


# --- gap-mining addition (2026-07-12): remaining Odyssey zero-coverage lemmas -

def test_odyssey_zero_coverage_gap_fill_added():
    """A fresh sweep of all 5 Odyssey lessons' vocab against the full 8-lexicon
    chain (after the 2026-07-11 audit fixes above) found only 13 remaining
    zero-coverage (lemma, pos) pairs -- down from 73 before odyssey_morpheus
    existed. 9 were genuine Epic-appropriate Morpheus-confirmed gaps (verified
    against the actual Homeric line for the 3 gender-ambiguous ones: ἕλικας
    βοῦς is genuinely common-gender so both APM/APF are kept; ἐϋκνήμιδες
    ἑταῖροι and ἐρίηρας ἑταίρους are both unambiguously masculine). 3 more
    (τρηχύς, ἐρίηρες, κληίς) are deliberate-alias cases (Morpheus's own
    preferred hdwd differs -- τραχύς, ἐρίηρος, κλείς respectively -- but the
    dial tag confirms the reading is genuinely Epic/neutral); logged in
    tools/morpheus/README.md's alias list. One candidate (ὑλήεις, attested
    form ὑλήεσσα) was investigated and left OUT -- Morpheus confirms it only
    for Doric dial, the same failure mode already caught and removed once
    from this same lexicon on 2026-07-11.

    The remaining 2 of the original 13 are NOT lexicon gaps at all: λαθέσθαι
    and οἰχόμενοι are course-TSV lemma-column bugs (the inflected form was
    entered as the lemma) -- λανθάνω already has the exact needed form
    (AMN: λαθέσθαι); οἴχομαι needs a backend fix (plural participle cells
    aren't enumerated by _build_verb_paradigm at all), not lexicon data.
    """
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml

    adjs = _load_lexicon_yaml("odyssey_morpheus_adjs_lexicon.yaml")
    assert adjs["πίων"]["forms"]["ASM"] == "πίονα"
    assert adjs["τρηχύς"]["forms"]["NSF"] == "τρηχεῖα"
    assert adjs["ἀμφιέλισσα"]["forms"]["NPF"] == "ἀμφιέλισσαι"
    assert adjs["ἐρίηρες"]["forms"]["APM"] == "ἐρίηρας"
    assert adjs["ἐϋκνήμις"]["forms"]["NPM"] == "ἐϋκνήμιδες"
    assert adjs["ἕλιξ"]["forms"]["APM"] == "ἕλικας"
    assert adjs["ἕλιξ"]["forms"]["APF"] == "ἕλικας"
    assert adjs["ἐυπλόκαμος"]["forms"]["NSF"] == "ἐυπλόκαμος"
    assert adjs["τρίτος"]["forms"]["ASN"] == "τρίτον"
    assert adjs["τρίτατος"]["forms"]["ASN"] == "τρίτατον"
    assert "ὑλήεις" not in adjs  # Doric-only, deliberately left uncovered

    nouns = _load_lexicon_yaml("odyssey_morpheus_nouns_lexicon.yaml")
    assert nouns["κληίς"]["forms"]["DPF"] == "κληῖσι"
