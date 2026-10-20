# Changelog — archicad-automation

SemVer; `metadata.version` in the SKILL.md frontmatter mirrors the current version.

## [3.5.1] — 2026-10-20

- Protocol: which channel to use. Prefer the Tapir MCP server's tools when the session has them
  (discovery first - a fresh server rejects calls until then); direct HTTP is the fallback; a
  sandboxed agent shell cannot reach the host's ports and should get the MCP server instead of
  HTTP scripts run through a desktop-automation shell.
- Visual checks through `SaveCurrentWindowAsImage` instead of desktop screenshots (verified AC28,
  1.7.2: 0.1 s, foreground unchanged); GUI automation only for what Tapir cannot do, with consent.

## [3.5.0] — 2026-10-20

- New section "Documentation views: sections, details, drawings", from a live documentation
  session (AC26, Tapir 1.7.1): the recommended Detail-tool workflow (details marked in an existing
  1:50 section, 2D drafting in the Detail window, no separate section per detail), what the API can
  do there (2D drafting in a detail database, hatches without a closing point, section markers not
  readable), drawings and layouts (no `clipPolygon` on model-section drawings, default drawing
  titles, refreshing by recreating, layout texts, sheet numbering), dimensions in sections
  (`CreateAssociativeDimensionsOnSection` presets instead of ghost section witnesses, beam witness
  indices, dimension layers) and modelling details that affect documentation (locked layers,
  `zCoordinate` as bottom offset, building-material priority in sections).
- Level dimensions in that section updated: `CreateLevelDimensions` exists since 1.7.2.
- The description names sections, details and drawings on layouts.

## [3.4.1] — 2026-10-20

- New gotcha and golden rule: element queries work in the **active window's** database.
  `GetElementsByType` without `databases` lists the elements of the active view, so with a
  section open a floor-plan element is not found (verified AC28, Tapir 1.7.2).
- New section "Detail and Worksheet markers": read, move, rotate, change layer and delete work;
  placing a marker and changing its name, ID or clip polygon do not (requested upstream as
  #1377). `SetDetailsOfElements` reports `success:true` for `detailName`/`detailIdStr` and
  changes nothing. `RotateElements` takes absolute begin and end points.

## [3.4.0] — 2026-10-19

Synced to Tapir **1.7.2** (both instances updated through Tapir's own auto-update; live-probed on
AC26 and AC28 with the community test runner's checks).

- **The full command catalog is complete again.** It still listed Tapir 1.5.3 (about 180
  commands); it is now regenerated from Tapir 1.7.2's own command reference (314 commands, with
  group, introducing version and schemas) by the new `tools/generate_tapir_catalog.py`, which
  carries the hand-written notes over. Cross-cutting notes from the old trailing sections moved
  into one section at the top.
- New section "New since release 1.7.2": text content and size change on AC25–AC27 again (#886);
  `MoveElements`/`RotateElements` report elements they cannot edit (#861); verified examples for
  `GetQuantitiesOfElements`, `Get3DGeometryOfElements`, `CreateCurtainWalls`,
  `CreateLevelDimensions`, `CreateGridElements`/`GetGridElements`. Release-note items that were
  not probed are marked as such, among them the now required `parentNavigatorItemId` of
  `CloneProjectMapItemToViewMap`/`CreateViewsInViewMap` (#776).
- The text-modification warning applies to 1.7.0/1.7.1 only; the stale `ChangeWindow` note in the
  catalog is corrected.

## [3.3.0] — 2026-10-16

Synced to Tapir **1.7.1** (both instances updated through Tapir's own auto-update; live-probed).

- New section "New since release 1.7.1": `CreateSlabs` accepts structure, composite and building
  material at create; `CreateWalls` keeps a favorite's composite; `thickness` documented as
  Basic-only. Older notes marked as applying to releases <= 1.7.0.
- **Correction of 3.2.1:** the text-modification failure is not session state and not AC28. It is
  deterministic on AC25–AC27 for texts with two or more characters (AC26 verified across two
  sessions; one-character texts change fine; AC28 unaffected). The October 5 probes identified
  instances by port, and the ports had swapped. Workaround: delete and recreate.
- New golden rule: identify each Archicad by `API.GetProductInfo`, never by its port.

## [3.2.1] — 2026-10-05

- **Correction:** the "AC28 text modification regression in 1.7.0" is not a regression. It
  appeared in the first Archicad session after installing 1.7.0 and was gone after a restart;
  the same calls and the whole earlier probe sequence passed in the fresh session. Now documented
  as a session-state failure with "restart Archicad first" as the remedy (upstream #759).

## [3.2.0] — 2026-10-05

Synced to Tapir **1.7.0** (installed and live-probed on AC26 and AC28).

- New section "New since release 1.7.0": `ChangeWindow.storyIndex` works (#752), `SetStories`
  converges with any active story and restores it (#753), AC25-AC27 text content complete (#735),
  batch reads fast (#586); **regression on AC28: every text modification fails** (workaround:
  delete and recreate); #749/#751 and #425/#750 still unreleased.
- SetStories/ChangeWindow sections: the 1.6.0 workarounds are now marked as applying to
  releases <= 1.6.0 only.
- `build_from_model.py`: stories are activated via the navigator item and, if that is refused
  (AC25/AC26) or has no effect, via `ChangeWindow.storyIndex` (works since 1.7.0); each attempt is
  confirmed via `actStory`. Two new tests (137 total).

## [3.1.1] — 2026-10-02

- **Correction — roof `thickness` is not ignored** (live on 1.6.0, AC26 and AC28, both roof
  classes): a composite roof tool default makes the new roof `structureType:"Composite"`, and the
  composite defines the thickness. With `structureType:"Basic"` the sent thickness applies exactly.
  The earlier "single-plane branch bypasses thickness" note was a misreading; corrected in
  `tapir-verified-command-schemas.md` and SKILL.md (new golden rule: a tool default can override a
  sent value). `GetDetailsOfElements` returns roof details on 1.6.0.
- `build_from_model.py`: roofs without a resolvable composite are now sent as
  `structureType:"Basic"`, so the planned thickness applies; new test (135 total).

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
