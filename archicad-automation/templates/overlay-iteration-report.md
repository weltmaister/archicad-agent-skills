# Overlay iteration report – <case-name>

## Iteration header
- Timestamp: `<YYYY-MM-DD HH:MM TZ>`
- Project / port: `<project> / <port>`
- Source image: `<path>`
- Published/export image: `<path>`
- Overlay script: `<path>`

## Registration basis
- Source box: `<x0,y0,x1,y1>`
- Published box: `<x0,y0,x1,y1>`
- Published fallback box: `<x0,y0,x1,y1 or n/a>`
- Common registered size: `<w x h>`

## Metrics
- Raw common: `<n>`
- Raw source_only: `<n>`
- Raw published_only: `<n>`
- Structural common: `<n>`
- Structural source_only: `<n>`
- Structural published_only: `<n>`

## Main hotspots
(adapt the hotspot list to the plan; examples below)
- Exterior contour: `<status>`
- Wet-room / utility core: `<status>`
- Stair / hallway zone: `<status>`
- Mid-plan wall junctions: `<status>`
- Terrace / plan edge: `<status>`

## Decision
- [ ] no mutation
- [ ] incremental repair
- [ ] delete + recreate local group
- [ ] partial rebuild
- [ ] full rebuild

Reason:
`<1–3 sentences grounded in the overlay + readback evidence>`

## Artefacts
- Summary JSON: `<path>`
- Difference map: `<path>`
- Difference overlay: `<path>`
- Registered source/publish: `<paths>`

## Reusable skill lesson
`<what this iteration taught the skill library>`
