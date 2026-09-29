"""Fixed modelling rules as data, plus the pure geometry they need.

Sources: Graphisoft Deutschland, "BIM-Modellierungsrichtlinien Archicad 29" (09.03.2026, CC BY-NC-SA 4.0; page
numbers below) and the office experience in references/. The catalog with sources, checks and status is
references/modeling-rule-catalog.md; keep both in step.

Two layers on purpose:
- ROLES holds what the guideline fixes for every building part (tool, classification, load-bearing, position).
  These do not change between offices.
- OFFICE_PROFILE holds what the office template decides (layer names, favorites, default floor build-up). It was
  read from a German Archicad 28 office template on 2026-09-29 and can be replaced with a JSON file (--office-profile).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

TOL = 1e-6


@dataclass(frozen=True)
class Role:
    tool: str                    # Archicad element type the script creates
    classification: str | None  # path of item ids in "Archicad Klassifizierung" (" > " joined)
    load_bearing: bool | None    # guideline value; None = "Nicht definiert"
    position: str | None         # "exterior", "interior", "host" (= host wall), "envelope" (= inside/outside the envelope), None
    from_model: bool = False     # a model value (is_load_bearing) overrides load_bearing
    pages: str = ""


ROLES: dict[str, Role] = {
    # walls
    "exterior_wall": Role("Wall", "ELEMENTE > Wand", True, "exterior", True, "8, 9, 12, 17-19"),
    "interior_wall": Role("Wall", "ELEMENTE > Wand", None, "interior", True, "20"),
    "parapet": Role("Wall", "ELEMENTE > Wand", True, "exterior", True, "29"),
    "railing": Role("Wall", "ELEMENTE > Geländer", False, "exterior", False, "13, 14"),
    "installation_wall": Role("Wall", "ELEMENTE > Wand > Vorwand / Installationswand", False, "interior", False, "22"),
    "strip_footing": Role("Wall", "ELEMENTE > Fundament > Streifenfundament", True, "exterior", False, "8"),
    # slabs
    "ground_slab": Role("Slab", "ELEMENTE > Fundament > Bodenplatte / Flachgründung", True, "exterior", False, "8, 9"),
    "floor_slab": Role("Slab", "ELEMENTE > Decke > Rohbaudecke", True, "interior", False, "12"),
    "roof_slab": Role("Slab", "ELEMENTE > Dach > Dachkonstruktion", True, "exterior", False, "28, 29"),
    "floor_buildup": Role("Slab", "ELEMENTE > Bekleidung / Belag > Fußbodenaufbau", False, "interior", False, "12, 20"),
    "ground_insulation": Role("Slab", "ELEMENTE > Bekleidung / Belag > Dämmung", False, "exterior", False, "9"),
    "roof_insulation": Role("Slab", "ELEMENTE > Bekleidung / Belag > Dämmung", False, "exterior", False, "28, 29"),
    "suspended_ceiling": Role("Slab", "ELEMENTE > Bekleidung / Belag > Abgehängte Decke / Deckenbekleidung", False, "interior", False, "15, 16"),
    # openings
    "window": Role("Window", "ELEMENTE > Fenster / Dachfenster / Lichtkuppel > Fenster", False, "host", False, "13, 31"),
    "door": Role("Door", "ELEMENTE > Tür / Tor > Tür", False, "host", False, "31"),
    "wall_opening": Role("Opening", "ELEMENTE > Durchbrüche / Schlitze > Öffnung", None, "interior", False, "31"),
    "wall_niche": Role("Opening", "ELEMENTE > Durchbrüche / Schlitze > Nische", None, "interior", False, "31"),
    "slab_opening": Role("Opening", "ELEMENTE > Durchbrüche / Schlitze > Öffnung", None, "interior", False, "30"),
    # rooms and bodies
    "space": Role("Zone", "ELEMENTE > Raum", None, None, False, "7"),
    "din277_body": Role("Morph", "ELEMENTE > Raum", None, None, False, "32"),
    "technical_zone": Role("Morph", "ELEMENTE > Raum > Raumvorschlag", False, "interior", False, "15, 22"),
    "site_area": Role("Morph", "ELEMENTE > Bauelement - beliebig", None, None, False, "33"),
    # columns and beams
    "column": Role("Column", "ELEMENTE > Stütze / Pfeiler > Stütze", True, "envelope", False, "11"),
    "pad_footing": Role("Column", "ELEMENTE > Fundament > Punktfundament", True, "exterior", False, "10"),
    "downstand_beam": Role("Beam", "ELEMENTE > Träger / Balken / Unterzug > Unterzug", True, "envelope", False, "11"),
    "lintel": Role("Beam", "ELEMENTE > Träger / Balken / Unterzug > Sturz", True, "exterior", False, "13"),
    "balcony": Role("Beam", "ELEMENTE > Decke > Rohbaudecke", True, "exterior", False, "14"),
    "thermal_break": Role("Beam", "ELEMENTE > Bekleidung / Belag > Dämmung", True, "exterior", False, "14"),
    "insulation_strip": Role("Beam", "ELEMENTE > Bekleidung / Belag > Dämmung", False, "exterior", False, "8, 9, 17-19"),
    "parapet_cover": Role("Beam", "ELEMENTE > Bekleidung / Belag", False, "exterior", False, "29"),
    "ring_beam": Role("Beam", "ELEMENTE > Dach", True, "exterior", False, "23-26"),
    # roofs
    "roof_structure": Role("Roof", "ELEMENTE > Dach", True, "exterior", False, "23-27"),
    "roof_covering": Role("Roof", "ELEMENTE > Bekleidung / Belag > Dachdeckung", False, "exterior", False, "23-27"),
}

# non-localised enum values of the built-in category properties (language-neutral; set through API.SetPropertyValuesOfElements)
LOAD_BEARING_VALUE = {True: "LoadBearingElement", False: "NonLoadBearingElement", None: "Undefined"}
POSITION_VALUE = {"exterior": "Exterior", "interior": "Interior", None: "Undefined"}

# Example office profile, read live from a German Archicad 28 template on 2026-09-29 (favorites, layers, zone
# defaults). Replace with --office-profile.
OFFICE_PROFILE: dict[str, Any] = {
    "name": "Example office template (AC28 GER, verified 2026-09-29)",
    "classification_system": "Archicad Klassifizierung",
    "floor_buildup": 0.15,
    "zone_base_offset": -0.15,   # zone bottom relative to the story, fixed by the template (not settable through Tapir)
    "din277_display": "OutLinesOnly",  # what the office favorite "BRI R" sets: bodies do not cover the floor plan
    "layers": {
        "exterior_wall": "10 Wand außen",
        "interior_wall": {"load_bearing": "10 Wand innen tragend", "default": "10 Wand innen"},
        "parapet": "10 Wand außen",
        "railing": "40 Absturzsicherung",
        "installation_wall": "10 Wand innen",
        "strip_footing": "20 Fundament",
        "ground_slab": "20 Decke",
        "floor_slab": "20 Decke",
        "roof_slab": "30 Dachkonstruktion massiv",
        "floor_buildup": "20 Bodenaufbau",
        "ground_insulation": "20 Unterdämmung",
        "roof_insulation": "30 Dachaufbau",
        "suspended_ceiling": "20 Decke abgehängt",
        "space": "80 Raum",
        "din277_body": "80 BGF BRI",
        "site_area": "80 BGF BRI",
        "technical_zone": "70 Lüftung Installation",   # as the office favorite "Haustechnik-Bereiche" (live 29.09.2026)
        "column": "10 Stütze",
        "pad_footing": "20 Fundament",
        "downstand_beam": "20 Träger",
        "lintel": "20 Träger",
        "balcony": "20 Decke",
        "thermal_break": "20 Träger",
        "insulation_strip": "20 Unterdämmung",
        "parapet_cover": "30 Dachaufbau",
        "ring_beam": "30 Dachstuhl",
        "roof_structure": "30 Dachstuhl",
        "roof_covering": "30 Dachaufbau",
    },
    "favorites": {
        "ground_slab": "Bodenplatte WU 30 cm",
        "floor_slab": "Rohdecke Stb 20 cm",
        "roof_slab": "Rohdecke Stb 20 cm",
        "floor_buildup": "Boden 15 cm",
    },
    # Favorites are only used where a create command takes favoriteName. Applied afterwards (ApplyFavoritesToElements) they
    # moved an upper-story morph by -3.00 m and a roof covering by +0.04 m (live 29.09.2026): roofs and DIN 277 bodies get
    # composite, layer and display explicitly (the office favorite "BRI R" shows bodies as outlines only).
    "floor_finish_favorites": {"Estrich": "Boden 15 cm", "Fliesen": "Boden+Fliesen 15 cm", "Parkett": "Boden+Parkett 15 cm",
                               "Teppich": "Boden+Teppich 15 cm"},
    "morph_materials": {"technical_zone": "Haustechnikbereich"},
    # building material of the raw-slab favorites (probed live 29.09.2026), for the priority check C8
    "favorite_materials": {"Rohdecke Stb 20 cm": "Stahlbeton", "Bodenplatte WU 30 cm": "WU-Beton"},
    # composite each slab favorite brings (probed live 29.09.2026; favorites are not readable through the API)
    "favorite_composites": {"Boden 15 cm": "Estrich 15 cm", "Boden+Fliesen 15 cm": "Estrich + Fliesen 15 cm",
                            "Boden+Parkett 15 cm": "Estrich + Parkett 15 cm", "Boden+Teppich 15 cm": "Estrich + Teppich 15 cm"},
    "composites": {"suspended_ceiling": "Abgehängte Decke 40 cm", "roof_structure": "Unterdach mit Dämmung 21,5 cm",
                   "roof_covering": "Oberdach ohne Sparren 8,5 cm"},
}


def layer_for(role: str, load_bearing: bool | None, profile: dict[str, Any]) -> str | None:
    entry = (profile.get("layers") or {}).get(role)
    if isinstance(entry, dict):
        return entry["load_bearing"] if load_bearing else entry["default"]
    return entry


# --- composites --------------------------------------------------------------------------

def _skins(skins: list[dict] | None) -> list[dict]:
    return list(skins or [])


def has_core(skins: list[dict] | None) -> bool:
    return any(s.get("type") == "Core" or s.get("isCore") for s in _skins(skins))


def core_outside_offset(skins: list[dict] | None) -> float:
    """Thickness in front of the first core skin; the first skin is the exterior face (live 29.09.2026)."""
    total = 0.0
    for s in _skins(skins):
        if s.get("type") == "Core" or s.get("isCore"):
            return round(total, 6)
        total += float(s.get("thickness", 0.0))
    return 0.0


def core_thickness(skins: list[dict] | None) -> float:
    return round(sum(float(s.get("thickness", 0.0)) for s in _skins(skins) if s.get("type") == "Core" or s.get("isCore")), 6)


def total_thickness(skins: list[dict] | None) -> float:
    return round(sum(float(s.get("thickness", 0.0)) for s in _skins(skins)), 6)


# --- geometry ----------------------------------------------------------------------------

def signed_area(poly: list[Any]) -> float:
    n = len(poly)
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))


def unit(a: Any, b: Any) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    return (dx / length, dy / length) if length > TOL else (0.0, 0.0)


def left_normal(u: tuple[float, float]) -> tuple[float, float]:
    return -u[1], u[0]


def line_intersection(p: Any, d: Any, q: Any, e: Any) -> tuple[float, float] | None:
    """Intersection of the lines p + s*d and q + t*e; None when they are parallel."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    s = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return p[0] + s * d[0], p[1] + s * d[1]


def offset_ring(ring: list[Any], distances: list[float]) -> list[tuple[float, float]]:
    """Move every edge of a counter-clockwise ring inward by its own distance; vertices are the new intersections.

    Edge i runs from ring[i] to ring[i+1]; the result keeps the vertex order (vertex i starts edge i).
    """
    n = len(ring)
    lines = []
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        u = unit(a, b)
        nx, ny = left_normal(u)
        lines.append(((a[0] + distances[i] * nx, a[1] + distances[i] * ny), u))
    out = []
    for i in range(n):
        (p, d), (q, e) = lines[i - 1], lines[i]
        hit = line_intersection(p, d, q, e)
        if hit is None:  # collinear neighbours: keep the vertex on the offset line of edge i
            nx, ny = left_normal(e)
            hit = (ring[i][0] + distances[i] * nx, ring[i][1] + distances[i] * ny)
        out.append((round(hit[0], 9), round(hit[1], 9)))
    return out


def point_in_polygon(point: Any, polygon: list[Any]) -> bool:
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        (x1, y1), (x2, y2) = polygon[i], polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside
