---
name: archicad-automation
description: "Use when operating Archicad through the Tapir add-on's JSON API: inspecting an open project, inferring office standards from the open file's favorites/attributes/properties, creating or modifying BIM elements (walls, slabs, openings, roofs, zones, stairs), reading element details, placing associative dimensions, managing layers and attributes, creating views and layouts, sections and details (Detail tool workflow: detail markers placed in an existing 1:50 section, 2D drafting in the detail window), drawings on layouts (clipped drawing windows, removing drawing titles, static dimension chains and height marks in sections), or publishing. Talks HTTP to the Archicad host on ports 19723-19743. Pairs with abstracting-building-models when drawings or scans must first be interpreted."
license: MIT
metadata:
  version: 3.5.1
  author: weltmaister
---

# Archicad Automation via the Tapir JSON API

Drive Archicad itself through the [Tapir add-on](https://github.com/ENZYME-APD/tapir-archicad-automation)'s
HTTP interface: inspect an open project, create/modify BIM elements, set properties and
classifications, build documentation views and layouts, and verify model state.

**Core principle: never infer success from a return value.** Every mutation is confirmed by an
independent read-back (`GetElementsByType` count, `GetDetailsOfElements`, `Get3DBoundingBoxes`).
Commands can return `succeeded: true` with per-item `error` objects, and in known cases even a
GUID for an element that was never created. What works reliably is anything with an answer that
can be checked by arithmetic — dimension closure, counts, bounding boxes; what needs human eyes
is design intent and visual quality.

## When to use

- Direct Archicad operations: "create these walls", "place windows in wall X", "publish the floor plan".
- Documentation: sections at 1:50, details via the Detail tool, drawings on layouts, sheet sets for
  trades (see "Documentation views" below).
- Executing a source-derived building model produced by `abstracting-building-models`
  (use that skill FIRST when the task starts from scans, PDFs, photos, or vague references).

## Building a whole model: `scripts/build_from_model.py`

When a validated intermediate model exists (the JSON of `abstracting-building-models`), build it with
`scripts/build_from_model.py` instead of composing create calls one by one. The script applies fixed
modelling rules (catalog: `references/modeling-rule-catalog.md`; rules as data: `scripts/modeling_rules.py`):
classification, load-bearing function, position and layer for every part, core-outside reference lines for
exterior walls, raw-slab-to-raw-slab wall heights linked to the story above, slab edges on the wall core
faces, floor build-ups and associative zones per room, openings, columns, beams, footings, parapets,
two-part pitched roofs, optional DIN 277 bodies — and **reads every rule back** after building.

Workflow: `--dry-run --port N` first (reads the office catalog read-only and completes the plan), show the
plan summary, then repeat with `--confirm`; `--check report.json --port N` re-verifies a finished build
without changing anything. Office-specific names (layers, favorites) come from `--office-profile
profile.json`; the built-in default is an example profile from a German Archicad 28 template. Situational
decisions (datum, load-bearing interior walls, finishes) come from the model fields listed in the script
header. Stairs are not built by the script — create them separately. `tests/` carries a 134-test suite with
a fake Archicad that mirrors live-measured behavior (`python -m unittest discover -s tests`).

## Operating sequence

1. **Discover the port**: scan 19723–19743 on the Archicad host; the first responding port is
   the active instance. The JSON server only listens while a project is open, and it listens on
   localhost only — if your agent runtime cannot reach the Archicad host's localhost (e.g. a
   Linux sandbox next to a Windows host), run the HTTP calls host-side and keep the scripts on
   the host; sandbox↔host mount sync is unreliable for freshly written files, so hand data over
   via stdout when in doubt. If TCP on a port is open but HTTP requests are closed immediately
   (`RemoteDisconnected`), see the localhost-only/port-proxy note in
   `references/tapir-http-direct-protocol.md`.
   **Port hijack:** if `127.0.0.1:<port>` suddenly times out while Archicad is idle, check
   `Get-NetTCPConnection -LocalPort <port>` — another program can bind `127.0.0.1` on the same port
   (seen: VS Code remote-SSH automatic port forwarding). Archicad binds `0.0.0.0`, so
   `http://127.0.0.2:<port>` still reaches it. Several Archicad instances may run at once — identify
   yours by `GetProjectInfo` (project path), not by port.
