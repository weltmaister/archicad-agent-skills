# Modelling rule catalog — fixed rules for the build script (as of 2026-09-29)

Catalog for `scripts/build_from_model.py` (plan, build, verify) and `scripts/modeling_rules.py` (rules as
data): every rule that **always** applies, with source, implementation, independent check and status.
Situational decisions live separately in part F — there the script sets a documented default that the
intermediate model can override. The IDs are the same ones the verification report (`rule checks: …`) counts.

**Sources.** `MR` = Graphisoft Deutschland, *BIM-Modellierungsrichtlinien Archicad 29* (German BIM modelling
guideline for Archicad 29), dated 2026-03-09, licensed CC BY-NC-SA 4.0 (page numbers, paraphrased).
`BR` = `bim-element-modeling-rules.md`, `WR` = `wall-reference-lines-and-opening-placement.md`,
`VS` = `tapir-verified-command-schemas.md`, `OT` = `opening-side-triad-oside-reflected-refside.md`,
`SK` = `SKILL.md`, `L29` = live probes 2026-09-29 (AC28 GER, Tapir 1.5.9, a German office template in an
unnamed test project; part H).

**License note for this file.** The rules marked `MR` paraphrase that guideline; this reference file is
therefore shared under **CC BY-NC-SA 4.0** with attribution to Graphisoft Deutschland, separately from the
repository's MIT license. The scripts implement the rules but do not reproduce the guideline's text.

**Status.** ✅ implemented + unit test · 🟢 live-verified (test house v4 and outbuilding, 2026-09-29) ·
◐ partial, limit named · ⛔ not achievable through Tapir 1.5.9 / the template, workaround named ·
🔶 situational (part F).

**Verification 2026-09-29 (test house v5, 73 elements, live run):** B1 73/73 · B2 134/134 · B5 40/40 ·
B6 14/14 · C1 12/12 · C2 12/12 · C3 26/26 · C6 7/7 · C13 1/1 · D1 4/4 · D2 4/4 · D4 4/4 · D8 1/1 · D9 3/3 ·
E1 29/29 · E4 1/1 · E9 1/1 · R2 4/4 · R5 4/4 · R6 4/4 · R7 4/4 · T1 2/2 · T6 4/4 · T7 1/1 · T8 4/4 ·
V8 10/10 → **RESULT OK** (26 groups). Outbuilding with a pitched roof: all checks passed, T4 2/2; only
T2 (ring beam) ⛔, see part G.

---

## A. Project and foundations

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| A1 | Model in metres; other units are not built (no silent scaling). | SK | `build_plan` → plan error | test | ✅ |
| A2 | Model near the project origin. | MR p.5 | warning beyond 1 km distance | test | ✅ |
| A3 | North = 90° (counter-clockwise from x). | MR p.5 | `GetGeoLocation.north` against π/2 | run warning | ✅ 🟢 |
| A4 | Before any height, fix the datum: ±0.00 = top of finished floor (OKFF) or top of raw slab (OKRD). | MR p.6, SK | `metadata.level_datum`; if missing, inferred from the slab tops (note) | test | ✅ 🔶 |
| A5 | Fix whether the raw slab belongs below or above its story. | MR p.6 | `metadata.slab_story` (`below` default) | test | ✅ 🔶 |
| A6 | The story at ±0.00 has index 0, basements are negative; the script never creates stories. | VS | abort when a needed story is missing; warning on wrong numbering | test | ✅ |
| A7 | Foundations on their own story; the ground slab stays the slab of the lowest building story. | MR p.8 | warning for a foundation on a story with walls/rooms | test | ✅ 🟢 |

