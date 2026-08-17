# Full scan-to-BIM rebuild pattern from measured-plan source

Use this pattern when the goal is not just to patch an existing Archicad model, but to prove a clean, reproducible end-to-end workflow from source plan to rebuilt BIM model and published verification.

## When to prefer this over incremental repair

Choose the full rebuild path when most of the following are true:

1. the task explicitly calls for an end-to-end scan-to-BIM rehearsal;
2. the current live model may contain legacy helper geometry, stale carriers, or earlier experimental dimensions;
3. the measured-plan chain structure is already better understood than the current live topology;
4. the available write coverage is strong enough for the main native elements (walls, doors, windows, slabs, zones, columns);
5. the available read coverage is strong enough to verify the rebuilt result (`GetDimensionData`, `GetDoorsDetails`, `GetWindowsDetails`).

## Recommended execution sequence

1. **Consolidate a source-derived rebuild specification first.**
   - Write one explicit JSON or Markdown spec for target geometry, openings, slabs, zones, columns, and dimension chains.
   - Include fixed assumptions such as coordinate system, storey height, target publish path, and chosen building materials.
   - Do this before destructive edits so the rebuild is driven by evidence rather than improvised from memory.

2. **Capture a pre-delete baseline.**
   - Record active project/port/path.
   - Record element counts and GUID inventories by type.
   - Record why the rebuild scope is being fully replaced.
   - Treat this as the rollback/audit trail.

3. **Delete the full modelling/documentation scope deliberately.**
   - For a true rebuild rehearsal, clear walls, doors, windows, slabs, zones, columns, and dimensions inside the target scope.
   - Verify that the model is actually empty for those types before recreating anything.

4. **Recreate the native model core first.**
   - Walls first.
   - Then hosted openings (doors/windows).
   - Then slabs, zones, columns.
   - Do not start dimension reconstruction before the host geometry exists.

5. **Use carrier geometry intentionally for measured-plan dimension reconstruction.**
   - If exact original witness points cannot be bound directly to the real model geometry, create explicit short/thin carrier walls at the source-derived witness coordinates.
   - Dimension the carriers associatively.
   - Keep them conceptually separate from the real model: they are a control grid, not proof that the real geometry is already correct.

6. **Rebuild both chain structure and wall-thickness callouts.**
   - Use associative dimensions for the main source chains.
   - Use wall-thickness dimensions separately for thickness verification.
   - Verify the whole chain topology, not just isolated values.

7. **Verify with readback before publish.**
   - Read doors with `elements_get_doors_details`.
   - Read windows with `elements_get_windows_details`.
   - Read dimensions with `elements_get_dimension_data`.
   - Confirm that widths, offsets, sill heights, chain values, and chain positions match the rebuild spec.

8. **Publish and verify the publish, not just the model.**
   - Publish to the fixed, agreed target path (`<output-folder>`).
   - Confirm file rewrite by timestamp.
   - Extract page text from the fresh PDF and compare it to the expected source chain values.
   - If available, do a visual overlay/render check after rerendering from the fresh PDF, not from an old cached PNG.

## Strong lessons from live runs

### 1) Source-derived spec first, destructive actions second
A full rebuild is only safe if the target state is written down before deletion. Without that, the workflow degrades into ad-hoc re-modelling.

### 2) Readback APIs make the rebuild genuinely testable
Once `GetDimensionData`, `GetDoorsDetails`, and `GetWindowsDetails` are live, the rebuild can be verified as structured model state rather than only by screenshots.

### 3) Carrier-based dimensions are a valid verification layer
For measured-plan reconstruction, explicit carrier walls at witness coordinates are a practical way to reconstruct source chains reproducibly when direct witness-point APIs for real elements are still incomplete.

### 4) Publish verification must include structure, not only number presence
The best verification stack is:
- chain values from `GetDimensionData`,
- opening parameters from door/window detail reads,
- fresh publish timestamp,
- PDF text containing the expected published chain values,
- optional visual overlay.

## Minimal output contract for this workflow

Report all of the following:

- active Archicad project + port;
- spec file used for the rebuild;
- full delete scope;
- created counts by element type;
- whether the readback counts match the intended rebuild;
- exact dimension chains read back from `GetDimensionData`;
- exact opening widths/offsets read back from door/window detail tools;
- publish target path and publish verification result.

## Pitfalls

- Do not leave the task list claiming the rebuild is still pending after the live rebuild already happened; update the task state to reflect real progress.
- Do not treat successful model recreation as enough; the workflow is only complete once the publish output is checked too.
- Do not rely on stale exported page renders when validating the final state; always re-read the fresh PDF or rerender from it.
- Do not confuse carrier geometry with the native model core in later follow-up work; document the distinction explicitly.
