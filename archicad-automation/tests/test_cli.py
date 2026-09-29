"""CLI and transport tests for scripts/build_from_model.py, plus the fixture house under the rules.

Run from the skill folder:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import build_from_model as bfm  # noqa: E402
from fake_archicad import FakeArchicad  # noqa: E402
from helpers import FIXTURE, OFFICE, fixture_model  # noqa: E402

MATERIAL_MAP = HERE / "fixtures" / "material_map.json"


def material_map():
    return json.loads(MATERIAL_MAP.read_text(encoding="utf-8"))


class FixtureHouseTest(unittest.TestCase):
    def test_fixture_house_plans_cleanly_under_the_rules(self):
        # 2.80 m window axes: four on the long facades, none on the interior wall at x = 6.00
        plan = bfm.build_plan(fixture_model(), office=OFFICE, material_map=material_map())
        keys = ("walls", "slabs", "windows", "doors", "zones", "buildups", "ceilings", "openings", "columns")
        counts = {k: len(plan[k]) for k in keys}
        self.assertEqual(counts, {"walls": 20, "slabs": 4, "windows": 27, "doors": 2, "zones": 4, "buildups": 4, "ceilings": 1,
                                  "openings": 4, "columns": 2})
        self.assertEqual(plan["skipped"], [])
        self.assertEqual(plan["errors"], [])
        self.assertEqual(plan["warnings"], [])
        self.assertEqual({s["role"] for s in plan["slabs"]}, {"ground_slab", "floor_slab", "roof_slab", "roof_insulation"})
        self.assertEqual({w["role"] for w in plan["walls"]}, {"exterior_wall", "interior_wall", "parapet", "railing", "strip_footing",
                                                              "installation_wall"})

    def test_fixture_house_builds_and_passes_every_check(self):
        model = fixture_model()
        report = bfm.run(model, FakeArchicad(spaces=model["spaces"]), material_map=material_map())
        self.assertTrue(report["ok"], report["errors"][:5])
        self.assertEqual(report["created"], {"Wall": 20, "Slab": 9, "Window": 27, "Door": 2, "Zone": 4, "Opening": 4, "Column": 2,
                                             "Morph": 3})


class CliTest(unittest.TestCase):
    def test_dry_run_writes_the_plan_and_prints_a_short_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = bfm.main([str(FIXTURE), "--dry-run", "--material-map", str(MATERIAL_MAP), "--plan-out", str(plan_path)])
            self.assertEqual(code, 0)
            text = out.getvalue()
            self.assertIn("DRY RUN", text)
            self.assertIn("walls 20", text)
            self.assertIn("office catalog: NO", text)
            self.assertLess(len(text), 2000)  # the whole point: keep the agent context small
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(len(plan["windows"]), 27)

    def test_dry_run_with_plan_errors_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = fixture_model()
            model["metadata"]["units"] = "mm"
            path = Path(tmp) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = bfm.main([str(path), "--dry-run"])
            self.assertEqual(code, 1)
            self.assertIn("ERRORS", out.getvalue())

    def test_json_inputs_with_a_byte_order_mark_are_accepted(self):
        # PowerShell (Set-Content -Encoding UTF8) and Notepad write a BOM in front of the JSON
        with tempfile.TemporaryDirectory() as tmp:
            mm = Path(tmp) / "map.json"
            mm.write_text(MATERIAL_MAP.read_text(encoding="utf-8"), encoding="utf-8-sig")
            model = Path(tmp) / "model.json"
            model.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8-sig")
            plan_path = Path(tmp) / "plan.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = bfm.main([str(model), "--dry-run", "--material-map", str(mm), "--plan-out", str(plan_path)])
            self.assertEqual(code, 0)
            self.assertIn("KS + WDVS 42 cm", json.loads(plan_path.read_text(encoding="utf-8"))["materials"])

    def test_live_run_refuses_without_confirm(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = bfm.main([str(FIXTURE), "--port", "19723"])
        self.assertEqual(code, 2)
        self.assertIn("--confirm", out.getvalue())

    def test_check_needs_a_port_and_no_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            path.write_text(json.dumps({"plan": {}}), encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                bfm.main(["--check", str(path)])
            self.assertIn("--check needs --port", err.getvalue())

    def test_envelopes_for_tapir_and_official_commands(self):
        env = bfm.make_envelope("CreateWalls", {"wallsData": []})
        self.assertEqual(env["command"], "API.ExecuteAddOnCommand")
        self.assertEqual(env["parameters"]["addOnCommandId"], {"commandNamespace": "TapirCommand", "commandName": "CreateWalls"})
        self.assertEqual(env["parameters"]["addOnCommandParameters"], {"wallsData": []})
        official = bfm.make_envelope("API.SetPropertyValuesOfElements", {"elementPropertyValues": []})
        self.assertEqual(official, {"command": "API.SetPropertyValuesOfElements", "parameters": {"elementPropertyValues": []}})

    def test_read_only_sender_refuses_changes(self):
        fake = FakeArchicad()
        guarded = bfm.readonly(fake)
        self.assertEqual(guarded("GetAddOnVersion", {})["version"], "1.5.9")
        self.assertIn("layers", bfm.fetch_office(guarded))
        with self.assertRaises(bfm.BuildError):
            guarded("CreateWalls", {"wallsData": []})
        with self.assertRaises(bfm.BuildError):
            guarded("API.SetPropertyValuesOfElements", {"elementPropertyValues": []})
        self.assertEqual([c for c, _ in fake.calls if not c.startswith(("Get", "API.Get"))], [])


if __name__ == "__main__":
    unittest.main()
