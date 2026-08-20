# Tapir — verified command schemas (exact field names)

Authoritative field reference for the most-used Scan-to-BIM commands. Verified **live against Archicad 28 (Windows) running Tapir 1.5.x** and cross-checked against the add-on C++ source (`upstream/main`). When a create/modify call fails with `4002 ... additionalProperties` it almost always means a **wrong field name**, not a missing feature — look it up here first.

All commands go through the `API.ExecuteAddOnCommand` envelope (see SKILL.md "Protocol"). The field names below are the contents of `addOnCommandParameters`.

**This file** is the hand-verified gotchas + key-field layer for the most-used commands. For the **complete list of all ~157 registered commands** with their input/response schemas, see `references/tapir-full-command-catalog.md` (generated from the add-on source, v1.5.3, amended with post-1.5.3 merges).

## Version/build variance — mandatory probe at session start

**Never assume the documented catalog matches the connected instance.** Different machines run different Tapir builds against different Archicad versions (e.g. one instance on AC26 with release 1.5.3 while another runs a 1.5.4-dev build on AC28 — several commands and fields differ). At the start of every session against a new/uncertain instance:

1. `GetAddOnVersion` → log the version (e.g. `1.5.3` vs `1.5.4`).
2. **Command availability** via the official envelope (not a Tapir command): `{"command":"API.IsAddOnCommandAvailable","parameters":{"addOnCommandId":{"commandNamespace":"TapirCommand","commandName":"X"}}}` — scan your working command list. (`GetDoorsDetails`/`GetWindowsDetails` exist on NO build.) WARNING — **namespace trap (verified live):** `GetProductInfo` and `Get2DBoundingBoxes` are NOT Tapir commands on ANY build — they are **official API commands** and work without the wrapper: `{"command":"API.GetProductInfo"}` (returns version/buildNumber/languageCode) and `{"command":"API.Get2DBoundingBoxes","parameters":{"elements":[...]}}`. A "missing on build X" finding for these two is a namespace mix-up.
3. **Field probes** for version-sensitive fields (create a probe element far outside the model, read back, delete): `CreateWalls.arcAngle` → `4002 additionalProperties` means **< 1.5.4**; `GetStories` stories without `height` → **pre-#434**; `GetDetailsOfElements` wall details without `begThickness` → **<= 1.5.3**.
4. Cache the result as a per-instance command/field matrix in the project folder and consult it instead of re-probing.