## B. Semantics — every part: classification, load-bearing function, position, layer, composite

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| B1 | Every part classified (Archicad classification), never "unclassified" — office favorites do not bring a classification along. | MR, BR | `SetClassificationsOfElements` with system AND item GUID, item resolved by path | read-back per element | ✅ 🟢 |
| B2 | "Tragende Funktion" (load-bearing function) and "Lage" (position) per role (table B-T). Set through `API.SetPropertyValuesOfElements` with the **non-localised** value (`LoadBearingElement`, `Exterior` …); openings take only "Lage" ("Tragende Funktion" is read-only there). | MR, L29 | `_write_semantics` | `API.GetPropertyValuesOfElements` (language-neutral) | ✅ 🟢 |
| B3 | An interior wall's unknown load-bearing state is not guessed ("Nicht definiert" + warning). | MR p.20 | role `interior_wall.from_model` | test | ✅ |
| B4 | Classify the whole part or its segments, never both. | MR p.11 | single-segment parts only, classification on the element | — | ✅ |
| B5 | Layer per office template (names, never hard-coded indices). | VS, L29 | `SetDetailsOfElements.layerIndex` | read-back | ✅ 🟢 |
| B6 | Composite from the office file by name; wall favorites with a composite structure arrive single-skin through `CreateWalls` → always send the structure explicitly. | VS, L29 | `structureType` + `compositeId`/`buildingMaterialId` | `details.structureType/compositeId` | ✅ 🟢 |
| B7 | Empty window/door openings with the window/door tool, classified as window/door. | MR p.31 | `window`/`door` → CreateWindows/Doors | — | ✅ |
| B8 | Never create or overwrite attributes or favorites; favorites only at creation, never afterwards (`ApplyFavoritesToElements` moved an upper-story morph by −3.00 m and a roof covering by +0.04 m, live). | SK, L29 | favorites only as `favoriteName` in the create call | test | ✅ 🟢 |

### Table B-T — role → tool, classification, load-bearing, position (MR, pages)

| Role | Tool | Classification | Load-bearing | Position | Notes |
|---|---|---|---|---|---|
| `exterior_wall` (8, 9, 12, 17-19) | wall, composite | Wand | yes¹ | exterior | core outside; raw slab top → raw slab top of the next story |
| `interior_wall` (20) | wall | Wand | model² | interior | raw slab top (or screed top) → underside of the slab above |
| `parapet` (29) | wall | Wand | yes | exterior | on the roof slab top, core outside |
| `railing` (13, 14) | wall | Geländer | no | exterior | the railing tool cannot be created through the API |
| `installation_wall` (22) | wall (profile) | Wand > Vorwand / Installationswand | no | interior | "subtract from room area and volume" |
| `strip_footing` (8) | wall | Fundament > Streifenfundament | yes | exterior | top = ground slab top, own story |
| `ground_slab` (8, 9) | slab, single-skin | Fundament > Bodenplatte / Flachgründung³ | yes | exterior | edge = outer face of the structural wall |
| `floor_slab` (12) | slab, single-skin | Decke > Rohbaudecke | yes | interior | ends at the inner core face |
| `roof_slab` flat-roof slab (28, 29) | slab, single-skin | Dach > Dachkonstruktion | yes | exterior | |
| `floor_buildup` (12, 20, 30) | slab, composite without core | Bekleidung / Belag > Fußbodenaufbau | no | interior | per room, holes instead of openings |
| `ground_insulation` / `roof_insulation` (9, 28) | slab | Bekleidung / Belag > Dämmung | no | exterior | |
| `suspended_ceiling` (15, 16) | slab, composite | Bekleidung / Belag > Abgehängte Decke / Deckenbekleidung | no | interior | per room, top = underside of the slab above |
| `window` / `door` (13, 31) | window / door | Fenster … > Fenster / Tür / Tor > Tür | no | as host wall | |
| `wall_opening` / `slab_opening` (30, 31) | opening | Durchbrüche / Schlitze > Öffnung | — | interior | one per penetrated part |
| `space` (7) | zone | Raum | — | — | inner edge, raw slab top → underside of the slab above |
| `column` / `pad_footing` (10, 11) | column | Stütze / Pfeiler > Stütze / Fundament > Punktfundament | yes | envelope / exterior | |
| `downstand_beam`, `lintel`, `balcony`, `thermal_break`, `insulation_strip`, `parapet_cover`, `ring_beam` (11-19, 23-29) | beam | Unterzug / Sturz / Rohbaudecke / Dämmung / Bekleidung / Belag / Dach | per role | per role | ⛔ in the tested template (T2) |
| `roof_structure` / `roof_covering` (23-27) | roof | Dach / Bekleidung / Belag > Dachdeckung | yes / no | exterior | pitched roofs always in two parts |
| `din277_body` (32) | morph | Raum | undefined | undefined | per story, "Klassifizierung nach DIN 277" |