2. **Verify connectivity**: `GetProjectInfo`.
3. **Probe version and capabilities**: `GetAddOnVersion`, an `API.IsAddOnCommandAvailable` scan
   over your working command list, and field probes for version-sensitive fields. Different
   machines run different Tapir builds — never assume the documented catalog matches the
   connected instance. See `references/tapir-verified-command-schemas.md` → "Version variance".
4. **Inspect before you mutate**: stories, layers, attributes, favorites, existing elements.
5. **Load the references** (below) instead of guessing field names.
6. Classify missing parameters: discoverable from the file / inferable / genuinely user-required.
   Ask concise questions only for the last group.
7. Present non-trivial mutation plans before executing.
8. Execute minimal HTTP calls; batch where safe (see the batching gotchas in the references).
9. **Verify with read-only calls and report evidence.**

For deliverables meant for human reading/publishing, establish orientation early: verify project
north / view rotation and place a north arrow from the office favorite library near the beginning
of the documentation workflow, not as a late cosmetic afterthought. If north is unknown, say so
instead of guessing from page appearance. Copying a library object (north arrow) from another
layout: `CreateObjects` with the same `libraryPartName`, then copy its GDL parameters
(`GetGDLParametersOfElements` → `SetGDLParametersOfElements`) — dimensions alone do not give the
same symbol size.

**Working next to the user:** API calls need neither mouse nor keyboard and `ChangeWindow` does not
steal the foreground focus (verified AC26) — the user can keep working in other programs, but not in
the same Archicad project. UI automation cannot run "on a separate virtual desktop" in parallel:
all Windows virtual desktops share one mouse and keyboard, simulated input goes to the visible one.
**Long jobs:** if the shell tool has a short timeout, run scripts detached (`Start-Process … 
-RedirectStandardOutput log`) and poll the log; a killed client can leave half-done steps (e.g. a
duplicate drawing) — re-list and clean up. Batched `SetDetailsOfElements` on ~30 elements took
>60 s once; batch by 5.

## Office standard

The office standard is inferred from the **currently open Archicad file**, not invented
externally. Before modelling, inspect the existing resources through Tapir: favorites by element
type, pen tables, layers and layer combinations, line types, fills, surfaces, building materials,
composites, profiles, properties, classifications, zone categories, model view options, graphic
overrides, renovation filters, and layout-book/master-layout conventions. Do not create new
office conventions when suitable resources already exist in the file; if external guidance
conflicts with the open file, report the mismatch and ask instead of silently overwriting
attributes or favorites. The full checklist (source hierarchy, discovery questions, when to ask
vs. discover) is `references/source-and-office-standard-checklist.md`.

## Protocol

**Which channel.** Prefer the **Tapir MCP server** when the session has its tools
(`discovery_list_active_archicads`, `archicad_list_commands`, `archicad_get_command_schema`,
`archicad_call_tool`): it checks parameters against the schema, logs every request and runs long
commands as background jobs. Call `discovery_list_active_archicads` first — a freshly started
server rejects `archicad_call_tool` until discovery has run. Direct HTTP (below) is the fallback.
An agent whose shell runs in a sandbox (a VM, a container) cannot reach the host's Archicad ports
at all; give it the MCP server instead of routing HTTP scripts through a desktop-automation shell.

