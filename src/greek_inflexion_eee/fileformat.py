"""
encapsulates details of file format used for stemming.yaml, and lexicon YAMLs,
providing functions for loading the file and populating StemmingRuleSet or
Lexicon (with form and accent overrides)
"""

from __future__ import annotations

import os
from collections import defaultdict
from importlib.resources import files
from typing import TYPE_CHECKING

import yaml

from greek_accentuation.characters import strip_length as do_strip_length

from inflexion import Inflexion
from inflexion.lexicon import Lexicon
from inflexion.stemming import StemmingRuleSet

if TYPE_CHECKING:
    from greek_inflexion_eee.inflexion import GreekInflexion

_DATA_PKG = "greek_inflexion_eee.data"

# Named verb lexicons bundled with the package
_VERB_LEXICONS: dict[str, str] = {
    "pratt":    "pratt_verbs_lexicon.yaml",
    "dik":      "dik_verbs_lexicon.yaml",
    "ltrg":     "ltrg_verbs_lexicon.yaml",
    "homer":    "homer_verbs_lexicon.yaml",
    "lxx":      "lxx_verbs_lexicon.yaml",
    "morphgnt": "morphgnt_verbs_lexicon.yaml",
    "lsj":      "lsj_verbs_lexicon.yaml",
    "morpheus": "morpheus_verbs_lexicon.yaml",
    "byzantine": "byzantine_verbs_lexicon.yaml",
    "odyssey_morpheus": "odyssey_morpheus_verbs_lexicon.yaml",
}

# Named noun lexicons bundled with the package
_NOUN_LEXICONS: dict[str, str] = {
    "pratt": "pratt_nouns_lexicon.yaml",
    "homer": "homer_nouns_lexicon.yaml",
    "lsj": "lsj_nouns_lexicon.yaml",
    "morpheus": "morpheus_nouns_lexicon.yaml",
    "odyssey_morpheus": "odyssey_morpheus_nouns_lexicon.yaml",
    "palaestra_morpheus": "palaestra_morpheus_nouns_lexicon.yaml",
}

# Named adjective lexicons bundled with the package
_ADJ_LEXICONS: dict[str, str] = {
    "pratt": "pratt_adjs_lexicon.yaml",
    "odyssey_morpheus": "odyssey_morpheus_adjs_lexicon.yaml",
}

_PARTNUM_TO_KEY_REGEX = {
    "1-": "P",
    "1-A": "PA",
    "1-M": "PM",
    "1+": "I",
    "2-": "F[AM]",
    "2-A": "FA",
    "2-M": "FM",
    "3-": "A[AM][NPDSO]",
    "3+": "A[AM]I",
    "3+A": "AAI",
    "3+M": "AMI",
    "4-": "XA",
    "4+": "YA",
    "5-": "X[MP]",
    "5+": "Y[MP]",
    "6-": "AP[NPDSO]",
    "6+": "API",
    "7-": "FP",
    "8-": "Z[MP]",
    "M": "..M",
    "F": "..F",
    "N": "..N",
    "noun": "[NGDAV][SP][MFN]",
}


class RefDoesNotExistException(Exception):
    pass


def split_stem_tags(stems):
    for stem in stems.split("/"):
        if ";" in stem:
            stem, tag = stem.split(";")
            tag = {tag}
        else:
            tag = set()

        yield stem, tag


def _populate_stemming(stemming_dict, ruleset, strip_length_flag=False):
    for key, rules in stemming_dict.items():
        while isinstance(rules, dict) and "ref" in rules:
            if rules["ref"] in stemming_dict:
                rules = stemming_dict[rules["ref"]]
            else:
                raise RefDoesNotExistException(
                    "ref to {} which doesn't exist".format(rules["ref"]))
        for rule in rules:
            if strip_length_flag:
                rule = do_strip_length(rule)
            if ";" in rule:
                rule, annotation = rule.split(";")
                ruleset.add(key, rule, {annotation})
            else:
                ruleset.add(key, rule)
    return ruleset


def _populate_lexicon(data, lexicon, form_override, accent_override,
                      segmented_lemmas, pre_processor):
    for lemma, entry in data.items():
        if entry:
            if "-" in lemma:
                segmented_lemma = lemma
                lemma = lemma.replace("-", "")
                segmented_lemmas[lemma] = segmented_lemma
            if "stems" in entry:
                for partnum, stems in sorted((
                    entry["stems"] if entry.get("stems") else {}
                ).items()):
                    key_regex = _PARTNUM_TO_KEY_REGEX[partnum]
                    for stem, tag in split_stem_tags(stems):
                        lexicon.add(lemma, key_regex, pre_processor(stem), tag)
                for key_regex, stems in entry.get("stem_overrides", []):
                    if stems is None:
                        continue
                    for stem, tag in split_stem_tags(stems):
                        lexicon.add(lemma, key_regex, pre_processor(stem), tag)
            for key, form in entry.get("forms", {}).items():
                form_override[(lemma, key)] = form
            for key_regex, form in entry.get("accents", []):
                accent_override[lemma].append((key_regex, form))


