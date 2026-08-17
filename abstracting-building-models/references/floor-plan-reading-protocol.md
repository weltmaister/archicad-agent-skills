# Floor-plan reading protocol for BIM handoff

Use this when a measured floor plan must become an Archicad/BIM model and the source is a normal architectural floor plan, not an already-structured CAD/BIM export.

## Non-negotiable principle

Do not begin by making line geometry fit. A floor plan is a conventional architectural drawing: a horizontal section plus visible/overhead symbols, dimensions, room semantics, and line weights. The task is to read building elements, not to copy graphics.

The correct order is:

1. Read sheet and drawing conventions.
2. Read dimension-chain hierarchy.
3. Classify element types.
4. Attach each element to the governing dimension evidence.
5. Build a parameter model.
6. Only then hand off to Archicad construction.

## Source hierarchy for geometry

1. Written dimensions and dimension-chain witness lines.
2. Element symbols / line weights / hatches / room labels.
3. Cross-checks from sections/elevations/schedules if available.
4. Raster/vector measurements only as secondary inference.

Never prefer pixel/vector length over a legible dimension string.

## Dimension-chain hierarchy

Read each side of the plan independently and classify chains by role before computing coordinates:

- `overall`: full documented extent on that side.
- `major_subdivision`: facade offsets, main body vs annex/terrace, large room spans.
- `openings_piers`: openings, piers, wall returns, small facade steps.
- `wall_thickness`: explicit wall thicknesses such as 0.31, 0.15, 0.12.
- `interior_control`: room/core/stair/wet-room dimensions inside the building.

Important: a value is not a coordinate by itself. It must be labelled as one of: wall thickness, clear room width, opening width, pier, facade return, terrace/column grid, stair/object control, or total extent.

## Element-class checklist

For every source plan, inventory these classes explicitly:

### Exterior walls
- Cut/heavy wall bodies forming the thermal/enclosed building boundary.
- Store wall face-pair or reference line, thickness, join endpoints, and which side is outside.
- Do not confuse a terrace/column field or exterior slab outline with the enclosed exterior wall.

### Interior walls
- Cut/heavy internal partitions, including short wall stubs and returns.
- Store wall body/face pairs, not only a simplified centerline.
- Use room labels and door openings to validate topology.

### Columns / piers
- Small square/rectangular structural symbols, often in terrace/carport/exterior fields.
- Store as columns/piers, not wall fragments.

### Doors
- Wall gap plus swing arc / sliding symbol / door leaf.
- Store host wall, rough opening width, swing side/handing, and whether it is exterior/interior/terrace door.

### Windows
- Thin rectangles/double lines within walls.
- Store host wall, rough opening width, sill height if visible, and type if symbol indicates it.

### Terrace doors / French doors
- Window-like opening plus door arc/diagonal or floor-level opening to terrace/balcony.
- Do not classify merely as window because it lies in an exterior wall.

### Stairs
- Treads, direction arrow/diagonal, landings, boundaries/railings/walls.
- Store stair bbox, baseline/path, flight width, number of visible treads if countable, start/end side, and uncertainty.
- A stair is never "just lines" in the handoff model.

### Objects / fixtures
- Kitchen counters/island/sink/cooktop, bathroom sanitary fixtures, washing machine, built-ins, furniture if part of plan semantics.
- Store as object/fixture class with bbox and symbol evidence.

### Rooms / zones
- Room label, likely polygon/enclosure, adjacency, function.
- Use rooms to check whether wall topology makes sense.

## BIM handoff schema requirements

Each element record must contain:

- `id`
- `kind` and `subtype`
- `geometry_parameters`
- `dimension_chains`
- `source_evidence` with page/image/text/symbol references
- `confidence`
- `uncertainties`
- `handoff_status`: ready / needs_more_recognition / blocked_by_missing_source

## Case-derived warning: closed dimensions are not element understanding

In one measured-plan training case, a mathematically closed dimension model still produced a wrong Archicad model because the drawing was not read as element classes:

- A documented `13.5 x 10.0` overall extent described the full extent including a terrace/column field, not a simple enclosed-main-body rectangle.
- The terrace on one side was an exterior field with columns and terrace doors, not a normal room inside the main body.
- The interior core (hallway / stair / utility room / bathroom) needed stair and fixture recognition; a handful of preliminary interior walls was insufficient.
- Opening positions must come from dimension chain + symbol + host wall, not from chain values alone.
- Kitchen, bathroom, and utility-room fixtures and stair symbols are required plan content and must not disappear in a rebuild.

If these classes are not all represented, stop and improve the source-element model before writing more Archicad geometry.
