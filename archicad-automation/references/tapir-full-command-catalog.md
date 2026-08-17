# Tapir Archicad Commands v1.5.3

## Protocol
Every command goes through the `API.ExecuteAddOnCommand` wrapper. The bare `{"command": "TapirCommand.X"}` form is rejected by the native Archicad JSON server with error 2002 (verified live).
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
The `{CommandName}` and the field schemas below go into `commandName` / `addOnCommandParameters`. Response: `{"succeeded": true, "result": {"addOnCommandResponse": {...}}}`.

Port discovery: scan 19723-19743, first responding port is the active Archicad instance.

## Notation
- `?field` = optional
- `field[]` = array of items
- `→` = response
- `"A"|"B"` = enum values
- Types: float, int, bool, string

## Shared Types

- **Coordinate2D**: {x: number, y: number}
- **Coordinate3D**: {x: number, y: number, z: number}
- **ElementId**: {guid: Guid}
- **AttributeId**: {guid: Guid}
- **NavigatorItemId**: {guid: Guid}
- **PropertyId**: {guid: Guid}
- **ClassificationItemId**: {guid: Guid}

## Application Commands

### GetAddOnVersion
# Retrieves the version of the Tapir Additional JSON Commands Add-On.
  (no parameters)
  → version: string

### GetArchicadLocation
# Retrieves the location of the currently running Archicad executable.
  (no parameters)
  → archicadLocation: string

### QuitArchicad
# Performs a quit operation on the currently running Archicad instance.
  (no parameters)
  → 

### GetCurrentWindowType
# Returns the type of the current (active) window.
  (no parameters)
  → currentWindowType: WindowType

### ChangeWindow
# Changes the current (active) window to the given window.
# Since main 2026-07-06 (#437): optional storyIndex (switches the active story when windowType is 'FloorPlan').
  → 

## Project Commands

### GetProjectInfo
# Retrieves information about the currently loaded project.
  (no parameters)
  → isUntitled: bool, isTeamwork: bool, projectLocation: string, projectPath: string, projectName: string

### GetProjectInfoFields
# Retrieves the names and values of all project info fields.
  (no parameters)
  → fields: ProjectInfoFields

### SetProjectInfoField
# Sets the value of a project info field.
  projectInfoId: string
  projectInfoValue: string

### CreateProjectInfoFields
# Creates one or more custom project info fields.
  projectInfoFields[]: projectInfoName: string, ?projectInfoValue: string
  → fields: ProjectInfoFields

### GetStories
# Retrieves information about the story sructure of the currently loaded project.
  (no parameters)
  → firstStory: int, lastStory: int, actStory: int, skipNullFloor: bool, stories: StoriesParameters  # each story also returns height (level diff to next story up; topmost has none), since PR #434

### SetStories
# Sets the story sructure of the currently loaded project.
  stories: StoriesSettings
  → 

### GetHotlinks
# Gets the file system locations (path) of the hotlink modules. The hotlinks can have tree hierarchy in the project.
  (no parameters)
  → hotlinks: Hotlinks

### OpenProject
# Opens the given project.
  projectFilePath: string
  → 

### CloseProject
# Closes the currently opened project.
  (no parameters)
  → 

### SaveProject
# Saves the currently opened project.
  (no parameters)
  → 

### GetCalculationUnits
# Gets the project calculation units.
  (no parameters)
  → length: {unit: LengthType, accuracy: AccuracyType, decimals: int, roundInch: int}, area: {unit: AreaType, accuracy: AccuracyType, decimals: int}, volume: {unit: VolumeType, accuracy: AccuracyType, decimals: int}, angle: {unit: AngleType, decimals: int, accuracy: int}

### GetGeoLocation
# Gets the project location details.
  (no parameters)
  → projectLocation: {longitude: float, latitude: float, altitude: float, north: float}, surveyPoint: {position: {eastings: float, northings: float, elevation: float}, geoReferencingParameters: {crsName: string, description: string, geodeticDatum: string, verticalDatum: string, mapProjection: string, ...}}

### SetGeoLocation
# Sets the project location details.
  ?projectLocation: {longitude: float, latitude: float, altitude: float, north: float}
  ?surveyPoint: {position: {eastings: float, northings: float, elevation: float}, geoReferencingParameters: {crsName: string, description: string, geodeticDatum: string, verticalDatum: string, mapProjection: string, ...}}
  → 

### PrintView
# Prints from the current view.
  ?grid: bool
  ?fixText: bool
  ?scale: int
  ?printArea: "currentView"|"entireDrawing"|"marquee"
  → 

### RebuildView
# Rebuilds the current view.
  ?regenerate: bool
  → 

## Element Commands