def load_stemming(stemming_file, strip_length=False):
    ruleset = StemmingRuleSet()
    with open(stemming_file) as f:
        stemming_dict = yaml.safe_load(f)
    return _populate_stemming(stemming_dict, ruleset, strip_length)


def load_lexicon(lexicon_file, pre_processor=lambda x: x):
    lexicon = Lexicon()
    form_override = {}
    accent_override = defaultdict(list)
    segmented_lemmas = {}
    with open(lexicon_file) as f:
        data = yaml.safe_load(f)
    _populate_lexicon(data, lexicon, form_override, accent_override,
                      segmented_lemmas, pre_processor)
    return lexicon, form_override, accent_override, segmented_lemmas


def _load_stemming_resource(
    filename: str,
    ruleset: StemmingRuleSet | None = None,
    strip_length_flag: bool = False,
) -> StemmingRuleSet:
    """Load a bundled stemming YAML. Pass an existing *ruleset* to merge."""
    if ruleset is None:
        ruleset = StemmingRuleSet()
    resource = files(_DATA_PKG) / filename
    with resource.open("r", encoding="utf-8") as f:
        stemming_dict = yaml.safe_load(f)
    return _populate_stemming(stemming_dict, ruleset, strip_length_flag)


def _load_lexicon_yaml(filename: str) -> dict:
    """Load a lexicon YAML from a package resource or an absolute file path."""
    if os.path.isabs(filename):
        with open(filename, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    resource = files(_DATA_PKG) / filename
    with resource.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_lexicon_resource(
    filename: str,
    pre_processor=lambda x: x,
) -> tuple:
    """Load a bundled lexicon YAML."""
    lexicon = Lexicon()
    form_override = {}
    accent_override = defaultdict(list)
    segmented_lemmas = {}
    data = _load_lexicon_yaml(filename)
    _populate_lexicon(data, lexicon, form_override, accent_override,
                      segmented_lemmas, pre_processor)
    return lexicon, form_override, accent_override, segmented_lemmas


def _make_gi(
    stemming_files: "str | list[str]", lexicon_files: "str | list[str]"
) -> "GreekInflexion":
    from greek_inflexion_eee.accent import debreath
    from greek_inflexion_eee.inflexion import GreekInflexion

    if isinstance(stemming_files, str):
        stemming_files = [stemming_files]
    if isinstance(lexicon_files, str):
        lexicon_files = [lexicon_files]

    ruleset = None
    for f in stemming_files:
        ruleset = _load_stemming_resource(f, ruleset=ruleset)

    lexicon = Lexicon()
    form_override: dict = {}
    accent_override: defaultdict = defaultdict(list)
    segmented_lemmas: dict = {}

    for lex in lexicon_files:
        data = _load_lexicon_yaml(lex)
        _populate_lexicon(data, lexicon, form_override, accent_override,
                          segmented_lemmas, debreath)

    gi = object.__new__(GreekInflexion)
    gi.ruleset = ruleset
    gi.lexicon = lexicon
    gi.form_override = form_override
    gi.accent_override = accent_override
    gi.segmented_lemmas = segmented_lemmas
    gi.inflexion = Inflexion()
    gi.inflexion.add_lexicon(gi.lexicon)
    gi.inflexion.add_stemming_rule_set(gi.ruleset)
    return gi


def load_default() -> "GreekInflexion":
    """Return a GreekInflexion for verb inflection, loaded with the bundled Pratt lexicon.

    Loads stemming.yaml + pratt_verbs_lexicon.yaml from the bundled data directory
    via importlib.resources.

    Cold-start cost is tenths of a second (YAML parsing). Cache externally
    if calling frequently.
    """
    return _make_gi("stemming.yaml", "pratt_verbs_lexicon.yaml")


def load_noun_default() -> "GreekInflexion":
    """Return a GreekInflexion for noun inflection, loaded with the bundled Pratt noun lexicon.

    Loads noun_stemming.yaml + pratt_nouns_lexicon.yaml from the bundled data
    directory via importlib.resources.
    """
    return _make_gi("noun_stemming.yaml", "pratt_nouns_lexicon.yaml")


def load_adj_default() -> "GreekInflexion":
    """Return a GreekInflexion for adjective inflection, loaded with the bundled Pratt adj lexicon.

    Loads noun_stemming.yaml + adj_stemming.yaml (merged) + pratt_adjs_lexicon.yaml.
    """
    return _make_gi(["noun_stemming.yaml", "adj_stemming.yaml"], "pratt_adjs_lexicon.yaml")


def load_lexicons(names: "str | list[str]") -> "GreekInflexion":
    """Return a GreekInflexion for verb inflection using one or more lexicons merged.

    Args:
        names: a lexicon name or list of names / absolute file paths.

    Named lexicons (corpus / period)::

        "pratt"    — Pratt textbook verbs (~20 verbs, teaching)
        "dik"      — Dik textbook verbs (~10 verbs, teaching)
        "ltrg"     — LTRG textbook verbs (~34 verbs, teaching)
        "homer"    — Homeric corpus, Epic/Ionic, ~800 BCE (~2335 verbs)
        "lxx"      — Septuagint, Biblical koine, ~250–100 BCE (~1905 verbs)
        "morphgnt" — New Testament, koine, ~1st c. CE (~1848 verbs)
        "lsj"      — Classical Attic, hand-authored from LSJ (small, curated)
        "morpheus" — Morpheus-confirmed attested forms for lemmas the other
                     lexicons can't handle cleanly (athematic/contract/
                     compound/deponent verbs); Epic/Homeric register
        "byzantine" — Byzantine period, ~4th–15th c. CE, hand-curated from
                     Sophocles' Lexicon of the Roman and Byzantine Periods
                     (very small; documents specific attested morphological
                     divergences from Attic/Koine, not a full paradigm source)
        "odyssey_morpheus" — Morpheus-confirmed attested forms for verbs in
                     the created_with_eee Odyssey course vocabulary not
                     already covered by the rest of the chain; course-
                     vocabulary-driven (see its own header), distinct from
                     the treebank-driven "morpheus"

    Absolute file paths load custom YAML lexicon files in the same format.
    Multiple names are merged additively; later entries add new stems without
    removing existing ones.

    Examples::

        load_lexicons("homer")
        load_lexicons(["homer", "lxx"])
        load_lexicons(["pratt", "/path/to/my_course.yaml"])
    """
    if isinstance(names, str):
        names = [names]
    filenames = [_VERB_LEXICONS.get(n, n) for n in names]
    return _make_gi("stemming.yaml", filenames)


def _load_pos_lexicons(
    stemming_yaml: "str | list[str]",
    lexicon_map: "dict[str, str]",
    default_file: str,
    names: "str | list[str]",
) -> "GreekInflexion":
    if isinstance(names, str):
        names = [names]
    filenames = [default_file]
    for n in names:
        if os.path.isabs(n):
            if n not in filenames:
                filenames.append(n)
        else:
            fname = lexicon_map.get(n)
            if fname and fname not in filenames:
                filenames.append(fname)
    return _make_gi(stemming_yaml, filenames)


def load_noun_lexicons(names: "str | list[str]") -> "GreekInflexion":
    """Return a GreekInflexion for noun inflection using one or more lexicons merged.

    Always includes the Pratt base noun lexicon. Additional named lexicons
    are merged additively when available.

    Args:
        names: a lexicon name or list of names. Unknown names are silently skipped.

    Named lexicons::

        "pratt"    — Pratt teaching nouns (~26 nouns)
        "homer"    — Homeric corpus nouns (~15 nouns, Odyssey/Iliad vocabulary)
        "lsj"      — Classical Attic, hand-authored from LSJ (small, curated)
        "morpheus" — Morpheus-confirmed attested forms for lemmas the other
                     lexicons can't handle cleanly (non-2nd-declension,
                     oxytone, irregular); Epic/Homeric register
        "odyssey_morpheus" — Morpheus-confirmed attested forms for nouns in
                     the created_with_eee Odyssey course vocabulary not
                     already covered by the rest of the chain
        "palaestra_morpheus" — Morpheus-confirmed forms for the 27 nouns in
                     the created_with_eee Palaestra course vocabulary;
                     synthetic candidates generated from known declension
                     patterns then Morpheus-verified, not attestation-
                     harvested (see its own header) — usable standalone

    Examples::

        load_noun_lexicons("homer")
        load_noun_lexicons(["homer", "lxx"])
    """
    return _load_pos_lexicons("noun_stemming.yaml", _NOUN_LEXICONS, "pratt_nouns_lexicon.yaml", names)


def load_adj_lexicons(names: "str | list[str]") -> "GreekInflexion":
    """Return a GreekInflexion for adjective inflection using one or more lexicons merged.

    Always includes the Pratt base adjective lexicon. Additional named lexicons
    are merged additively when available.

    Args:
        names: a lexicon name or list of names. Unknown names are silently skipped.

    Named lexicons::

        "pratt" — Pratt teaching adjectives
        "odyssey_morpheus" — Morpheus-confirmed attested forms for
                     adjectives in the created_with_eee Odyssey course
                     vocabulary; the first named adjective lexicon beyond
                     "pratt" (see its own header)

    Examples::

        load_adj_lexicons("pratt")
        load_adj_lexicons(["pratt"])
    """
    return _load_pos_lexicons(
        ["noun_stemming.yaml", "adj_stemming.yaml"],
        _ADJ_LEXICONS,
        "pratt_adjs_lexicon.yaml",
        names,
    )
