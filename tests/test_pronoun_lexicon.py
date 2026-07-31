"""Tests for the pronoun lexicon (pronoun_lexicon.yaml) -- structural
guard, per-lemma correctness gate, and defective-paradigm-specific guards
for the two structurally distinct pronoun tag shapes (adjective-like
Case+Number+Gender, and personal-pronoun Case+Number+Person). Mirrors
test_morpheus_lexicon.py's conventions for a forms:-only lexicon.

Most tests read the raw YAML directly via _load_lexicon_yaml instead of
going through a loader, matching test_morpheus_lexicon.py's own
structural guard (test_all_entries_use_forms_not_stems), which does the
same thing for the same reason. The load_pron_lexicons()-based tests
near the end of this file are the exception, exercising the loader
itself rather than the raw lexicon content.
"""
import pytest
from greek_inflexion_eee import load_pron_lexicons
from greek_inflexion_eee.fileformat import _load_lexicon_yaml

LEXICON_FILE = "pronoun_lexicon.yaml"


@pytest.fixture(scope="module")
def pronoun_data():
    return _load_lexicon_yaml(LEXICON_FILE)


# --- structural guard: every entry is forms:, never stems: -------------

def test_all_entries_use_forms_not_stems():
    """Every pronoun lexicon entry must be a forms: block -- matches
    test_morpheus_lexicon.py's identically-purposed guard for the same
    forms:-only-lexicon convention (byzantine/morpheus/odyssey_morpheus
    all follow it; pronoun_lexicon.yaml is the same shape for the same
    reason -- every lemma here is suppletive/irregular, not mechanically
    generatable from stems: + stemming.yaml rules)."""
    from conftest import assert_all_entries_use_forms
    assert_all_entries_use_forms(LEXICON_FILE)


def test_all_ten_lemmas_present(pronoun_data):
    """Regression guard for the exact scoped lemma set (excludes αὐτός,
    which lives in an adjective lexicon instead -- see section-01)."""
    expected = {"ἐγώ", "σύ", "οὗτος", "ἐκεῖνος", "ὅδε",
                "ὅς", "τίς", "τις", "ὅστις", "ἀλλήλων"}
    assert set(pronoun_data.keys()) == expected


