#!/usr/bin/env python3
"""Build an intermediate building model in Archicad through Tapir, under fixed modelling rules.

Input is the JSON model of `abstracting-building-models` (check it with that skill's validate_model.py first). On
the way the fixed rules of Graphisoft Germany's "BIM-Modellierungsrichtlinien Archicad 29" and live-verified
Archicad experience are applied
(references/modeling-rule-catalog.md; rule data in modeling_rules.py): every part is classified and carries
"Tragende Funktion" and "Lage" and sits on its office layer; exterior walls reference the outer face of their core
and run from raw slab to raw slab; raw slabs stop at the walls; floor build-ups are separate slabs per room; rooms
are associative (inner edge) with floor thickness and a top under the slab. Afterwards every rule is read back.

Usage:
  python scripts/build_from_model.py model.json --dry-run [--port 19723] [--plan-out plan.json]
  python scripts/build_from_model.py model.json --port 19723 --confirm [--guid-map guids.json] [--report-out report.json]

A dry run with --port reads the office catalog (composites, favorites, layers, classification, properties) from the
open project with read-only commands, so the plan is complete; without --port core offsets and favorites stay open.

Options: --material-map map.json   model material name -> Archicad composite or building material
         --window-favorite / --door-favorite NAME   default office favorites for openings
         --office-profile profile.json   layer and favorite names of another office template (default: modeling_rules.py)
         --allow-manual-zones   draw a room polygon when no wall ring closes (the rules forbid it; off by default)

Model fields beyond the schema that the builder reads (all optional; defaults in the catalog, part F):
  metadata.level_datum "OKFF"|"OKRD", metadata.slab_story "below"|"above", metadata.floor_buildup (m),
  metadata.sill_reference "OKFF"|"OKRD"; levels[].floor_buildup;
  walls[].role (exterior_wall, interior_wall, parapet, railing, installation_wall, strip_footing) / is_load_bearing /
    base "screed" / covering_thickness / top "height" / favorite;
  openings[].kind window|door|opening (niche is skipped) / favorite / swing / offset_reference;
  slabs[].role (ground_slab, floor_slab, roof_slab, ground_insulation, roof_insulation, suspended_ceiling) / favorite /
    material / extent "boundary" / openings [{id, center, width, depth}];
  spaces[].floor_buildup / floor_finish / floor_buildup_favorite / favorite / use / ceiling {type "suspended", material,
    thickness, variant "01"|"02"};
  columns[] {id, level_id, position, width, depth|diameter, role column|pad_footing, height, top_elevation, material, favorite};
  beams[] {id, level_id, baseline, width, height, role, top_elevation, host_wall_id (insulation_strip), material, favorite};
  roofs[] {id, level_id, kind pitched|flat, boundary, slope (deg), eave_elevation, overhang};
  technical_zones[] {id, level_id, boundary, bottom_elevation, top_elevation};
  site_areas[] {id, kind GF|AF|BF|UF, boundary, elevation}.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modeling_rules as mr  # noqa: E402

MIN_WALL_LENGTH = 0.2
TOL = 1e-3
BBOX_TOL = 0.01
Z_TOL = 0.011
MIN_TAPIR = (1, 5, 9)  # flipped/referenceLineLocation/top-link read-back, fields[] in GetDetailsOfElements
WALL_ROLES = ("exterior_wall", "interior_wall", "parapet", "railing", "installation_wall", "strip_footing")
SLAB_ROLES = ("ground_slab", "floor_slab", "roof_slab", "ground_insulation", "roof_insulation", "suspended_ceiling")
RAW_SLABS = ("ground_slab", "floor_slab")
OUTSIDE_REFERENCE = ("exterior_wall", "parapet")  # reference line on the outer face of the core (rule C1)
REFERENCE_LINE = {"outer_face": "Outside", "centerline": "Center", "inner_face": "Inside"}
INWARD = ("inward", "in", "nach innen", "innen")
OUTWARD = ("outward", "out", "nach außen", "nach aussen", "außen", "aussen")
# plan key, Archicad element type (for counts)
PLAN_TYPES = [("walls", "Wall"), ("slabs", "Slab"), ("windows", "Window"), ("doors", "Door"), ("zones", "Zone"), ("buildups", "Slab"),
              ("ceilings", "Slab"), ("openings", "Opening"), ("columns", "Column"), ("beams", "Beam"), ("roofs", "Roof"),
              ("morphs", "Morph")]
COUNT_TYPES = ("Wall", "Slab", "Window", "Door", "Zone", "Opening", "Column", "Beam", "Roof", "Morph")
COLUMN_ROLES = ("column", "pad_footing")
BEAM_ROLES = ("downstand_beam", "lintel", "balcony", "thermal_break", "insulation_strip", "parapet_cover", "ring_beam")
FOUNDATION_ROLES = ("strip_footing", "pad_footing")
# static built-in properties keep their GUID in every project and language
STATIC_PROPERTIES = {"floor_thickness": "9F8F2A12-A6ED-4D52-8830-BFFB7357B2CA", "clear_height": "09CEBC76-3990-494A-9F85-5B5DFD6B16FE",
                     "top_offset": "1606C1A4-A80B-4EA6-A179-0983C8120B46", "top_story": "6D644AF5-B050-446F-883E-DB89AB3365A9",
                     "opening_sill": "D851A129-5C6F-4E33-B790-35AE2C8BB9FF"}
READ_ONLY = ("Get", "API.Get", "API.IsAddOnCommandAvailable")

Send = Callable[[str, dict], dict]
_UNSET = object()


class BuildError(Exception):
    """A live run has to stop: nothing (further) may be sent to Archicad."""


class TapirError(BuildError):
    def __init__(self, code: Any, message: str):
        super().__init__(f"Tapir error {code}: {message}")
        self.code = code


# --- geometry ---------------------------------------------------------------------------

def pt(p: Any) -> dict[str, float]:
    return {"x": round(float(p[0]), 6), "y": round(float(p[1]), 6)}


def _xy(c: dict[str, float]) -> tuple[float, float]:
    return c["x"], c["y"]


def dist(a: Any, b: Any) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def point_segment_distance(p: Any, a: Any, b: Any) -> tuple[float, float]:
    """Distance from p to segment a-b and the position along it (0 at a, 1 at b)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy
    t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length2))
    return dist(p, (a[0] + t * dx, a[1] + t * dy)), t


def interior_point(polygon: list[tuple[float, float]]) -> tuple[float, float]:
    """A point inside the room: the centroid if it lies inside, else the middle of the widest scanline span."""
    area = mr.signed_area(polygon)
    n = len(polygon)
    if abs(area) > TOL:
        cx = sum((polygon[i][0] + polygon[(i + 1) % n][0]) *
                 (polygon[i][0] * polygon[(i + 1) % n][1] - polygon[(i + 1) % n][0] * polygon[i][1]) for i in range(n)) / (6 * area)
        cy = sum((polygon[i][1] + polygon[(i + 1) % n][1]) *
                 (polygon[i][0] * polygon[(i + 1) % n][1] - polygon[(i + 1) % n][0] * polygon[i][1]) for i in range(n)) / (6 * area)
    else:
        cx, cy = sum(p[0] for p in polygon) / n, sum(p[1] for p in polygon) / n
    if mr.point_in_polygon((cx, cy), polygon):
        return cx, cy
    ys = [p[1] for p in polygon]
    for y in [cy] + [min(ys) + f * (max(ys) - min(ys)) for f in (0.5, 0.25, 0.75, 0.1, 0.9)]:
        xs = sorted(polygon[i][0] + (y - polygon[i][1]) * (polygon[(i + 1) % n][0] - polygon[i][0]) /
                    (polygon[(i + 1) % n][1] - polygon[i][1])
                    for i in range(n) if (polygon[i][1] > y) != (polygon[(i + 1) % n][1] > y))
        spans = [(xs[k], xs[k + 1]) for k in range(0, len(xs) - 1, 2)]
        if spans:
            a, b = max(spans, key=lambda s: s[1] - s[0])
            if mr.point_in_polygon(((a + b) / 2, y), polygon):
                return (a + b) / 2, y
    return cx, cy


