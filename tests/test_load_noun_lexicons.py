"""Tests for load_noun_lexicons() and the homer_nouns_lexicon."""
import pytest
from greek_inflexion_eee import load_noun_lexicons


HOMER_NOUNS = [
    "θάνατος", "μόρος", "ἄνεμος", "ἑταῖρος",  # 2nd decl masc
    "νῆσος", "ἤπειρος", "μάχη",               # 2nd/1st decl fem
    "μῆλον", "φύλλον",                          # 2nd decl neut
    "αἶσα",                                      # 1st decl fem α-stem
    "ἄλγος", "ἄνθος",                           # 3rd decl neut σ-stem
    "κτῆμα",                                     # 3rd decl neut τ-stem
    "γείτων",                                    # 3rd decl masc ν-stem
    "βοῦς",                                      # irregular
]

# spot-check: (lemma, CSG_key, expected_form)
SPOT_CHECKS = [
    ("θάνατος", "NSM", "θάνατος"),
    ("θάνατος", "GSM", "θανάτου"),
    ("μάχη",    "NSF", "μάχη"),
    ("μάχη",    "GSF", "μάχης"),
    ("μάχη",    "DSF", "μάχῃ"),
    ("μῆλον",   "NSN", "μῆλον"),
    ("μῆλον",   "GPN", "μήλων"),
    ("ἄλγος",   "NSN", "ἄλγος"),
    ("ἄλγος",   "GPN", "ἀλγῶν"),
    ("κτῆμα",   "NSN", "κτῆμα"),
    ("κτῆμα",   "GPN", "κτημάτων"),
    ("γείτων",  "NSM", "γείτων"),
    ("γείτων",  "GSM", "γείτονος"),
    ("γείτων",  "NPM", "γείτονες"),
    ("βοῦς",    "NSM", "βοῦς"),
    ("βοῦς",    "GPM", "βοῶν"),
]


@pytest.fixture(scope="module")
def gi():
    return load_noun_lexicons("homer")


@pytest.mark.parametrize("names", ["pratt", "homer"])
def test_pratt_nouns_present(names):
    # pratt's λόγος must be reachable whether "pratt" is loaded alone or as
    # part of a broader set (e.g. "homer", which composes pratt as a base)
    gi = load_noun_lexicons(names)
    forms = gi.generate("λόγος", "NSM")
    assert "λόγος" in forms


@pytest.mark.parametrize("lemma", HOMER_NOUNS)
def test_homer_noun_has_forms(gi, lemma):
    all_keys = [c + n + g for c in "NGDAV" for n in "SP" for g in "MFN"]
    any_form = any(gi.generate(lemma, k) for k in all_keys)
    assert any_form, f"{lemma!r} produced no forms"


@pytest.mark.parametrize("lemma,key,expected", SPOT_CHECKS)
def test_spot_check(gi, lemma, key, expected):
    forms = gi.generate(lemma, key)
    assert expected in forms, f"{lemma} {key}: got {set(forms)!r}, expected {expected!r}"


def test_unknown_lexicon_name_ignored():
    gi = load_noun_lexicons(["homer", "nonexistent"])
    forms = gi.generate("θάνατος", "NSM")
    assert "θάνατος" in forms


def test_absolute_path_custom_lexicon_loaded(tmp_path):
    custom_yaml = tmp_path / "custom_nouns.yaml"
    custom_yaml.write_text("ἀγρός:\n    stems:\n        noun: ἀγρο\n", encoding="utf-8")
    gi = load_noun_lexicons(["pratt", str(custom_yaml)])
    forms = gi.generate("ἀγρός", "NSM")
    assert "ἀγρός" in forms
