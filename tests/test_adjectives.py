import pytest
from greek_inflexion_eee import GreekInflexion, load_adj_default


@pytest.fixture(scope="module")
def gi():
    return load_adj_default()


def test_2_1_2_uncontracted_masculine(gi):
    """ἀγαθός — 2-1-2 uncontracted — masc singular and plural forms."""
    assert "ἀγαθός" in gi.generate("ἀγαθός", "NSM")
    assert "ἀγαθόν" in gi.generate("ἀγαθός", "ASM")
    assert "ἀγαθοῦ" in gi.generate("ἀγαθός", "GSM")
    assert "ἀγαθῷ" in gi.generate("ἀγαθός", "DSM")
    assert "ἀγαθοί" in gi.generate("ἀγαθός", "NPM")
    assert "ἀγαθῶν" in gi.generate("ἀγαθός", "GPM")


def test_2_1_2_uncontracted_feminine(gi):
    """ἀγαθός — feminine forms follow 1st-declension η pattern."""
    assert "ἀγαθή" in gi.generate("ἀγαθός", "NSF")
    assert "ἀγαθῆς" in gi.generate("ἀγαθός", "GSF")
    assert "ἀγαθαί" in gi.generate("ἀγαθός", "NPF")


def test_2_1_2_uncontracted_neuter(gi):
    """ἀγαθός — neuter forms match 2nd-declension -ον pattern."""
    assert "ἀγαθόν" in gi.generate("ἀγαθός", "NSN")
    assert "ἀγαθά" in gi.generate("ἀγαθός", "NPN")


def test_2_1_2_contracted(gi):
    """χρυσοῦς — contracted forms."""
    assert "χρυσοῦς" in gi.generate("χρυσοῦς", "NSM")
    assert "χρυσῆ" in gi.generate("χρυσοῦς", "NSF")
    assert "χρυσοῦν" in gi.generate("χρυσοῦς", "NSN")


def test_2_2_two_termination(gi):
    """ἄδικος — masc and fem nominative singular are identical."""
    nsm = gi.generate("ἄδικος", "NSM")
    nsf = gi.generate("ἄδικος", "NSF")
    assert "ἄδικος" in nsm
    assert "ἄδικος" in nsf
    assert "ἄδικον" in gi.generate("ἄδικος", "NSN")


def test_3_1_3_participial_nt_stem(gi):
    """λύων — 3-1-3 participial (ντ-stem) — nom/gen singular all genders."""
    assert "λύων" in gi.generate("λύων", "NSM")
    assert "λύουσα" in gi.generate("λύων", "NSF")
    assert "λύον" in gi.generate("λύων", "NSN")
    assert "λύοντος" in gi.generate("λύων", "GSM")
    assert "λυούσης" in gi.generate("λύων", "GSF")
    assert "λύοντος" in gi.generate("λύων", "GSN")


def test_3_1_3_upsilon_stem(gi):
    """ταχύς — 3-1-3 upsilon-stem — masc/fem nominative singular."""
    assert "ταχύς" in gi.generate("ταχύς", "NSM")
    assert "ταχεῖα" in gi.generate("ταχύς", "NSF")
    assert "ταχύ" in gi.generate("ταχύς", "NSN")


def test_3_3_sigma_stem(gi):
    """ἀληθής — 3-3 sigma-stem — neuter nominative singular is ες-form."""
    assert "ἀληθής" in gi.generate("ἀληθής", "NSM")
    assert "ἀληθής" in gi.generate("ἀληθής", "NSF")
    assert "ἀληθές" in gi.generate("ἀληθής", "NSN")
    assert "ἀληθοῦς" in gi.generate("ἀληθής", "GSN")
    assert "ἀληθεῖ" in gi.generate("ἀληθής", "DSN")


def test_3_3_comparative(gi):
    """μείζων — 3-3 comparative — masc/fem share nom sg, neut is distinct."""
    assert "μείζων" in gi.generate("μείζων", "NSM")
    assert "μείζων" in gi.generate("μείζων", "NSF")
    assert "μεῖζον" in gi.generate("μείζων", "NSN")
    assert "μείζονος" in gi.generate("μείζων", "GSM")


def test_unknown_adjective_lemma(gi):
    """Unknown lemma returns empty dict."""
    result = gi.generate("ἄγνωστος_not_in_lexicon", "NSM")
    assert result == {}