# --- correctness gate: exact attested forms, Smyth's + Morpheus confirmed
# Each row is (lemma, tag, expected_form). Every row below was verified
# during implementation against Smyth's Grammar (paradigm shape, Part II
# §325-339) and independently cross-checked against Morpheus (per-form
# attestation, lemma+case+number(+gender/person) agreement) -- see
# pronoun_lexicon.yaml's own header comment for the full sourcing and
# verification-discipline note, including the documented, Smyth's-backed
# dual-syncretism judgment calls where Morpheus's own dual tagging is
# incomplete (under-tags feminine gender and sometimes only tags one of
# the two syncretic dual cases).
PRONOUN_FORMS = [
    # ἐγώ -- dual (Morpheus person-tag gap, lemma+case+number confirmed)
    ("ἐγώ", "ND1", "νώ"),
    ("ἐγώ", "AD1", "νώ"),
    ("ἐγώ", "GD1", "νῷν"),
    ("ἐγώ", "DD1", "νῷν"),
    # ἐγώ -- singular (enclitic/emphatic pair, plus epic variants added
    # 2026-07-27) and plural (= ἡμεῖς cells)
    ("ἐγώ", "NS1", ["ἐγώ", "ἐγὼν"]),
    ("ἐγώ", "GS1", ["ἐμοῦ", "μου", "μευ"]),
    ("ἐγώ", "DS1", ["ἐμοί", "μοι"]),
    ("ἐγώ", "AS1", ["ἐμέ", "με", "μ᾽"]),
    ("ἐγώ", "NP1", "ἡμεῖς"),
    ("ἐγώ", "GP1", "ἡμῶν"),
    ("ἐγώ", "DP1", "ἡμῖν"),
    ("ἐγώ", "AP1", "ἡμᾶς"),
    # σύ -- dual
    ("σύ", "ND2", "σφώ"),
    ("σύ", "AD2", "σφώ"),
    ("σύ", "GD2", "σφῷν"),
    ("σύ", "DD2", "σφῷν"),
    # σύ -- singular (enclitic/emphatic pair) and plural (= ὑμεῖς cells)
    ("σύ", "NS2", "σύ"),
    ("σύ", "GS2", ["σοῦ", "σου"]),
    ("σύ", "DS2", ["σοί", "σοι"]),
    ("σύ", "AS2", ["σέ", "σε"]),
    ("σύ", "NP2", "ὑμεῖς"),
    ("σύ", "GP2", "ὑμῶν"),
    ("σύ", "DP2", "ὑμῖν"),
    ("σύ", "AP2", "ὑμᾶς"),
    # οὗτος -- representative singular/dual/plural sample across genders
    ("οὗτος", "NSM", "οὗτος"),
    ("οὗτος", "NSF", "αὕτη"),
    ("οὗτος", "NSN", "τοῦτο"),
    ("οὗτος", "GSF", "ταύτης"),
    ("οὗτος", "ASM", "τοῦτον"),
    ("οὗτος", "NDM", "τούτω"),
    ("οὗτος", "GDM", "τούτοιν"),
    ("οὗτος", "NPM", "οὗτοι"),
    ("οὗτος", "NPN", "ταῦτα"),
    ("οὗτος", "APF", "ταύτᾱς"),
    # ἐκεῖνος -- representative sample
    ("ἐκεῖνος", "NSM", "ἐκεῖνος"),
    ("ἐκεῖνος", "NSF", "ἐκείνη"),
    ("ἐκεῖνος", "NSN", "ἐκεῖνο"),
    ("ἐκεῖνος", "GSM", "ἐκείνου"),
    ("ἐκεῖνος", "GSN", "ἐκείνου"),
    ("ἐκεῖνος", "DSF", "ἐκείνῃ"),
    ("ἐκεῖνος", "ASM", "ἐκεῖνον"),
    ("ἐκεῖνος", "ASN", "ἐκεῖνο"),
    ("ἐκεῖνος", "NDM", "ἐκείνω"),
    ("ἐκεῖνος", "GDM", "ἐκείνοιν"),
    ("ἐκεῖνος", "NPM", "ἐκεῖνοι"),
    ("ἐκεῖνος", "NPF", "ἐκεῖναι"),
    ("ἐκεῖνος", "NPN", "ἐκεῖνα"),
    ("ἐκεῖνος", "GPM", "ἐκείνων"),
    ("ἐκεῖνος", "DPM", "ἐκείνοις"),
    ("ἐκεῖνος", "APM", "ἐκείνους"),
    ("ἐκεῖνος", "APF", "ἐκείνᾱς"),
    ("ἐκεῖνος", "APN", "ἐκεῖνα"),
    # ὅδε -- representative sample (τ-stem + -δε, article-derived pattern)
    ("ὅδε", "NSM", "ὅδε"),
    ("ὅδε", "NSF", "ἥδε"),
    ("ὅδε", "NSN", "τόδε"),
    ("ὅδε", "GSM", "τοῦδε"),
    ("ὅδε", "GSN", "τοῦδε"),
    ("ὅδε", "DSF", "τῇδε"),
    ("ὅδε", "ASM", "τόνδε"),
    ("ὅδε", "ASN", "τόδε"),
    ("ὅδε", "NDM", "τώδε"),
    ("ὅδε", "GDM", "τοῖνδε"),
    ("ὅδε", "NPM", "οἵδε"),
    ("ὅδε", "NPF", "αἵδε"),
    ("ὅδε", "NPN", "τάδε"),
    ("ὅδε", "GPM", "τῶνδε"),
    ("ὅδε", "DPM", "τοῖσδε"),
    ("ὅδε", "APM", "τούσδε"),
    ("ὅδε", "APF", "τά̄σδε"),
    ("ὅδε", "APN", "τάδε"),
    # ὅς -- relative; NSN/DSN are the trickiest cells (neuter shares the
    # masculine dative ᾧ -- an early source-extraction pass mis-rendered
    # this as "ὅᾧ"; Morpheus confirms the standard ᾧ, matching every
    # other Greek relative/article-derived paradigm's masc=neut dative).
    ("ὅς", "NSM", "ὅς"),
    ("ὅς", "NSF", "ἥ"),
    ("ὅς", "NSN", "ὅ"),
    ("ὅς", "GSF", "ἧς"),
    ("ὅς", "DSM", "ᾧ"),
    ("ὅς", "DSN", "ᾧ"),
    ("ὅς", "NDM", "ὥ"),
    ("ὅς", "NPM", "οἵ"),
    ("ὅς", "NPN", "ἅ"),
    # DPM gained an epic variant (οἷσι) 2026-07-27
    ("ὅς", "DPM", ["οἷς", "οἷσι"]),
    # τίς -- interrogative, always accented; common-gender M/F share one
    # form (the "M"-labeled keys), N is distinct. No gender distinction
    # at all outside Nom/Acc, so GSN/DSN/GPN/DPN deliberately repeat
    # GSM/DSM/GPM/DPM (not a masc-only omission -- see the entry's own
    # header comment).
    ("τίς", "NSM", "τίς"),
    ("τίς", "NSN", "τί"),
    ("τίς", "GSM", "τίνος"),
    ("τίς", "GSN", "τίνος"),
    ("τίς", "DSM", "τίνι"),
    ("τίς", "DSN", "τίνι"),
    ("τίς", "NPM", "τίνες"),
    ("τίς", "GPM", "τίνων"),
    ("τίς", "GPN", "τίνων"),
    ("τίς", "DPM", "τίσι(ν)"),
    ("τίς", "DPN", "τίσι(ν)"),
    # τις -- indefinite, enclitic; distinct top-level entry from τίς
    # despite the near-identical spelling (accent-only minimal pair)
    ("τις", "NSM", "τις"),
    ("τις", "NSN", "τι"),
    ("τις", "GSM", "τινός"),
    ("τις", "GSN", "τινός"),
    ("τις", "DSM", "τινί"),
    ("τις", "DSN", "τινί"),
    ("τις", "NPM", "τινές"),
    ("τις", "GPM", "τινῶν"),
    ("τις", "GPN", "τινῶν"),
    ("τις", "DPM", "τισί(ν)"),
    ("τις", "DPN", "τισί(ν)"),
    # ὅστις -- indefinite relative; neuter ὅ τι is two words (ὅς's own
    # neuter ὅ + τις's own neuter τι, independently confirmed each).
    # Mirrors ὅς's own masc=neut Gen/Dat-singular syncretism (GSN=GSM,
    # DSN=DSM) and fully-3-way Gen-plural syncretism (GPN=GPF=GPM), plus
    # ὅς's genuinely distinct feminine dative (DSF/DPF, both freshly
    # Morpheus-confirmed, not copied from masc/neut).
    ("ὅστις", "NSM", "ὅστις"),
    ("ὅστις", "NSF", "ἥτις"),
    ("ὅστις", "NSN", "ὅ τι"),
    ("ὅστις", "ASN", "ὅ τι"),
    ("ὅστις", "GSM", "οὗτινος"),
    ("ὅστις", "GSN", "οὗτινος"),
    ("ὅστις", "DSM", "ᾧτινι"),
    ("ὅστις", "DSF", "ᾗτινι"),
    ("ὅστις", "DSN", "ᾧτινι"),
    ("ὅστις", "NPM", "οἵτινες"),
    ("ὅστις", "GPM", "ὧντινων"),
    ("ὅστις", "GPF", "ὧντινων"),
    ("ὅστις", "DPM", "οἷστισι(ν)"),
    ("ὅστις", "DPF", "αἷστισι(ν)"),
    # ἀλλήλων -- reciprocal, defective (oblique dual/plural only)
    ("ἀλλήλων", "GDM", "ἀλλήλοιν"),
    ("ἀλλήλων", "GDF", "ἀλλήλαιν"),
    ("ἀλλήλων", "ADM", "ἀλλήλω"),
    ("ἀλλήλων", "ADF", "ἀλλήλᾱ"),
    ("ἀλλήλων", "GPM", "ἀλλήλων"),
    # DPF gained an epic variant (ἀλλήλῃσι) 2026-07-27
    ("ἀλλήλων", "DPF", ["ἀλλήλαις", "ἀλλήλῃσι"]),
    ("ἀλλήλων", "APM", "ἀλλήλους"),
    ("ἀλλήλων", "APN", "ἄλληλα"),
]


