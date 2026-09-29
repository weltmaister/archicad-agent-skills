"""Executor tests for the further building parts (openings, columns, beams, roofs, bodies, ceilings) against FakeArchicad.

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
from helpers import CCW, MATERIAL_MAP, two_story_model  # noqa: E402


def rich_model():
    model = two_story_model()
    model["slabs"][1]["openings"] = [{"id": "SCH1", "center": [7.0, 7.0], "width": 0.6, "depth": 0.8}]
    model["openings"] = [{"id": "WD1", "host_wall_id": "IW", "kind": "opening", "offset_along_wall": 6.0, "width": 0.5, "height": 0.5,
                          "sill_height": 2.15}]
    model["columns"] = [{"id": "C1", "level_id": "L_EG", "position": [3.0, 4.0], "width": 0.3, "depth": 0.3, "material": "Stahlbeton"}]
    model["beams"] = [{"id": "UZ1", "level_id": "L_EG", "baseline": [[0.41, 4.0], [4.9, 4.0]], "width": 0.24, "height": 0.4,
                       "material": "Stahlbeton"}]
    model["roofs"] = [{"id": "SD", "level_id": "L_OG", "kind": "pitched", "boundary": [list(p) for p in CCW], "slope": 30,
                       "eave_elevation": 5.85, "overhang": 0.5}]
    model["spaces"][0]["ceiling"] = {"type": "suspended", "material": "Abgehängte Decke 40 cm"}
    model["technical_zones"] = [{"id": "HT1", "level_id": "L_EG", "boundary": [[6, 1], [9, 1], [9, 3], [6, 3]],
                                 "bottom_elevation": 2.25, "top_elevation": 2.65}]
    model["site_areas"] = [{"id": "GF1", "kind": "GF", "boundary": [[-5, -5], [20, -5], [20, 15], [-5, 15]], "elevation": -0.3}]
    return model


def run(model=None, fake=None, **kw):
    model = model or rich_model()
    fake = fake or FakeArchicad(spaces=model["spaces"])
    kw.setdefault("material_map", MATERIAL_MAP)
    return bfm.run(model, fake, **kw), fake


def items(fake, command, key):
    return [i for call in fake.sent(command) for i in call[key]]


class ExtrasTest(unittest.TestCase):
    def setUp(self):
        self.report, self.fake = run(din277=True)

    def test_everything_is_created_and_checked(self):
        self.assertTrue(self.report["ok"], self.report["errors"][:5])
        created = self.report["created"]
        self.assertEqual((created["Opening"], created["Column"], created["Beam"], created["Roof"], created["Morph"]), (2, 1, 1, 2, 4))
        for rule in ("D9", "E9", "T1", "T2", "T4", "T6", "T7", "T8", "D8"):
            self.assertIn(rule, self.report["checks"])
            self.assertEqual(self.report["checks"][rule]["failed"], 0, rule)

    def test_openings_go_one_per_call_into_their_host(self):
        calls = self.fake.sent("CreateOpenings")
        self.assertEqual([len(c["openingsData"]) for c in calls], [1, 1])  # one item per call (VS:117)
        g = self.report["guid_map"]
        hosts = {c["openingsData"][0]["ownerElementId"]["guid"] for c in calls}
        self.assertEqual(hosts, {g["D1"], g["IW#0"]})

    def test_floor_buildup_over_the_shaft_gets_a_hole(self):
        slabs = items(self.fake, "CreateSlabs", "slabsData")
        og_buildup = next(s for s in slabs if s.get("favoriteName") == "Boden 15 cm" and abs(s["level"] - 3.0) < 1e-6)
        self.assertEqual(og_buildup["holes"], [{"polygonCoordinates": [{"x": 6.7, "y": 6.6}, {"x": 7.3, "y": 6.6}, {"x": 7.3, "y": 7.4},
                                                                      {"x": 6.7, "y": 7.4}]}])

    def test_columns_beams_and_roofs_carry_their_materials(self):
        col = items(self.fake, "CreateColumns", "columnsData")[0]
        self.assertEqual(col["buildingMaterialId"], {"guid": "M-STB"})
        beam = items(self.fake, "CreateBeams", "beamsData")[0]
        self.assertEqual((beam["buildingMaterialId"], beam["zCoordinate"]), ({"guid": "M-STB"}, 2.65))
        roofs = items(self.fake, "CreateRoofs", "roofsData")
        self.assertEqual([r["compositeId"]["guid"] for r in roofs], ["C-UD", "C-OD"])

    def test_suspended_ceiling_uses_the_room_outline_and_its_composite(self):
        mods = items(self.fake, "ModifySlabs", "slabsWithDetails")
        self.assertIn({"elementId": {"guid": self.report["guid_map"]["ceiling:R1"]}, "structureType": "Composite",
                       "compositeId": {"guid": "C-AD"}}, mods)

    def test_site_area_gets_its_din277_kind_through_tapir(self):
        values = [v["propertyValue"] for call in self.fake.sent("SetPropertyValuesOfElements") for v in call["elementPropertyValues"]
                  if v["propertyId"]["guid"] == "P-FLAECHE"]
        self.assertEqual(values, [{"value": "GF"}])
        morphs = items(self.fake, "CreateMorphs", "morphsData")
        self.assertEqual(sorted(m["body"]["bodyType"] for m in morphs), ["Solid", "Solid", "Solid", "Surface"])
        ht = next(m for m in morphs if m.get("buildingMaterialId"))
        self.assertEqual(ht["buildingMaterialId"], {"guid": "M-HT"})

    def test_din277_bodies_get_their_class_through_tapir(self):
        # the official API does not support "Klassifizierung nach DIN 277" (6702, live 29.09.2026); Tapir takes the display value
        values = [v for call in self.fake.sent("SetPropertyValuesOfElements") for v in call["elementPropertyValues"]
                  if v["propertyId"]["guid"] == "P-DIN"]
        self.assertEqual([v["propertyValue"] for v in values], [{"value": "Regelfall"}, {"value": "Regelfall"}])

    def test_no_favorite_is_applied_after_creation(self):
        # ApplyFavoritesToElements moved an upper-story morph by -3.00 m and a roof covering by +0.04 m (live 29.09.2026):
        # roofs and bodies get composite, layer and display explicitly instead
        self.assertEqual(self.fake.sent("ApplyFavoritesToElements"), [])
        din = [m for m in self.report["plan"]["morphs"] if m["role"] in ("din277_body", "site_area")]
        self.assertEqual({m["sent"]["displayOption"] for m in din}, {"OutLinesOnly"})  # DIN 277 bodies must not cover the plan
        g = self.report["guid_map"]
        layer_of = {i["elementId"]["guid"]: i["details"]["layerIndex"] for call in self.fake.sent("SetDetailsOfElements")
                    for i in call["elementsWithDetails"]}
        self.assertEqual(layer_of[g["SD:structure"]], self.fake.office["layers"]["30 Dachstuhl"]["index"])
        self.assertEqual(layer_of[g["SD:covering"]], self.fake.office["layers"]["30 Dachaufbau"]["index"])
        self.assertEqual(self.report["checks"]["T6"]["failed"], 0)

    def test_openings_get_a_position_but_no_load_bearing_value(self):
        # "Tragende Funktion" is read-only on openings (6800, live); the guideline only gives "Lage: Innen" for them
        g = {v for k, v in self.report["guid_map"].items() if k in ("SCH1", "WD1")}
        written = [(v["elementId"]["guid"], v["propertyId"]["guid"]) for call in self.fake.sent("API.SetPropertyValuesOfElements")
                   for v in call["elementPropertyValues"] if v["elementId"]["guid"] in g]
        self.assertEqual(sorted(p for _, p in written), ["P-LAGE", "P-LAGE"])


class InstallationWallTest(unittest.TestCase):
    def test_installation_wall_is_subtracted_from_the_room_and_checked(self):
        model = rich_model()
        model["walls"].append({"id": "VW", "level_id": "L_EG", "role": "installation_wall", "baseline": [[1, 0.52], [3, 0.52]],
                               "representation": "centerline", "thickness": 0.2, "favorite": "GK Installationswand"})
        report, fake = run(model)
        self.assertTrue(report["ok"], report["errors"][:3])  # a profile wall keeps the reference line of its profile
        mods = {m["elementId"]["guid"]: m for call in fake.sent("ModifyWalls") for m in call["wallsWithDetails"]}
        self.assertEqual(mods[report["guid_map"]["VW#0"]]["zoneRel"], "SubtractFromZone")
        self.assertEqual(report["checks"]["C13"], {"passed": 1, "failed": 0})


class ExtrasVerificationTest(unittest.TestCase):
    def test_beam_with_a_fixed_segment_length_is_caught(self):
        # the office beam tool has a fixed 0.40 m segment: Tapir keeps it whatever endCoordinate says (live 29.09.2026)
        model = rich_model()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], fixed_beam_length=0.4))
        self.assertFalse(report["ok"])
        self.assertTrue(any("UZ1" in e and "length" in e for e in report["errors"]))

    def test_wall_opening_at_the_wrong_height_is_caught(self):
        model = rich_model()
        report, _ = run(model, FakeArchicad(spaces=model["spaces"], opening_sill_shift=-0.15))
        self.assertFalse(report["ok"])
        self.assertTrue(any("WD1" in e and "sill" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
