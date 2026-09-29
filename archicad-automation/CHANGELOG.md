# Changelog — archicad-automation

SemVer; `metadata.version` in the SKILL.md frontmatter mirrors the current version.

## [3.0.0] — 2026-09-29

Single-source consolidation: this repository is now the one and only version of the skill — the
former private (German) and public (English) lineages are merged. The installed `.skill` package
is built directly from this tree.

### Merged from the private lineage
- Live findings 2026-09-29 (AC28 GER / Tapir 1.5.9) into `references/tapir-verified-command-schemas.md`:
  wall body side depends on the mirror state (`flipped`), `oSide` is drawing-direction-relative,
  enum properties need non-localised values through the official API, story switching only works via
  navigator items, `ApplyFavoritesToElements` is not geometry-neutral, fixed beam segment lengths.
- The corrected `oSide` semantics in `references/opening-side-triad-oside-reflected-refside.md`.
- New references: `source-and-office-standard-checklist.md`, `repair-vs-rebuild-decision.md`.
- SKILL.md: office-standard section, north-arrow rule, sandbox/host transport note, publish-ambiguity
  and helper-geometry golden rules, Teamwork safety item, pipeline output note.

### Deliberately not carried over
- Legacy references tied to a personal MCP-wrapper setup (case log, wrapper gap analysis, runtime
  recovery, training workspaces, transport probes, 1.5.0 validation notes). Their durable technical
  content had already been distilled into the remaining references.

## [2026-09-29] build_from_model (previously tracked privately as 2.13.0)

- `scripts/build_from_model.py`: builds a validated intermediate model in one run under a fixed
  modelling-rule catalog, with a pure plan phase, `--dry-run`/`--confirm`/`--check`, and read-back
  of every rule. `scripts/modeling_rules.py` holds the role table and an example office profile;
  `references/modeling-rule-catalog.md` documents every rule (that file is CC BY-NC-SA 4.0,
  derived from Graphisoft Germany's "BIM-Modellierungsrichtlinien Archicad 29").
- `tests/`: 134 unittest cases with a fake Archicad mirroring live-measured behavior.
- Live-verified 2026-09-29: 73 elements, all 26 rule groups passed.

## Earlier history

Maintained privately (German) until 2026-09-29; archived outside this repository.