### GetSelectedElements
# Gets the list of the currently selected elements.
  (no parameters)
  → elements: Elements

### GetElementsByType
# Returns the identifier of every element of the given type on the plan. It works for any type. Use the optional filter parameter for filtering.
  elementType: ElementType
  ?filters[]: ElementFilter
  ?databases: Databases
  → 

### GetAllElements
# Returns the identifier of all elements on the plan. Use the optional filter parameter for filtering.
  ?filters[]: ElementFilter
  ?databases: Databases

### ChangeSelectionOfElements
# Adds/removes a number of elements to/from the current selection.
  ?addElementsToSelection: Elements
  ?removeElementsFromSelection: Elements
  → executionResultsOfAddToSelection: ExecutionResults, executionResultsOfRemoveFromSelection: ExecutionResults

### FilterElements
# Tests an elements by the given criterias.
  elements: Elements
  ?filters[]: ElementFilter
  → elements: Elements

### GetDetailsOfElements
# Gets the details of the given elements (geometry parameters etc).
  elements: Elements
  → detailsOfElements: [{type: ElementType, id: string, floorIndex: float, layerIndex: float, drawIndex: float, ...}]  # since main 2026-07-06 (#437) additionally optional floorPlanPolygons (floor-plan outline polygons, across stories)

### SetDetailsOfElements
# Sets the details of the given elements (floor, layer, order etc).
  elementsWithDetails[]: elementId: ElementId, details: {floorIndex: float, layerIndex: float, drawIndex: float, typeSpecificDetails: TypeSpecificSettings}
  → executionResults: ExecutionResults
  # drawIndex: before main 2026-07-06 (#436) silently ignored (Graphisoft bug); since then functional via Grouping_Tool (limits: door/window/skylight minimum level 7, generic Opening cannot be moved)

### Get3DBoundingBoxes
# Get the 3D bounding box of elements. The bounding box is calculated from the global origin in the 3D view. The output is the array of the bounding boxes respective to the input array of elements.
  elements: Elements
  → boundingBoxes3D: BoundingBoxes3D

### GetSubelementsOfHierarchicalElements
# Gets the subelements of the given hierarchical elements.
  elements: Elements
  → subelements: [{cWallSegments: Elements, cWallFrames: Elements, cWallPanels: Elements, cWallJunctions: Elements, cWallAccessories: Elements, ...}]

### GetConnectedElements
# Gets connected elements of the given elements.
  elements: Elements
  connectedElementType: ElementType
  → 

### GetZoneBoundaries
# Gets the boundaries of the given Zone (connected elements, neighbour zones, etc.).
  zoneElementId: ElementId
  → 

### GetCollisions
# Detect collisions between the given two groups of elements.
  elementsGroup1: Elements
  elementsGroup2: Elements
  ?settings: {volumeTolerance: float, performSurfaceCheck: bool, surfaceTolerance: float}
  → collisions: [{elementId1: ElementId, elementId2: ElementId, hasBodyCollision: bool, hasClearenceCollision: bool}]

### HighlightElements
# Highlights the elements given in the elements array. In case of empty elements array removes all previously set highlights.
  elements: Elements
  highlightedColors[]: [int]
  ?wireframe3D: bool
  ?nonHighlightedColor[]: int
  → 

### MoveElements
# Moves elements with a given vector.
  elementsWithMoveVectors[]: elementId: ElementId, moveVector: {x: float, y: float, z: float}, ?copy: bool
  → executionResults: ExecutionResults

### DeleteElements
# Deletes elements.
  elements: Elements
  → 

### LockElements
# Locks the given elements. Manual lock, not teamwork!
  elements: Elements
  → 

### UnlockElements
# Unlocks the given elements. Manual lock, not teamwork!
  elements: Elements
  → 

### GetGDLParametersOfElements
# Gets all the GDL parameters (name, type, value) of the given elements.
  elements: Elements
  → gdlParametersOfElements: [GDLParameterList]

### SetGDLParametersOfElements
# Sets the given GDL parameters of the given elements.
  elementsWithGDLParameters[]: elementId: ElementId, gdlParameters: SetGDLParameterArray
  → executionResults: ExecutionResults

### CreateColumns
# Creates Column elements based on the given parameters.
  columnsData[]: coordinates: {x: float, y: float, z: float}, ?height: float, ?axisRotationAngle: float, ?width: float, ?depth: float, ?coreAnchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"

### CreateWalls
# Creates Wall elements based on the given parameters.
  wallsData[]: begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, zCoordinate: float, height: float, thickness: float, ?offset: float, ?referenceLineLocation: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside", ?structureType: "Basic"|"Composite"|"Profile", ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?arcAngle: float, ?floorIndex: int  # arcAngle: radians; non-zero = curved wall (chord = beg/endCoordinate), since PR #435 (1.5.4). floorIndex: place the wall directly on a story index; zCoordinate then becomes bottomOffset relative to that story — since main 2026-07-06 (#437)

