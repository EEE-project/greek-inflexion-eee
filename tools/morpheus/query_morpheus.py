"""Query the Perseids Morpheus morphological analysis service for Ancient Greek words.

Rate-limited, cached (avoid re-querying the same word), robust to the
API's Body being either a dict (one analysis) or a list (multiple), and
to infl being either a dict or a list within one entry.

See README.md in this directory for the service description and the
overall lexicon-building workflow this tool supports.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

BASE_URL = "https://services.perseids.org/bsp/morphologyservice/analysis/word"


def _cache_path(word):
    safe = urllib.parse.quote(word, safe="")
    return os.path.join(CACHE_DIR, safe + ".json")


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _text_of(x):
    return x.get("$") if isinstance(x, dict) else x


def query_word(word, lang="grc", engine="morpheusgrc", delay=0.4, use_cache=True):
    """Query Morpheus for a single word form. Returns a list of parsed entries.

    Each entry: {"lemma": str, "pofs": str, "case": str|None, "number": str|None,
                 "gender": str|None, "person": str|None, "tense": str|None,
                 "mood": str|None, "voice": str|None, "stemtype": str|None,
                 "decl": str|None, "dial": list[str]}

    ``dial`` is the dialect(s) Morpheus attributes to this specific reading
    (e.g. ["epic", "Ionic"], ["Doric"], or [] when unmarked/dialect-neutral).
    Always check it before trusting a reading for a specific register --
    "the word exists in Morpheus" is not the same as "this exact reading is
    appropriate for the register you're building a lexicon for" (see the
    dial-awareness note in README.md; this bit the odyssey_morpheus lexicon
    once already -- 5 Doric-only readings shipped as if Epic-appropriate,
    caught only in a follow-up audit).

    Returns [] if no analysis found; {"error": str} on a request failure.
    """
    cache_file = _cache_path(word)
    if use_cache and os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        encoded = urllib.parse.quote(word)
        url = f"{BASE_URL}?word={encoded}&lang={lang}&engine={engine}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EEE-project research (educational, low-volume)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False)
        time.sleep(delay)

    return _parse_entries(raw)


def _parse_entries(raw):
    try:
        body = raw["RDF"]["Annotation"]["Body"]
    except (KeyError, TypeError):
        return []
    results = []
    for b in _as_list(body):
        if not isinstance(b, dict):
            continue
        entry = b.get("rest", {}).get("entry") if isinstance(b.get("rest"), dict) else None
        for e in _as_list(entry):
            if not isinstance(e, dict):
                continue
            dict_ = e.get("dict", {})
            infl = e.get("infl", {})
            for inf in _as_list(infl) or [{}]:
                results.append({
                    "lemma": _text_of(dict_.get("hdwd")),
                    "pofs": _text_of(dict_.get("pofs")) or _text_of(inf.get("pofs")),
                    "case": _text_of(inf.get("case")),
                    "number": _text_of(inf.get("num")),
                    "gender": _text_of(inf.get("gend")),
                    "person": _text_of(inf.get("pers")),
                    "tense": _text_of(inf.get("tense")),
                    "mood": _text_of(inf.get("mood")),
                    "voice": _text_of(inf.get("voice")),
                    "stemtype": _text_of(inf.get("stemtype")),
                    "decl": _text_of(dict_.get("decl")) or _text_of(inf.get("decl")),
                    "dial": [_text_of(d) for d in _as_list(inf.get("dial"))],
                })
    return results


if __name__ == "__main__":
    for w in sys.argv[1:]:
        print(f"=== {w} ===")
        for r in query_word(w):
            print(" ", r)