def _num(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


# --- planning ---------------------------------------------------------------------------

class _Context:
    def __init__(self, model: dict, office: dict | None, material_map: dict, profile: dict, plan: dict):
        self.model, self.office, self.material_map, self.profile, self.plan = model, office, material_map, profile, plan
        self.meta = model.get("metadata") or {}
        self.levels: dict[str, dict] = {}
        self.ordered: list[dict] = []
        self.slab_info: dict[str, dict] = {}
        self.roof: dict | None = None
        self.segments: dict[str, dict] = {}
        self.strip_hosts: set[str] = set()
        self.ground: dict | None = None
        self.slab_holes: list[tuple[str, list[tuple[float, float]]]] = []
        self._said: set[str] = set()

    def once(self, bucket: str, text: str) -> None:
        if text not in self._said:
            self._said.add(text)
            self.plan[bucket].append(text)

    def next_level(self, level: dict) -> dict | None:
        i = level["index"] + 1
        return self.ordered[i] if i < len(self.ordered) else None

    def prev_level(self, level: dict) -> dict | None:
        i = level["index"] - 1
        return self.ordered[i] if i >= 0 else None

    def okrd_above(self, level: dict) -> float | None:
        nxt = self.next_level(level)
        if nxt:
            return nxt["okrd"]
        return self.roof["top"] if self.roof else None

    def ukrd_above(self, level: dict) -> float | None:
        nxt = self.next_level(level)
        if nxt:
            if nxt["slab_thickness"] is None:
                self.once("warnings", f"level {nxt['id']}: no raw slab in the model; the underside above {level['id']} is taken at OK Rohdecke")
                return nxt["okrd"]
            return nxt["okrd"] - nxt["slab_thickness"]
        if self.roof:
            return self.roof["top"] - self.roof["thickness"]
        return None

    def favorites(self, kind: str) -> list[str] | None:
        return None if self.office is None else list((self.office.get("favorites") or {}).get(kind, []))


def _semantics(role: str, profile: dict, load_bearing: Any = _UNSET, position: str | None = None) -> dict:
    r = mr.ROLES[role]
    lb = r.load_bearing if load_bearing is _UNSET else load_bearing
    pos = position if position is not None else (r.position if r.position in ("exterior", "interior") else None)
    return {"classification": r.classification, "load_bearing": lb, "position": pos, "layer": mr.layer_for(role, lb, profile)}


def build_plan(model: dict[str, Any], office: dict | None = None, material_map: dict[str, str] | None = None,
               window_favorite: str | None = None, door_favorite: str | None = None, zones: str = "auto",
               allow_manual_zones: bool = False, profile: dict | None = None, din277: bool = False) -> dict[str, Any]:
    """Apply the fixed rules to the intermediate model and plan the Tapir payloads. Pure: sends nothing."""
    plan: dict[str, Any] = {"datum": {}, "levels": [], "walls": [], "slabs": [], "windows": [], "doors": [], "zones": [],
                            "buildups": [], "ceilings": [], "openings": [], "columns": [], "beams": [], "roofs": [], "morphs": [],
                            "loops": [], "skipped": [], "errors": [], "warnings": [], "notes": [],
                            "materials": [], "favorites": {}, "office_catalog": office is not None}
    ctx = _Context(model, office, material_map or {}, profile or mr.OFFICE_PROFILE, plan)
    if not _check_input(ctx):
        return plan
    if office is None:
        plan["warnings"].append("office catalog missing (dry run without --port): core offsets, composite thicknesses, favorites "
                                "and layers are unresolved; repeat the dry run with --port for the complete plan")
    _plan_levels(ctx)
    _classify_slabs(ctx)
    _plan_walls(ctx)
    _orient_exterior_loops(ctx)
    _apply_core_offsets(ctx)
    _snap_wall_ends(ctx)
    _check_junctions(plan)
    ctx.strip_hosts = {b.get("host_wall_id") for b in model.get("beams") or [] if b.get("role") == "insulation_strip"}
    _wall_heights(ctx)
    _plan_openings(ctx, window_favorite, door_favorite)
    _check_opening_junctions(plan)
    _plan_slabs(ctx)
    _plan_slab_openings(ctx)
    _plan_zones(ctx, zones, allow_manual_zones)
    _plan_buildups(ctx)
    _plan_ceilings(ctx)
    _plan_columns(ctx)
    _plan_beams(ctx)
    _plan_roofs(ctx)
    if din277:
        _plan_din277(ctx)
    _plan_technical_zones(ctx)
    _plan_site_areas(ctx)
    _check_foundation_stories(ctx)
    for item in model.get("stairs") or []:
        _skip(plan, item.get("id", "?"), "stair", "not built by build_from_model (create it separately)")
    plan["materials"] = sorted({w["material"] for w in plan["walls"] if w.get("material")})
    favs: dict[str, set] = {}
    for key in ("walls", "slabs", "windows", "doors", "zones", "buildups", "columns", "beams"):
        for rec in plan[key]:
            if rec["payload"].get("favoriteName"):
                favs.setdefault(key, set()).add(rec["payload"]["favoriteName"])
    plan["favorites"] = {k: sorted(v) for k, v in favs.items()}
    return plan


def _skip(plan: dict, item_id: Any, kind: str, reason: str) -> None:
    plan["skipped"].append({"id": item_id, "kind": kind, "reason": reason})


def _check_input(ctx: _Context) -> bool:
    units = ctx.meta.get("units", "m")
    if units != "m":
        ctx.plan["errors"].append(f"model units '{units}': the builder only builds metres; convert the model first (rule A1)")
        return False
    far = [p for w in ctx.model.get("walls") or [] for p in w.get("baseline") or [] if abs(p[0]) > 1000 or abs(p[1]) > 1000]
    if far:
        ctx.plan["warnings"].append("the model lies more than 1 km from the project origin; model near 0,0 (rule A2)")
    return True


def _slab_top(s: dict) -> float | None:
    top, bottom, t = _num(s.get("top_elevation")), _num(s.get("bottom_elevation")), _num(s.get("thickness"))
    if top is not None:
        return top
    if bottom is not None and t is not None:
        return bottom + t
    return None


def _plan_levels(ctx: _Context) -> None:
    plan, meta = ctx.plan, ctx.meta
    usable = []
    for lv in ctx.model.get("levels") or []:
        if _num(lv.get("elevation")) is not None:
            usable.append(lv)
        else:
            _skip(plan, lv.get("id"), "level", "elevation missing")
    usable.sort(key=lambda lv: lv["elevation"])
    b_meta = _num(meta.get("floor_buildup"))
    datum = str(meta.get("level_datum") or "").upper()
    if datum not in ("OKFF", "OKRD"):
        datum = _infer_datum(ctx, usable, b_meta)
    slab_story = str(meta.get("slab_story") or "below").lower()
    if slab_story not in ("below", "above"):
        plan["warnings"].append(f"metadata.slab_story '{slab_story}' unknown; 'below' used (Rohdecke unter Geschoss)")
        slab_story = "below"
    sill_ref = str(meta.get("sill_reference") or "OKFF").upper()
    plan["datum"] = {"level_datum": datum, "slab_story": slab_story, "sill_reference": sill_ref if sill_ref in ("OKFF", "OKRD") else "OKFF"}
    assumed = False
    for i, lv in enumerate(usable):
        b = _num(lv.get("floor_buildup"))
        if b is None:
            b = b_meta
        if b is None:
            b = float(ctx.profile.get("floor_buildup", 0.15)) if datum == "OKFF" else 0.0
            assumed = True
        e = float(lv["elevation"])
        rec = {"id": lv["id"], "name": lv.get("name") or lv["id"], "elevation": e, "index": i, "buildup": b,
               "okrd": e - b if datum == "OKFF" else e, "okff": e if datum == "OKFF" else e + b, "slab_thickness": None,
               "floor_to_floor_height": _num(lv.get("floor_to_floor_height"))}
        plan["levels"].append(rec)
        ctx.levels[rec["id"]] = rec
        ctx.ordered.append(rec)
    if assumed and datum == "OKFF":
        plan["warnings"].append(f"floor build-up not given: {ctx.profile.get('floor_buildup', 0.15):.2f} m from the office profile assumed")
    elif assumed:
        plan["notes"].append("floor build-up not given (OKRD datum): 0.00 m, no floor build-up slabs")


def _infer_datum(ctx: _Context, levels: list[dict], b_meta: float | None) -> str:
    b_guess = b_meta if b_meta is not None else float(ctx.profile.get("floor_buildup", 0.15))
    elevations = [float(lv["elevation"]) for lv in levels]
    tops = [_slab_top(s) for s in ctx.model.get("slabs") or [] if s.get("role") in (None, "ground_slab", "floor_slab")]
    tops = [t for t in tops if t is not None]
    okrd = sum(1 for t in tops if any(abs(t - e) <= 0.01 for e in elevations))
    okff = sum(1 for t in tops if b_guess > 0 and any(abs(t - (e - b_guess)) <= 0.01 for e in elevations))
    if okff > okrd:
        datum = "OKFF"
    elif okrd:
        datum = "OKRD"
    else:
        ctx.plan["warnings"].append("metadata.level_datum missing and not inferable from the slab tops: OKRD assumed (rule A4)")
        return "OKRD"
    ctx.plan["notes"].append(f"level_datum inferred from the slab tops: {datum} (set metadata.level_datum to make it explicit)")
    return datum


def _classify_slabs(ctx: _Context) -> None:
    """Role and owning level of every model slab; refines OK Rohdecke and slab thickness per level."""
    plan, datum = ctx.plan, ctx.plan["datum"]["level_datum"]
    if not ctx.ordered:
        return
    building = {w.get("level_id") for w in ctx.model.get("walls") or [] if w.get("role") not in FOUNDATION_ROLES}
    building |= {sp.get("level_id") for sp in ctx.model.get("spaces") or []}
    ctx.ground = next((lv for lv in ctx.ordered if lv["id"] in building), ctx.ordered[0])  # a foundation story lies below it
    for s in ctx.model.get("slabs") or []:
        sid, role, top = s.get("id", "?"), s.get("role"), _slab_top(s)
        if role is not None and role not in SLAB_ROLES:
            plan["warnings"].append(f"slab {sid}: role '{role}' unknown; derived from its height instead")
            role = None
        owner, by_datum = None, False
        if top is not None:
            owner = next((lv for lv in ctx.ordered if abs(top - lv["okrd"]) <= 0.02), None)
            by_datum = owner is not None
            if owner is None:
                owner = next((lv for lv in ctx.ordered if abs(top - lv["elevation"]) <= 0.02), None)
                if owner is not None and datum == "OKFF" and owner["buildup"] > 0.005:
                    plan["warnings"].append(f"slab {sid}: top {top:.3f} m sits on level {owner['id']} itself, but with the OKFF datum "
                                            f"the raw slab belongs {owner['buildup']:.3f} m lower (OK Rohdecke {owner['okrd']:.3f} m)")
        if role is None:
            if top is None:
                role = "floor_slab"
                plan["warnings"].append(f"slab {sid}: no elevation; treated as raw slab of its level")
            elif owner is not None:
                role = "ground_slab" if owner is ctx.ground else "floor_slab"
            elif top > ctx.ordered[-1]["elevation"] + 0.5:
                role, owner = "roof_slab", ctx.ordered[-1]
            else:
                role = "floor_slab"
                plan["warnings"].append(f"slab {sid}: top {top:.3f} m matches no level; treated as raw slab of its model level")
        if owner is None:
            owner = ctx.ordered[-1] if role == "roof_slab" else ctx.levels.get(s.get("level_id"))
        t = _num(s.get("thickness"))
        ctx.slab_info[sid] = {"role": role, "owner": owner, "top": top, "thickness": t}
        if role in RAW_SLABS and owner is not None and top is not None and owner["slab_thickness"] is None:
            if not by_datum:
                owner["okrd"] = top
            owner["slab_thickness"] = t
        if role == "roof_slab" and top is not None and t is not None and ctx.roof is None:
            ctx.roof = {"id": sid, "top": top, "thickness": t}


def _plan_walls(ctx: _Context) -> None:
    plan, office = ctx.plan, ctx.office
    for wall in ctx.model.get("walls") or []:
        wid = wall.get("id", "?")
        level = ctx.levels.get(wall.get("level_id"))
        if level is None:
            _skip(plan, wid, "wall", "level missing or without elevation")
            continue
        if not _num(wall.get("thickness")):
            _skip(plan, wid, "wall", "thickness missing")
            continue
        rep = wall.get("representation") or "unknown"
        role = wall.get("role")
        if role not in WALL_ROLES:
            if role is not None:
                plan["warnings"].append(f"wall {wid}: role '{role}' unknown; derived from its representation")
            role = "exterior_wall" if rep == "outer_face" or wall.get("position") == "exterior" else "interior_wall"
        if rep not in REFERENCE_LINE:
            plan["warnings"].append(f"wall {wid}: representation '{rep}' unknown, placed with a centred reference line")
        elif rep == "inner_face":
            plan["warnings"].append(f"wall {wid}: inner_face reference line, body side not live-verified; check its bounding box")
        reference = "CoreOutside" if role in OUTSIDE_REFERENCE else REFERENCE_LINE.get(rep, "Center")
        r = mr.ROLES[role]
        lb = wall.get("is_load_bearing") if r.from_model and isinstance(wall.get("is_load_bearing"), bool) else r.load_bearing
        if role == "interior_wall" and lb is None:
            plan["warnings"].append(f"wall {wid}: load-bearing unknown (is_load_bearing missing); 'Nicht definiert' is set, "
                                    "not guessed (rule B3)")
        material = wall.get("material")
        material = ctx.material_map.get(material, material) if material else None
        comp = (office.get("composites") or {}).get(material) if office and material else None
        basic = (office.get("materials") or {}).get(material) if office and material and not comp else None
        if office and material and not comp and not basic:
            plan["warnings"].append(f"wall {wid}: material '{material}' is neither a composite nor a building material of the "
                                    "office file; the tool default is used")
        skins = list(comp["skins"]) if comp else []
        model_t = float(wall["thickness"])
        thickness = mr.total_thickness(skins) if comp else model_t
        if comp and abs(thickness - model_t) > 0.005:
            plan["warnings"].append(f"wall {wid}: composite '{material}' is {thickness:.3f} m thick, the model says {model_t:.3f} m; "
                                    f"the room side moves by {thickness - model_t:+.3f} m (rule C10)")
        favorite = wall.get("favorite")
        if not favorite and material and material in (ctx.favorites("Wall") or []):
            favorite = material
        sem = _semantics(role, ctx.profile, lb)
        pts = wall.get("baseline") or []
        recs, lengths = [], []
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            length = dist(a, b)
            lengths.append(length)
            if length < MIN_WALL_LENGTH:
                _skip(plan, wid if len(pts) == 2 else f"{wid}#{i}", "wall",
                      f"segment {length:.3f} m too short (< {MIN_WALL_LENGTH} m; zero-length walls crash Archicad)")
                recs.append(None)
                continue
            payload: dict[str, Any] = {"begCoordinate": pt(a), "endCoordinate": pt(b), "zCoordinate": 0.0, "height": 0.0,
                                       "thickness": thickness, "referenceLineLocation": reference, "floorIndex": level["index"]}
            if favorite:
                payload["favoriteName"] = favorite
            rec = {"key": f"{wid}#{i}", "model_id": wid, "segment": i, "level_id": level["id"], "role": role,
                   "exterior": role in OUTSIDE_REFERENCE, "representation": rep, "reversed": False, "length": length,
                   "model_length": length, "material": material, "composite": material if comp or (office is None and material) else None,
                   "building_material": material if basic else None, "skins": skins, "base": wall.get("base"),
                   "covering": _num(wall.get("covering_thickness")), "top_mode": wall.get("top"), "model_height": _num(wall.get("height")),
                   "interior_left": None, "top_link": None, "zone_rel": "SubtractFromZone" if role == "installation_wall" else None,
                   "semantics": sem, "payload": payload, "expect": {}}
            plan["walls"].append(rec)
            recs.append(rec)
        ctx.segments[wid] = {"recs": recs, "lengths": lengths}


def _reverse(rec: dict) -> None:
    p = rec["payload"]
    p["begCoordinate"], p["endCoordinate"] = p["endCoordinate"], p["begCoordinate"]
    rec["reversed"] = not rec["reversed"]


def _orient_exterior_loops(ctx: _Context) -> None:
    """Draw every closed outer-face loop counter-clockwise: the interior then lies LEFT of every wall (plan convention)."""
    plan = ctx.plan

    def node(c: dict) -> tuple[float, float]:
        return round(c["x"], 3), round(c["y"], 3)

    warned: set[str] = set()
    groups = sorted({(w["level_id"], w["role"]) for w in plan["walls"] if w["exterior"]})
    for level_id, role in groups:
        recs = [w for w in plan["walls"] if w["exterior"] and w["level_id"] == level_id and w["role"] == role]
        ends: dict[tuple, list[dict]] = {}
        for r in recs:
            for c in (r["payload"]["begCoordinate"], r["payload"]["endCoordinate"]):
                ends.setdefault(node(c), []).append(r)
        seen: set[int] = set()
        for start in recs:
            if id(start) in seen:
                continue
            comp, stack = [], [start]
            while stack:
                r = stack.pop()
                if id(r) in seen:
                    continue
                seen.add(id(r))
                comp.append(r)
                for c in (r["payload"]["begCoordinate"], r["payload"]["endCoordinate"]):
                    stack.extend(o for o in ends[node(c)] if id(o) not in seen)
            degree: dict[tuple, int] = {}
            for r in comp:
                for c in (r["payload"]["begCoordinate"], r["payload"]["endCoordinate"]):
                    degree[node(c)] = degree.get(node(c), 0) + 1
            if len(comp) < 3 or any(d != 2 for d in degree.values()):
                for r in comp:
                    r["interior_left"] = True
                    if r["model_id"] not in warned:
                        warned.add(r["model_id"])
                        plan["warnings"].append(f"wall {r['model_id']}: outer-face wall not part of a closed loop; "
                                                "body side (left of the drawing direction) unchecked")
                continue
            order = [(comp[0], False)]
            used = {id(comp[0])}
            current = node(comp[0]["payload"]["endCoordinate"])
            while len(order) < len(comp):
                nxt = next(o for o in ends[current] if id(o) not in used)
                used.add(id(nxt))
                forward = node(nxt["payload"]["begCoordinate"]) == current
                order.append((nxt, not forward))
                current = node(nxt["payload"]["endCoordinate"] if forward else nxt["payload"]["begCoordinate"])
            poly = [_xy(r["payload"]["endCoordinate"] if backwards else r["payload"]["begCoordinate"]) for r, backwards in order]
            traversal_is_ccw = mr.signed_area(poly) > 0
            for r, backwards in order:
                if (not backwards) != traversal_is_ccw:
                    _reverse(r)
                r["interior_left"] = True
            ccw = [r for r, _ in (order if traversal_is_ccw else list(reversed(order)))]
            ring = [_xy(r["payload"]["begCoordinate"]) for r in ccw]
            xs, ys = [p[0] for p in ring], [p[1] for p in ring]
            plan["loops"].append({"level_id": level_id, "role": role, "keys": [r["key"] for r in ccw],
                                  "bbox": [min(xs), min(ys), max(xs), max(ys)], "outer_ring": ring})


def _apply_core_offsets(ctx: _Context) -> None:
    """Rule C1: move the reference line of exterior walls from the model's outer face to the outer face of the core."""
    plan = ctx.plan
    by_key = {w["key"]: w for w in plan["walls"]}
    for w in plan["walls"]:
        w["model_beg"], w["model_end"] = _xy(w["payload"]["begCoordinate"]), _xy(w["payload"]["endCoordinate"])
    in_loop: set[str] = set()
    for loop in plan["loops"]:
        recs = [by_key[k] for k in loop["keys"]]
        in_loop.update(loop["keys"])
        ring = loop["outer_ring"]
        front = [mr.core_outside_offset(r["skins"]) for r in recs]
        core = [mr.core_thickness(r["skins"]) if r["skins"] else r["payload"]["thickness"] for r in recs]
        total = [r["payload"]["thickness"] for r in recs]
        ref = mr.offset_ring(ring, front)
        loop["ref_ring"] = ref
        loop["core_in_ring"] = mr.offset_ring(ring, [f + c for f, c in zip(front, core)])
        loop["inner_ring"] = mr.offset_ring(ring, total)
        n = len(recs)
        for k, r in enumerate(recs):
            r["payload"]["begCoordinate"], r["payload"]["endCoordinate"] = pt(ref[k]), pt(ref[(k + 1) % n])
            r["length"] = dist(ref[k], ref[(k + 1) % n])
    for w in plan["walls"]:
        if w["exterior"] and w["key"] not in in_loop and w["skins"]:
            d = mr.core_outside_offset(w["skins"])
            nx, ny = mr.left_normal(mr.unit(w["model_beg"], w["model_end"]))
            w["payload"]["begCoordinate"] = pt((w["model_beg"][0] + d * nx, w["model_beg"][1] + d * ny))
            w["payload"]["endCoordinate"] = pt((w["model_end"][0] + d * nx, w["model_end"][1] + d * ny))


def _snap_wall_ends(ctx: _Context) -> None:
    """Rule C7: a wall ending in another wall's body is moved onto that wall's reference line (Archicad joins there)."""
    plan = ctx.plan
    loop_keys = {k for loop in plan["loops"] for k in loop["keys"]}
    for a in plan["walls"]:
        if a["key"] in loop_keys:
            continue
        for end in ("begCoordinate", "endCoordinate"):
            p = _xy(a["payload"][end])
            direction = mr.unit(_xy(a["payload"]["begCoordinate"]), _xy(a["payload"]["endCoordinate"]))
            for b in plan["walls"]:
                if b is a or b["level_id"] != a["level_id"]:
                    continue
                d, t = point_segment_distance(p, b["model_beg"], b["model_end"])
                if d > b["payload"]["thickness"] + TOL or t <= 1e-6 or t >= 1 - 1e-6:
                    continue
                rb, re_ = _xy(b["payload"]["begCoordinate"]), _xy(b["payload"]["endCoordinate"])
                if point_segment_distance(p, rb, re_)[0] <= TOL:
                    break
                hit = mr.line_intersection(p, direction, rb, mr.unit(rb, re_))
                if hit is None or dist(hit, p) > b["payload"]["thickness"] + TOL:
                    continue
                a["payload"][end] = pt(hit)
                plan["notes"].append(f"wall {a['model_id']}: end moved {dist(hit, p):.3f} m onto the reference line of wall "
                                     f"{b['model_id']} (rule C7)")
                break
        a["length"] = dist(_xy(a["payload"]["begCoordinate"]), _xy(a["payload"]["endCoordinate"]))


def _check_junctions(plan: dict) -> None:
    """Warn where a wall end still touches another wall's body but misses its reference line."""
    for r in plan["walls"]:
        for end in ("begCoordinate", "endCoordinate"):
            p = _xy(r["payload"][end])
            on_line, touched = False, None
            ur = mr.unit(_xy(r["payload"]["begCoordinate"]), _xy(r["payload"]["endCoordinate"]))
            for o in plan["walls"]:
                if o is r or o["level_id"] != r["level_id"] or "railing" in (r["role"], o["role"]):
                    continue
                uo = mr.unit(_xy(o["payload"]["begCoordinate"]), _xy(o["payload"]["endCoordinate"]))
                if abs(ur[0] * uo[1] - ur[1] * uo[0]) < 0.01:  # parallel walls do not join end-on
                    continue
                d, _ = point_segment_distance(p, _xy(o["payload"]["begCoordinate"]), _xy(o["payload"]["endCoordinate"]))
                if d <= TOL:
                    on_line = True
                    break
                if d <= o["payload"]["thickness"] + TOL and touched is None:
                    touched = o
            if touched is not None and not on_line:
                plan["warnings"].append(f"wall {r['model_id']}: end ({p[0]:.3f}, {p[1]:.3f}) touches wall {touched['model_id']} "
                                        "but misses its reference line; Archicad cleans junctions only where reference lines meet")


def _wall_heights(ctx: _Context) -> None:
    """Rules C3-C5, C11-C14: foot and head of every wall from the level datum and the slabs; head linked to the story above."""
    plan = ctx.plan
    noted: set[str] = set()
    for w in plan["walls"]:
        level = ctx.levels[w["level_id"]]
        nxt = ctx.next_level(level)
        role, wid = w["role"], w["model_id"]
        bottom, top, link, rule = level["okrd"], None, None, ""
        if role in ("interior_wall", "installation_wall") and w["base"] == "screed":
            if w["semantics"]["load_bearing"]:
                ctx.once("warnings", f"wall {wid}: base 'screed' is only for non-load-bearing walls (guideline p.20); raw slab used")
            else:
                covering = w["covering"]
                if covering is None:
                    covering = 0.015
                    ctx.once("warnings", f"wall {wid}: covering_thickness missing; 0.015 m assumed for the wall on the screed")
                bottom = level["okff"] - covering
        mh = w["model_height"] or level.get("floor_to_floor_height")
        if w["top_mode"] == "height" and w["model_height"]:
            top, rule = bottom + w["model_height"], "model height"
        elif role == "exterior_wall" and wid in ctx.strip_hosts and ctx.ukrd_above(level) is not None:
            # guideline p.17/18: an insulation strip or fire barrier in front of the slab -> the wall stops at UK Rohdecke
            top, rule = ctx.ukrd_above(level), "C15"
            if nxt:
                link = {"relativeTopStory": 1, "topOffset": round(top - nxt["elevation"], 6)}
        elif role == "exterior_wall":
            if nxt:
                top, rule = nxt["okrd"], "C3"
                link = {"relativeTopStory": 1, "topOffset": round(nxt["okrd"] - nxt["elevation"], 6)}
            elif ctx.roof:
                top, rule = ctx.roof["top"], "C4"
                ctx.once("notes", f"level {level['id']}: no story above; exterior walls end at the roof slab with a fixed height (rule C4)")
        elif role in ("interior_wall", "installation_wall"):
            under = ctx.ukrd_above(level)
            if under is not None:
                top, rule = under, "C5"
                if nxt:
                    link = {"relativeTopStory": 1, "topOffset": round(under - nxt["elevation"], 6)}
        elif role == "parapet":
            if ctx.roof:
                bottom = ctx.roof["top"]
            else:
                ctx.once("warnings", f"wall {wid}: parapet without a roof slab; placed on OK Rohdecke of {level['id']}")
            top, rule = bottom + (w["model_height"] or 1.0), "C11"
        elif role == "railing":
            bottom = level["okff"]
            top, rule = bottom + (w["model_height"] or 1.0), "C12"
        elif role == "strip_footing":
            top = nxt["okrd"] if nxt else level["okrd"]
            bottom, rule = top - (w["model_height"] or 0.8), "C14"
        if top is None:
            top = bottom + (mh or 3.0)
            ctx.once("warnings", f"wall {wid}: no slab or story above to end at; height {top - bottom:.2f} m from the model")
        if role in ("parapet", "railing", "strip_footing") and not w["model_height"]:
            ctx.once("warnings", f"wall {wid}: height missing for role {role}; {top - bottom:.2f} m assumed")
        w["payload"]["zCoordinate"] = round(bottom - level["elevation"], 6)
        w["payload"]["height"] = round(top - bottom, 6)
        w["top_link"] = link
        w["expect"] = {"z_min": round(bottom, 6), "z_max": round(top, 6)}
        if (w["model_height"] and w["top_mode"] != "height" and abs(w["model_height"] - (top - bottom)) > 0.005
                and wid not in noted and role not in ("parapet", "railing", "strip_footing")):
            noted.add(wid)
            plan["notes"].append(f"wall {wid}: model height {w['model_height']:.2f} m replaced by the rule ({top - bottom:.2f} m, rule {rule})")


def _plan_openings(ctx: _Context, window_favorite: str | None, door_favorite: str | None) -> None:
    plan = ctx.plan
    sill_ref = plan["datum"]["sill_reference"]
    for op in ctx.model.get("openings") or []:
        oid, kind = op.get("id", "?"), op.get("kind")
        if kind not in ("window", "door", "opening", "niche"):
            _skip(plan, oid, "opening", f"kind '{kind}' not supported (window, door, opening = Wanddurchbruch, niche = Schlitz)")
            continue
        if kind == "niche":
            _skip(plan, oid, "niche", "slot depth is not settable through Tapir 1.5.9 (CreateOpenings has no depth) and a through-"
                                      "opening would be wrong; model the slot in Archicad (rule E9)")
            continue
        host = ctx.segments.get(op.get("host_wall_id"))
        if not host or all(r is None for r in host["recs"]):
            _skip(plan, oid, kind, f"host wall {op.get('host_wall_id')} not planned")
            continue
        width, height, sill = _num(op.get("width")), _num(op.get("height")), _num(op.get("sill_height"))
        if height is None and _num(op.get("head_height")) is not None and sill is not None:
            height = op["head_height"] - sill
        offset = _num(op.get("offset_along_wall"))
        if not width:
            _skip(plan, oid, kind, "width missing")
            continue
        if not height:
            _skip(plan, oid, kind, "height missing")
            continue
        if offset is None:
            _skip(plan, oid, kind, "offset_along_wall missing (derive it from witness geometry first)")
            continue
        if op.get("offset_reference") == "start_edge":
            offset += width / 2.0
        found, seg, local, start = False, None, 0.0, 0.0
        for rec, length in zip(host["recs"], host["lengths"]):
            if offset <= start + length + TOL:
                found, seg, local = True, rec, offset - start
                break
            start += length
        if not found:
            _skip(plan, oid, kind, f"offset {offset:.3f} m lies beyond host wall {op.get('host_wall_id')}")
            continue
        if seg is None:
            _skip(plan, oid, kind, f"host segment of wall {op.get('host_wall_id')} was skipped (too short)")
            continue
        if seg["reversed"]:
            local = seg["model_length"] - local
        u = mr.unit(seg["model_beg"], seg["model_end"])
        beg = _xy(seg["payload"]["begCoordinate"])
        local -= (beg[0] - seg["model_beg"][0]) * u[0] + (beg[1] - seg["model_beg"][1]) * u[1]
        if local - width / 2.0 < -TOL or local + width / 2.0 > seg["length"] + TOL:
            plan["warnings"].append(f"opening {oid}: extends beyond host segment {seg['key']}")
        level = ctx.levels[seg["level_id"]]
        if kind in ("opening", "niche"):
            # guideline p.31: opening tool, "Durchbrüche / Schlitze - Öffnung" (slot: "Nische"), position inside;
            # CreateOpenings takes the centre on the wall line and the sill as z (live 29.09.2026)
            z = round((level["okff"] if sill_ref == "OKFF" else level["okrd"]) + (sill or 0.0), 6)
            b2, e2 = _xy(seg["payload"]["begCoordinate"]), _xy(seg["payload"]["endCoordinate"])
            u2 = mr.unit(b2, e2)
            role = "wall_opening" if kind == "opening" else "wall_niche"
            plan["openings"].append({"key": oid, "model_id": oid, "role": role, "host_key": seg["key"], "host_kind": "wall",
                                     "level_id": seg["level_id"], "semantics": _semantics(role, ctx.profile),
                                     "payload": {"basePoint": {"x": round(b2[0] + u2[0] * local, 6), "y": round(b2[1] + u2[1] * local, 6),
                                                               "z": z}, "width": width, "height": height},
                                     "expect": {"sill_abs": z}})
            continue
        foot = seg["expect"]["z_min"]
        payload: dict[str, Any] = {"width": width, "height": height}
        if kind == "door" and sill is None:
            sill = 0.0
        if sill is None:
            plan["warnings"].append(f"opening {oid}: sill_height missing, Archicad default used")
            z_min = None
        else:
            base = level["okff"] if sill_ref == "OKFF" else level["okrd"]
            z_min = base + sill
            if kind == "window" and sill_ref == "OKFF" and sill <= 0.005 and level["okff"] - level["okrd"] > 0.005:
                z_min = level["okrd"]
                height += level["okff"] - level["okrd"]
                payload["height"] = round(height, 6)
                plan["notes"].append(f"opening {oid}: floor-to-ceiling window extended down to OK Rohdecke by the floor build-up (rule E2)")
            payload["sillHeight"] = round(z_min - foot, 6)
        swing_text = str(op.get("swing") or "").strip().lower()
        if seg["exterior"]:
            swing = "outward" if swing_text in OUTWARD else "inward"
        else:
            swing = None
        favorite = op.get("favorite") or (window_favorite if kind == "window" else door_favorite)
        if favorite:
            payload["favoriteName"] = favorite
        sem = _semantics(kind, ctx.profile, position=seg["semantics"]["position"])
        rec = {"key": oid, "model_id": oid, "kind": kind, "role": kind, "host_key": seg["key"], "level_id": seg["level_id"],
               "center_offset": round(local, 6), "swing": swing, "interior_left": seg["interior_left"], "payload": payload,
               "semantics": sem, "expect": {} if z_min is None else {"z_min": round(z_min, 6), "z_max": round(z_min + height, 6)}}
        plan["windows" if kind == "window" else "doors"].append(rec)


def _check_opening_junctions(plan: dict) -> None:
    """Warn where another wall joins the host wall inside an opening's width (it would cut the door or window)."""
    walls = {w["key"]: w for w in plan["walls"]}
    for op in plan["windows"] + plan["doors"]:
        host = walls[op["host_key"]]
        a, b = _xy(host["payload"]["begCoordinate"]), _xy(host["payload"]["endCoordinate"])
        centre, half = op["center_offset"], op["payload"]["width"] / 2.0
        for other in plan["walls"]:
            if other is host or other["level_id"] != host["level_id"]:
                continue
            for end in ("begCoordinate", "endCoordinate"):
                d, t = point_segment_distance(_xy(other["payload"][end]), a, b)
                along = t * host["length"]
                if d > TOL or along <= TOL or along >= host["length"] - TOL:  # not on the host, or a corner
                    continue
                if abs(along - centre) < half + other["payload"]["thickness"] / 2.0 - TOL:
                    plan["warnings"].append(f"opening {op['model_id']}: wall {other['model_id']} joins host wall "
                                            f"{host['model_id']} inside the opening ({along:.3f} m from its start)")


def _follows(boundary: list, ring: list, tol: float) -> bool:
    if len(boundary) != len(ring):
        return False
    return all(min(dist(p, q) for q in ring) <= tol for p in boundary)


def _plan_slabs(ctx: _Context) -> None:
    """Rules D1-D3, D6: role, extent, height and home story of every model slab."""
    plan = ctx.plan
    slab_story = plan["datum"]["slab_story"]
    for s in ctx.model.get("slabs") or []:
        sid = s.get("id", "?")
        info = ctx.slab_info.get(sid)
        boundary = [tuple(p) for p in s.get("boundary") or []]
        if info is None or info["owner"] is None:
            _skip(plan, sid, "slab", "level missing or without elevation")
            continue
        if len(boundary) < 3:
            _skip(plan, sid, "slab", "boundary missing")
            continue
        if not info["thickness"]:
            _skip(plan, sid, "slab", "thickness missing")
            continue
        role, owner, t = info["role"], info["owner"], info["thickness"]
        top = info["top"] if info["top"] is not None else owner["okrd"]
        polygon = boundary
        if role in ("ground_slab", "floor_slab", "roof_slab") and s.get("extent") != "boundary":
            wall_level = owner if role in ("ground_slab", "roof_slab") else (ctx.prev_level(owner) or owner)
            rings = [lp for lp in plan["loops"] if lp["level_id"] == wall_level["id"] and lp["role"] == "exterior_wall"]
            ring_key, label = ("ref_ring", "outer face of the core") if role == "ground_slab" else ("core_in_ring", "inner face of the core")
            match = None
            for loop in rings:  # several bodies on one level: the slab follows the ring it lies on
                tol = max((w["payload"]["thickness"] for w in plan["walls"] if w["key"] in loop["keys"]), default=0.5) + 0.02
                if _follows(boundary, loop["outer_ring"], tol) or _follows(boundary, loop.get("inner_ring", []), tol):
                    match = loop
                    break
            if not rings:
                plan["warnings"].append(f"slab {sid}: no closed exterior wall ring on level {wall_level['id']}; model boundary kept")
            elif match is None:
                plan["warnings"].append(f"slab {sid}: boundary does not follow the exterior walls of {wall_level['id']}; "
                                        "rule D2/D3 not applied, model boundary kept")
            else:
                polygon = match[ring_key]
                plan["notes"].append(f"slab {sid}: edge on the {label} of the exterior walls of {wall_level['id']} (rule D2/D3)")
                if ring_key == "core_in_ring":
                    _check_priorities(ctx, sid, s, role, match)
        home = owner
        if slab_story == "above" and role in RAW_SLABS:
            home = ctx.prev_level(owner) or owner
        payload: dict[str, Any] = {"level": round(top, 6), "polygonCoordinates": [pt(p) for p in polygon], "thickness": t,
                                   "referencePlaneLocation": "Top", "floorIndex": home["index"]}
        favorite = s.get("favorite") or (ctx.profile.get("favorites") or {}).get(role)
        if favorite:
            payload["favoriteName"] = favorite
        material = s.get("material")
        material = ctx.material_map.get(material, material) if material else None
        plan["slabs"].append({"key": sid, "model_id": sid, "role": role, "level_id": home["id"], "material": material,
                              "payload": payload, "semantics": _semantics(role, ctx.profile),
                              "expect": {"z_min": round(top - t, 6), "z_max": round(top, 6)}})


def _check_priorities(ctx: _Context, sid: str, s: dict, role: str, loop: dict) -> None:
    """Rule C8: a raw slab ending at the inner core face overlaps the inner finish of the wall; its material must win."""
    materials = (ctx.office or {}).get("materials") or {}
    favorite = s.get("favorite") or (ctx.profile.get("favorites") or {}).get(role)
    name = ctx.material_map.get(s.get("material"), s.get("material")) or (ctx.profile.get("favorite_materials") or {}).get(favorite)
    slab_prio = (materials.get(name) or {}).get("priority") if name else None
    if slab_prio is None:
        return
    walls = {w["key"]: w for w in ctx.plan["walls"]}
    seen: set[str] = set()
    for key in loop["keys"]:
        skins = walls[key]["skins"]
        cores = [i for i, sk in enumerate(skins) if sk.get("type") == "Core"]
        for sk in skins[cores[-1] + 1:] if cores else []:
            prio = (materials.get(sk.get("material") or "") or {}).get("priority")
            if prio is not None and prio >= slab_prio and sk["material"] not in seen:
                seen.add(sk["material"])
                ctx.plan["warnings"].append(f"slab {sid}: its material {name} (priority {slab_prio}) does not cut the inner finish "
                                            f"{sk['material']} (priority {prio}) of the exterior walls; check the building material "
                                            "priorities (rule C8)")


def _plan_zones(ctx: _Context, mode: str, allow_manual: bool) -> None:
    """Rules R1-R6: associative rooms (inner edge), floor thickness, top under the slab; the template base is checked."""
    plan = ctx.plan
    template_base = _num(((ctx.office or {}).get("zone_defaults") or {}).get("base_offset"))
    if template_base is None:
        template_base = _num(ctx.profile.get("zone_base_offset"))
    checked: set[str] = set()
    for sp in ctx.model.get("spaces") or []:
        zid = sp.get("id", "?")
        level = ctx.levels.get(sp.get("level_id"))
        boundary = [tuple(p) for p in sp.get("boundary") or []]
        if level is None or len(boundary) < 3:
            _skip(plan, zid, "zone", "level or boundary missing")
            continue
        b = _num(sp.get("floor_buildup"))
        b = level["buildup"] if b is None else b
        polygon = {"polygonCoordinates": [pt(p) for p in boundary]}
        geometry = {"referencePosition": pt(interior_point(boundary))} if mode == "auto" else polygon
        if mode != "auto":
            ctx.once("warnings", "zones drawn as manual polygons (--zones manual): not associative, against rule R3")
        props: dict[str, float] = {"floor_thickness": round(b, 6)}
        under, nxt = ctx.ukrd_above(level), ctx.next_level(level)
        ceiling = sp.get("ceiling") or {}
        if under is not None and ceiling.get("type") == "suspended" and str(ceiling.get("variant", "01")) == "02":
            under -= _ceiling_thickness(ctx, ceiling)  # guideline p.7/16 variant 02: room up to UK Abhangdecke
        if under is not None and nxt:
            props["top_offset"] = round(under - nxt["elevation"], 6)
        elif under is not None:
            props["clear_height"] = round(under - (level["okrd"] + b), 6)
        else:
            plan["warnings"].append(f"zone {zid}: no slab above; the room height stays as the template sets it")
        rule_base = level["okrd"] - level["elevation"]
        if template_base is not None and level["id"] not in checked and abs(template_base - rule_base) > 0.005:
            checked.add(level["id"])
            plan["warnings"].append(f"zone base: the template puts rooms at {template_base:+.2f} m, the rule wants OK Rohdecke "
                                    f"{rule_base:+.2f} m on level {level['id']} (not settable through Tapir; rule R5)")
        payload: dict[str, Any] = {"name": sp.get("name") or zid, "numberStr": str(sp.get("number") or zid), "geometry": geometry,
                                   "floorIndex": level["index"]}
        if sp.get("favorite"):
            payload["favoriteName"] = sp["favorite"]
        plan["zones"].append({"key": zid, "model_id": zid, "level_id": level["id"], "payload": payload, "use": sp.get("use"),
                              "fallback_geometry": polygon if allow_manual and mode == "auto" else None, "zone_properties": props,
                              "semantics": _semantics("space", ctx.profile), "area": abs(mr.signed_area(boundary)),
                              "expect": {"z_min": round(level["okrd"] + b, 6), "z_max": None if under is None else round(under, 6)}})


def _plan_buildups(ctx: _Context) -> None:
    """Rule D4: one floor build-up slab per room, multi-skin without core, top = OKFF; its outline comes from the zone."""
    plan, profile = ctx.plan, ctx.profile
    spaces = {sp.get("id"): sp for sp in ctx.model.get("spaces") or []}
    finishes = profile.get("floor_finish_favorites") or {}
    for z in plan["zones"]:
        b = z["zone_properties"]["floor_thickness"]
        if b <= 0.001:
            continue
        sp, level = spaces[z["model_id"]], ctx.levels[z["level_id"]]
        favorite = sp.get("floor_buildup_favorite") or finishes.get(sp.get("floor_finish")) or (profile.get("favorites") or {}).get("floor_buildup")
        comp_name = (profile.get("favorite_composites") or {}).get(favorite)
        comp = ((ctx.office or {}).get("composites") or {}).get(comp_name) if comp_name else None
        if comp:
            t_fav = mr.total_thickness(comp["skins"])
            if abs(t_fav - b) > 0.005:
                plan["warnings"].append(f"floor build-up {z['model_id']}: favorite '{favorite}' is {t_fav:.3f} m, the room needs {b:.3f} m")
            if mr.has_core(comp["skins"]):
                plan["warnings"].append(f"floor build-up {z['model_id']}: composite '{comp_name}' has a core; the rule wants none (D4)")
        top = level["okrd"] + b
        payload: dict[str, Any] = {"level": round(top, 6), "thickness": round(b, 6), "referencePlaneLocation": "Top",
                                   "polygonCoordinates": [pt(p) for p in (sp.get("boundary") or [])], "floorIndex": level["index"]}
        if favorite:
            payload["favoriteName"] = favorite
        boundary = [tuple(p) for p in sp.get("boundary") or []]
        # rule D5: an opening in the raw slab below becomes a geometric hole in the build-up, never an opening
        holes = [[pt(p) for p in rect] for owner, rect in ctx.slab_holes if owner == level["id"]
                 and mr.point_in_polygon((sum(p[0] for p in rect) / 4, sum(p[1] for p in rect) / 4), boundary)]
        plan["buildups"].append({"key": f"buildup:{z['model_id']}", "model_id": z["model_id"], "zone_key": z["key"], "role": "floor_buildup",
                                 "level_id": level["id"], "payload": payload, "holes": holes, "semantics": _semantics("floor_buildup", profile),
                                 "expect": {"z_min": round(top - b, 6), "z_max": round(top, 6)}})


def _ceiling_thickness(ctx: _Context, ceiling: dict) -> float:
    name = ceiling.get("material") or (ctx.profile.get("composites") or {}).get("suspended_ceiling")
    comp = ((ctx.office or {}).get("composites") or {}).get(name) if name else None
    if comp:
        return mr.total_thickness(comp["skins"])
    return float(_num(ceiling.get("thickness")) or 0.4)


def _envelope_position(ctx: _Context, level_id: str, point: Any) -> str:
    """Rule B2 'envelope': inside the closed exterior wall ring of the level -> interior, else exterior."""
    rings = [lp["outer_ring"] for lp in ctx.plan["loops"] if lp["level_id"] == level_id and lp["role"] == "exterior_wall"]
    if not rings:
        return "interior"
    return "interior" if any(mr.point_in_polygon(point, ring) for ring in rings) else "exterior"


def _plan_slab_openings(ctx: _Context) -> None:
    """Rule D9: openings in raw slabs are opening elements (one per call later); base point x = centre, y = upper edge."""
    plan = ctx.plan
    slabs = {s["key"]: s for s in plan["slabs"]}
    for s in ctx.model.get("slabs") or []:
        host = slabs.get(s.get("id"))
        for op in s.get("openings") or []:
            oid = op.get("id", f"{s.get('id')}:opening")
            center, w, d = op.get("center"), _num(op.get("width")), _num(op.get("depth"))
            if host is None or not center or not w or not d:
                _skip(plan, oid, "slab opening", "host slab, center, width or depth missing")
                continue
            if host["role"] == "floor_buildup":
                _skip(plan, oid, "slab opening", f"host {host['key']} is a floor build-up: holes, not openings (rule D5)")
                continue
            cx, cy = float(center[0]), float(center[1])
            top = host["payload"]["level"]
            plan["openings"].append({"key": oid, "model_id": oid, "role": "slab_opening", "host_key": host["key"], "host_kind": "slab",
                                     "level_id": host["level_id"], "semantics": _semantics("slab_opening", ctx.profile),
                                     "payload": {"basePoint": {"x": round(cx, 6), "y": round(cy + d / 2, 6), "z": top}, "width": w, "height": d},
                                     "expect": {"rect": [cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2]}})
            owner = ctx.slab_info.get(s.get("id"), {}).get("owner")
            if owner is not None and host["role"] in RAW_SLABS:  # the floor build-up on this raw slab gets the hole
                ctx.slab_holes.append((owner["id"], [(cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2),
                                                     (cx - w / 2, cy + d / 2)]))


def _plan_ceilings(ctx: _Context) -> None:
    """Rule D8: suspended ceilings per room, top = UK Rohdecke, outline from the room (read at execution)."""
    plan = ctx.plan
    spaces = {sp.get("id"): sp for sp in ctx.model.get("spaces") or []}
    for z in plan["zones"]:
        ceiling = spaces[z["model_id"]].get("ceiling") or {}
        if ceiling.get("type") != "suspended":
            continue
        level = ctx.levels[z["level_id"]]
        under = ctx.ukrd_above(level)
        if under is None:
            plan["warnings"].append(f"suspended ceiling {z['model_id']}: no slab above; not planned")
            continue
        t = _ceiling_thickness(ctx, ceiling)
        name = ceiling.get("material") or (ctx.profile.get("composites") or {}).get("suspended_ceiling")
        plan["ceilings"].append({"key": f"ceiling:{z['model_id']}", "model_id": z["model_id"], "zone_key": z["key"], "role": "suspended_ceiling",
                                 "level_id": level["id"], "composite": name, "semantics": _semantics("suspended_ceiling", ctx.profile),
                                 "payload": {"level": round(under, 6), "thickness": round(t, 6), "referencePlaneLocation": "Top",
                                             "polygonCoordinates": z["payload"].get("geometry", {}).get("polygonCoordinates")
                                             or [pt(p) for p in spaces[z["model_id"]].get("boundary") or []], "floorIndex": level["index"]},
                                 "expect": {"z_min": round(under - t, 6), "z_max": round(under, 6)}})


def _plan_columns(ctx: _Context) -> None:
    """Rules T1, T3: columns OK Rohdecke to UK Rohdecke; pad footings end at the top of the ground slab."""
    plan = ctx.plan
    for c in ctx.model.get("columns") or []:
        cid = c.get("id", "?")
        level = ctx.levels.get(c.get("level_id"))
        pos = c.get("position")
        role = c.get("role") if c.get("role") in COLUMN_ROLES else "column"
        width = _num(c.get("width")) or _num(c.get("diameter"))
        if level is None or not pos or not width:
            _skip(plan, cid, "column", "level, position or width missing")
            continue
        depth = _num(c.get("depth")) or width
        if role == "pad_footing":
            top = _num(c.get("top_elevation"))
            if top is None:  # OK Fundament = OK Sohlplatte (guideline p.8)
                top = (ctx.ground or ctx.ordered[0])["okrd"]
            height = _num(c.get("height")) or 0.5
            bottom = top - height
        else:
            bottom = level["okrd"]
            under = ctx.ukrd_above(level)
            top = under if under is not None else bottom + (_num(c.get("height")) or 2.5)
            if under is None:
                ctx.once("warnings", f"column {cid}: no slab above; height from the model")
        material = c.get("material")
        material = ctx.material_map.get(material, material) if material else None
        payload: dict[str, Any] = {"coordinates": {"x": round(float(pos[0]), 6), "y": round(float(pos[1]), 6), "z": round(bottom, 6)},
                                   "height": round(top - bottom, 6), "width": width, "depth": depth, "floorIndex": level["index"]}
        if _num(c.get("diameter")):
            payload["circleBased"] = True
        if c.get("favorite"):
            payload["favoriteName"] = c["favorite"]
        r = mr.ROLES[role]
        lb = c.get("is_load_bearing") if isinstance(c.get("is_load_bearing"), bool) else r.load_bearing
        position = _envelope_position(ctx, level["id"], (float(pos[0]), float(pos[1]))) if r.position == "envelope" else None
        plan["columns"].append({"key": cid, "model_id": cid, "role": role, "level_id": level["id"], "building_material": material,
                                "semantics": _semantics(role, ctx.profile, lb, position), "payload": payload,
                                "expect": {"z_min": round(bottom, 6), "z_max": round(top, 6)}})


def _plan_beams(ctx: _Context) -> None:
    """Rule T2: beam roles of the guideline; zCoordinate is the top of the beam (live), downstand beams hang under the slab."""
    plan = ctx.plan
    for b in ctx.model.get("beams") or []:
        bid = b.get("id", "?")
        level = ctx.levels.get(b.get("level_id"))
        line = b.get("baseline") or []
        role = b.get("role") if b.get("role") in BEAM_ROLES else "downstand_beam"
        width, height = _num(b.get("width")), _num(b.get("height"))
        if level is None or len(line) != 2 or not width or not height:
            _skip(plan, bid, "beam", "level, two-point baseline, width or height missing")
            continue
        top = _num(b.get("top_elevation"))
        if top is None and role == "downstand_beam":
            top = ctx.ukrd_above(level)
        if top is None:
            _skip(plan, bid, "beam", f"top_elevation missing for role {role}")
            continue
        material = b.get("material")
        material = ctx.material_map.get(material, material) if material else None
        a, e = line
        payload: dict[str, Any] = {"begCoordinate": pt(a), "endCoordinate": pt(e), "zCoordinate": round(top, 6), "width": width,
                                   "height": height, "anchorPoint": "TopCenter", "isWidthAndHeightLinked": False,
                                   "floorIndex": level["index"]}
        if b.get("favorite"):
            payload["favoriteName"] = b["favorite"]
        r = mr.ROLES[role]
        mid = ((a[0] + e[0]) / 2, (a[1] + e[1]) / 2)
        position = _envelope_position(ctx, level["id"], mid) if r.position == "envelope" else None
        plan["beams"].append({"key": bid, "model_id": bid, "role": role, "level_id": level["id"], "building_material": material,
                              "semantics": _semantics(role, ctx.profile, position=position), "payload": payload,
                              "expect": {"z_min": round(top - height, 6), "z_max": round(top, 6), "length": round(dist(a, e), 6)}})


def _plan_roofs(ctx: _Context) -> None:
    """Rule T4: a pitched roof is two roofs, Sparrenlage mit Dämmung (Dach, load-bearing) and Dachdeckung on top."""
    plan, profile = ctx.plan, ctx.profile
    composites = (ctx.office or {}).get("composites") or {}
    for roof in ctx.model.get("roofs") or []:
        rid = roof.get("id", "?")
        kind = str(roof.get("kind") or "pitched").lower()
        if kind == "flat":
            _skip(plan, rid, "roof", "flat roofs are slabs: role roof_slab (Dachkonstruktion) plus roof_insulation (rule T5)")
            continue
        level = ctx.levels.get(roof.get("level_id")) or (ctx.ordered[-1] if ctx.ordered else None)
        boundary = roof.get("boundary") or []
        slope = _num(roof.get("slope"))
        if level is None or len(boundary) < 3 or slope is None:
            _skip(plan, rid, "roof", "level, boundary (pivot polygon) or slope (degrees) missing")
            continue
        eave = _num(roof.get("eave_elevation"))
        if eave is None:
            eave = ctx.roof["top"] if ctx.roof else level["okrd"] + (level.get("floor_to_floor_height") or 3.0)
        angle = math.radians(slope)
        overhang = _num(roof.get("overhang")) or 0.0
        base = eave
        for part in ("roof_structure", "roof_covering"):
            name = roof.get("structure_material" if part == "roof_structure" else "covering_material") or (profile.get("composites") or {}).get(part)
            comp = composites.get(name)
            t = mr.total_thickness(comp["skins"]) if comp else _num(roof.get("thickness")) or 0.2
            if ctx.office is not None and not comp:
                plan["warnings"].append(f"roof {rid}: composite '{name}' not in the office file; thickness {t:.3f} m assumed")
            payload = {"level": round(base, 6), "polygonCoordinates": [pt(p) for p in boundary], "floorIndex": level["index"],
                       "levels": [{"levelHeight": 0.0, "levelAngle": angle}], "eavesOverhang": overhang}
            plan["roofs"].append({"key": f"{rid}:{'structure' if part == 'roof_structure' else 'covering'}", "model_id": rid, "role": part,
                                  "level_id": level["id"], "composite": name, "semantics": _semantics(part, profile), "payload": payload,
                                  "expect": {"z_min": round(base - overhang * math.tan(angle), 6)}})
            base += t / math.cos(angle)
        plan["notes"].append(f"roof {rid}: merge the parts at the eaves in Archicad (\"Elemente verschmelzen\" is not in the API)")


def _plan_din277(ctx: _Context) -> None:
    """Rule T6: one DIN 277 body per story along the outer contour, bottom = story level."""
    plan = ctx.plan
    for loop in plan["loops"]:
        if loop["role"] != "exterior_wall":
            continue
        level = ctx.levels[loop["level_id"]]
        nxt = ctx.next_level(level)
        top = nxt["elevation"] if nxt else (ctx.roof["top"] if ctx.roof else level["elevation"] + (level.get("floor_to_floor_height") or 3.0))
        ring, z0 = loop["outer_ring"], level["elevation"]
        count = sum(1 for m in plan["morphs"] if m["level_id"] == level["id"])
        plan["morphs"].append({"key": f"din277:{level['id']}" + (f":{count + 1}" if count else ""), "model_id": level["id"], "role": "din277_body", "level_id": level["id"],
                               "din277": "Regelfall", "semantics": _semantics("din277_body", ctx.profile),
                               "payload": {"basePoint": {"x": 0.0, "y": 0.0, "z": 0.0}, "floorIndex": level["index"],
                                           "displayOption": ctx.profile.get("din277_display", "OutLinesOnly"), "useCoverFillType": False,
                                           "body": _prism(ring, z0, top)},
                               "expect": {"z_min": round(z0, 6), "z_max": round(top, 6)}})


def _prism(ring: list, z0: float, z1: float) -> dict:
    """A closed morph body: bottom, top and one side face per edge (CreateMorphs body, live 29.09.2026)."""
    n = len(ring)
    vertices = [{"x": round(x, 6), "y": round(y, 6), "z": round(z0, 6)} for x, y in ring] + \
               [{"x": round(x, 6), "y": round(y, 6), "z": round(z1, 6)} for x, y in ring]
    polygons = [{"vertexIds": list(range(n - 1, -1, -1))}, {"vertexIds": [n + i for i in range(n)]}]
    polygons += [{"vertexIds": [i, (i + 1) % n, n + (i + 1) % n, n + i]} for i in range(n)]
    return {"bodyType": "Solid", "isClosed": True, "vertices": vertices, "polygons": polygons}


def _plan_technical_zones(ctx: _Context) -> None:
    """Guideline p.15/22: areas for building services as morphs, "Raumvorschlag", not load-bearing, inside."""
    plan = ctx.plan
    for tz in ctx.model.get("technical_zones") or []:
        tid = tz.get("id", "?")
        level = ctx.levels.get(tz.get("level_id"))
        ring = [tuple(p) for p in tz.get("boundary") or []]
        z0, z1 = _num(tz.get("bottom_elevation")), _num(tz.get("top_elevation"))
        if level is None or len(ring) < 3 or z0 is None or z1 is None or z1 <= z0:
            _skip(plan, tid, "technical zone", "level, boundary, bottom_elevation or top_elevation missing")
            continue
        if mr.signed_area(ring) < 0:
            ring = list(reversed(ring))
        plan["morphs"].append({"key": tid, "model_id": tid, "role": "technical_zone", "level_id": level["id"],
                               "building_material": (ctx.profile.get("morph_materials") or {}).get("technical_zone"),
                               "semantics": _semantics("technical_zone", ctx.profile),
                               "payload": {"basePoint": {"x": 0.0, "y": 0.0, "z": 0.0}, "floorIndex": level["index"],
                                           "body": _prism(ring, z0, z1)},
                               "expect": {"z_min": round(z0, 6), "z_max": round(z1, 6)}})


def _plan_site_areas(ctx: _Context) -> None:
    """Guideline p.33: plot areas as morph surfaces with "Flächenart nach DIN 277" (GF, AF, BF, UF)."""
    plan = ctx.plan
    lowest = ctx.ground or (ctx.ordered[0] if ctx.ordered else None)
    for area in ctx.model.get("site_areas") or []:
        aid, kind = area.get("id", "?"), str(area.get("kind") or "").upper()
        ring = [tuple(p) for p in area.get("boundary") or []]
        z = _num(area.get("elevation"))
        if kind not in ("GF", "AF", "BF", "UF"):
            _skip(plan, aid, "site area", f"kind '{kind}' unknown; DIN 277 plot areas are GF, AF, BF or UF")
            continue
        if lowest is None or len(ring) < 3 or z is None:
            _skip(plan, aid, "site area", "boundary or elevation missing")
            continue
        vertices = [{"x": round(x, 6), "y": round(y, 6), "z": round(z, 6)} for x, y in ring]
        plan["morphs"].append({"key": aid, "model_id": aid, "role": "site_area", "level_id": lowest["id"], "din277_area": kind,
                               "semantics": _semantics("site_area", ctx.profile),
                               "payload": {"basePoint": {"x": 0.0, "y": 0.0, "z": 0.0}, "floorIndex": lowest["index"],
                                           "displayOption": ctx.profile.get("din277_display", "OutLinesOnly"), "useCoverFillType": False,
                                           "body": {"bodyType": "Surface", "isClosed": False, "vertices": vertices,
                                                    "polygons": [{"vertexIds": list(range(len(ring)))}]}},
                               "expect": {"z_min": round(z, 6), "z_max": round(z, 6)}})


def _check_foundation_stories(ctx: _Context) -> None:
    """Rule A7: footings belong on their own story (guideline p.8)."""
    plan = ctx.plan
    building = {w["level_id"] for w in plan["walls"] if w["role"] not in FOUNDATION_ROLES} | {z["level_id"] for z in plan["zones"]}
    footings = [w for w in plan["walls"] if w["role"] in FOUNDATION_ROLES] + [c for c in plan["columns"] if c["role"] in FOUNDATION_ROLES]
    for f in footings:
        if f["level_id"] in building:
            ctx.once("warnings", f"footing {f['model_id']}: on level {f['level_id']} with walls or rooms; footings belong on their own story "
                                 "(guideline p.8)")


# --- office catalog -----------------------------------------------------------------------

def _version_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for piece in str(version).split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def readonly(send: Send) -> Send:
    """A sender that refuses everything but reads (dry runs against a live project)."""
    def guarded(command: str, params: dict) -> dict:
        if not command.startswith(READ_ONLY):
            raise BuildError(f"dry run: '{command}' would change the project; refused")
        return send(command, params)
    return guarded


def fetch_office(send: Send, profile: dict | None = None) -> dict[str, Any]:
    """Read the office catalog from the open project (read-only commands only)."""
    profile = profile or mr.OFFICE_PROFILE
    office: dict[str, Any] = {"tapir": send("GetAddOnVersion", {}).get("version", "?")}
    info = send("GetProjectInfo", {})
    office["project"] = info.get("projectName") or info.get("projectPath") or ("untitled" if info.get("isUntitled") else "?")
    st = send("GetStories", {})
    office["stories"] = [{"index": int(s["index"]), "level": float(s["level"]), "name": s.get("name", "")} for s in st.get("stories", [])]
    office["act_story"] = int(st.get("actStory", 0))
    office["story_items"] = _story_items(send)
    layers = send("GetAttributesByType", {"attributeType": "Layer"}).get("attributes", [])
    hidden: dict[str, bool] = {}
    if layers:
        for d in send("GetLayers", {"attributeIds": [{"attributeId": a["attributeId"]} for a in layers]}).get("layers", []):
            if "attributeId" in d:
                hidden[d["attributeId"]["guid"]] = bool(d.get("isHidden"))
    office["layers"] = {a["name"]: {"index": int(a["index"]), "hidden": hidden.get(a["attributeId"]["guid"], False)} for a in layers}
    mats = send("GetAttributesByType", {"attributeType": "BuildingMaterial"}).get("attributes", [])
    priority: dict[str, Any] = {}
    if mats:
        r = send("GetBuildingMaterials", {"attributeIds": [{"attributeId": a["attributeId"]} for a in mats]})
        for m in r.get("buildingMaterials", r.get("attributes", [])):
            if "attributeId" in m:
                priority[m["attributeId"]["guid"]] = m.get("connPriority")
    office["materials"] = {a["name"]: {"guid": a["attributeId"]["guid"], "priority": priority.get(a["attributeId"]["guid"])} for a in mats}
    names = {v["guid"]: k for k, v in office["materials"].items()}
    comps = send("GetAttributesByType", {"attributeType": "Composite"}).get("attributes", [])
    office["composites"] = {}
    if comps:
        for c in send("GetComposites", {"attributeIds": [{"attributeId": a["attributeId"]} for a in comps], "fields": ["skins"]}).get("composites", []):
            if "name" not in c:
                continue
            office["composites"][c["name"]] = {"guid": c["attributeId"]["guid"], "skins": [
                {"type": s.get("type"), "thickness": float(s.get("thickness", 0.0)),
                 "material": names.get(((s.get("buildingMaterialId") or {}).get("attributeId") or {}).get("guid"))} for s in c.get("skins", [])]}
    office["favorites"] = {t: send("GetFavoritesByType", {"elementType": t}).get("favorites", [])
                           for t in ("Wall", "Slab", "Zone", "Window", "Door", "Column", "Beam", "Roof", "Morph")}
    office["classification"] = _classification(send, profile)
    office["properties"] = _properties(send)
    cats = send("GetAttributesByType", {"attributeType": "ZoneCategory"}).get("attributes", [])
    office["zone_categories"] = {a["name"]: a["attributeId"]["guid"] for a in cats}
    office["zone_defaults"] = {"base_offset": profile.get("zone_base_offset")}
    office["north"] = ((send("GetGeoLocation", {}).get("projectLocation")) or {}).get("north")
    return office


def _story_items(send: Send) -> dict[str, str]:
    tree = send("GetNavigatorItemTree", {"navigatorMapId": "ProjectMap"}).get("navigatorItemTree", {})
    items: dict[str, str] = {}

    def walk(node: dict) -> None:
        item = node.get("navigatorItem", node)
        if item.get("type") == "StoryItem" and item.get("prefix") is not None:
            items[str(item["prefix"]).strip()] = item["navigatorItemId"]["guid"]
        for child in item.get("children") or []:
            walk(child)
    walk(tree)
    return items


def _classification(send: Send, profile: dict) -> dict[str, Any]:
    systems = send("API.GetAllClassificationSystems", {}).get("classificationSystems", [])
    prefix = profile.get("classification_system", "Archicad Klassifizierung")
    system = next((s for s in systems if str(s.get("name", "")).startswith(prefix)), None)
    if system is None:
        return {"system": None, "items": {}}
    guid = system["classificationSystemId"]["guid"]
    tree = send("API.GetAllClassificationsInSystem", {"classificationSystemId": {"guid": guid}}).get("classificationItems", [])
    items: dict[str, str] = {}

    def walk(entries: list, path: list[str]) -> None:
        for entry in entries:
            item = entry.get("classificationItem", entry)
            here = path + [item.get("id") or item.get("name") or "?"]
            items[" > ".join(here)] = item["classificationItemId"]["guid"]
            walk(item.get("children") or [], here)
    walk(tree, [])
    return {"system": {"guid": guid, "name": system.get("name")}, "items": items}


def _properties(send: Send) -> dict[str, str | None]:
    props = send("GetAllProperties", {}).get("properties", [])

    def enum_values(p: dict) -> set:
        return {e["enumValue"].get("nonLocalizedValue") for e in p.get("possibleEnumValues") or []}

    def find(pred: Callable[[dict], bool]) -> str | None:
        return next((p["propertyId"]["guid"] for p in props if pred(p)), None)

    guids = {p["propertyId"]["guid"].upper(): p["propertyId"]["guid"] for p in props}
    out = {
        "load_bearing": find(lambda p: {"LoadBearingElement", "NonLoadBearingElement"} <= enum_values(p)),
        "position": find(lambda p: {"Exterior", "Interior"} <= enum_values(p) and p.get("propertyType") == "DynamicBuiltIn"),
        "din277": find(lambda p: "DIN 277" in p.get("propertyName", "") and p.get("propertyType") == "DynamicBuiltIn"),
        "din277_area": find(lambda p: p.get("propertyName") == "Flächenart nach DIN 277"),
    }
    names = {"floor_thickness": ("Raum", "Fußbodendicke"), "clear_height": ("Raum", "Lichte Raumhöhe (Archicad 20)"),
             "top_offset": ("Allgemeine Parameter", "Abstand Oberkante"),
             "top_story": ("Allgemeine Parameter", "Relatives Geschoss für Oberkantenverknüpfung"),
             "opening_sill": ("Positionierung", "Öffnung Brüstungshöhe zu Projektursprung")}
    for key, guid in STATIC_PROPERTIES.items():
        group, name = names[key]
        out[key] = guids.get(guid.upper()) or find(lambda p, g=group, n=name: p.get("propertyGroupName") == g and p.get("propertyName") == n)
    return out


# --- execution --------------------------------------------------------------------------

def _count(send: Send, element_type: str) -> int:
    return len(send("GetElementsByType", {"elementType": element_type}).get("elements", []))


def _map_levels(plan: dict, stories: list[dict], report: dict) -> dict[str, int]:
    used = {rec["level_id"] for key, _ in PLAN_TYPES for rec in plan[key]}
    floor_map = {}
    for lv in plan["levels"]:
        match = next((s for s in stories if abs(float(s.get("level", 1e9)) - lv["elevation"]) < BBOX_TOL), None)
        if match is None:
            match = next((s for s in stories if str(s.get("name", "")).lower() == lv["name"].lower()), None)
            if match is not None:
                report["warnings"].append(f"level {lv['id']}: matched story '{match['name']}' by name, "
                                          f"elevation {match['level']} differs from {lv['elevation']}")
        if match is None:
            if lv["id"] in used:
                raise BuildError(f"no Archicad story at +{lv['elevation']:.2f} m for level {lv['id']}; "
                                 "create the story first (SetStories), nothing was sent")
            continue
        floor_map[lv["id"]] = int(match["index"])
    return floor_map


def _all_records(plan: dict) -> list[dict]:
    return [rec for key, _ in PLAN_TYPES for rec in plan[key]]


def _check_layers(plan: dict, office: dict, report: dict) -> None:
    layers = office.get("layers") or {}
    targets = {rec["semantics"].get("layer") for rec in _all_records(plan)} - {None}
    hidden = sorted(n for n in targets if (layers.get(n) or {}).get("hidden"))
    if hidden:
        raise BuildError(f"target layer(s) hidden: {', '.join(hidden)}; a hidden layer freezes elements (modify and delete report "
                         "success and change nothing). Show the layer first; nothing was sent")
    for name in sorted(n for n in targets if n not in layers):
        report["warnings"].append(f"layer '{name}' not in the office file; elements stay on the layer they are created on")


def _create(send: Send, command: str, array_key: str, items: list[tuple[dict, dict]], report: dict,
            element_type: str) -> tuple[dict[str, str], list[tuple[dict, dict]]]:
    """Send one batch; return plan key -> GUID for accepted items and the (record, error) pairs of rejected ones."""
    if not items:
        return {}, []
    try:
        response = send(command, {array_key: [payload for _, payload in items]})
    except TapirError as exc:
        report["errors"].append(f"{command} rejected the whole batch ({len(items)} items): {exc}")
        return {}, [(rec, {"message": str(exc)}) for rec, _ in items]
    results = response.get("elements", [])
    created, failed = {}, []
    for (rec, _), result in zip(items, results):
        if "elementId" in result:
            rec["guid"] = result["elementId"]["guid"]
            created[rec["key"]] = rec["guid"]
        else:
            failed.append((rec, result.get("error", {})))
    if len(results) < len(items):
        report["errors"].append(f"{command}: {len(items) - len(results)} items without a result")
        failed.extend((rec, {"message": "no result"}) for rec, _ in items[len(results):])
    report["created"][element_type] = report["created"].get(element_type, 0) + len(created)
    report["planned"][element_type] = report["planned"].get(element_type, 0) + len(items)
    report["guid_map"].update(created)
    return created, failed


def _details(send: Send, guid: str) -> dict:
    # one element per call: batched detail reads have hung for minutes on AC28/1.5.9 (VS:65)
    items = send("GetDetailsOfElements", {"elements": [{"elementId": {"guid": guid}}],
                                          "fields": ["type", "floorIndex", "layerIndex", "details"]}).get("detailsOfElements", [])
    return items[0] if items else {}


def _bbox(send: Send, guid: str) -> dict | None:
    items = send("Get3DBoundingBoxes", {"elements": [{"elementId": {"guid": guid}}]}).get("boundingBoxes3D", [])
    if not items or "error" in items[0]:
        return None
    return items[0].get("boundingBox3D", items[0])


def _bbox2d(send: Send, guid: str) -> dict | None:
    items = send("API.Get2DBoundingBoxes", {"elements": [{"elementId": {"guid": guid}}]}).get("boundingBoxes2D", [])
    if not items or "error" in items[0]:
        return None
    return items[0].get("boundingBox2D", items[0])


def _favorite_ok(rec: dict, payload: dict, office: dict, kind: str, missing: set) -> None:
    name = payload.get("favoriteName")
    if name and name not in (office.get("favorites") or {}).get(kind, []):
        payload.pop("favoriteName")
        missing.add((kind, name))


def _activate_story(send: Send, office: dict, story: int, report: dict) -> bool:
    """Rule R4: switch the floor plan to the story through its navigator item (ChangeWindow.storyIndex does not, live 29.09.2026)."""
    nav = (office.get("story_items") or {}).get(str(story))
    if nav is None:
        report["errors"].append(f"story {story}: no navigator item to activate it")
        return False
    send("ChangeWindow", {"navigatorItemId": {"guid": nav}})
    active = send("GetStories", {}).get("actStory")
    if active != story:
        report["errors"].append(f"story {story} could not be activated (active story {active})")
        return False
    return True


def run(model: dict, send: Send, material_map: dict | None = None, window_favorite: str | None = None,
        door_favorite: str | None = None, zones: str = "auto", allow_manual_zones: bool = False,
        profile: dict | None = None, din277: bool = False) -> dict[str, Any]:
    """Live run: guards, office catalog, plan, build, read-back. Raises BuildError before any change if a guard fails."""
    version = send("GetAddOnVersion", {}).get("version", "?")
    if _version_tuple(version) < MIN_TAPIR:
        raise BuildError(f"Tapir {version} is too old; the rule mode needs >= 1.5.9 (read-back of flipped, reference line and "
                         "top link); nothing was sent")
    warnings = []
    # Tapir counts only the active database: in a section or 3D window every element count reads 0
    window = send("GetCurrentWindowType", {}).get("currentWindowType")
    if window != "FloorPlan":
        send("ChangeWindow", {"windowType": "FloorPlan", "storyIndex": -1})
        if send("GetCurrentWindowType", {}).get("currentWindowType") != "FloorPlan":
            raise BuildError(f"active window is {window} and could not be switched to the floor plan; nothing was sent")
        warnings.append(f"active window was {window}; switched to the floor plan so element counts are valid")
    office = fetch_office(send, profile)
    plan = build_plan(model, office, material_map, window_favorite, door_favorite, zones, allow_manual_zones, profile, din277)
    if plan["errors"]:
        raise BuildError("the plan has errors, nothing was sent: " + "; ".join(plan["errors"]))
    report = execute(plan, send, office)
    report["warnings"] = warnings + report["warnings"]
    return report


def execute(plan: dict, send: Send, office: dict) -> dict[str, Any]:
    """Create the planned elements in the open project, apply the semantics and verify every rule by read-back."""
    report: dict[str, Any] = {"ok": True, "errors": [], "warnings": list(plan["warnings"]), "notes": list(plan["notes"]),
                              "created": {}, "planned": {}, "failed": [], "guid_map": {}, "zone_fallbacks": 0, "checks": {},
                              "tapir": office.get("tapir"), "project": office.get("project"), "plan": plan}
    floor_map = _map_levels(plan, office.get("stories") or [], report)
    zero = next((s for s in office.get("stories") or [] if abs(float(s.get("level", 1.0))) < 0.005), None)
    if zero is not None and int(zero["index"]) != 0:
        report["warnings"].append(f"story '{zero['name']}' on 0.00 has index {zero['index']}; office convention: the story on +-0.00 "
                                  "is index 0, basements negative (rule A6)")
    _check_layers(plan, office, report)
    north = office.get("north")
    if north is not None and abs(float(north) - math.pi / 2) > 1e-3:
        report["warnings"].append(f"project north is {math.degrees(float(north)):.2f}°, the model assumes 90° (rule A3)")
    before = {etype: _count(send, etype) for etype in COUNT_TYPES}
    missing_favorites: set = set()
    walls = _build_walls(plan, send, office, floor_map, report, missing_favorites)
    _build_slabs(plan["slabs"], send, office, floor_map, report, missing_favorites)
    _build_openings(plan, send, office, walls, report, missing_favorites)
    _build_host_openings(plan, send, report)
    _build_members(plan, send, office, floor_map, report, missing_favorites)
    _build_zones(plan, send, office, floor_map, report, missing_favorites)
    _build_room_slabs(plan, "buildups", send, office, floor_map, report, missing_favorites)
    _build_room_slabs(plan, "ceilings", send, office, floor_map, report, missing_favorites)
    for kind, name in sorted(missing_favorites):
        report["warnings"].append(f"{kind} favorite '{name}' not found in the project; the tool default is used")
    _write_semantics(plan, send, office, report)
    _verify(plan, send, office, report, before)
    report["failed"] = len(report["failed"])
    report["ok"] = not report["errors"]
    return report


def check(plan: dict, send: Send, profile: dict | None = None) -> dict[str, Any]:
    """Re-check a finished build (the plan inside --report-out) against every rule, read-only."""
    office = fetch_office(send, profile)
    report: dict[str, Any] = {"ok": True, "errors": [], "warnings": [], "notes": [], "created": {}, "planned": {}, "failed": 0,
                              "guid_map": {r["key"]: r["guid"] for r in _created(plan)}, "zone_fallbacks": 0, "checks": {},
                              "tapir": office.get("tapir"), "project": office.get("project")}
    _verify(plan, send, office, report, None)
    report["ok"] = not report["errors"]
    return report


def _build_walls(plan, send, office, floor_map, report, missing) -> dict[str, dict]:
    items = []
    for w in plan["walls"]:
        payload = copy.deepcopy(w["payload"])
        payload["floorIndex"] = floor_map[w["level_id"]]
        comp = (office.get("composites") or {}).get(w["composite"] or "")
        basic = (office.get("materials") or {}).get(w["building_material"] or w["material"] or "")
        if comp:
            payload["structureType"], payload["compositeId"] = "Composite", {"guid": comp["guid"]}
        elif basic:
            payload["structureType"], payload["buildingMaterialId"] = "Basic", {"guid": basic["guid"]}
        _favorite_ok(w, payload, office, "Wall", missing)
        w["sent"] = payload
        items.append((w, payload))
    _, failed = _create(send, "CreateWalls", "wallsData", items, report, "Wall")
    for rec, err in failed:
        report["errors"].append(f"wall {rec['model_id']} ({rec['key']}): Tapir {err.get('code')} {err.get('message', '')}".strip())
    mods = []
    for w in plan["walls"]:
        if not w.get("guid"):
            continue
        d = _details(send, w["guid"]).get("details", {})
        # the exterior face is LEFT of the drawing direction when not flipped, RIGHT when flipped (live 29.09.2026);
        # the plan draws exterior walls with the interior on the left, which needs a flipped wall
        w["swapped"] = w["interior_left"] is not None and not d.get("flipped", True)
        item: dict[str, Any] = {"elementId": {"guid": w["guid"]}}
        if w["swapped"]:
            item["begCoordinate"], item["endCoordinate"] = w["sent"]["endCoordinate"], w["sent"]["begCoordinate"]
        if w["top_link"]:
            item.update(w["top_link"])
        if w.get("zone_rel"):
            item["zoneRel"] = w["zone_rel"]
        if len(item) > 1:
            mods.append(item)
    if mods:
        results = send("ModifyWalls", {"wallsWithDetails": mods}).get("executionResults", [])
        for item, res in zip(mods, results):
            if not res.get("success", False):
                report["errors"].append(f"ModifyWalls failed for {item['elementId']['guid']}: {res.get('error')}")
    return {w["key"]: w for w in plan["walls"]}


def _build_slabs(slabs: list[dict], send, office, floor_map, report, missing) -> None:
    items = []
    for s in slabs:
        payload = copy.deepcopy(s["payload"])
        payload["floorIndex"] = floor_map[s["level_id"]]
        _favorite_ok(s, payload, office, "Slab", missing)
        s["sent"] = payload
        items.append((s, payload))
    _, failed = _create(send, "CreateSlabs", "slabsData", items, report, "Slab")
    for rec, err in failed:
        report["errors"].append(f"slab {rec['model_id']}: Tapir {err.get('code')} {err.get('message', '')}".strip())
    mods = []
    for s in slabs:
        if not s.get("guid") or s["sent"].get("favoriteName") or not s.get("material"):
            continue
        comp = (office.get("composites") or {}).get(s["material"])
        basic = (office.get("materials") or {}).get(s["material"])
        if comp:
            mods.append({"elementId": {"guid": s["guid"]}, "structureType": "Composite", "compositeId": {"guid": comp["guid"]}})
        elif basic:
            mods.append({"elementId": {"guid": s["guid"]}, "structureType": "Basic", "buildingMaterialId": {"guid": basic["guid"]}})
    if mods:
        send("ModifySlabs", {"slabsWithDetails": mods})


def _build_openings(plan, send, office, walls, report, missing) -> None:
    for key, etype, command, array_key in (("windows", "Window", "CreateWindows", "windowsData"), ("doors", "Door", "CreateDoors", "doorsData")):
        items = []
        for op in plan[key]:
            host = walls.get(op["host_key"])
            if not host or not host.get("guid"):
                report["errors"].append(f"{key[:-1]} {op['model_id']} not placed: host wall {op['host_key']} was not created")
                continue
            swapped = bool(host.get("swapped"))
            payload = copy.deepcopy(op["payload"])
            payload["ownerWallId"] = {"guid": host["guid"]}
            payload["centerOffset"] = round(host["length"] - op["center_offset"] if swapped else op["center_offset"], 6)
            interior_left = None if op["interior_left"] is None else (op["interior_left"] != swapped)
            # oSide = true puts the swing LEFT of the host wall direction, whatever the flip state (live 29.09.2026)
            if op["swing"] == "inward" and interior_left is not None:
                payload["oSide"] = interior_left
            elif op["swing"] == "outward" and interior_left is not None:
                payload["oSide"] = not interior_left
            op["interior_left_final"] = interior_left
            _favorite_ok(op, payload, office, etype, missing)
            op["sent"] = payload
            items.append((op, payload))
        _, failed = _create(send, command, array_key, items, report, etype)
        for rec, err in failed:
            report["errors"].append(f"{key[:-1]} {rec['model_id']}: Tapir {err.get('code')} {err.get('message', '')}".strip())


def _build_zones(plan, send, office, floor_map, report, missing) -> None:
    by_story: dict[int, list[dict]] = {}
    for z in plan["zones"]:
        by_story.setdefault(floor_map[z["level_id"]], []).append(z)
    cats = office.get("zone_categories") or {}
    for story in sorted(by_story):
        zones = by_story[story]
        if not _activate_story(send, office, story, report):
            for z in zones:
                report["errors"].append(f"zone {z['model_id']}: not created, story {story} could not be activated")
            continue
        items = []
        for z in zones:
            payload = copy.deepcopy(z["payload"])
            payload["floorIndex"] = story
            if z.get("use") in cats:
                payload["categoryAttributeId"] = {"guid": cats[z["use"]]}
            _favorite_ok(z, payload, office, "Zone", missing)
            z["sent"] = payload
            items.append((z, payload))
        _, failed = _create(send, "CreateZones", "zonesData", items, report, "Zone")
        retry = []
        for z, err in failed:
            if z.get("fallback_geometry") and "referencePosition" in z["sent"]["geometry"]:
                payload = copy.deepcopy(z["sent"])
                payload["geometry"] = z["fallback_geometry"]
                retry.append((z, payload))
                report["planned"]["Zone"] -= 1
            else:
                report["errors"].append(f"zone {z['model_id']}: Archicad found no closed wall ring around the seed point "
                                        f"({err.get('code')}); close the walls — rooms are never drawn by hand (rule R3)")
        if retry:
            made, still = _create(send, "CreateZones", "zonesData", retry, report, "Zone")
            report["zone_fallbacks"] += len(made)
            for z, _ in retry:
                if z["key"] in made:
                    z["manual"] = True
                    report["warnings"].append(f"zone {z['model_id']}: no closed wall ring; created as a manual polygon "
                                              "(--allow-manual-zones, not associative)")
            for z, err in still:
                report["errors"].append(f"zone {z['model_id']}: manual polygon rejected too ({err.get('message', '')})")
    _activate_story(send, office, int(office.get("act_story", 0)), report)
    values = []
    props = office.get("properties") or {}
    for z in plan["zones"]:
        if not z.get("guid"):
            continue
        for key, value in z["zone_properties"].items():
            if not props.get(key):
                report["warnings"].append(f"zone property '{key}' not found in the project; not set")
                continue
            values.append({"elementId": {"guid": z["guid"]}, "propertyId": {"guid": props[key]},
                           "propertyValue": {"type": "length", "status": "normal", "value": value}})
    if values:
        results = send("API.SetPropertyValuesOfElements", {"elementPropertyValues": values}).get("executionResults", [])
        for v, res in zip(values, results):
            if not res.get("success", False):
                report["errors"].append(f"zone property {v['propertyId']['guid']} not set: {res.get('error')}")


def _zone_polygon(send: Send, guid: str) -> list[dict]:
    poly = _details(send, guid).get("details", {}).get("polygonOutline") or []
    if len(poly) > 3 and abs(poly[0]["x"] - poly[-1]["x"]) < 1e-6 and abs(poly[0]["y"] - poly[-1]["y"]) < 1e-6:
        poly = poly[:-1]
    return [pt((p["x"], p["y"])) for p in poly]


def _build_room_slabs(plan, key, send, office, floor_map, report, missing) -> None:
    """Floor build-ups and suspended ceilings: one slab per room, outline = the room polygon Archicad computed."""
    label = {"buildups": "floor build-up", "ceilings": "suspended ceiling"}[key]
    zones = {z["key"]: z for z in plan["zones"]}
    items = []
    for b in plan[key]:
        zone = zones.get(b["zone_key"])
        if not zone or not zone.get("guid"):
            report["warnings"].append(f"{label} {b['model_id']} not placed: its room was not created")
            continue
        payload = copy.deepcopy(b["payload"])
        polygon = _zone_polygon(send, zone["guid"])
        if len(polygon) >= 3:
            payload["polygonCoordinates"] = polygon
        else:
            report["warnings"].append(f"{label} {b['model_id']}: room outline not readable; model boundary used")
        if b.get("holes"):
            payload["holes"] = [{"polygonCoordinates": h} for h in b["holes"]]
        payload["floorIndex"] = floor_map[b["level_id"]]
        _favorite_ok(b, payload, office, "Slab", missing)
        b["sent"] = payload
        items.append((b, payload))
    _, failed = _create(send, "CreateSlabs", "slabsData", items, report, "Slab")
    for rec, err in failed:
        report["errors"].append(f"{label} {rec['model_id']}: Tapir {err.get('code')} {err.get('message', '')}".strip())
    mods = []
    for b in plan[key]:
        comp = (office.get("composites") or {}).get(b.get("composite") or "")
        if b.get("guid") and comp and not (b.get("sent") or {}).get("favoriteName"):
            mods.append({"elementId": {"guid": b["guid"]}, "structureType": "Composite", "compositeId": {"guid": comp["guid"]}})
        elif b.get("guid") and b.get("composite") and not comp:
            report["warnings"].append(f"{label} {b['model_id']}: composite '{b['composite']}' not in the office file")
    if mods:
        send("ModifySlabs", {"slabsWithDetails": mods})


def _build_host_openings(plan, send, report) -> None:
    """Rules D9, E9: openings in walls and raw slabs, one item per call (a batch created nothing live, VS:117)."""
    hosts = {w["key"]: w for w in plan["walls"]}
    hosts.update({s["key"]: s for s in plan["slabs"]})
    for op in plan["openings"]:
        host = hosts.get(op["host_key"])
        if not host or not host.get("guid"):
            report["errors"].append(f"opening {op['model_id']} not placed: host {op['host_key']} was not created")
            continue
        payload = copy.deepcopy(op["payload"])
        payload["ownerElementId"] = {"guid": host["guid"]}
        op["sent"] = payload
        _, failed = _create(send, "CreateOpenings", "openingsData", [(op, payload)], report, "Opening")
        for rec, err in failed:
            report["errors"].append(f"opening {rec['model_id']}: Tapir {err.get('code')} {err.get('message', '')}".strip())


def _build_members(plan, send, office, floor_map, report, missing) -> None:
    """Columns, beams, roofs and DIN 277 bodies."""
    materials, composites = office.get("materials") or {}, office.get("composites") or {}
    for key, etype, command, array_key in (("columns", "Column", "CreateColumns", "columnsData"), ("beams", "Beam", "CreateBeams", "beamsData"),
                                           ("roofs", "Roof", "CreateRoofs", "roofsData"), ("morphs", "Morph", "CreateMorphs", "morphsData")):
        items = []
        for rec in plan[key]:
            payload = copy.deepcopy(rec["payload"])
            payload["floorIndex"] = floor_map[rec["level_id"]]
            if rec.get("building_material"):
                basic = materials.get(rec["building_material"])
                if basic:
                    payload["buildingMaterialId"] = {"guid": basic["guid"]}
                else:
                    report["warnings"].append(f"{etype.lower()} {rec['model_id']}: building material '{rec['building_material']}' not found")
            if key == "roofs":
                comp = composites.get(rec["composite"]) if rec.get("composite") else None
                if comp:
                    payload["structureType"], payload["compositeId"] = "Composite", {"guid": comp["guid"]}
                else:  # a composite roof tool default would otherwise override the sent thickness (live 02.10.2026)
                    payload["structureType"] = "Basic"
            if etype in ("Column", "Beam"):
                _favorite_ok(rec, payload, office, etype, missing)
            rec["sent"] = payload
            items.append((rec, payload))
        _, failed = _create(send, command, array_key, items, report, etype)
        for rec, err in failed:
            report["errors"].append(f"{etype.lower()} {rec['model_id']}: Tapir {err.get('code')} {err.get('message', '')}".strip())


def _created(plan: dict) -> list[dict]:
    return [rec for rec in _all_records(plan) if rec.get("guid")]


def _enum_value(guid: str, prop: str, value: str) -> dict:
    return {"elementId": {"guid": guid}, "propertyId": {"guid": prop},
            "propertyValue": {"type": "singleEnum", "status": "normal", "value": {"type": "nonLocalizedValue", "nonLocalizedValue": value}}}


def _write_semantics(plan, send, office, report) -> None:
    """Rules B1, B2, B5: classification, Tragende Funktion / Lage (language-neutral, official API), layer by name."""
    cls = office.get("classification") or {}
    system, items = (cls.get("system") or {}).get("guid"), cls.get("items") or {}
    props = office.get("properties") or {}
    layers = office.get("layers") or {}
    classes, values, layer_items, tapir_values = [], [], [], []
    for rec in _created(plan):
        sem = rec["semantics"]
        path = sem.get("classification")
        if path:
            item = items.get(path)
            if system and item:
                classes.append({"elementId": {"guid": rec["guid"]}, "classificationId": {"classificationSystemId": {"guid": system},
                                                                                         "classificationItemId": {"guid": item}}})
            else:
                report["errors"].append(f"{rec['key']}: classification '{path}' missing in the office classification system")
        tool = mr.ROLES[rec["role"] if rec.get("role") in mr.ROLES else "space"].tool
        if tool != "Zone":
            # "Tragende Funktion" is read-only on openings (6800, live 29.09.2026); the guideline gives them only "Lage"
            if props.get("load_bearing") and tool != "Opening":
                values.append(_enum_value(rec["guid"], props["load_bearing"], mr.LOAD_BEARING_VALUE[sem.get("load_bearing")]))
            if props.get("position"):
                values.append(_enum_value(rec["guid"], props["position"], mr.POSITION_VALUE[sem.get("position")]))
        if rec.get("din277_area") and props.get("din277_area"):
            tapir_values.append({"elementId": {"guid": rec["guid"]}, "propertyId": {"guid": props["din277_area"]},
                                 "propertyValue": {"value": rec["din277_area"]}})
        if rec.get("din277") and props.get("din277"):
            # "Klassifizierung nach DIN 277": the official API does not support it (6702, live 29.09.2026); Tapir takes the
            # display value, which has no umlaut ("Regelfall"/"Sonderfall")
            tapir_values.append({"elementId": {"guid": rec["guid"]}, "propertyId": {"guid": props["din277"]},
                                 "propertyValue": {"value": rec["din277"]}})
        layer = layers.get(sem.get("layer") or "")
        if layer:
            layer_items.append({"elementId": {"guid": rec["guid"]}, "details": {"layerIndex": layer["index"]}})
    for command, key, batch in (("SetClassificationsOfElements", "elementClassifications", classes),
                                ("API.SetPropertyValuesOfElements", "elementPropertyValues", values),
                                ("SetPropertyValuesOfElements", "elementPropertyValues", tapir_values),
                                ("SetDetailsOfElements", "elementsWithDetails", layer_items)):
        if not batch:
            continue
        results = send(command, {key: batch}).get("executionResults", [])
        failures = [r for r in results if not r.get("success", False)]
        if failures:
            report["errors"].append(f"{command}: {len(failures)} of {len(batch)} items rejected ({failures[0].get('error')})")
    if not props.get("load_bearing") or not props.get("position"):
        report["errors"].append("properties 'Tragende Funktion'/'Lage' not found in the project; rule B2 not applied")


def _read_classes(send: Send, guids: list[str], system: str) -> dict[str, str | None]:
    out = {}
    for i in range(0, len(guids), 25):
        chunk = guids[i:i + 25]
        res = send("GetClassificationsOfElements", {"elements": [{"elementId": {"guid": g}} for g in chunk],
                                                    "classificationSystemIds": [{"classificationSystemId": {"guid": system}}]})
        for g, entry in zip(chunk, res.get("elementClassifications", [])):
            ids = entry.get("classificationIds") or [{}]
            out[g] = (ids[0].get("classificationItemId") or {}).get("guid")
    return out


def _read_props(send: Send, guids: list[str], prop_ids: list[str]) -> dict[str, list[Any]]:
    out = {}
    for i in range(0, len(guids), 25):
        chunk = guids[i:i + 25]
        res = send("API.GetPropertyValuesOfElements", {"elements": [{"elementId": {"guid": g}} for g in chunk],
                                                       "properties": [{"propertyId": {"guid": p}} for p in prop_ids]})
        for g, entry in zip(chunk, res.get("propertyValuesForElements", [])):
            vals = []
            for v in entry.get("propertyValues", []):
                # enum: {"type":"singleEnum","value":{"type":"nonLocalizedValue","nonLocalizedValue":...}}; length: {"value": 0.15}
                value = (v.get("propertyValue") or {}).get("value")
                if isinstance(value, dict):
                    value = value.get("nonLocalizedValue", value.get("displayValue"))
                vals.append(value)
            out[g] = vals
    return out


def _verify(plan, send, office, report, before) -> None:
    checks: dict[str, dict[str, int]] = {}

    def check(rule: str, ok: bool, message: str) -> None:
        entry = checks.setdefault(rule, {"passed": 0, "failed": 0})
        if ok:
            entry["passed"] += 1
        else:
            entry["failed"] += 1
            report["errors"].append(f"{message} (rule {rule})")

    if before is not None:  # a re-check (check()) has no count baseline
        for etype in COUNT_TYPES:
            delta, made = _count(send, etype) - before[etype], report["created"].get(etype, 0)
            check("V8", delta == made, f"{etype} count +{delta}, expected +{made}: Archicad accepted items without creating them")
    recs = _created(plan)
    cls = office.get("classification") or {}
    system, items = (cls.get("system") or {}).get("guid"), cls.get("items") or {}
    if system:
        got = _read_classes(send, [r["guid"] for r in recs], system)
        for r in recs:
            want = items.get(r["semantics"].get("classification") or "")
            if want:
                check("B1", got.get(r["guid"]) == want, f"{r['key']}: classification '{r['semantics']['classification']}' not applied")
    props = office.get("properties") or {}
    enum_recs = [r for r in recs if mr.ROLES.get(r.get("role") or "space", mr.ROLES["space"]).tool != "Zone"]
    if props.get("load_bearing") and props.get("position") and enum_recs:
        got = _read_props(send, [r["guid"] for r in enum_recs], [props["load_bearing"], props["position"]])
        for r in enum_recs:
            lb, pos = (got.get(r["guid"]) or [None, None])[:2]
            want_lb, want_pos = mr.LOAD_BEARING_VALUE[r["semantics"].get("load_bearing")], mr.POSITION_VALUE[r["semantics"].get("position")]
            if mr.ROLES.get(r.get("role") or "space", mr.ROLES["space"]).tool != "Opening":
                check("B2", lb == want_lb, f"{r['key']}: Tragende Funktion reads {lb}, rule wants {want_lb}")
            check("B2", pos == want_pos, f"{r['key']}: position (Lage) reads {pos}, rule wants {want_pos}")
    zone_recs = [z for z in plan["zones"] if z.get("guid")]
    if zone_recs and props.get("floor_thickness"):
        got = _read_props(send, [z["guid"] for z in zone_recs], [props["floor_thickness"]])
        for z in zone_recs:
            value = (got.get(z["guid"]) or [None])[0]
            want = z["zone_properties"]["floor_thickness"]
            check("R6", isinstance(value, (int, float)) and abs(value - want) <= 0.001,
                  f"zone {z['key']}: floor thickness reads {value}, rule wants {want:.3f}")
    layers = office.get("layers") or {}
    loops = {k: lp for lp in plan["loops"] for k in lp["keys"]}
    kind_of = {id(r): key for key, _ in PLAN_TYPES for r in plan[key]}
    sills: dict[str, Any] = {}
    wall_openings = [o for o in plan["openings"] if o.get("guid") and o.get("host_kind") == "wall"]
    if wall_openings and props.get("opening_sill"):
        sills = {g: (v or [None])[0] for g, v in _read_props(send, [o["guid"] for o in wall_openings], [props["opening_sill"]]).items()}
    z_rules = {"slabs": "D1", "buildups": "D4", "ceilings": "D8", "windows": "E1", "doors": "E1", "columns": "T1", "morphs": "T6"}
    morph_rule = {"din277_body": "T6", "technical_zone": "T7", "site_area": "T8"}
    for r in recs:
        kind = kind_of.get(id(r))
        info = _details(send, r["guid"])
        d = info.get("details", {})
        layer = layers.get(r["semantics"].get("layer") or "")
        if layer:
            check("B5", int(info.get("layerIndex", -1)) == layer["index"], f"{r['key']}: layer {info.get('layerIndex')} is not "
                  f"'{r['semantics']['layer']}' ({layer['index']})")
        box = _bbox(send, r["guid"]) if kind != "openings" else None
        exp = r.get("expect") or {}
        if kind == "slabs" and d.get("polygonOutline") is not None:
            # rules D2/D3: the edge the rule set (core faces of the exterior walls) is the edge Archicad holds
            got = [(p["x"], p["y"]) for p in d["polygonOutline"]]
            if len(got) > 3 and dist(got[0], got[-1]) < 1e-6:
                got = got[:-1]
            want = [(p["x"], p["y"]) for p in (r.get("sent") or r["payload"])["polygonCoordinates"]]
            same = len(got) == len(want) and all(min(dist(p, q) for q in got) <= BBOX_TOL for p in want)
            check("D2", same, f"slab {r['key']}: outline {[(round(x, 3), round(y, 3)) for x, y in got][:4]} differs from the planned "
                  f"edge {[(round(x, 3), round(y, 3)) for x, y in want][:4]}")
        if kind == "walls":
            _verify_wall(r, d, box, loops.get(r["key"]), office, check)
        elif kind == "openings":
            if r.get("host_kind") == "wall" and props.get("opening_sill"):
                sill = sills.get(r["guid"])
                check("E9", isinstance(sill, (int, float)) and abs(sill - exp["sill_abs"]) <= Z_TOL,
                      f"opening {r['key']}: sill at {sill} m, rule wants {exp['sill_abs']:.3f} m above the project zero")
            elif r.get("host_kind") == "slab":
                b2 = _bbox2d(send, r["guid"])
                x0, y0, x1, y1 = exp["rect"]
                check("D9", bool(b2) and all(abs(a - b) <= BBOX_TOL for a, b in zip((b2["xMin"], b2["yMin"], b2["xMax"], b2["yMax"]), (x0, y0, x1, y1))),
                      f"slab opening {r['key']}: outline {b2} differs from {exp['rect']}")
        elif kind == "beams":
            beg, end = d.get("begCoordinate"), d.get("endCoordinate")
            length = dist(_xy(beg), _xy(end)) if beg and end else None
            check("T2", length is not None and abs(length - exp["length"]) <= BBOX_TOL,
                  f"beam {r['key']}: length {length if length is None else round(length, 3)} m, the model says {exp['length']:.3f} m "
                  "(fixed segment length in the beam tool?)")
            if box:
                check("T2", abs(box["zMax"] - exp["z_max"]) <= Z_TOL and abs(box["zMin"] - exp["z_min"]) <= Z_TOL,
                      f"beam {r['key']}: z {box['zMin']:.3f}..{box['zMax']:.3f} m, rule wants {exp['z_min']:.3f}..{exp['z_max']:.3f} m")
        elif kind == "roofs":
            if box and exp.get("z_min") is not None:
                check("T4", abs(box["zMin"] - exp["z_min"]) <= Z_TOL, f"roof {r['key']}: lowest point {box['zMin']:.3f} m, rule wants "
                      f"{exp['z_min']:.3f} m")
        elif kind == "zones":
            check("R2", d.get("isManual") is False or r.get("manual"), f"zone {r['key']}: manual polygon, not associative")
            poly = [(p["x"], p["y"]) for p in d.get("polygonOutline") or []]
            if len(poly) > 3 and poly[0] == poly[-1]:
                poly = poly[:-1]
            if poly and r.get("area"):
                area = abs(mr.signed_area(poly))
                check("R7", abs(area - r["area"]) <= 0.02 * r["area"], f"zone {r['key']}: area {area:.2f} m² vs {r['area']:.2f} m² in the model")
            if box and exp.get("z_max") is not None:
                check("R5", abs(box["zMax"] - exp["z_max"]) <= Z_TOL, f"zone {r['key']}: top at {box['zMax']:.3f} m, rule wants "
                      f"{exp['z_max']:.3f} m (UK Rohdecke)")
        elif box and exp and kind in z_rules and exp.get("z_max") is not None:
            rule = morph_rule.get(r.get("role"), "T6") if kind == "morphs" else z_rules[kind]
            check(rule, abs(box["zMax"] - exp["z_max"]) <= Z_TOL and abs(box["zMin"] - exp["z_min"]) <= Z_TOL,
                  f"{kind[:-1]} {r['key']}: z {box['zMin']:.3f}..{box['zMax']:.3f} m, rule wants {exp['z_min']:.3f}..{exp['z_max']:.3f} m")
        if kind == "doors" and r.get("swing") and r.get("interior_left_final") is not None:
            _verify_swing(r, send, plan, check)
    for field, rule, label in (("din277", "T6", "Klassifizierung nach DIN 277"), ("din277_area", "T8", "Flächenart nach DIN 277")):
        morphs = [m for m in plan["morphs"] if m.get("guid") and m.get(field)]
        if not morphs or not props.get(field):
            continue
        res = send("GetPropertyValuesOfElements", {"elements": [{"elementId": {"guid": m["guid"]}} for m in morphs],
                                                   "properties": [{"propertyId": {"guid": props[field]}}]})
        for m, entry in zip(morphs, res.get("propertyValuesForElements", [])):
            value = ((entry.get("propertyValues") or [{}])[0].get("propertyValue") or {}).get("value")
            check(rule, value == m[field], f"morph {m['key']}: '{label}' reads {value}, rule wants {m[field]}")
    report["checks"] = checks


def _verify_wall(w: dict, d: dict, box: dict | None, loop: dict | None, office: dict, check) -> None:
    sent = w.get("sent") or {}
    if d.get("structureType") != "Profile" or w["exterior"]:  # a profile wall takes its reference line from the profile (live)
        check("C1" if w["exterior"] else "C6", d.get("referenceLineLocation") == sent.get("referenceLineLocation"),
              f"wall {w['key']}: reference line {d.get('referenceLineLocation')}, rule wants {sent.get('referenceLineLocation')}")
    if sent.get("structureType") == "Composite":
        check("B6", d.get("structureType") == "Composite" and (d.get("compositeId") or {}).get("guid") == sent["compositeId"]["guid"],
              f"wall {w['key']}: composite '{w['composite']}' not applied (reads {d.get('structureType')})")
    if w.get("zone_rel"):
        check("C13", d.get("zoneRel") == w["zone_rel"], f"wall {w['key']}: relation to the room is {d.get('zoneRel')}, "
              f"rule wants {w['zone_rel']} (subtract from room area and volume)")
    if w["top_link"]:
        link = w["top_link"]
        check("C3", int(d.get("relativeTopStory") or 0) == link["relativeTopStory"] and abs(float(d.get("topOffset") or 0) - link["topOffset"]) <= 0.001,
              f"wall {w['key']}: top link not applied (relativeTopStory {d.get('relativeTopStory')}, topOffset {d.get('topOffset')})")
    if box:
        exp = w["expect"]
        check("C3", abs(box["zMin"] - exp["z_min"]) <= Z_TOL and abs(box["zMax"] - exp["z_max"]) <= Z_TOL,
              f"wall {w['key']}: z {box['zMin']:.3f}..{box['zMax']:.3f} m, rule wants foot {exp['z_min']:.3f} and top {exp['z_max']:.3f} m")
        if loop is not None:
            x0, y0, x1, y1 = loop["bbox"]
            check("C2", not (box["xMin"] < x0 - BBOX_TOL or box["yMin"] < y0 - BBOX_TOL or box["xMax"] > x1 + BBOX_TOL
                             or box["yMax"] > y1 + BBOX_TOL),
                  f"wall {w['key']}: body protrudes the outer contour; drawing direction or reference line is wrong")


def _verify_swing(op: dict, send: Send, plan: dict, check) -> None:
    """Rule E4: the door's plan outline (swing arc) must reach out on the side it opens to."""
    host = next(w for w in plan["walls"] if w["key"] == op["host_key"])
    box = _bbox2d(send, op["guid"])
    if not box:
        return
    beg, end = _xy(host["sent"]["begCoordinate"]), _xy(host["sent"]["endCoordinate"])
    if host.get("swapped"):
        beg, end = end, beg
    u = mr.unit(beg, end)
    left = mr.left_normal(u)
    c = op["sent"]["centerOffset"]
    p = (beg[0] + u[0] * c, beg[1] + u[1] * c)
    corners = [(box["xMin"], box["yMin"]), (box["xMin"], box["yMax"]), (box["xMax"], box["yMin"]), (box["xMax"], box["yMax"])]
    reach_left = max((q[0] - p[0]) * left[0] + (q[1] - p[1]) * left[1] for q in corners)
    reach_right = max(-((q[0] - p[0]) * left[0] + (q[1] - p[1]) * left[1]) for q in corners)
    opens_left = reach_left > reach_right
    wants_left = op["interior_left_final"] if op["swing"] == "inward" else not op["interior_left_final"]
    check("E4", opens_left == wants_left, f"door {op['key']}: swing drawn to the {'left' if opens_left else 'right'} of the wall, "
          f"rule wants {op['swing']}")


# --- transport and CLI ------------------------------------------------------------------

def make_envelope(command: str, params: dict) -> dict:
    if command.startswith("API."):
        return {"command": command, "parameters": params}
    return {"command": "API.ExecuteAddOnCommand",
            "parameters": {"addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": command},
                           "addOnCommandParameters": params}}