¹ A model value `is_load_bearing: false` wins. ² MR p.20: variant 02 load-bearing or not → the value must come
from the model. ³ MR also allows "Rohbaudecke" (question F-3).

## C. Walls

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| C1 | Exterior wall/parapet: reference line core outside (`CoreOutside`); the model's outer face is offset inward by the skins in front of the core (first skin = exterior face), corners as intersections of the offset lines. | MR p.9, 12, 19 | `offset_ring`, `core_outside_offset` | `details.referenceLineLocation` | ✅ 🟢 |
| C2 | The body side depends on the mirror state (not mirrored: exterior side left of the drawing direction); wrongly lying ring walls are flipped with `ModifyWalls` **before** openings are placed. | L29 | `_build_walls` | 3D box inside the contour | ✅ 🟢 |
| C3 | Wall foot and top per role, per story: exterior wall raw slab top → raw slab top above, top linked to the story above (`relativeTopStory`/`topOffset`); a model height is replaced (note). | MR p.9, 12, 14; BR | `_wall_heights` | link + 3D box z | ✅ 🟢 |
| C4 | Topmost story: fixed height up to the roof slab top. | MR p.12 | note "not linked" | 3D box | ✅ 🟢 |
| C5 | Interior wall raw slab top → underside of the slab above (variant 02); on the screed only non-load-bearing and only on the model's request. | MR p.20 | `base: "screed"` | 3D box | ✅ 🟢 🔶 |
| C6 | Reference line of the remaining walls as sent (center); profile walls take it from the profile. | L29 | — | read-back | ✅ 🟢 |
| C7 | Junctions: reference lines must meet; a wall ending in another wall's body is moved onto that wall's reference line; parallel walls (a railing in front of the facade) are not a junction. | BR, WR | `_snap_wall_ends`, warning | test | ✅ 🟢 |
| C8 | Intersection through building-material priorities; the raw slab must cut the interior plaster (slab priority > plaster). | MR p.9, 12 | `_check_priorities` (warning) | test | ✅ |
| C9 | Segments < 0.20 m are not sent. | VS | `MIN_WALL_LENGTH` | test | ✅ |
| C10 | Composite thickness = model thickness (± 5 mm), otherwise a warning with its effect. | VS | skin-sum comparison | test | ✅ |
| C11 | Parapet on the roof slab top. | MR p.29 | role `parapet` | 3D box | ✅ 🟢 |
| C12 | Fall protection as a wall, classified as railing, non-load-bearing, exterior. | MR p.13, 14 | role `railing` | read-back | ✅ 🟢 |
| C13 | Installation wall: "subtract from room area and volume". | MR p.22 | `ModifyWalls.zoneRel = SubtractFromZone` | `details.zoneRel` | ✅ 🟢 |
| C14 | Strip footing top = ground slab top, own story. | MR p.8 | role `strip_footing` | 3D box | ✅ 🟢 |
| C15 | With an insulation strip/fire barrier in front of the slab, the exterior wall ends at the slab underside. | MR p.17, 18 | `insulation_strip.host_wall_id` | test | ✅ |

