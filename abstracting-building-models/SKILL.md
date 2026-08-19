---
name: abstracting-building-models
description: Use when asked to turn architectural drawings — floor plans, sections, elevations, site plans, details, PDFs, or scans — into a structured parametric building model; to read or interpret measured/dimensioned drawings; to extract building geometry with evidence and uncertainty; to produce BIM-ready parametric JSON; or to prepare an evidence-backed intermediate model for Archicad automation.
license: MIT
metadata:
  version: 1.0.0
  author: weltmaister
---

# Architectural drawings to parametric building model

Use this skill when the task is to turn architectural sources into a structured building model: construction drawings, floor plans, sections, elevations, site plans, details, permit or working drawings, scans/PDFs, a live Archicad model, BIM (Building Information Modeling), CAD (Computer-Aided Design), IFC (Industry Foundation Classes), parametric JSON, geometry extraction, or drawing-driven Archicad modelling/inspection.

## Operating principle

Produce a **model with evidence**, not a pretty interpretation. Every inferred element should carry source references, confidence, units, and unresolved assumptions. Prefer explicit dimensions over pixel measurements; use pixel/vector measurements only to fill gaps and mark them as inferred.

## Inputs to request or use

Minimum useful bundle:
1. One or more **floor plans** per storey.
2. At least one **section** for heights, slab thickness, stairs, roof, and vertical relationships.
3. Elevations when facade openings, roof shape, or external levels matter.
4. Title block, scale, north arrow, level marks, and legends if available.

If only one drawing is available, still extract a partial model and label missing dimensions instead of blocking.

## Workflow

1. **Inventory drawings**
   - Identify drawing type: floor plan, section, elevation, site plan, detail, schedule.
   - Capture sheet metadata: title, drawing number, revision, scale, date, author, units.
   - Normalize orientation: north/up direction, view direction, and storey name.

2. **Calibrate geometry**
   - Use written dimensions first, then scale bar/title scale, then known object sizes.
   - **Dimension chains outrank drawn geometry — always.** Point/pixel coordinates of a PDF are
     never as accurate as the inscribed dimension text. Where a chain states a value (two
     decimals, or millimetres as a superscript), the model must hit exactly that value — not the
     result measured from coordinates. Procedure: (1) extract every dimension chain and **assign
     each chain to the element it dimensions** — that assignment is the real work, not the
     measuring; (2) accumulate the chain texts into an exact control grid; (3) place wall axes,
     edges, and openings on that grid — measured geometry serves only to match chain to element,
     never as the source of a value; (4) only where no chain exists does measured geometry
     govern — then rounded per "Snap to buildable values" (step 7) and flagged
     `derived-from-geometry`. (Typical failures without this rule: a parking grid measured as
     8.098/8.102/8.098 where the chain says 8.10 throughout; wall thicknesses measured as
     0.239/0.245/0.254 where the chain says 25 cm.)
   - If the plan carries NO dimensions and no scale bar, anchor the scale on one recognizable
     standard component (a double garage is ~6.0 m wide, a door leaf ~0.9 m, a parking bay ~2.5 m),
     pixel-measure everything from that anchor, and validate the result against catalogue standards
     (room areas, door/window widths) and overall rectangular closure before trusting it.
   - Establish coordinate system: origin, x/y axes, unit in meters or millimeters.
   - Keep original page coordinates in evidence so extraction can be checked later.

3. **Read drawing conventions**
   - A floor plan is a horizontal section, conventionally cut around 1.20 m above floor level.
   - A section is a vertical cut; use its A-A/B-B markers and arrows to locate the cut line in plan.
   - Broad solid lines usually mean cut elements; thin solid lines visible edges; dashed lines hidden/overhead; dash-dot lines cut planes/axes; hatching or fill indicates cut material.
   - Treat detail drawings as higher-scale overrides for the local assembly they show.