def http_sender(host: str, port: int, timeout: float = 120.0) -> Send:
    url = f"http://{host}:{port}"

    def send(command: str, params: dict) -> dict:
        request = urllib.request.Request(url, data=json.dumps(make_envelope(command, params)).encode("utf-8"),
                                         headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                answer = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError) as exc:
            raise BuildError(f"no answer from {url} for {command}: {exc}") from exc
        if not answer.get("succeeded"):
            err = answer.get("error") or {}
            raise TapirError(err.get("code"), err.get("message", "request failed"))
        if command.startswith("API."):
            return answer.get("result") or {}
        result = (answer.get("result") or {}).get("addOnCommandResponse", {})
        if isinstance(result, dict) and set(result) == {"error"}:
            raise TapirError(result["error"].get("code"), result["error"].get("message", ""))
        return result

    return send


def _tail(lines: list[str], items: list[str], title: str, limit: int = 8) -> None:
    if items:
        lines.append(f"{title} ({len(items)}):")
        lines.extend(f"  - {text}" for text in items[:limit])
        if len(items) > limit:
            lines.append(f"  ... {len(items) - limit} more (see --plan-out / --report-out)")


def format_plan_report(plan: dict, model_path: Path, plan_out: Path | None) -> str:
    batches = " | ".join(f"{key} {len(plan[key])}" for key, _ in PLAN_TYPES if plan[key])
    reoriented = sum(1 for w in plan["walls"] if w["reversed"])
    size = len(json.dumps(plan, ensure_ascii=False, default=str))
    d = plan["datum"]
    lines = [f"build_from_model: DRY RUN, nothing sent | {model_path.name} | office catalog: {'yes' if plan['office_catalog'] else 'NO'}",
             f"datum: +-0.00 = {d.get('level_datum')}, raw slab {d.get('slab_story')} the story, sill from {d.get('sill_reference')}",
             f"planned: {batches}",
             f"exterior loops: {len(plan['loops'])} closed, {reoriented} wall segments re-oriented counter-clockwise"]
    for kind, names in plan["favorites"].items():
        lines.append(f"{kind} favorites: " + "; ".join(names))
    lines.append(f"plan: {size / 1000:.1f} kB kept out of the agent context" + (f", written to {plan_out}" if plan_out else ""))
    _tail(lines, plan["errors"], "ERRORS")
    _tail(lines, plan["warnings"], "warnings")
    _tail(lines, [f"{s['kind']} {s['id']}: {s['reason']}" for s in plan["skipped"]], "skipped")
    if plan["notes"]:
        lines.append(f"notes: {len(plan['notes'])} (rule adjustments, see --plan-out)")
    return "\n".join(lines)


