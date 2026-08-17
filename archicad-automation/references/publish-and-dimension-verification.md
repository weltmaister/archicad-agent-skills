# Publish and dimension verification in Archicad automation

Use this reference when the task is a measured-plan style verification run: mutate model geometry, regenerate dimensions, publish a layout PDF, and prove that the visible output matches the intended chains.

## Reliable verification sequence

1. **Mutate the model first, then re-read live state**
   - verify changed wall/column/slab bounding boxes after each batch;
   - do not assume a successful modify call implies a visible publish change.

2. **Regenerate dimensions explicitly**
   - if the task is to match a source measured plan, delete stale `Dimension` elements before creating new chains;
   - create associative chains only after mapping source strings to explicit witness-point sequences;
   - use `elements_create_wall_thickness_dimensions` for thickness callouts instead of trying to fold them into one generic chain.

3. **Publish the specific layout item, not the whole publisher set blindly**
   - prefer `navigator_publish_publisher_set(selectedNavigatorItemIds=[...])` with the publisher-tree LayoutItem GUID when the target layout already exists;
   - verify the target PDF was freshly rewritten by checking modification time, not only automation success/empty `{}` output.

4. **Inspect the published PDF directly**
   - render page 1 to PNG for visual review;
   - extract page text and look for room names and dimension strings;
   - if the fresh PDF has `extract_text() == ""` (or zero meaningful text) **and** the rendered page is effectively all-white/blank, treat that as a failed publish/view-path result even when the file timestamp advanced;
   - for measured-plan work, compare the extracted numeric chains against the expected source chains.

## Important runtime quirks

### 1) Slab footprint edits may not be supported in-place

A live Archicad 28 / Tapir run accepted `elements_modify_slabs` for the tool itself but returned:

- `-2130313112: No slab fields to modify.`

when trying to change `polygonOutline` only.

**Practical rule:** when the task is to change slab footprint / plan extent, be ready to:

1. record the current slab GUIDs and levels/floor indices;
2. delete the old slabs;
3. recreate replacement slabs with the corrected polygon coordinates;
4. verify the new slab bounding boxes immediately.

Treat delete/recreate as the normal fallback for slab-outline corrections, not as a last-minute panic move.

### 2) Publish output path may need to be a directory path

In one live publish run, `navigator_publish_publisher_set` returned `{}` with no visible error when given a file-like path, but the reliable update came from publishing the selected LayoutItem to the known output **directory** and then checking that the expected PDF file was freshly rewritten.

**Practical rule:** if publishing appears to succeed but the PDF timestamp does not change, retry with:

- the known publisher output directory (`<output-folder>`),
- `selectedNavigatorItemIds` set to the exact publisher LayoutItem,
- timestamp verification on the resulting PDF file.

Do not conclude that the publish failed until you verify the target file.

## Dimension-chain proof pattern

For a measured-plan correction, the proof should not stop at "dimensions are visible". Do this instead:

1. define the expected chain strings from the source (`top`, `bottom`, `left`, `right`, inner/outer as needed);
2. extract the new PDF text;
3. test whether each expected chain appears as an ordered subsequence;
4. document which chains are complete, partial, or missing.

This is stronger than a visual-only claim and catches cases where some chains are present but in the wrong grouping.

## When overlay and publish disagree

If the publish shows correct numeric chains but the structural overlay still looks noisy:

- trust the direct numeric chain comparison for dimension correctness;
- then isolate remaining geometry mismatches to local hotspots (for example stair/object-heavy cores, terrace edge conditions, or short wall stubs) rather than discarding the whole correction pass.

## Dimension-aware overlay calibration rule

A failed live comparison exposed a common overlay mistake: if the published layout is missing some or all outer dimension chains, you must **not** derive the registration crop from the publish content bounding box alone. That shrinks the publish crop, changes the effective scale, and makes the origin look wrong even when the plan body is roughly aligned.

Use this safer pattern instead:

1. calibrate the shared scale/origin from the same physical outer plan contour (not from the full visible content box);
2. measure the source-side margins from outer contour to the full measured-plan crop (the zone that includes all source dimension chains);
3. transfer those margins proportionally onto the published page using the contour-based scale factors;
4. generate the final overlay from those two expanded boxes.

Practical consequence: a dimension-aware overlay should show the missing source chains as red source-only content around the plan, while keeping the plan body at a stable shared scale. If the overlay only shows the bare plan but no outer chains, it is not an acceptable measured-plan verification artifact.

## Corner-anchored registration rule

A second failure mode from the same class of comparisons: even with dimension-aware margins, a crop-and-resize overlay can still leave the building corners visibly apart because the registration is being driven by bounding boxes instead of the real outer wall corners of the main building mass. When a reviewer explicitly reports that the exterior wall corners do not coincide, treat that as a registration failure, not as a model-geometry conclusion.

Use this escalation path:

1. detect or manually verify the four outer wall corners of the **main building body** (not terrace posts, not page content box, not the visible measure chains);
2. compute a four-point transform from published page to source page using those corners;
3. only then crop the larger dimension-aware verification region around the transformed plan;
4. generate the overlay from the transformed publish crop and the source crop.

This guarantees that top-left / top-right / bottom-right / bottom-left building corners are the anchor truth. Only after those corners plausibly coincide is the overlay acceptable for judging wall offsets, interior topology, or missing dimension chains.

## Direct dimensioning rule — no artificial witness carriers

For production/readback dimensioning, do **not** create artificial helper walls, helper polylines, or other carrier elements just to obtain numeric dimension chains. They contaminate the model and can create misleading success signals. Dimensions must reference the real modeled elements:

- exterior/interior wall edges: use the actual Wall element IDs as witness references;
- windows/doors: use the actual Window/Door element IDs; when a whole opening collapses to a coarse segment, retry with explicit opening-edge witness references (`line: false`, `special: 1`, `inIndex: 1/2`) instead of introducing carriers;
- terraces/posts/slabs: use real Column/Slab/Wall elements only if they are part of the modeled geometry being dimensioned.

If the API can only produce a coarse chain from real elements, report that limitation directly and fix the modeled element references or Tapir witness-point support. Do not hide the issue with synthetic dimension-only elements.

In measured-plan cases with a terrace or other attached side geometry, the nominal "top-right" or "bottom-right" content near the building can be contaminated by terrace posts, side walls, door swings, or hatch masses. Do not overclaim corner alignment from a full-plan view alone. After a corner-anchored transform, inspect small local corner crops and verify that each detected corner still belongs to the **main building body**. If the right-side top and bottom candidates imply different visible x-positions, allow a slight projective/sheared four-point fit or re-pick the semantic main-body corner explicitly instead of forcing a rectangular assumption or silently treating the terrace edge as the building corner.
