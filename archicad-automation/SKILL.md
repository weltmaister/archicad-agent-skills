---
name: archicad-automation
description: "Use when operating Archicad through the Tapir add-on's JSON API: inspecting an open project, creating or modifying BIM elements (walls, slabs, openings, roofs, zones, stairs), reading element details, placing associative dimensions, managing layers and attributes, creating views and layouts, or publishing. Talks HTTP to the Archicad host on ports 19723-19743. Pairs with abstracting-building-models when drawings or scans must first be interpreted."
license: MIT
metadata:
  version: 1.0.0
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
- Executing a source-derived building model produced by `abstracting-building-models`
  (use that skill FIRST when the task starts from scans, PDFs, photos, or vague references).

## Operating sequence

1. **Discover the port**: scan 19723–19743 on the Archicad host; the first responding port is
   the active instance. The JSON server only listens while a project is open, and it listens on
   localhost only — if your agent runtime cannot reach the Archicad host's localhost, run the
   HTTP calls host-side.
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

## Protocol

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
| `templates/` | Rebuild-plan and overlay-report templates. |

## Golden rules (the short list)

- **Element IDs are nested objects**: every command that takes element IDs wants
  `{"elementId": {"guid": "..."}}` (or `{"guid": ...}` inside named fields like `ownerWallId`).
  A bare GUID string fails validation — and `DeleteElements` with the wrong shape returns
  `succeeded: true` while deleting **nothing**.
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
  formats, roof `thickness`, stair step parameters, attribute deletes, and `ac_*` GDL
  parameters. Read the RAW response JSON (not the expected path), and never let an empty
  result stand without counter-checking one element whose target value is known.
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
  active tool, a user working in the model, or a locked Windows screen.
- **Check the active window before interpreting element counts** — a section window in front
  makes every count read 0 (`GetCurrentWindowType` first).

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

- Never delete, overwrite attributes/favorites, bulk-create, or change layout conventions
  without explicit confirmation.
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