4. **Extract plan geometry**
   - Storeys/levels: names, elevations, floor-to-floor heights, finished floor levels.
   - Spaces: room polygons, names, numbers, areas, usage, adjacency.
   - Walls: centerline or face geometry, thickness, height, construction/material if known.
   - Openings: doors/windows attach to host wall with width, height, sill/threshold, swing/opening direction.
   - Structural/grid: axes, columns, beams, shafts, stair cores, chimneys, ducts.
   - Vertical circulation: stairs/ramps with start/end levels, rise, run, landing geometry.

5. **Extract sections/elevations**
   - Map section line in plan to section geometry; do not mix unrelated sections.
   - Derive heights: floor slabs, ceilings, roof ridge/eaves, terrain, foundations, sill/head heights.
   - Use elevations to validate facade openings and roof parameters.

6. **Reconcile all views**
   - Match elements across drawings by coordinates, dimensions, labels, axes, and adjacency.
   - Resolve conflicts by priority: explicit dimension > high-scale detail > section/elevation cross-check > scaled inference.
   - **If an overall dimension contradicts the sum of its segment dimensions (or two chains
     disagree): stop for that region.** Do not decide yourself, do not average, do not silently
     prefer one chain — name the conflict with both values and the difference, and let the user
     decide before modelling the affected region.

7. **Parameterize**
   - Convert raw lines into objects with parameters and constraints: wall length/thickness, opening offsets, room polygons, level heights, roof slopes, grid spacing.
   - Preserve constraints: parallel/perpendicular, alignment to axes, equal spacing, host relationships, storey membership.
   - Separate `observed`, `inferred`, and `assumed` values.
   - **Snap to buildable values — no chain means round to 5 mm, system-wise.** Architecture is
     never drawn finer than half a centimetre: model values like 0.919 / 8.098 / 0.239 are
     categorically invalid. Where a value must be derived from geometry, round to 5 mm — but the
     DIRECTION of rounding is a system decision, not arithmetic: (1) detect the system first
     (axis grid, recurring nominal dimension, module order), then round; (2) round GROUP-wise,
     not element-wise — values scattering around one target are all pulled to that target, not
     each to its own nearest 5 mm multiple; (3) a dimension that recurs identically is the
     system dimension — deviating single values are measurement noise or explainable specials
     (edge bays, junctions) and must be justified as such. Worked case: measured axis spacings
     8.473 / 8.352 / 8.348 / 8.348 / 8.478 with a chain giving a clear measure of 8.10 and
     25 cm walls → axis dimension 8.35, occurring three times → all inner bays snap to 8.35 and
     the edge bays are explained by the exterior-wall junction; element-wise rounding
     (8.475/8.35/8.35/8.35/8.48) would have destroyed the system.
   - **Before rounding, test for a masonry grid.** An existing building often sits in the
     nominal module of its masonry (DIN 4172 / brick formats); if so, wall thicknesses AND
     length/axis dimensions snap to the masonry dimensions, not to a neutral 5 mm grid — and
     off-grid walls date later alterations. Load `references/masonry-grid-calibration.md`.

8. **Validate**
   - Dimensions close: outer dimensions equal sums of segments within tolerance.
   - Spaces are enclosed; walls hosting openings exist; stairs connect valid levels.
   - Section heights are consistent with storey elevations.
   - Report unresolved ambiguities and request missing sheets only when needed.
   - If JSON is written to disk, validate it with:
     `python scripts/validate_model.py model.json`

## Output contract

Default output is concise Markdown plus JSON. For the JSON shape, see
`templates/parametric-building-model.schema.json`.

Include at least:
- `metadata`: source sheets, units, coordinate system, scale.
- `levels`, `grids`, `spaces`, `walls`, `openings`, `slabs`, `stairs`, `roofs`, `site` as applicable.
- `constraints`: alignments, host relations, equal dimensions, vertical correspondences.
- `evidence`: sheet id, view type, page coordinates, dimension text, confidence.
- `assumptions`, `conflicts`, `missing_information`.

