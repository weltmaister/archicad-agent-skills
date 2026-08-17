# Measured-plan proof and Archicad handoff

This note captures a reusable workflow correction from measured-plan reconstruction work.

## Primary rule

Archicad construction should consume an element-parameter model, not a copied PDF/vector line model.

A line trace can be a useful proof layer for a clean vector PDF, but it is not a BIM construction strategy and will fail as soon as the source is a distorted bitmap scan. The construction input must state what each element is and which dimension chain controls it.

## Required handoff fields for Archicad construction

For each element class:

### Exterior walls
- wall ID
- reference line endpoints
- thickness
- reference side / outside face convention
- associated overall/detail/subdivision chains

### Interior walls
- wall ID
- reference line or face pair
- thickness
- associated interior/room/core chains
- uncertainty branch if wall pair/extents are ambiguous

### Doors/windows
- host wall ID
- type: door/window/opening
- width
- span or center offset along host reference line
- source chain(s)
- symbol/handing confidence

### Columns
- center or bbox
- size if known
- source evidence: symbol recognition + chain relation

### Stairs and objects
- bbox/polygon/control extents
- type candidate
- dimension-chain relation or explicit source evidence
- native Archicad parameterization status

### Rooms/zones
- name
- center and/or polygon
- surrounding wall references when available

## Proof routine requirements

A useful proof routine should report by layer, not only one global pixel score:

- building linework
- dimension linework
- text / numeric dimension strings
- room labels
- doors/windows/opening symbols
- stairs/objects/fixtures
- columns

The stop criterion is per-layer: no relevant missing/extra elements, all accepted dimension chains close within tolerance, and the fresh published output visually matches the source.

## Text pitfall

If the live automation registry lacks a true CreateText/TextBlock tool, do not substitute leader labels for plan text. In an observed workflow, `elements_create_labels` created real PDF-extractable text but also leader lines/arrows that corrupted the drawing. Treat missing true text creation as a capability gap and keep text in the proof report until a non-leader text tool exists.
