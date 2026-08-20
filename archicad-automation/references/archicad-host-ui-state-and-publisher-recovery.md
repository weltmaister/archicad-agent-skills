# Archicad host UI-state and publisher recovery notes

Use when a previously working Archicad/Tapir session suddenly rejects unrelated commands or when remembered layout/publisher IDs stop working after reopening the project.

## Modal UI-state blocker

If direct Tapir HTTP calls start failing with an error of the form:

- `Invalid program status (there is an open modal dialog: <dialog name>)` — note that the dialog name in the message is localized to the host Archicad's UI language
- or another `Invalid program status` / modal-dialog message

then treat this as a **host UI-state block**, not as a geometry/schema bug.

### Required response

1. Stop sending further create/modify/publish retries into the blocked state.
2. Report exactly which modal dialog is open.
3. Ask for the host-side dialog to be closed/cancelled.
4. Re-test with a cheap read call (`GetProjectInfo`, `GetCurrentWindowType`) before resuming mutations.

Do not interpret door/window/publisher failures observed during the modal state as evidence about defaults or payload shape.

## SaveProject fails from the 3D window

`SaveProject` returns `succeeded:true` at call level with an item error
`-2130312308 "Failed to save the project."` whenever the **3D window** is the active
window. The project is not written; the file mtime does not move.

Live-verified 2026-08-20 (AC28, current main build): two consecutive `SaveProject` calls
failed with the 3D window active (`GetCurrentWindowType` → `3DModel`); after
`ChangeWindow {"windowType":"FloorPlan","storyIndex":-1}` the very next `SaveProject`
succeeded and the `.pln` mtime advanced.

**Discipline:** read `GetCurrentWindowType` before every save; if it is not a floor plan,
switch, save, and switch back to whatever the user was looking at. Treat a failed save the
same as a modal-dialog block: never keep mutating on top of an unsaved model.

**Schema note:** the `ChangeWindow.windowType` enum value for the 3D window is exactly
**`3DModel`**. `Model3D`, `3D`, `ThreeD`, `Perspective`, `Axonometry` are all rejected with
`-2130313112 "Invalid parameter: windowType."`

## Reopen-the-real-project recovery step

If the session looks structurally wrong after restart (for example missing libraries, dead publisher assumptions, stale layout/view IDs), use this sequence:

1. `GetProjectInfo`
2. `SaveProject`
3. `OpenProject` on the real saved `projectPath`
4. Re-check `GetProjectInfo`
5. Re-check `GetLibraries`

This can restore the real file context and loaded built-in libraries, but it does **not** guarantee that remembered navigator IDs or publisher-set names still exist.

## Dead navigator ID pitfall after reopen

A previously recorded navigator/view/publisher GUID can come back as:

- `navigatorItemId is corrupt or missing`

after reopening the project.

Treat old navigator IDs as session-bound evidence, not durable truth. After reopen:

1. probe the remembered IDs once;
2. if they are corrupt/missing, stop relying on them;
3. rebuild the live publish/view path from the current file state instead of retrying stale IDs.

## Publisher-set name pitfall after reopen

Even after reopening the correct saved project, `PublishPublisherSet` can still fail with:

- `Not valid publisher set name.`

Do not keep retrying the old remembered set name. Re-discover the live publisher structure or ask for the current valid publisher-set name from the host UI.

### Exact-name discipline

If the operator says they created a publisher set and only gives the output path, that is **not** enough to resume API publishing. `PublishPublisherSet` needs the exact live publisher-set **name**, not the output directory and not a likely layout/file name. Treat the path as evidence that host-side publishing is configured, but still ask for or rediscover the real set name before retrying the API call.

### Existing-file inspection fallback

If API publishing is blocked or the set name is still unknown, check whether the watched output directory (`<output-folder>`) already contains a freshly written PDF from host-side publishing and inspect that artifact instead of stalling. A real exported PDF is stronger evidence than a successful-looking but unverified publish call.

## Publish corruption from leader labels

If the published PDF shows a fan of long arrows/rays across the whole plan, first suspect `Label` elements used as a text fallback. In one live case, label-based room names published as long leader arrows radiating across the sheet and visually destroyed an otherwise usable plan.

Required response:

1. read the published artifact, not just the model state;
2. identify `Label` elements as likely culprits;
3. delete the label elements in a bounded batch;
4. republish and re-check the PDF.

Do not leave leader-label text fallbacks in the final measured-plan publish state.

## Native door/window defaults: re-test only after UI-state is clean

If `CreateDoors` / `CreateWindows` fail with:

- `Failed to prepare door defaults.`
- `Failed to prepare window defaults.`

make sure the modal-dialog state is already cleared first. Only then interpret the failure as a real defaults/library/favorite problem.

## PrintView caution

`PrintView` may return `success: true` while producing no user-accessible output file in the expected watched folder. Treat this as a weak signal only; do not present it as a verified export result without an actual file artifact.
