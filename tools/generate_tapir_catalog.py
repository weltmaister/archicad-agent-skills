#!/usr/bin/env python3
"""Generate references/tapir-full-command-catalog.md from Tapir's own command reference.

Tapir's weekly release regenerates docs/archicad-addon/command_definitions.js and
common_schema_definitions.js from the registered commands (tools/generate_addon_docs.py), so
they list every command of a release with its group, the version it was introduced in, its
description and its input/output JSON schema. This script turns them into the compact
catalog the skill reads, and carries over the hand-written notes ("# ..." lines after the
description) of the previous catalog.

Usage:
    python tools/generate_tapir_catalog.py <tapir checkout> <release tag> [--out <catalog.md>]

The checkout needs the tag (git fetch --tags); nothing is checked out, the files are read with
'git show <tag>:<path>'.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parent / "archicad-automation" / "references" / "tapir-full-command-catalog.md"
DOCS = "docs/archicad-addon"

HEADER = """# Tapir Archicad Commands v{version}

Generated from Tapir {version}'s command reference ({count} commands) by
`tools/generate_tapir_catalog.py`. Signatures are the add-on's own schemas; the `# ...` lines
under a description are verified notes and warnings carried over from live use. Field names,
required fields and version gates that matter in practice are in
`tapir-verified-command-schemas.md` - read that first for anything it covers.

## Protocol
Every command goes through the `API.ExecuteAddOnCommand` wrapper. The bare `{{"command": "TapirCommand.X"}}` form is rejected by the native Archicad JSON server with error 2002 (verified live).
```
POST http://localhost:{{port}}
Content-Type: application/json

{{
  "command": "API.ExecuteAddOnCommand",
  "parameters": {{
    "addOnCommandId": {{"commandNamespace": "TapirCommand", "commandName": "{{CommandName}}"}},
    "addOnCommandParameters": {{ ... }}
  }}
}}
```
The `{{CommandName}}` and the field schemas below go into `commandName` / `addOnCommandParameters`. Response: `{{"succeeded": true, "result": {{"addOnCommandResponse": {{...}}}}}}`.

Port discovery: scan 19723-19743 and ask each answering port `API.GetProductInfo` for its Archicad version - ports follow the start order, so never infer the version from the port.