@pytest.mark.parametrize("lemma,tag,expected", PRONOUN_FORMS)
def test_pronoun_form(pronoun_data, lemma, tag, expected):
    assert pronoun_data[lemma]["forms"][tag] == expected


# --- masc=neut Gen/Dat-singular syncretism: a general regression guard.
# Found during code review: τίς/τις/ὅστις initially shipped GSM/DSM but
# not the required GSN/DSN, breaking a pattern every other M/F/N lemma
# in this file follows consistently. A per-cell test alone can't catch
# "this key is silently missing" the way a structural guard can -- this
# asserts the RELATIONSHIP (whenever GSM/DSM exists, GSN/DSN must exist
# and match), not just specific values, so this exact bug class can't
# silently recur if a cell is added to one gender and not the other. -----

@pytest.mark.parametrize("lemma", ["οὗτος", "ἐκεῖνος", "ὅδε", "ὅς", "τίς", "τις", "ὅστις"])
def test_masc_neut_genitive_dative_singular_syncretism(pronoun_data, lemma):
    forms = pronoun_data[lemma]["forms"]
    for case in "GD":
        masc_key, neut_key = f"{case}SM", f"{case}SN"
        if masc_key in forms:
            assert neut_key in forms, f"{lemma!r} has {masc_key!r} but no {neut_key!r}"
            assert forms[neut_key] == forms[masc_key], (
                f"{lemma!r} {neut_key!r} ({forms[neut_key]!r}) should equal "
                f"{masc_key!r} ({forms[masc_key]!r})"
            )


