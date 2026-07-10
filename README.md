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

  Combined unique coverage: ~5064 verbs. Custom YAML files (same format) are also
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

- **Adjective morphology** — `adj_stemming.yaml` + `pratt_adjs_lexicon.yaml` covering
  2-1-2 uncontracted/contracted, two-termination, 3-1-3 participial and υ-stem,
  3-3 σ-stem, and comparative adjectives.

- **Improved accent engine** — correct handling of nominal accent overrides for
  neuter forms; `_fix_nominal_oxytone` converts acute on inflected long ultima to
  circumflex while preserving native long ultimas (e.g. βασιλεύς).


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
