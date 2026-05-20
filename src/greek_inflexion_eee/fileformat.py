"""
encapsulates details of file format used for stemming.yaml, and lexicon YAMLs,
providing functions for loading the file and populating StemmingRuleSet or
Lexicon (with form and accent overrides)
"""

from __future__ import annotations

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


def _load_lexicon_resource(
    filename: str,
    pre_processor=lambda x: x,
) -> tuple:
    """Load a bundled lexicon YAML."""
    lexicon = Lexicon()
    form_override = {}
    accent_override = defaultdict(list)
    segmented_lemmas = {}
    resource = files(_DATA_PKG) / filename
    with resource.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _populate_lexicon(data, lexicon, form_override, accent_override,
                      segmented_lemmas, pre_processor)
    return lexicon, form_override, accent_override, segmented_lemmas


def _make_gi(
    stemming_files: str | list[str], lexicon_file: str
) -> "GreekInflexion":
    from greek_inflexion_eee.accent import debreath
    from greek_inflexion_eee.inflexion import GreekInflexion

    if isinstance(stemming_files, str):
        stemming_files = [stemming_files]
    ruleset = None
    for f in stemming_files:
        ruleset = _load_stemming_resource(f, ruleset=ruleset)

    lexicon, form_override, accent_override, segmented_lemmas = \
        _load_lexicon_resource(lexicon_file, pre_processor=debreath)

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

    Loads stemming.yaml + pratt_lexicon.yaml from the bundled data directory
    via importlib.resources.

    Cold-start cost is tenths of a second (YAML parsing). Cache externally
    if calling frequently.
    """
    return _make_gi("stemming.yaml", "pratt_lexicon.yaml")


def load_noun_default() -> "GreekInflexion":
    """Return a GreekInflexion for noun inflection, loaded with the bundled Pratt noun lexicon.

    Loads noun_stemming.yaml + pratt_noun_lexicon.yaml from the bundled data
    directory via importlib.resources.
    """
    return _make_gi("noun_stemming.yaml", "pratt_noun_lexicon.yaml")


def load_adj_default() -> "GreekInflexion":
    """Return a GreekInflexion for adjective inflection, loaded with the bundled Pratt adj lexicon.

    Loads noun_stemming.yaml + adj_stemming.yaml (merged) + pratt_adj_lexicon.yaml.
    """
    return _make_gi(["noun_stemming.yaml", "adj_stemming.yaml"], "pratt_adj_lexicon.yaml")