def format_run_report(report: dict, port: int, guid_map: Path | None) -> str:
    made = " | ".join(f"{etype} {report['created'].get(etype, 0)}/{report['planned'].get(etype, 0)}"
                      for etype in COUNT_TYPES if report["planned"].get(etype))
    checks = " ".join(f"{rule} {c['passed']}/{c['passed'] + c['failed']}" for rule, c in sorted(report["checks"].items()))
    lines = [f"build_from_model: LIVE | {report.get('project')} | Tapir {report.get('tapir')} | port {port}",
             f"created: {made}", f"rule checks: {checks}"]
    if report["zone_fallbacks"]:
        lines.append(f"zones from room polygon (not associative): {report['zone_fallbacks']}")
    if guid_map:
        lines.append(f"guid map: {guid_map}")
    _tail(lines, report["warnings"], "warnings")
    _tail(lines, report["errors"], "errors", limit=12)
    lines.append("RESULT: OK" if report["ok"] else "RESULT: FAILED (see errors; created elements are in the guid map)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Build an intermediate building model in Archicad via Tapir, under the office rules.")
    parser.add_argument("model", type=Path, nargs="?")
    parser.add_argument("--dry-run", action="store_true", help="plan only, send nothing that changes the project")
    parser.add_argument("--check", type=Path, help="re-check a finished build against every rule, read-only: the --report-out file")
    parser.add_argument("--port", type=int, help="Archicad JSON port (19723-19743); with --dry-run: read the office catalog only")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--confirm", action="store_true", help="required for a live run: creates elements in the open project")
    parser.add_argument("--plan-out", type=Path)
    parser.add_argument("--guid-map", type=Path)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--material-map", type=Path)
    parser.add_argument("--office-profile", type=Path)
    parser.add_argument("--window-favorite")
    parser.add_argument("--door-favorite")
    parser.add_argument("--zones", choices=["auto", "manual"], default="auto")
    parser.add_argument("--allow-manual-zones", action="store_true")
    parser.add_argument("--din277", action="store_true", help="also build the DIN 277 bodies per story (guideline p.32)")
    args = parser.parse_args(argv)
    # utf-8-sig: PowerShell and Notepad put a byte order mark in front of JSON files
    profile = json.loads(args.office_profile.read_text(encoding="utf-8-sig")) if args.office_profile else None
    if args.check:
        if args.port is None:
            parser.error("--check needs --port (it reads the open project)")
        data = json.loads(args.check.read_text(encoding="utf-8-sig"))
        try:
            report = check(data.get("plan", data), readonly(http_sender(args.host, args.port)), profile)
        except BuildError as exc:
            print(f"build_from_model: check stopped: {exc}", file=sys.stderr)
            return 1
        print(format_run_report(report, args.port, None).replace(": LIVE |", ": CHECK (read-only) |", 1))
        return 0 if report["ok"] else 1
    if args.model is None:
        parser.error("the model file is required (except with --check)")
    if not args.dry_run and args.port is None:
        parser.error("either --dry-run or --port is required")
    model = json.loads(args.model.read_text(encoding="utf-8-sig"))
    material_map = json.loads(args.material_map.read_text(encoding="utf-8-sig")) if args.material_map else None
    options = dict(material_map=material_map, window_favorite=args.window_favorite, door_favorite=args.door_favorite,
                   zones=args.zones, allow_manual_zones=args.allow_manual_zones, profile=profile, din277=args.din277)
    if args.dry_run:
        office = None
        if args.port is not None:
            try:
                office = fetch_office(readonly(http_sender(args.host, args.port)), profile)
            except BuildError as exc:
                print(f"build_from_model: office catalog not read: {exc}", file=sys.stderr)
                return 1
        plan = build_plan(model, office, **options)
        if args.plan_out:
            args.plan_out.write_text(json.dumps(plan, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        print(format_plan_report(plan, args.model, args.plan_out))
        return 1 if plan["errors"] else 0
    if not args.confirm:
        print("refused: a live run creates elements in the open Archicad project. Run --dry-run, show the plan "
              "to the user, then repeat with --confirm.", file=sys.stderr)
        return 2
    try:
        report = run(model, http_sender(args.host, args.port), **options)
    except BuildError as exc:
        print(f"build_from_model: stopped: {exc}", file=sys.stderr)
        return 1
    if args.guid_map:
        args.guid_map.write_text(json.dumps({"model": str(args.model), "guids": report["guid_map"]}, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
    if args.report_out:
        args.report_out.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(format_run_report(report, args.port, args.guid_map))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
