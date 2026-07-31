def assert_all_entries_use_forms(*filenames):
    """Every entry in each bundled lexicon YAML file must be a forms: block,
    never stems: -- the shared structural guard for every forms:-only
    lexicon (byzantine, morpheus, pronoun): each is verbatim
    attested/suppletive forms, not mechanically generatable from stems: +
    stemming.yaml rules, so a stems: entry slipping in would silently
    reintroduce that generation risk."""
    from greek_inflexion_eee.fileformat import _load_lexicon_yaml

    for filename in filenames:
        data = _load_lexicon_yaml(filename)
        for lemma, entry in data.items():
            assert "stems" not in entry, f"{filename}: {lemma!r} has a stems: entry"
            assert "forms" in entry and entry["forms"], f"{filename}: {lemma!r} has no forms:"


def assert_no_duplicate_yaml_keys(*filenames):
    """Parse each bundled lexicon YAML file with a duplicate-key-aware
    loader, since yaml.safe_load silently keeps only the last of a
    duplicate top-level key -- a lemma mined in an earlier pattern and
    extended in a later one (without noticing it already has a block
    further up the file) would otherwise silently lose its earlier
    entries."""
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

    for filename in filenames:
        resource = files(_DATA_PKG) / filename
        with resource.open("r", encoding="utf-8") as f:
            yaml.load(f, Loader=_DupeCheckLoader)