### CreateBeams
# Creates Beam elements based on the given parameters.
  beamsData[]: begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, zCoordinate: float, ?offset: float, ?slantAngle: float, ?arcAngle: float, ?verticalCurveHeight: float, ?width: float, ?height: float, ?anchorPoint: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"

### CreateStairs
# Creates Stair elements based on the given baseline and parameters.
  stairsData[]: baseLinePoints: [Coordinate2D], zCoordinate: float, ?totalHeight: float, ?flightWidth: float, ?stepNum: int, ?riserHeight: float, ?treadDepth: float
  # ⚠ L/U shapes (3+ points): on releases <=1.5.3 ALWAYS fails with -2130313215 (bug #444); fixed since release 1.5.4 (#445) and works provided the geometry is solvable. stepNum/treadDepth/riserHeight are ignored (#425).

### CreateSlabs
# Creates Slab elements based on the given parameters.
  slabsData[]: level: float, ?thickness: float, ?referencePlaneLocation: "Top"|"CoreTop"|"CoreBottom"|"Bottom", polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D

### CreateWindows
# Creates Window elements in host walls based on the given parameters.
  windowsData[]: ownerWallId: ElementId, centerOffset: float, ?sillHeight: float, ?width: float, ?height: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?favoriteName: string
  → elements: Elements

### CreateDoors
# Creates Door elements in host walls based on the given parameters.
  doorsData[]: ownerWallId: ElementId, centerOffset: float, ?sillHeight: float, ?width: float, ?height: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?favoriteName: string
  → elements: Elements

### CreateOpenings
# Creates Opening elements in the given host elements.
  openingsData[]: ownerElementId: ElementId, basePoint: Coordinate3D, ?width: float, ?height: float
  → elements: Elements

### CreateMorphs
# Creates Morph elements from simple box definitions.
  morphsData[]: basePoint: Coordinate3D, size: Dimensions3D, ?buildingMaterialId: AttributeId
  → elements: Elements

### CreateRoofs
# Creates multi-plane Roof elements based on footprint, level and roof profile data.
# ⚠ Releases <=1.5.5: NON-FUNCTIONAL (stub, #467) — model roofs as Slab/Morph instead. FIXED since release 1.5.6 (#482): multi-plane works; NEW ?pivotLine:{begCoordinate,endCoordinate} + ?angle (rad) for single-plane (the plane rises to the left of the line direction).
  roofsData[]: level: float, ?thickness: float, polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?eavesOverhang: float, ?levels: [{levelHeight: float, levelAngle: float}], ?structureType: "Basic"|"Composite", ?buildingMaterialId: AttributeId, ?compositeId: AttributeId

### CreateAssociativeDimensions
# Creates associative linear dimensions from explicit witness point references.
  dimensionsData[]: referencePoint: Coordinate2D, direction: Coordinate2D, ?floorIndex: float, witnessPoints: [{elementId: ElementId, line: bool, inIndex: int, special: int, nodeType: int, ...}]
  → elements: Elements

### CreateAssociativeDimensionsOnSection
# Creates associative linear dimensions on section elements using common wall, slab, beam, column and opening presets.
  dimensionsData[]: sectionElementId: ElementId, referencePoint: Coordinate2D, preset: "WallCompositeFaces"|"WallSkinBorders"|"SlabCompositeFaces"|"SlabSkinBorders"|"BeamOrColumnRefLineEndPoints"|"BeamOrColumnBoundingBoxCorners"|"DoorWindowWallHoleCorners"|"DoorWindowModelHotspots", ?direction: Coordinate2D, ?skinBorderIndices: [int], ?beginPlane: bool, ?totalSizePlane: bool, ?placeOnTop: bool
  → elements: Elements

### CreateWallThicknessDimensions
# Creates associative wall thickness dimensions for the given walls.
  dimensionsData[]: wallId: ElementId, referencePoint: Coordinate2D, direction: Coordinate2D
  → elements: Elements

### GetDimensionData
# Gets witness point data (coordinates, measured values) from existing dimension chains.
  elements[]: elementId: ElementId
  → dimensionsData: [DimensionDataOrError]

### CreateZones
# Creates Zone elements based on the given parameters.
  zonesData[]: ?floorIndex: float, name: string, numberStr: string, ?categoryAttributeId: AttributeId, ?stampPosition: Coordinate2D, geometry: ZoneCreationGeometry