## Notation
- `?field` = optional
- `field[]` = array of items (an array of objects lists the item's fields)
- `→` = response
- `"A"|"B"` = enum values
- `A | B` = one of several shapes
- `(since x.y.z)` = the Tapir version that introduced the command; `[AC27+]` and similar = Archicad versions named in the description
- Types: float, int, bool, string; other names are the shared types below

## Cross-cutting notes (verified live)
- `floorIndex` is available in all create commands, with split semantics: `CreateWalls` `z` is RELATIVE to the story, all other create commands take `z` ABSOLUTE (`floorIndex` only pins the home story).
- GDL array parameters are editable (since 1.5.4, #455); since 1.7.2 they are written through the API (#558).
- Reads of attribute details (`GetLayers`, `GetBuildingMaterials`, ...) need `attributeIds`; list them first with `GetAttributesByType`.
- Layout and navigator work starts from `GetNavigatorItemTree` (item ids); `SetLayoutSettings` sizes apply to master layouts only - verify by reading back.
"""

SCALARS = {"number": "float", "integer": "int", "boolean": "bool", "string": "string", "null": "null"}


def git_show(checkout: Path, tag: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(checkout), "show", f"{tag}:{path}"], capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout


def js_value(text: str, name: str):
    """The JSON value assigned to 'var <name> = ...;' in a generated .js file."""
    start = text.index("=", text.index(f"var {name}")) + 1
    return json.loads(text[start:].strip().rstrip(";"))


def ref_name(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def render(schema, depth: int = 0) -> str:
    """A schema as a compact type expression."""
    if not isinstance(schema, dict) or not schema:
        return "any"
    if "$ref" in schema:
        return ref_name(schema["$ref"])
    if "enum" in schema:
        return "|".join(json.dumps(v, ensure_ascii=False) for v in schema["enum"])
    if "const" in schema:
        return json.dumps(schema["const"], ensure_ascii=False)
    for key in ("oneOf", "anyOf"):
        if key in schema:
            return " | ".join(render(s, depth) for s in schema[key])
    if "allOf" in schema:
        return " & ".join(render(s, depth) for s in schema["allOf"])
    kind = schema.get("type")
    if isinstance(kind, list):
        return "|".join(SCALARS.get(k, k) for k in kind)
    if kind == "array":
        return f"[{render(schema.get('items', {}), depth + 1)}]"
    if kind == "object" or "properties" in schema:
        props = fields(schema, depth + 1)
        return "{" + props + "}" if props else "object"
    return SCALARS.get(kind, kind or "any")


def fields(schema: dict, depth: int = 0) -> str:
    required = set(schema.get("required", []))
    parts = []
    for name, sub in (schema.get("properties") or {}).items():
        opt = "" if name in required else "?"
        parts.append(f"{opt}{name}: {render(sub, depth)}")
    return ", ".join(parts)


def signature(schema) -> list[str]:
    """Input lines: a top-level array of objects is listed as 'name[]: <item fields>'."""
    if not schema:
        return []
    if "properties" not in schema:
        return [render(schema)]
    required = set(schema.get("required", []))
    lines, rest = [], []
    for name, sub in schema["properties"].items():
        opt = "" if name in required else "?"
        items = sub.get("items") if isinstance(sub, dict) and sub.get("type") == "array" else None
        if isinstance(items, dict) and "properties" in items and len(schema["properties"]) <= 3:
            lines.append(f"{opt}{name}[]: {fields(items)}")
        else:
            rest.append(f"{opt}{name}: {render(sub)}")
    return ([", ".join(rest)] if rest else []) + lines


def old_notes(path: Path) -> dict[str, list[str]]:
    """'# ...' lines after the description line of each command in the previous catalog."""
    notes: dict[str, list[str]] = {}
    if not path.exists():
        return notes
    current, seen_description = None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"### (\w+)\s*$", line)
        if match:
            current, seen_description = match.group(1), False
            continue
        if line.startswith("## "):
            current = None
            continue
        if current and line.startswith("# "):
            if seen_description:
                notes.setdefault(current, []).append(line)
            seen_description = True
    return notes


def archicad_versions(description: str) -> str:
    found = re.findall(r"Archicad (\d{2})(\+| or later| and later|)", description)
    return f" [AC{found[0][0]}+]" if found and found[0][1] else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("tag")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    groups = js_value(git_show(args.checkout, args.tag, f"{DOCS}/command_definitions.js"), "gCommands")
    shared = js_value(git_show(args.checkout, args.tag, f"{DOCS}/common_schema_definitions.js"), "gSchemaDefinitions")
    notes = old_notes(args.out)
    count = sum(len(g["commands"]) for g in groups)

    out = [HEADER.format(version=args.tag, count=count), "## Shared Types", ""]
    for name, schema in sorted(shared.items()):
        out.append(f"- **{name}**: {render(schema)}")
    out.append("")
    carried = 0
    for group in groups:
        out += [f"## {group['name']}", ""]
        for command in group["commands"]:
            description = " ".join(command.get("description", "").split())
            out.append(f"### {command['name']}")
            out.append(f"# {description} (since {command.get('version', '?')}){archicad_versions(description)}")
            kept = notes.get(command["name"], [])
            carried += len(kept)
            out += kept
            out += [f"  {line}" for line in signature(command.get("inputScheme"))]
            result = command.get("outputScheme")
            if result:
                out.append(f"  → {fields(result) if 'properties' in result else render(result)}")
            out.append("")
    args.out.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8", newline="\n")
    lost = sorted(set(notes) - {c["name"] for g in groups for c in g["commands"]})
    print(f"{count} commands, {carried} notes carried over" + (f"; notes of unknown commands: {lost}" if lost else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
