# Measured-plan intermediate model

Use this note when a measured floor plan must become a durable intermediate model for later Archicad editing, rebuilds, or repeat verification.

## Goal

The intermediate model should let a later session answer all of these without re-interpreting the whole drawing from scratch:

- what is the accepted outer contour?
- which walls are explicit and which are simplified?
- which openings belong to which walls?
- which dimensions came from the sheet, and which came from user assumptions?
- where do uncertainty branches remain?

## Recommended content

### 1. Global frame
- units
- origin choice
- source page id / image path
- accepted overall extents
- orientation statement

### 2. Wall representation
For each wall or wall segment, keep:
- axis or face-pair geometry
- thickness
- storey / z basis
- confidence
- source evidence
- whether it is part of the canonical model or only an alternative branch

Important: if the source shows stepped or notched geometry, preserve that branch explicitly instead of flattening it too early into one long wall.

### 3. Opening representation
For each door/window/opening, keep:
- host wall id in the intermediate model
- explicit source-chain evidence or witness geometry
- width / height / sill basis
- center-offset if known
- if center-offset is not yet known, enough anchor geometry to derive it later without re-reading the whole sheet

### 4. Room / zone representation
Keep:
- room polygon
- room name / label
- area if explicit
- adjacency notes if important for wall interpretation

### 5. Dimension-chain evidence
Group dimension strings by role, not only by raw text order:
- overall building size
- facade / room subdivisions
- openings and piers
- wall thicknesses

This grouping is what later lets Archicad automation rebuild openings and dimension chains systematically.

### 6. Uncertainty ledger
Track unresolved issues explicitly:
- competing wall interpretations
- stair / built-in ambiguities
- places where the drawing is occluded or low-resolution
- project assumptions supplied by the user (for example storey height or sill height) that are not visible in plan

## Rebuild handoff rule

If a rebuild becomes preferable, the intermediate model should be rich enough to drive:
1. wall recreation,
2. opening recreation,
3. zone recreation,
4. post-rebuild overlay verification,
without depending on the old broken live model as the primary truth source.

## Case-derived warning

In one measured-plan case, the interior core around the bathroom / utility room / stair had close parallel source lines with different extents. That is exactly the kind of area where a too-simple intermediate model creates a plausible but wrong Archicad rebuild. Preserve the branch or uncertainty rather than force a single straight wall too early.
