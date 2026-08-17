# Opening witness-point derivation from `GetDoorsDetails` / `GetWindowsDetails`

Use this note when the Archicad automation layer exposes rich opening detail reads but still does not expose explicit named dimension witness points for floor-plan dimensioning.

## Goal

Derive concrete 2D witness-point coordinates for doors/windows from raw opening data plus the owner wall geometry, so helper-carrier-free dimension experiments can be driven from real opening edges where possible.

## Required inputs

From `elements_get_doors_details` / `elements_get_windows_details`:

- `startPoint` (opening-local anchor; according to the API this is measured from the beginning corner of the wall and rotated into the wall-reference-edge direction, so do **not** assume it is global on straight walls)
- `dirVector` (opening direction along wall; primarily relevant when `startPoint` semantics matter, especially on polygonal walls)
- `width`
- `fixPoint` = `BegFix` | `Center` | `EndFix`
- `reflected`, `oSide`
- `revealDepthFromSide`
- `jambDepth`, `jambDepth2`
- `sillHeight`, `height`

From owner wall details (resolve via `ownerId` → wall detail read):

- `begCoordinate`, `endCoordinate`
- `thickness`
- `offset`

## Coordinate basis

```text
wallDir = normalize(endC - begC)
wallNormal = (-wallDir.y, wallDir.x)
```

`wallNormal` points to the left when walking from wall begin to wall end.

## Step 1 — Opening edge points on wall reference line

Depending on `fixPoint`, a local opening anchor can be interpreted as:

- `BegFix`: `begEdge = anchor`, `endEdge = anchor + width * wallDir`
- `Center`: `begEdge = anchor - width/2 * wallDir`, `endEdge = anchor + width/2 * wallDir`
- `EndFix`: `begEdge = anchor - width * wallDir`, `endEdge = anchor`

For **straight walls**, derive the global `anchor` from owner-wall geometry plus `centerOffset` (or equivalent object location) instead of blindly using `startPoint`. Treat `startPoint` as wall-local by default. The formulas above then give the opening limits on the wall reference line.

## Step 2 — Wall-face offsets / jamb points

If `oSide == false` (opening on reference side):

```text
outsideFace = wallNormal * offset
insideFace  = wallNormal * (offset - thickness)
```

If `oSide == true` (opening on opposite side):

```text
outsideFace = -wallNormal * (thickness - offset)
insideFace  = -wallNormal * offset
```

Then:

```text
begOutside = begEdge + outsideFace
begInside  = begEdge + insideFace
endOutside = endEdge + outsideFace
endInside  = endEdge + insideFace
```

Optional jamb-depth correction along wall direction:

```text
begOutside_corrected = begEdge + outsideFace + jambDepth * wallDir
endOutside_corrected = endEdge + outsideFace - jambDepth2 * wallDir
```

## Semantic witness-point set

Recommended exported witness-point types:

- `opening_beg_ref`
- `opening_end_ref`
- `opening_beg_outside`
- `opening_end_outside`
- `opening_beg_inside`
- `opening_end_inside`
- `opening_center_ref`
- `sill_height`
- `header_height`

## Sorting for facade chains

Sort openings along a wall by:

```text
projectedPos = dot(startPoint - wallBeg, wallDir)
```

Use ascending order for measured-plan-style facade chains.

## Exterior-opening dimension-chain rule

When dimensioning openings in exterior walls, create a **separate opening dimension chain** from one exterior building edge to the other. The chain must measure the opening **edges / width**, not the opening midpoint. In a measured-plan workflow this means:

- use source facade chains to derive opening spans such as `x=1.50..2.50`, not only a `centerOffset=2.00`;
- include facade endpoints / outside building edges as the first and last witness points;
- for Archicad/Tapir associative dimensions, do not rely on a plain window witness (`line=true`) because it can collapse to zero-valued witness points;
- probe and use opening edge witnesses explicitly (observed working form in one live case: `line=false`, `special=1`, `inIndex=1` and `inIndex=3` for window edge points);
- verify with `elements_get_dimension_data`; if the chain reads back zeros, delete it immediately and retry with explicit edge witnesses or clearly documented technical carriers.

Convention to keep: exterior-wall openings get a separate chain ending at building outside edges, with opening widths dimensioned from edge to edge, not midpoint/axis values.

## Important caveat

This derivation provides *computed candidate witness points*. It does not prove that Archicad's internal associative-dimension engine uses exactly the same anchors for every libpart/opening type. Therefore, still verify any final dimension-chain migration by publish output and dimension readback.