# --- personal-pronoun dual: its own explicit test, not folded into the
# general parametrized list above (per the plan: "the one cell type no
# other lexicon in this project has needed to test before") -----------

def test_personal_pronoun_dual_forms(pronoun_data):
    """Dual number for 1st/2nd person. Note this is NOT the same as
    verbs' dual: ancient_greek_backend_eee/backend.py's _VERB_PERSONS
    list has no '1D' entry ('Ancient Greek has no first-person dual' --
    true for finite VERB conjugation), but the personal PRONOUN ἐγώ
    genuinely does have a confirmed 1st-person dual (νώ/νῷν) -- don't
    assume the verb precedent's omission carries over here."""
    assert pronoun_data["ἐγώ"]["forms"]["ND1"] == "νώ"
    assert pronoun_data["ἐγώ"]["forms"]["AD1"] == "νώ"
    assert pronoun_data["ἐγώ"]["forms"]["GD1"] == "νῷν"
    assert pronoun_data["ἐγώ"]["forms"]["DD1"] == "νῷν"
    assert pronoun_data["σύ"]["forms"]["ND2"] == "σφώ"
    assert pronoun_data["σύ"]["forms"]["AD2"] == "σφώ"
    assert pronoun_data["σύ"]["forms"]["GD2"] == "σφῷν"
    assert pronoun_data["σύ"]["forms"]["DD2"] == "σφῷν"


# --- reciprocal: defective-paradigm-specific guard ----------------------

