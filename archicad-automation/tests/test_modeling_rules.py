"""Tests for scripts/modeling_rules.py — the fixed rules as data and the pure geometry behind them.

Run from the skill folder:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import modeling_rules as mr  # noqa: E402

# Skins as GetComposites returns them for the office composite "KS + WDVS 42 cm" (live 29.09.2026):
# the first skin is the exterior face.
KS_WDVS = [{"type": "Finish", "thickness": 0.01}, {"type": "Other", "thickness": 0.16},
           {"type": "Core", "thickness": 0.24}, {"type": "Finish", "thickness": 0.01}]
FLOOR_BUILDUP = [{"type": "Other", "thickness": 0.015}, {"type": "Other", "thickness": 0.065}, {"type": "Other", "thickness": 0.07}]

# Classification paths that exist in "Archicad Klassifizierung 28" of the office template (live inventory 29.09.2026)
KNOWN_PATHS = {
    "ELEMENTE > Wand", "ELEMENTE > Wand > Vorwand / Installationswand", "ELEMENTE > Geländer",
    "ELEMENTE > Fundament > Streifenfundament", "ELEMENTE > Fundament > Bodenplatte / Flachgründung",
    "ELEMENTE > Fundament > Punktfundament", "ELEMENTE > Decke > Rohbaudecke", "ELEMENTE > Dach > Dachkonstruktion",
    "ELEMENTE > Dach", "ELEMENTE > Bekleidung / Belag", "ELEMENTE > Bekleidung / Belag > Fußbodenaufbau",
    "ELEMENTE > Bekleidung / Belag > Dämmung", "ELEMENTE > Bekleidung / Belag > Abgehängte Decke / Deckenbekleidung",
    "ELEMENTE > Bekleidung / Belag > Dachdeckung", "ELEMENTE > Fenster / Dachfenster / Lichtkuppel > Fenster",
    "ELEMENTE > Tür / Tor > Tür", "ELEMENTE > Durchbrüche / Schlitze > Öffnung", "ELEMENTE > Durchbrüche / Schlitze > Nische",
    "ELEMENTE > Raum", "ELEMENTE > Raum > Raumvorschlag", "ELEMENTE > Stütze / Pfeiler > Stütze",
    "ELEMENTE > Träger / Balken / Unterzug > Unterzug", "ELEMENTE > Träger / Balken / Unterzug > Sturz",
    "ELEMENTE > Bauelement - beliebig",
}


class CompositeTest(unittest.TestCase):
    def test_core_outside_offset_is_the_thickness_in_front_of_the_core(self):
        self.assertAlmostEqual(mr.core_outside_offset(KS_WDVS), 0.17)
        self.assertAlmostEqual(mr.core_thickness(KS_WDVS), 0.24)
        self.assertAlmostEqual(mr.total_thickness(KS_WDVS), 0.42)

    def test_basic_structure_has_no_offset(self):
        self.assertEqual(mr.core_outside_offset([]), 0.0)
        self.assertEqual(mr.core_outside_offset(None), 0.0)

    def test_composite_without_core_is_recognised(self):
        # floor build-ups must be multi-skin WITHOUT a core (guideline p.12)
        self.assertFalse(mr.has_core(FLOOR_BUILDUP))
        self.assertTrue(mr.has_core(KS_WDVS))


class GeometryTest(unittest.TestCase):
    def test_counter_clockwise_ring_is_offset_inward_per_edge(self):
        ring = [(0, 0), (10, 0), (10, 8), (0, 8)]
        out = mr.offset_ring(ring, [0.17] * 4)
        expected = [(0.17, 0.17), (9.83, 0.17), (9.83, 7.83), (0.17, 7.83)]
        for (x, y), (ex, ey) in zip(out, expected):
            self.assertAlmostEqual(x, ex)
            self.assertAlmostEqual(y, ey)

    def test_edges_with_different_offsets_meet_in_their_intersection(self):
        ring = [(0, 0), (10, 0), (10, 8), (0, 8)]
        out = mr.offset_ring(ring, [0.1, 0.2, 0.1, 0.2])
        self.assertAlmostEqual(out[0][0], 0.2)
        self.assertAlmostEqual(out[0][1], 0.1)
        self.assertAlmostEqual(out[2][0], 9.8)
        self.assertAlmostEqual(out[2][1], 7.9)

    def test_collinear_edges_keep_a_straight_offset(self):
        ring = [(0, 0), (5, 0), (10, 0), (10, 8), (0, 8)]
        out = mr.offset_ring(ring, [0.17] * 5)
        self.assertAlmostEqual(out[1][0], 5.0)
        self.assertAlmostEqual(out[1][1], 0.17)

    def test_polygon_area_is_signed_by_orientation(self):
        self.assertAlmostEqual(mr.signed_area([(0, 0), (4, 0), (4, 3), (0, 3)]), 12.0)
        self.assertAlmostEqual(mr.signed_area([(0, 0), (0, 3), (4, 3), (4, 0)]), -12.0)

    def test_line_intersection(self):
        p = mr.line_intersection((0, 1), (1, 0), (5, -3), (0, 1))
        self.assertAlmostEqual(p[0], 5.0)
        self.assertAlmostEqual(p[1], 1.0)
        self.assertIsNone(mr.line_intersection((0, 0), (1, 0), (0, 1), (2, 0)))


class RoleTableTest(unittest.TestCase):
    def test_every_role_uses_an_existing_classification(self):
        for name, role in mr.ROLES.items():
            if role.classification:
                self.assertIn(role.classification, KNOWN_PATHS, name)

    def test_guideline_values_of_the_main_roles(self):
        # guideline pages 8-13, 20, 28-31
        r = mr.ROLES
        self.assertEqual((r["exterior_wall"].classification, r["exterior_wall"].load_bearing, r["exterior_wall"].position),
                         ("ELEMENTE > Wand", True, "exterior"))
        self.assertEqual((r["floor_slab"].classification, r["floor_slab"].load_bearing, r["floor_slab"].position),
                         ("ELEMENTE > Decke > Rohbaudecke", True, "interior"))
        self.assertEqual((r["ground_slab"].load_bearing, r["ground_slab"].position), (True, "exterior"))
        self.assertEqual((r["roof_slab"].classification, r["roof_slab"].position), ("ELEMENTE > Dach > Dachkonstruktion", "exterior"))
        self.assertEqual((r["floor_buildup"].classification, r["floor_buildup"].load_bearing),
                         ("ELEMENTE > Bekleidung / Belag > Fußbodenaufbau", False))
        self.assertEqual((r["window"].load_bearing, r["window"].position), (False, "host"))
        self.assertEqual(r["space"].classification, "ELEMENTE > Raum")
        self.assertEqual((r["railing"].tool, r["railing"].classification), ("Wall", "ELEMENTE > Geländer"))
        self.assertEqual(r["slab_opening"].position, "interior")

    def test_interior_wall_load_bearing_comes_from_the_model(self):
        # guideline p.20: variant 02 may be load-bearing or not; the script must not guess
        role = mr.ROLES["interior_wall"]
        self.assertTrue(role.from_model)
        self.assertIsNone(role.load_bearing)

    def test_property_values_are_language_neutral(self):
        # Tapir writes display values with umlauts wrongly (live 29.09.2026); the official API takes these
        self.assertEqual(mr.LOAD_BEARING_VALUE[True], "LoadBearingElement")
        self.assertEqual(mr.LOAD_BEARING_VALUE[False], "NonLoadBearingElement")
        self.assertEqual(mr.LOAD_BEARING_VALUE[None], "Undefined")
        self.assertEqual(mr.POSITION_VALUE["exterior"], "Exterior")
        self.assertEqual(mr.POSITION_VALUE["interior"], "Interior")

    def test_office_profile_layer_for_interior_walls_depends_on_load_bearing(self):
        self.assertEqual(mr.layer_for("interior_wall", True, mr.OFFICE_PROFILE), "10 Wand innen tragend")
        self.assertEqual(mr.layer_for("interior_wall", False, mr.OFFICE_PROFILE), "10 Wand innen")
        self.assertEqual(mr.layer_for("exterior_wall", True, mr.OFFICE_PROFILE), "10 Wand außen")
        self.assertIsNone(mr.layer_for("window", False, mr.OFFICE_PROFILE))


if __name__ == "__main__":
    unittest.main()
