# Host defaults, library reload, favorite payload shape, and opening fallback

Use this note when a fresh/restarted Archicad session behaves differently from older validated runs during a measured-plan rebuild.

## Durable lessons from live rebuild runs

### 1) Fresh session can lose usable door/window defaults even when geometry tools still work
Symptoms during live rebuild:
- `CreateWindows` → `Failed to prepare window defaults.`
- `CreateDoors` → `Failed to prepare door defaults.`
- `GetLibraries` initially showed only the embedded library.

Action pattern:
1. Check `GetLibraries` before assuming the model payload is wrong.
2. If only the embedded library is loaded, run `ReloadLibraries` and re-check.
3. After reload, verify whether built-in libraries reappear.
4. Even if libraries reappear, do **not** assume door/window defaults are now usable — retest one minimal door and one minimal window on known-good host walls.

Reason: library presence and usable opening defaults are related but not equivalent. In the observed case, built-in libraries returned after reload, but door/window default preparation still failed.

### 2) `ApplyFavoritesToElementDefaults` payload shape matters
A wrong payload can look superficially plausible but fail silently or return an unhelpful default-setting error.

Observed working shape:

```json
{
  "favorites": [
    {"favorite": "window-favorite-name"}
  ]
}
```

Observed non-working shape:

```json
{
  "favorites": ["window-favorite-name"]
}
```

Operational rule:
- pass favorites as objects, not bare strings;
- then retest the real create call immediately.

Important follow-up lesson: a successful `ApplyFavoritesToElementDefaults` response still does **not** prove that `CreateDoors` / `CreateWindows` will work in the current host state. Always verify by creating one real opening.

### 3) When door/window defaults remain broken, switch to native `CreateOpenings`
If the task requires a real redraw/rebuild and the host still rejects door/window defaults after:
- reloading libraries,
- verifying host walls,
- and testing favorites/defaults,

then the productive fallback is:
1. continue with native walls/slabs/columns;
2. create wall-hosted `Opening` elements for door/window holes;
3. verify counts and `Get3DBoundingBoxes`;
4. report clearly that geometry is rebuilt but library-part symbolics are still blocked by host defaults.

This keeps the reconstruction geometrically real and reversible. It is better than stopping with only a plan description, and better than faking door/window completion from unverified assumptions.

### 3a) Wrapper validation noise can hide the real host-side opening failure
In one fallback batch, bulk `CreateDoors` / `CreateWindows` did not come back as clean Archicad element-error payloads in the agent. Instead the wrapper layer raised Pydantic-style `CreateDoorsResult` / `CreateWindowsResult` validation failures because the returned items contained `error` objects instead of `elementId`. The raw embedded Archicad-side signal still mattered:
- error code `-2130313110`
- message family `Failed to create door.` / `Failed to create window.`

Operational rule:
- do **not** misdiagnose this as proof that the geometry payload shape is wrong;
- preserve the raw failing response/log for later wrapper debugging;
- interpret it first as a host/default-preparation failure unless a smaller single-item probe proves otherwise;
- then either recover defaults or switch to the `CreateOpenings` fallback.

### 3b) Once you switch to `CreateOpenings`, change the verification and reporting contract
After the fallback switch, stop talking as if native door/window semantics still exist.

Required practice:
1. keep a stable source-opening → `Opening` GUID mapping in the case artefacts;
2. verify the fallback batch with live counts and `Get3DBoundingBoxes`, not only with a create-call success flag;
3. report the live state explicitly as placeholder geometry.

Example of a verified fallback state snapshot (element counts by type):
- `Wall: 12`
- `Opening: 14`
- `Slab: 2`
- `Column: 4`
- `Door: 0`
- `Window: 0`

Do **not** continue using `GetDoorsDetails` / `GetWindowsDetails` as if those placeholders were native Door/Window elements. At that point the correct readback tools are the opening GUID map, bounding boxes, publish/overlay checks, and any 2D proof-layer artefacts. Treat symbolics, schedules, and opening semantics as still unresolved until real native Door/Window creation works again.

### 4) New/restarted file can invalidate previously known publisher-set assumptions
A previously successful publisher-set name (for example a "floor-plan PDF" set) may no longer exist in the freshly started file.

Observed symptom:
- `PublishPublisherSet` → `Not valid publisher set name.`

Operational rule:
- treat old publisher-set names as file-specific, not globally durable;
- re-read the live navigator/publisher state before assuming a past publisher set still exists;
- if publisher structure is missing, do not report publish success from historical knowledge.

### 4a) Fresh session can silently reopen on `Untitled` / `projectPath: null`
In one recovery log, the active project probe before the rebuild batch reported:
- `projectName: "Untitled"`
- `projectType: "untitled"`
- `projectPath: null`

Operational rule:
- run `GetProjectInfo` at the start of every fresh-session rebuild batch, not only when connectivity is first restored;
- if the session is `Untitled` / pathless, downgrade all cached case assumptions immediately: old GUID inventories, publisher-set names, and claims about which project file is open are no longer trustworthy;
- rebuild live evidence from the current host state before destructive edits, and report any results as belonging to the currently open session unless the intended project file is re-proved.

This is stricter than merely calling out an unsaved file: in restart/recovery flows it protects against accidentally treating a temporary session as if it were the intended case project.

### 5) Verification hierarchy for rebuild sessions
When the session is in this degraded host state, use this proof order:
1. live element counts by type;
2. readback via `Get3DBoundingBoxes` / detail calls;
3. geometry preview reconstructed from live bounding boxes;
4. only then publisher/PDF verification once live publisher state is re-established.

## Recommended bounded retry sequence

For fresh-session rebuilds with opening failures:
1. `GetProjectInfo`
2. `GetLibraries`
3. if needed `ReloadLibraries`
4. `GetFavoritesByType` for `Door` / `Window`
5. `ApplyFavoritesToElementDefaults` with object payloads
6. one minimal `CreateWindows` test
7. one minimal `CreateDoors` test
8. if still failing: switch to `CreateOpenings` fallback and continue the rebuild

Do not loop on bulk door/window creation while the single-item probe still fails.