### CreatePolylines
# Creates Polyline elements based on the given parameters.
  polylinesData[]: ?floorInd: float, ?layerIndex: int, ?linePenIndex: int, ?lineTypeIndex: int, ?penWeightMm: float, coordinates: [Coordinate2D], ?arcs: [PolyArc]

### CreateObjects
# Creates Object elements based on the given parameters.
  objectsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D

### CreateLamps
# Creates Lamp elements based on the given parameters.
  lampsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D

### CreateMeshes
# Creates Mesh elements based on the given parameters.
  meshesData[]: ?floorIndex: int, ?level: float, ?skirtType: MeshSkirtType, ?skirtLevel: float, ?ridges: "AllSharp"|"AllSmooth"|"UserDefined", ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [{coordinates: [Coordinate3D]}]

### CreateLabels
# Creates Label elements based on the given parameters.
  labelsData[]: ?parentElementId: ElementId, ?text: string, ?begCoordinate: Coordinate2D, ?floorInd: float

### CreateTexts
# Creates standalone Text elements based on the given parameters.
  textsData[]: coordinate: Coordinate3D, text: string, ?height: float, ?pen: int, ?angle: float, ?justification: "Left"|"Center"|"Right"|"Full", ?floorIndex: int

### ModifyWalls
# Modifies Wall elements based on the given parameters.
  wallsWithDetails[]: elementId: ElementId, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?height: float, ?thickness: float, ?bottomOffset: float, ?offset: float, ?structureType: "Basic"|"Composite"|"Profile", ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?arcAngle: float  # radians; curves a straight wall, 0 straightens, since PR #435
  → executionResults: ExecutionResults

### ModifyBeams
# Modifies Beam elements based on the given parameters.
  beamsWithDetails[]: elementId: ElementId, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?level: float, ?offset: float, ?slantAngle: float, ?arcAngle: float, ?verticalCurveHeight: float

### ModifySlabs
# Modifies Slab elements based on the given parameters.
  slabsWithDetails[]: elementId: ElementId, ?zCoordinate: float, ?thickness: float, ?structureType: "Basic"|"Composite", ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D

### ModifyColumns
# Modifies Column elements based on the given parameters.
  columnsWithDetails[]: elementId: ElementId, ?origin: Coordinate2D, ?zCoordinate: float, ?height: float, ?bottomOffset: float, ?axisRotationAngle: float

### ModifyWindows
# Modifies Window elements based on the given parameters.
  windowsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool

### ModifyDoors
# Modifies Door elements based on the given parameters.
  doorsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool

### ModifyMorphs
# Modifies Morph elements based on the given parameters.
  morphsWithDetails[]: elementId: ElementId, ?translation: Coordinate3D, ?rotationDegreesZ: float, ?buildingMaterialId: AttributeId

### ModifyRoofs
# Modifies multi-plane Roof elements based on the given parameters.
  roofsWithDetails[]: elementId: ElementId, ?level: float, ?thickness: float, ?eavesOverhang: float, ?levels: [{levelHeight: float, levelAngle: float}], ?structureType: "Basic"|"Composite", ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D

### GetElementPreviewImage
# Returns the preview image of the given element.
  elementId: ElementId
  ?imageType: "2D"|"Section"|"3D"
  ?format: "png"|"jpg"
  ?width: int
  ?height: int
  → previewImage: string

### GetRoomImage
# Returns the room image of the given zone.
  zoneId: ElementId
  ?format: "png"|"jpg"
  ?width: int
  ?height: int
  ?offset: float
  ?scale: float
  ?backgroundColor: ColorRGB
  → roomImage: string

### AddElementNotificationClient
# Sets up a new notification client to receive element events.
  ?host: string
  port: int
  ?notifyOnNewElement: bool
  ?notifyOnModificationOfAnElement: bool
  ?notifyOnReservationChanges: bool
  → 

### RemoveElementNotificationClient
# Removes an element notification client.
  ?host: string
  port: int
  → 

## Element grouping Commands

### CreateGroups
# Creates groups of the passed elements
  elementGroups[]: ElementGroupParameters
  → groupGuids: [GroupIdOrError]

## Favorites Commands

### GetFavoritesByType
# Returns a list of the names of all favorites with the given element type
  elementType: ElementType
  → 

### GetFavoritePreviewImage
# Returns the preview image of the given favorite.
  favorite: string
  ?imageType: "2D"|"Section"|"3D"
  ?format: "png"|"jpg"
  ?width: int
  ?height: int
  → previewImage: string

### ApplyFavoritesToElementDefaults
# Apply the given favorites to element defaults.
  favorites: Favorites
  → executionResults: ExecutionResults