Known variance (verified live). **Clean release gates exist since 2026-07-21:** release **1.5.4** (roll-up release: #428–#457) and **1.5.5** (+ #449 Morph, #458–#462). "<= 1.5.3" = all older releases:

| Feature | Releases <= 1.5.3 | Since release 1.5.4 (2026-07-21) |
|---|---|---|
| `CreateWalls`/`ModifyWalls` `arcAngle` | rejected (4002) → fallback: approximate the arc as a polyline of short segments, **chord error < half the wall thickness** | works (#435) |
| `GetStories` `stories[].height` | missing | works (#434) |
| Wall read-back `begThickness`/`endThickness` (normal wall) | missing (no thickness in read-back — track thickness in your own records) | works (= thickness, verified 0.365→0.365) |
| Zero-length wall in `CreateWalls` | **CRASHES Archicad** (data loss!) — ALWAYS sanitize source data | controlled per-item error, batch continues (#443) |
| Multi-segment (L/U) stair baseline | ALWAYS fails with `-2130313215` (#444) | works if the geometry is solvable (#445) |
| `CreateWalls.floorIndex`, `floorPlanPolygons`, `drawIndex` functional, `ChangeWindow.storyIndex` | missing | works (#436/#437) |
| Explicit `height` with a top-linked tool default (Walls+Columns, Create+Modify) | **ignored** (story link wins; template-dependent — cause of the old "height not honored" reports) | works — resolves the top link, height always applies (#446); WITHOUT `height` the link stays |
| Attribute family (`DeleteAttributes`, detail reads, new creates), Favorites complete, floorIndex in all creates | missing | works (#447/#448/#451) |
| Layout book & Navigator (#441) | missing | works |
| `UpdateZones`, full Morph coverage (Get/Create/Modify), 2D coordinate schema fix | missing | works **since 1.5.5** (#461/#449/#460) |
| `CreateRoofs` functional (multi-plane + NEW single-plane) | stub — every item returns `-2130313215` (#467) | works **since 1.5.6** (#482) |
| Keynotes + MEP (each AC28+), element grouping, 2D drawing elements, `ShowAlert`, drawing titles, `GetSpecialFolders`, `GetUserGSID` | missing | works **since 1.5.6** (#472/#473/#475/#484/#468/#464/#487/#478) |
| `SetStories` multi-story call | reliable (after the #423 fix in 1.5.3) | reliable |

## Common gotchas (these caused real false "feature missing" reports)

- **`ModifyWalls` top-level key is `wallsWithDetails`, NOT `wallsData`.** With the wrong key the whole call is rejected and it *looks* like height/thickness aren't supported — they are.
- **`CreateZones` polygon goes INSIDE `geometry`, not at the top level.** Top-level `polygonCoordinates` is rejected.
- **`CreateLabels` uses `text` + `begCoordinate`**, not `position`/`coordinate`/`content`.
- **`CreateWalls` `height`: template-dependent on releases <= 1.5.3, deterministic on fixed builds.** If the wall tool default is top-linked, the story link wins and the explicit `height` is ignored (cause of the old "height not honored" reports; on other templates it works). **Since release 1.5.4 (#446):** an explicit `height` resolves the link and ALWAYS applies (verified live: Create 2.2 / Modify 1.8). On releases <= 1.5.3: check/re-set the height with `ModifyWalls` after the create and verify via bbox.
- **There is NO `GetDoorsDetails` / `GetWindowsDetails`** — calling them returns `4010` (command not registered). Use **`GetDetailsOfElements`**, which returns width/height/sillHeight/centerOffset/reflected/refSide/oSide for doors and windows. (The rendered 2D door-swing image is not retrievable via the API; check the swing visually in the host.)
- **`DeleteElements` needs `{"elements":[{"elementId":{"guid":...}}]}`** — the shorthand `[{"guid":...}]` **fails silently AND returns `succeeded:true`** (verified live: the call succeeded while 0 of 2 walls were deleted — a common root cause of "it didn't delete" / "duplicate" confusion). Always re-check with a `GetElementsByType` count afterwards.
- WARNING — **Hidden layer = element is silently frozen (live-verified AC28, current main build 2026-08-20; = upstream issue #555).** While an element's layer has `isHidden:true`, BOTH `DeleteElements` AND `SetDetailsOfElements` return `succeeded:true` / `success:true` and change **nothing**; `DeleteElements` additionally **hangs >25 s** on some calls. There is no error anywhere in the response.
  - Live proof: a probe slab on a hidden layer — `SetDetailsOfElements` → new `layerIndex` returned success, readback unchanged; four `DeleteElements` calls returned success, `GetElementsByType` still listed the slab. After `CreateLayers {"layerDataArray":[{"name":"<that layer>","isHidden":false,"isLocked":false}],"overwriteExisting":true}` the **next** delete removed it immediately.
  - **Root trap:** creates without an explicit layer inherit the **tool default layer**, which can be a hidden one — such elements are born un-editable and un-deletable.
  - **Protocol before any delete/modify batch:** `GetAttributesByType(Layer)` → `GetLayers(attributeIds)` and check `isHidden` for every layer you will touch. If hidden: unhide via `CreateLayers` + `overwriteExisting`, mutate, then **restore `isHidden`** — the hidden state is part of the office template and must not be left changed.
  - This is the concrete mechanism behind "never infer success from a return value": here the return value is actively wrong, not merely uninformative.
- **Layers ARE fully manageable (corrected and verified live).** The full layer workflow works via Tapir — earlier "no layer setter" notes were a wrong-payload usage error.
  - **Set an existing element's layer:** `SetDetailsOfElements` with top-level key **`elementsWithDetails`** (NOT `elements`), each `{ "elementId": {guid}, "details": { "layerIndex": N } }`. Verified live: it sets `elem.header.layer` (wall moved layer 2→3, read-back confirmed). The common mistake is the wrong top-level key or putting `layerIndex` outside `details`.
  - **Create a layer by name:** `CreateLayers` → `{ "layerDataArray": [ { "name": "exterior-walls", "isHidden": false, "isLocked": false } ] }` (since 1.0.3; `overwriteExisting` optional). Verified live: created and confirmed via `GetAttributesByType`.
  - **List layers (names + indices):** `GetAttributesByType` → `{ "attributeType": "Layer" }`. Layer *indices* are stable within a file.
  - **Layer-true modelling from source OCG layers:** CreateLayers (ensure source layers exist) → GetAttributesByType (get indices) → create element → SetDetailsOfElements(layerIndex). No template file needed. (`ApplyFavoritesToElementDefaults` before create is an *alternative* for inheriting a favorite's layer; create commands themselves have no layer field.)
- **Read-back element wrapping:** `GetDetailsOfElements` / `Get3DBoundingBoxes` / `GetDimensionData` want `{"elementId":{"guid":...}}` items. Multi-element reads ARE stable on current builds — verified live with 30 elements in one call (AC28, 1.5.4-dev) and 25–45 in one call (AC26, 1.5.3). The old "query individually and retry" rule is only a fallback if a specific build/instance shows instability; don't pay the per-call overhead by default.
  - WARNING — **Instance-dependent — probe once per session.** On another AC28 instance (current main build, 2026-08-20) the opposite held: one `GetDetailsOfElements` with **10** elements hung for **>9 minutes** (300 s client timeout, never returned), while **30 single-element** calls completed in **576 ms total**. `Get3DBoundingBoxes` with 40 and even 5 elements timed out the same way. Cause unknown (`floorPlanPolygons` payload is a candidate). Therefore: at session start, time one 1-element and one 10-element read. If the batch is not clearly faster per element, loop single reads — 153 walls verified that way cost under 3 s.
- **Attribute GUIDs (building materials, composites, surfaces) change per file** → resolve them by name each session. Layer *indices* are stable.
- **Never infer success from a return value or counter** — always confirm with an independent live read-back (`GetElementsByType` count, `GetDetailsOfElements`, or `Get3DBoundingBoxes`).
- Strict schemas everywhere (`additionalProperties:false`): any unknown field rejects the whole item.

## Create commands

### CreateWalls — array key `wallsData`
- Required: `begCoordinate` {x,y}, `endCoordinate` {x,y}, `zCoordinate` (number), `height` (number, **ignored at runtime when the tool default top-links to a story — see gotcha above**), `thickness` (number)
- Optional: `offset` (number), `referenceLineLocation` (enum: `Outside`/`Center`/`Inside`/`CoreOutside`/`CoreCenter`/`CoreInside`), `structureType` (enum: `Basic`/`Composite`/`Profile`), `buildingMaterialId`/`compositeId`/`profileId` ({guid} via AttributeId), `arcAngle` (number, radians)
- **`arcAngle` makes a curved wall (PR #435 — only since release 1.5.4; on 1.5.3 → `4002`).** `begCoordinate`/`endCoordinate` are the **chord** endpoints; a non-zero `arcAngle` bulges the wall into an arc spanning that angle (e.g. `1.0` rad over a 4 m chord). Verified live: `arcAngle:1.0` → `Get3DBoundingBoxes` y-extent 0.79 m (vs ~thickness for a straight wall), and `GetDetailsOfElements` echoes `details.arcAngle:1.0`. Unlike the placement enums below, `arcAngle` **is** read back. On pre-1.5.4 builds approximate arcs as a polyline of short straight walls with **chord error < half the wall thickness**.
- **`floorIndex`** (optional, **since release 1.5.4, #437**): place the wall directly on a story by its index (as returned by `GetStories`); when provided, `zCoordinate` becomes a **bottomOffset relative to that story** instead of an absolute height. Avoids the fragile reverse Z→story calculation when stacking floors.
- **`referenceLineLocation="Outside"` works, but wall *direction* decides which side the body lands on. CORRECTED (re-verified live, four-wall rectangle test):** the reference line sits on the drawn coordinates; the wall body extends to the **LEFT-hand side of the drawing direction** (begin→end). So for a closed perimeter where the reference line must lie on the building outer edge AND the body must fall **inside**, walk the outline **COUNTER-clockwise with y pointing up**: South (0,0)→(11,0), East (11,0)→(11,10), North (11,10)→(0,10), West (0,10)→(0,0). Drawing it clockwise leaves the reference line on the contour but pushes the body **outside** (verified: all four bboxes protruded, e.g. west wall `x[-0.3,0]`), enlarging the building by the wall thickness. (An earlier version of this note claimed the opposite/right-hand rule — that was wrong; counter-clockwise is correct.) ALWAYS confirm with `Get3DBoundingBoxes`: the body must stay within the contour, not protrude.
- **Zero-length walls (`begCoordinate == endCoordinate`): build-dependent!** Since release 1.5.4 (**#443**) the item returns a controlled per-item error (`-2130313112` / APIERR_BADPARS, "Zero-length wall..."), the rest of the batch continues, and Archicad stays alive (verified live). On **older releases** a zero-length wall **CRASHES Archicad** (data loss!). Always sanitize source data (drop walls < 0.2 m) before batching — the guard is a safety net, not a license.

### CreateColumns — array key `columnsData`
- Required: `coordinates` {x,y,z} (3D)
- Optional: `height`, `axisRotationAngle` (rad), `width`, `depth` (rectangular only), `coreAnchor` (enum 3×3 grid: `TopLeft`/`TopCenter`/`TopRight`/`MiddleLeft`/`Center`/`MiddleRight`/`BottomLeft`/`BottomCenter`/`BottomRight`)

- WARNING — `structureType` is rejected (`4002 additionalProperties`, AC28, current main build 2026-08-20). `buildingMaterialId` was not probed on that build — verify before relying on it.

### CreateBeams — array key `beamsData`
- Required: `begCoordinate` {x,y}, `endCoordinate` {x,y}, `zCoordinate`
- Optional: `offset`, `slantAngle`, `arcAngle`, `verticalCurveHeight`, `width`, `height`, `anchorPoint` (enum: same 3×3 grid as column `coreAnchor`), `profileAngle`
- WARNING — **`slantAngle`: has no effect on all releases <= 1.5.7** (issue #508 — `isSlanted` was never set, the beam stays silently horizontal, read-back always 0). **Fixed upstream, included in release 1.5.8:** via **#507** (merged — `profileAngle` + explicit `isSlanted` in ModifyBeams + read-back, plus cross-sections) and **#526** (merged — `slantAngle` alone now also sets `isSlanted`, on the Create AND Modify side, **also for Columns**; closed #508). Measured values on a fixed build: slantAngle 0.3 over 6 m → z-extent 2.14; `profileAngle` 0.785 on a 0.2×0.4 profile → envelope exactly 0.424/0.424. After updating, probe the final #507/#526 field names (including explicit `isSlanted`).

### CreateSlabs — array key `slabsData`
- Required: `level` (number — Z of the reference plane), `polygonCoordinates` [{x,y}, >=3]
- Optional: `thickness`, `referencePlaneLocation` (enum: `Top`/`CoreTop`/`CoreBottom`/`Bottom`; basic slab supports only `Top`/`Bottom`), `polygonArcs`, `holes`
- WARNING — **`buildingMaterialId` and `structureType` are rejected** (`4002`, AC28, current main build 2026-08-20) → slabs always get the tool-default material; there is no create-time way to set it (set afterwards via SetDetailsOfElements/ModifySlabs).
- WARNING — **`level` is absolute on create but story-relative on readback:** `CreateSlabs {level: 0.0, floorIndex: -1}` on a story at -3.10 produces a slab at absolute z -0.42..0.00 — but `GetDetailsOfElements` reports `details.level: 3.1` (= 0.00 - (-3.10)). A "find the slab at level X" filter written against the create value finds nothing.

### CreateZones — array key `zonesData`
- Required: `name` (string), **`numberStr` (string — MANDATORY, verified live: without numberStr → 4002; an older version of this file wrongly called it optional)**, `geometry` (object, see below)
- Optional: `floorIndex`, `categoryAttributeId` {guid}, `stampPosition` {x,y}
- `geometry` is one of two construction methods (schema `oneOf` — send exactly ONE):
  - **Automatic (associative):** `{ "referencePosition": {x,y} }` — a point **inside a closed wall loop**. Creates an **associative** zone whose boundary follows the surrounding walls (`manual=false`, i.e. real auto-updating room stamps). **Verified live: this works** — a zone was created from a seed point inside a wall rectangle. WARNING: the field is exactly **`referencePosition`**. Using `referencePoint`, or giving a point with no enclosing wall loop, makes the call fall through to the manual branch and fail with `"polygonCoordinates parameter is missing"` (-2130313112) — that error is a wrong-field / no-loop symptom, **not** proof that automatic mode is unavailable.
  - **Manual:** `{ "polygonCoordinates": [{x,y} >=3], "polygonArcs": [...], "holes": ... }` — explicit, non-associative polygon.
  - Do **not** send `referencePosition` and `polygonCoordinates` together (`oneOf` → -2130313215). Use automatic for associative stamps; manual when there is no clean wall loop.

### CreateLabels — array key `labelsData`
- Required: **either** `begCoordinate` {x,y} **or** `parentElementId` {guid}
- Optional: `text` (string content), `floorInd` (number)

### CreateWindows / CreateDoors — array keys `windowsData` / `doorsData`
- Required: `ownerWallId` {guid}, `centerOffset` (number, from wall start)
- Optional: `sillHeight`, `width`, `height`, `reflected`/`refSide`/`oSide` (bool), `favoriteName` (string; from `GetFavoritesByType`)
- **Doors and windows are building components, not wall interruptions.** That a permit or as-built plan draws no door/window symbols is a drawing convention — **not a reason to use `CreateOpenings`**. Always place `CreateDoors`/`CreateWindows`; `CreateOpenings` remains a last-resort fallback for irrecoverably broken door/window defaults (see rebuild-session-host-defaults-and-fallbacks.md).

### CreateOpenings — array key `openingsData`
- Required per item: `ownerElementId` {guid} (any host: wall, slab, roof, shell), `basePoint` {x,y,z}
- Optional: `width`, `height`
- WARNING — **One item per call.** A single call with 7 items returned `elements: []` with no error and created nothing; the identical items created one-per-call all succeeded (live 2026-08-20, AC28, current main build).
- **Slab openings — anchor semantics (live-measured):** `basePoint.x` is the **centre** in x, but `basePoint.y` is the **upper edge**; `height` extends in **-y** from there. `width` is the x extent. `basePoint.z` is ignored (the opening cuts the host through its full thickness). Verified: `basePoint (24.445, 14.59)`, `width 3.55`, `height 1.775` → `Get2DBoundingBoxes` x 22.670-26.220, y 12.815-14.590.
- `Get3DBoundingBoxes` for an Opening reports a **degenerate z** (zMin = zMax = the home story level) regardless of the z sent — use the 2D bbox for verification, and verify the cut itself visually or via the host's plan geometry.
- **Use case beyond doors/windows:** slab voids for stairwells and ramps. A polygon hole in the slab is NOT an IfcOpening (see bim-element-modeling-rules.md), and `ModifySlabs` cannot add holes to an existing slab (see ModifySlabs below) — so `CreateOpenings` on the slab is the only non-destructive path to a ceiling void.

## Modify commands

### ModifyWalls — array key `wallsWithDetails`  (NOT `wallsData`)
- Required per item: `elementId` {guid}
- Optional: `begCoordinate`, `endCoordinate`, `height`, `thickness`, `bottomOffset`, `offset`, `structureType` (enum), `buildingMaterialId`/`compositeId`/`profileId`, `arcAngle` (number, radians — since PR #435)
- **`arcAngle` on `ModifyWalls` curves an existing straight wall** (or re-curves a curved one; only since release 1.5.4, on 1.5.3 → `4002`). Verified live: a straight wall set to `arcAngle:0.8` → `GetDetailsOfElements` `details.arcAngle` went `0 → 0.8`. Set `arcAngle:0` to straighten.

### ModifyDoors / ModifyWindows — array keys `doorsWithDetails` / `windowsWithDetails`
- Required per item: `elementId` {guid}
- Sets `width`/`height`/`sillHeight`/`centerOffset`/`reflected`/`refSide`/`oSide`.
- **Send the full intended payload** — omitted size fields can reset (e.g. width snaps back to default). Read back with `GetDetailsOfElements` to confirm.

### ModifySlabs — array key `slabsWithDetails`
- Accepts `elementId`, `zCoordinate`, `thickness`, `structureType`, `buildingMaterialId`, `compositeId`, **`polygonOutline`**, `polygonArcs`, **`holes`** (schema-level: all accepted).
- WARNING — **Geometry changes fail at runtime.** `polygonOutline` alone, `holes` alone, and both together each return item error `-2130312912 "Failed to modify slab geometry."` (live 2026-08-20, AC28, current main build; the error string sits at the `ACAPI_Element_ChangeMemo` call in the source). `thickness` and material changes work.
- Note the asymmetry with `CreateSlabs`, which uses **`polygonCoordinates`** — sending that name to `ModifySlabs` yields `4002 additionalProperties`, which is easy to misread as "the field does not exist". It does; it just cannot be modified. The readback (`GetDetailsOfElements`) confirms the names: `details.polygonOutline`, `details.holes`.
- **Consequence:** to change a slab footprint or add holes, delete + recreate (mind the hidden-layer trap above) — or, for voids, use `CreateOpenings` on the slab instead.

## Stairs

### CreateStairs — array key `stairsData`  (verified live)
- Required: `baseLinePoints` [{x,y}], `zCoordinate`
- WARNING — **multi-segment L/U baselines (3+ points): version-dependent!** On releases <= 1.5.3 they ALWAYS fail with `-2130313215 "Failed to create new Stair"` (bug #444: the command filled the baseline's `edgeData/vertexData` by hand and thereby forced step segments onto every edge). **Fixed since release 1.5.4 (#445):** L- and U-baselines now create stairs, **provided the geometry is solvable** — the solver rejects e.g. U-runs whose parallel legs are so close that the flights/landings overlap (measured: a leg spacing of 1.4 m fails even with flightWidth 0.6; a spacing of 3.0 m with flightWidth 1.2 works). A solver failure still comes back as `-2130313215` in the **item** (`succeeded:true` at call level!) → always check items for `elementId` + cross-check the stair count. A curved baseline via `polygonArcs` is still rejected (schema). On unfixed builds: only straight 2-point stairs, otherwise use a 2D substitute.
- Optional: `totalHeight`, `flightWidth`, `stepNum` (int >=1), `riserHeight`, `treadDepth`
- WARNING — **HARD LIMIT (all releases <= 1.5.8, issue #425): `stepNum`, `treadDepth` and `riserHeight` are accepted but IGNORED** — the run length is auto-computed regardless of the sent values AND regardless of the baseline length. A straight source run **shorter** than the auto length cannot be matched — it overshoots. A community experiment documented in #425 (rules pinning via `API_StairRulesData`, following the maintainer's recipe) found that **`treadDepth` pinning works precisely** (run = N × treadDepth) while **`riserHeight` pinning does not take effect** (three iterations, including releasing the pitch rule and a +/-0.1% tolerance band) → joint run-length control remains an open issue; see #425 for status.
- **Pre-check BEFORE placing a straight stair:** estimate the expected run length — `runLength ~ (ceil(totalHeight / 0.17) - 1) * 0.26` (e.g. totalHeight 3.25 → ~19 steps → ~4.65 m). Compare against the run length available in the source plan: **if it does not fit, choose an L/U baseline (only on release >= 1.5.4, see above) or a 2D substitute right away** — do NOT place first. After placing, check the footprint via `Get3DBoundingBoxes` against the target space (the bbox is footprint-only, zMax=0 — verify the 3D height separately).
- **No `ModifyStairs`** — a stair's geometry/step parameters cannot be edited after creation. Workaround: delete + recreate. (Generic `MoveElements`, `SetDetailsOfElements` layer, classifications/properties, delete still apply.)
- `Get3DBoundingBoxes` for a stair returns only the footprint (zMax=0) — 3D height not verifiable that way.

## Dimensions (all associative, element-bound)

- `CreateAssociativeDimensions` — array key `dimensionsData`; each: `referencePoint` {x,y}, `direction` {x,y} (any non-zero vector — not limited to horizontal/vertical), `witnessPoints` [>=2; each `elementId` + optional `line`/`inIndex`/`special`/`nodeType`/`nodeStatus`/`nodeId`], optional `floorIndex`. Required: `referencePoint`, `direction`, `witnessPoints`.
- `CreateAssociativeDimensionsOnSection` — linear dimensions on a section view via wall/slab/beam/column/opening presets.
- `CreateWallThicknessDimensions` — associative wall-thickness dimensions for the given walls.
- `GetDimensionData` — read witness-point data (coordinates, measured values) from existing chains.
- **Witness-point conventions (verified):** a witness point = `{elementId, line, special, inIndex}`. Wall outer edge: `line=false, special=1, inIndex=1`. Window edges: `inIndex=2` (near) / `3` (far). Column outer corner: `inIndex=3`. **One dimension with N witness points = a chain with N-1 segments** (use this to build dimension chains). Door witness points behave differently from window ones — verify per case.
- **Full `inIndex` corner mapping (`line:false, special:1`; live-measured 2026-08-20, AC28, current main build):** **Wall (4 corners):** `1` = begin corner on the REFERENCE-line face, `2` = end corner on the reference-line face, `3` = end corner on the FAR face, `4` = begin corner on the far face — along the axis use `1`/`2`, across it `1`/`4`. **Window:** `1` = near-side left edge, `2` = far-side left edge, `3` = **centre**, `4` = right edge. **Door:** `1` = low edge (near face), `2` = **centre**, `3` = low edge (far face), `4` = high edge. Practical rule for chains on opening edges: **low/left edge = `inIndex 1`, high/right edge = `inIndex 4`** for both doors and windows; only the centre index differs (`3` window / `2` door). Cheapest way to establish any element class's witness semantics on a new build: create one dimension with `inIndex` 1..4 on the SAME element, read `GetDimensionData.witnessPoints[].coordinate`, delete the probe dimension.
- **`referencePoint` = where the dimension LINE sits — derive it from the source, not arbitrarily.** Measure the source's dimension-line offsets (in a calibrated raster they are typically stacked at ~1.5 / 2.0 / 2.45 m outside the building: subdivision innermost, overall outermost) and place each chain there, or the chains will be at the wrong distance even when the values are correct.
- **Slabs cannot be dimension witnesses.** `CreateAssociativeDimensions` with a Slab `elementId` does not anchor on the slab edge — the witness collapses to a degenerate point (verified live: a slab witness produced a garbage chain value roughly equal to the absolute coordinate, i.e. anchored near the origin; other runs saw zero-length points). Consequence: an overall dimension to a slab edge that has **no wall or column on it** (e.g. a terrace slab's outer edge) is **not associatively measurable** — the nearest real element only yields the shorter value. Report this rather than faking it with a carrier element; delete such probe dimensions immediately.
- **Replicate the source's CHAIN STRUCTURE, not just its values.** Which edge each witness anchors (clear/light measure between finished faces vs. axis measure), which subdivisions the chain carries, its stacking tier, and its offset from the building are part of the task. Typical live failures: axis dimensions created where the source chains clear opening widths with the wall thicknesses between them; a chain measured to a wall AXIS instead of its outer face; separately created wall-thickness dimensions landing in the same tier as the main chain and visually merging with it; whole source subdivisions missing entirely. **If the anchors do not match the source, the chain is wrong — even when a number happens to look plausible. Numeric equality is not proof.**
- **Measure EVERY element class from the calibrated file** before placing — columns (centres + size), door/window centre-offsets + widths, and dimension-line offsets. Re-using remembered/assumed coordinates for one class while measuring the others is a recurring source of "X sits in the wrong place" (typical failure: columns and door offsets left on old assumed values after walls/rooms had already been re-measured).
- **Read the opening LAYOUT of each facade from the source — never carry over another project's opening chain.** A reused chain can be inverted: e.g. a wall modelled from an assumed `1|1|1.75|2.5|1.75|1|1` chain (two doors flanking a central wall) where the source actually has a single central 2-leaf terrace door with windows on either side — door and wall swapped. Verify against the source DIMENSION TEXT and the symbols (a door has a swing arc; a window does not), not against your own model read back through `GetDimensionData`.
- **Opening detection caveat:** a "dark-fraction < threshold" scan over the wall-thickness band false-positives on solid wall (thin inner edge line) and can invent extra openings; confirm each opening visually (frame symbol + swing arc) before trusting it.
- **Limitation:** only **linear** associative dimensions (plus wall-thickness and section variants). There is **no** create command for radial, angular, or level/elevation dimensions.
- WARNING — **ghost GUID with an active section/elevation window (issue #510, releases <= 1.5.7):** `CreateWallThicknessDimensions`/`CreateAssociativeDimensions` can return a GUID **without any element being created** (the GUID exists in no database) when a section/elevation window is active. Before dimension batches, make sure a **floor-plan window is active**, and confirm every created dimension via read-back. **Fixed since release 1.5.8 (#512):** a clean per-item error is returned instead. For real section dimensioning, `GetSectionElements` (#535, also 1.5.8) now provides the section witness anchors.
- **`CreateAssociativeDimensionsOnSection`: reachable since release 1.5.8** — `GetSectionElements` (#535) provides the required `API_SectElemID` GUIDs including owner IDs (on releases <= 1.5.7 no command handed out such GUIDs, #509). Workflow: section DB → `GetSectionElements` → sectionElementId as witness. Probe the schema before productive use.

## Stories (SetStories / GetStories)

- `GetStories` → `firstStory`, `lastStory`, `actStory`, `skipNullFloor`, and `stories[]` (each `index`, `floorId`, `dispOnSections`, `level`, `name`, **`height`**). `height` is the floor-to-floor height = level difference to the **next story up** (added in PR #434). The **topmost story has no `height`** (no story above it).
- `SetStories` — send the FULL desired `stories[]` (StorySettings: `dispOnSections`, `level`, `name`, plus optional `index` **only since PR #571**, see below; without `index`, matching is purely positional, bottom-up). It diffs against the current structure: more entries → inserts story at top; fewer → deletes from top; otherwise applies per-story level / dispOnSections / name / height changes. **Create, delete, and level/height change all work** (verified live on a project with a basement story).
- **Story numbering convention (verify EVERY time): the storey at reference level +/-0.00 (ground floor) gets index 0, basements negative (-1, -2, ...), upper floors positive (+1, +2, ...).** This is the standard convention in most European offices — treat it as the default unless the project dictates otherwise.
  - **Releases <= 1.5.8:** negative story indices CANNOT be created when the basement stories do not exist yet — `SetStories` creates new stories exclusively via `APIStory_InsAbove` at the top (issue #570). A list that includes basement entries makes the deepest basement story index 0 and pushes the ground floor up (verified live: levels -5.95/-3.10/0 produced indices 0/1/2). Workaround: if the basements already exist, only set levels/names positionally; if they are missing, ask the user to create the structure once in the Story Settings dialog ("insert below"). Do NOT silently continue with shifted numbering.
  - **FIXED by PR #571 (merged 2026-08-20, first release after 1.5.8):** `StorySettings` gains an optional `index`. Providing it on any story pins the numbering of the WHOLE list (story at position i becomes firstIndex+i), so basements can be created directly: `[{index:-2,level:-5.95,...},{index:-1,level:-3.10,...},{index:0,level:0,...}]` → firstStory -2, ground floor = index 0. Live-verified 8/8 (combined reshape, growing down by 2 in one call, shrinking from the bottom; `APIStory_InsBelow` lowers firstStory without renumbering). Non-consecutive indices → clean error `-2130313112 "The given story indices are not consecutive."`. Without `index` the behaviour is unchanged (backward compatible). **Gate probe:** send `index` — on <= 1.5.8 it returns `4002 additionalProperties`.
  - **Live addendum 2026-08-20 (current main build, AC28):** `index` works as documented — from **one** story (level -5.95), `[{index:-2,...},{index:-1,...},{index:0,...},{index:1,...}]` immediately produced `firstStory:-2 ... lastStory:1`. WARNING: the **levels** sent in the same call were applied **relative**: requested -5.95/-3.10/0.00/3.10, resulting -11.90/-9.05/-5.95/-5.95 (mechanism: Archicad's set-elevation moves the stories above along; the level-correction pass has a 3-iteration cap). Recipe: create the structure with `index` first, then set the levels in a **second** pass — the FULL list per call, one target level per call, **top-down**. Then `GetStories`: levels and `height` came out right first try.
  - **Always: after every `SetStories`, verify via `GetStories` that the storey at level +/-0.00 actually has index 0** — if not, fix it before doing anything else.
- **Storey height (floor-to-floor) is the level difference to the NEXT story up — it is a DERIVED, read-only value, not a settable per-story field.** `GetStories` reports it as `stories[].height` (PR #434), but `SetStories` has **no working settable height**: `SetStories({stories:[{index:0,height:H}]})` returns success yet does not establish a story height. To set the ground-floor storey height to e.g. 3.25, you still set it implicitly by placing the **next story's level**: `SetStories({stories:[{index:0,level:0,name:"Ground floor"},{index:1,level:3.25,name:"Upper floor"}]})` → verify via `GetStories` that story 0 now reports `height:3.25` (and story 1 sits at `level:3.25`). (A wall `height=3.25` alone makes the walls tall but leaves the storey height undefined.)
- **Standard recipe for the story grid:** send ALL desired stories in **ONE** `SetStories` call (including names), then a mandatory `GetStories` read-back. Verified live: 6 stories in one call, reliable (AC26, release 1.5.3 — the older "SetStories unreliable" note was the negative-index bug, fixed with #423). With a broken/uncertain grid: stack walls via absolute `CreateWalls.zCoordinate` (grid-independent) — or since release 1.5.4 use `CreateWalls.floorIndex`.
- Historical note: in releases before 1.5.3, level-change and delete failed with `-2130313112` on projects with a basement (negative story index) — fixed via the story-index correction (PR #423). If you hit that error, the running add-on predates the fix.
- **Stacking by elevation:** set a wall's absolute base with **`CreateWalls.zCoordinate`** (verified reliable: zCoordinate 7.0 → wall zMin 7.0). Do **NOT** use `ModifyWalls{bottomOffset:0}` afterwards to "stack" — it snaps the wall to the base of its home story and can dump all upper-floor walls onto z equal to the home story. Put height in `CreateWalls.height` and elevation in `zCoordinate` at creation time. (The SetStories level glitch on repeated calls was the negative-index bug fixed in PR #423; re-test on a current build.)

## New since release 1.5.4 (#436/#437)

These fields exist since release 1.5.4; older releases return `4002`. **Verified live (AC28):** `floorIndex=1` + `zCoordinate=0.25` → wall zMin exactly story level + offset (3.5); `floorPlanPolygons` returns the closed cut contour top-level in the details item; `GetStories.height` = level difference to the next story up (topmost has none).

- **`SetDetailsOfElements` → `drawIndex`** (#436): repositions display order via `ACAPI_Grouping_Tool` (direct `drawIndex` set is a Graphisoft bug and silently ignored). Known limits: Door/Window/Skylight min level 7 (host-based stepping for 8–14); generic `Opening` immovable; multiple openings in the same host in one batch end at the same level.
- **`GetDetailsOfElements` → `floorPlanPolygons`** (#437): optional per-element output — the cut-fill contour polygons as drawn in the floor plan, works for elements on any story (`allStories`) without switching the active view. Useful for outline extraction / overlay proofs.
- **`ChangeWindow` → `storyIndex`** (#437): with `windowType:'FloorPlan'` switches the active story by index.

## New since release 1.5.8 (2026-08-13)

Probe schemas before productive use:
- **`GetSectionElements`** (#535): list the section elements of a section database, **with owner element IDs** — closes the earlier "CreateAssociativeDimensionsOnSection unreachable" gap (#509): section witness anchors are now obtainable.
- **`CreateInteriorElevations`** (#545) — create interior elevations (previously not reachable at all, #466/#471).
- **`favoriteName` in ALL create commands** (#529) — no longer windows/doors only.
- Fixes: float indices in `SetDetailsOfElements` (#534, previously a silent fail), window/door **markers are preserved** instead of reset to the libpart default (#556, closed #551), error objects are now schema-conformant (#543 → #483), **every batch item starts from tool defaults** (#542 — no more state bleeding between items), publisher set by **name** in `GetNavigatorItemTree` (#536), polygon walls are rejected with a clear message (#547), `basePoint` places openings vertically (#544 → #533).
- Full Beam/Column/Wall/Slab coverage (#507) + effective `isSlanted` (#526) are included in 1.5.8 (see the CreateBeams gotcha).
- **Merged after 1.5.8** (in the next release): windows/doors are created from the **floor-plan database** (#559 — fixes the AC29 silent-fail class #481/#532), CreateDrawings validation (#562), GDL array write path (#558).

## New since release 1.5.6 (2026-07-31)

Probe schemas before productive use (only `CreateRoofs` is verified live, see below):
- **Keynotes** (#472, AC28+): manage the keynote tree + place keynote labels.
- **MEP commands** (#473, AC28+): create/modify/connect/query MEP elements.
- **Element grouping** (#475): `GetGroupsOfElements`, `GetElementsOfGroups`, `Get/SetSuspendGroupsMode` — also solves the "SetDetailsOfElements fails on grouped elements" problem (#465).
- **2D drawing elements** (#484): full GET/SET/Create support for pure drawing elements (lines etc.) — relevant for survey-plan linework.
  - WARNING — **`CreateLines` is the ATTRIBUTE command** (creates line types, `Line` attributes) — a geometric payload is rejected with `4002` on `#/linesData`. For 2D linework that must not become BIM geometry (stair treads and arrows, furniture outlines), use **`CreatePolylines`** (`polylinesData[].coordinates`) — creates real `PolyLine` elements; set the layer afterwards via `SetDetailsOfElements`.
  - WARNING — `CreatePolylines` rejects `floorIndex` (`4002`); the polyline lands on the **active** story (readback-observed, one consistent case) → set the story via `ChangeWindow` before creating.
- `ShowAlert` (#468, dialogs), drawing titles via Get/SetDetailsOfElements (#464), `GetSpecialFolders` (#487), `GetUserGSID` (#478).
- **`CreateRoofs` works** (#482) — details in the Roofs section below.

## New since release 1.5.4 (July 2026 wave) (#447/#448/#451/#455/#456)

**`floorIndex` now in ALL create commands (#448) — WARNING: TWO semantics (verified live):**
- **`CreateWalls`**: with `floorIndex` set, `zCoordinate` becomes a **bottomOffset RELATIVE to the story** (floorIndex=1 @ level 3.0 + z=0.25 → zMin 3.25). Original #437 semantics, unchanged.
- **All others** (Column/Slab/Object/Lamp/Beam/Stair/Roof/Morph, #448): the z coordinate stays **ABSOLUTE** — `floorIndex` only pins the home story, the offset is computed internally as `z - story level` (floorIndex=1 @ 3.0 + z=0.25 → zMin 0.25!). Same field name, different meaning — do not mix them up when stacking floors.

**Attribute family (#447):**
- **`DeleteAttributes`** — attributes (e.g. test layers) are now deletable: `{ attributes:[{attributeId:{guid}}] }`.
- Detail reads per type: `GetLayers`, `GetBuildingMaterials`, `GetComposites`, `GetFills`, `GetLines`, `GetPenTables`, `GetProfiles`, `GetSurfaces`, `GetZoneCategories`, `GetMEPSystems` — WARNING: input **`attributeIds` is MANDATORY** (verified: without it → 4002); for **listing** keep using `GetAttributesByType`, then fetch details selectively. An optional `fields` array filters the response fields.
- New creates: `CreateFills`, `CreateLines`, `CreatePenTables`, `CreateProfiles`, `CreateZoneCategories`, `CreateMEPSystems`.

**Favorites complete (#451):** `ApplyFavoritesToElements` (on EXISTING elements, not just defaults), `UpdateFavoritesFromElements`, `RenameFavorites`, `DeleteFavorites` — all registered (verified via availability scan). Probe schemas before use.

**Miscellaneous:** GDL **array** parameters now editable (#455, `SetGDLParametersOfElements`); script slots/toolbar (#456, host UI); Grasshopper components for 193/196 commands (#457 — affects only the GH plugin, not the HTTP API).

**New since release 1.5.5 (2026-07-21):** **`UpdateZones`** (#461 — update existing zones, verified registered); **full Morph coverage** `GetDetailsOfElements`/`CreateMorphs`/`ModifyMorphs` with the full `API_MorphType` parameter set (#449); 2D coordinate reference in the response schema fixed (#460); browser palette as a tkinter alternative for Python scripts (#459, host UI). Probe schemas before use.

## Layout book & Navigator (#441 — since release 1.5.4)

Large documentation/layout command set. On older releases → `4002`/`4010`. The layout chain below is **verified live (AC28)**; for the rest (view map / custom scheme) check the exact schemas against the upstream `Examples/*.py` (`test_layout_workflow.py`, `test_navigator_views.py`, `test_layout_custom_scheme.py`).

**Layout book — verified chain (navigator ID → databaseId → settings):**
1. `GetNavigatorItemTree` — input **`navigatorMapId`** (STRING enum: `PublicViewMap`/`ProjectMap`/`LayoutBook`/`PublisherSets`; WARNING: NOT as a `{type:...}` object — that is the *official* `API.GetNavigatorItemTree`, not the Tapir variant). Response: `navigatorItemTree` with `children[].navigatorItem` = `{type (BookItem/LayoutItem/MasterFolderItem/MasterLayoutItem/...), name, navigatorItemId:{guid}, prefix, children[]}`.
2. `GetDatabaseIdFromNavigatorItemId` — input `{navigatorItemIds:[{navigatorItemId:{guid}}]}` → response **`databases:[{databaseId:{guid}}]`**.
3. `GetLayoutSettings` — input `{layoutDatabaseIds:[{databaseId}]}` → response **`layoutSettings:[{layoutName, horizontalSize, verticalSize, leftMargin, topMargin, rightMargin, bottomMargin, customLayoutNumber, customLayoutNumbering, doNotIncludeInNumbering, displayMasterLayoutBelow}]`** (sizes in mm; A1 = 841×594).
4. `SetLayoutSettings` — input `{layoutsData:[{layoutDatabaseId:{guid}, <settings fields>}]}`. Confirmed live: `customLayoutNumber '' → 'X99'`, `customLayoutNumbering false → true`, reversible. **Proven rules:** `horizontalSize`/`verticalSize` only on **master layouts**; `displayMasterLayoutBelow` is silently ignored on normal layouts → **verify via read-back**.
- `CreateLayoutSubset` — subset with numbering options (style, prefix, startAt, continueNumbering...).
- `CreateLayout` — layout with `layoutParameters` (size, margins, numbering, master by name or ID). (Alternatively the older `CreateLayouts` (plural) from #370 exists with `layoutsData:[{masterLayoutName, layoutName}]`.)
- `GetLayoutCustomScheme` — read user-defined layout scheme / custom data.

**View map / Navigator**
- `CreateViewMapFolder` — folder in the view map.
- `CloneProjectMapItemToViewMap` — clone a project-map item as a view.
- `CreateViewsInViewMap` — create views in the view map.
- `SetViewRotation` — set view rotation (relevant for plan north / orientation).
- `GetNavigatorItemTree` — read the navigator tree (starting point for all navigator ops).
- `MoveNavigatorItem` / `RenameNavigatorItem` / `DeleteNavigatorItems` — move/rename/delete navigator items.

**Workflow:** `GetNavigatorItemTree` (get IDs) → build the view map (`CreateViewMapFolder`/`CloneProjectMapItemToViewMap`/`CreateViewsInViewMap`) → `CreateLayout` (master by name) → place the view as a drawing → `PublishPublisherSet`. This largely closes the earlier gap where view-to-layout placement was manual-only — **re-verify live on the connected build**.

## Roofs / Meshes / Railings (create coverage)
- WARNING — **`CreateRoofs`: version-dependent!** On **all releases <= 1.5.5** the command is an unconditional stub — every item returns `-2130313215 "Multi-plane roof creation is not yet supported"`, NO payload works (issue #467); there, substitute roofs as slab/morph. **Fixed since release 1.5.6 (2026-07-31, #482). Verified live:**
  - **Multi-plane (default):** the existing schema now works — `level` + `polygonCoordinates` (= pivot polygon) + optional `levels[{levelAngle,levelHeight}]` (1–16, radians) + optional `eavesOverhang` (the contour is generated automatically by offset; measured: 0.5 → exactly +/-0.5 m). Without `levels` the tool defaults apply.
  - **Single-plane (NEW):** `pivotLine:{begCoordinate,endCoordinate}` + optional `angle` (rad) → one inclined plane; the plane **rises to the left of the line direction** (flip the line = other side). Measured: 30 degrees over 4 m depth → rise of about 2.7 m including thickness.
  - Mixed forms are cleanly rejected (`levels`/`eavesOverhang` + `pivotLine`, or `angle` without `pivotLine`); errors as usual **in the item** (`succeeded:true` at call level).
  - **Height model of the single-plane form (live-measured 2026-08-20, AC28, current main build):** `thickness` is **ignored** — the tool default applies (0.345 m here); roof thickness cannot be set on create. `level` is the **lowest point** = the BOTTOM face at the pivot line; the top face there is `level + t/cos a`, at horizontal distance L it is `level + L*tan a + t/cos a` (verified over L = 8 m at a = 0 / 0.1 / 0.22147 rad → bbox z-spans 0.345 / 1.1494 / 2.1549, exactly formula-true). **To place a driving/walking surface at a target height, subtract `t/cos a` from it to get `level`** — `level` = target height sits the surface a full thickness too low.
  - Usable as a **ramp** (several single-plane roofs with one common angle, tops continuous). Semantic caveat: it remains an IfcRoof — flag that for IFC/quantities, or consider Morphs (project decision).
  - `GetDetailsOfElements` for a Roof returns `{"error":"Not yet supported element type"}` (issue #569) — verify roofs via `Get3DBoundingBoxes` only.
- **`CreateMeshes`** exists and works — usable for terrain source layers (see the full catalog for the schema).
- **No `CreateRailings`** — railings cannot be created via Tapir. Workaround: model as a thin wall, a morph, or a library object until such a command exists.
- WARNING — **AC29 issue (#481, unresolved on <= 1.5.8):** on Archicad 29 (observed with 1.5.5), `CreateWindows`/`CreateDoors` can return a **GUID without any element being created** (silent, no crash, also for single items, also with a valid favorite). A drastic proof of the meta rule: **NEVER infer success from the return value — always cross-read via `GetElementsByType` count / `GetDetailsOfElements`.** (A fix creating windows/doors from the floor-plan database, #559, is merged for the release after 1.5.8.)

## Read-back (GetDetailsOfElements)
Input: `{ "elements": [ { "elementId": {"guid": ...} } ] }`.

**Response shape (verified live, 1.5.4-dev):** each item has **top-level** `id`, `type`, `layerIndex`, `floorIndex`, `drawIndex` plus the type-specific `details` object. So the element's **layer is read at top level** (`detailsOfElements[i].layerIndex`), NOT inside `details` — but *setting* it goes through `SetDetailsOfElements` with `details.layerIndex` (asymmetry!).

Returned `details` per type:
- **Wall:** geometryType, `arcAngle` (radians; non-zero = curved wall, since PR #435), structureType, zCoordinate, begCoordinate, endCoordinate, height, bottomOffset, offset, flipped, **begThickness/endThickness**. CORRECTION (verified live): `begThickness`/`endThickness` are returned **for normal walls too** and equal the wall thickness (probe: create 0.365 → read-back 0.365/0.365) — the earlier "thickness is not returned" note only holds for **<= 1.5.3** builds. (`geometryType` currently reports `"Straight"` even for an arc-curved wall; read `arcAngle` to detect curvature.)
- **Slab:** structureType, thickness, level, offsetFromTop, zCoordinate.
- **Column:** origin, zCoordinate, height, bottomOffset. **No cross-section / no `coreAnchor`** (known gap).
- **Beam:** zCoordinate, begCoordinate, endCoordinate, level, offset, slantAngle, arcAngle, verticalCurveHeight (+ `profileAngle` since the #507 fix; `slantAngle` reads 0 on all releases <= 1.5.7, see the CreateBeams gotcha). **No cross-section / no `anchorPoint`** (known gap).
- **Window/Door:** width, height, sillHeight, centerOffset, reflected, refSide, oSide.

> Placement fields set on create (`referenceLineLocation`, `coreAnchor`, `anchorPoint`, `referencePlaneLocation`) are **not currently echoed** by GetDetailsOfElements, so they cannot be read back for verification yet.

## Object/fixture placement limit (verified live)

`CreateObjects` places a library part at a point, but its **anchor and rotation are not reliably controllable** via the API:
- Small sanitary/appliance parts (WC, washbasin, shower cabin, washing machine, kitchen sink, cooktop — tested against a localized standard library) place fine but anchor at their back/top edge (~0.25–0.3 m offset from the given point); nudge the input coordinate to centre them.
- Macro/parametric parts are unusable as a single object: parametric stair library parts fail with `-2130313112 Failed to create new Object`; an all-in-one parametric kitchen part creates a huge sprawling corpus. Use **individual parts** (sink + cooktop) instead of the parametric kitchen.
- **`CreateObjects` has no rotation field** — `angle`/`rotation`/`rotationAngle`/`orientation`/`direction` are all rejected (`additionalProperties`); the object is placed at default orientation. **Workaround (since 1.5.3): rotate it afterwards with `RotateElements`** (generic, works on any element incl. objects). Input: `elementsWithRotations[]`, each `{ elementId, rotation: { beginPoint{x,y}, endPoint{x,y}, origin{x,y} }, copy? }` — the angle is given by the arc from `origin→beginPoint` to `origin→endPoint` (not a scalar angle). So fixtures that need turning (a WC against a side wall, an L-kitchen) CAN be oriented: create at the point, then `RotateElements`.
- **Take opening WIDTHS (and column sizes/axes) from the dimension TEXT, not from pixels.** Pixel-measuring an opening gave 2.25 m for a terrace door whose dimension chain clearly reads 2.50 m — the written value is authoritative; pixels are only for elements that carry no dimension.
- Always verify with `Get3DBoundingBoxes` and correct the input coordinate by the measured offset.

## Verifying against a measured source plan (calibrated overlay)

The reliable end-check for a scan-to-BIM rebuild is a **calibrated overlay** of the live model on the source raster — not screenshots or bbox spot-checks:
1. Get the source as a file (PDF/JPG/PNG, high-res). Calibrate px-to-m by projecting dark pixels onto X and Y and reading the strong wall lines; two known dimensions fix origin + scale (worked example: x=0 → px 2878, x=13.5 → px 6067 ⇒ 236.2 px/m; y=0 → px 4623, y=10 → px 2258 ⇒ 236.4 px/m).
2. **Measure** ambiguous geometry (non-rectangular rooms, stair run, fixture centres) from the calibrated image instead of guessing — e.g. an L-shaped utility room is found from the wall line under the stair, not assumed.
3. Dump live geometry (walls begin/end via `GetDetailsOfElements`; openings/columns/objects via `Get3DBoundingBoxes`) to JSON, then draw it over the source at the calibrated transform.
4. **Tooling gotchas:** matplotlib + Tapir HTTP calls in one process can break the sockets, and files written on one host can read stale/truncated on another host's mount. Do the Tapir reads in a plain script (no matplotlib) → JSON, and render the overlay with matplotlib **on the same host** that holds the file. If your agent runtime cannot reach localhost of the Archicad host, run the HTTP calls host-side.
