"""One-shot: query fresh Morpheus data for every form in morpheus_{verbs,nouns}_lexicon.yaml.

Populates tools/morpheus/cache/ so audit_dial.py can then check them
(no cache existed for these forms before -- they were built in an earlier
session via a different pipeline, grc_paradigm_cache_final.tsv, which
didn't preserve dial or raw responses).
"""
import os
import sys

from greek_inflexion_eee.fileformat import _load_lexicon_yaml

sys.path.insert(0, os.path.dirname(__file__))
from query_morpheus import query_word, _as_list

forms = set()
for fn in ["morpheus_verbs_lexicon.yaml", "morpheus_nouns_lexicon.yaml"]:
    data = _load_lexicon_yaml(fn)
    for lemma, entry in data.items():
        for tag, val in entry["forms"].items():
            for form in _as_list(val):
                forms.add(form.replace("(ν)", ""))

forms = sorted(forms)
print(f"{len(forms)} distinct forms to query", flush=True)
for i, form in enumerate(forms, 1):
    query_word(form)
    if i % 25 == 0 or i == len(forms):
        print(f"  [{i}/{len(forms)}] {form}", flush=True)
print("done")
