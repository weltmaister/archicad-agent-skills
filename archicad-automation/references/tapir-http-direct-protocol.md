# Tapir Archicad Direct HTTP Protocol (v1.5.0+)

## Protocol

Every Tapir command is wrapped in the official `API.ExecuteAddOnCommand` envelope:

```
POST http://localhost:{port}
Content-Type: application/json

{
  "command": "API.ExecuteAddOnCommand",
  "parameters": {
    "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": "{CommandName}"},
    "addOnCommandParameters": { ... }
  }
}
```

The bare form `{"command": "TapirCommand.{CommandName}", "parameters": {...}}` is rejected by the native Archicad JSON server. Response envelope: `{"succeeded": true, "result": {"addOnCommandResponse": {...}}}`.

**Port discovery:** Scan 19723-19743. The first responding port is the active Archicad instance.

**Important:** There is no detour through an MCP server. This direct HTTP call goes straight to the Tapir Add-On running inside the Archicad process.

## Notation

- `?field` = optional
- `field[]` = array
- `→` = response field
- `"A"|"B"` = enum values

## Shared Types

- **Coordinate2D**: `{x: number, y: number}`
- **Coordinate3D**: `{x: number, y: number, z: number}`
- **ElementId**: `{guid: Guid}`
- **AttributeId**: `{guid: Guid}`
- **NavigatorItemId**: `{guid: Guid}`

## Most important commands for Scan-to-BIM

### Project
| Command | Purpose |
|--------|-------|
| `TapirCommand.GetProjectInfo` | project metadata |
| `TapirCommand.GetStories` | story structure |
| `TapirCommand.SaveProject` | save |

### Read
| Command | Purpose |
|--------|-------|
| `TapirCommand.GetSelectedElements` | current selection |
| `TapirCommand.GetElementsByType` | filter by type |
| `TapirCommand.GetAllElements` | all elements |
| `TapirCommand.GetDetailsOfElements` | read details |
| `TapirCommand.Get3DBoundingBoxes` | 3D bounding box |
| `TapirCommand.GetConnectedElements` | connected elements |
| `TapirCommand.GetCollisions` | collision check |
| `TapirCommand.GetWindowsDetails` | window details |
| `TapirCommand.GetDoorsDetails` | door details |
| `TapirCommand.GetDimensionData` | dimension data |

### Create
| Command | Purpose |
|--------|-------|
| `TapirCommand.CreateWalls` | walls |
| `TapirCommand.CreateSlabs` | slabs/floor plates |
| `TapirCommand.CreateColumns` | columns |
| `TapirCommand.CreateBeams` | beams |
| `TapirCommand.CreateDoors` | doors |
| `TapirCommand.CreateWindows` | windows |
| `TapirCommand.CreateOpenings` | openings (cuts) |
| `TapirCommand.CreateZones` | **zones/rooms** |
| `TapirCommand.CreateObjects` | objects (with `libraryPartName`) |
| `TapirCommand.CreateMorphs` | morph boxes |
| `TapirCommand.CreateRoofs` | roofs |
| `TapirCommand.CreateMeshes` | terrain meshes |
| `TapirCommand.CreatePolylines` | polylines |
| `TapirCommand.CreateLabels` | labels |

### Modify
| Command | Purpose |
|--------|-------|
| `TapirCommand.ModifyWalls` | modify walls |
| `TapirCommand.ModifySlabs` | modify slabs |
| `TapirCommand.ModifyColumns` | modify columns |
| `TapirCommand.ModifyBeams` | modify beams |
| `TapirCommand.ModifyDoors` | modify doors |
| `TapirCommand.ModifyWindows` | modify windows |
| `TapirCommand.ModifyMorphs` | modify morphs |
| `TapirCommand.ModifyRoofs` | modify roofs |
| `TapirCommand.SetDetailsOfElements` | set details |
| `TapirCommand.MoveElements` | move |
| `TapirCommand.DeleteElements` | **delete** |

### Attributes
| Command | Purpose |
|--------|-------|
| `TapirCommand.GetAttributesByType` | read attributes |
| `TapirCommand.CreateLayers` | create layers |
| `TapirCommand.CreateBuildingMaterials` | create building materials |
| `TapirCommand.CreateComposites` | create composites |
| `TapirCommand.CreateSurfaces` | create surfaces |

### Documentation
| Command | Purpose |
|--------|-------|
| `TapirCommand.CreateAssociativeDimensions` | dimensions |
| `TapirCommand.CreateWallThicknessDimensions` | wall thickness dimensions |
| `TapirCommand.CreateLayouts` | layouts |
| `TapirCommand.CreateSubsets` | subsets |
| `TapirCommand.CreateDrawings` | drawings |
| `TapirCommand.PublishPublisherSet` | **publish** |
| `TapirCommand.SetViewSettings` | view settings |

### Properties & classification
| Command | Purpose |
|--------|-------|
| `TapirCommand.GetAllProperties` | all properties |
| `TapirCommand.GetPropertyValuesOfElements` | read property values |
| `TapirCommand.SetPropertyValuesOfElements` | set property values |
| `TapirCommand.GetClassificationsOfElements` | read classifications |
| `TapirCommand.SetClassificationsOfElements` | set classifications |

### Library
| Command | Purpose |
|--------|-------|
| `TapirCommand.GetLibraries` | loaded libraries |
| `TapirCommand.GetAvailableLibraryParts` | **available library parts** (filterable by type) |

## Example call (Python)

```python
import urllib.request, json

url = "http://127.0.0.1:19723"  # replace port with the first responding port in 19723-19743

payload = {
    "command": "API.ExecuteAddOnCommand",
    "parameters": {
        "addOnCommandId": {
            "commandNamespace": "TapirCommand",
            "commandName": "CreateWalls"
        },
        "addOnCommandParameters": {
            "wallsData": [{
                "begCoordinate": {"x": 0, "y": 0},
                "endCoordinate": {"x": 5, "y": 0},
                "zCoordinate": 0,
                "height": 3.0,
                "thickness": 0.31,
                "referenceLineLocation": "Outside"
            }]
        }
    }
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
resp = urllib.request.urlopen(req, timeout=10)
result = json.loads(resp.read().decode())
```

## Critical Pitfall: ElementId format

All APIs that expect element IDs (e.g. `ownerWallId` in `CreateDoors`, `elementId` in `ModifyWalls`) require a **nested object**:

```json
{"guid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

A bare GUID string **fails** with a validation error.

## Critical Pitfall: port distinction

- **Ports 19723-19743**: the Tapir Add-On directly inside the Archicad process. This is where the actual work happens.
- Any other port (e.g. an MCP server's HTTP endpoint) is a separate wrapper process, not the Archicad JSON server.

For direct Tapir commands, **always** use the 19723-19743 range.

## Critical Pitfall: localhost-only listener

The Archicad JSON server listens on localhost only; remote agents need a host-side proxy or must run calls host-side.

Operational rule: if a TCP connect to the port succeeds but HTTP requests to the same port immediately fail with a closed connection (e.g. `RemoteDisconnected: Remote end closed connection without response`), the listener is very likely localhost-only. Do not keep debugging the payload — run the calls on the Archicad host or through a host-side proxy instead.

## Reference files

- **Full command catalog**: `tapir-full-command-catalog.md` (same directory)
- **Verified command schemas**: `tapir-verified-command-schemas.md` (same directory)
