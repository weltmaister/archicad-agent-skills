"""A small in-memory Archicad + Tapir for the executor tests.

It reproduces the behaviour measured live on 29.09.2026 (AC28, Tapir 1.5.9), not an idealised API:
- walls created with an office favorite are not flipped, walls from the tool default are; the exterior face is
  LEFT of the drawing direction when not flipped and RIGHT when flipped; CoreOutside puts the skins in front of the
  core on the exterior side;
- oSide = true puts a door's swing to the LEFT of the host wall direction;
- ChangeWindow with storyIndex does not change the active story (Tapir <= 1.6.0; story_switch_by_index=True models
  1.7.0+), a navigator StoryItem does (navigator_supported=False models AC25/AC26); automatic zones are only found
  on the active story;
- values can be silently ignored (switches below) so the verification has something to catch.
"""
from __future__ import annotations

import copy
import json
import math

from helpers import OFFICE


def _pt(c):
    return c["x"], c["y"]


class FakeArchicad:
    def __init__(self, office=None, version="1.5.9", window="FloorPlan", switchable=True, spaces=(), hidden_layers=(),
                 fail_zone_ids=(), ignore_classification=False, ignore_position=False, ignore_top_link=False,
                 ignore_windows=False, invert_oside=False, story_switch_by_index=False, navigator_supported=True, zone_base=-0.15,
                 fixed_beam_length=None, opening_sill_shift=0.0, slab_outline_shift=0.0):
        self.office = copy.deepcopy(office or OFFICE)
        self.version, self.window, self.switchable = version, window, switchable
        self.spaces = list(spaces)
        self.hidden_layers = set(hidden_layers)
        self.fail_zone_ids = set(fail_zone_ids)
        self.ignore_classification, self.ignore_position, self.ignore_top_link = ignore_classification, ignore_position, ignore_top_link
        self.ignore_windows, self.invert_oside, self.story_switch_by_index = ignore_windows, invert_oside, story_switch_by_index
        self.navigator_supported = navigator_supported
        self.zone_base = zone_base
        self.fixed_beam_length, self.opening_sill_shift = fixed_beam_length, opening_sill_shift
        self.slab_outline_shift = slab_outline_shift
        self.act_story = self.office["act_story"]
        self.levels = {s["index"]: s["level"] for s in self.office["stories"]}
        self.elements: dict[str, dict] = {}
        self.calls: list[tuple[str, dict]] = []
        self.n = 0

    # -- helpers ------------------------------------------------------------------------
    def _guid(self, prefix):
        self.n += 1
        return f"{prefix}-{self.n:04d}"

    def sent(self, command):
        return [p for c, p in self.calls if c == command]

    def _layer_index(self, name):
        return self.office["layers"][name]["index"]

    def _composite(self, guid):
        return next((c for c in self.office["composites"].values() if c["guid"] == guid), None)

    def _wall_geometry(self, el):
        p = el["payload"]
        (bx, by), (ex, ey) = _pt(p["begCoordinate"]), _pt(p["endCoordinate"])
        length = math.hypot(ex - bx, ey - by)
        ux, uy = (ex - bx) / length, (ey - by) / length
        lx, ly = -uy, ux  # left normal
        comp = self._composite((p.get("compositeId") or {}).get("guid")) if p.get("structureType") == "Composite" else None
        t = sum(s["thickness"] for s in comp["skins"]) if comp else p["thickness"]
        front = 0.0
        if comp:
            for s in comp["skins"]:
                if s["type"] == "Core":
                    break
                front += s["thickness"]
        ext_sign = 1.0 if not el["flipped"] else -1.0  # exterior side: +left when not flipped
        ref = p.get("referenceLineLocation", "Center")
        ext_part = {"Outside": 0.0, "CoreOutside": front, "Center": t / 2, "Inside": t}.get(ref, t / 2)
        a = ext_sign * ext_part          # exterior extent along the left normal
        b = -ext_sign * (t - ext_part)   # interior extent along the left normal
        pts = [(bx + lx * s, by + ly * s) for s in (a, b)] + [(ex + lx * s, ey + ly * s) for s in (a, b)]
        return pts, t

    def _wall_z(self, el):
        p = el["payload"]
        base = self.levels[el["floor"]] + p.get("zCoordinate", 0.0)
        if el.get("relativeTopStory") and (el["floor"] + el["relativeTopStory"]) in self.levels:
            top = self.levels[el["floor"] + el["relativeTopStory"]] + el.get("topOffset", 0.0)
            return base, top
        return base, base + p["height"]

    def _bbox3(self, el):
        t = el["type"]
        p = el["payload"]
        if t == "Wall":
            pts, _ = self._wall_geometry(el)
            z0, z1 = self._wall_z(el)
        elif t == "Slab":
            pts = [_pt(c) for c in p["polygonCoordinates"]]
            z0, z1 = p["level"] - el["thickness"], p["level"]
        elif t == "Zone":
            pts = el["polygon"]
            base = self.levels[el["floor"]] + self.zone_base
            z0 = base + el["props"].get("P-FB", 0.15)
            if el["props"].get("P-LICHT") is not None:
                z1 = z0 + el["props"]["P-LICHT"]
            elif (el["floor"] + 1) in self.levels:
                z1 = self.levels[el["floor"] + 1] + el["props"].get("P-ABST", -0.35)
            else:
                z1 = z0 + 2.65
        elif t in ("Window", "Door"):
            host = self.elements[p["ownerWallId"]["guid"]]
            (bx, by), (ex, ey) = _pt(host["payload"]["begCoordinate"]), _pt(host["payload"]["endCoordinate"])
            length = math.hypot(ex - bx, ey - by)
            ux, uy = (ex - bx) / length, (ey - by) / length
            cx, cy = bx + ux * p["centerOffset"], by + uy * p["centerOffset"]
            w = p.get("width", 1.0)
            pts = [(cx - ux * w / 2, cy - uy * w / 2), (cx + ux * w / 2, cy + uy * w / 2)]
            z0 = self._wall_z(host)[0] + p.get("sillHeight", 0.0)
            z1 = z0 + p.get("height", 1.0)
        elif t == "Column":
            c = p["coordinates"]
            w, d = p.get("width", 0.3), p.get("depth", 0.3)
            pts = [(c["x"] - w / 2, c["y"] - d / 2), (c["x"] + w / 2, c["y"] + d / 2)]
            z0, z1 = c["z"], c["z"] + p.get("height", 2.5)
        elif t == "Beam":
            pts = [_pt(p["begCoordinate"]), _pt(p["endCoordinate"])]
            z1 = p["zCoordinate"]
            z0 = z1 - p.get("height", 0.2)
        elif t == "Opening":
            box = self._bbox2(el)
            level = self.levels[el["floor"]]
            return dict(box, zMin=level, zMax=level)  # openings report a degenerate z (VS:119)
        elif t == "Roof":
            over = p.get("eavesOverhang", 0.0)
            xs0, ys0 = [c["x"] for c in p["polygonCoordinates"]], [c["y"] for c in p["polygonCoordinates"]]
            pts = [(min(xs0) - over, min(ys0) - over), (max(xs0) + over, max(ys0) + over)]
            angle = (p.get("levels") or [{"levelAngle": math.radians(45)}])[0]["levelAngle"]
            z0 = p["level"] - over * math.tan(angle)
            z1 = z0 + 3.0
        elif t == "Morph":
            vs = p["body"]["vertices"]
            pts = [(v["x"], v["y"]) for v in vs]
            z0, z1 = min(v["z"] for v in vs), max(v["z"] for v in vs)
        else:
            pts, z0, z1 = [(0, 0)], 0.0, 0.0
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        return {"xMin": min(xs), "yMin": min(ys), "zMin": z0, "xMax": max(xs), "yMax": max(ys), "zMax": z1}

    def _bbox2(self, el):
        if el["type"] == "Opening":
            p = el["payload"]
            host = self.elements[p["ownerElementId"]["guid"]]
            bp, w, h = p["basePoint"], p.get("width", 0.5), p.get("height", 0.5)
            if host["type"] == "Slab":  # x = centre, y = upper edge, height runs in -y (VS:118)
                return {"xMin": bp["x"] - w / 2, "yMin": bp["y"] - h, "xMax": bp["x"] + w / 2, "yMax": bp["y"]}
            (bx, by), (ex, ey) = _pt(host["payload"]["begCoordinate"]), _pt(host["payload"]["endCoordinate"])
            length = math.hypot(ex - bx, ey - by)
            ux, uy = (ex - bx) / length, (ey - by) / length
            t = host["payload"]["thickness"] / 2
            pts = [(bp["x"] + ux * s * w / 2 - uy * q * t, bp["y"] + uy * s * w / 2 + ux * q * t) for s in (-1, 1) for q in (-1, 1)]
            return {"xMin": min(x for x, _ in pts), "yMin": min(y for _, y in pts), "xMax": max(x for x, _ in pts), "yMax": max(y for _, y in pts)}
        box = self._bbox3(el)
        if el["type"] != "Door":
            return box
        host = self.elements[el["payload"]["ownerWallId"]["guid"]]
        (bx, by), (ex, ey) = _pt(host["payload"]["begCoordinate"]), _pt(host["payload"]["endCoordinate"])
        length = math.hypot(ex - bx, ey - by)
        lx, ly = -(ey - by) / length, (ex - bx) / length
        left = bool(el["payload"].get("oSide")) != self.invert_oside
        sign = 1.0 if left else -1.0
        w = el["payload"].get("width", 1.0)
        cx, cy = (box["xMin"] + box["xMax"]) / 2, (box["yMin"] + box["yMax"]) / 2
        arc = (cx + lx * sign * w, cy + ly * sign * w)
        return {"xMin": min(box["xMin"], arc[0]), "yMin": min(box["yMin"], arc[1]), "xMax": max(box["xMax"], arc[0]),
                "yMax": max(box["yMax"], arc[1])}

    def _details(self, el):
        t, p = el["type"], el["payload"]
        if t == "Wall":
            d = {"begCoordinate": p["begCoordinate"], "endCoordinate": p["endCoordinate"], "flipped": el["flipped"],
                 "referenceLineLocation": p.get("referenceLineLocation", "Center"), "structureType": p.get("structureType", "Basic"),
                 "height": self._wall_z(el)[1] - self._wall_z(el)[0], "bottomOffset": p.get("zCoordinate", 0.0),
                 "relativeTopStory": el.get("relativeTopStory", 0), "topOffset": el.get("topOffset", 0.0),
                 "zoneRel": el.get("zoneRel", "Boundary")}
            if p.get("compositeId"):
                d["compositeId"] = p["compositeId"]
            return d
        if t == "Slab":
            outline = [{"x": c["x"] + self.slab_outline_shift, "y": c["y"]} for c in p["polygonCoordinates"]]
            return {"level": p["level"] - self.levels[el["floor"]], "thickness": el["thickness"],
                    "polygonOutline": outline, "holes": p.get("holes", []), "structureType": el.get("structureType", "Basic")}
        if t == "Zone":
            poly = [{"x": x, "y": y} for x, y in el["polygon"]]
            return {"name": p["name"], "numberStr": p["numberStr"], "isManual": el["manual"], "polygonOutline": poly + [poly[0]],
                    "zCoordinate": self.zone_base}
        if t in ("Window", "Door"):
            return {k: p.get(k) for k in ("width", "height", "sillHeight", "centerOffset", "oSide", "reflected", "refSide")}
        if t == "Beam":
            return {"begCoordinate": p["begCoordinate"], "endCoordinate": p["endCoordinate"], "zCoordinate": p["zCoordinate"],
                    "width": p.get("width"), "height": p.get("height")}
        if t == "Opening":
            return {"error": "Not yet supported element type"}
        return {}

    # -- dispatcher -----------------------------------------------------------------------
    def __call__(self, command, params):
        self.calls.append((command, json.loads(json.dumps(params))))
        o = self.office
        if command == "GetAddOnVersion":
            return {"version": self.version}
        if command == "GetProjectInfo":
            return {"projectName": "Test.pln", "isUntitled": False}
        if command == "GetCurrentWindowType":
            return {"currentWindowType": self.window}
        if command == "ChangeWindow":
            if "navigatorItemId" in params:
                if not self.navigator_supported:  # AC25/AC26
                    return {"success": False, "error": {"code": -2130312313,
                            "message": "navigatorItemId requires Archicad 27 or later; use databaseId instead."}}
                nav = params["navigatorItemId"]["guid"]
                self.act_story = next(int(k) for k, v in o["story_items"].items() if v == nav)
                self.window = "FloorPlan"
            elif self.switchable:
                self.window = params["windowType"]
                if self.story_switch_by_index and "storyIndex" in params:
                    self.act_story = params["storyIndex"]
            return {"success": True}
        if command == "GetStories":
            return {"firstStory": -1, "lastStory": 1, "actStory": self.act_story, "skipNullFloor": False,
                    "stories": [dict(s, floorId=s["index"] + 10, dispOnSections=True) for s in o["stories"]]}
        if command == "GetNavigatorItemTree":
            children = [{"navigatorItem": {"type": "StoryItem", "name": s["name"], "prefix": str(s["index"]),
                                           "navigatorItemId": {"guid": o["story_items"][str(s["index"])]}, "children": []}}
                        for s in reversed(o["stories"])]
            return {"navigatorItemTree": {"navigatorItem": {"type": "ProjectMapRootItem", "name": "Projekt", "children": children}}}
        if command == "GetAttributesByType":
            kind = params["attributeType"]
            source = {"Layer": o["layers"], "Composite": o["composites"], "BuildingMaterial": o["materials"],
                      "ZoneCategory": {k: {"guid": v} for k, v in o["zone_categories"].items()}}[kind]
            out = []
            for i, (name, v) in enumerate(source.items()):
                guid = v.get("guid") or f"L-{name}"
                out.append({"attributeId": {"guid": guid}, "index": v.get("index", i + 1), "name": name})
            return {"attributes": out}
        if command == "GetLayers":
            by_guid = {f"L-{name}": (name, v) for name, v in o["layers"].items()}
            return {"layers": [{"attributeId": a["attributeId"], "index": by_guid[a["attributeId"]["guid"]][1]["index"],
                                "name": by_guid[a["attributeId"]["guid"]][0],
                                "isHidden": by_guid[a["attributeId"]["guid"]][0] in self.hidden_layers}
                               for a in params["attributeIds"]]}
        if command == "GetComposites":
            by_guid = {v["guid"]: (name, v) for name, v in o["composites"].items()}
            mats = {name: v["guid"] for name, v in o["materials"].items()}
            out = []
            for a in params["attributeIds"]:
                name, v = by_guid[a["attributeId"]["guid"]]
                out.append({"attributeId": a["attributeId"], "name": name, "skins": [
                    {"type": s["type"], "thickness": s["thickness"],
                     "buildingMaterialId": {"attributeId": {"guid": mats.get(s["material"], "M-?")}}} for s in v["skins"]]})
            return {"composites": out}
        if command == "GetBuildingMaterials":
            by_guid = {v["guid"]: (name, v) for name, v in o["materials"].items()}
            return {"buildingMaterials": [{"attributeId": a["attributeId"], "name": by_guid[a["attributeId"]["guid"]][0],
                                           "connPriority": by_guid[a["attributeId"]["guid"]][1]["priority"]} for a in params["attributeIds"]]}
        if command == "GetFavoritesByType":
            return {"favorites": o["favorites"].get(params["elementType"], [])}
        if command == "API.GetAllClassificationSystems":
            s = o["classification"]["system"]
            return {"classificationSystems": [{"classificationSystemId": {"guid": s["guid"]}, "name": s["name"], "version": "28"}]}
        if command == "API.GetAllClassificationsInSystem":
            tree: dict = {}
            for path, guid in o["classification"]["items"].items():
                parts = path.split(" > ")
                node = tree
                for depth, part in enumerate(parts):
                    node = node.setdefault(part, {"_guid": None, "_children": {}})
                    if depth == len(parts) - 1:
                        node["_guid"] = guid
                    node = node["_children"]

            def build(level, prefix):
                items = []
                for name, node in level.items():
                    guid = node["_guid"] or f"CL-{prefix}{name}"
                    items.append({"classificationItem": {"classificationItemId": {"guid": guid}, "id": name, "name": "",
                                                         "children": build(node["_children"], prefix + name + "/")}})
                return items
            return {"classificationItems": build(tree, "")}
        if command == "GetAllProperties":
            p = o["properties"]
            enum = lambda values: [{"enumValue": {"displayValue": d, "nonLocalizedValue": n}} for d, n in values]  # noqa: E731
            return {"properties": [
                {"propertyId": {"guid": p["load_bearing"]}, "propertyType": "DynamicBuiltIn", "propertyGroupName": "CategoryPropertyDefinitionGroup",
                 "propertyName": "Tragende Funktion", "propertyCollectionType": "SingleChoiceEnumeration", "propertyValueType": "Guid",
                 "propertyMeasureType": "Undefined", "propertyIsEditable": True, "isExpressionBased": False,
                 "possibleEnumValues": enum([("Nicht definiert", "Undefined"), ("Nicht tragende Elemente", "NonLoadBearingElement"),
                                             ("Tragende Elemente", "LoadBearingElement")])},
                {"propertyId": {"guid": p["position"]}, "propertyType": "DynamicBuiltIn", "propertyGroupName": "CategoryPropertyDefinitionGroup",
                 "propertyName": "Lage", "propertyCollectionType": "SingleChoiceEnumeration", "propertyValueType": "Guid",
                 "propertyMeasureType": "Undefined", "propertyIsEditable": True, "isExpressionBased": False,
                 "possibleEnumValues": enum([("Außen", "Exterior"), ("Innen", "Interior"), ("Nicht definiert", "Undefined")])},
                {"propertyId": {"guid": p["floor_thickness"]}, "propertyType": "StaticBuiltIn", "propertyGroupName": "Raum",
                 "propertyName": "Fußbodendicke", "propertyCollectionType": "Single", "propertyValueType": "Real", "propertyMeasureType": "Length",
                 "propertyIsEditable": True, "isExpressionBased": False},
                {"propertyId": {"guid": p["clear_height"]}, "propertyType": "StaticBuiltIn", "propertyGroupName": "Raum",
                 "propertyName": "Lichte Raumhöhe (Archicad 20)", "propertyCollectionType": "Single", "propertyValueType": "Real",
                 "propertyMeasureType": "Length", "propertyIsEditable": True, "isExpressionBased": False},
                {"propertyId": {"guid": p["top_offset"]}, "propertyType": "StaticBuiltIn", "propertyGroupName": "Allgemeine Parameter",
                 "propertyName": "Abstand Oberkante", "propertyCollectionType": "Single", "propertyValueType": "Real",
                 "propertyMeasureType": "Length", "propertyIsEditable": True, "isExpressionBased": False},
                {"propertyId": {"guid": p["top_story"]}, "propertyType": "StaticBuiltIn", "propertyGroupName": "Allgemeine Parameter",
                 "propertyName": "Relatives Geschoss für Oberkantenverknüpfung", "propertyCollectionType": "Single",
                 "propertyValueType": "Integer", "propertyMeasureType": "Default", "propertyIsEditable": True, "isExpressionBased": False},
                {"propertyId": {"guid": p["opening_sill"]}, "propertyType": "StaticBuiltIn", "propertyGroupName": "Positionierung",
                 "propertyName": "Öffnung Brüstungshöhe zu Projektursprung", "propertyCollectionType": "Single", "propertyValueType": "Real",
                 "propertyMeasureType": "Length", "propertyIsEditable": False, "isExpressionBased": False},
                {"propertyId": {"guid": p["din277_area"]}, "propertyType": "Custom", "propertyGroupName": "Allgemeine Werte",
                 "propertyName": "Flächenart nach DIN 277", "propertyCollectionType": "SingleChoiceEnumeration",
                 "propertyValueType": "String", "propertyMeasureType": "Default", "propertyIsEditable": True, "isExpressionBased": False,
                 "possibleEnumValues": [{"enumValue": {"displayValue": v}} for v in ("AF", "BF", "GF", "UF")]},
                {"propertyId": {"guid": p["din277"]}, "propertyType": "DynamicBuiltIn", "propertyGroupName": "CategoryPropertyDefinitionGroup",
                 "propertyName": "Klassifizierung nach DIN 277", "propertyCollectionType": "SingleChoiceEnumeration",
                 "propertyValueType": "Guid", "propertyMeasureType": "Undefined", "propertyIsEditable": True, "isExpressionBased": False,
                 "possibleEnumValues": enum([("Regelfall", "Regular"), ("Sonderfall", "Special")])},
            ]}
        if command == "GetGeoLocation":
            return {"projectLocation": {"longitude": 13.4, "latitude": 52.5, "altitude": 0, "north": o["north"]}}
        if command == "GetElementsByType":
            return {"elements": [{"elementId": {"guid": g}} for g, e in self.elements.items() if e["type"] == params["elementType"]
                                 and not (e["type"] == "Window" and self.ignore_windows)]}
        if command.startswith("Create"):
            return self._create(command, params)
        if command == "ModifyWalls":
            out = []
            for item in params["wallsWithDetails"]:
                el = self.elements[item["elementId"]["guid"]]
                for key in ("begCoordinate", "endCoordinate", "referenceLineLocation"):
                    if key in item:
                        el["payload"][key] = item[key]
                if "bottomOffset" in item:
                    el["payload"]["zCoordinate"] = item["bottomOffset"]
                if "height" in item:
                    el["payload"]["height"] = item["height"]
                if "relativeTopStory" in item and not self.ignore_top_link:
                    el["relativeTopStory"] = item["relativeTopStory"]
                    el["topOffset"] = item.get("topOffset", 0.0)
                if "zoneRel" in item:
                    el["zoneRel"] = item["zoneRel"]
                out.append({"success": True})
            return {"executionResults": out}
        if command == "ApplyFavoritesToElements":
            for item in params["favoritesToApply"]:
                el = self.elements[item["elementId"]["guid"]]
                el["favorite"] = item["favorite"]
                if item["favorite"] == "BRI R":
                    el["layer"] = self._layer_index("80 BGF BRI")
                    el["props"][o["properties"]["din277"]] = "Regelfall"
                if el["type"] == "Morph" and self.levels[el["floor"]]:
                    # live 29.09.2026: applying a morph favorite moved an upper-story body down by its story level
                    for v in el["payload"]["body"]["vertices"]:
                        v["z"] -= self.levels[el["floor"]]
            return {"executionResults": [{"success": True} for _ in params["favoritesToApply"]]}
        if command == "ModifySlabs":
            for item in params["slabsWithDetails"]:
                el = self.elements[item["elementId"]["guid"]]
                if "structureType" in item:
                    el["structureType"] = item["structureType"]
            return {"executionResults": [{"success": True} for _ in params["slabsWithDetails"]]}
        if command == "GetDetailsOfElements":
            out = []
            for item in params["elements"]:
                el = self.elements[item["elementId"]["guid"]]
                out.append({"type": el["type"], "id": item["elementId"]["guid"], "floorIndex": el["floor"], "layerIndex": el["layer"],
                            "drawIndex": 1, "details": self._details(el)})
            return {"detailsOfElements": out}
        if command == "SetDetailsOfElements":
            out = []
            for item in params["elementsWithDetails"]:
                el = self.elements[item["elementId"]["guid"]]
                if "layerIndex" in item["details"]:
                    el["layer"] = item["details"]["layerIndex"]
                out.append({"success": True})
            return {"executionResults": out}
        if command == "SetClassificationsOfElements":
            for item in params["elementClassifications"]:
                if not self.ignore_classification:
                    self.elements[item["elementId"]["guid"]]["classification"] = item["classificationId"]["classificationItemId"]["guid"]
            return {"executionResults": [{"success": True} for _ in params["elementClassifications"]]}
        if command == "GetClassificationsOfElements":
            out = []
            for item in params["elements"]:
                el = self.elements[item["elementId"]["guid"]]
                cid = {"classificationSystemId": {"guid": o["classification"]["system"]["guid"]}}
                if el.get("classification"):
                    cid["classificationItemId"] = {"guid": el["classification"]}
                out.append({"classificationIds": [cid]})
            return {"elementClassifications": out}
        if command == "API.SetPropertyValuesOfElements":
            out = []
            for item in params["elementPropertyValues"]:
                el = self.elements[item["elementId"]["guid"]]
                pid, value = item["propertyId"]["guid"], item["propertyValue"]
                if pid == o["properties"]["din277"]:  # live: the official API does not support this property (6702)
                    out.append({"success": False, "error": {"code": 6702, "message": "Property definition not supported"}})
                    continue
                if pid == o["properties"]["load_bearing"] and el["type"] == "Opening":  # live: read-only on openings (6800)
                    out.append({"success": False, "error": {"code": 6800, "message": "Value of property definition is read-only"}})
                    continue
                if pid == o["properties"]["position"] and self.ignore_position:
                    out.append({"success": True})
                    continue
                if value["type"] == "singleEnum":
                    el["props"][pid] = value["value"].get("nonLocalizedValue") or value["value"].get("displayValue")
                else:
                    el["props"][pid] = value["value"]
                out.append({"success": True})
            return {"executionResults": out}
        if command == "API.GetPropertyValuesOfElements":
            out = []
            for item in params["elements"]:
                el = self.elements[item["elementId"]["guid"]]
                vals = []
                # exact live shape (29.09.2026): enum values are nested one level deeper than lengths
                for prop in params["properties"]:
                    v = el["props"].get(prop["propertyId"]["guid"])
                    if v is None:
                        vals.append({"propertyValue": {"type": "singleEnum", "status": "notEvaluated"}})
                    elif isinstance(v, str):
                        vals.append({"propertyValue": {"type": "singleEnum", "status": "normal",
                                                       "value": {"type": "nonLocalizedValue", "nonLocalizedValue": v}}})
                    else:
                        vals.append({"propertyValue": {"type": "length", "status": "normal", "value": v}})
                out.append({"propertyValues": vals})
            return {"propertyValuesForElements": out}
        if command == "SetPropertyValuesOfElements":  # Tapir: display value as string
            for item in params["elementPropertyValues"]:
                self.elements[item["elementId"]["guid"]]["props"][item["propertyId"]["guid"]] = item["propertyValue"]["value"]
            return {"executionResults": [{"success": True} for _ in params["elementPropertyValues"]]}
        if command == "GetPropertyValuesOfElements":  # Tapir: display value as string
            out = []
            for item in params["elements"]:
                el = self.elements[item["elementId"]["guid"]]
                out.append({"propertyValues": [{"propertyValue": {"value": el["props"].get(p["propertyId"]["guid"], "Nicht definiert")}}
                                               for p in params["properties"]]})
            return {"propertyValuesForElements": out}
        if command == "Get3DBoundingBoxes":
            return {"boundingBoxes3D": [{"boundingBox3D": self._bbox3(self.elements[i["elementId"]["guid"]])} for i in params["elements"]]}
        if command == "API.Get2DBoundingBoxes":
            return {"boundingBoxes2D": [{"boundingBox2D": self._bbox2(self.elements[i["elementId"]["guid"]])} for i in params["elements"]]}
        raise AssertionError(f"unexpected command {command}")

    def _create(self, command, params):
        key = {"CreateWalls": "wallsData", "CreateSlabs": "slabsData", "CreateWindows": "windowsData", "CreateDoors": "doorsData",
               "CreateZones": "zonesData", "CreateOpenings": "openingsData", "CreateColumns": "columnsData", "CreateBeams": "beamsData",
               "CreateRoofs": "roofsData", "CreateMorphs": "morphsData"}[command]
        etype = {"CreateWalls": "Wall", "CreateSlabs": "Slab", "CreateWindows": "Window", "CreateDoors": "Door", "CreateZones": "Zone",
                 "CreateOpenings": "Opening", "CreateColumns": "Column", "CreateBeams": "Beam", "CreateRoofs": "Roof",
                 "CreateMorphs": "Morph"}[command]
        out = []
        for item in params[key]:
            floor = item.get("floorIndex", self.act_story)
            el = {"type": etype, "payload": copy.deepcopy(item), "floor": floor, "layer": 2, "props": {}, "classification": None}
            if etype == "Wall":
                el["flipped"] = not bool(item.get("favoriteName"))
                if item.get("favoriteName") == "GK Installationswand":  # a profile wall: the profile fixes the reference line (live)
                    el["payload"]["structureType"], el["payload"]["referenceLineLocation"] = "Profile", "Outside"
            if etype == "Slab":
                el["thickness"] = item.get("thickness", 0.2)
                el["structureType"] = "Composite" if item.get("favoriteName", "").startswith("Boden") else "Basic"
            if etype in ("Window", "Door"):
                host = self.elements[item["ownerWallId"]["guid"]]
                el["floor"] = host["floor"]
            if etype == "Opening":
                host = self.elements[item["ownerElementId"]["guid"]]
                el["floor"] = host["floor"]
                if host["type"] == "Wall":
                    el["props"][self.office["properties"]["opening_sill"]] = item["basePoint"]["z"] + self.opening_sill_shift
            if etype == "Beam" and self.fixed_beam_length:
                (bx, by), (ex, ey) = _pt(item["begCoordinate"]), _pt(item["endCoordinate"])
                length = math.hypot(ex - bx, ey - by)
                el["payload"]["endCoordinate"] = {"x": bx + (ex - bx) / length * self.fixed_beam_length,
                                                  "y": by + (ey - by) / length * self.fixed_beam_length}
            if etype == "Zone":
                if "referencePosition" in item["geometry"]:
                    seed = _pt(item["geometry"]["referencePosition"])
                    space = next((s for s in self.spaces if _inside(seed, s["boundary"])), None)
                    if space is None or floor != self.act_story or space["id"] in self.fail_zone_ids:
                        out.append({"error": {"code": -2130313215, "message": "Failed to create new Zone"}})
                        continue
                    el["polygon"] = [tuple(p) for p in space["boundary"]]
                    el["manual"] = False
                else:
                    el["polygon"] = [_pt(c) for c in item["geometry"]["polygonCoordinates"]]
                    el["manual"] = True
                el["props"] = {"P-FB": 0.15, "P-ABST": -0.35}
            guid = self._guid(etype)
            self.elements[guid] = el
            out.append({"elementId": {"guid": guid}})
        return {"elements": out}


def _inside(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        (x1, y1), (x2, y2) = polygon[i], polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside
