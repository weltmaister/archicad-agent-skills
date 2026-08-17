"""Derive candidate 2D dimension witness points for doors/windows from Tapir opening
detail reads (`GetDoorsDetails` / `GetWindowsDetails`) plus the owner wall geometry.

See references/opening-witness-point-derivation.md for the derivation rules and caveats.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any


@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def scale(self, factor: float) -> "Vec2":
        return Vec2(self.x * factor, self.y * factor)

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    def as_dict(self) -> dict[str, float]:
        return {"x": round(self.x, 6), "y": round(self.y, 6)}


def normalize(v: Vec2) -> Vec2:
    n = sqrt(v.x * v.x + v.y * v.y)
    if n == 0:
        raise ValueError("zero-length vector")
    return Vec2(v.x / n, v.y / n)


def wall_basis(beg: dict[str, float], end: dict[str, float]) -> tuple[Vec2, Vec2, Vec2]:
    beg_v = Vec2(beg["x"], beg["y"])
    end_v = Vec2(end["x"], end["y"])
    wall_dir = normalize(end_v - beg_v)
    wall_normal = Vec2(-wall_dir.y, wall_dir.x)
    return beg_v, wall_dir, wall_normal


def opening_edges(anchor_point: dict[str, float], width: float, fix_point: str, wall_dir: Vec2) -> tuple[Vec2, Vec2]:
    sp = Vec2(anchor_point["x"], anchor_point["y"])
    if fix_point == "BegFix":
        return sp, sp + wall_dir.scale(width)
    if fix_point == "Center":
        half = wall_dir.scale(width / 2.0)
        return sp - half, sp + half
    if fix_point == "EndFix":
        return sp - wall_dir.scale(width), sp
    raise ValueError(f"unsupported fixPoint: {fix_point}")


def anchor_from_center_offset(wall_beg: Vec2, wall_dir: Vec2, center_offset: float) -> dict[str, float]:
    pt = wall_beg + wall_dir.scale(center_offset)
    return {"x": pt.x, "y": pt.y}


def wall_faces(o_side: bool, offset: float, thickness: float, wall_normal: Vec2) -> tuple[Vec2, Vec2]:
    if not o_side:
        outside = wall_normal.scale(offset)
        inside = wall_normal.scale(offset - thickness)
    else:
        outside = wall_normal.scale(-(thickness - offset))
        inside = wall_normal.scale(-offset)
    return outside, inside


def derive_opening_witness_points(opening: dict[str, Any], wall: dict[str, Any]) -> dict[str, Any]:
    wall_beg, wall_dir, wall_normal = wall_basis(wall["begCoordinate"], wall["endCoordinate"])

    # Straight-wall default: use centerOffset to reconstruct a global anchor on the wall reference line.
    # `startPoint` from Tapir is wall-local by API contract and should not be treated as global unless
    # the caller explicitly provides a trusted globalized anchor.
    if opening.get("anchorPoint") is not None:
        anchor = opening["anchorPoint"]
    elif opening.get("centerOffset") is not None:
        anchor = anchor_from_center_offset(wall_beg, wall_dir, opening["centerOffset"])
    else:
        anchor = opening["startPoint"]

    beg_edge, end_edge = opening_edges(anchor, opening["width"], opening["fixPoint"], wall_dir)
    outside_face, inside_face = wall_faces(opening["oSide"], wall.get("offset", 0.0), wall["thickness"], wall_normal)

    beg_outside = beg_edge + outside_face
    end_outside = end_edge + outside_face
    beg_inside = beg_edge + inside_face
    end_inside = end_edge + inside_face

    jamb1 = opening.get("jambDepth", 0.0) or 0.0
    jamb2 = opening.get("jambDepth2", 0.0) or 0.0

    projected_pos = (Vec2(opening["startPoint"]["x"], opening["startPoint"]["y"]) - wall_beg).dot(wall_dir)

    return {
        "ownerId": opening["ownerId"],
        "projectedPos": round(projected_pos, 6),
        "wallDir": wall_dir.as_dict(),
        "wallNormal": wall_normal.as_dict(),
        "opening_beg_ref": beg_edge.as_dict(),
        "opening_end_ref": end_edge.as_dict(),
        "opening_center_ref": Vec2((beg_edge.x + end_edge.x) / 2.0, (beg_edge.y + end_edge.y) / 2.0).as_dict(),
        "opening_beg_outside": beg_outside.as_dict(),
        "opening_end_outside": end_outside.as_dict(),
        "opening_beg_inside": beg_inside.as_dict(),
        "opening_end_inside": end_inside.as_dict(),
        "opening_beg_outside_corrected": (beg_edge + outside_face + wall_dir.scale(jamb1)).as_dict(),
        "opening_end_outside_corrected": (end_edge + outside_face - wall_dir.scale(jamb2)).as_dict(),
        "sill_height": opening.get("sillHeight", 0.0),
        "header_height": (opening.get("sillHeight", 0.0) or 0.0) + (opening.get("height", 0.0) or 0.0),
        "revealDepthFromSide": opening.get("revealDepthFromSide"),
    }


__all__ = ["derive_opening_witness_points"]
