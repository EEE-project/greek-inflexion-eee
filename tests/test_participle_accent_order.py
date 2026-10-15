"""The accent of an active participle form must not depend on the order in which the engine returns the nominative singular forms of the other stems
(that order follows a set of stems, so it changed with PYTHONHASHSEED: λέγω gave εἰπάντας in one process and εἴπαντας in another)."""
import pytest
from inflexion.main import Inflexion

from greek_inflexion_eee import load_verb_lexicons

LEXICONS = ["pratt", "ltrg", "homer", "lxx", "morphgnt", "lsj", "byzantine"]


@pytest.fixture(scope="module")
def gi():
    return load_verb_lexicons(LEXICONS)


def reverse_engine_order(monkeypatch):
    """Make the engine return its forms in the opposite order (what another hash seed does)."""
    original = Inflexion.generate

    def reversed_generate(self, lemma, key, tag_filter=None):
        result = original(self, lemma, key, tag_filter)
        return dict(reversed(list(result.items())))

    monkeypatch.setattr(Inflexion, "generate", reversed_generate)


def _forms(gi, lemma, key):
    return set(gi.generate(lemma, key).keys())


@pytest.mark.parametrize("lemma, key, right, wrong", [
    ("λέγω", "AAP.APM", {"εἰπόντας", "εἴπαντας"}, {"εἰπάντας"}),
    ("προσφέρω", "AAP.APM", {"προσενέγκαντας", "προσενεγκόντας"}, {"προσενεγκάντας"}),
    ("ἐθέλω", "PAP.APM", {"θέλοντας", "ἐθέλοντας"}, {"θελόντας"}),
])
def test_participle_forms_follow_the_stem_that_makes_them(gi, lemma, key, right, wrong):
    forms = _forms(gi, lemma, key)
    assert right <= forms
    assert not forms & wrong


@pytest.mark.parametrize("lemma, key", [("λέγω", "AAP.APM"), ("προσφέρω", "AAP.APM"), ("ἐθέλω", "PAP.APM"), ("ἀπέχω", "AAP.GSM")])
def test_participle_forms_do_not_depend_on_the_engine_order(gi, lemma, key, monkeypatch):
    before = _forms(gi, lemma, key)
    reverse_engine_order(monkeypatch)
    assert _forms(gi, lemma, key) == before
