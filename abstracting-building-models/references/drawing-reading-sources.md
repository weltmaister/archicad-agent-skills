# Source and domain notes: reading architectural drawings

These notes condense the sources from which the skill rules were derived. They are not a full-text mirror of the sources.

## Drawing types and shared reading logic

- Floor plans, sections, and elevations only form an understandable building model together.
- Floor plan: a horizontal section through the building; popular introductory sources typically cite a cut height of about 1.20 m above floor level. What is shown is the cut material plus whatever lies below/above the cut plane according to the drawing convention.
- Section: a vertical cutting plane through the building. Decisive are the cut-line location, view direction, heights, storey references, roof/slab/foundation build-ups, and vertical openings.
- Elevation: exterior projection/facade; useful for opening heights, roof shape, terrain, facade material, eaves and ridge lines.
- Detail: local view at a larger scale; overrides/explains local construction details of the main plan.

## Standards-based conventions (German construction-drawing practice)

Source: a public German-language technical-drawing teaching document,
`https://www.bauberufe.eu/images/doks/zeichnen_414156.pdf`

- Construction drawings serve communication between client, architects, specialist engineers, authorities, and builders.
- DIN 1356 is cited as the central reference for construction drawings; DIN ISO 128-23/-50 for line types and cut surfaces; DIN 406 for dimensioning. (DIN standards themselves are licensed documents; cite the standard numbers rather than reproducing their text.)
- Important drawing types: design drawings, permit/submission drawings, execution/working drawings, foundation, drainage, installation, position, formwork, reinforcement, and precast drawings.

### Line types

- broad solid line: boundaries of cut surfaces / cut building elements.
- narrow solid line: visible edges and outlines.
- fine solid line: dimension lines, extension (witness) lines, leader lines, hatching.
- narrow dashed line: hidden edges/outlines.
- broad dash-dot line: location of the cutting plane.
- fine dash-dot line: axes.
- dotted line: building elements in front of or above the cutting plane.

### Section lines and section marks

- The section line is marked in the floor plan with a broad dash-dot line.
- View direction is indicated by black right-angled triangles/arrows.
- Section labels use matching capital letters, e.g. A-A or B-B.
- Cut surfaces are outlined with broad solid lines and may be hatched, filled, or marked by color/material.

### Dimensioning and scale

- An execution drawing should provide the necessary dimensions without additional arithmetic.
- Scale 1:50 means a real length is drawn 50 times smaller.
- The main scale is stated in the title block; deviating scales are assigned to the individual view they apply to.
- Dimension chains, witness lines, and dimension figures matter more for model parameters than pixel measurements.
- Typical model parameters read from dimension chains: overall dimensions, room dimensions, wall thicknesses, opening dimensions, axis dimensions, pier/wall-return dimensions.

### Hatching, material, colors

- Cut surfaces must be visually distinguished from surfaces seen in view.
- Hatching/fill can indicate material or simply the cut surface; adjacent elements may alternate hatch direction/spacing.
- Permit drawings may use colors for existing/new/demolished states or material states; always check the legend before modelling a renovation.

## Web introductions (German-language public sources)

- sanier.de — compact overview of site plan, floor plan, section, elevations, detail drawings, scale and dimensioning.
  `https://www.sanier.de/bauen/bauplaene-verstehen-grundrisse-schnitte-und-ansichten`
- grundriss-butler.de — explains dimension chains, wall lines, doors and windows for lay readers.
  `https://www.grundriss-butler.de/grundriss-richtig-lesen`
- Houzz — clarifies the terminology of floor plan, elevation, and section.
  `https://www.houzz.de/magazin/grundriss-ansicht-schnitt-eine-architektenzeichnung-richtig-lesen-stsetivw-vs~54839326`

## Library / database search anchors

- German National Library (DNB) catalogue: search for construction-drawing training manuals and drawing-convention textbooks.
- English-language references: Rendow Yee "Architectural Drawing", David Dernie "Architectural Drawing", Francis D. K. Ching "Building Construction Illustrated", Oliver Heckmann "Floor Plan Manual Housing", Ackerman/Jung "Conventions of Architectural Drawing".
- Building-surveying and renovation literature (reading plans, sections, and elevations together; details at larger scale) provides the same reading logic for existing-building work.

## Transfer into a parametric building model

- The modeller must first understand the drawing convention: cut surface, view direction, line type, scale, and legend determine what a line means.
- Parameters should be modelled as objects plus constraints: levels, axes, walls, openings, rooms, stairs, slabs, roof, terrain, material states.
- Every number needs a provenance: explicit dimension figure, derived dimension, scaled measurement, or assumption.
- Conflicts are part of the model: diverging dimension chains, detail vs main plan, contradictory opening positions, unreadable scan regions.
