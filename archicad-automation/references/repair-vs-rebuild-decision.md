# Repair vs. rebuild decision

Use this note when an Archicad reconstruction has drifted into repeated local fixes and you must decide
whether to keep patching or rebuild cleanly.

## Decision ladder

### 1. Keep incremental repair
Choose this only when all of the following are true:

- residual defects are local, not systemic;
- the affected element classes have reliable read + write coverage on the connected build;
- the current abstraction still matches the source interpretation;
- verification can be done immediately by export + calibrated overlay or strong read-backs.

Typical examples:
- one exterior wall axis is offset;
- one known door/window has the correct host wall and only needs a new `centerOffset` / width / height;
- a single dimension chain is missing but witness points are already identified.

### 2. Delete + recreate a bounded element group
Prefer this when the existing live state is worse than the source-derived evidence for a small subset.

Typical triggers:
- a modify command exists, but the current element state is unreliable or opaque;
- center offsets are easier to derive from the intermediate model than to recover from the live element;
- one wall group around a local hotspot has been patched repeatedly and is now harder to reason about
  than a clean re-create.

Scope examples:
- all openings on one facade;
- one wet-room core;
- one terrace / annex edge;
- one staircase-adjacent wall cluster.

### 3. Partial or full rebuild
Prefer a rebuild when one or more of these are true:

- local fixes are accumulating faster than confidence;
- the active abstraction is known to be too coarse (for example a 12-wall simplification hiding stepped
  source geometry);
- the remaining hotspot depends on unsupported or weakly inspectable content;
- verification keeps showing the same structural hotspot after multiple local edits;
- the source-derived intermediate model is already cleaner than the current live model.

## Pre-delete / pre-rebuild checklist

Before any larger destructive step, capture all of this in the working notes:

1. active Archicad instance / project / port
2. counts by type and GUID inventory by type
3. latest publish / overlay summary and image paths
4. current hypothesis for what is wrong
5. structured target plan: exterior contour · wall axes · openings · rooms/zones · stairs/objects ·
   terrace/outdoor areas
6. exact delete scope
7. verification plan after each batch

## Verification rule

Do not accept "file exists" or "call succeeded" as proof.

Use one of:
- publish + calibrated overlay,
- a fresh case-specific export inspected for real plan content,
- read-only evidence that directly covers the changed geometry.

## Runtime caveat: opaque `Object` content

In a live measured-plan case, generic `Object` content around the stair / zone / built-in area was not
safely inspectable: detail reads failed in the validation layer, 2D bounding boxes returned
`7203 Element not supported` for tested `Object` GUIDs, and some `Object` hits were zone-stamp / libpart
content rather than the expected stair proxy.

Implication: if the remaining hotspot depends on `Object` interpretation, do not bluff through it with
another tiny wall tweak. Either obtain a stronger export/overlay or rebuild from the intermediate model
with explicit uncertainty notes.
