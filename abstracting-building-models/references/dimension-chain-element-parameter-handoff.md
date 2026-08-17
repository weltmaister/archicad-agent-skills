# Dimension-chain + element-recognition handoff for measured plans

Use this when a floor plan must become a reusable construction model, especially when future inputs may be distorted bitmap scans rather than clean vector PDFs.

## Core lesson

Do **not** treat PDF vector tracing or pixel vectorization as the primary reconstruction strategy. It can be useful as a diagnostic/reference layer for clean vector PDFs, but it is not generalizable to scanned or distorted plans.

The durable workflow is:

1. Detect and classify drawing elements:
   - exterior walls
   - interior walls
   - columns
   - windows
   - doors
   - objects/fixtures
   - stairs
   - terraces/exterior areas
2. Assign the relevant dimension chain(s) to each element or element group.
3. Build a parameter handoff model from those chains and classifications.
4. Pass that parameter model to the Archicad construction skill.
5. Use overlays/vector traces only as proof/diagnostic evidence, not as the source of truth.

## Required intermediate-model additions

For each element, store:

- `kind`: wall / opening / column / stair / object / slab / terrace / room
- `subtype`: exterior_wall, interior_wall, door, window, etc.
- `dimension_chains`: chain IDs that justify position/size
- `geometry_parameters`: reference line, thickness, span, center offset, bbox, polygon, etc.
- `source_evidence`: OCR/vector text, image crop, chain grouping, symbol recognition
- `confidence`: high / medium / low
- `uncertainties`: ambiguity that still needs recognition or user/source resolution

## Dimension-chain grouping

Group dimension strings by role before constructing geometry:

- overall building size
- facade subdivision
- openings and piers
- wall thicknesses
- interior room/core chains
- stair/object/fixture control dimensions when present

Then compute cumulative coordinates and closure error for each chain. A chain is not accepted as a construction control unless the closure error is within tolerance or the mismatch is explicitly explained.

## Handoff shape

A useful handoff JSON should include:

```json
{
  "global_frame": {"width_x": 13.5, "height_y": 10.0, "origin": "south-west outside corner"},
  "dimension_chains": [
    {"id": "north_detail", "orientation": "x", "values": [0.31, 3.25], "cumulative": [0, 0.31, 3.56], "closure_error": 0.0}
  ],
  "elements": {
    "exterior_walls": [],
    "interior_walls": [],
    "exterior_openings": [],
    "columns": [],
    "stairs": [],
    "objects": [],
    "rooms": []
  }
}
```

## Pitfalls

- A clean vector PDF can tempt the agent into copying visible lines. That produces a drawing, not a model.
- A traced line model fails on distorted scans and does not encode which line is an exterior wall, opening edge, stair tread, object, or dimension witness.
- Text copied as leader labels is not equivalent to text: leader arrows can destroy the drawing. If a true text tool is unavailable, keep text as a proof-layer gap rather than inserting noisy labels.
- Numeric closure is necessary but insufficient: element class and source chain assignment must also be correct.
