"""Planning tests for scripts/build_from_model.py: the fixed rules applied to the intermediate model, nothing sent.

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
from helpers import CCW, CW, MATERIAL_MAP, OFFICE, by_id, office, ring_walls, two_story_model, window  # noqa: E402


def plan_of(model, **kw):
    kw.setdefault("office", OFFICE)
    kw.setdefault("material_map", MATERIAL_MAP)
    return bfm.build_plan(model, **kw)


def xy(c):
    return round(c["x"], 4), round(c["y"], 4)


def ring_of(polygon):
    return [(round(p["x"], 4), round(p["y"], 4)) for p in polygon]


class InputTest(unittest.TestCase):
    def test_model_in_millimetres_is_refused(self):
        model = two_story_model()
        model["metadata"]["units"] = "mm"
        plan = plan_of(model)
        self.assertTrue(any("units" in e for e in plan["errors"]))

    def test_level_datum_is_inferred_from_the_slab_tops(self):
        model = two_story_model()
        del model["metadata"]["level_datum"]
        self.assertEqual(plan_of(model)["datum"]["level_datum"], "OKFF")  # slab tops sit 0.15 below the levels
        for slab, top in zip(model["slabs"], (0.0, 3.0, 6.0)):
            slab["top_elevation"] = top
        del model["metadata"]["floor_buildup"]
        plan = plan_of(model)
        self.assertEqual(plan["datum"]["level_datum"], "OKRD")
        self.assertTrue(any("level_datum" in n for n in plan["notes"]))

    def test_model_far_from_the_origin_warns(self):
        model = two_story_model(walls=ring_walls([(5000, 0), (5010, 0), (5010, 8), (5000, 8)]), slabs=[], spaces=[])
        self.assertTrue(any("origin" in w for w in plan_of(model)["warnings"]))


class WallGeometryTest(unittest.TestCase):
    def test_exterior_reference_line_is_the_outer_face_of_the_core(self):
        # guideline p.9/12: reference line "Kern außen"; KS + WDVS 42 cm has 0.17 m of plaster + insulation in front
        w1 = by_id(plan_of(two_story_model())["walls"], "W1")[0]
        self.assertEqual(w1["payload"]["referenceLineLocation"], "CoreOutside")
        self.assertEqual(xy(w1["payload"]["begCoordinate"]), (0.17, 0.17))
        self.assertEqual(xy(w1["payload"]["endCoordinate"]), (9.83, 0.17))
        self.assertEqual(w1["composite"], "KS + WDVS 42 cm")
        self.assertAlmostEqual(w1["payload"]["thickness"], 0.42)

    def test_corners_follow_each_walls_own_offset(self):
        walls = ring_walls(CCW)
        walls[0]["material"] = "Stahlbeton"  # basic structure: no skins in front of the core
        w = {r["model_id"]: r for r in plan_of(two_story_model(walls=walls, slabs=[], spaces=[]))["walls"]}
        self.assertEqual(xy(w["W1"]["payload"]["begCoordinate"]), (0.17, 0.0))
        self.assertEqual(xy(w["W4"]["payload"]["endCoordinate"]), (0.17, 0.0))
        self.assertEqual(xy(w["W1"]["payload"]["endCoordinate"]), (9.83, 0.0))

    def test_without_the_office_catalog_the_core_offset_is_reported_as_open(self):
        plan = bfm.build_plan(two_story_model(), material_map=MATERIAL_MAP)
        self.assertTrue(any("office catalog" in w for w in plan["warnings"]))
        self.assertEqual(xy(by_id(plan["walls"], "W1")[0]["payload"]["begCoordinate"]), (0.0, 0.0))

    def test_clockwise_loop_is_reoriented_counter_clockwise(self):
        model = two_story_model(walls=ring_walls(CW), slabs=[], spaces=[], openings=[window("W1", 2.0)])
        plan = plan_of(model)
        w1 = by_id(plan["walls"], "W1")[0]
        self.assertTrue(w1["reversed"])
        self.assertEqual(xy(w1["payload"]["begCoordinate"]), (0.17, 7.83))
        # model offset 2.0 from (0,0) towards (0,8): the centre sits at y = 2.0 whatever the direction
        self.assertAlmostEqual(plan["windows"][0]["center_offset"], 7.83 - 2.0)

    def test_interior_wall_ending_on_the_facade_follows_the_core_line(self):
        iw = by_id(plan_of(two_story_model())["walls"], "IW")[0]
        self.assertEqual(xy(iw["payload"]["begCoordinate"]), (5.0, 0.17))
        self.assertEqual(xy(iw["payload"]["endCoordinate"]), (5.0, 7.83))
        self.assertEqual(iw["payload"]["referenceLineLocation"], "Center")

    def test_interior_wall_ending_at_the_inner_face_is_extended_to_the_reference_line(self):
        model = two_story_model()
        model["walls"][-1]["baseline"] = [[5, 0.42], [5, 7.58]]
        plan = plan_of(model)
        iw = by_id(plan["walls"], "IW")[0]
        self.assertEqual(xy(iw["payload"]["begCoordinate"]), (5.0, 0.17))
        self.assertFalse(any(w.startswith("wall IW:") for w in plan["warnings"]))
        self.assertTrue(any("IW" in n and "reference line" in n for n in plan["notes"]))

    def test_short_segments_are_skipped_with_their_openings(self):
        walls = [{"id": "TINY", "level_id": "L_EG", "baseline": [[20, 0], [20.1, 0]], "representation": "centerline", "thickness": 0.2}]
        plan = plan_of(two_story_model(walls=walls, slabs=[], spaces=[], openings=[window("TINY", 0.05)]))
        reasons = {s["id"]: s["reason"] for s in plan["skipped"]}
        self.assertIn("short", reasons["TINY"])
        self.assertIn("O_TINY_0.05", reasons)

    def test_multi_segment_baseline_is_split_and_the_opening_lands_on_its_segment(self):
        walls = [{"id": "L", "level_id": "L_EG", "baseline": [[20, 0], [24, 0], [24, 3]], "representation": "centerline",
                  "thickness": 0.2, "is_load_bearing": False}]
        plan = plan_of(two_story_model(walls=walls, slabs=[], spaces=[], openings=[window("L", 5.0, kind="door")]))
        self.assertEqual([w["key"] for w in plan["walls"]], ["L#0", "L#1"])
        self.assertEqual(plan["doors"][0]["host_key"], "L#1")
        self.assertAlmostEqual(plan["doors"][0]["center_offset"], 1.0)

    def test_composite_thicker_than_the_model_wall_warns(self):
        walls = ring_walls(CCW, thickness=0.365)
        plan = plan_of(two_story_model(walls=walls, slabs=[], spaces=[]))
        self.assertTrue(any("0.420" in w and "0.365" in w for w in plan["warnings"]))


class HeightTest(unittest.TestCase):
    def setUp(self):
        self.plan = plan_of(two_story_model())
        self.walls = {r["model_id"]: r for r in self.plan["walls"]}

    def test_exterior_wall_runs_from_raw_slab_to_raw_slab_above(self):
        # guideline p.12: UK = OK Rohdecke, OK = OK Rohdecke of the next story; the top is linked to that story
        w1 = self.walls["W1"]
        self.assertAlmostEqual(w1["payload"]["zCoordinate"], -0.15)
        self.assertAlmostEqual(w1["payload"]["height"], 3.0)
        self.assertEqual(w1["top_link"], {"relativeTopStory": 1, "topOffset": -0.15})
        self.assertEqual((round(w1["expect"]["z_min"], 3), round(w1["expect"]["z_max"], 3)), (-0.15, 2.85))

    def test_top_story_exterior_wall_ends_at_the_roof_slab(self):
        v1 = self.walls["V1"]
        self.assertAlmostEqual(v1["payload"]["zCoordinate"], -0.15)
        self.assertAlmostEqual(v1["payload"]["height"], 3.0)
        self.assertIsNone(v1["top_link"])
        self.assertEqual((round(v1["expect"]["z_min"], 3), round(v1["expect"]["z_max"], 3)), (2.85, 5.85))

    def test_interior_wall_ends_under_the_slab_above(self):
        # guideline p.20 variant 02: OK Rohdecke to UK Rohdecke
        iw = self.walls["IW"]
        self.assertAlmostEqual(iw["payload"]["zCoordinate"], -0.15)
        self.assertAlmostEqual(iw["payload"]["height"], 2.8)
        self.assertEqual(iw["top_link"], {"relativeTopStory": 1, "topOffset": -0.35})

    def test_non_load_bearing_wall_on_screed_starts_below_the_covering(self):
        model = two_story_model()
        model["walls"][-1].update(base="screed", covering_thickness=0.015)
        iw = by_id(plan_of(model)["walls"], "IW")[0]
        self.assertAlmostEqual(iw["payload"]["zCoordinate"], -0.015)
        self.assertAlmostEqual(iw["payload"]["height"], 2.665)

    def test_screed_base_is_refused_for_a_load_bearing_wall(self):
        model = two_story_model()
        model["walls"][-1].update(base="screed", is_load_bearing=True)
        plan = plan_of(model)
        self.assertAlmostEqual(by_id(plan["walls"], "IW")[0]["payload"]["zCoordinate"], -0.15)
        self.assertTrue(any("IW" in w and "screed" in w for w in plan["warnings"]))

    def test_okrd_datum_puts_the_wall_foot_on_the_story_level(self):
        model = two_story_model()
        model["metadata"].update(level_datum="OKRD", floor_buildup=0.10)
        for slab, top in zip(model["slabs"], (0.0, 3.0, 6.0)):
            slab["top_elevation"] = top
        plan = plan_of(model)
        w1 = by_id(plan["walls"], "W1")[0]
        self.assertAlmostEqual(w1["payload"]["zCoordinate"], 0.0)
        self.assertEqual(w1["top_link"], {"relativeTopStory": 1, "topOffset": 0.0})

    def test_model_wall_height_is_replaced_by_the_rule_and_noted(self):
        model = two_story_model()
        model["walls"][0]["height"] = 2.8
        plan = plan_of(model)
        self.assertAlmostEqual(by_id(plan["walls"], "W1")[0]["payload"]["height"], 3.0)
        self.assertTrue(any("W1" in n and "2.80" in n for n in plan["notes"]))


class OpeningTest(unittest.TestCase):
    def test_window_offset_follows_the_core_line(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0)]))
        self.assertAlmostEqual(plan["windows"][0]["center_offset"], 1.83)

    def test_sill_is_measured_from_the_raw_floor(self):
        # the office favorites sit doors 0.15 and windows 1.05 above the wall foot (= OKRD, live 29.09.2026)
        plan = plan_of(two_story_model(openings=[window("W1", 2.0), window("W1", 6.0, kind="door", sill_height=None, height=2.135)]))
        self.assertAlmostEqual(plan["windows"][0]["payload"]["sillHeight"], 1.05)
        self.assertAlmostEqual(plan["doors"][0]["payload"]["sillHeight"], 0.15)

    def test_floor_to_ceiling_window_reaches_down_to_the_raw_slab(self):
        # guideline p.13: add the floor build-up to the bottom of a floor-to-ceiling window
        plan = plan_of(two_story_model(openings=[window("W1", 2.0, sill_height=0.0, height=2.41)]))
        payload = plan["windows"][0]["payload"]
        self.assertAlmostEqual(payload["sillHeight"], 0.0)
        self.assertAlmostEqual(payload["height"], 2.56)

    def test_exterior_openings_open_inward_by_default(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0), window("W1", 6.0, kind="door")]))
        self.assertEqual((plan["windows"][0]["swing"], plan["doors"][0]["swing"]), ("inward", "inward"))
        self.assertIs(plan["windows"][0]["interior_left"], True)

    def test_an_explicit_outward_swing_is_kept(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0, swing="nach außen")]))
        self.assertEqual(plan["windows"][0]["swing"], "outward")

    def test_openings_in_interior_walls_keep_the_archicad_side(self):
        plan = plan_of(two_story_model(openings=[window("IW", 5.0, kind="door")]))
        self.assertIsNone(plan["doors"][0]["swing"])

    def test_opening_where_another_wall_joins_the_host_is_reported(self):
        plan = plan_of(two_story_model(openings=[window("W1", 5.0, kind="door")]))
        self.assertTrue(any(w.startswith("opening O_W1_5.0:") and "IW" in w for w in plan["warnings"]))

    def test_opening_beside_a_junction_is_accepted(self):
        plan = plan_of(two_story_model(openings=[window("W1", 3.0)]))
        self.assertFalse(any(w.startswith("opening") for w in plan["warnings"]))

    def test_opening_without_width_is_skipped(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0, width=None)]))
        self.assertEqual(plan["windows"], [])
        self.assertIn("width", plan["skipped"][0]["reason"])

    def test_edge_referenced_offset_is_converted_to_the_centre(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0, offset_reference="start_edge")]))
        self.assertAlmostEqual(plan["windows"][0]["center_offset"], 2.0 + 0.63 - 0.17)


class SlabTest(unittest.TestCase):
    def setUp(self):
        self.plan = plan_of(two_story_model())
        self.slabs = {r["model_id"]: r for r in self.plan["slabs"]}

    def test_slab_roles_follow_from_their_heights(self):
        self.assertEqual({k: s["role"] for k, s in self.slabs.items()}, {"BP": "ground_slab", "D1": "floor_slab", "DA": "roof_slab"})

    def test_ground_slab_reaches_the_outer_face_of_the_core(self):
        # guideline p.8: VK Sohlplatte = VK Rohbauwand
        self.assertEqual(ring_of(self.slabs["BP"]["payload"]["polygonCoordinates"]), [(0.17, 0.17), (9.83, 0.17), (9.83, 7.83), (0.17, 7.83)])

    def test_floor_slab_ends_at_the_inner_core_face_of_the_walls_passing_it(self):
        self.assertEqual(ring_of(self.slabs["D1"]["payload"]["polygonCoordinates"]), [(0.41, 0.41), (9.59, 0.41), (9.59, 7.59), (0.41, 7.59)])
        self.assertEqual(ring_of(self.slabs["DA"]["payload"]["polygonCoordinates"]), [(0.41, 0.41), (9.59, 0.41), (9.59, 7.59), (0.41, 7.59)])

    def test_raw_slab_level_and_home_story(self):
        d1 = self.slabs["D1"]
        self.assertAlmostEqual(d1["payload"]["level"], 2.85)
        self.assertEqual(d1["level_id"], "L_OG")  # "Rohdecke unter Geschoss"
        model = two_story_model()
        model["metadata"]["slab_story"] = "above"
        self.assertEqual(by_id(plan_of(model)["slabs"], "D1")[0]["level_id"], "L_EG")

    def test_slab_that_does_not_follow_the_envelope_keeps_its_boundary(self):
        model = two_story_model()
        model["slabs"].append({"id": "TER", "level_id": "L_EG", "boundary": [[12, 0], [15, 0], [15, 3], [12, 3]], "thickness": 0.2,
                               "top_elevation": -0.15})
        plan = plan_of(model)
        ter = by_id(plan["slabs"], "TER")[0]
        self.assertEqual(ring_of(ter["payload"]["polygonCoordinates"]), [(12, 0), (15, 0), (15, 3), (12, 3)])
        self.assertTrue(any("TER" in w for w in plan["warnings"]))

    def test_slab_top_that_contradicts_the_datum_warns(self):
        model = two_story_model()
        model["slabs"][0]["top_elevation"] = 0.0
        self.assertTrue(any("BP" in w and "OKFF" in w for w in plan_of(model)["warnings"]))

    def test_slab_semantics_and_favorites(self):
        s = self.slabs
        self.assertEqual(s["BP"]["semantics"], {"classification": "ELEMENTE > Fundament > Bodenplatte / Flachgründung", "load_bearing": True,
                                                "position": "exterior", "layer": "20 Decke"})
        self.assertEqual(s["BP"]["payload"]["favoriteName"], "Bodenplatte WU 30 cm")
        self.assertEqual((s["D1"]["semantics"]["classification"], s["D1"]["semantics"]["position"]), ("ELEMENTE > Decke > Rohbaudecke", "interior"))
        self.assertEqual((s["DA"]["semantics"]["classification"], s["DA"]["semantics"]["layer"]),
                         ("ELEMENTE > Dach > Dachkonstruktion", "30 Dachkonstruktion massiv"))


class ZoneTest(unittest.TestCase):
    def setUp(self):
        self.plan = plan_of(two_story_model())
        self.zones = {r["model_id"]: r for r in self.plan["zones"]}

    def test_zone_is_associative_and_never_falls_back_to_a_polygon(self):
        r1 = self.zones["R1"]
        self.assertIn("referencePosition", r1["payload"]["geometry"])
        self.assertIsNone(r1["fallback_geometry"])
        self.assertEqual(r1["semantics"]["classification"], "ELEMENTE > Raum")
        self.assertEqual(r1["semantics"]["layer"], "80 Raum")
        allowed = plan_of(two_story_model(), allow_manual_zones=True)["zones"][0]
        self.assertIn("polygonCoordinates", allowed["fallback_geometry"])

    def test_zone_carries_floor_thickness_and_ends_under_the_slab(self):
        # guideline p.7 variant 01: OK Rohdecke to UK Rohdecke, floor build-up thickness in the zone
        self.assertEqual(self.zones["R1"]["zone_properties"], {"floor_thickness": 0.15, "top_offset": -0.35})
        self.assertEqual(self.zones["R2"]["zone_properties"], {"floor_thickness": 0.15, "clear_height": 2.65})

    def test_template_zone_base_is_checked_against_the_rule(self):
        self.assertFalse(any("zone base" in w for w in self.plan["warnings"]))
        model = two_story_model()
        model["metadata"].update(level_datum="OKRD")
        for slab, top in zip(model["slabs"], (0.0, 3.0, 6.0)):
            slab["top_elevation"] = top
        self.assertTrue(any("zone base" in w for w in plan_of(model)["warnings"]))

    def test_seed_point_lies_inside_a_concave_room(self):
        l_shape = [[20, 0], [24, 0], [24, 1], [21, 1], [21, 4], [20, 4]]
        plan = plan_of(two_story_model(spaces=[{"id": "RL", "level_id": "L_EG", "name": "Flur", "boundary": l_shape}]))
        seed = plan["zones"][0]["payload"]["geometry"]["referencePosition"]
        self.assertTrue(bfm.mr.point_in_polygon((seed["x"], seed["y"]), l_shape))
        self.assertEqual(plan["zones"][0]["payload"]["numberStr"], "RL")

    def test_floor_buildup_is_planned_per_room(self):
        model = two_story_model()
        model["spaces"][0]["floor_finish"] = "Fliesen"
        plan = plan_of(model)
        b = {r["model_id"]: r for r in plan["buildups"]}
        self.assertEqual(set(b), {"R1", "R2"})
        self.assertEqual(b["R1"]["payload"]["favoriteName"], "Boden+Fliesen 15 cm")
        self.assertEqual(b["R2"]["payload"]["favoriteName"], "Boden 15 cm")
        self.assertAlmostEqual(b["R1"]["payload"]["level"], 0.0)
        self.assertAlmostEqual(b["R2"]["payload"]["level"], 3.0)
        self.assertAlmostEqual(b["R1"]["payload"]["thickness"], 0.15)
        self.assertEqual(b["R1"]["semantics"], {"classification": "ELEMENTE > Bekleidung / Belag > Fußbodenaufbau", "load_bearing": False,
                                                "position": "interior", "layer": "20 Bodenaufbau"})
        self.assertEqual(b["R1"]["zone_key"], "R1")

    def test_buildup_thinner_than_its_favorite_warns(self):
        model = two_story_model()
        model["spaces"][0]["floor_buildup"] = 0.10
        self.assertTrue(any("R1" in w and "0.150" in w for w in plan_of(model)["warnings"]))


class SemanticsTest(unittest.TestCase):
    def test_every_planned_element_carries_classification_and_properties(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0), window("IW", 5.0, kind="door")]))
        for key in ("walls", "slabs", "windows", "doors", "zones", "buildups"):
            for rec in plan[key]:
                self.assertTrue(rec["semantics"]["classification"], (key, rec["key"]))
                self.assertIn("load_bearing", rec["semantics"])
                self.assertIn("position", rec["semantics"])

    def test_exterior_wall_semantics_and_favorite(self):
        w1 = by_id(plan_of(two_story_model())["walls"], "W1")[0]
        self.assertEqual(w1["semantics"], {"classification": "ELEMENTE > Wand", "load_bearing": True, "position": "exterior",
                                           "layer": "10 Wand außen"})
        self.assertEqual(w1["payload"]["favoriteName"], "KS + WDVS 42 cm")  # a wall favorite carries the composite's name

    def test_interior_wall_without_load_bearing_value_is_not_guessed(self):
        model = two_story_model()
        del model["walls"][-1]["is_load_bearing"]
        plan = plan_of(model)
        iw = by_id(plan["walls"], "IW")[0]
        self.assertIsNone(iw["semantics"]["load_bearing"])
        self.assertEqual(iw["semantics"]["layer"], "10 Wand innen")
        self.assertNotIn("favoriteName", iw["payload"])
        self.assertTrue(any("IW" in w and "load" in w for w in plan["warnings"]))

    def test_load_bearing_interior_wall_goes_to_its_layer(self):
        model = two_story_model()
        model["walls"][-1]["is_load_bearing"] = True
        self.assertEqual(by_id(plan_of(model)["walls"], "IW")[0]["semantics"]["layer"], "10 Wand innen tragend")

    def test_opening_position_follows_its_host_wall(self):
        plan = plan_of(two_story_model(openings=[window("W1", 2.0), window("IW", 5.0, kind="door")]))
        self.assertEqual(plan["windows"][0]["semantics"]["position"], "exterior")
        self.assertEqual(plan["doors"][0]["semantics"]["position"], "interior")
        self.assertEqual(plan["doors"][0]["semantics"]["classification"], "ELEMENTE > Tür / Tor > Tür")


if __name__ == "__main__":
    unittest.main()
