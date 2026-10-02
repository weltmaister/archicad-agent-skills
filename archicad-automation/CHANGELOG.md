# Changelog — archicad-automation

SemVer; `metadata.version` in the SKILL.md frontmatter mirrors the current version.

## [3.1.0] — 2026-10-02

Synced to Tapir **1.6.0** (installed and live-probed on AC26 and AC28).

- New section "New since release 1.6.0" in `references/tapir-verified-command-schemas.md`:
  - `DeleteElements` now answers `executionResults[]` per element (breaking); deletes on hidden or
    locked layers are reported honestly; a nonexistent guid is reported as deleted, and after a
    real element it stops that element's deletion.
  - Text size is set via `details.typeSpecificDetails.height` (top-level `details.height` → 4002);
    on AC25–AC27 text content is truncated to the first character (upstream #735 open).
  - Release-note items not yet probed (SaveProject from any window, non-ASCII story names,
    top-story height, new commands/fields).
  - `CreateStairs.treadDepth` still ignored (#425, re-verified).
- SetStories: the "#574 ineffective on AC28" status is replaced by the isolated cause — one-call
  level changes converge only while the active story is at or below the lowest changed story;
  recipe (activate via navigator first) plus two-pass fallback.
- `ChangeWindow.storyIndex` confirmed as a no-op on 1.6.0 (AC26 and AC28); the navigator path is
  AC27+, so AC25/AC26 cannot activate a story through Tapir.
- Hidden-layer gotcha narrowed: deletes are honest since 1.6.0, SetDetails/MoveElements not re-tested.
- `archicad-host-ui-state-and-publisher-recovery.md`: SaveProject 3D-window failure marked as
  releases <= 1.5.9 (fix listed in 1.6.0, not yet verified).
- SKILL.md: golden rules for the new DeleteElements shape and the AC-version traps.

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
