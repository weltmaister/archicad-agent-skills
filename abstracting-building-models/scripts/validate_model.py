#!/usr/bin/env python3
"""Validate a parametric building model JSON produced from architectural drawings.

Usage:
  python scripts/validate_model.py model.json
  python scripts/validate_model.py model.json --schema templates/parametric-building-model.schema.json

Uses jsonschema when installed; otherwise performs lightweight structural checks.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP = {"metadata", "evidence", "assumptions", "missing_information"}
COLLECTION_KEYS = ["levels", "grids", "spaces", "walls", "openings", "slabs", "stairs", "roofs", "constraints"]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_ids(model: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for key in COLLECTION_KEYS + ["evidence", "assumptions", "conflicts"]:
        for item in model.get(key, []) or []:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.add(item["id"])
    for sheet in model.get("metadata", {}).get("source_sheets", []) or []:
        if isinstance(sheet, dict) and isinstance(sheet.get("id"), str):
            ids.add(sheet["id"])
    return ids


def lightweight_validate(model: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(model, dict):
        return ["model must be a JSON object"]

    missing = sorted(REQUIRED_TOP - set(model))
    if missing:
        errors.append(f"missing top-level keys: {', '.join(missing)}")

    metadata = model.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        for key in ["project_name", "units", "source_sheets"]:
            if key not in metadata:
                errors.append(f"metadata missing {key!r}")

    evidence = model.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    else:
        evidence_ids = {e.get("id") for e in evidence if isinstance(e, dict)}
        for e in evidence:
            if not isinstance(e, dict):
                errors.append("evidence items must be objects")
                continue
            for key in ["id", "sheet_id", "kind", "confidence"]:
                if key not in e:
                    errors.append(f"evidence item missing {key!r}: {e}")

        all_ids = collect_ids(model)
        for key in COLLECTION_KEYS:
            for item in model.get(key, []) or []:
                if not isinstance(item, dict):
                    errors.append(f"{key} item must be object")
                    continue
                for ref in item.get("evidence", []) or []:
                    if isinstance(ref, dict) and ref.get("evidence_id") not in evidence_ids:
                        errors.append(f"{key}.{item.get('id')} references missing evidence {ref.get('evidence_id')!r}")
                for rel_key in ["host_wall_id", "level_id", "from_level_id", "to_level_id"]:
                    if rel_key in item and item.get(rel_key) not in all_ids:
                        errors.append(f"{key}.{item.get('id')} references missing {rel_key}={item.get(rel_key)!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--schema", type=Path, default=None)
    args = parser.parse_args()

    model = load_json(args.model)
    errors: list[str] = []

    schema_path = args.schema
    if schema_path is None:
        here = Path(__file__).resolve().parent
        candidate = here.parent / "templates" / "parametric-building-model.schema.json"
        schema_path = candidate if candidate.exists() else None

    if schema_path and schema_path.exists():
        try:
            import jsonschema  # type: ignore
            jsonschema.Draft202012Validator.check_schema(load_json(schema_path))
            validator = jsonschema.Draft202012Validator(load_json(schema_path))
            errors.extend(f"schema: {e.message} at /{'/'.join(map(str, e.path))}" for e in validator.iter_errors(model))
        except ModuleNotFoundError:
            errors.extend(lightweight_validate(model))
        except Exception as exc:  # keep validation scripts diagnostic, not opaque
            errors.append(f"schema validation setup failed: {exc}")
            errors.extend(lightweight_validate(model))
    else:
        errors.extend(lightweight_validate(model))

    if errors:
        print("INVALID")
        for err in errors:
            print(f"- {err}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
