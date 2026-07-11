"""Audit a Morpheus-sourced lexicon YAML for dialect-register mismatches.

For each shipped (lemma, tag, form) cell, re-derive which cached Morpheus
reading(s) it came from and check their `dial` field against the register
the lexicon claims to represent. Flags cells whose *only* matching readings
carry a dial tag that excludes the target register -- e.g. a Doric-only
reading shipped as if it were Epic-appropriate (exactly what caught the
5 bad cells in odyssey_morpheus on 2026-07-11).

Usage: python3 audit_dial.py <lexicon_yaml> <pos> <target_register>
  pos:              "verb" | "noun" | "adjective"
  target_register:  "epic" or "attic" -- a reading counts as compatible if
                     ANY of its synonym markers appear in `dial` (Morpheus
                     tags the Epic/Homeric register inconsistently across
                     entries: "epic", "Homeric", and "Ionic" are all used,
                     sometimes combined, sometimes alone -- a bare substring
                     check on "epic" alone misses "Homeric Ionic" entirely,
                     which is exactly the register we want; caught this via
                     a first, buggy version of this script flagging 24 good
                     Homeric-Ionic entries as mismatches).
                     Pass "" (empty string) to only flag entries whose dial
                     is non-empty and clearly a DIFFERENT single dialect
                     (i.e. just report what's there, no accept/reject verdict).

Lemma matching is accent/diaeresis-tolerant (NFD-normalized, diacritics
stripped, trailing Morpheus homonym digits stripped) -- an exact-string
match here is a known trap: Morpheus's own `hdwd` spelling can differ from
a course's citation spelling by a diaeresis or breathing (e.g. δηϊόω vs
δηιόω) even when it's unambiguously the same lemma.
"""
import sys
import unicodedata
import yaml

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from query_morpheus import query_word, _as_list


def normalize_lemma(s):
    if not s:
        return ""
    s = s.rstrip("0123456789")
    nfd = unicodedata.normalize("NFD", s)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return stripped.replace("ς", "σ").casefold().strip()


# tag-code <-> Morpheus-entry mapping, duplicated (not imported) from the
# gap-analysis pipeline that originally built these lexicons -- see
# odyssey_morpheus_verbs_lexicon.yaml's own header for the full convention
# table (verified against greek_inflexion_eee's stemming.yaml).
_TENSE = {"present": "P", "imperfect": "I", "future": "F", "aorist": "A",
          "perfect": "X", "pluperfect": "Y", "futperf": "Z"}
_MOOD = {"indicative": "I", "subjunctive": "S", "optative": "O",
         "imperative": "D", "infinitive": "N", "participle": "P"}
_CASE = {"nominative": "N", "genitive": "G", "dative": "D", "accusative": "A", "vocative": "V"}
_NUMBER = {"singular": "S", "plural": "P", "dual": "D"}
_GENDER = {"masculine": "M", "feminine": "F", "neuter": "N"}
_PERSON = {"1st": "1", "2nd": "2", "3rd": "3"}
_NO_PASSIVE_TENSES = {"present", "imperfect", "perfect", "pluperfect"}


def _voice_codes(tense, voice):
    if tense in _NO_PASSIVE_TENSES:
        return ["M"] if voice in ("middle", "passive", "mediopassive") else ["A"]
    if voice == "active":
        return ["A"]
    if voice == "middle":
        return ["M"]
    if voice == "passive":
        return ["P"]
    if voice == "mediopassive":
        return ["M", "P"]
    return []


def tag_codes_for(pos, entry):
    if pos == "verb":
        tense, mood, voice = entry.get("tense"), entry.get("mood"), entry.get("voice")
        if not (tense and mood):
            return []
        t, m = _TENSE.get(tense), _MOOD.get(mood)
        if not (t and m):
            return []
        codes = []
        for v in _voice_codes(tense, voice):
            if mood == "infinitive":
                codes.append(f"{t}{v}N")
            elif mood == "participle":
                c, n, g = entry.get("case"), entry.get("number"), entry.get("gender")
                if c in _CASE and n in _NUMBER and g in _GENDER:
                    codes.append(f"{t}{v}P.{_CASE[c]}{_NUMBER[n]}{_GENDER[g]}")
            else:
                p, n = entry.get("person"), entry.get("number")
                if p in _PERSON and n in _NUMBER:
                    codes.append(f"{t}{v}{m}.{_PERSON[p]}{_NUMBER[n]}")
        return codes
    if pos in ("noun", "adjective"):
        c, n, g = entry.get("case"), entry.get("number"), entry.get("gender")
        if c in _CASE and n in _NUMBER and g in _GENDER:
            return [f"{_CASE[c]}{_NUMBER[n]}{_GENDER[g]}"]
    return []


# Morpheus tags the same register with different words across entries --
# a reading is "epic-compatible" if ANY of these appear anywhere in its
# dial list, not just the literal string "epic" (e.g. "Homeric Ionic" is
# Epic register but contains none of the substring "epic").
_REGISTER_SYNONYMS = {
    "epic": {"epic", "homeric", "ionic"},
    "attic": {"attic"},
}


def _register_present(dial_list, target_register):
    markers = _REGISTER_SYNONYMS.get(target_register.lower(), {target_register.lower()})
    joined = " ".join(dial_list).lower()
    return any(m in joined for m in markers)


def audit(yaml_path, pos, target_register):
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f.read())

    results = {"target_confirmed": [], "neutral": [], "MISMATCH": [], "not_found": []}
    for lemma, entry in data.items():
        norm_lemma = normalize_lemma(lemma)
        for tag, form_val in entry["forms"].items():
            forms = _as_list(form_val)
            for form in forms:
                bare = form.replace("(ν)", "")
                raw_entries = query_word(bare)
                if not raw_entries and bare != form:
                    raw_entries = query_word(form)
                if isinstance(raw_entries, dict) and "error" in raw_entries:
                    results["not_found"].append((lemma, tag, form, "query error"))
                    continue
                matches = [e for e in raw_entries
                           if normalize_lemma(e.get("lemma", "")) == norm_lemma
                           and tag in tag_codes_for(pos, e)]
                if not matches:
                    results["not_found"].append((lemma, tag, form, None))
                    continue
                dials = [m["dial"] for m in matches]
                if not target_register:
                    results["neutral"].append((lemma, tag, form, dials))
                    continue
                any_neutral = any(not d for d in dials)
                any_target = any(_register_present(d, target_register) for d in dials)
                if any_target:
                    results["target_confirmed"].append((lemma, tag, form, dials))
                elif any_neutral:
                    results["neutral"].append((lemma, tag, form, dials))
                else:
                    results["MISMATCH"].append((lemma, tag, form, dials))
    return results


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    path, pos, register = sys.argv[1], sys.argv[2], sys.argv[3]
    r = audit(path, pos, register)
    print(f"target_confirmed ({register!r} present): {len(r['target_confirmed'])}")
    print(f"neutral (no dial marker): {len(r['neutral'])}")
    print(f"MISMATCH (dial present, excludes {register!r}): {len(r['MISMATCH'])}")
    print(f"not_found (no matching cached entry): {len(r['not_found'])}")
    print()
    if r["MISMATCH"]:
        print("=== MISMATCH details ===")
        for m in r["MISMATCH"]:
            print(" ", m)
    if r["not_found"]:
        print("=== not_found details ===")
        for n in r["not_found"]:
            print(" ", n)
