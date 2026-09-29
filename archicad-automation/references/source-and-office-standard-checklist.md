# Source and office-standard checklist

Use this checklist before modelling, changing, documenting, or validating an Archicad file through Tapir.

## Source hierarchy

1. **Open Archicad file as office standard**
   - Tool favorites / element favorites
   - Pen sets / pen tables
   - Layers and layer combinations
   - Fills/hatches, line types, surfaces
   - Building materials, composites, profiles
   - Properties, classifications, IFC-related mappings where exposed
   - Zone categories, stamps
   - Model View Options, Graphic Overrides, Renovation Filters
   - Layout book, master layouts, title-block conventions

2. **The project's own knowledge base** (when one is connected)
   - Local standards, norm material, BIM/CAD references and office-specific documents.
   - Preserve query, document/path/id, snippet/page/section and confidence.
   - Treat norm hits as stronger than community practice, but do not invent text not present in the retrieved source.

3. **Official Graphisoft / Archicad sources**
   - Archicad Help, Graphisoft Learn, BIM content packages, official articles.
   - Use to confirm how Archicad concepts should be modelled and which settings/resources matter.

4. **Public standards metadata**
   - Standards-catalog metadata (e.g. DIN Media) can identify title/date/status/relevance.
   - Use metadata for orientation only unless full normative content is available through a legitimate source.

5. **Community / tutorial sources**
   - Graphisoft Community, forums, tutorials.
   - Use for workflow evidence, pitfalls, and common practice; do not treat as normative authority.

Norm texts (DIN and similar) are licensed — do not quote or recreate paid normative text unless it is
available through the user's own material with permission.

## Mandatory discovery questions

Before a mutating call, answer these in the working notes:

- Which Archicad instance and port are active?
- What is the project name/path/version?
- Which resources in the open file define the relevant office standard?
- Which source documents support or constrain the requested operation?
- Which parameters are still unknown after read-only discovery?
- Does any unknown affect geometry, classification, documentation, schedule/IFC semantics, standards compliance, or destructive overwrite behavior?
- What exact Tapir commands and schemas will be used?
- How will the result be verified?

## Ask the user when still missing

Ask concise clarification questions when these remain unresolved:

- real dimensions, heights, elevations, storey assignment or coordinate origin
- inside/outside/reference-line basis
- wall/slab/roof build-up when no suitable favorite/composite is clear
- intended element type when several Archicad tools could represent the request
- zone usage/category/name/number when not derivable from the brief
- whether to follow open-file convention, an external source, or an intentional deviation
- any delete, overwrite, favorite/attribute modification, bulk creation, layout change or Teamwork reserve/release action

## Do not ask when discoverable

Prefer read-only discovery over user interruption when values can be obtained from:

- current selection
- element details/properties/classifications
- attributes/favorites/resources in the open file
- the project knowledge base
- official Graphisoft docs for general tool behavior

## Reporting format

For small operations, report:

- source basis used
- planned/actual Tapir calls
- element GUIDs/counts
- verification result
- unresolved assumptions

For standards or conflicts, additionally report:

- source authority class
- source path/URL/id
- conflict between open-file office standard and external guidance
- recommended priority or question for the user