## D. Slabs

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| D1 | Raw slab single-skin, top = raw slab top of its story; role derived from the height (ground slab / floor slab / roof slab). | MR p.12 | `_classify_slabs` | 3D box z | ✅ 🟢 |
| D2 | Floor and roof slabs end at the inner core face of the continuous exterior walls. | MR p.12 | `core_in_ring` | outline read-back | ✅ 🟢 |
| D3 | Ground slab up to the outer face of the structural wall (core outside). | MR p.8, 9 | `ref_ring` | outline read-back | ✅ 🟢 |
| D4 | Floor build-up per room, composite without core, top = finished floor top; outline = the room polygon Archicad computed. | MR p.12, 20 | after the zones | 3D box z | ✅ 🟢 |
| D5 | No openings in the floor build-up, only holes. | MR p.30 | slab penetration → hole in the build-up above | test | ✅ 🟢 |
| D6 | Flat-roof slab: roof structure, load-bearing, exterior. | MR p.28, 29 | role `roof_slab` | read-back | ✅ 🟢 |
| D7 | Insulation as a slab: Bekleidung/Belag – Dämmung, non-load-bearing, exterior. | MR p.9, 28 | roles `*_insulation` | read-back | ✅ 🟢 |
| D8 | Suspended ceiling per room, top = underside of the slab above; the room reaches to that underside (variant 01) or to the suspended ceiling's underside (variant 02). | MR p.7, 15, 16 | `spaces[].ceiling` | 3D box z | ✅ 🟢 |
| D9 | Slab penetration with the opening tool, one per penetrated part (insulation too), one element per call; base point x = centre, y = top edge. | MR p.30, VS | `_build_host_openings` | 2D box | ✅ 🟢 |
| D10 | Slab material is not settable in `CreateSlabs` → favorite or `ModifySlabs`. | VS | favorite per role, else `ModifySlabs` | `structureType` | ✅ 🟢 |

## E. Openings

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| E1 | Sill in the model from finished floor top; Archicad measures from the wall bottom (= raw slab top) → `sillHeight` = model value + floor build-up. | MR p.9, 12, L29 | `metadata.sill_reference` | 3D box z | ✅ 🟢 |
| E2 | Floor-to-ceiling window: extended downward by the floor build-up. | MR p.13 | sill 0 → from raw slab top, height + build-up | 3D box | ✅ 🟢 |
| E3 | Openings in exterior walls swing inward (unless `swing: outward`). | live finding 2026-09-28 | — | E4 | ✅ 🟢 |
| E4 | `oSide = true` puts the swing left of the wall's drawing direction, regardless of the mirror state → set `oSide` only after the final wall direction. | L29 (corrects OT) | `_build_openings` | 2D box of the door (swing arc) | ✅ 🟢 |
| E5 | Window/door non-load-bearing, position = the host wall's position. | MR p.13, 31 | roles | read-back | ✅ 🟢 |
| E6 | No opening where another wall joins the host. | live finding 2026-09-28 | warning | test | ✅ |
| E7 | Opening fully inside its host segment. | WR | warning | test | ✅ |
| E8 | `centerOffset` = final wall start → opening centre (after core offset, snapping, flipping). | VS, WR | recomputation | test | ✅ 🟢 |
| E9 | Wall penetration: opening tool, base point on the wall line, z = absolute sill. Slot (niche) ⛔: `CreateOpenings` has no depth → skipped with a reason, not built as a through-opening. | MR p.31, L29 | `kind: opening` | property "Öffnung Brüstungshöhe zu Projektursprung" | ✅ 🟢 / ⛔ |
| E10 | Floor-to-ceiling window: carry the floor build-up into the reveal up to the frame. | MR p.13 | not implemented: the library part's frame position is not readable through the API (question F-13) | — | ◐ |

## R. Rooms

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| R1 | Zone tool, classification Raum. | MR p.7 | role `space` | B1 | ✅ 🟢 |
| R2 | Inner edge, automatic (associative) from a seed point; the template provides the inner-edge method. | MR p.7 | `geometry.referencePosition` | `isManual == false` | ✅ 🟢 |
| R3 | Never draw by hand: no closed wall ring → error, no polygon (only with `--allow-manual-zones`). | BR | default without fallback | test | ✅ |
| R4 | Before creating, activate the story through its navigator item (`ChangeWindow.storyIndex` reports success but does not switch). | L29 | `_activate_story` + `actStory` probe | count delta | ✅ 🟢 |
| R5 | Room raw slab top → underside of the slab above, top linked to the story above ("Abstand Oberkante"); topmost story through "Lichte Raumhöhe" (clear height). | MR p.7 | official API, length value | 3D box zMax | ✅ 🟢 |
| R6 | Floor thickness = the room's build-up. | MR p.7 | property "Fußbodendicke" | read-back | ✅ 🟢 |
| R7 | Room area as in the model (± 2 %). | SK | polygon area | read-back | ✅ 🟢 |

