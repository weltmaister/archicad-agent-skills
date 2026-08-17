# Object triage and opening-handing notes

Use this note in measured-plan repair/rebuild cases when the live Archicad model contains many `Object` libparts and it is unclear which ones correspond to real source objects.

## 1) Triage source objects vs annotation libparts

Do not treat `Object` count as proof that source objects are modeled.

Classify candidates into:

### A. True modeled source objects / elements
Typical examples from a residential floor plan:
- stair
- terrace columns / posts
- WC
- washbasin / vanity
- shower
- washing machine
- kitchen counter with sink
- kitchen island with cooktop

### B. Annotation / stamp / marker libparts
Typical contaminants:
- room stamps
- door stamps
- window stamps
- section markers
- other label / marker / 2D symbol libparts

## 2) Evidence order for object identification

1. Source-plan visual reading
2. Published plan visual verification after modeling
3. Live Archicad readback / libpart name inspection
4. Raw `Object` inventory only as a weak hint

If automation readback is noisy, prefer source + publish evidence over `Object` inventory counts.

## 3) Opening handing / inward-vs-outward verification checklist

When door or window geometry is still wrong after host/offset corrections, verify the symbol semantics explicitly.

Check all of the following:
- correct host wall
- correct opening width / height
- correct offset / center position along host
- correct side of host wall
- correct swing / handing symbol in plan
- correct inward vs outward reading according to the drawing convention used in the source

Important: a mirrored opening can preserve the same width and offset while still being wrong.

## 4) Dimension verification beyond numeric equality

Do not stop at matching the published numeric sequence.

Also verify:
- chain count
- chain grouping / hierarchy
- witness / reference points
- which openings / wall faces each chain is dimensioning
- whether opening positions implied by the dimensions agree with the geometry

A plan can reproduce the same numbers while still using the wrong reference points or wrong opening topology.
