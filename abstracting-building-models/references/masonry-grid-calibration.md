# Masonry-grid calibration for existing buildings

Use this before the 5 mm rounding step whenever the source is an existing building.
If the building sits in a masonry module, wall thicknesses AND length/axis dimensions
are snapped to the masonry nominal dimensions, not to a neutral 5 mm grid. This is the
strongest control available without an on-site survey, and it doubles as a
construction-phase analysis: walls outside the detected grid date later alterations.

## The grids

Dimensional order per **DIN 4172** (octametric, base module 12.5 cm = 1/8 m):

- projection/grid dimension = n × 12.5 cm
- component/external dimension = n × 12.5 − 1 cm
- opening dimension = n × 12.5 + 1 cm → 1.01 / 1.26 / 1.51 / 1.76 / 2.01 m

Brick formats and the wall-thickness series they produce (1 cm joint):

| Format | Brick size (cm) | Module | Thickness series ½ / 1 / 1½ / 2 / 2½ / 3 brick |
|---|---|---|---|
| Old imperial format ("altes Reichsformat", from 1872) | 25 × 12 × 6.5 | 13.0 | **12 / 25 / 38 / 51 / 64 / 77** |
| New RF, NF, DF | 24 × 11.5 × 6.3/7.1/5.2 | 12.5 | **11.5 / 24 / 36.5 / 49 / 61.5 / 74** |
| Monastery format ("Klosterformat") | 28–30 × 14–15 × 9–10 | non-uniform | determine individually |

**Plaster does NOT belong to the grid:** measured thickness = nominal + 1.5 cm per
plastered side (so test each measured value against nominal + 0 / 1.5 / 3.0 cm).

## Procedure

1. Test ALL measured wall thicknesses against both series (× the plaster variants
   0 / 1.5 / 3.0 cm).
2. The grid that hits the **most frequent and the load-bearing** walls with ≈ 0
   deviation is the building's grid. A hit on the thick exterior and spine walls
   weighs more than one on thin partitions.
3. Snap every wall of that grid to the nominal value — including those measured
   5 mm off.
4. Do NOT force outliers into the grid; classify them as **later insertions** with
   their own material logic — sand-lime block (17.5 / 24), reinforced concrete
   (25 / 30), gypsum-board studwork (10 / 12.5) — and document that reasoning.
   This is simultaneously a construction-phase analysis.
5. Test length and axis dimensions against the grid too — combined with the
   recurring-axis-dimension rule (SKILL.md step 7) this is the strongest check
   that exists without an on-site survey.

## Worked case (heritage building, built c. 1900, basement storey)

The building sits in the **old imperial format**, module 13 cm — deviation at the
main thicknesses 0.0 cm:

| measured | count | reading | nominal |
|---|---|---|---|
| 0.770 | 6 | 3 brick | 77 |
| 0.640 | 3 | 2½ brick | 64 |
| 0.510 | 2 | 2 brick | 51 |
| 0.380 | 3 | 1½ brick | 38 |
| 0.250 | 16 | 1 brick | 25 |
| 0.125 | 16 | ½ brick | 12 (or gypsum board 12.5) |
| 0.280 | 8 | 1 brick + plaster both sides | 25 + 3 |
| 0.410 | 4 | 1½ brick + plaster both sides | 38 + 3 |
| 0.540 | 4 | 2 brick + plaster both sides | 51 + 3 |

Later insertions, correctly OUTSIDE the imperial-format grid: 0.175 (sand-lime
block), 0.300 (reinforced concrete, underground garage), 0.100 / 0.075 (gypsum
board), 0.240 / 0.365 (NF masonry). 94 of 124 walls sat within ≤ 6 mm of the
detected system.

Model consequence: crooked measured values snap to the system — 0.409 → **0.41**,
0.541 → **0.54**, 0.308 → **0.30**, 0.299 → **0.30**, 0.239/0.245/0.254 → **0.25**,
0.119/0.127/0.131 → **0.125**.
