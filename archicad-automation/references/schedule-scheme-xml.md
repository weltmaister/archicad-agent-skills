# Interactive schedule schemes (XML)

**No API.** The Archicad API (DevKits AC25–AC30) has no schedule scheme functions; Tapir issue #820
was closed for that reason. `GetSchedules` lists schedules and `CreateDrawings` places an existing
one on a layout by its navigator item ID — creating, changing, importing or exporting a scheme is
manual work in Archicad (Scheme Settings → Export/Import).

Workflow: the user exports an existing scheme → a script changes the XML → the user imports it.

## Rules for an importable file (observed AC28 GER, one session — re-check on a test project)

Archicad's import error ("damaged XML file, scheme settings could not be loaded") names no
position. Find the cause by halving the file.

- Write exactly like Archicad: LF line endings, no space before `/>`. Test: an exported file read
  and written by your script must be byte-identical before you change anything.
- Criterion on a property with a value list:
  `<UniValue><HasVariant/><ByValue/><Variant Type="StringVariant">…`
- Criterion on a free-text property: the `Variant` element must additionally be wrapped in
  `<Value>`. Without it the whole file fails to import.
- `Relation_Index`: 1 = is, 6 = is not.
- Property fields are addressed by name, group and type (`ACPropertyName`, `ACPropertyGroup`,
  `ACPropertyType`), not by the property GUID.
- Existing schemes with the same name were not the cause of import failures.