## Confidence rules

- `high`: explicit dimension/label confirmed by another view or schedule.
- `medium`: explicit in one view or robust scaled measurement with clear scale.
- `low`: inferred from pixel geometry, ambiguous symbol, or partially occluded scan.
- Never fabricate hidden geometry. Model it as `unknown` or `assumed` with rationale.

## Common pitfalls

- Do not read a floor plan as a top-down photograph; it is a cut plane plus conventions.
- Do not infer heights from a plan alone unless a section/level note supports it or the user explicitly supplies a modelling height.
- Do not treat dashed/overhead/hidden lines as normal wall outlines without checking legend and context.
- Do not collapse existing/new/demolished elements when renovation drawings use colors or line styles.
- Do not ignore title-block scale changes; details often have different scales than the main plan.
- Do not output a single clean model without uncertainties; downstream automation needs evidence and conflict records.
- For measured but low-resolution PDFs, extract both PDF text and a rendered image. Use explicit dimension text for global calibration, then vision/pixel interpretation only for room partitioning, openings, and ambiguous details. Save a machine-readable intermediate JSON so Archicad automation can continue even if the tool connection fails.
- For measured-plan-to-Archicad work, do not output only wall body polygons/BBoxes and assume the Archicad layer can infer clean native walls. Include the intended wall reference line, wall direction, reference-line position (outside/inside/center or explicit body side/inward normal), thickness, and join endpoints. Door/window host side and centerOffset are meaningful only relative to that reference-line convention; omitting it causes alternating inside/outside openings and unclean wall junctions downstream.

## Measured-plan intermediate models

For measured floor plans that will drive later Archicad repair or rebuild, the intermediate model must be explicit enough that geometry can be recreated without re-reading the whole sheet each time. Do **not** output only a line trace, PDF vector copy, or pixel-vectorization as the model. A clean vector PDF may allow tracing, but that method does not generalize to distorted bitmap scans. The reusable abstraction must classify drawing content into element classes and attach source dimensions to those classes.

**Calibrate the raster before measuring.** If the source is an image/PDF, do not eyeball positions from a low-resolution inline view — get the file and establish a pixel-to-meter transform first: project dark pixels onto X and Y, read the strong wall lines, and pin origin+scale from two known dimensions (for example: x=0 at px 2878 and x=13.5 at px 6067 gives 236.2 px/m; y=0 at px 4623 and y=10 at px 2258 gives 236.4 px/m). Then **measure** ambiguous geometry — non-rectangular rooms, stair runs, fixture centres — from the calibrated image instead of guessing (an L-shaped utility room is found from the wall line under the stair, not assumed). Overlay the resulting model back on the calibrated raster as the end-check (see the calibrated-overlay verification in the `archicad-automation` skill).

### Positioning un-dimensioned elements (constraint-first, not pixel-first)

Some elements carry no dimension text (e.g. terrace columns, fixtures, stairs). Do **not** just pixel-measure them — pixels are within 0.05-0.15 m and unanchored. Instead **anchor them to the dimensions you already trust** and let pixels fill only what is left. Strategies, strongest first, combined:

