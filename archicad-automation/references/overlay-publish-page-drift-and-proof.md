# Overlay proof when the published plan moves on the page

Use this note when a measured-plan verification run needs a trustworthy source-vs-publish overlay and the published drawing may have shifted on the layout page.

## Core lesson

Do not assume an older published crop box is still valid after later model/view/layout iterations. The plan can move on the sheet even when the geometry itself is similar. If you reuse a stale crop, the overlay can look empty or nonsensical even though the publish actually contains plan content.

## Required verification sequence

1. Publish the real layout PDF.
2. Render the full published page to PNG.
3. Inspect the full page first, not only an old content crop.
4. Detect or measure the current non-white / real-content bounding box from the fresh full-page render.
5. Re-run the calibrated overlay with the new published box.
6. Only then interpret red/cyan geometry differences.

## Practical signs of stale registration

- The registered publish crop looks blank/white while the full published page still contains a plan lower or higher on the sheet.
- Overlay summary shows near-zero `published_only` and `common` pixels even though the PDF timestamp advanced.
- A previous fallback crop came from an older publish profile or earlier page placement.

## Deliverable rule

If the overlay is requested, show the actual image artifact directly in the reply, not just a textual summary. Prefer the cleanest comparison image first:

1. line-only overlay (best for geometry review)
2. structural-difference overlay (useful but louder)
3. registered published plan

## Interpretation rule

When the line-only overlay is available:

- red = only in source
- cyan = only in current publish
- dark gray = overlap
- orange = shared bottom-left origin

Use the overlay to call out concrete hotspots: interior wall axes, stair geometry, wet-room core, facade openings, and entrance situations. Do not claim success from numeric readbacks alone when the overlay still shows visible geometric disagreement.