### CreateFavoritesFromElements
# Create favorites from the given elements.
  favoritesFromElements[]: elementId: ElementId, favorite: string
  → executionResults: ExecutionResults

### ImportFavorites
# Import Favorites from a .prefs file or folder into the current project.
  path: string
  ?targetFolder[]: string
  ?importFolders: bool
  ?conflictPolicy: "Error"|"Skip"|"Overwrite"|"Append"
  → firstConflictName: string

### ExportFavorites
# Export the project's Favorites to a .prefs file or folder.
  path: string
  ?names[]: string
  → 

## Property Commands

### GetAllProperties
# Returns all user defined and built-in properties.
  (no parameters)
  → properties: [PropertyDetails]

### GetPropertyValuesOfElements
# Returns the property values of the elements for the given property. It works for subelements of hierarchal elements also.
  elements: Elements
  properties: PropertyIds
  → propertyValuesForElements: PropertyValuesOrErrorArray

### SetPropertyValuesOfElements
# Sets the property values of elements. It works for subelements of hierarchal elements also.
  elementPropertyValues: ElementPropertyValues
  → executionResults: ExecutionResults

### GetPropertyValuesOfAttributes
# Returns the property values of the attributes for the given property.
  attributeIds: AttributeIds
  properties: PropertyIds
  → propertyValuesForAttributes: PropertyValuesOrErrorArray

### SetPropertyValuesOfAttributes
# Sets the property values of attributes.
  attributePropertyValues: AttributePropertyValues
  → executionResults: ExecutionResults

### CreatePropertyGroups
# Creates Property Groups based on the given parameters.
  propertyGroups[]: PropertyGroupArrayItem
  → propertyGroupIds: [PropertyGroupIdArrayItem]

### DeletePropertyGroups
# Deletes the given Custom Property Groups.
  propertyGroupIds[]: PropertyGroupIdArrayItem
  → executionResults: ExecutionResults

### CreatePropertyDefinitions
# Creates Custom Property Definitions based on the given parameters.
  propertyDefinitions[]: PropertyDefinitionArrayItem
  → propertyIds: PropertyIdOrErrorArray

### DeletePropertyDefinitions
# Deletes the given Custom Property Definitions.
  propertyIds[]: PropertyIdArrayItem
  → executionResults: ExecutionResults

## Classification Commands

### GetClassificationsOfElements
# Returns the classification of the given elements in the given classification systems. It works for subelements of hierarchal elements also.
  elements: Elements
  classificationSystemIds: ClassificationSystemIds
  → elementClassifications: ElementClassificationsOrErrors

### SetClassificationsOfElements
# Sets the classifications of elements. In order to set the classification of an element to unclassified, omit the classificationItemId field. It works for subelements of hierarchal elements also.
  elementClassifications: ElementClassifications
  → executionResults: ExecutionResults

### CreateClassificationSystems
# Creates Classification Systems including Classification Items based on the given parameters.
  classificationSystemsWithItems: ClassificationSystemsWithItems
  → executionResults: ExecutionResults

### CreateClassificationItems
# Creates Classification Items in the given Classification Systems based on the given parameters.
  newClassificationItems: NewClassificationItems
  → executionResults: ExecutionResults

### DeleteClassificationSystems
# Deletes the given Classification Systems.
  classificationSystemIds: ClassificationSystemIds
  → executionResults: ExecutionResults

### DeleteClassificationItems
# Deletes the given Classification Items.
  classificationItemIds: ClassificationItemIds
  → executionResults: ExecutionResults

## Attribute Commands

### GetAttributesByType
# Returns the details of every attribute of the given type.
  attributeType: AttributeType
  → 

### CreateLayers
# Creates or overwrites Layer attributes based on the given parameters.
  layerDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?isHidden: bool, ?isLocked: bool, ?isWireframe: bool, ?intersectionGroupNr: int
  ?overwriteExisting: bool

### CreateLayerCombinations
# Creates or overwrites Layer Combination attributes based on the given parameters.
  layerCombinationDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, layers: LayersOfLayerCombination
  ?overwriteExisting: bool

### CreateBuildingMaterials
# Creates or overwrites Building Material attributes based on the given parameters.
  buildingMaterialDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?id: string, ?manufacturer: string, ?description: string, ?connPriority: int, ?cutFillIndex: int, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutSurfaceIndex: int, ?thermalConductivity: float, ?density: float, ?heatCapacity: float, ?embodiedEnergy: float, ?embodiedCarbon: float
  ?overwriteExisting: bool

### CreateComposites
# Creates or overwrites Composite attributes based on the given parameters.
  (no parameters)
  → attributeIds: AttributeIds

