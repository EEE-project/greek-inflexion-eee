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
      load_verb_lexicons, load_noun_lexicons, load_adj_lexicons,
  )

  gi = load_default()                          # verb inflection (Pratt lexicon)
  gi = load_noun_default()                     # noun inflection (Pratt lexicon)
  gi = load_adj_default()                      # adjective inflection (Pratt lexicon)
  gi = load_verb_lexicons("homer")                  # verb inflection — Homeric corpus
  gi = load_verb_lexicons(["homer", "lxx"])         # merge two corpora
  gi = load_verb_lexicons(["pratt", "/my.yaml"])    # Pratt + custom file
  gi = load_noun_lexicons("homer")             # noun inflection — Homeric corpus
  gi = load_noun_lexicons(["homer"])           # merge noun lexicons
  gi = load_adj_lexicons("pratt")              # adjective inflection — Pratt lexicon
  ```

- **Bundled corpus lexicons** — named lexicons for verbs and nouns:

  **Verbs** (`load_verb_lexicons`):

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

  Combined unique coverage: ~5050 verbs. Custom YAML files (same format) are also
  accepted as absolute paths.

  **Nouns** (`load_noun_lexicons`) — always includes Pratt as base:

  | Name | Nouns | Source |
  |------|------:|--------|
  | `"pratt"` | 26 | Pratt textbook paradigm nouns |
  | `"homer"` | 15 | Homeric Odyssey/Iliad vocabulary |
  | `"lsj"` | 18 | Classical Attic (Perseus/LSJ-verified) |
  | `"morpheus"` | 62 | Morpheus-confirmed attested forms, Epic/Homeric (mixed) |

  **Adjectives** (`load_adj_lexicons`) — always includes Pratt as base:

  | Name | Source |
  |------|--------|
  | `"pratt"` | Pratt textbook paradigm adjectives |

  Course-specific vocabulary lexicons (formerly `"odyssey_morpheus"`,
  `"palaestra_morpheus"`) now live as course-local files in
  `created_with_eee`, not here — see "Course-specific lexicons moved out"
  below.

- **Perseids Morpheus** — the `"morpheus"` lexicon is sourced from or verified against
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
  inflected cells. Standalone (`load_verb_lexicons("byzantine")`), the lexicon
  therefore only covers its own 61 lemmas with 1-2 cells each. Merged with
  `lxx`/`morphgnt`/`lsj` as the base, it inherits their combined ~3000+
  lemma paradigm coverage and the `byzantine` override silently wins
  wherever Sophocles documents a divergence, falling through cleanly to
  the Koine/Attic-generated form everywhere else — which is also the
  linguistically accurate picture: most Byzantine literary Greek genuinely
  *is* Koine/Attic morphology, cell for cell; the exceptions layer is
  exactly where (and only where) it actually diverges.

  ```python
  gi = load_verb_lexicons(["lxx", "morphgnt", "pratt", "ltrg", "lsj", "byzantine"])
  gi.generate("γιγνώσκω", "XAI.3P")   # {'ἔγνωκαν': [...]} (byzantine override)
  gi.generate("πάσχω", "AAI.3P")      # {'ἔπαθον': [...]}  (plain Koine, no override)
  ```

- **Course-specific lexicons moved out (2026-07-31)** — `"odyssey_morpheus"`
  and `"palaestra_morpheus"` (`forms:`-only lexicons covering gaps in the
  created_with_eee Odyssey and Palaestra course vocabularies, verified
  against the Perseids Morpheus analyzer) were removed as named lexicons
  here and now live as course-local files directly in `created_with_eee`
  (see each course's own AGENTS.md). Both courses are still under active
  development — bundling their data as a named package lexicon had forced
  a full version bump + PyPI republish every time one more lesson needed a
  few more gap-mined words (7 releases in 16 days for Odyssey alone).
  Course-specific data goes back into the package only as a deliberate,
  one-time consolidation once a course is actually finished — not
  incrementally per lesson. Pass an absolute file path in `lexicons=[...]`
  instead of a registered name to use them (same mechanism as any other
  custom YAML lexicon file, see "Absolute file paths" above).

- **Unrecognized lexicon names now raise, and `load_lexicons` is renamed
  (2026-07-31)** — an unrecognized bare (non-absolute-path) name passed to
  `load_verb_lexicons`/`load_noun_lexicons`/`load_adj_lexicons`/`load_pron_lexicons`
  now raises `ValueError` naming the bad lexicon, instead of the previous
  split behavior: the noun/adj/pronoun loaders silently dropped an unknown
  name with no signal anything went wrong, while the verb loader (worse)
  fell through to opening it as a literal package-resource filename and
  crashed with a confusing raw `FileNotFoundError`. Both were real
  problems in practice, not theoretical — removing `"odyssey_morpheus"`
  above is exactly the kind of change the silent-skip path was built to
  hide. New `known_verb_lexicons()` / `known_noun_lexicons()` /
  `known_adj_lexicons()` / `known_pron_lexicons()` return each POS's
  registered name set, for a caller (e.g. `ancient_greek_backend_eee`,
  which shares one general-purpose `lexicons=[...]` list across every
  part of speech) to filter a shared list down to what's actually valid
  for a given POS before calling its loader — a bare name irrelevant to
  one POS is not a mistake in general, only when it's not registered
  *anywhere*. Also: `load_lexicons()` (verbs) is renamed to
  `load_verb_lexicons()`, matching `load_noun_lexicons`/`load_adj_lexicons`/
  `load_pron_lexicons` — it predated that naming convention (added when
  verbs were the library's only part of speech) and was never
  retroactively renamed until now.

- **Adjective morphology** — `adj_stemming.yaml` + `pratt_adjs_lexicon.yaml` covering
  2-1-2 uncontracted/contracted, two-termination, 3-1-3 participial and υ-stem,
  3-3 σ-stem, and comparative adjectives. 3-3 σ-stem two-termination adjectives
  (e.g. `ἀληθής`) generate masculine oblique forms directly now — previously
  only the feminine cells were reachable via `noun_stemming.yaml`'s existing
  masculine sigma-stem rule, which is correctly scoped to a different,
  genuinely masc-only class (contracted proper names like `Περικλῆς`) and left
  untouched; the two-termination adjective case gets its own rules instead.
  Verified via a full sweep (real Perseids Morpheus lookups, not guessing)
  that only `μείζων` (comparative) and `ἐυπλόκαμος` were genuinely missing a
  cell for their shared gender's data; added those directly. Every other
  adjective with an apparent masc/fem gap turned out to be a regular
  3-termination adjective (distinct forms exist, just not yet in the bundled
  lexicons) or a genuinely gender-restricted fixed epithet — not fixed here,
  since mirroring the other gender for those would be grammatically wrong.
  Separately, `δίκαιος`'s feminine paradigm had 5 wrong cells: NSF/GSF/ASF/APF
  came out accented on the antepenult (`δίκαια` etc.) instead of the correct
  penult (`δικαία`), and GPF got a wrong baked-in circumflex (`δικαιῶν` instead
  of `δικαίων`) — both are the stemming engine's inability to know a bare,
  undiacritized alpha's true (here, long) vowel length. Fixed via targeted
  `forms:` overrides for just those 5 cells (same pattern as `ταχύς`'s entry
  in the same file); the unaffected DSF/NPF/DPF and all masc/neut cells stay
  on the regular mechanism.

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

Development version (latest, from Codeberg):
```bash
pip install "greek-inflexion-eee @ git+https://codeberg.org/EEE-project/greek-inflexion-eee.git"
```

Or from source:

```bash
pip install -e .
```


## Quick start

```python
from greek_inflexion_eee import (
    load_default, load_noun_default, load_adj_default,
    load_verb_lexicons, load_noun_lexicons, load_adj_lexicons,
)

# Verbs — Pratt lexicon (20 verbs, teaching vocabulary)
gi = load_default()
gi.generate("λύω", "AAN")               # {'λῦσαι': [...]}

# Verbs — corpus lexicon by name
gi = load_verb_lexicons("homer")
gi.generate("λέγω", "PAD.2S")           # {'λέγε'}
gi.generate("ἀκούω", "PAD.2S")          # {'ἄκουε'}

# Verbs — merge corpora
gi = load_verb_lexicons(["homer", "lxx"])
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
gi = load_verb_lexicons(["morphgnt", "byzantine"])
gi.generate("γιγνώσκω", "XAI.3P")       # {'ἔγνωκαν': [...]} (not ἐγνώκᾱσι(ν))

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