1. **Constraint / alignment to dimensioned geometry** — un-dimensioned elements usually align with dimensioned ones (a column's outer face flush with the dimensioned terrace edge; an axis flush with a wall face or opening jamb; a fixture flush against a wall). Each such alignment fixes ONE coordinate exactly, with zero pixel error.
2. **Symmetry** about a dimensioned axis (building centre, opening centre). Measure roughly, then force exact symmetry (average the pair). Halves the measurements and removes bias.
3. **Regularity / module / grid** — repeated elements are usually equally spaced or on a module (often 12.5 cm). Fit the rough positions to an equal-spacing/grid model anchored at dimensioned endpoints (least-squares), instead of taking each centre independently.
4. **Standard / catalogue size for the DIMENSION** — an un-dimensioned element's size is almost always a standard product or library part (column 24/30, door leaf 0.885, standard sanitary-fixture sizes). Placing the correct library part gives the true size with no measurement.
5. **Sub-pixel centroid, not a single edge** — detect the whole outline (contour/Hough), fit a rectangle, take centroid + size, then snap to module. More robust than reading one edge.
6. **Cross-view** — a section/elevation often dimensions what the plan omits (heights, depths). Reconcile across views.
7. **Round to buildable values + carry an uncertainty flag** per coordinate ("exact-constrained" vs "measured plus/minus x") so only the genuinely uncertain ones need review.

**Pipeline:** fix constrained coordinates (alignment/symmetry) exactly, then sub-pixel-measure the remaining free coordinate, snap to module/standard, enforce global constraints (symmetry, equal spacing) by a small fit, take size from the library part/standard, and verify on the calibrated overlay. Example: 4 terrace columns become "outer face flush to terrace edge 13.50 (x exact) + symmetric about y=5.0 + standard column size", not four independently pixel-read squares.

At minimum, preserve:

- `outer_contour` and terrace / annex extents as separate evidence-backed geometry,
- wall axes or face pairs with the chosen abstraction level called out,
- element-class records for exterior walls, interior walls, columns, windows, doors, stairs, fixtures/objects, zones/rooms,
- for every constructible element, the relevant dimension-chain evidence (`overall`, `facade subdivision`, `openings/piers`, `wall thickness`, or interior control chain),
- openings with host wall, source-chain evidence, and either center-offset or enough witness geometry to derive it later,
- room / zone polygons, names, and areas,
- dimension-chain evidence grouped by chain role (overall, subdivision, openings/piers, wall-thickness),
- ambiguity branches where close parallel source lines or stair/built-in regions could imply more than one valid wall interpretation,
- explicit user/project assumptions separated from drawing observations.

When this deeper checklist is needed, load `references/measured-plan-intermediate-model.md`.

For measured-plan reconstruction that must generalize beyond clean vector PDFs, load the dimension-chain + element-recognition handoff note: `references/dimension-chain-element-parameter-handoff.md`.

For any case where the produced geometry looks like lines or where the user says the plan has not been understood, load the stricter floor-plan reading protocol: `references/floor-plan-reading-protocol.md`.

Important correction: PDF vector tracing or pixel vectorization may be used as diagnostic/proof evidence, but the primary reusable model must be constructed from dimension-chain grouping plus element classification: exterior walls, interior walls, columns, windows, doors, objects, stairs, rooms, and the dimension chain(s) that justify each element. If the element classes and their governing dimension chains are not represented, stop before writing more Archicad geometry.

## References

Load the condensed domain notes in `references/drawing-reading-sources.md` when deeper grounding is needed.

## Boundary with Archicad automation

Keep this skill focused on **reading, interpreting, and parameterizing building information from sources**: scans, PDFs, drawings, floor plans, sections, elevations, reference photos, precedent buildings, or an existing model that must be abstracted into a structured representation.

Do **not** let this skill become the whole Archicad automation playbook. If the user's request is primarily to operate Archicad itself — create/edit elements, use favorites, infer the office standard from the open file, set properties/classifications, or verify changes through the Tapir Archicad API — use `archicad-automation` instead. This skill may produce the evidence-backed intermediate model that `archicad-automation` consumes.

Routing examples:
- "Take these scanned floor plans and sections and build an Archicad model from them" — first use this skill to extract a parametric model with evidence, then use `archicad-automation` to create the file/elements.
- "Recreate the Villa Rotonda" — first use this skill for precedent/source research and parametric abstraction, then `archicad-automation` for creation.
- "Create an SVG from this floor-plan scan" — use this skill for drawing interpretation/vectorization output; Archicad is not needed unless explicitly requested.
- "Use the favorites in the open Archicad project and model a wall/zone/slab" — use `archicad-automation`, not this drawing-abstraction skill.
