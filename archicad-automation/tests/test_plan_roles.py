"""Planning tests for the further building parts of the guideline: openings in walls and slabs, columns, beams,
railings, parapets, installation walls, footings, suspended ceilings, roof insulation, pitched roofs, DIN 277 bodies.

Run from the skill folder:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import build_from_model as bfm  # noqa: E402
from helpers import CCW, MATERIAL_MAP, OFFICE, by_id, ring_walls, two_story_model, window  # noqa: E402


def plan_of(model, **kw):
    kw.setdefault("office", OFFICE)
    kw.setdefault("material_map", MATERIAL_MAP)
    return bfm.build_plan(model, **kw)


def rect(cx, cy, w, d):
    return [(cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2), (cx - w / 2, cy + d / 2)]


class SlabOpeningTest(unittest.TestCase):
    def setUp(self):
        model = two_story_model()
        model["slabs"][1]["openings"] = [{"id": "SCH1", "center": [7.0, 7.0], "width": 0.6, "depth": 0.8}]
        self.plan = plan_of(model)

    def test_opening_in_a_raw_slab_is_an_opening_element(self):
        # guideline p.30: opening tool, one opening per affected element, "Durchbrüche / Schlitze - Öffnung", inside
        op = by_id(self.plan["openings"], "SCH1")[0]
        self.assertEqual((op["role"], op["host_key"]), ("slab_opening", "D1"))
        # base point: x = centre, y = UPPER edge, height runs in -y (VS:118)
        self.assertEqual(op["payload"]["basePoint"], {"x": 7.0, "y": 7.4, "z": 2.85})
        self.assertEqual((op["payload"]["width"], op["payload"]["height"]), (0.6, 0.8))
        self.assertEqual(op["semantics"]["classification"], "ELEMENTE > Durchbrüche / Schlitze > Öffnung")
        self.assertEqual(op["semantics"]["position"], "interior")

    def test_floor_buildup_above_gets_a_hole_not_an_opening(self):
        # guideline p.30: no openings in floor build-ups, geometric holes instead
        b = {r["model_id"]: r for r in self.plan["buildups"]}
        self.assertEqual(b["R2"]["holes"], [[{"x": 6.7, "y": 6.6}, {"x": 7.3, "y": 6.6}, {"x": 7.3, "y": 7.4}, {"x": 6.7, "y": 7.4}]])
        self.assertEqual(b["R1"]["holes"], [])


class WallOpeningTest(unittest.TestCase):
    def test_wall_penetration_and_slot(self):
        model = two_story_model(openings=[
            {"id": "WD1", "host_wall_id": "IW", "kind": "opening", "offset_along_wall": 6.0, "width": 0.5, "height": 0.5, "sill_height": 2.15},
            {"id": "WS1", "host_wall_id": "W1", "kind": "niche", "offset_along_wall": 3.0, "width": 0.2, "height": 1.0, "sill_height": 0.2}])
        plan = plan_of(model)
        wd = by_id(plan["openings"], "WD1")[0]
        self.assertEqual(wd["role"], "wall_opening")
        self.assertEqual(wd["semantics"]["classification"], "ELEMENTE > Durchbrüche / Schlitze > Öffnung")
        # base point on the final reference line of the host; z = sill above OKFF (absolute); model position is absolute
        self.assertEqual(wd["payload"]["basePoint"], {"x": 5.0, "y": 6.0, "z": 2.15})
        self.assertEqual(wd["expect"]["sill_abs"], 2.15)
        # a slot needs a depth; CreateOpenings has none and would cut through the wall -> skipped with the reason
        self.assertEqual(by_id(plan["openings"], "WS1"), [])
        self.assertIn("depth", {s["id"]: s["reason"] for s in plan["skipped"]}["WS1"])

    def test_opening_goes_into_every_penetrated_slab_but_the_floor_buildup(self):
        model = two_story_model()
        model["slabs"].append({"id": "DD", "level_id": "L_OG", "role": "roof_insulation", "boundary": [list(p) for p in CCW],
                               "thickness": 0.2, "bottom_elevation": 5.85, "openings": [{"id": "SD1", "center": [7, 7], "width": 0.6, "depth": 0.6}]})
        op = by_id(plan_of(model)["openings"], "SD1")[0]
        self.assertEqual((op["host_key"], op["payload"]["basePoint"]["z"]), ("DD", 6.05))

    def test_railing_in_front_of_the_facade_is_no_junction(self):
        model = two_story_model()
        model["walls"].append({"id": "GL", "level_id": "L_OG", "role": "railing", "baseline": [[2, -0.06], [4, -0.06]],
                               "representation": "centerline", "thickness": 0.04, "height": 1.0})
        self.assertFalse(any(w.startswith("wall GL:") for w in plan_of(model)["warnings"]))


class ColumnTest(unittest.TestCase):
    def test_column_runs_from_raw_slab_to_slab_underside(self):
        # guideline p.11: OK Rohdecke to UK Rohdecke, load-bearing, inside/outside by the envelope
        model = two_story_model(columns=[{"id": "C1", "level_id": "L_EG", "position": [3.0, 4.0], "width": 0.3, "depth": 0.3,
                                          "material": "Stahlbeton"},
                                         {"id": "C2", "level_id": "L_EG", "position": [12.0, 4.0], "width": 0.3, "depth": 0.3}])
        plan = plan_of(model)
        c1, c2 = by_id(plan["columns"], "C1")[0], by_id(plan["columns"], "C2")[0]
        self.assertEqual(c1["payload"]["coordinates"], {"x": 3.0, "y": 4.0, "z": -0.15})
        self.assertAlmostEqual(c1["payload"]["height"], 2.8)
        self.assertEqual(c1["semantics"], {"classification": "ELEMENTE > Stütze / Pfeiler > Stütze", "load_bearing": True,
                                           "position": "interior", "layer": "10 Stütze"})
        self.assertEqual(c2["semantics"]["position"], "exterior")
        self.assertEqual(c1["building_material"], "Stahlbeton")

    def test_pad_footing_ends_at_the_top_of_the_ground_slab(self):
        model = two_story_model(columns=[{"id": "PF", "level_id": "L_EG", "role": "pad_footing", "position": [3.0, 4.0], "width": 1.0,
                                          "depth": 1.0, "height": 0.6}])
        plan = plan_of(model)
        pf = by_id(plan["columns"], "PF")[0]
        self.assertEqual(pf["payload"]["coordinates"]["z"], -0.75)
        self.assertEqual(pf["semantics"]["classification"], "ELEMENTE > Fundament > Punktfundament")
        self.assertTrue(any("PF" in w and "own story" in w for w in plan["warnings"]))  # guideline p.8: separate story


class BeamTest(unittest.TestCase):
    def test_downstand_beam_hangs_under_the_slab(self):
        model = two_story_model(beams=[{"id": "UZ1", "level_id": "L_EG", "baseline": [[0.41, 4.0], [9.59, 4.0]], "width": 0.24,
                                        "height": 0.4, "material": "Stahlbeton"}])
        uz = by_id(plan_of(model)["beams"], "UZ1")[0]
        self.assertEqual(uz["role"], "downstand_beam")
        self.assertAlmostEqual(uz["payload"]["zCoordinate"], 2.65)  # top = UK Rohdecke, zCoordinate is the top (live)
        self.assertEqual(uz["payload"]["anchorPoint"], "TopCenter")
        self.assertEqual(uz["semantics"]["classification"], "ELEMENTE > Träger / Balken / Unterzug > Unterzug")

    def test_insulation_strip_stops_the_exterior_wall_under_the_slab(self):
        # guideline p.17/18: with a Dämmstreifen/Brandriegel the exterior wall ends at UK Rohdecke (no double quantities)
        model = two_story_model(beams=[{"id": "DS1", "level_id": "L_EG", "role": "insulation_strip", "host_wall_id": "W1",
                                        "baseline": [[0, 0.08], [10, 0.08]], "width": 0.16, "height": 0.2, "top_elevation": 2.85}])
        plan = plan_of(model)
        w1 = by_id(plan["walls"], "W1")[0]
        self.assertEqual(w1["top_link"], {"relativeTopStory": 1, "topOffset": -0.35})
        self.assertAlmostEqual(w1["expect"]["z_max"], 2.65)
        self.assertEqual(by_id(plan["beams"], "DS1")[0]["semantics"]["load_bearing"], False)


class WallRoleTest(unittest.TestCase):
    def test_railing_as_wall(self):
        model = two_story_model()
        model["walls"].append({"id": "GL", "level_id": "L_OG", "role": "railing", "baseline": [[2, -1], [4, -1]],
                               "representation": "centerline", "thickness": 0.05, "height": 1.0})
        gl = by_id(plan_of(model)["walls"], "GL")[0]
        self.assertEqual(gl["semantics"], {"classification": "ELEMENTE > Geländer", "load_bearing": False, "position": "exterior",
                                           "layer": "40 Absturzsicherung"})
        self.assertEqual((gl["expect"]["z_min"], gl["expect"]["z_max"]), (3.0, 4.0))

    def test_parapet_stands_on_the_roof_slab_with_its_core_line(self):
        model = two_story_model()
        model["walls"] += ring_walls(CCW, "L_OG", "P", role="parapet", height=0.5)
        plan = plan_of(model)
        p1 = by_id(plan["walls"], "P1")[0]
        self.assertEqual(p1["payload"]["referenceLineLocation"], "CoreOutside")
        self.assertEqual((p1["payload"]["begCoordinate"], p1["payload"]["endCoordinate"]), ({"x": 0.17, "y": 0.17}, {"x": 9.83, "y": 0.17}))
        self.assertEqual((p1["expect"]["z_min"], p1["expect"]["z_max"]), (5.85, 6.35))
        self.assertAlmostEqual(p1["payload"]["zCoordinate"], 2.85)
        self.assertEqual(len(plan["loops"]), 3)

    def test_installation_wall_is_subtracted_from_the_room(self):
        model = two_story_model()
        model["walls"].append({"id": "VW", "level_id": "L_EG", "role": "installation_wall", "baseline": [[1, 0.52], [3, 0.52]],
                               "representation": "centerline", "thickness": 0.2})
        vw = by_id(plan_of(model)["walls"], "VW")[0]
        self.assertEqual(vw["zone_rel"], "SubtractFromZone")
        self.assertEqual(vw["semantics"]["classification"], "ELEMENTE > Wand > Vorwand / Installationswand")

    def test_strip_footing_on_a_building_story_warns(self):
        model = two_story_model()
        model["walls"].append({"id": "SF", "level_id": "L_EG", "role": "strip_footing", "baseline": [[0, 0], [10, 0]],
                               "representation": "centerline", "thickness": 0.5, "height": 0.8})
        plan = plan_of(model)
        self.assertTrue(any("SF" in w and "own story" in w for w in plan["warnings"]))


class CeilingAndRoofTest(unittest.TestCase):
    def test_suspended_ceiling_is_planned_per_room(self):
        model = two_story_model()
        model["spaces"][0]["ceiling"] = {"type": "suspended", "thickness": 0.40, "material": "Abgehängte Decke 40 cm"}
        plan = plan_of(model)
        c = by_id(plan["ceilings"], "R1")[0]
        self.assertEqual(c["role"], "suspended_ceiling")
        self.assertAlmostEqual(c["payload"]["level"], 2.65)   # top = UK Rohdecke
        self.assertAlmostEqual(c["payload"]["thickness"], 0.40)
        self.assertEqual(c["semantics"]["layer"], "20 Decke abgehängt")
        self.assertEqual(by_id(plan["zones"], "R1")[0]["zone_properties"]["top_offset"], -0.35)  # variant 01: room to UK Rohdecke

    def test_room_variant_02_ends_under_the_suspended_ceiling(self):
        model = two_story_model()
        model["spaces"][0]["ceiling"] = {"type": "suspended", "thickness": 0.40, "variant": "02"}
        self.assertAlmostEqual(by_id(plan_of(model)["zones"], "R1")[0]["zone_properties"]["top_offset"], -0.75)

    def test_roof_insulation_slab_keeps_its_boundary_and_semantics(self):
        model = two_story_model()
        model["slabs"].append({"id": "DD", "level_id": "L_OG", "role": "roof_insulation", "boundary": [list(p) for p in CCW],
                               "thickness": 0.2, "bottom_elevation": 5.85})
        dd = by_id(plan_of(model)["slabs"], "DD")[0]
        self.assertEqual(dd["semantics"], {"classification": "ELEMENTE > Bekleidung / Belag > Dämmung", "load_bearing": False,
                                           "position": "exterior", "layer": "30 Dachaufbau"})
        self.assertAlmostEqual(dd["payload"]["level"], 6.05)

    def test_pitched_roof_is_built_from_structure_and_covering(self):
        # guideline p.23-27: pitched roofs are always multi-part (Sparrenlage mit Dämmung + Dachdeckung)
        model = two_story_model(roofs=[{"id": "SD", "level_id": "L_OG", "kind": "pitched", "boundary": [list(p) for p in CCW],
                                        "slope": 30, "eave_elevation": 5.85, "overhang": 0.5}])
        plan = plan_of(model)
        parts = {r["role"]: r for r in plan["roofs"]}
        self.assertEqual(set(parts), {"roof_structure", "roof_covering"})
        s, c = parts["roof_structure"], parts["roof_covering"]
        self.assertAlmostEqual(s["payload"]["levels"][0]["levelAngle"], math.radians(30))
        self.assertAlmostEqual(s["payload"]["level"], 5.85)
        self.assertEqual(s["composite"], "Unterdach mit Dämmung 21,5 cm")
        self.assertEqual(c["composite"], "Oberdach ohne Sparren 8,5 cm")
        self.assertAlmostEqual(c["payload"]["level"], 5.85 + 0.215 / math.cos(math.radians(30)), places=4)
        self.assertEqual(s["semantics"]["classification"], "ELEMENTE > Dach")
        self.assertEqual(c["semantics"]["classification"], "ELEMENTE > Bekleidung / Belag > Dachdeckung")
        self.assertFalse(c["semantics"]["load_bearing"])


class TwoBodiesTest(unittest.TestCase):
    def test_each_slab_follows_its_own_exterior_ring(self):
        second = [(20, 0), (26, 0), (26, 5), (20, 5)]
        model = two_story_model()
        model["walls"] += ring_walls(second, "L_EG", "G")
        model["slabs"].append({"id": "BP2", "level_id": "L_EG", "boundary": [list(p) for p in second], "thickness": 0.3,
                               "top_elevation": -0.15})
        model["columns"] = [{"id": "C9", "level_id": "L_EG", "position": [23.0, 2.5], "width": 0.3, "depth": 0.3}]
        plan = plan_of(model)
        bp2 = by_id(plan["slabs"], "BP2")[0]
        self.assertEqual(bp2["payload"]["polygonCoordinates"][0], {"x": 20.17, "y": 0.17})
        self.assertEqual(by_id(plan["slabs"], "BP")[0]["payload"]["polygonCoordinates"][0], {"x": 0.17, "y": 0.17})
        self.assertEqual(by_id(plan["columns"], "C9")[0]["semantics"]["position"], "interior")


class Din277Test(unittest.TestCase):
    def test_bodies_follow_the_outer_contour_story_by_story(self):
        # guideline p.32: one body per story, bottom = story level, DIN 277 class set
        plan = plan_of(two_story_model(), din277=True)
        bodies = {r["level_id"]: r for r in plan["morphs"]}
        self.assertEqual(set(bodies), {"L_EG", "L_OG"})
        eg = bodies["L_EG"]
        self.assertEqual((eg["expect"]["z_min"], eg["expect"]["z_max"]), (0.0, 3.0))
        self.assertEqual(bodies["L_OG"]["expect"]["z_max"], 5.85)
        self.assertEqual(eg["din277"], "Regelfall")
        self.assertEqual(eg["semantics"]["layer"], "80 BGF BRI")
        self.assertEqual(len(eg["payload"]["body"]["vertices"]), 8)

    def test_bodies_are_off_by_default(self):
        self.assertEqual(plan_of(two_story_model())["morphs"], [])


if __name__ == "__main__":
    unittest.main()


class FoundationStoryTest(unittest.TestCase):
    def model(self):
        model = two_story_model()
        model["levels"].insert(0, {"id": "L_UG", "name": "UG", "elevation": -3.0})
        model["walls"].append({"id": "SF1", "level_id": "L_UG", "role": "strip_footing", "baseline": [[0.29, 0.29], [9.71, 0.29]],
                               "representation": "centerline", "thickness": 0.5, "height": 0.8, "material": "Stahlbeton"})
        model["columns"] = [{"id": "PF1", "level_id": "L_UG", "role": "pad_footing", "position": [3.0, 4.0], "width": 1.0, "depth": 1.0,
                             "height": 0.6, "material": "Stahlbeton"}]
        return model

    def test_ground_slab_stays_the_ground_slab_above_a_foundation_story(self):
        plan = plan_of(self.model())
        self.assertEqual(by_id(plan["slabs"], "BP")[0]["role"], "ground_slab")
        self.assertFalse(any("own story" in w for w in plan["warnings"]))

    def test_strip_footing_reaches_up_to_the_top_of_the_ground_slab(self):
        # guideline p.8: OK Fundament = OK Sohlplatte, own story for the foundations
        plan = plan_of(self.model())
        sf = by_id(plan["walls"], "SF1")[0]
        self.assertEqual((sf["expect"]["z_min"], sf["expect"]["z_max"]), (-0.95, -0.15))
        self.assertEqual(sf["semantics"]["classification"], "ELEMENTE > Fundament > Streifenfundament")
        self.assertEqual(by_id(plan["columns"], "PF1")[0]["expect"], {"z_min": -0.75, "z_max": -0.15})


class PriorityTest(unittest.TestCase):
    def test_slab_that_cannot_cut_the_wall_finish_warns(self):
        # rule C8: the raw slab ends at the inner core face and overlaps the inner plaster; its material must win
        office = dict(OFFICE, materials=dict(OFFICE["materials"], Gipsputz={"guid": "M-GP", "priority": 900}))
        plan = bfm.build_plan(two_story_model(), office=office, material_map=MATERIAL_MAP)
        self.assertTrue(any("D1" in w and "Gipsputz" in w and "priority" in w for w in plan["warnings"]))
        self.assertFalse(any("priority" in w for w in plan_of(two_story_model())["warnings"]))


class StoryIndexTest(unittest.TestCase):
    def test_story_on_zero_must_have_index_zero(self):
        # office convention (VS:176): the story on +-0.00 has index 0, basements negative
        import helpers
        from fake_archicad import FakeArchicad
        office = helpers.office(stories=[{"index": 0, "level": -3.0, "name": "UG"}, {"index": 1, "level": 0.0, "name": "EG"},
                                         {"index": 2, "level": 3.0, "name": "OG"}],
                                story_items={"0": "NAV-UG", "1": "NAV-EG", "2": "NAV-OG"}, act_story=1)
        model = two_story_model()
        report = bfm.run(model, FakeArchicad(office=office, spaces=model["spaces"]), material_map=MATERIAL_MAP)
        self.assertTrue(any("index 1" in w and "0.00" in w for w in report["warnings"]))


class MorphRoleTest(unittest.TestCase):
    def test_technical_zone_is_a_room_proposal_body(self):
        # guideline p.15/22: Morph, "Raum > Raumvorschlag", not load-bearing, inside (as the office favorite "Haustechnik-Bereiche")
        model = two_story_model(technical_zones=[{"id": "HT1", "level_id": "L_EG", "boundary": [[1, 1], [4, 1], [4, 3], [1, 3]],
                                                  "bottom_elevation": 2.25, "top_elevation": 2.65}])
        ht = by_id(plan_of(model)["morphs"], "HT1")[0]
        self.assertEqual(ht["semantics"], {"classification": "ELEMENTE > Raum > Raumvorschlag", "load_bearing": False,
                                           "position": "interior", "layer": "70 Lüftung Installation"})
        self.assertEqual(ht["building_material"], "Haustechnikbereich")
        self.assertEqual((ht["expect"]["z_min"], ht["expect"]["z_max"]), (2.25, 2.65))

    def test_site_areas_carry_their_din277_kind(self):
        # guideline p.33: morph surfaces, property "Flächenart nach DIN 277" for every area
        model = two_story_model(site_areas=[{"id": "GF1", "kind": "GF", "boundary": [[-5, -5], [20, -5], [20, 15], [-5, 15]], "elevation": -0.3}])
        gf = by_id(plan_of(model)["morphs"], "GF1")[0]
        self.assertEqual(gf["role"], "site_area")
        self.assertEqual(gf["din277_area"], "GF")
        self.assertEqual(gf["payload"]["body"]["bodyType"], "Surface")
        self.assertEqual(gf["semantics"]["classification"], "ELEMENTE > Bauelement - beliebig")
        # a surface below the cut plane is drawn with its cover fill over the walls (live 29.09.2026): no cover fill
        self.assertIs(gf["payload"]["useCoverFillType"], False)
        body = plan_of(two_story_model(), din277=True)["morphs"][0]
        self.assertIs(body["payload"]["useCoverFillType"], False)

    def test_unknown_area_kind_is_skipped(self):
        model = two_story_model(site_areas=[{"id": "X1", "kind": "NUF", "boundary": [[0, 0], [1, 0], [1, 1]], "elevation": 0.0}])
        plan = plan_of(model)
        self.assertEqual(plan["morphs"], [])
        self.assertIn("GF", {s["id"]: s["reason"] for s in plan["skipped"]}["X1"])
