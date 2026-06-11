"""Tests for load_lexicons() — named lexicons and custom file paths."""
import pytest
from greek_inflexion_eee import load_lexicons


def test_pratt_string_shortcut():
    gi = load_lexicons("pratt")
    assert set(gi.generate("λύω", "PAI.1S").keys())


def test_homer_legw_imperative_2s():
    gi = load_lexicons("homer")
    assert set(gi.generate("λέγω", "PAD.2S").keys()) == {"λέγε"}


def test_homer_legw_imperative_2p():
    gi = load_lexicons("homer")
    assert set(gi.generate("λέγω", "PAD.2P").keys()) == {"λέγετε"}


def test_homer_akouo_imperative_2s():
    gi = load_lexicons("homer")
    assert set(gi.generate("ἀκούω", "PAD.2S").keys()) == {"ἄκουε"}


def test_homer_akouo_imperative_2p():
    gi = load_lexicons("homer")
    assert set(gi.generate("ἀκούω", "PAD.2P").keys()) == {"ἀκούετε"}


def test_homer_anagignwskw_imperative_2s():
    gi = load_lexicons("homer")
    result = set(gi.generate("ἀναγιγνώσκω", "PAD.2S").keys())
    assert result  # present stem now bundled
    assert any("γνωσκ" in f for f in result)


def test_homer_anagignwskw_imperative_2p():
    gi = load_lexicons("homer")
    result = set(gi.generate("ἀναγιγνώσκω", "PAD.2P").keys())
    assert result


def test_homer_pauō_imperative_2s():
    gi = load_lexicons("homer")
    assert set(gi.generate("παύω", "PAD.2S").keys()) == {"παῦε"}


def test_homer_pauō_imperative_2p():
    gi = load_lexicons("homer")
    assert set(gi.generate("παύω", "PAD.2P").keys()) == {"παύετε"}


def test_lxx_loads():
    gi = load_lexicons("lxx")
    assert set(gi.generate("λέγω", "PAI.1S").keys())


def test_morphgnt_loads():
    gi = load_lexicons("morphgnt")
    assert set(gi.generate("λέγω", "PAI.1S").keys())


def test_merge_homer_lxx():
    gi = load_lexicons(["homer", "lxx"])
    assert set(gi.generate("λέγω", "PAD.2S").keys()) == {"λέγε"}
    assert set(gi.generate("ἀκούω", "PAD.2S").keys()) == {"ἄκουε"}


def test_merge_all_three():
    gi = load_lexicons(["homer", "lxx", "morphgnt"])
    assert set(gi.generate("λέγω", "PAD.2S").keys())


def test_custom_file_path(tmp_path):
    import yaml
    custom = {"λύω": {"stems": {"1-": "λῡ", "2-": "λῡσ", "3-": "λῡσ", "3+": "ἐλυσ",
                                "4-": "λελυκ", "5-": "λελυ", "6-": "λυθ",
                                "6+": "ἐλυθ", "7-": "λυθησ"}}}
    p = tmp_path / "custom.yaml"
    p.write_text(yaml.dump(custom, allow_unicode=True), encoding="utf-8")
    gi = load_lexicons(str(p))
    assert set(gi.generate("λύω", "PAI.1S").keys())


def test_unknown_name_falls_back_to_path():
    with pytest.raises((FileNotFoundError, Exception)):
        load_lexicons("nonexistent_lexicon")
