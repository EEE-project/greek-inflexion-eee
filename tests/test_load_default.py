from greek_inflexion_eee import GreekInflexion, load_default


def test_import():
    assert GreekInflexion is not None
    assert load_default is not None


def test_returns_instance():
    gi = load_default()
    assert isinstance(gi, GreekInflexion)


def test_no_path_args():
    gi = load_default()
    assert gi is not None


def test_verb_form_luo():
    gi = load_default()
    result = gi.generate("λύω", "PAI.1S")
    assert result, "generate() returned empty for λύω PAI.1S"
    assert "λύω" in result


def test_verb_find_stems_luo():
    gi = load_default()
    stems = gi.find_stems("λύω", "AAI.1S")
    assert stems, "find_stems returned empty for λύω AAI.1S"


def test_parse_ballo():
    # Not λύω: its principal stem carries a macron (λῡ), which possible_stems()
    # can't recover from the plain surface spelling -- a separate, pre-existing
    # reverse-stemming limitation, unrelated to parse() itself.
    gi = load_default()
    assert ("βάλλω", "PAI.1S") in gi.parse("βάλλω")
