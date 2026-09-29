"""Shared test data: an office catalog shaped like fetch_office() returns it, and small model builders.

The office values mirror a German Archicad 28 office template read live on 2026-09-29 (composites with
skins, layer names, favorites, classification paths, built-in property GUIDs).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "test_house.json"

KS_WDVS = [{"type": "Finish", "thickness": 0.01, "material": "Kunstharzputz"}, {"type": "Other", "thickness": 0.16, "material": "XPS"},
           {"type": "Core", "thickness": 0.24, "material": "Kalksandstein"}, {"type": "Finish", "thickness": 0.01, "material": "Gipsputz"}]
KS_115 = [{"type": "Finish", "thickness": 0.01, "material": "Gipsputz"}, {"type": "Core", "thickness": 0.115, "material": "Kalksandstein"},
          {"type": "Finish", "thickness": 0.01, "material": "Gipsputz"}]
KS_24 = [{"type": "Finish", "thickness": 0.01, "material": "Gipsputz"}, {"type": "Core", "thickness": 0.24, "material": "Kalksandstein"},
         {"type": "Finish", "thickness": 0.01, "material": "Gipsputz"}]
ESTRICH = [{"type": "Other", "thickness": 0.065, "material": "Estrich"}, {"type": "Other", "thickness": 0.085, "material": "Trittschalldämmung"}]
FLIESEN = [{"type": "Other", "thickness": 0.015, "material": "Fliesen anthrazit"}, {"type": "Other", "thickness": 0.065, "material": "Estrich"},
           {"type": "Other", "thickness": 0.07, "material": "Trittschalldämmung"}]

PATHS = [
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
]
LAYERS = ["10 Wand außen", "10 Wand innen tragend", "30 Dachkonstruktion massiv", "20 Decke", "10 Stütze", "80 Raum", "20 Träger",
          "20 Fundament", "10 Wand innen", "30 Dachaufbau", "40 Absturzsicherung", "20 Bodenaufbau", "20 Decke abgehängt",
          "20 Unterdämmung", "30 Dachstuhl", "80 BGF BRI", "70 Lüftung Installation"]

OFFICE = {
    "tapir": "1.5.9",
    "project": "untitled",
    "stories": [{"index": -1, "level": -3.0, "name": "UG"}, {"index": 0, "level": 0.0, "name": "EG"}, {"index": 1, "level": 3.0, "name": "OG"}],
    "story_items": {"-1": "NAV-UG", "0": "NAV-EG", "1": "NAV-OG"},
    "act_story": 0,
    "composites": {
        "KS + WDVS 42 cm": {"guid": "C-AW", "skins": KS_WDVS},
        "KS 11,5 cm beidseitig Gipsputz": {"guid": "C-IW", "skins": KS_115},
        "KS 24 cm beidseitig Gipsputz": {"guid": "C-IW24", "skins": KS_24},
        "Estrich 15 cm": {"guid": "C-EST", "skins": ESTRICH},
        "Estrich + Fliesen 15 cm": {"guid": "C-FL", "skins": FLIESEN},
        "Unterdach mit Dämmung 21,5 cm": {"guid": "C-UD", "skins": [{"type": "Core", "thickness": 0.16, "material": "Mineralwolle 3"},
                                                                    {"type": "Other", "thickness": 0.03, "material": "Mineralwolle 3"},
                                                                    {"type": "Finish", "thickness": 0.025, "material": "Gipsputz"}]},
        "Oberdach ohne Sparren 8,5 cm": {"guid": "C-OD", "skins": [{"type": "Other", "thickness": 0.025, "material": "Mineralwolle 3"},
                                                                   {"type": "Other", "thickness": 0.06, "material": "Mineralwolle 3"}]},
        "Abgehängte Decke 40 cm": {"guid": "C-AD", "skins": [{"type": "Other", "thickness": 0.375, "material": "Mineralwolle 3"},
                                                             {"type": "Other", "thickness": 0.025, "material": "Gipsputz"}]},
        "Holzrahmen abgehängt 35,5 cm": {"guid": "C-HR", "skins": [{"type": "Other", "thickness": 0.3295, "material": "Mineralwolle 3"},
                                                                   {"type": "Other", "thickness": 0.025, "material": "Gipsputz"}]},
    },
    "materials": {"Stahlbeton": {"guid": "M-STB", "priority": 670}, "WU-Beton": {"guid": "M-WU", "priority": 690},
                  "Kalksandstein": {"guid": "M-KS", "priority": 635}, "Gipsputz": {"guid": "M-GP", "priority": 360},
                  "XPS": {"guid": "M-XPS", "priority": 730}, "Mineralwolle 3": {"guid": "M-MW", "priority": 740},
                  "EPS 1": {"guid": "M-EPS", "priority": 750}, "Stahl verzinkt": {"guid": "M-ST", "priority": 900},
                  "Haustechnikbereich": {"guid": "M-HT", "priority": 100}},
    "layers": {name: {"index": i + 2, "hidden": False} for i, name in enumerate(LAYERS)},
    "favorites": {"Wall": ["KS + WDVS 42 cm", "KS 11,5 cm zweiseitig Gipsputz", "KS 24 cm", "GK Installationswand"],
                  "Slab": ["Boden 15 cm", "Rohdecke Stb 20 cm", "Boden+Fliesen 15 cm", "Boden+Parkett 15 cm", "Bodenplatte WU 30 cm"],
                  "Zone": ["Raum Wohnen", "Raum Büro"], "Window": ["F 1 1,26x1,51", "F 1 bodentief, 1,26x2,41"],
                  "Door": ["T Eingang 1Fl 1,01x2,135", "T Innen 1Fl 88,5x2,01"], "Column": ["Stütze Stb 50x50"], "Beam": [],
                  "Morph": ["BRI R", "BRI S"], "Roof": ["Oberdach 8,5cm", "Unterdach+Dämmung 21,5cm"]},
    "favorite_slabs": {"Boden 15 cm": "Estrich 15 cm", "Boden+Fliesen 15 cm": "Estrich + Fliesen 15 cm"},
    "classification": {"system": {"guid": "SYS", "name": "Archicad Klassifizierung 28"}, "items": {p: f"CL-{i}" for i, p in enumerate(PATHS)}},
    "properties": {"load_bearing": "P-TRAG", "position": "P-LAGE", "floor_thickness": "P-FB", "top_offset": "P-ABST",
                   "top_story": "P-REL", "clear_height": "P-LICHT", "din277": "P-DIN", "opening_sill": "P-OSILL",
                   "din277_area": "P-FLAECHE"},
    "zone_categories": {"Wohnen und Aufenthalt": "ZC-5", "Büroarbeit": "ZC-4"},
    "zone_defaults": {"base_offset": -0.15},
    "north": 1.5707963267948966,
}

MATERIAL_MAP = {"AW": "KS + WDVS 42 cm", "IW": "KS 11,5 cm beidseitig Gipsputz", "IW24": "KS 24 cm beidseitig Gipsputz"}

CCW = [(0, 0), (10, 0), (10, 8), (0, 8)]
CW = [(0, 0), (0, 8), (10, 8), (10, 0)]


def office(**changes):
    data = copy.deepcopy(OFFICE)
    data.update(changes)
    return data


def fixture_model():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def ring_walls(points, level="L_EG", prefix="W", material="AW", thickness=0.42, **extra):
    walls = []
    for i in range(len(points)):
        wall = {"id": f"{prefix}{i + 1}", "level_id": level, "baseline": [list(points[i]), list(points[(i + 1) % len(points)])],
                "representation": "outer_face", "thickness": thickness, "material": material}
        wall.update(extra)
        walls.append(wall)
    return walls


def window(host, offset, **extra):
    item = {"id": f"O_{host}_{offset}", "host_wall_id": host, "kind": "window", "offset_along_wall": offset,
            "width": 1.26, "height": 1.51, "sill_height": 0.9}
    item.update(extra)
    return item


def two_story_model(**parts):
    """OKFF datum, 15 cm floor build-up, 20 cm slabs: the office template convention (live 29.09.2026)."""
    model = {
        "metadata": {"project_name": "test", "units": "m", "source_sheets": [], "level_datum": "OKFF", "floor_buildup": 0.15},
        "evidence": [], "assumptions": [], "missing_information": [],
        "levels": [{"id": "L_EG", "name": "EG", "elevation": 0.0}, {"id": "L_OG", "name": "OG", "elevation": 3.0}],
        "walls": ring_walls(CCW, "L_EG", "W") + ring_walls(CCW, "L_OG", "V") +
        [{"id": "IW", "level_id": "L_EG", "baseline": [[5, 0], [5, 8]], "representation": "centerline", "thickness": 0.135,
          "material": "IW", "is_load_bearing": False}],
        "openings": [],
        "slabs": [{"id": "BP", "level_id": "L_EG", "boundary": [list(p) for p in CCW], "thickness": 0.30, "top_elevation": -0.15},
                  {"id": "D1", "level_id": "L_OG", "boundary": [list(p) for p in CCW], "thickness": 0.20, "top_elevation": 2.85},
                  {"id": "DA", "level_id": "L_OG", "boundary": [list(p) for p in CCW], "thickness": 0.20, "top_elevation": 5.85}],
        "spaces": [{"id": "R1", "level_id": "L_EG", "name": "Wohnen", "number": "0.01",
                    "boundary": [[0.42, 0.42], [4.9325, 0.42], [4.9325, 7.58], [0.42, 7.58]]},
                   {"id": "R2", "level_id": "L_OG", "name": "Schlafen", "number": "1.01",
                    "boundary": [[0.42, 0.42], [9.58, 0.42], [9.58, 7.58], [0.42, 7.58]]}],
    }
    model.update(parts)
    return model


def by_id(records, model_id):
    return [r for r in records if r["model_id"] == model_id]