### CreateSurfaces
# Creates or overwrites Surface attributes based on the given parameters.
  surfaceDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, materialType: SurfaceType, ambientReflection: float, diffuseReflection: float, specularReflection: float, transparency: float, shine: float, transparencyAttenuation: float, emissionAttenuation: float, surfaceColor: ColorRGB, specularColor: ColorRGB, emissionColor: ColorRGB, ?fillId: AttributeIdArrayItem, ?texture: Texture
  ?overwriteExisting: bool

### GetBuildingMaterialPhysicalProperties
# Retrieves the physical properties of the given Building Materials.
  attributeIds: AttributeIds
  → properties: BuildingMaterialPhysicalPropertiesList

### GetLayerCombinations
# Returns the details of layer combination attributes.
  attributes: AttributeIds
  → layerCombinations: [LayerCombinationAttributeOrError]

## IFC Commands

### IFCFileOperation
# Executes an IFC file operation.
  method: "save"|"merge"|"open"
  ifcFilePath: string
  ?fileType: "ifc"|"ifcxml"|"ifczip"|"ifcxmlzip"
  → 

### GetElementsByIFCIds
# Retrieves the elements by the given IFC identifiers.
  ifcIds[]: string
  → elementsByIFCIds: ElementsByIFCIds

### GetIFCIdsOfElements
# Retrieves the IFC identifiers of the given elements.
  elements: Elements
  → elementIFCIds: ElementIFCIdsOrErrors

### GetIFCTypeOfElements
# Retrieves the IFC types of the given elements.
  elements: Elements
  → elementIFCTypes: ElementIFCTypesOrErrors

### GetIFCPropertiesOfElements
# Retrieves the IFC properties of the given elements.
  elements: Elements
  → elementIFCProperties: ElementIFCPropertiesOrErrors

## Library Commands

### GetLibraries
# Gets the list of loaded libraries.
  (no parameters)
  → libraries: [{name: string, path: string, type: string, available: bool, readOnly: bool, ...}]

### ReloadLibraries
# Executes the reload libraries command.
  (no parameters)
  → 

### AddFilesToEmbeddedLibrary
# Adds the given files into the embedded library.
  files: LibraryFileAdditions
  → executionResults: ExecutionResults

### GetAvailableLibraryParts
# Lists library parts currently available to the project. Filter by typeId (e.g. 'Door', 'Window', 'Object', 'Lamp').
  ?filterByTypeId: LibraryPartType
  → libraryParts: [{guid: string, index: int, documentName: string, fileName: string, typeId: LibraryPartType}], skippedCount: int, skippedSample: [{index: int, code: int}]

## Teamwork Commands

### TeamworkSend
# Performs a send operation on the currently opened Teamwork project.
  (no parameters)
  → 

### TeamworkReceive
# Performs a receive operation on the currently opened Teamwork project.
  (no parameters)
  → 

### ReserveElements
# Reserves elements in Teamwork mode.
  elements: Elements
  → executionResult: ExecutionResult, conflicts: [{elementId: ElementId, user: {userId: float, userName: string}}]

### ReleaseElements
# Releases elements in Teamwork mode.
  elements: Elements
  → 

## Navigator Commands

### PublishPublisherSet
# Performs a publish operation on the currently opened project. Only the given publisher set will be published.
  publisherSetName: string
  ?outputPath: string
  ?selectedNavigatorItemIds: NavigatorItemIds

### UpdateDrawings
# Performs a drawing update on the given elements.
  elements: Elements
  → 

### GetDatabaseIdFromNavigatorItemId
# Gets the ID of the database associated with the supplied navigator item id
  navigatorItemIds: NavigatorItemIds
  → databases: Databases

### CreateDetails
# Creates independent Detail databases.
  detailsData[]: name: string, referenceId: string
  → databases: Databases

### CreateWorksheets
# Creates independent Worksheet databases.
  worksheetsData[]: name: string, referenceId: string

### CreateLayouts
# Creates Layouts and their backing master layouts.
  layoutsData[]: masterLayoutName: string, layoutName: string

### CreateSubsets
# Creates Layout Book subsets.
  subsetsData[]: name: string, ?parentNavigatorItemId: NavigatorItemId, ?ownPrefix: string, ?customNumber: string
  → executionResults: ExecutionResults

### CreateDrawings
# Creates Drawing elements on the specified or active layout from navigator items.
  drawingsData[]: navigatorItemId: NavigatorItemId, ?layoutDatabaseId: DatabaseId, name: string, position: Coordinate2D, ?scale: float
  → elements: Elements

### GetModelViewOptions
# Gets all model view options
  (no parameters)
  → modelViewOptions: [{name: string}]

### GetViewSettings
# Gets the view settings of navigator items
  navigatorItemIds: NavigatorItemIds
  → viewSettings: [ViewSettingsOrError]

