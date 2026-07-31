"""Tests for load_verb_lexicons() — named lexicons and custom file paths."""
import pytest
from greek_inflexion_eee import load_verb_lexicons


def test_pratt_string_shortcut():
    gi = load_verb_lexicons("pratt")
    assert set(gi.generate("λύω", "PAI.1S").keys())


def test_homer_legw_imperative_2s():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("λέγω", "PAD.2S").keys()) == {"λέγε"}


def test_homer_legw_imperative_2p():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("λέγω", "PAD.2P").keys()) == {"λέγετε"}


def test_homer_akouo_imperative_2s():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("ἀκούω", "PAD.2S").keys()) == {"ἄκουε"}


def test_homer_akouo_imperative_2p():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("ἀκούω", "PAD.2P").keys()) == {"ἀκούετε"}


def test_homer_anagignwskw_imperative_2s():
    gi = load_verb_lexicons("homer")
    result = set(gi.generate("ἀναγιγνώσκω", "PAD.2S").keys())
    assert result  # present stem now bundled
    assert any("γνωσκ" in f for f in result)


def test_homer_anagignwskw_imperative_2p():
    gi = load_verb_lexicons("homer")
    result = set(gi.generate("ἀναγιγνώσκω", "PAD.2P").keys())
    assert result


def test_homer_pauō_imperative_2s():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("παύω", "PAD.2S").keys()) == {"παῦε"}


def test_homer_pauō_imperative_2p():
    gi = load_verb_lexicons("homer")
    assert set(gi.generate("παύω", "PAD.2P").keys()) == {"παύετε"}


def test_lxx_loads():
    gi = load_verb_lexicons("lxx")
    assert set(gi.generate("λέγω", "PAI.1S").keys())


def test_morphgnt_loads():
    gi = load_verb_lexicons("morphgnt")
    assert set(gi.generate("λέγω", "PAI.1S").keys())


def test_merge_homer_lxx():
    gi = load_verb_lexicons(["homer", "lxx"])
    assert set(gi.generate("λέγω", "PAD.2S").keys()) == {"λέγε"}
    assert set(gi.generate("ἀκούω", "PAD.2S").keys()) == {"ἄκουε"}


def test_merge_all_three():
    gi = load_verb_lexicons(["homer", "lxx", "morphgnt"])
    assert set(gi.generate("λέγω", "PAD.2S").keys())


def test_custom_file_path(tmp_path):
    import yaml
    custom = {"λύω": {"stems": {"1-": "λῡ", "2-": "λῡσ", "3-": "λῡσ", "3+": "ἐλυσ",
                                "4-": "λελυκ", "5-": "λελυ", "6-": "λυθ",
                                "6+": "ἐλυθ", "7-": "λυθησ"}}}
    p = tmp_path / "custom.yaml"
    p.write_text(yaml.dump(custom, allow_unicode=True), encoding="utf-8")
    gi = load_verb_lexicons(str(p))
    assert set(gi.generate("λύω", "PAI.1S").keys())


def test_unknown_name_raises():
    """2026-07-31: previously fell through to _load_lexicon_yaml() as a
    literal package-resource filename and crashed with a confusing raw
    FileNotFoundError. Now raises a clear, intentional ValueError naming
    the bad lexicon -- see _resolve_lexicon_name()'s own docstring for why
    (this exact silent-degradation-turned-confusing-crash shape is what
    happened in practice when "odyssey_morpheus" was removed from the
    registry while callers still referenced it by name)."""
    with pytest.raises(ValueError, match="nonexistent_lexicon"):
        load_verb_lexicons("nonexistent_lexicon")
