# Overlay registration and view-profile notes

Notes for iterative Archicad publish-vs-source comparison, derived from a measured-plan training run.

## When to use

Use these notes when you are repeatedly:

1. changing Archicad view/publisher settings,
2. publishing a PDF,
3. rendering it to an image,
4. overlaying it against a source drawing,
5. deciding whether the differences are geometry or presentation noise.

## Main lesson

A calibrated overlay pipeline must not depend on a hard-coded published crop box once you start changing view settings. Even with unchanged model geometry, the published drawing can move or scale within the page because of:

- model view options,
- graphic overrides,
- pen sets,
- drawing scale,
- publisher/layout presentation.

Therefore:

- keep the **source full-page box** fixed only after validating it really spans the intended real outer contour,
- re-detect the **published outer contour** on each fresh publish render,
- keep only a last-known box as fallback.

## Practical detection pattern

A robust heuristic for the published image:

1. render the published PDF page to a raster at the same DPI as the source comparison,
2. threshold to isolate dark linework,
3. use horizontal and vertical morphological opening kernels sized relative to image width/height,
4. collect connected components,
5. keep long, sufficiently thick horizontal/vertical candidates,
6. derive the outer box from min/max extents of those candidates.

This works better than using the non-white bbox of the whole page because text, dimensions, stamps, terrace markers and layout noise can distort the crop.

## Comparison outcome from the training run

Tested view profiles behaved very differently for overlay purposes:

- A general working-settings profile reduced some fill noise but still produced too much presentation mismatch.
- An execution-planning (construction-documentation) profile was clearly worse for overlay comparison because it added dense dimension chains and opening labels around the plan.
- The best presentation match among the tested profiles was a presentation/marketing-style setup: a reduced-annotation model-view-options combination, a matching presentation layer combination, a graphic-override combination that renders all components black, a 1:100/1:200 pen set, and `drawingScale: 200` matching the source plan scale.

A nearby variant with graphic overrides disabled introduced colored room fills and moved farther away from the source style.

## Decision rule

When a view-profile test changes the publish look, ask two separate questions:

1. **Does it reduce presentation noise?**
   - fewer room tables,
   - fewer door/window labels,
   - fewer dimension chains,
   - wall graphics closer to source.
2. **Does the calibrated overlay improve structurally?**
   - more common pixels,
   - fewer source-only / publish-only structural regions,
   - visually better agreement at staircase, wet-room block, facade splits, terrace edge.

If a profile only changes graphics but worsens the structural overlay or adds strong noise, revert it.

## Typical remaining true-geometry zones

After presentation was reduced, the meaningful residual differences were concentrated in:

- stair / landing zone near the hallway,
- wet-room / utility-room partitioning and connections,
- facade / terrace opening alignment.

Treat these as modelling targets, not rendering targets.
