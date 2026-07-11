# Morpheus tooling

Scripts for building and auditing the `*_morpheus_*` lexicons (`morpheus`,
`odyssey_morpheus`, `palaestra_morpheus`) against the Perseids Morpheus
morphological analyzer.

## The service

**Perseids Morpheus** (`https://services.perseids.org/bsp/morphologyservice/analysis/word`)
is a free, public, no-auth HTTP API that analyzes a single Ancient Greek
surface form and returns every morphological reading it can find for it —
lemma, part of speech, and the full grammatical feature set (case/number/
gender for nominals; tense/mood/voice/person/number for verbs), plus a
`dial` field naming the dialect(s) that specific reading is attested in
(e.g. `"epic"`, `"Homeric Ionic"`, `"Doric Aeolic"`, `"Attic"` — often
several combined, sometimes absent/dialect-neutral). It analyzes; it does
not generate — given a lemma it cannot produce "all forms of X", only the
reverse (given a form, what could this be). It was originally built by the
Perseus Project specifically to parse the Homeric corpus, so Epic/Ionic
coverage is a core strength, not an afterthought, though it also covers
Attic, Koine, and other periods.

Request shape: `?word=<url-encoded-form>&lang=grc&engine=morpheusgrc`.
Response is JSON (not XML) at `RDF.Annotation.Body` — `Body` is a dict for
a single reading or a list for multiple; each entry's `rest.entry` similarly
may hold one `infl` dict or a list of them (one per morphological reading
sharing that dictionary headword).

## Files

- **`query_morpheus.py`** — the HTTP client. `query_word(form)` returns a
  list of flat dicts (`lemma`, `pofs`, `case`, `number`, `gender`, `person`,
  `tense`, `mood`, `voice`, `stemtype`, `decl`, `dial`). Caches every
  response to `cache/<url-encoded-form>.json` so a lexicon-building or
  audit pass never re-queries the same form twice; rate-limits fresh
  requests to ~0.4s apart. Run directly for a quick lookup:
  ```bash
  python3 query_morpheus.py ἄνδρα μοῦσα
  ```

- **`audit_dial.py`** — checks a lexicon YAML's shipped `(lemma, tag, form)`
  cells against the cached Morpheus data for two failure modes at once:
  1. **Register mismatch** — the only matching reading(s) carry a `dial`
     that excludes the register the lexicon claims (e.g. a form shipped as
     Epic-appropriate that's actually Doric-only).
  2. **Cross-lemma contamination** — *no* cached reading has both the
     shipped lemma AND the shipped tag simultaneously, meaning the tag was
     computed from a different reading (usually a different lemma sharing
     that surface form) and incorrectly filed under this one.
  ```bash
  python3 audit_dial.py ../../src/greek_inflexion_eee/data/odyssey_morpheus_verbs_lexicon.yaml verb epic
  ```
  Lemma matching is accent/diaeresis-tolerant (NFD-normalized, diacritics
  stripped) and strips Morpheus's trailing homonym-disambiguation digits
  (`μόσχος1`/`μόσχος2`) — an exact string match is a known trap (Morpheus's
  own `hdwd` spelling can differ from a course's citation spelling by a
  breathing or diaeresis, e.g. `δηϊόω` vs `δηιόω`, for unambiguously the
  same lemma).

- **`cache/`** — every raw JSON response fetched while building/auditing
  the current lexicons (~700 files, ~3 MB). Committed so the whole pipeline
  is reproducible without hitting the live service again; safe to delete
  and let `query_morpheus.py` regenerate on demand.

## Lessons learned the hard way

Both failure modes `audit_dial.py` checks for were real bugs shipped in
`odyssey_morpheus`, caught only in a follow-up audit (2026-07-11) after the
lexicons were already committed:

- **Dial-blindness**: the first version of `query_morpheus.py` never
  extracted the `dial` field at all, so 5 Doric/Doric-Aeolic-only readings
  shipped as if they were Epic-appropriate.
- **Cross-lemma contamination**: the original gap-mining script computed a
  tag code from *every* Morpheus reading for a surface form without
  re-filtering to the readings whose lemma actually matched the target
  lemma — so a tag genuinely belonging to a different (often homographic)
  lemma got filed under the wrong entry. 26 cells across 21 lemmas were
  affected; see `test_cross_lemma_contamination_excluded` and
  `test_dialect_mismatched_cells_excluded` in
  `tests/test_odyssey_palaestra_morpheus_lexicons.py` for the full list and
  the reasoning behind each fix.

**If you build a new Morpheus-sourced lexicon, run `audit_dial.py` against
it before shipping — do not rely on "Morpheus confirmed the lemma matches"
alone**, since that check alone is exactly what let both bugs through.

## Known gaps in this tooling

- **`audit_dial.py`'s lemma matching doesn't know about deliberate spelling
  aliases.** It's accent/diaeresis-tolerant, but a handful of lemmas are
  filed under one citation spelling while Morpheus's own preferred `hdwd`
  is a genuinely different consonant sequence for the same word (known
  cases so far: `ἐννέπω`↔`ἐνέπω`, `μετανίσομαι`↔`μετανίσσομαι`,
  `νοῦς`↔`νόος`, `ἄεθλος`↔`ἆθλος`). These show up as `not_found` in an
  audit even though the underlying data is correct — **always check by
  hand whether a `not_found` entry is this, or a real bug**, before
  removing anything (see `query_all_morpheus_lexicon.py`'s audit history
  for worked examples of telling the two apart).
- **Some `dial`-only tags reflect corpus provenance, not a real dialect
  restriction.** A lemma whose stem ends in ε/ι/ρ keeps long-α in its
  paradigm in *every* period (the same rule that makes σκιά's plural
  dialect-general) — if Morpheus happens to only have cited it from an
  Attic/Doric source, that's not evidence the Epic spelling differs.
  `θεά` and `ὥρα` in `morpheus_nouns_lexicon.yaml` were investigated this
  way and deliberately kept despite an all-"Attic Doric Aeolic" `dial`.
  Don't auto-remove on `dial` mismatch alone — check whether the lemma's
  own phonology explains it first.
- `audit_dial.py` needs a raw cached (or freshly queryable) response for
  the *exact* surface-form spelling shipped. Movable-nu parentheses and
  elision apostrophes are stripped before querying; anything else missing
  needs a fresh query or manual lookup.
- **`query_all_morpheus_lexicon.py`** — the one-shot script used to backfill
  fresh queries for `morpheus_{verbs,nouns}_lexicon.yaml` (built in an
  earlier session via a different pipeline, `grc_paradigm_cache_final.tsv`,
  which didn't preserve `dial` or raw responses at all). Not something
  you'd normally re-run — kept for the record and as a template for
  auditing any future non-`audit_dial.py`-built lexicon the same way.

## Audit status

| Lexicon | Audited | Result |
|---|---|---|
| `odyssey_morpheus` (verbs/nouns/adjs) | yes (2026-07-11) | 33 bad cells found and removed across two passes (5 dial, 28 cross-lemma-contamination) |
| `palaestra_morpheus` | yes (2026-07-11) | 0 bad cells; 4 `σκιά` cells flagged then kept (see phonology note above) |
| `morpheus` (verbs/nouns) | yes (2026-07-11, fresh queries — no prior cache existed) | 22 bad cells found and removed across 13 lemmas (dial mismatches + wrong gender/number/case + invalid voice-letter tags); 2 lemmas (θεά, ὥρα) investigated and kept |
| `byzantine` | not applicable | never went through live Morpheus querying — sourced from Sophocles' 1887 dictionary, cross-checked against the existing stem-based engine and published critical texts instead |
