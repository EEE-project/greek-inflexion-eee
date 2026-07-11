# greek-inflexion-eee

A fork of [jtauber/greek-inflexion](https://github.com/jtauber/greek-inflexion) packaged as
an installable Python library (`greek-inflexion-eee`) for use in the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools ecosystem.

The original library generates and analyzes Ancient Greek inflectional paradigms (verbs,
nouns, adjectives) with precise accentuation. See [README-greek-inflexion.md](README-greek-inflexion.md)
for the upstream documentation.


## What this fork adds

- **Installable package** — `src/` layout; data files bundled via `importlib.resources`
  so the library works correctly when installed (not just run from the source directory).

- **Factory functions** — ready-to-use entry points:

  ```python
  from greek_inflexion_eee import (
      load_default, load_noun_default, load_adj_default,
      load_lexicons, load_noun_lexicons, load_adj_lexicons,
  )

  gi = load_default()                          # verb inflection (Pratt lexicon)
  gi = load_noun_default()                     # noun inflection (Pratt lexicon)
  gi = load_adj_default()                      # adjective inflection (Pratt lexicon)
  gi = load_lexicons("homer")                  # verb inflection — Homeric corpus
  gi = load_lexicons(["homer", "lxx"])         # merge two corpora
  gi = load_lexicons(["pratt", "/my.yaml"])    # Pratt + custom file
  gi = load_noun_lexicons("homer")             # noun inflection — Homeric corpus
  gi = load_noun_lexicons(["homer"])           # merge noun lexicons
  gi = load_adj_lexicons("pratt")              # adjective inflection — Pratt lexicon
  ```

- **Bundled corpus lexicons** — named lexicons for verbs and nouns:

  **Verbs** (`load_lexicons`):

  | Name | Verbs | Source | Period / dialect |
  |------|------:|--------|-----------------|
  | `"pratt"` | 20 | Pratt textbook | teaching |
  | `"dik"` | 10 | Dik textbook | teaching |
  | `"ltrg"` | 34 | LTRG textbook | teaching |
  | `"lsj"` | 9 | hand-authored | Classical Attic, V–IV c. BCE |
  | `"homer"` | 2335 | Homeric corpus | Epic/Ionic, ~800 BCE |
  | `"lxx"` | 1905 | Septuagint | Biblical κοινή, ~250–100 BCE |
  | `"morphgnt"` | 1848 | New Testament | κοινή, ~1st c. CE |
  | `"morpheus"` | 46 | Morpheus-confirmed attested forms | Epic/Homeric (mixed) |
  | `"byzantine"` | 61 | hand-curated from Sophocles' Lexicon (1887) | Byzantine, ~4th–15th c. CE |
  | `"odyssey_morpheus"` | 56 | Morpheus-confirmed, Odyssey course vocabulary | Epic/Homeric |

  Combined unique coverage: ~5050 verbs. Custom YAML files (same format) are also
  accepted as absolute paths.

  **Nouns** (`load_noun_lexicons`) — always includes Pratt as base:

  | Name | Nouns | Source |
  |------|------:|--------|
  | `"pratt"` | 26 | Pratt textbook paradigm nouns |
  | `"homer"` | 15 | Homeric Odyssey/Iliad vocabulary |
  | `"lsj"` | 18 | Classical Attic (Perseus/LSJ-verified) |
  | `"morpheus"` | 62 | Morpheus-confirmed attested forms, Epic/Homeric (mixed) |
  | `"odyssey_morpheus"` | 59 | Morpheus-confirmed, Odyssey course vocabulary |
  | `"palaestra_morpheus"` | 26 | Morpheus-confirmed, Palaestra course vocabulary |

  **Adjectives** (`load_adj_lexicons`) — always includes Pratt as base:

  | Name | Source |
  |------|--------|
  | `"pratt"` | Pratt textbook paradigm adjectives |
  | `"odyssey_morpheus"` | Morpheus-confirmed, Odyssey course vocabulary (57 lemmas) |

- **Perseids Morpheus** — three lexicons (`"morpheus"`, `"odyssey_morpheus"`,
  `"palaestra_morpheus"`) are sourced from or verified against
  [Perseids Morpheus](https://services.perseids.org/bsp/morphologyservice/analysis/word),
  a free, public, no-auth HTTP API that analyzes a single Ancient Greek
  surface form and returns every morphological reading it can find — lemma,
  part of speech, full grammatical features, and a `dial` field naming the
  attested dialect(s) for that specific reading (e.g. `"epic"`, `"Homeric
  Ionic"`, `"Attic"`). It analyzes; it does not generate (no "give me all
  forms of X"). Built originally by the Perseus Project for the Homeric
  corpus specifically, so Epic/Ionic coverage is a genuine strength, not an
  afterthought — but always check `dial` before trusting a reading for a
  specific register; see `tools/morpheus/README.md` for the querying/
  auditing scripts and two real bugs they caught.

- **Morpheus-confirmed attested-form lexicon** (`"morpheus"`) — unlike every other
  bundled lexicon, every entry is a `forms:` block: a verbatim attested surface
  form, not a `stems:` entry generated on demand. Built for lemmas the stem-based
  lexicons can't handle cleanly — athematic `-μι` verbs, contract verbs,
  compounds, deponents, non-2nd-declension nouns, oxytone nouns, and irregular/
  suppletive nouns (Ζεύς) — by collecting attested `(form, UD-feats)` pairs from
  the UD_Ancient_Greek-Perseus and UD_Ancient_Greek-PROIEL treebanks and
  independently re-confirming each one against the Perseids Morpheus analyzer
  (matching lemma + tense/aspect + voice, or case + gender). Since `forms:`
  bypasses stem lookup entirely (`generate()` checks it before any stem-based
  generation), there's no stem-extraction/re-inflection risk for these
  irregulars — and an explicit override always wins over a stem-generated guess,
  which is what makes it safe to merge alongside a stem-based lexicon like
  `"homer"` for the same lemma. See `ancient_greek_backend_eee`'s own README for
  the companion fix that makes `.paradigm()` (the full-table view) render this
  data correctly — restricting a noun's enumerated genders to what it actually
  has, since the fix and this lexicon were built together to solve the same
  problem (Ζεύς-style irregulars) from two ends.

- **Byzantine lexicon** (`"byzantine"`) — a hand-curated `forms:`-only lexicon
  documenting several well-known Byzantine-period verb morphology shifts,
  mostly variants of an analogical `-αν`/`-σαν`/`-ασι` ending spreading into
  slots classical Greek marked differently (e.g. `ἔγνωκαν` replacing
  classical `ἐγνώκᾱσι(ν)`; `ἐποιοῦσαν` replacing `ἐποίουν`; `ἐδώκασι(ν)`
  replacing `ἔδωκαν`/`ἔδοσαν`) — the direct ancestor of Modern Greek's
  uniform past-tense endings. See the lexicon file's own header for the
  complete pattern-by-pattern breakdown and sourcing/verification discipline
  for each. 61 lemmas, sourced from Sophocles' *Greek Lexicon of the Roman
  and Byzantine Periods* (1887, public domain) — specifically its
  Introduction's own systematic survey of this phenomenon, not scattered
  dictionary entries. The two entries whose citation is an NT verse
  (`γιγνώσκω`, `ὁράω`) are additionally cross-verified against the
  Westcott-Hort/Nestle 1904 critical text; the rest cite patristic/Byzantine
  authors (Barnabas, Hippolytus, the Sibylline Oracles, Malalas, Theophanes,
  ...) instantiating the same independently-documented phenomenon (see
  Wikipedia's *Medieval Greek* article). Unlike `morpheus`, this is not a
  systematic sweep of a corpus — TLG and LBG (the two best-fitting Byzantine
  lexicons) were investigated and ruled out as sources, since both explicitly
  prohibit bulk/programmatic extraction; see the lexicon file's own header
  for the full sourcing story and what was deliberately excluded (ambiguous
  mood readings, illegible OCR, forms already reachable via another
  lexicon's own stem-based generation).

  **Use `"byzantine"` merged with a Koine/Attic base, not standalone.**
  Sophocles' Introduction documents *specific, optional deviations* from an
  already-known classical paradigm (e.g. "3rd plural sometimes ends in -αν
  instead of -ασι"), not a self-contained stemming engine — there's no
  principal-parts information here, only citations for individual already-
  inflected cells. Standalone (`load_lexicons("byzantine")`), the lexicon
  therefore only covers its own 61 lemmas with 1-2 cells each. Merged with
  `lxx`/`morphgnt`/`lsj` as the base, it inherits their combined ~3000+
  lemma paradigm coverage and the `byzantine` override silently wins
  wherever Sophocles documents a divergence, falling through cleanly to
  the Koine/Attic-generated form everywhere else — which is also the
  linguistically accurate picture: most Byzantine literary Greek genuinely
  *is* Koine/Attic morphology, cell for cell; the exceptions layer is
  exactly where (and only where) it actually diverges.

  ```python
  gi = load_lexicons(["lxx", "morphgnt", "pratt", "ltrg", "lsj", "byzantine"])
  gi.generate("γιγνώσκω", "XAI.3P")   # {'ἔγνωκαν': [...]} (byzantine override)
  gi.generate("πάσχω", "AAI.3P")      # {'ἔπαθον': [...]}  (plain Koine, no override)
  ```

- **Course-specific Morpheus lexicons** (`"odyssey_morpheus"`, `"palaestra_morpheus"`)
  — `forms:`-only lexicons covering gaps in the created_with_eee Odyssey and
  Palaestra course vocabularies, verified against the Perseids Morpheus
  analyzer. Distinct provenance from `"morpheus"` (treebank-driven, corpus-
  general): these start from each course's own vocabulary and keep only
  cells the rest of the lexicon chain doesn't already generate correctly.
  Odyssey's forms are attested-in-text (harvested from the course's own
  lesson TSVs, Morpheus-confirmed); Palaestra's are synthetic candidates
  generated from known declension patterns and then Morpheus-verified, since
  its vocabulary TSVs give only a citation form with no running text to
  harvest from. See each lexicon file's own header for the full sourcing
  story, and `test_odyssey_palaestra_morpheus_lexicons.py` for behavioral
  coverage.

  ```python
  gi = load_noun_lexicons(["homer", "odyssey_morpheus"])
  gi.generate("βοῦς", "NPM")              # {'βοῦς': [...]} (Homeric, not βόες)

  gi = load_noun_lexicons("palaestra_morpheus")
  gi.generate("σκιά", "GSF")              # {'σκιᾶς': [...]} (usable standalone)
  ```

- **Adjective morphology** — `adj_stemming.yaml` + `pratt_adjs_lexicon.yaml` covering
  2-1-2 uncontracted/contracted, two-termination, 3-1-3 participial and υ-stem,
  3-3 σ-stem, and comparative adjectives.

- **Improved accent engine** — correct handling of nominal accent overrides for
  neuter forms; `_fix_nominal_oxytone` converts acute on inflected long ultima to
  circumflex while preserving native long ultimas (e.g. βασιλεύς). The pedagogical
  vowel-length macron some lexicon stems carry (e.g. λύω's long υ, needed so
  participles/infinitives/imperatives get circumflex where Greek requires a long
  vowel) is now stripped from final output once accent computation has used it —
  previously it leaked into acute-accented forms as a stray combining mark
  (`λύω` → `λῡ́ω`).


## Installation

```bash
pip install greek-inflexion-eee
```

Or from source:

```bash
pip install -e .
```


## Quick start

```python
from greek_inflexion_eee import (
    load_default, load_noun_default, load_adj_default,
    load_lexicons, load_noun_lexicons, load_adj_lexicons,
)

# Verbs — Pratt lexicon (20 verbs, teaching vocabulary)
gi = load_default()
gi.generate("λύω", "AAN")               # {'λῦσαι': [...]}

# Verbs — corpus lexicon by name
gi = load_lexicons("homer")
gi.generate("λέγω", "PAD.2S")           # {'λέγε'}
gi.generate("ἀκούω", "PAD.2S")          # {'ἄκουε'}

# Verbs — merge corpora
gi = load_lexicons(["homer", "lxx"])
gi.generate("παύω", "PAD.2P")           # {'παύετε'}

# Nouns — Pratt paradigm words only
gi = load_noun_default()
gi.generate("θεός", "NSM")              # {'θεός': [...]}
gi.generate("βασιλεύς", "NSM")          # {'βασιλεύς': [...]}

# Nouns — Homeric vocabulary (Pratt + Homer merged)
gi = load_noun_lexicons("homer")
gi.generate("θάνατος", "NSM")           # {'θάνατος': [...]}
gi.generate("μάχη", "GSF")              # {'μάχης': [...]}
gi.generate("βοῦς", "GPM")              # {'βοῶν': [...]}

# Nouns — Morpheus-confirmed attested forms (real Epic spellings, not generated)
gi = load_noun_lexicons("morpheus")
gi.generate("Ζεύς", "GSM")              # {'Διός': [...]} (suppletive, not a stem+ending)
gi.generate("θεός", "GSM")              # {'θεοῖο': [...]} (Epic genitive, not Attic -ου)

# Verbs — Byzantine-period attested divergence (merge alongside a Koine lexicon)
gi = load_lexicons(["morphgnt", "byzantine"])
gi.generate("γιγνώσκω", "XAI.3P")       # {'ἔγνωκαν': [...]} (not ἐγνώκᾱσι(ν))

# Nouns — Palaestra course vocabulary (usable standalone, no Homeric base needed)
gi = load_noun_lexicons("palaestra_morpheus")
gi.generate("δεσπότης", "GPM")          # {'δεσποτῶν': [...]}

# Adjectives
gi = load_adj_default()
gi.generate("ἀγαθός", "NSM")            # {'ἀγαθός': [...]}
gi.generate("ἀγαθός", "NSF")            # {'ἀγαθή': [...]}
gi.generate("ἀγαθός", "NSN")            # {'ἀγαθόν': [...]}
```


## Origin

Forked from [jtauber/greek-inflexion](https://github.com/jtauber/greek-inflexion)
by James Tauber. The upstream library and its data (stemming rules, Pratt/Dik/Homer
lexica) are the work of James Tauber and contributors; see [AUTHORS](AUTHORS) and
[LICENSE](LICENSE).

This fork is maintained by
[Ελληνικά Εκπαιδευτικά Εργαλεία (EEE)](https://codeberg.org/EEE-project) —
Greek Language Educational Tools.
