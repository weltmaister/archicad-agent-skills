# BIM element modeling rules (office-grade semantics)

Distilled, in our own words, from the official German Graphisoft modeling guideline
("BIM Modellierungsrichtlinien für Archicad", GRAPHISOFT Deutschland GmbH,
CC BY-NC-SA 4.0, free PDF at pub.graphisoft.de) plus community sources
(runxel.xyz Archicad wiki, Graphisoft Community KB). Use when creating elements
that must survive as a real BIM model — quantities, IFC, AVA handover — not just
look right in 3D. Target detail level of the guideline: the as-designed building
at 1:50 (structural shell exact, finishes as separate real elements, no
fabrication detail).

## The mandatory semantic triple

Every created element carries three semantic attributes, set right after creation
and confirmed by readback:

1. **Classification** (e.g. Wand, Rohbaudecke, Fundament - Streifenfundament,
   Bekleidung/Belag - Dämmung, Dach, Dachkonstruktion, Raum)
2. **Structural function**: load-bearing / non-load-bearing (tragend / nicht tragend)
3. **Position**: interior / exterior (courtyard-facing walls are EXTERIOR — see
   wall-reference-lines note)

Geometry without these is not a BIM element: they drive IFC export, structural
filtering, and quantity handover. For segmented columns/beams classify either the
parent element or its segments, never both — classifying both double-counts in
schedules.

## Tool choice is semantic, not geometric

| Building part | Tool (create command) | Classification | Notes |
|---|---|---|---|
| Strip footing | Wall or Beam | Fundament - Streifenfundament | profile for complex sections; top = top of floor slab |
| Pad footing | Column | Fundament - Punktfundament | |
| Balcony slab | Beam | Rohbaudecke | precast: segments with different profiles |
| Thermal-break element | Beam | Bekleidung/Belag - Dämmung, load-bearing | |
| Insulation strip / fire barrier at slab edge | Beam (profiled) | Bekleidung/Belag - Dämmung | wall then stops at slab soffit — overlap double-counts |
| Parapet (Attika) | Wall | Wand | coping = separate Beam |
| Ring beam / foot purlin | Beam | Dach | |
| Suspended ceiling | Slab | Bekleidung/Belag - Abgehängte Decke | composite with explicit air layer |
| Services reservation volume | Morph | Raumvorschlag | |
| Terrain | Mesh (Freifläche) | — | never slab or morph |
| Guardrail | Railing or Wall | Geländer | |

The classification declares what the element IS — a beam-tool balcony is still
classified Rohbaudecke.

## Walls

- **Per storey, raw slab to raw slab:** bottom = top of the structural slab of the
  home storey, top = top of the structural slab of the storey above. Never one
  wall spanning multiple storeys — sill heights, per-storey quantities and story
  edits all depend on it. (Tapir: `floorIndex` + per-storey `height`.)
- **Reference line on the outer face of the CORE** (Kern außen) for exterior
  walls — finish/insulation thickness can then change without moving the
  structural shell line. Interior walls centered. (Refines the class rule in the
  wall-reference-lines note: outer CORE face, not outer finish face.)
- Load-bearing interior walls run raw slab to raw slab; non-load-bearing
  partitions may instead stand on the screed and stop at the slab soffit
  (lowered by the floor-finish thickness).
- Draw exterior perimeter loops **counterclockwise** so the exterior face lands
  consistently (Tapir walls: the body extends LEFT of the drawing direction).

## Slabs and floor build-ups

- The structural slab (Rohdecke) is ONE single-layer load-bearing element,
  classification Rohbaudecke. The ground slab extends exactly to the outer face
  of the structural wall core — not to the insulation face.
- The floor build-up (Fußbodenaufbau) is a SEPARATE non-load-bearing multi-layer
  slab **without a core**, modeled per room or per area — finishes differ room by
  room. Never merge structure and finishes into one composite slab.
- A flat roof's structural slab is classified **Dachkonstruktion**, NOT
  Rohbaudecke.

## Roofs (decomposition)

- Pitched roofs are several elements: a non-load-bearing covering roof
  (Bekleidung/Belag - Dachdeckung) separate from the load-bearing
  rafter/insulation roof (Dach), plus ridge/eave members (ring beam, foot
  purlin) as Beam elements (Dach).
- Model gable walls over-height, then trim them to the roof.
- Tapered flat roof: minimum-thickness insulation as a slab, tapered
  insulation/skin as single-pitch Roof elements; parapet = wall on the slab with
  a separate beam as coping.

## Openings

- **One Opening element per penetrated component** — a duct through wall + slab
  = two openings, so each exports as its own IfcOpening.
- Empty wall openings meant as future windows/doors still use
  `CreateWindows`/`CreateDoors` + classification — never generic openings (see
  the doors/windows rule in the schemas reference).
- A polygon hole cut into a slab does NOT export as an IfcOpening — use real
  Opening elements when the void must be semantically visible downstream; avoid
  Solid Element Operations for large voids (atria).
- **Orientation is fixed at placement:** exterior side / opening side must be
  right in the create payload (`reflected`/`oSide`/`refSide`); fixing later works
  only through `ModifyDoors`/`ModifyWindows` flags, never by moving or rotating
  the element.
- **Story assignment of windows/doors is height-derived** (the storey containing
  >50% of the element's height), NOT inherited from the host wall. A readback
  showing a different storey than the wall's home storey is expected behavior,
  not an error — but flag floor-to-ceiling openings on split-levels.

## Junction cleanup gates

Two elements clean up ONLY if all three hold:

1. the bodies physically touch,
2. their reference lines meet or intersect in plan (touching faces alone do
   nothing),
3. their layers share the same **intersection-group number** (different numbers
   = never intersect; 0 = the element is excluded entirely).

Only then does **building-material priority** decide who cuts whom. Consensus
ladder: structural concrete > structural steel/timber > insulation > air >
non-structural masonry > finishes. Model junctions by letting structural cores
overlap and priorities resolve the cut — do not trim geometry manually to fake a
connection. SEO operator bodies keep participating in priority intersections:
park them on a dedicated layer with intersection group 0 and a low-priority
material. When created elements fail to clean up, check the layer's intersection
number before suspecting geometry. (Collision checks cannot see priority-based
cuts; set intersection groups to 0 on the layers under test to expose all
overlaps.)

## Zones

One zone per room, **inner-edge** construction method, classification Raum, from
top of structural slab to the slab soffit (or the suspended-ceiling soffit when
the plenum is modeled as an air layer). Record the floor-build-up thickness in
the zone — DIN 277 areas and volumes derive from it. Zone areas double as QA:
compare computed areas against the room areas printed on the source plan
(typical tolerance 1-2%); a zone that cannot auto-detect its boundary marks a
hole in the wall loop — fix topology, never hand-draw the zone polygon.

## German term traps (plans and user requests)

| German | Archicad/API concept |
|---|---|
| Ebene | Layer (NOT storey!) |
| Geschoss | Story |
| Freifläche | Mesh |
| Fassade | Curtain Wall |
| Schraffur | Fill |
| Verbinden | Intersect |
