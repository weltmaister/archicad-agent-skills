"""Executor tests for scripts/build_from_model.py against FakeArchicad (behaviour measured live on 29.09.2026).

Run from the skill folder:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import build_from_model as bfm  # noqa: E402
from fake_archicad import FakeArchicad  # noqa: E402
from helpers import MATERIAL_MAP, two_story_model, window  # noqa: E402


def house(**parts):
    parts.setdefault("openings", [window("W1", 2.0), window("W1", 6.0, kind="door", sill_height=None, height=2.135), window("IW", 4.0, kind="door")])
    return two_story_model(**parts)


def run(model=None, fake=None, **kw):
    model = model or house()
    fake = fake or FakeArchicad(spaces=model["spaces"])
    kw.setdefault("material_map", MATERIAL_MAP)
    return bfm.run(model, fake, **kw), fake


def created_keys(fake, command, array_key):
    return [item for call in fake.sent(command) for item in call[array_key]]


class GuardTest(unittest.TestCase):
    def test_old_tapir_is_refused_before_any_mutation(self):
        fake = FakeArchicad(version="1.5.8")
        with self.assertRaises(bfm.BuildError):
            run(fake=fake)
        self.assertEqual([c for c, _ in fake.calls if c.startswith(("Create", "Modify", "Set"))], [])

    def test_non_floor_plan_window_is_switched_before_counting(self):
        report, fake = run(fake=FakeArchicad(window="3DModel", spaces=house()["spaces"]))
        names = [c for c, _ in fake.calls]
        self.assertLess(names.index("ChangeWindow"), names.index("GetElementsByType"))
        self.assertTrue(any("3DModel" in w for w in report["warnings"]))

    def test_window_that_cannot_be_switched_stops_before_mutation(self):
        fake = FakeArchicad(window="Section", switchable=False)
        with self.assertRaises(bfm.BuildError):
            run(fake=fake)
        self.assertEqual([c for c, _ in fake.calls if c.startswith("Create")], [])

    def test_missing_story_stops_before_mutation(self):
        model = house()
        model["levels"].append({"id": "L_DG", "name": "DG", "elevation": 6.0})
        model["walls"].append({"id": "X", "level_id": "L_DG", "baseline": [[0, 0], [5, 0]], "representation": "centerline", "thickness": 0.2})
        fake = FakeArchicad(spaces=model["spaces"])
        with self.assertRaises(bfm.BuildError):
            run(model, fake)
        self.assertEqual([c for c, _ in fake.calls if c.startswith("Create")], [])

    def test_hidden_target_layer_stops_before_mutation(self):
        # a hidden layer freezes elements: modify and delete report success and change nothing (VS:54-58)
        fake = FakeArchicad(hidden_layers={"80 Raum"}, spaces=house()["spaces"])
        with self.assertRaises(bfm.BuildError):
            run(fake=fake)
        self.assertEqual([c for c, _ in fake.calls if c.startswith("Create")], [])


class WallExecutionTest(unittest.TestCase):
    def setUp(self):
        self.report, self.fake = run()

    def test_walls_carry_core_outside_composite_and_favorite(self):
        walls = created_keys(self.fake, "CreateWalls", "wallsData")
        w1 = walls[0]
        self.assertEqual(w1["referenceLineLocation"], "CoreOutside")
        self.assertEqual((w1["structureType"], w1["compositeId"]), ("Composite", {"guid": "C-AW"}))
        self.assertEqual(w1["favoriteName"], "KS + WDVS 42 cm")
        self.assertEqual(w1["floorIndex"], 0)

    def test_unflipped_exterior_walls_are_turned_before_openings_are_placed(self):
        # office favorites create unflipped walls: exterior face LEFT of the drawing direction (live 29.09.2026)
        names = [c for c, _ in self.fake.calls]
        self.assertLess(names.index("ModifyWalls"), names.index("CreateWindows"))
        mods = {m["elementId"]["guid"]: m for call in self.fake.sent("ModifyWalls") for m in call["wallsWithDetails"]}
        w1_guid = self.report["guid_map"]["W1#0"]
        self.assertEqual(mods[w1_guid]["begCoordinate"], {"x": 9.83, "y": 0.17})
        self.assertEqual(mods[w1_guid]["endCoordinate"], {"x": 0.17, "y": 0.17})
        win = created_keys(self.fake, "CreateWindows", "windowsData")[0]
        self.assertAlmostEqual(win["centerOffset"], 9.66 - 1.83)
        self.assertIs(win["oSide"], False)  # interior now lies RIGHT of the turned wall

    def test_top_links_are_set_for_walls_with_a_story_above(self):
        mods = {m["elementId"]["guid"]: m for call in self.fake.sent("ModifyWalls") for m in call["wallsWithDetails"]}
        g = self.report["guid_map"]
        self.assertEqual((mods[g["W1#0"]]["relativeTopStory"], mods[g["W1#0"]]["topOffset"]), (1, -0.15))
        self.assertEqual((mods[g["IW#0"]]["relativeTopStory"], mods[g["IW#0"]]["topOffset"]), (1, -0.35))
        self.assertNotIn("relativeTopStory", mods.get(g["V1#0"], {}))

    def test_the_run_passes_every_check(self):
        self.assertTrue(self.report["ok"], self.report["errors"])
        self.assertEqual(self.report["errors"], [])


class ZoneExecutionTest(unittest.TestCase):
    def test_zones_are_created_story_by_story_after_activating_the_story(self):
        report, fake = run()
        seq = [(c, p) for c, p in fake.calls if c in ("ChangeWindow", "CreateZones")]
        nav = [p["navigatorItemId"]["guid"] for c, p in seq if c == "ChangeWindow" and "navigatorItemId" in p]
        self.assertEqual(nav[:2], ["NAV-EG", "NAV-OG"])
        self.assertEqual(nav[-1], "NAV-EG")  # the active story is restored
        zone_calls = [p["zonesData"] for c, p in seq if c == "CreateZones"]
        self.assertEqual([[z["floorIndex"] for z in call] for call in zone_calls], [[0], [1]])
        self.assertTrue(report["ok"], report["errors"])

    def test_without_navigator_the_story_is_activated_by_index(self):
        # AC25/AC26 refuse navigatorItemId; since Tapir 1.7.0 ChangeWindow.storyIndex activates the story (live 05.10.2026)
        model = two_story_model()
        report, fake = run(model, FakeArchicad(spaces=model["spaces"], navigator_supported=False, story_switch_by_index=True))
        by_index = [p["storyIndex"] for c, p in fake.calls if c == "ChangeWindow" and "storyIndex" in p]
        self.assertIn(1, by_index)
        zone_calls = [p["zonesData"] for c, p in fake.calls if c == "CreateZones"]
        self.assertEqual([[z["floorIndex"] for z in call] for call in zone_calls], [[0], [1]])
        self.assertTrue(report["ok"], report["errors"])

    def test_story_that_cannot_be_activated_is_reported(self):
        # AC25/AC26 with Tapir <= 1.6.0: neither the navigator nor storyIndex works
        model = two_story_model()
        report, fake = run(model, FakeArchicad(spaces=model["spaces"], navigator_supported=False))
        self.assertFalse(report["ok"])
        self.assertTrue(any("could not be activated" in e for e in report["errors"]))

    def test_zone_without_a_closed_wall_ring_is_an_error_not_a_polygon(self):
        model = house()
        report, fake = run(model, FakeArchicad(spaces=model["spaces"], fail_zone_ids={"R1"}))
        self.assertFalse(report["ok"])
        self.assertTrue(any("R1" in e and "ring" in e for e in report["errors"]))
        self.assertFalse(any("polygonCoordinates" in z["geometry"] for z in created_keys(fake, "CreateZones", "zonesData")))

    def test_manual_zone_fallback_only_on_request(self):
        model = house()
        report, fake = run(model, FakeArchicad(spaces=model["spaces"], fail_zone_ids={"R1"}), allow_manual_zones=True)
        self.assertTrue(any("polygonCoordinates" in z["geometry"] for z in created_keys(fake, "CreateZones", "zonesData")))
        self.assertTrue(any("R1" in w and "manual" in w for w in report["warnings"]))

    def test_zone_properties_go_through_the_official_api(self):
        report, fake = run()
        values = [(v["propertyId"]["guid"], v["propertyValue"]) for call in fake.sent("API.SetPropertyValuesOfElements")
                  for v in call["elementPropertyValues"]]
        self.assertIn(("P-FB", {"type": "length", "status": "normal", "value": 0.15}), values)
        self.assertIn(("P-ABST", {"type": "length", "status": "normal", "value": -0.35}), values)
        self.assertIn(("P-LICHT", {"type": "length", "status": "normal", "value": 2.65}), values)

    def test_floor_buildups_follow_the_zone_polygon_read_back(self):
        report, fake = run()
        slabs = created_keys(fake, "CreateSlabs", "slabsData")
        buildup = next(s for s in slabs if s.get("favoriteName") == "Boden 15 cm" and abs(s["level"]) < 1e-6)
        self.assertEqual(len(buildup["polygonCoordinates"]), 4)  # Archicad repeats the first point; it is dropped
        self.assertEqual(buildup["polygonCoordinates"][0], {"x": 0.42, "y": 0.42})
        names = [c for c, _ in fake.calls]
        self.assertLess(max(i for i, c in enumerate(names) if c == "CreateZones"), max(i for i, c in enumerate(names) if c == "CreateSlabs"))


class SemanticsExecutionTest(unittest.TestCase):
    def test_every_element_is_classified_with_system_and_item(self):
        report, fake = run()
        items = created_keys(fake, "SetClassificationsOfElements", "elementClassifications")
        self.assertEqual(len(items), sum(report["created"].values()))
        self.assertTrue(all(i["classificationId"]["classificationSystemId"] == {"guid": "SYS"} for i in items))
        self.assertTrue(all("classificationItemId" in i["classificationId"] for i in items))

    def test_load_bearing_and_position_are_written_language_neutral(self):
        report, fake = run()
        values = [v["propertyValue"] for call in fake.sent("API.SetPropertyValuesOfElements") for v in call["elementPropertyValues"]
                  if v["propertyId"]["guid"] in ("P-TRAG", "P-LAGE")]
        self.assertTrue(values)
        self.assertTrue(all(v["type"] == "singleEnum" and v["value"]["type"] == "nonLocalizedValue" for v in values))
        self.assertIn("Exterior", {v["value"]["nonLocalizedValue"] for v in values})

    def test_layers_are_set_by_name(self):
        report, fake = run()
        g = report["guid_map"]
        layer_of = {i["elementId"]["guid"]: i["details"]["layerIndex"] for call in fake.sent("SetDetailsOfElements")
                    for i in call["elementsWithDetails"]}
        self.assertEqual(layer_of[g["IW#0"]], fake.office["layers"]["10 Wand innen"]["index"])
        self.assertEqual(layer_of[g["R1"]], fake.office["layers"]["80 Raum"]["index"])


class VerificationTest(unittest.TestCase):
    def test_silently_ignored_classification_is_caught(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], ignore_classification=True))
        self.assertFalse(report["ok"])
        self.assertTrue(any("classification" in e for e in report["errors"]))

    def test_silently_ignored_position_is_caught(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], ignore_position=True))
        self.assertFalse(report["ok"])
        self.assertTrue(any("position" in e.lower() or "Lage" in e for e in report["errors"]))

    def test_ignored_top_link_is_caught_by_the_heights(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], ignore_top_link=True))
        self.assertFalse(report["ok"])
        self.assertTrue(any("top" in e for e in report["errors"]))

    def test_silently_ignored_windows_are_caught_by_the_count(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], ignore_windows=True))
        self.assertFalse(report["ok"])
        self.assertTrue(any("Window" in e and "count" in e for e in report["errors"]))

    def test_slab_outline_that_differs_from_the_rule_is_caught(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], slab_outline_shift=0.1))
        self.assertFalse(report["ok"])
        self.assertTrue(any("outline" in e and "(rule D2)" in e for e in report["errors"]))

    def test_door_swing_is_checked_on_the_plan_outline(self):
        model = house()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], invert_oside=True))
        self.assertFalse(report["ok"])
        self.assertTrue(any("swing" in e for e in report["errors"]))

    def test_report_lists_the_rule_checks(self):
        report, _ = run()
        checks = report["checks"]
        for rule in ("B1", "B2", "B5", "C1", "C3", "D2", "R2", "E4"):
            self.assertIn(rule, checks)
            self.assertEqual(checks[rule]["failed"], 0, rule)
            self.assertGreater(checks[rule]["passed"], 0, rule)

    def test_check_mode_rereads_a_finished_build_without_changing_it(self):
        import json
        report, fake = run()
        plan = json.loads(json.dumps(report["plan"], default=str))  # as written by --report-out
        again = bfm.check(plan, bfm.readonly(fake))
        self.assertTrue(again["ok"], again["errors"][:3])
        fake.elements[report["guid_map"]["W1#0"]]["classification"] = None  # someone removed it by hand
        again = bfm.check(plan, bfm.readonly(fake))
        self.assertFalse(again["ok"])
        self.assertTrue(any("W1#0" in e and "classification" in e for e in again["errors"]))

    def test_guid_map_links_model_ids_to_archicad(self):
        report, _ = run()
        self.assertIn("W1#0", report["guid_map"])
        self.assertIn("R1", report["guid_map"])
        self.assertIn("buildup:R1", report["guid_map"])


if __name__ == "__main__":
    unittest.main()