def test_allelon_has_no_nominative_or_singular(pronoun_data):
    """ἀλλήλων is confirmed defective (Smyth's): oblique cases only (no
    Nom), dual+plural only (no Sing) -- assert the ABSENCE of these keys
    outright, not just presence of the oblique/dual/plural ones. The
    exact surviving cell set (which of G/D/A x D/P x M/F/N are actually
    attested) is determined during implementation -- don't assume all up
    to 18 non-excluded cells are attested; only ship what's confirmed."""
    forms = pronoun_data["ἀλλήλων"]["forms"]
    assert forms, "ἀλλήλων should have at least some attested cells"
    for key in forms:
        assert not key.startswith("N"), f"ἀλλήλων has unexpected nominative cell {key!r}"
        assert key[1] != "S", f"ἀλλήλων has unexpected singular cell {key!r}"


# --- τίς vs τις: distinct entries despite near-identical spelling ------

def test_interrogative_and_indefinite_are_distinct_entries(pronoun_data):
    """τίς (interrogative, accented) and τις (indefinite, enclitic) are
    two separate top-level lemma keys, not one lemma with two accent
    variants -- a standard Ancient Greek accent-based minimal pair."""
    assert pronoun_data["τίς"]["forms"]["NSM"] == "τίς"
    assert pronoun_data["τις"]["forms"]["NSM"] == "τις"
    assert pronoun_data["τίς"]["forms"] != pronoun_data["τις"]["forms"]


# --- load_pron_lexicons(): name resolution, matching load_noun_lexicons/
# load_adj_lexicons's existing pattern --------------------------------

def test_pron_lexicon_loads_without_error():
    """Name-resolution smoke test. lexicon_map is empty for
    load_pron_lexicons (no named variants exist yet), so the only names
    that don't raise are [] and absolute paths -- default_file is always
    included regardless."""
    gi = load_pron_lexicons([])
    assert "ἐγώ" in gi.generate("ἐγώ", "NS1")


def test_pron_lexicon_has_no_stemming_ruleset():
    """Pronoun forms are all forms:-overrides (see the module docstring's
    structural guard above) -- load_pron_lexicons() passes an empty
    stemming-file list, so .ruleset is None, not a real StemmingRuleSet."""
    gi = load_pron_lexicons([])
    assert gi.ruleset is None


def test_parse_raises_clear_error_without_a_ruleset():
    """.parse() walks .ruleset unconditionally; a pronoun-loaded instance
    has none (see test_pron_lexicon_has_no_stemming_ruleset above), so
    calling it must raise a clear, actionable error instead of leaking an
    AttributeError from deep inside the upstream inflexion.parse()."""
    gi = load_pron_lexicons([])
    with pytest.raises(ValueError, match="stemming rule set"):
        gi.parse("ἐγώ")


def test_unknown_lexicon_name_raises():
    """2026-07-31: no named pronoun lexicons have ever existed, so a bare
    name here was always inapplicable -- previously silently ignored
    (falling through to just the always-included default file), now
    raises like verb/noun/adjective (see fileformat.py's
    _resolve_lexicon_name() docstring)."""
    with pytest.raises(ValueError, match="nonexistent"):
        load_pron_lexicons(["nonexistent"])


def test_absolute_path_custom_lexicon_loaded(tmp_path):
    """Mirrors test_absolute_path_custom_lexicon_loaded in
    test_load_adj_lexicons.py / test_load_noun_lexicons.py. Uses a forms:
    block (not stems:), matching the pronoun lexicon's own forms:-only
    convention. Uses ἑαυτοῦ (reflexive "himself/herself/itself") -- a
    real pronoun, but NOT one of the 10 lemmas in pronoun_lexicon.yaml
    (see test_all_ten_lemmas_present's fixed set) -- because
    _load_pos_lexicons always includes default_file regardless of names,
    so reusing an already-shipped lemma (e.g. τις) would pass even if
    absolute-path loading were completely broken."""
    custom_yaml = tmp_path / "custom_pronouns.yaml"
    custom_yaml.write_text(
        "ἑαυτοῦ:\n    forms:\n        GSM: ἑαυτοῦ\n", encoding="utf-8",
    )
    gi = load_pron_lexicons([str(custom_yaml)])
    assert "ἑαυτοῦ" in gi.generate("ἑαυτοῦ", "GSM")
