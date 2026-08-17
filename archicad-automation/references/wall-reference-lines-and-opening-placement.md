# Archicad wall reference lines and opening placement

Use this note when a live measured-plan reconstruction shows inconsistent window/door sides, unclean wall joins, or dimension chains that attach to the wrong geometry.

## First-party source facts

Sources consulted:

- Graphisoft Archicad Help: Wall Reference Line — https://help.graphisoft.com/AC/24/INT/_AC24_Help/040_ElementsVB/040_ElementsVB-7.htm
- Graphisoft Archicad Help: Modify Wall Reference Line — https://help.graphisoft.com/AC/20/INT/AC20Help/03_1_Elements_Virtual_Building/03_1_Elements_Virtual_Building-18.htm
- Graphisoft Archicad Help: Specific Element Intersections and Junctions — https://help.graphisoft.com/AC/28/INT/_AC28_Help/040_ElementsVB/040_ElementsVB-272.htm
- Graphisoft API DevKit: `API_WindowType` — https://graphisoft.github.io/archicad-api-devkit/struct_a_p_i___window_type.html
- Graphisoft Community KB: How Walls are Connected in Archicad — https://community.graphisoft.com/t5/Getting-started/How-Walls-are-Connected-in-Archicad/ta-p/303922

Condensed facts:

1. Every Archicad Wall has a **reference line** and **direction**. The reference line is central to placement, editing, intersections, selection, and inside/outside surface definition.
2. Basic walls can have reference line at outside face, inside face, or center. Changing reference-line location can move the wall body laterally; `Modify Wall Reference Line` can move/flip the reference line while retaining the wall body's floor-plan position.
3. Wall-wall cleanup requires reference-line intersection/join. Graphisoft states that physical collision alone is not enough: wall reference lines must join or intersect. Layer intersection group and building-material priority then control the cleanup result.
4. Door/window placement is host-wall-relative. API fields include owner wall, center location (`objLoc` / Tapir `centerOffset` for straight walls), sill/parapet height, fix point, reveal/jamb depth fields, and side/orientation flags (`reflected`, `oSide`, `refSide` in Tapir reads). `startPoint` is measured from the beginning corner of the wall and rotated into the wall reference-edge direction; it is not a global plan point for straight walls.
5. Tapir's current simple create/modify schemas for doors/windows may expose only owner wall, centerOffset, width, height, and sillHeight. If side/orientation fields are not writable, the wall reference-line direction/location becomes the practical control over how the opening appears in plan. Do not assume `centerOffset` alone fixes inside/outside behavior.

## Root cause pattern: midpoint reference lines

A failed reconstruction converted wall **body polygons/BBoxes** into native Archicad walls by using the polygon midpoint as the wall reference line:

```python
if wall_bbox_is_horizontal:
    beg = (minx, (miny + maxy) / 2)
    end = (maxx, (miny + maxy) / 2)
else:
    beg = ((minx + maxx) / 2, miny)
    end = ((minx + maxx) / 2, maxy)
```

This is wrong for a measured-plan Archicad rebuild unless the intermediate model explicitly intended centerline walls and carried a consistent inside/outside convention. It loses:

- the intended wall reference-line position (outside face / inside face / center),
- wall direction consistency around the building perimeter,
- the closed reference-line graph at outside corners and T-junctions,
- which side of the wall is exterior/interior for hosted openings,
- stable witness geometry for exterior dimension chains.

In a live case this produced exactly the observed symptoms: windows sometimes rendered toward the inside and sometimes toward the outside, outer corners were not clean architectural wall joins, interior walls drifted by half-thickness or more, and facade dimension chains could only measure the broken current geometry.

## Correct workflow

Before placing doors/windows or dimensions:

1. Build a source-derived **wall reference-line graph**, not only wall body polygons.
   - For exterior walls, choose and record one convention: e.g. reference line on the exterior face with a consistent loop direction, or centerline with explicit inward normal/body side. Do not mix conventions.
   - For every corner, reference-line endpoints must meet exactly when that is the selected convention; do not rely on body-overlap cleanup.
   - For T-junctions, the interior wall reference-line endpoint must meet the host wall reference line or intentionally intersect it.
2. Create/modify walls from that graph, including thickness, offset/reference-line convention, building material, and layer intersection group.
3. Verify wall joins before adding openings:
   - bounding boxes are not enough;
   - use wall detail/reference-line readback when available;
   - otherwise reconstruct expected reference lines from the payload you used and publish/check reference-line-visible or plan-overlay evidence.
4. Place windows/doors only after the wall graph is correct.
   - For straight walls, derive global opening center from `wallBeg + centerOffset * wallDir`.
   - Keep `centerOffset`, `width`, `fixPoint`, and host wall direction together as one invariant.
   - If `reflected`/`oSide`/`refSide` cannot be written through the current Tapir schema, do not try to repair inside/outside by random offset edits. Fix wall direction/reference-line convention first or request/export a richer Tapir side-setting tool.
5. Create dimensions last, and only against the real intended wall/opening geometry. If dimensions show wrong values, treat that as evidence that geometry/reference lines are still wrong, not as a dimension-formatting issue.

## Immediate stop conditions

Stop mutating and diagnose instead of continuing when any of these are true:

- exterior wall bodies look plausible but reference-line graph is not proven;
- openings visually alternate between inner and outer wall side;
- exterior wall endpoints overlap/cross when the chosen convention requires endpoint meeting;
- dimensions measure current wrong geometry rather than the source control grid;
- `elements_get_details_of_elements` fails due to additive fields such as `WallDetails.thickness` and the workflow would otherwise rely on that readback.

## Mutation discipline after a reference-line failure

When a measured-plan reconstruction has already been flagged as stagnant or visibly wrong, do not continue with explanatory reports alone. Execute a bounded live correction batch and verify it, but keep the report brutally honest:

1. delete hosted openings and dependent dimensions before changing wall reference-line direction/endpoints;
2. modify the wall graph first, then recreate doors/windows from recalculated host-wall offsets;
3. recreate only dimensions that are proven by `GetDimensionData` and the fresh published PDF;
4. immediately delete any probe dimensions that collapse to zero or bind to the wrong witness points;
5. publish, re-render the fresh PDF, and report each target as `OK` / `not OK` rather than describing partial progress as success.

### Dimension API pitfall: zero-valued Slab witnesses

In a live case, attempts to create overall dimensions from Slab witnesses (`line=true` and several `special=1` / `inIndex` edge probes) created Dimension elements but read back as zero-valued witness points in `elements_get_dimension_data`. Those probe dimensions were deleted immediately. Lesson: if overall chains like `13,50` / `10,00` are needed, do not assume Slab witnesses will work through the current Tapir associative-dimension API. Probe one minimal chain, inspect `GetDimensionData`, and keep only non-zero chains whose witness coordinates match the intended real elements. If no real-element witness works, report the API gap explicitly instead of leaving fake or zero-value dimensions in the model.
