# Dimension-first measured-plan control grids

Use this reference when recreating or correcting an Archicad model from a measured plan whose dimension-chain structure must match the original, not merely show plausible dimensions.

## Lesson

For measured-plan reconstruction, build the dimension-chain skeleton early and use it as a control grid. Do not wait until the model looks visually plausible before dimensioning. The model must be corrected against the chains, not the other way around.

## Reliable workflow

1. Extract and group source dimension strings by role:
   - overall building extents;
   - facade / room subdivision chains;
   - openings, piers, and wall thickness chains;
   - secondary/section markers that should not become linear dimensions.
2. Delete stale/test dimensions before publishing a new verification state.
3. Create a small set of explicit witness carriers at source-derived coordinates when native element witnesses do not expose the required face/opening points.
4. Create associative dimensions from those carriers and publish the real layout item.
5. Verify with both:
   - PDF text extraction for ordered dimension strings; and
   - rendered PDF visual review for chain count, grouping, witness-line structure, and clutter.
6. Only after the original dimension skeleton is visible, move/rebuild walls, openings, zones, and objects until the model geometry agrees with the grid.

## Witness-carrier pattern

In one measured-plan case, direct wall/opening witnesses were insufficient for exact source-chain reconstruction because they measured current model reference geometry or collapsed to coarser chains. A robust fallback was to create very short, thin reference walls at the desired source coordinates and use them as associative-dimension witness carriers.

Working witness settings observed for those carriers:

```json
{
  "line": false,
  "special": 1,
  "inIndex": 1
}
```

This produced published chains matching the original values, including overall `13,50` / `10,00` (decimal-comma plan annotation), facade subdivisions, opening/pier dimensions, and wall-thickness dimensions.

## Important caveats

- This is a control-grid technique, not a claim that the model geometry is already correct. Report it as "dimension skeleton/control grid is correct" until walls/openings/zones have been rebuilt to match.
- Numeric equality in extracted PDF text is not enough. Also verify chain structure: count, grouping, witness lines, outer-vs-inner chains, and visual relation to the plan.
- If a dimension value like `0,60` is extracted as `60`, inspect the rendered PDF before treating it as wrong; PDF text extraction can lose leading `0,` on small metric annotations.
- Do not keep failed experimental dimensions or labels in the model. Delete noisy tests before the next publish.
- Avoid using leader labels as room-stamp substitutes. If room names need correction, prefer zone recreation/stamp placement or clean 2D text; leader labels can introduce visible arrows that make the plan less like the source.

## When to escalate

If the control grid is correct but the model still diverges, switch from dimension work to geometry rebuild:

- delete/recreate windows or doors when modify calls report success but published/bounding-box evidence does not change;
- rebuild broken local wall topology before trying to force final associative dimensions;
- recreate zones with proper room names and stamp positions instead of overloading one large zone.