**Visual checks without the GUI.** `SaveCurrentWindowAsImage {imageFilePath, format:"png"}`
(since 1.7.1) saves what the current Archicad window shows and returns its zoom — verified on
AC28 with 1.7.2: 0.1 s, no change of the foreground window. Prefer it over desktop screenshots.
On AC26/1.7.1 it worked for layout windows only (floor plan and section windows failed: "cannot
be saved as a picture") — check views through their drawing on a layout (`FitInWindow` on the
drawing, then save the layout image). Keep GUI automation for what Tapir cannot do (placing
Detail markers, #1377; section marker range), and only with the user's consent.

Every Tapir command goes through the official envelope — the bare
`{"command": "TapirCommand.X"}` form is rejected with error 2002:

```json
{
  "command": "API.ExecuteAddOnCommand",
  "parameters": {
    "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": "<CommandName>"},
    "addOnCommandParameters": { }
  }
}
```

```python
import urllib.request, json

def tapir_call(host, port, command, parameters):
    payload = json.dumps({
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": command},
            "addOnCommandParameters": parameters,
        },
    })
    req = urllib.request.Request(f"http://{host}:{port}", data=payload.encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
```

Success: `{"succeeded": true, "result": {"addOnCommandResponse": {...}}}`.
Schema violation: `{"succeeded": false, "error": {"code": 4002, ...}}` naming the offending JSON
path — that usually means a wrong or missing **field name**, not a missing feature. Look the
command up in the references before retrying. Batch commands report per-item results: always
check each item for an `elementId` vs. an `error` object.

## References (load on demand)

| File | Use for |
|---|---|
| `references/tapir-verified-command-schemas.md` | **Read first.** Hand-verified field names, gotchas, and version gates for the most-used commands. The authority when unsure about a payload. |
| `references/tapir-full-command-catalog.md` | Complete command list with input/response schemas. Breadth; anything not in the verified file. |
| `references/tapir-http-direct-protocol.md` | Protocol details, error semantics, command family overview. |
| `references/modeling-rule-catalog.md` + `scripts/modeling_rules.py` | Fixed modelling rules for `build_from_model.py`: rule IDs with source/implementation/check, role table, situational defaults, live-proven API limits. |
| `references/wall-reference-lines-and-opening-placement.md` | Wall reference-line direction rules, clean junctions, opening placement. |
| `references/bim-element-modeling-rules.md` | Office-grade BIM semantics: mandatory classification triple, tool-choice matrix, per-storey walls, slab vs. build-up, roofs, openings/IfcOpenings, junction gates, zone QA. |
| `references/opening-side-triad-oside-reflected-refside.md` | Door/window side and handing control (`oSide`, `reflected`, `refSide`). |
| `references/opening-witness-point-derivation.md` + `scripts/opening_witness_points.py` | Deriving global opening edge coordinates from owner-wall geometry. |
| `references/publish-and-dimension-verification.md` | Verifying dimensions and published output after model edits. |
| `references/dimension-first-measured-plan-control-grids.md` | Dimension-chain-first reconstruction of measured plans. |
| `references/measured-plan-proof-and-handoff.md` | Proof routines and parameter handoff from dimension chains. |
| `references/full-scan-to-bim-rebuild-pattern.md` | Full delete/recreate/publish/read-back rehearsal workflow. |
| `references/rebuild-session-host-defaults-and-fallbacks.md` | Fresh-session failures: library defaults, publisher state. |
| `references/archicad-host-ui-state-and-publisher-recovery.md` | Modal-dialog blocks, dead navigator IDs, publish recovery. |
| `references/overlay-*.md` + `scripts/calibrated_plan_overlay.py`, `scripts/proof_plan_layers.py` | Calibrated source-vs-model overlay proofs. |
| `references/object-triage-and-opening-handing-notes.md` | Separating model objects from annotation libparts. |
| `references/repair-vs-rebuild-decision.md` | When to keep patching vs. delete/recreate a group vs. rebuild. |
| `references/source-and-office-standard-checklist.md` | Source hierarchy, discovery questions, ask-vs-discover rules. |
| `templates/` | Rebuild-plan and overlay-report templates. |

## Golden rules (the short list)

- **Element IDs are nested objects**: every command that takes element IDs wants
  `{"elementId": {"guid": "..."}}` (or `{"guid": ...}` inside named fields like `ownerWallId`).
  A bare GUID string fails validation — and `DeleteElements` with the wrong shape returns
  `succeeded: true` while deleting **nothing**. Since 1.6.0 `DeleteElements` answers
  `executionResults[]` per element, but reports a nonexistent guid as deleted — always re-count.
- **Identify each Archicad by `API.GetProductInfo` / `GetProjectInfo`, never by its port** — ports
  follow the start order and swap between sessions.
- **Queries act on the active window** — `GetElementsByType` without `databases` lists the active
  view's elements (a section, say), not the floor plan. Check `GetCurrentWindowType`; pass
  `databases` or `ChangeWindow` first.
- **Archicad-version traps:** on AC25–AC27 with Tapir 1.7.0/1.7.1 (not 1.7.2), changing the content
  or size of a text with two or more characters fails with `-2130312713` — delete and recreate it
  instead (AC28 unaffected). On releases <= 1.6.0, AC25–AC27 truncated text content and
  `ChangeWindow.storyIndex` was a no-op — both fixed in 1.7.0; probe the connected version.
- **Top-level array keys differ between create and modify**: `wallsData` vs `wallsWithDetails`,
  `doorsWithDetails`, `elementsWithDetails` (for `SetDetailsOfElements`). Wrong key = whole call
  rejected, which can masquerade as "feature missing".
- **Read-back is asymmetric**: an element's layer is read top-level
  (`detailsOfElements[i].layerIndex`) but written via `details.layerIndex`.
- **Send full payloads on modify** for doors/windows — omitted size fields can reset to defaults.
- **Sanitize geometry before batching**: zero-length walls crash older releases outright; keep
  batch inputs clean rather than relying on guards.
- **Version-gate everything**: many fields exist only from a specific Tapir release. The
  verified-schemas file carries the gates; probe the connected instance at session start.
- **The most expensive failure class is "accepted and silently ignored"**: `succeeded:true`,
  no item error, model unchanged or partially changed — verified live for slab holes in wrong
  formats, stair step parameters, attribute deletes, `ac_*` GDL parameters, `pos` on unclipped
  drawings, `floorIndex` on texts and `SetLayoutSettings.layoutName` (AC26). Read the RAW
  response JSON (not the expected path), and never let an empty result stand without
  counter-checking one element whose target value is known.
- **A tool default can override a sent value**: a roof `thickness` looked ignored for weeks —
  the roof tool default was a composite, which defines the thickness itself. Before calling a
  parameter "ignored", read back the element's `structureType`/composite and send the structure
  type explicitly (`structureType:"Basic"` + `thickness`).
- **When a create parameter seems ignored, calibrate instead of guessing**: place two
  throwaway elements far outside the model with two DIFFERENT values of the suspect
  parameter, measure both bounding boxes, back-compute what actually applied, delete the
  probes. Never run format probes on real project elements.
- **Session entry probe**: time one 1-element and one 10-element read at session start; if
  the batch is not clearly faster per element, loop single reads (a 10-element read has hung
  >9 minutes while 30 single reads took 576 ms).
- **Blockade diagnosis on timeouts**: send a command the HTTP server answers without
  Archicad (an unknown command name returns "not found" instantly). If that returns but
  element commands hang, Archicad itself is busy — open modal dialog (the error names it),
  active tool, a user working in the model, or a locked Windows screen. If nothing answers at
  all, check who listens on the port (see "Port hijack").
- **Check the active window before interpreting element counts** — a section window in front
  makes every count read 0 (`GetCurrentWindowType` first).
- **An empty `{}` publish response is ambiguous**: verify the target file's rewrite timestamp and
  a fresh page render, never a stale image (see the publish-verification reference).
- **`SaveProject` right after a save can fail** ("Failed to save the project") on cloud-synced
  folders — wait ~20 s and retry, then check the file timestamp.
- **Carrier/helper geometry is diagnostic only** — probe elements and helper linework never stay
  in the final publish state; delete them once measured, and check every delete result.

## Documentation views: sections, details, drawings

### Recommended workflow for details

Details are **not** separate sections. The workflow is the Archicad Detail tool:

1. Every cut exists **once** as a model section at 1:50 (e.g. the cross-section through a shaft),
   created from a section marker in the floor plan and kept up to date from the model.
2. A detail is marked **inside that 1:50 section window** with the Detail tool: a *source* Detail
   marker with an area-based geometry method (rectangle, rotated rectangle, polygon) and
   "Create new detail viewpoint". Archicad creates a Detail viewpoint (Project Map, own Detail
   window) that is a **2D copy** of the marked part of the section.
3. Everything the model does not show (flashings, sealing layers, profiles, battens, screws,
   leader markers, hatches, notes, detail dimensions) is drafted with **2D elements in the Detail
   window**, on the project's drafting/annotation layers.
4. Linked Detail markers (no model source) are only references to an existing detail/drawing.
5. "Rebuild from source view" regenerates the model-derived 2D part of a detail. Community reports
   say manually edited exploded elements can be lost while newly drafted elements usually survive —
   keep drafting on its own layer and check the detail after every rebuild.
6. Never create one model section per detail just to get a 1:5 drawing: it multiplies views,
   section markers and vertical ranges, and puts the 2D drafting into section databases where a
   model rebuild changes the context under it.

Sources: Graphisoft Help "About Details" and "Create a Detail Drawing Viewpoint with Model Source".

### What the API can and cannot do here (live session, AC26 / Tapir 1.7.1)

- **No command places a source Detail marker** or rebuilds a detail (requested upstream as #1377;
  what works on existing markers is in `tapir-verified-command-schemas.md`, "Detail and Worksheet
  markers"). `CreateDetails` only makes
  *independent* detail databases without model source. Placing the marker in the 1:50 section is a
  manual step (or UI automation with the user's consent) — say so and ask for it; do not fall back
  to a separate section. A reference to an existing (old 2D) detail sheet can be drawn as 2D
  (frame + "D04" text) in the view.
- Once the marker exists, the detail is fully scriptable: find the `DetailDrawingItem` in the
  Project Map, `GetDatabaseIdFromNavigatorItemId`, `ChangeWindow {windowType:"Details", databaseId}`,
  then use the 2D create commands (`CreateLineElements`, `CreateArcs`, `CreateCircles`,
  `CreateSplines`, `CreateHatches`, `CreateTexts`, `CreateLabels`) in that database. Detail markers
  are readable as element type `Detail` (`DetailWorksheetDetails`: clipPolygon, linkData).
- **Hatches**: send the polygon *without* the closing point — a closed coordinate list (first =
  last) fails with "Failed to create new Hatch".
- **Reusing old 2D detail drafting**: copy by zones with a translation per zone, anchored on stable
  features (finished outer face, top edge of the new roof, surface of the existing roof); exclude
  everything the model/detail copy already shows; log every created GUID so the copy can be undone;
  render the layout and check visually before declaring it done.
- **Reading old 2D drawing sets**: old layout drawings are often clips of ONE 2D section window.
  Their `pos` is the model origin, so `model = (layout − pos) / drawingScale` turns each clip
  polygon into a model window; assign the old texts and dimensions (`GetDimensionData` gives exact
  witness coordinates) to the old views and re-measure every value from the current model instead
  of copying numbers.
- Section markers (`CutPlane`) are not readable or editable via the API ("Not yet supported element
  type"): marker length and vertical range are UI-only — but the drawing can be clipped (below).

### Drawings and layouts (live session, AC26 / Tapir 1.7.1)

- A newly created section database only becomes reachable after it has been placed as a drawing;
  `ChangeWindow` by navigatorItemId is rejected on AC25/AC26.
- **Clipping drawings works — if `position` is computed right** (verified 2026-10-21 for sections,
  elevations and floor plans). `clipPolygon` is in layout coordinates; the drawing's `pos` is the
  layout location of the view's MODEL ORIGIN (content on the layout = pos + model/scale), and
  Archicad stores `pos = position − clipMin`. To show model window [mx0..mx1]×[my0..my1] with its
  lower-left at layout point (Lx,Ly):
  - clip = rectangle from (Lx,Ly) with size ((mx1−mx0)/scale, (my1−my0)/scale)
  - pos = (Lx − mx0/scale, Ly − my0/scale); send `position = pos + (Lx,Ly)`.
  A naive `position` puts the content outside the clip → "blank drawing" (the earlier failure).
  Section/elevation model coordinates: x along the marker, y = absolute height; obtain exact values
  with temporary `CreateAssociativeDimensionsOnSection` probes (bounding-box presets) +
  `GetDimensionData`, then delete the probes. Floor plans with a rotated view carry an extra
  offset: create once, read back `pos`, correct `position` by the error, recreate (converges in 1 step).
- Drawings of detail/worksheet views can be clipped the same way (their `pos` also refers to the
  view's model origin / saved zoom).
- **Drawing title can be removed via API**: `SetDetailsOfElements` →
  `details.typeSpecificDetails = {titleLibraryPartIndex: 0}` ("No title", titleElementId becomes
  null); `numberingType`/`customNumber` are settable the same way. Office style "title as layout
  text": remove the title and create the title text on the layout.
- Setting `pos` on an UNclipped drawing is accepted and ignored; clipped drawings move when `pos`
  and `clipPolygon` are shifted together. To "move" an unclipped drawing, delete and recreate it.
- Drawings did not refresh after model/2D edits in AC26; delete and recreate the drawing at the same
  `position` (or test `UpdateDrawings` on the connected build). Log the current drawing GUID per
  sheet slot so a re-run replaces it.
- Layout texts (titles, legends, notes, index rows, date field) can be copied between layouts with
  `CreateTexts` (style + runs). Put them on a layer that is visible in every combination
  (layer 1 "Archicad layer"), otherwise they vanish with the user's layer settings. Moving or
  rewording a layout text on AC26/1.7.1 = recreate it (style copied) and delete the old one; when
  selecting texts by content, match precisely (a prefix match caught a second, older text).
- Layout settings: `SetLayoutSettings` with `customLayoutNumber`, `customLayoutNumbering`;
  `layoutName` was accepted and ignored on AC26 — rename in the UI.
- `PublishPublisherSet` only publishes an existing publisher set (`API.GetPublisherSetNames`
  lists them); new layouts are not in any set — PDF export of new sheets is a UI step unless the
  user adds them to a set.

### Dimensions in sections and plans (live session, AC26 / Tapir 1.7.1)

- `CreateAssociativeDimensions` with section-element witnesses returns a GUID for an element that
  does not exist (ghost) — use `CreateAssociativeDimensionsOnSection` presets instead:
  `WallSkinBorders` + `skinBorderIndices:[1,2]` gives clean core-face chains;
  `BeamOrColumnRefLineEndPoints` gives clean chains (coincident points become zero segments, which
  are not displayed); `BeamOrColumnBoundingBoxCorners` and `WallCompositeFaces` always add midpoints.
  Clean vertical (height) chains are not possible with presets; level dimensions:
  `CreateLevelDimensions` since Tapir 1.7.2 (verified; floor plan only).
- **Free (static) dimension chains anywhere, incl. vertical height chains in sections**: create short
  2D helper lines lying ON the dimension line between consecutive measuring points, then
  `CreateAssociativeDimensions` with witnesses `{elementId: line_i, inIndex: 1, special: 0}` for every
  line plus `{elementId: line_last, inIndex: 2}`, `referencePoint` = first point, `direction` = chain
  direction. Values are exact and the result is a normal Archicad dimension (helper lines disappear
  under the dimension line; give them the solid line type — the default line type may be dashed).
  The chain is static with respect to the model: recompute after model changes and keep the script.
  Witnesses on Roof elements resolve to wrong coordinates (segment ≈ distance to the origin) — use
  helper lines there too, also in floor plans. For plans of rotated buildings, work in a local frame
  (s along an edge, d perpendicular) and convert to model x/y.
- **Height marks in sections/elevations**: the Level Dimension tool is not available in
  section/elevation windows and the "Elevation dimension" method is UI-only → draw them as 2D:
  level line, filled triangle (solid-fill hatch with 3 points, apex on the line) and text "+22,86"
  (optional second line "OK Dach"). Keep text inside the drawing's clip window.
- Floor-plan beam witnesses: `special:0`; `inIndex` 1 = end point on the reference line,
  2 and 4 = begin corners (both sides), 3 = end corner.
- **Layer trap for new dimensions**: they land on the dimension tool's default layer. If that layer is
  hidden in the current layer state, the dimension is invisible AND not editable/deletable ("The
  element was not deleted, because it is not editable", "Failed to change element"). Show that
  layer during creation, set `details.layerIndex` to the target dimension layer (moving onto a
  hidden target layer works), hide it again. The same applies to probe dimensions — delete them
  while their layer is visible and check results.
- **Texts**: in floor plans pass `floorIndex` to `CreateTexts` (without it the text lands on floor 0;
  `SetDetailsOfElements.floorIndex` on texts is ignored). Text angle = direction of the edge it
  labels; `flipEnabled` keeps it readable. Texts over cut fills (walls): raise `drawIndex`. A text
  with background fill hides dimension lines under it — switch `usedFill` off or move it.

### Sheet set for a trade (e.g. roofer's quote) — proven sequence

1. Save, then work only through the API (user keeps working elsewhere).
2. Determine sheet budget: A3 = 0.42 × 0.297 m; subtract title block / note boxes; compute each view's
   window at 1:50 (model metres / 50) and decide 2–3 sheets before placing anything.
3. Place every view as a clipped drawing (formula above), remove the drawing title, add the title as
   layout text in the office style (copy style from an existing sheet).
4. Measure the needed geometry (probes / element details), then add chains with helper lines and
   height marks as 2D, all on the annotation layers of the view's layer combination; log every GUID
   per view so a whole view's annotation can be undone and regenerated.
5. Recreate the drawings, render each sheet with `SaveCurrentWindowAsImage`, fix overlaps/clipped
   text, cross-check chain sums against the model, update index row and date, save.
6. Compare against the previous (2D) drawings item by item — dimensions, height marks, legend
   letters, notes, view markers, section line, north arrow — transfer everything re-measured, and
   report values that changed (and design conflicts the new numbers reveal) instead of copying.

### Modelling details that affect documentation

- Elements on hidden/locked layers cannot be moved, deleted or modified ("layer is hidden",
  "not editable"). Showing layers via `CreateLayers overwriteExisting` changes the user's current
  layer settings — restore them afterwards and say so.
- `CreateWalls.zCoordinate` is stored as the bottom offset relative to the home story, not as an
  absolute elevation — set/verify `bottomOffset` explicitly.
- What a section shows where elements overlap is decided by building-material priority (e.g.
  masonry 625 beats timber 520). For timber that must stay visible (rafters, sill plates), assign a
  dedicated building material with higher priority instead of changing the global timber material.
- A locked Windows screen stops UI automation; API calls keep working.

## Object and fixture placement: measure, then snap

Library objects place at their libpart origin with orientation conventions the API does not
expose. Do not trust assumed sizes or rotations. Protocol:

1. Place **one** instance of every object type in a blank staging area far from the model.
2. Read its actual bounding box and facing convention back (`Get3DBoundingBoxes`,
   `GetDetailsOfElements`); use `RotateElements` to establish the rotation behavior.
3. Only then place/reposition all real instances using the verified dimensions and offsets,
   and delete the staging instances.

Parametric macro objects (stairs, kitchen blocks) are frequently unusable through the API —
prefer native elements or individual parts, and verify every placement by bounding box.

## Safety rules

- Never delete, overwrite attributes/favorites, bulk-create, change layout conventions, or
  perform Teamwork reserve/release without explicit confirmation.
- Default `overwriteExisting`-style flags to `false`.
- If the open file is untitled or unsaved, say so before significant modelling.
- If a command is missing on the connected build, state the limitation and offer a manual
  Archicad step — never invent a command.
- If Archicad reports `Invalid program status (ongoing user input)` or names an open modal
  dialog, stop mutating: the host UI is blocked. Ask for the dialog to be closed, confirm
  recovery with a cheap read call, then resume.

## Output contract

Report: project/port used, planned vs. executed calls (high level), created/modified GUIDs and
counts, verification evidence, and any unresolved assumptions.

For pipelines that start from drawings/scans/references, accept the intermediate model from
`abstracting-building-models` and preserve its evidence/confidence/uncertainty fields in the
Archicad implementation notes.