### SetViewSettings
# Sets the view settings of navigator items
  navigatorItemIdsWithViewSettings[]: navigatorItemId: NavigatorItemId, viewSettings: ViewSettings
  → executionResults: ExecutionResults

### GetView2DTransformations
# Get zoom and rotation of 2D views
  ?databases: Databases
  → transformations: [ViewTransformationsOrError]

### Set3DCutPlanes
# Sets the 3D cut planes.
  ?cutPlanes[]: pa: float, pb: float, pc: float, pd: float
  → 

### FitInWindow
# Zooms to the given elements or fits everything in the window.
  ?elements: Elements
  → 

### CreateSections
# Creates Section elements on the floor plan.
  sectionsData[]: startCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?depth: float, ?name: string, ?floorIndex: int
  → elements: Elements

## Issue Management Commands

### CreateIssue
# Creates a new issue.
  name: string
  ?parentIssueId: IssueId
  ?tagText: string
  → issueId: IssueId

### DeleteIssue
# Deletes the specified issue.
  issueId: IssueId
  ?acceptAllElements: bool
  → 

### GetIssues
# Retrieves information about existing issues.
  (no parameters)
  → issues: [{issueId: IssueId, name: string, parentIssueId: IssueId, creaTime: int, modiTime: int, ...}]

### AddCommentToIssue
# Adds a new comment to the specified issue.
  issueId: IssueId
  ?author: string
  ?status: IssueCommentStatus
  text: string
  → 

### GetCommentsFromIssue
# Retrieves comments information from the specified issue.
  issueId: IssueId
  → comments: [{guid: Guid, author: string, text: string, status: IssueCommentStatus, creaTime: int}]

### AttachElementsToIssue
# Attaches elements to the specified issue.
  issueId: IssueId
  elements: Elements
  type: IssueElementType
  → 

### DetachElementsFromIssue
# Detaches elements from the specified issue.
  issueId: IssueId
  elements: Elements
  → 

### GetElementsAttachedToIssue
# Retrieves attached elements of the specified issue, filtered by attachment type.
  issueId: IssueId
  type: IssueElementType
  → elements: Elements

### ExportIssuesToBCF
# Exports specified issues to a BCF file.
  ?issues: Issues
  exportPath: string
  useExternalId: bool
  alignBySurveyPoint: bool
  → 

### ImportIssuesFromBCF
# Imports issues from the specified BCF file.
  importPath: string
  alignBySurveyPoint: bool
  → 

## Revision Management Commands

### GetRevisionIssues
# Retrieves all issues.
  (no parameters)
  → revisionIssues: [RevisionIssue]

### GetRevisionChanges
# Retrieves all changes.
  (no parameters)
  → revisionChanges: [RevisionChange]

### GetDocumentRevisions
# Retrieves all document revisions.
  (no parameters)
  → documentRevisions: [DocumentRevision]

### GetCurrentRevisionChangesOfLayouts
# Retrieves all changes belong to the last revision of the given layouts.
  layoutDatabaseIds: Databases
  → currentRevisionChangesOfLayouts: RevisionChangesOfEntities

### GetRevisionChangesOfElements
# Retrieves the changes belong to the given elements.
  elements: Elements
  → revisionChangesOfElements: RevisionChangesOfEntities

## Design Options Commands

### GetDesignOptions
# Retrieves information about existing design options. Available from Archicad 29.
  (no parameters)
  → designOptions: [DesignOptionDetails]

### GetDesignOptionSets
# Retrieves information about existing design option sets. Available from Archicad 29.
  (no parameters)
  → designOptionSets: [{designOptionSetId: GuidId, name: string, designOptions: [DesignOptionIdArrayItem]}]

### GetDesignOptionCombinations
# Retrieves information about existing design option combinations.
  (no parameters)
  → designOptionCombinations: [{designOptionCombinationId: GuidId, name: string, activeDesignOptions: [DesignOptionIdArrayItem]}]

### GetElementsOfDesignOptions
# Retrieves the elements associated with the given design options. Available from Archicad 29.
  designOptions[]: designOptionId: DesignOptionId
  → elementsOfDesignOptions: []

### GetDesignOptionForElements
# Retrieves the design option association for the specified elements. Available from Archicad 29.
  elements: Elements
  → designOptionForElements: [{elementId: ElementId, type: "NotExistingElement"|"MissingDesignOption"|"NotLinkedToAnyDesignOption"|"LinkedToDesignOption", designOption: DesignOptionDetails}]

### CreateDesignOptionSets
# Creates new design option sets with the given names. Available from Archicad 29.
  designOptionSets[]: string
  → executionResults: ExecutionResults

