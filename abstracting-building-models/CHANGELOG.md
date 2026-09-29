# Changelog — abstracting-building-models

SemVer; `metadata.version` in the SKILL.md frontmatter mirrors the current version.

## [2.0.0] — 2026-09-29

Single-source consolidation: this repository is now the one and only version of the skill — the
former private and public lineages are merged. The installed `.skill` package is built directly
from this tree.

- The 52-line "Positioning un-dimensioned elements" block moved from the SKILL.md body to
  `references/positioning-un-dimensioned-elements.md` (token-efficiency pass from the private
  lineage); the body keeps the core rule (constraint-first, never pixel-first) with a pointer.
- New References note: which optional model fields to fill when the model is destined for the
  rule-driven Archicad build (`archicad-automation` → `scripts/build_from_model.py`).

## Earlier history

Maintained privately (German, up to 1.4.1) until 2026-09-29; archived outside this repository.
