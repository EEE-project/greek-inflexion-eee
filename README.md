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

- **Factory functions** — three ready-to-use entry points that load the bundled Pratt lexica:

  ```python
  from greek_inflexion_eee import load_default, load_noun_default, load_adj_default

  gi = load_default()          # verb inflection
  gi = load_noun_default()     # noun inflection
  gi = load_adj_default()      # adjective inflection
  ```

- **Adjective morphology** — `adj_stemming.yaml` + `pratt_adj_lexicon.yaml` covering
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
from greek_inflexion_eee import load_default, load_noun_default, load_adj_default

# Verbs
gi = load_default()
gi.generate("λύω", "AAN")       # {'λῦσαι': [...]}

# Nouns (bundled lexicon covers Pratt paradigm words)
gi = load_noun_default()
gi.generate("θεός", "NSM")      # {'θεός': [...]}
gi.generate("θεός", "GSM")      # {'θεοῦ': [...]}
gi.generate("σοφία", "NSF")     # {'σοφία': [...]}
gi.generate("βασιλεύς", "NSM")  # {'βασιλεύς': [...]}

# Adjectives
gi = load_adj_default()
gi.generate("ἀγαθός", "NSM")    # {'ἀγαθός': [...]}
gi.generate("ἀγαθός", "NSF")    # {'ἀγαθή': [...]}
gi.generate("ἀγαθός", "NSN")    # {'ἀγαθόν': [...]}
```


## Origin

Forked from [jtauber/greek-inflexion](https://github.com/jtauber/greek-inflexion)
by James Tauber. The upstream library and its data (stemming rules, Pratt/Dik/Homer
lexica) are the work of James Tauber and contributors; see [AUTHORS](AUTHORS) and
[LICENSE](LICENSE).

This fork is maintained by
[Ελληνικά Εκπαιδευτικά Εργαλεία (EEE)](https://codeberg.org/eee) —
Greek Language Educational Tools.