### CreateDesignOptions
# Creates new design options with the given parameters. Available from Archicad 29.
  designOptions[]: name: string, id: string, ownerSetName: string
  → designOptionIdsOrErrors: DesignOptionIdsOrErrors

### CreateDesignOptionCombinations
# Creates new design option combinations with the given parameters. Available from Archicad 29.
  designOptionCombinations[]: name: string, activeDesignOptions: [DesignOptionIdArrayItem]
  → designOptionCombinationIdsOrErrors: DesignOptionCombinationIdsOrErrors

### SetActiveDesignOptionsInCombinations
# Sets active design options in the given combinations. Available from Archicad 29.
  activeDesignOptionsInCombinations[]: designOptionCombinationId: DesignOptionCombinationId, activeDesignOptions: [DesignOptionIdArrayItem]
  → executionResults: ExecutionResults

### MoveElementsToDesignOptions
# Moves the given elements into the given design options. Use NULLGuid for design option to remove the element from any design options and move it to the main model. Available from Archicad 29.
  elementDesignOptionPairs[]: elementId: ElementId, designOptionId: DesignOptionId
  → executionResults: ExecutionResults

### MoveDesignOptionsToAnotherSet
# Moves the given design options to another sets. Available from Archicad 29.
  designOptionAndSetPairs[]: ?designOptionId: DesignOptionId, setName: string
  → executionResults: ExecutionResults

## Layout book & Navigator (#441 — since release 1.5.4)
# Probe exact schemas field-by-field / verify against Examples/test_layout_workflow.py, test_layout_settings.py, test_navigator_views.py in the upstream repo.
### CreateLayoutSubset      # subset with numbering (style, prefix, startAt, continueNumbering...)
### CreateLayout           # layout with layoutParameters (size, margins, numbering, master by name/ID)
### GetLayoutSettings      # read layout parameters (also master layouts)
### SetLayoutSettings      # change layout parameters; horizontalSize/verticalSize ONLY on master layouts; verify showMasterBelow via readback
### GetLayoutCustomScheme  # read the custom layout scheme / custom data
### CreateViewMapFolder    # create a folder in the view map
### CloneProjectMapItemToViewMap  # clone a project map item as a view
### CreateViewsInViewMap   # create views in the view map
### SetViewRotation        # set view rotation (plan north/orientation)
### GetNavigatorItemTree   # read the navigator tree + IDs (starting point for all navigator ops)
### MoveNavigatorItem      # move a navigator item
### RenameNavigatorItem    # rename a navigator item
### DeleteNavigatorItems   # delete navigator items

## New in release 1.5.6 (2026-07-31) — probe schemas before use
### Keynote commands (#472, AC28+)      # keynote tree + keynote labels
### MEP commands (#473, AC28+)          # create/modify/connect/query
### GetGroupsOfElements | GetElementsOfGroups | GetSuspendGroupsMode | SetSuspendGroupsMode   # element grouping (#475)
### 2D drawing elements GET/SET/Create (#484)   # pure drafting elements
### ShowAlert (#468) | GetSpecialFolders (#487) | GetUserGSID (#478)   # drawing titles via Get/SetDetailsOfElements (#464)

## New since release 1.5.4 (#447/#448/#451/#455/#456)
# Probe schemas before use; details in tapir-verified-command-schemas.md.
### DeleteAttributes         # attributes:[{attributeId:{guid}}] — delete attributes (#447)
### GetLayers | GetBuildingMaterials | GetComposites | GetFills | GetLines | GetPenTables | GetProfiles | GetSurfaces | GetZoneCategories | GetMEPSystems
#   detail reads per attribute type; input attributeIds REQUIRED (listing still via GetAttributesByType); optional fields[] filter (#447)
### CreateFills | CreateLines | CreatePenTables | CreateProfiles | CreateZoneCategories | CreateMEPSystems   # new attribute create commands (#447)
### ApplyFavoritesToElements | UpdateFavoritesFromElements | RenameFavorites | DeleteFavorites   # favorites completion (#451)
# floorIndex (#448) now available in ALL create commands — ⚠ semantics split: CreateWalls z is RELATIVE to the story; all other commands z is ABSOLUTE (floorIndex only pins the home story). Verified live.
# GDL array parameters are editable (#455). Fixes #443/#445/#446 are included since release 1.5.4.
### UpdateZones               # update existing zones (#461, since release 1.5.5)
### ModifyMorphs              # + full Morph coverage in Get/CreateMorphs (#449, since release 1.5.5)

## Developer Commands

### GenerateDocumentation
# Generates files for the documentation. Used by Tapir developers only.
  destinationFolder: string
  → 
