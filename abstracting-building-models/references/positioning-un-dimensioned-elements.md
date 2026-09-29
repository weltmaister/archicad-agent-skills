# Positioning un-dimensioned elements (constraint-first, not pixel-first)

Load this when the source plan contains elements the dimension chains do NOT position (terrace
columns, fixtures, stairs, built-ins) and their location/size must be derived.

Some elements carry no dimension text. Do **not** just pixel-measure them — pixels are within
0.05–0.15 m and unanchored. Instead **anchor them to the dimensions you already trust** and let
pixels fill only what is left. Strategies, strongest first, combined:

1. **Constraint / alignment to dimensioned geometry** — un-dimensioned elements usually align with
   dimensioned ones (a column's outer face flush with the dimensioned terrace edge; an axis flush
   with a wall face or opening jamb; a fixture flush against a wall). Each such alignment fixes ONE
   coordinate exactly, with zero pixel error.
2. **Symmetry** about a dimensioned axis (building centre, opening centre). Measure roughly, then
   force exact symmetry (average the pair). Halves the measurements and removes bias.
3. **Regularity / module / grid** — repeated elements are usually equally spaced or on a module
   (often 12.5 cm). Fit the rough positions to an equal-spacing/grid model anchored at dimensioned
   endpoints (least-squares), instead of taking each centre independently.
4. **Standard / catalogue size for the DIMENSION** — an un-dimensioned element's size is almost
   always a standard product or library part (column 24/30, door leaf 0.885, standard
   sanitary-fixture sizes). Placing the correct library part gives the true size with no
   measurement.
5. **Sub-pixel centroid, not a single edge** — detect the whole outline (contour/Hough), fit a
   rectangle, take centroid + size, then snap to module. More robust than reading one edge.
6. **Cross-view** — a section/elevation often dimensions what the plan omits (heights, depths).
   Reconcile across views.
7. **Round to buildable values + carry an uncertainty flag** per coordinate ("exact-constrained"
   vs "measured plus/minus x") so only the genuinely uncertain ones need review.

**Pipeline:** fix constrained coordinates (alignment/symmetry) exactly, then sub-pixel-measure the
remaining free coordinate, snap to module/standard, enforce global constraints (symmetry, equal
spacing) by a small fit, take size from the library part/standard, and verify on the calibrated
overlay.

Example: 4 terrace columns become "outer face flush to terrace edge 13.50 (x exact) + symmetric
about y=5.0 + standard column size", not four independently pixel-read squares.