## T. Columns, beams, foundations, roofs, bodies

| ID | Rule | Source | Implementation | Check | Status |
|---|---|---|---|---|---|
| T1 | Column raw slab top → underside of the slab above, position per envelope; pad footing up to the ground slab top. | MR p.10, 11 | fixed height (top link through the API has no effect) | 3D box | ◐ 🟢 |
| T2 | Beams per role (a downstand beam hangs under the slab, `zCoordinate` = top edge). | MR p.11-29 | `_plan_beams` | length + z | ✅ / ⛔ in the tested template |
| T3 | Pad/pocket foundation with the column tool. | MR p.10 | role `pad_footing` | 3D box | ✅ 🟢 |
| T4 | Pitched roof in two parts: rafter layer with insulation (load-bearing) + roof covering above (level + t/cos α). | MR p.23-27 | `_plan_roofs` | lowest point | ✅ 🟢 (merging ⛔) |
| T5 | Flat roof: raw slab (roof structure) + insulation as a slab. | MR p.28 | roles `roof_slab` + `roof_insulation` | read-back | ✅ 🟢 |
| T6 | DIN 277 body per story along the outer contour, bottom = story level, class "Regelfall", displayed as outlines only without a cover fill. | MR p.32, L29 | `--din277` | z + DIN class (through Tapir) | ✅ 🟢 🔶 |
| T7 | Building-services area as a morph: Raum > Raumvorschlag, non-load-bearing, interior, on the services layer, dedicated building material. | MR p.15, 22, L29 | `technical_zones[]` | z | ✅ 🟢 |
| T8 | Site areas per DIN 277 as morph surfaces with "Flächenart nach DIN 277" (GF, AF, BF, UF; overlap allowed), without a cover fill. | MR p.33, L29 | `site_areas[]` | z + area type (through Tapir) | ✅ 🟢 |

## V. Interface, safety, verification

| ID | Rule | Source | Status |
|---|---|---|---|
| V1 | Tapir ≥ 1.5.9 (read-back of mirror state, reference line, top link); older builds are rejected before any change. | VS | ✅ |
| V2 | Floor-plan window active (otherwise Tapir counts 0). | VS | ✅ 🟢 |
| V3 | Live only with `--confirm` after a dry run; a dry run with `--port` reads the office catalog through a read-only sender. | SK | ✅ 🟢 |
| V4 | Hidden target layer → abort before any change (it freezes elements). | VS | ✅ |
| V5 | Attribute GUIDs per session by name; layers by name. | VS | ✅ 🟢 |
| V6 | Only fields from the 1.5.9 schema (strict schemas). | VS | ✅ 🟢 |
| V7 | `CreateOpenings` one element per call. | VS | ✅ 🟢 |
| V8 | Never infer success from return values: count delta per type and read-back of every rule (values can return `success` without effect). | VS, L29 | ✅ 🟢 |
| V9 | Enum properties: official API with the non-localised value; Tapir display values with umlauts ("Außen") are silently discarded. Exception "Klassifizierung nach DIN 277": only through Tapir (official API errors with 6702). | L29 | ✅ 🟢 |
| V10 | Classification needs the system AND item GUID. | VS | ✅ 🟢 |
| V11 | Re-verification any time, read-only: `--check report.json --port N`. | — | ✅ 🟢 |

## F. Situational decisions — default and model field

