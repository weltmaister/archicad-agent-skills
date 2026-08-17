# Rebuild plan – <case-name>

## Context
- Case path: `<path>`
- Active project / port: `<project> / <port>`
- Prepared by: `<agent/session>`
- Reason for rebuild: `<why incremental repair is no longer the best path>`

## Before-state evidence
- Latest overlay/export summary: `<path>`
- Latest difference images: `<paths>`
- Current counts by type: `<counts>`
- GUID inventory file: `<path>`

## Chosen rebuild scope
- [ ] openings only
- [ ] one wall group
- [ ] one local core / room block
- [ ] terrace / annex edge
- [ ] full ground-plan rebuild

## Target model plan
### 1. Exterior contour
- `<overall extents and key offsets>`

### 2. Wall axes
- `<wall-axis set, abstraction level, unresolved branches>`

### 3. Openings
- `<host walls, offsets, widths/heights, assumptions>`

### 4. Rooms / zones
- `<room polygons, names, areas if relevant>`

### 5. Stairs / objects
- `<what is known, what remains uncertain, how verified>`

### 6. Terrace / outdoor area
- `<slabs, columns, external strip, edge conditions>`

## Delete scope
- Element types: `<types>`
- GUID groups: `<path or inline list>`
- Legacy elements kept for reference: `<if any>`

## Execution batches
1. `<batch 1>`
2. `<batch 2>`
3. `<batch 3>`

## Verification after each batch
- Read-only checks: `<which ones>`
- Export + calibrated overlay: `<script/path>`
- Acceptance threshold / expected improvement: `<metric or qualitative target>`

## Stop conditions
- `<what would make you pause instead of continuing>`

## Result
- Status: `<not started / in progress / complete / aborted>`
- Notes: `<short outcome>`
