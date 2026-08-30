# Vector PDF: OCG layers, fills, and openings

For a vector CAD export (not a scan), the PDF carries the drawing's own layer structure and
exact geometry. Extracting from a raster render throws both away. All facts below are
live-verified (2026-08-20, PyMuPDF 1.2x, German as-built basement plan at 1:100). Order of
operations:

## 0. First: list the layers against the path types

Before ANY geometry extraction, list the OCG layers and cross-tabulate them with
the path types they contain (`f` fills / `s` strokes) plus the stroke widths.
The layer structure carries half the building semantics (existing walls as
poché, drywall as strokes only, stairs, hidden lines, fire-protection marks,
new/demolition, shafts, dimensions per scale) — and which extraction method is
even applicable follows from the path types: fill-based extraction only works
on layers that HAVE fills. In live work, every extraction dead-end traced back
to skipping this step.

## 1. Switch layers with the UI-config API, not `set_layer`

`doc.set_layer(-1, on=[...], off=[...])` takes OCG **xrefs** and, on PyMuPDF 1.2x, silently
does nothing for this purpose — every layer stays visible. The working path is the UI config,
indexed exactly like `doc.layer_ui_configs()`:

```python
n = len(doc.layer_ui_configs())
for i in range(n): doc.set_layer_ui_config(i, 2)   # 2 = OFF
for i in wanted:   doc.set_layer_ui_config(i, 0)   # 0 = ON
```

**Consequence of getting this wrong:** the first complete extraction in the live case ran on
a render that still contained text, dimension lines and hatching — 4 million foreign pixels,
and every derived wall section was noise. Always sanity-check the ink count of a
single-layer render against the all-layers render before trusting it.

## 2. Subtract the "all layers off" baseline

Untagged content (sheet frame, title block) is drawn regardless of layer state. Render with
all layers off once and subtract that mask; otherwise every layer's bounding box equals the
sheet.

```python
import pymupdf, numpy as np
d = pymupdf.open(pdf); n = len(d.layer_ui_configs())
def mask(on):
    for i in range(n): d.set_layer_ui_config(i, 2)
    for i in on:       d.set_layer_ui_config(i, 0)
    p = d[0].get_pixmap(matrix=pymupdf.Matrix(Z, Z))
    a = np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width, p.n)
    return a[:, :, :3].min(axis=2) < 100
base  = mask([])                   # untagged content
walls = mask(wall_layers) & ~base  # only the wanted layers
```

## 3. Read fill paths, never the raster, for thicknesses

Wall poché is a filled path; its stroked outline adds **half the line width on each side**.
In the live case the dominant stroke was 0.51 pt → 0.51 × 0.0352778 = **18.0 mm at 1:100**,
which turned 0.125 into 0.145 and 0.535 into 0.555 across the whole model. Take the geometry
from `page.get_drawings()` with `type == 'f'` and the fill colour you want, convert with the
calibrated transform, and you get exact polygons — quadrilaterals, triangle pairs that
recombine into rectangles, and rectilinear L/T shapes.

```python
fills = [p for p in d[0].get_drawings() if p['type'] == 'f']
black = [p for p in fills if p['fill'] == (0.0, 0.0, 0.0)]   # wall bodies
white = [p for p in fills if p['fill'] == (1.0, 1.0, 1.0)]   # openings
```

## 4. White fills inside the wall layer ARE the openings

A CAD export punches openings out of the poché with **white** fill paths on the same wall
layer. This is exact opening geometry for free:

- union the white paths per host wall; a part that spans the wall's full thickness is an
  opening;
- **window vs door:** a window carries inner sash/glazing strips (thin sub-rectangles,
  ~0.07 m, fully inside the opening bbox). ≥ 3 sub-strips ⇒ window, plain rectangle ⇒ door.
  In the live case this classified 13 windows and 6 doors with zero guessing, including a
  0.41 m narrow window that any width heuristic would have mis-typed.

## 5. Mine the layer names — they are the element classification

The OCG list names the classes the draughtsman used (live case: existing walls, drywall
walls, new construction, demolition, stairs, shafts, rooms, lines, hidden lines, elevation
lines, door, window, dimensions). Three lessons:

- **A separate wall layer is a scope question, not a fact.** A drywall-partition layer was
  drawn in the "existing" colour but stroked only, with no poché. Whether it belongs in the
  existing-construction scope is the user's call; ask, do not assume. (Live: it held exactly
  the 42 partitions of the sanitary rooms the model needed.)
- **Elevation-line layers can carry slope information.** Two long triangles there were a
  ramp: a base line at the low end and two converging edges, **apex pointing uphill**
  (German slope-triangle convention). That yielded the complete ramp geometry from a layer
  that reads like annotation.
- **Shaft / hidden-line layers explain "missing" dimension-chain anchors.** Before reporting
  a source chain as unbuildable, render each candidate layer alone and test which one has
  geometry at the unanchored coordinate. In the live case all 21 unanchored chain nodes sat
  on hidden-line / new-construction / room layers — none on an existing wall — which turned
  "7 chains still open" into "7 chains provably out of scope".

## 6. Prove absence, don't assume it

Claiming "the plan has no door arcs" needs a measurement. Count Bézier items on the sheet
(live case: 36 in total, all in text/title-block/north-arrow) or render the suspect layer
alone and count ink. A coincidental 4-point circle fit is not an arc.