| ID | Decision | Default | Model field |
|---|---|---|---|
| F-1 | ±0.00 = finished floor (OKFF) or raw slab (OKRD) | inferred from the slab tops; template convention: OKFF | `metadata.level_datum` |
| F-2 | Raw slab below/above its story | below | `metadata.slab_story` |
| F-3 | Ground slab classification | Fundament > Bodenplatte / Flachgründung | `slabs[].role`/profile |
| F-4 | Non-load-bearing interior wall on the raw slab or the screed | raw slab | `walls[].base` |
| F-5 | Interior wall load-bearing state | never guessed | `walls[].is_load_bearing` |
| F-6 | Floor build-up per room | 0.15 m, favorite per finish | `spaces[].floor_buildup`, `floor_finish` |
| F-7 | Room up to the slab underside or the suspended ceiling | slab underside | `spaces[].ceiling.variant` |
| F-8 | Layer of the flat-roof slab / parapet | roof-structure layer / exterior-wall layer | office profile |
| F-9 | DIN 277 bodies on every build | off | `--din277` |
| F-10 | Swing, DIN left/right | exterior walls inward; hinge side not set | `openings[].swing` |
| F-11 | Room without a closed wall ring | error | `--allow-manual-zones` |
| F-12 | Wall top under a pitched roof (ring beam, gable) | model height | `walls[].height`, `top: "height"` |
| F-13 | Floor build-up in the reveal of floor-to-ceiling windows | not carried | — |
| F-14 | Layer of the DIN 277 site areas | area layer | office profile |

## G. Limits (Tapir 1.5.9 / the tested template) and workaround

| Point | Limit (live-proven) | Workaround in the script |
|---|---|---|
| Beams (T2) | The tool default and all beam favorites of the tested template have fixed segment lengths (default 0.40 m, one precast favorite 10.00 m); `endCoordinate` and `ModifyBeams` do not change that | planned and checked; the verification reports the wrong length; remedy: switch the template's beam tool to proportional segmentation, or a Tapir fix |
| Slot / niche (E9) | `CreateOpenings` has no depth | skipped with a reason |
| Room bottom offset | not settable | template convention −0.15 = raw slab top on an OKFF story; deviations are reported |
| Column top link | `ModifyColumns.relativeTopStory` stays 0 | fixed height raw slab top → slab underside |
| Railing tool | no `CreateRailings` | wall, classified as railing |
| Favorites afterwards | `ApplyFavoritesToElements` is not geometry-neutral (morph −3.00 m, roof covering +0.04 m) | only `favoriteName` at creation; structure/layer/display explicit |
| Switching stories | `ChangeWindow.storyIndex` has no effect | navigator item (StoryItem) |
| Enum values through Tapir | display values with umlauts silently discarded | official API, non-localised values |
| "Merge elements", "trim to roof/shell", solid-element operations | not in the API | note in the plan; finish in the program |
| Profile manager (insulation wedge, profile beams) | existing profiles only | rectangle or an existing profile |
| Window frame "width at bottom" | library-part dependent | height/sill extended (E2); frame in the favorite |
| Zone construction method | not settable | template provides inner edge (verified) |
| Morph surfaces below the cut plane | drawn with a cover fill across the walls | `useCoverFillType: false` for DIN 277 surfaces and bodies |

## H. Live findings 2026-09-29 (summary)

- Tested template: story datum = finished floor, build-up 0.15, raw slab 0.20 (zone base −0.15, top link story+1
  at −0.35; doors 0.15 above the wall bottom).
- Favorites bring layer, load-bearing function and position, but no classification; wall favorites with a
  composite arrive single-skin; the wall tool default was mirrored, the office favorites were not.
- Body side: not mirrored → exterior side left of the drawing direction, mirrored → right; `CoreOutside` puts
  the skins in front of the core on the exterior side; flipping through `ModifyWalls` works.
- `oSide = true` → swing left of the drawing direction (measured on the door's swing arc).
- Writable: classification, load-bearing/position (official API, non-localised), layer, zone floor thickness,
  "Abstand Oberkante" (top offset), "Lichte Raumhöhe" (clear height); "relative top story link" only through
  Tapir and only ≠ 0; "Klassifizierung nach DIN 277" only through Tapir.
- Wall penetration: `basePoint` = centre on the wall line, z = sill; its height is readable through the
  property "Öffnung Brüstungshöhe zu Projektursprung" (the 3D box degenerates).
- Roof: `level` = underside at the eave of the base polygon; lowest point = level − overhang · tan α.
- Building-material priorities (tested template): insulation 730–750, waterproof concrete 690, reinforced
  concrete 670, sand-lime brick 635, plasters 360–370, screed 330.
