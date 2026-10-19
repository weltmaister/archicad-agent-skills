# Tapir Archicad Commands v1.7.2

Generated from Tapir 1.7.2's command reference (314 commands) by
`tools/generate_tapir_catalog.py`. Signatures are the add-on's own schemas; the `# ...` lines
under a description are verified notes and warnings carried over from live use. Field names,
required fields and version gates that matter in practice are in
`tapir-verified-command-schemas.md` - read that first for anything it covers.

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

Port discovery: scan 19723-19743 and ask each answering port `API.GetProductInfo` for its Archicad version - ports follow the start order, so never infer the version from the port.

## Notation
- `?field` = optional
- `field[]` = array of items (an array of objects lists the item's fields)
- `→` = response
- `"A"|"B"` = enum values
- `A | B` = one of several shapes
- `(since x.y.z)` = the Tapir version that introduced the command; `[AC27+]` and similar = Archicad versions named in the description
- Types: float, int, bool, string; other names are the shared types below

## Cross-cutting notes (verified live)
- `floorIndex` is available in all create commands, with split semantics: `CreateWalls` `z` is RELATIVE to the story, all other create commands take `z` ABSOLUTE (`floorIndex` only pins the home story).
- GDL array parameters are editable (since 1.5.4, #455); since 1.7.2 they are written through the API (#558).
- Reads of attribute details (`GetLayers`, `GetBuildingMaterials`, ...) need `attributeIds`; list them first with `GetAttributesByType`.
- Layout and navigator work starts from `GetNavigatorItemTree` (item ids); `SetLayoutSettings` sizes apply to master layouts only - verify by reading back.

## Shared Types

- **AccuracyType**: "Off"|"ShowSmall5"|"ShowSmall25"|"ShowSmall1"|"ShowSmall01"|"InchCaseFractions"
- **AngleType**: "DecimalDegree"|"DegreeMinSec"|"Grad"|"Radian"|"Surveyors"
- **ArcDetails**: {origin: Coordinate2D, radius: float, angle: float, ratio: float, ?begAngle: float, ?endAngle: float, reflected: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **ArcSettings**: {?origin: Coordinate2D, ?radius: float, ?angle: float, ?ratio: float, ?begAngle: float, ?endAngle: float, ?reflected: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **AreaType**: "SquareMeter"|"SquareCentimeter"|"SquareMillimeter"|"SquareFoot"|"SquareInch"
- **AssociativeWitnessPoint**: {elementId: ElementId, ?line: bool, ?inIndex: int, ?special: int, ?nodeType: int, ?nodeStatus: int, ?nodeId: float}
- **AttributeHeaders**: [{attributeId: AttributeId, index: float, name: string, modificationTime: int}]
- **AttributeHeadersOrError**: AttributeHeadersWrapper | ErrorItem
- **AttributeHeadersWrapper**: {attributes: AttributeHeaders}
- **AttributeId**: {guid: Guid}
- **AttributeIdArrayItem**: {attributeId: AttributeId}
- **AttributeIdOrError**: AttributeIdArrayItem | ErrorItem
- **AttributeIds**: [AttributeIdArrayItem]
- **AttributeIdsOrErrors**: [AttributeIdOrError]
- **AttributePropertyValue**: {attributeId: AttributeId, propertyId: PropertyId, propertyValue: PropertyValue}
- **AttributePropertyValues**: [AttributePropertyValue]
- **AttributeType**: "Layer"|"Line"|"Fill"|"Composite"|"Surface"|"LayerCombination"|"ZoneCategory"|"Profile"|"PenTable"|"MEPSystem"|"OperationProfile"|"BuildingMaterial"
- **AutoTextKeyValue**: string
- **AutoTextName**: {name: string}
- **AutoTextNameOrError**: AutoTextName | ErrorItem
- **AutoTextNamesOrErrors**: [AutoTextNameOrError]
- **AutomaticZoneGeometry**: {referencePosition: Coordinate2D}
- **BasicDefaultValue**: {basicDefaultValue: PropertyValueDetails}
- **BeamAnchorPoint**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **BeamDetails**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, zCoordinate: float, level: float, offset: float, slantAngle: float, arcAngle: float, verticalCurveHeight: float, ?beamShape: "Straight"|"HorizontallyCurved"|"VerticallyCurved", ?isSlanted: bool, ?isFlipped: bool, ?profileAngle: float, ?anchorPoint: BeamAnchorPoint, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill, ?holes: [BeamHole], ?width: float, ?height: float, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId}
- **BeamHole**: {holeId: float, type: BeamHoleType, ?showContour: bool, centerX: float, centerZ: float, width: float, ?height: float}
- **BeamHoleModification**: {type: BeamHoleType, ?showContour: bool, centerX: float, centerZ: float, width: float, ?height: float}
- **BeamHoleType**: "Rectangular"|"Circular"
- **BeamQuantities**: {volume: float, volumeConditional: float, holesVolume: float, area: float, leftLength: float, rightLength: float, topSurface: float, bottomSurface: float, leftSurface: float, rightSurface: float, endSurface: float, holesSurface: float, holesEdgeSurface: float, holesNumber: int, crossSectionAreaCutBegin: float, crossSectionAreaCutEnd: float}
- **BeamRelations**: {beamConnections: EndpointConnections}
- **BeamSegmentQuantities**: {volume: float, holesVolume: float, length: float, leftLength: float, rightLength: float, topSurface: float, bottomSurface: float, leftSurface: float, rightSurface: float, endSurface: float, holesSurface: float}
- **BeamSegmentRelations**: {beamSegmentConnections: EndpointConnections}
- **Body3D**: {vertices: [Coordinate3D], polygons: [{vertexIds: [int], ?holes: [{vertexIds: [int]}], ?surfaceId: AttributeId}]}
- **BoundingBox2D**: {xMin: float, yMin: float, xMax: float, yMax: float}
- **BoundingBox3D**: {xMin: float, yMin: float, zMin: float, xMax: float, yMax: float, zMax: float}
- **BoundingBox3DArrayItem**: {boundingBox3D: BoundingBox3D}
- **BoundingBox3DOrError**: BoundingBox3DArrayItem | ErrorItem
- **BoundingBoxes3D**: [BoundingBox3DOrError]
- **BuildingMaterialAttribute**: {attributeId: AttributeId, index: int, name: string, ?id: string, ?manufacturer: string, ?description: string, ?connPriority: int, ?cutFillIndex: int, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutSurfaceIndex: int, ?cutFillOrientation: "ProjectOrigin"|"ElementOrigin"|"FitToSkin", ?thermalConductivity: float, ?density: float, ?heatCapacity: float, ?embodiedEnergy: float, ?embodiedCarbon: float, ?showUncutLines: bool, ?collisionDetection: bool}
- **BuildingMaterialAttributeField**: "id"|"manufacturer"|"description"|"connPriority"|"cutFillIndex"|"cutFillPen"|"cutFillBackgroundPen"|"cutSurfaceIndex"|"cutFillOrientation"|"thermalConductivity"|"density"|"heatCapacity"|"embodiedEnergy"|"embodiedCarbon"|"showUncutLines"|"collisionDetection"
- **BuildingMaterialAttributeOrError**: BuildingMaterialAttribute | ErrorItem
- **BuildingMaterialPhysicalProperties**: {thermalConductivity: float, density: float, heatCapacity: float, embodiedEnergy: float, embodiedCarbon: float}
- **BuildingMaterialPhysicalPropertiesArrayItem**: {properties: BuildingMaterialPhysicalProperties}
- **BuildingMaterialPhysicalPropertiesList**: [BuildingMaterialPhysicalPropertiesArrayItem]
- **ClassificationId**: {classificationSystemId: ClassificationSystemId, ?classificationItemId: ClassificationItemId}
- **ClassificationIdArrayItem**: {classificationId: ClassificationId}
- **ClassificationIdOrError**: ClassificationIdArrayItem | ErrorItem
- **ClassificationIdsOrErrors**: [ClassificationIdOrError]
- **ClassificationItemConflictPolicy**: "replace"|"skip"
- **ClassificationItemDetails**: {id: string, name: string, description: string, ?children: [ClassificationItemDetails]}
- **ClassificationItemId**: {guid: Guid}
- **ClassificationItemIdArrayItem**: {classificationItemId: ClassificationItemId}
- **ClassificationItemIds**: [ClassificationItemIdArrayItem]
- **ClassificationItemUpdate**: {classificationItemId: ClassificationItemId, ?id: string, ?name: string, ?description: string}
- **ClassificationSystemConflictPolicy**: "merge"|"replace"|"skip"
- **ClassificationSystemDetails**: {name: string, description: string, source: string, version: string, date: Date}
- **ClassificationSystemId**: {guid: Guid}
- **ClassificationSystemIdArrayItem**: {classificationSystemId: ClassificationSystemId}
- **ClassificationSystemIds**: [ClassificationSystemIdArrayItem]
- **ClassificationSystemUpdate**: {classificationSystemId: ClassificationSystemId, ?name: string, ?description: string, ?source: string, ?version: string, ?date: Date}
- **ClassificationSystemsWithItems**: [{classificationSystem: ClassificationSystemDetails, classificationItems: [ClassificationItemDetails]}]
- **ColorRGB**: {red: float, green: float, blue: float}
- **ColumnCoreAnchor**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **ColumnDetails**: {origin: Coordinate2D, zCoordinate: float, height: float, bottomOffset: float, ?axisRotationAngle: float, ?coreAnchor: ColumnCoreAnchor, ?isSlanted: bool, ?slantAngle: float, ?slantDirectionAngle: float, ?isFlipped: bool, ?wrapping: bool, ?topOffset: float, ?relativeTopStory: float, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill, ?width: float, ?depth: float, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId}
- **ColumnQuantities**: {coreVolume: float, veneerVolume: float, coreGrossVolume: float, veneerGrossVolume: float, coreSurface: float, veneerSurface: float, coreGrossSurface: float, veneerGrossSurface: float, area: float, perimeter: float, minHeight: float, maxHeight: float, crossSectionAreaCutBegin: float, crossSectionAreaCutEnd: float}
- **ColumnSegmentQuantities**: {volume: float, grossVolume: float, coreVolume: float, coreGrossVolume: float, veneerVolume: float, veneerGrossVolume: float, coreSurface: float, veneerSideSurface: float, length: float, area: float, height: float, minHeight: float, maxHeight: float}
- **CompositeAttribute**: {attributeId: AttributeId, index: int, name: string, ?useWith: [string], ?skins: [CompositeSkin], ?separators: [CompositeSeparator]}
- **CompositeAttributeField**: "useWith"|"skins"|"separators"
- **CompositeAttributeOrError**: CompositeAttribute | ErrorItem
- **CompositeSeparator**: {?lineTypeId: AttributeIdArrayItem, linePen: int}
- **CompositeSkin**: {type: CompositeSkinType, ?buildingMaterialId: AttributeIdArrayItem, framePen: int, thickness: float}
- **CompositeSkinType**: "Core"|"Finish"|"Other"
- **ConnectedElementsOrError**: ConnectedElementsWrapper | ErrorItem
- **ConnectedElementsWrapper**: {connectedElements: [{elements: Elements}]}
- **ConnectionItem**: {elementId: ElementId, connectedWithBeginPoint: bool}
- **Coordinate2D**: {x: float, y: float}
- **Coordinate3D**: {x: float, y: float, z: float}
- **CoordinateWitnessPoint**: {?coordinate: Coordinate2D, ?coordinate3D: Coordinate3D, ?dimensionPosition: Coordinate2D, ?dimensionValue: float, ?witnessForm: "None"|"Small"|"Large"|"Fix"|"Unknown", ?witnessVal: float, ?baseElementId: ElementId, ?line: bool, ?inIndex: int, ?special: int, ?nodeType: int, ?nodeStatus: int, ?nodeId: float}
- **CoverFill**: {use: bool, useFromSurface: bool, orientationComesFrom3D: bool, fillId: AttributeId, foregroundPen: int, backgroundPen: int, transformationType: "Global"|"Rotated"|"Distorted", transformation: CoverFillTransformation}
- **CoverFillOrientation**: {?type: HatchOrientationType, ?origo: Coordinate2D, ?matrix00: float, ?matrix10: float, ?matrix01: float, ?matrix11: float, ?innerRadius: float}
- **CoverFillTransformation**: {origin: Coordinate2D, xAxis: Coordinate2D, yAxis: Coordinate2D}
- **CurtainWallCrossingFrameType**: "None"|"FromBottomLeftToTopRight"|"FromTopLeftToBottomRight"
- **CurtainWallDetails**: {?height: float, ?flipped: bool, ?angle: float}
- **CurtainWallFrameDetails**: {begCoordinate: Coordinate3D, endCoordinate: Coordinate3D, orientationVector: Coordinate3D, panelConnectionHole: {d: float, w: float}, frameContour: {a1: float, a2: float, b1: float, b2: float}, segmentIndex: float, className: string, type: CurtainWallFrameType}
- **CurtainWallFrameType**: "Deleted"|"Division"|"Corner"|"Boundary"|"Custom"
- **CurtainWallPanelDetails**: {polygonCoordinates: [Coordinate3D], isHidden: bool, segmentIndex: float, className: string, frames: [ElementIdArrayItem]}
- **CurtainWallPattern**: {sizes: [float], ?logic: CurtainWallPatternLogic, ?origin: CurtainWallPatternOrigin, ?flexibleIndices: [int]}
- **CurtainWallPatternCell**: {columnIndex: int, rowIndex: int, ?panelClassIndex: int, ?rightPanelClassIndex: int, ?leftFrameClassIndex: int, ?bottomFrameClassIndex: int, ?crossingFrameType: CurtainWallCrossingFrameType, ?crossingFrameClassIndex: int}
- **CurtainWallPatternLogic**: "FixedSizes"|"BestDivision"
- **CurtainWallPatternOrigin**: "StartWithPattern"|"StartFromCenter"|"AlignToCenter"|"EndWithPattern"
- **CurtainWallSegmentDetails**: {begCoordinate: Coordinate3D, endCoordinate: Coordinate3D, extrusionVector: Coordinate3D, gridOrigin: Coordinate3D, gridAngle: float, ?arcOrigin: Coordinate3D, ?isNegativeArc: bool}
- **DatabaseId**: {guid: Guid}
- **DatabaseIdAndWindowType**: {windowType: WindowType, ?databaseId: DatabaseId, ?storyIndex: int}
- **DatabaseIdArrayItem**: {databaseId: DatabaseId}
- **DatabaseIdOrError**: DatabaseIdArrayItem | ErrorItem
- **DatabaseIdsOrErrors**: [DatabaseIdOrError]
- **Databases**: [DatabaseIdArrayItem]
- **Date**: string
- **DesignOptionCombinationData**: {name: string, activeDesignOptions: [DesignOptionIdArrayItem]}
- **DesignOptionCombinationDetails**: {designOptionCombinationId: GuidId, name: string, ?activeDesignOptions: [DesignOptionIdArrayItem]}
- **DesignOptionCombinationId**: {guid: Guid}
- **DesignOptionCombinationIdArrayItem**: {designOptionCombinationId: DesignOptionCombinationId}
- **DesignOptionCombinationIdOrError**: DesignOptionCombinationIdArrayItem | ErrorItem
- **DesignOptionCombinationIdsOrErrors**: [DesignOptionCombinationIdOrError]
- **DesignOptionData**: {name: string, id: string, ownerSetName: string}
- **DesignOptionDetails**: {designOptionId: DesignOptionId, name: string, id: string, ownerSetName: string}
- **DesignOptionId**: {guid: Guid}
- **DesignOptionIdArrayItem**: {designOptionId: DesignOptionId}
- **DesignOptionIdOrError**: DesignOptionIdArrayItem | ErrorItem
- **DesignOptionIdsOrErrors**: [DesignOptionIdOrError]
- **DesignOptionLinkType**: "NotExistingElement"|"MissingDesignOption"|"NotLinkedToAnyDesignOption"|"LinkedToDesignOption"
- **DesignOptionSetId**: {guid: Guid}
- **DesignOptionSetIdArrayItem**: {designOptionSetId: DesignOptionSetId}
- **DetailWorksheetDetails**: {basePoint: Coordinate2D, angle: float, markerId: ElementId, detailName: string, detailIdStr: string, isHorizontalMarker: bool, isWindowOpened: bool, clipPolygon: [Coordinate2D], linkData: {?referredView: ElementId, ?referredDrawing: ElementId, ?referredPMViewPoint: ElementId}}
- **DimensionData**: {?elementId: ElementId, ?direction: Coordinate2D, ?dimensionLinePosition: Coordinate2D, ?witnessPoints: [CoordinateWitnessPoint]}
- **DimensionDataOrError**: DimensionData | ErrorItem
- **DimensionOrigin**: "ProjectZero"|"ReferenceLevel1"|"ReferenceLevel2"|"StoredOrigin"|"Altitude"
- **Dimensions3D**: {x: float, y: float, z: float}
- **DisplayOption**: "Standard"|"StandardWithAbstract"|"CutOnly"|"OutLinesOnly"|"AbstractAll"|"CutAll"
- **DisplayValueEnumId**: {type: "displayValue", displayValue: string}
- **DocumentRevision**: {revisionId: DocumentRevisionId, id: string, finalId: string, ownerUser: string, status: "Actual"|"Issued", ?changes: [{id: string}], layoutInfo: LayoutInfo}
- **DocumentRevisionId**: {guid: Guid}
- **DocumentRevisionReference**: {revisionId: DocumentRevisionId}
- **DocumentRevisionReferences**: [DocumentRevisionReference]
- **DrawingDetails**: {pos: Coordinate2D, angle: float, ratio: float, drawingScale: float, modelOffset: Coordinate2D, isCutWithFrame: bool, bounds: BoundingBox2D, ?clipPolygon: [Coordinate2D], navigatorItemId: NavigatorItemId, nameType: DrawingNameType, ?customName: string, numberingType: DrawingNumberingType, ?customNumber: string, isInNumbering: bool, titleLibraryPartIndex: float, ?titleElementId: ElementId}
- **DrawingNameType**: "ViewOrSourceFileName"|"ViewIdAndName"|"CustomName"
- **DrawingNumberingType**: "ByLayout"|"ByViewId"|"CustomNumber"
- **DrawingSettings**: {?pos: Coordinate2D, ?angle: float, ?ratio: float, ?drawingScale: float, ?modelOffset: Coordinate2D, ?isCutWithFrame: bool, ?clipPolygon: [Coordinate2D], ?nameType: DrawingNameType, ?customName: string, ?numberingType: DrawingNumberingType, ?customNumber: string, ?isInNumbering: bool, ?titleLibraryPartIndex: float}
- **ElectricalCircuitDetails**: {elementId: ElementId, name: string, description: string, ownerPanelId: ElementId, childDevices: Elements, childPanels: Elements, voltage: float, phases: string, isPhaseAUsed: bool, isPhaseBUsed: bool, isPhaseCUsed: bool, wiringTypeName: string, connectedLoad: ElectricalLoads, demandLoad: ElectricalLoads, voltageDrop: float, estimatedCableLength: float}
- **ElectricalCircuitDetailsOrError**: ElectricalCircuitDetails | ErrorItem
- **ElectricalDeviceDetails**: {elementId: ElementId, ?parentCircuitId: ElementId, anchorPoint: Coordinate3D, orientation: MEPOrientation, rotation: float, isReflected: bool, libraryPartId: LibPartUnId, xSize: float, ySize: float, apparentPower: float, isApparentPowerEnabled: bool, loadClassificationName: string, demandLoad: float, connectedElements: Elements}
- **ElectricalDeviceDetailsOrError**: ElectricalDeviceDetails | ErrorItem
- **ElectricalLoads**: {total: float, phaseA: float, phaseB: float, phaseC: float}
- **ElectricalPanelDetails**: {elementId: ElementId, panelName: string, circuitNamePrefix: string, circuitIdStyle: int, circuits: Elements, ?parentCircuitId: ElementId, anchorPoint: Coordinate3D, orientation: MEPOrientation, rotation: float, isReflected: bool, libraryPartId: LibPartUnId, xSize: float, ySize: float, connectedLoad: ElectricalLoads, demandLoad: ElectricalLoads}
- **ElectricalPanelDetailsOrError**: ElectricalPanelDetails | ErrorItem
- **ElementClassification**: {elementId: ElementId, classificationId: ClassificationId}
- **ElementClassificationItemArray**: {classificationIds: ClassificationIdsOrErrors}
- **ElementClassificationOrError**: ElementClassificationItemArray | ErrorItem
- **ElementClassifications**: [ElementClassification]
- **ElementClassificationsOrErrors**: [ElementClassificationOrError]
- **ElementDetailsField**: "type"|"id"|"floorIndex"|"layerIndex"|"drawIndex"|"details"|"floorPlanPolygons"|"hotlinkId"
- **ElementFilter**: "IsEditable"|"IsVisibleByLayer"|"IsVisibleByRenovation"|"IsVisibleByStructureDisplay"|"IsVisibleIn3D"|"OnActualFloor"|"OnActualLayout"|"InMyWorkspace"|"IsIndependent"|"InCroppedView"|"HasAccessRight"|"IsOverriddenByRenovation"|"IncludeSubElemObjects"
- **ElementGroupParameters**: {elements: ElementOrGroupIds, ?parentGroupId: GroupId}
- **ElementIFCIds**: {elementId: ElementId, ifcId: string, externalIFCId: string}
- **ElementIFCIdsOrError**: ElementIFCIds | ErrorItem
- **ElementIFCIdsOrErrors**: [ElementIFCIdsOrError]
- **ElementIFCProperties**: {elementId: ElementId, ifcProperties: [ElementIFCProperty]}
- **ElementIFCPropertiesOrError**: ElementIFCProperties | ErrorItem
- **ElementIFCPropertiesOrErrors**: [ElementIFCPropertiesOrError]
- **ElementIFCProperty**: {propertySetName: string, name: string, value: string}
- **ElementIFCType**: {elementId: ElementId, ifcType: string, typeObjectIFCType: string}
- **ElementIFCTypeOrError**: ElementIFCType | ErrorItem
- **ElementIFCTypesOrErrors**: [ElementIFCTypeOrError]
- **ElementId**: {guid: Guid}
- **ElementIdArrayItem**: {elementId: ElementId}
- **ElementIdOrError**: ElementIdArrayItem | ErrorItem
- **ElementIdsOrErrors**: [ElementIdOrError]
- **ElementOrGroupId**: ElementIdArrayItem | GroupIdArrayItem
- **ElementOrGroupIds**: [ElementOrGroupId]
- **ElementPropertyValue**: {elementId: ElementId, propertyId: PropertyId, propertyValue: PropertyValue}
- **ElementPropertyValues**: [ElementPropertyValue]
- **ElementQuantities**: WallQuantities | ColumnQuantities | BeamQuantities | SlabQuantities | RoofQuantities | ShellQuantities | MorphQuantities | ZoneQuantities | ColumnSegmentQuantities | BeamSegmentQuantities
- **ElementRelationsOrError**: WallRelations | BeamRelations | BeamSegmentRelations | ZoneRelationsOfElement | OpeningRelationsOfElement | RoofOrShellRelationsOfElement | ErrorItem
- **ElementTrims**: {trimmedBy: [{elementId: ElementId, trimType: TrimType}], trims: Elements}
- **ElementTrimsOrError**: ElementTrims | ErrorItem
- **ElementType**: "Wall"|"Column"|"Beam"|"Window"|"Door"|"Object"|"Lamp"|"Slab"|"Roof"|"Mesh"|"Dimension"|"RadialDimension"|"LevelDimension"|"AngleDimension"|"Text"|"Label"|"Zone"|"Hatch"|"Line"|"PolyLine"|"Arc"|"Circle"|"Spline"|"Hotspot"|"CutPlane"|"Camera"|"CamSet"|"Group"|"SectElem"|"Drawing"|"Picture"|"Detail"|"Elevation"|"InteriorElevation"|"Worksheet"|"Hotlink"|"CurtainWall"|"CurtainWallSegment"|"CurtainWallFrame"|"CurtainWallPanel"|"CurtainWallJunction"|"CurtainWallAccessory"|"Shell"|"Skylight"|"Morph"|"ChangeMarker"|"Stair"|"Riser"|"Tread"|"StairStructure"|"Railing"|"RailingToprail"|"RailingHandrail"|"RailingRail"|"RailingPost"|"RailingInnerPost"|"RailingBaluster"|"RailingPanel"|"RailingSegment"|"RailingNode"|"RailingBalusterSet"|"RailingPattern"|"RailingToprailEnd"|"RailingHandrailEnd"|"RailingRailEnd"|"RailingToprailConnection"|"RailingHandrailConnection"|"RailingRailConnection"|"RailingEndFinish"|"BeamSegment"|"ColumnSegment"|"Opening"|"Unknown"
- **Elements**: [ElementIdArrayItem]
- **ElementsByIFCIds**: [{ifcId: string, elements: [ElementIdArrayItem]}]
- **ElementsOfDesignOption**: {designOptionId: DesignOptionId, elements: Elements}
- **ElementsOfDesignOptionOrError**: ElementsOfDesignOption | ErrorItem
- **ElementsOfElementType**: {elementType: ElementType, elements: Elements}
- **ElementsWithExecutionResults**: {elements: Elements, ?executionResultForDatabases: ExecutionResults}
- **ElementsWithExecutionResultsOrError**: ElementsWithExecutionResults | ErrorItem
- **ElementsWrapper**: {elements: Elements}
- **ElementsWrapperOrError**: ElementsWrapper | ErrorItem
- **EndpointConnections**: {connectedToBeginPoint: [ConnectionItem], connectedToEndPoint: [ConnectionItem], connectedWithReferenceLineToEndPoints: [ConnectionItem], connectedToReferenceLine: [ConnectionItem], crossingReferenceLine: [ConnectionItem]}
- **EnumValue**: {?enumValueId: EnumValueId, ?guid: Guid, displayValue: string, ?nonLocalizedValue: string}
- **EnumValueId**: DisplayValueEnumId | NonLocalizedValueEnumId
- **EnumValueIdArrayItem**: {enumValueId: EnumValueId}
- **EnumValueIds**: [EnumValueIdArrayItem]
- **EnumValueToAdd**: {displayValue: string, ?nonLocalizedValue: string}
- **EnumValuesToAdd**: [{enumValue: EnumValueToAdd}]
- **Error**: {code: int, message: string}
- **ErrorItem**: {error: Error}
- **ExecutionResult**: SuccessfulExecutionResult | FailedExecutionResult
- **ExecutionResults**: [ExecutionResult]
- **ExpressionDefaultValue**: {expressions: [string]}
- **FailedExecutionResult**: {success: false, error: Error}
- **FavoriteRename**: {oldName: string, newName: string}
- **Favorites**: [string]
- **FavoritesFromElementUpdate**: {elementId: ElementId, favorite: string}
- **FavoritesOrError**: FavoritesWrapper | ErrorItem
- **FavoritesWrapper**: {favorites: Favorites}
- **FillAttribute**: {attributeId: AttributeId, index: int, name: string, ?subType: FillSubType, ?scaleWithPlan: bool, ?useForWalls: bool, ?useForDraft: bool, ?useForCover: bool, ?horizontalSpacing: float, ?verticalSpacing: float, ?angle: float, ?bitPattern: string, ?gradientStart: Coordinate2D, ?gradientEnd: Coordinate2D, ?percent: float, ?texture: Texture, ?lineItems: [FillLineItem], ?symbolLines: [FillSymbolLine], ?symbolArcs: [FillSymbolArc], ?symbolHotspots: [Coordinate2D]}
- **FillAttributeField**: "subType"|"scaleWithPlan"|"useForWalls"|"useForDraft"|"useForCover"|"horizontalSpacing"|"verticalSpacing"|"angle"|"bitPattern"|"gradientStart"|"gradientEnd"|"percent"|"texture"|"lineItems"|"symbolLines"|"symbolArcs"|"symbolHotspots"
- **FillAttributeOrError**: FillAttribute | ErrorItem
- **FillLineItem**: {frequency: float, direction: float, offsetLine: float, offset: Coordinate2D, ?lineLengths: [float]}
- **FillSubType**: "Vector"|"Solid"|"Empty"|"Symbol"|"LinearGradient"|"RadialGradient"
- **FillSymbolArc**: {begin: Coordinate2D, origin: Coordinate2D, angle: float}
- **FillSymbolLine**: {begin: Coordinate2D, end: Coordinate2D}
- **FloorFill**: {use: bool, foregroundPen: int, backgroundPen: int, fillId: AttributeId, use3DHatching: bool, orientation: HatchOrientation}
- **GDLParameterArray**: [GDLParameterDetails]
- **GDLParameterDetails**: {name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, value: any, ?valueDescription: string, isLocked: bool, flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"], ?possibleValues: PossibleStringValues | PossibleNumericValues, ?canHaveCustomValue: bool, ?itemDescriptions: [string]}
- **GDLParameterList**: {parameters: GDLParameterArray}
- **GeoReferencingParameters**: {crsName: string, description: string, geodeticDatum: string, verticalDatum: string, mapProjection: string, mapZone: string, xAxisAbscissa: float, xAxisOrdinate: float, scale: float}
- **GeoReferencingParametersUpdate**: {?crsName: string, ?description: string, ?geodeticDatum: string, ?verticalDatum: string, ?mapProjection: string, ?mapZone: string, ?xAxisAbscissa: float, ?xAxisOrdinate: float, ?scale: float}
- **GraphicOverrideCombinationId**: {guid: Guid}
- **GraphicOverrideCombinationIdArrayItem**: {graphicOverrideCombinationId: GraphicOverrideCombinationId}
- **GraphicOverrideCombinationIdOrError**: GraphicOverrideCombinationIdArrayItem | ErrorItem
- **GraphicOverrideCriterion**: {?and: [GraphicOverrideCriterion], ?or: [GraphicOverrideCriterion], ?elementType: GraphicOverrideElementType, ?classification: string, ?classificationNot: string, ?classificationSystem: string, ?all3DTypes: bool, ?all2DTypes: bool, ?missingAttributes: bool, ?missingLibraryPart: bool, ?layer: string, ?layerNot: string, ?layerLocked: bool, ?layerVisible: bool, ?layerCombination: string, ?layerCombinationNot: string, ?layerNameIs: string, ?layerNameIsNot: string, ?layerNameContains: string, ?layerNameNotContains: string, ?layerNameStartsWith: string, ?layerNameEndsWith: string, ?compositeStructure: string, ?compositeStructureNot: string, ?complexProfile: string, ?complexProfileNot: string, ?compositeStructureNameIs: string, ?compositeStructureNameIsNot: string, ?compositeStructureNameContains: string, ?compositeStructureNameNotContains: string, ?compositeStructureNameStartsWith: string, ?compositeStructureNameEndsWith: string, ?complexProfileNameIs: string, ?complexProfileNameIsNot: string, ?complexProfileNameContains: string, ?complexProfileNameNotContains: string, ?complexProfileNameStartsWith: string, ?complexProfileNameEndsWith: string, ?roofConnected: bool, ?structureType: "Basic"|"Composite"|"ComplexProfile", ?seaLevelAltitude: float, ?seaLevelAltitudeNot: float, ?seaLevelAltitudeLessThan: float, ?seaLevelAltitudeGreaterThan: float, ?seaLevelAltitudeLessOrEqual: float, ?seaLevelAltitudeGreaterOrEqual: float, ?projectZeroAltitude: float, ?projectZeroAltitudeNot: float, ?projectZeroAltitudeLessThan: float, ?projectZeroAltitudeGreaterThan: float, ?projectZeroAltitudeLessOrEqual: float, ?projectZeroAltitudeGreaterOrEqual: float, ?groundFloorAltitude: float, ?groundFloorAltitudeNot: float, ?groundFloorAltitudeLessThan: float, ?groundFloorAltitudeGreaterThan: float, ?groundFloorAltitudeLessOrEqual: float, ?groundFloorAltitudeGreaterOrEqual: float, ?roofAltitude: float, ?roofAltitudeNot: float, ?roofAltitudeLessThan: float, ?roofAltitudeGreaterThan: float, ?roofAltitudeLessOrEqual: float, ?roofAltitudeGreaterOrEqual: float, ?floorIndex: int, ?sillHeight: float, ?sillHeightNot: float, ?sillHeightLessThan: float, ?sillHeightGreaterThan: float, ?sillHeightLessOrEqual: float, ?sillHeightGreaterOrEqual: float, ?lintelHeight: float, ?lintelHeightNot: float, ?lintelHeightLessThan: float, ?lintelHeightGreaterThan: float, ?lintelHeightLessOrEqual: float, ?lintelHeightGreaterOrEqual: float, ?screedThickness: float, ?screedThicknessNot: float, ?screedThicknessLessThan: float, ?screedThicknessGreaterThan: float, ?screedThicknessLessOrEqual: float, ?screedThicknessGreaterOrEqual: float, ?linkedUpperStoryAbsolute: int, ?linkedUpperStoryRelative: int, ?mepDiameter: float, ?mepDiameterNot: float, ?mepDiameterLessThan: float, ?mepDiameterGreaterThan: float, ?mepDiameterLessOrEqual: float, ?mepDiameterGreaterOrEqual: float, ?mepDiameter2: float, ?mepDiameter2Not: float, ?mepDiameter2LessThan: float, ?mepDiameter2GreaterThan: float, ?mepDiameter2LessOrEqual: float, ?mepDiameter2GreaterOrEqual: float, ?mepDN: int, ?mepDNNot: int, ?mepDNLessThan: int, ?mepDNGreaterThan: int, ?mepDNLessOrEqual: int, ?mepDNGreaterOrEqual: int, ?mepDN2: int, ?mepDN2Not: int, ?mepDN2LessThan: int, ?mepDN2GreaterThan: int, ?mepDN2LessOrEqual: int, ?mepDN2GreaterOrEqual: int, ?mepHeight: float, ?mepHeightNot: float, ?mepHeightLessThan: float, ?mepHeightGreaterThan: float, ?mepHeightLessOrEqual: float, ?mepHeightGreaterOrEqual: float, ?mepHeight2: float, ?mepHeight2Not: float, ?mepHeight2LessThan: float, ?mepHeight2GreaterThan: float, ?mepHeight2LessOrEqual: float, ?mepHeight2GreaterOrEqual: float, ?mepWidth: float, ?mepWidthNot: float, ?mepWidthLessThan: float, ?mepWidthGreaterThan: float, ?mepWidthLessOrEqual: float, ?mepWidthGreaterOrEqual: float, ?mepWidth2: float, ?mepWidth2Not: float, ?mepWidth2LessThan: float, ?mepWidth2GreaterThan: float, ?mepWidth2LessOrEqual: float, ?mepWidth2GreaterOrEqual: float, ?mepAngle: float, ?mepAngleNot: float, ?mepAngleLessThan: float, ?mepAngleGreaterThan: float, ?mepAngleLessOrEqual: float, ?mepAngleGreaterOrEqual: float, ?mepCustomAngle: float, ?mepCustomAngleNot: float, ?mepCustomAngleLessThan: float, ?mepCustomAngleGreaterThan: float, ?mepCustomAngleLessOrEqual: float, ?mepCustomAngleGreaterOrEqual: float, ?mepInsulationThickness: float, ?mepInsulationThicknessNot: float, ?mepInsulationThicknessLessThan: float, ?mepInsulationThicknessGreaterThan: float, ?mepInsulationThicknessLessOrEqual: float, ?mepInsulationThicknessGreaterOrEqual: float, ?mepLength: float, ?mepLengthNot: float, ?mepLengthLessThan: float, ?mepLengthGreaterThan: float, ?mepLengthLessOrEqual: float, ?mepLengthGreaterOrEqual: float, ?mepDescriptionIs: string, ?mepDescriptionIsNot: string, ?mepDescriptionContains: string, ?mepDescriptionNotContains: string, ?mepDescriptionStartsWith: string, ?mepDescriptionEndsWith: string, ?mepMaterialNameIs: string, ?mepMaterialNameIsNot: string, ?mepMaterialNameContains: string, ?mepMaterialNameNotContains: string, ?mepMaterialNameStartsWith: string, ?mepMaterialNameEndsWith: string, ?wallComplexity: "Straight"|"Slanted"|"DoubleSlanted", ?wallComplexityNot: "Straight"|"Slanted"|"DoubleSlanted", ?wallLevelOffset: float, ?wallLevelOffsetNot: float, ?wallLevelOffsetLessThan: float, ?wallLevelOffsetGreaterThan: float, ?wallLevelOffsetLessOrEqual: float, ?wallLevelOffsetGreaterOrEqual: float, ?wallTopOffset: float, ?wallTopOffsetNot: float, ?wallTopOffsetLessThan: float, ?wallTopOffsetGreaterThan: float, ?wallTopOffsetLessOrEqual: float, ?wallTopOffsetGreaterOrEqual: float, ?wallReferenceLinePosition: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside", ?wallReferenceLinePositionNot: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside", ?wallOutsideAngle: float, ?wallOutsideAngleNot: float, ?wallOutsideAngleLessThan: float, ?wallOutsideAngleGreaterThan: float, ?wallOutsideAngleLessOrEqual: float, ?wallOutsideAngleGreaterOrEqual: float, ?wallInsideAngle: float, ?wallInsideAngleNot: float, ?wallInsideAngleLessThan: float, ?wallInsideAngleGreaterThan: float, ?wallInsideAngleLessOrEqual: float, ?wallInsideAngleGreaterOrEqual: float, ?wallThickness: float, ?wallThicknessNot: float, ?wallThicknessLessThan: float, ?wallThicknessGreaterThan: float, ?wallThicknessLessOrEqual: float, ?wallThicknessGreaterOrEqual: float, ?wallHeight: float, ?wallHeightNot: float, ?wallHeightLessThan: float, ?wallHeightGreaterThan: float, ?wallHeightLessOrEqual: float, ?wallHeightGreaterOrEqual: float, ?wallProfileHeight: float, ?wallProfileHeightNot: float, ?wallProfileHeightLessThan: float, ?wallProfileHeightGreaterThan: float, ?wallProfileHeightLessOrEqual: float, ?wallProfileHeightGreaterOrEqual: float, ?wallHeightReversed: bool, ?wallWidth: float, ?wallWidthNot: float, ?wallWidthLessThan: float, ?wallWidthGreaterThan: float, ?wallWidthLessOrEqual: float, ?wallWidthGreaterOrEqual: float, ?wallProfileWidth: float, ?wallProfileWidthNot: float, ?wallProfileWidthLessThan: float, ?wallProfileWidthGreaterThan: float, ?wallProfileWidthLessOrEqual: float, ?wallProfileWidthGreaterOrEqual: float, ?objectLength: float, ?objectLengthNot: float, ?objectLengthLessThan: float, ?objectLengthGreaterThan: float, ?objectLengthLessOrEqual: float, ?objectLengthGreaterOrEqual: float, ?jambThickness1: float, ?jambThickness1Not: float, ?jambThickness1LessThan: float, ?jambThickness1GreaterThan: float, ?jambThickness1LessOrEqual: float, ?jambThickness1GreaterOrEqual: float, ?jambThickness2: float, ?jambThickness2Not: float, ?jambThickness2LessThan: float, ?jambThickness2GreaterThan: float, ?jambThickness2LessOrEqual: float, ?jambThickness2GreaterOrEqual: float, ?curtainWallPanelOffset: float, ?curtainWallPanelOffsetNot: float, ?curtainWallPanelOffsetLessThan: float, ?curtainWallPanelOffsetGreaterThan: float, ?curtainWallPanelOffsetLessOrEqual: float, ?curtainWallPanelOffsetGreaterOrEqual: float, ?stairRiserInclineAngle: float, ?stairRiserInclineAngleNot: float, ?stairRiserInclineAngleLessThan: float, ?stairRiserInclineAngleGreaterThan: float, ?stairRiserInclineAngleLessOrEqual: float, ?stairRiserInclineAngleGreaterOrEqual: float, ?stairMinHeadroom: float, ?stairMinHeadroomNot: float, ?stairMinHeadroomLessThan: float, ?stairMinHeadroomGreaterThan: float, ?stairMinHeadroomLessOrEqual: float, ?stairMinHeadroomGreaterOrEqual: float, ?stairInvalidHeight: bool, ?stairDefaultWidth: float, ?stairDefaultWidthNot: float, ?stairDefaultWidthLessThan: float, ?stairDefaultWidthGreaterThan: float, ?stairDefaultWidthLessOrEqual: float, ?stairDefaultWidthGreaterOrEqual: float, ?stairSlope: float, ?stairSlopeNot: float, ?stairSlopeLessThan: float, ?stairSlopeGreaterThan: float, ?stairSlopeLessOrEqual: float, ?stairSlopeGreaterOrEqual: float, ?stairMaxRiserHeight: float, ?stairMinRiserHeight: float, ?stairMaxGoing: float, ?stairMinGoing: float, ?stairRiserCount: int, ?stairStepCount: int, ?stairStepCountPerFlight: int, ?wallGeometryType: "Uniform"|"Trapezoid"|"Polygonal", ?wallGeometryTypeNot: "Uniform"|"Trapezoid"|"Polygonal", ?wallReferenceLineOffset: float, ?wallReferenceLineOffsetNot: float, ?wallReferenceLineOffsetLessThan: float, ?wallReferenceLineOffsetGreaterThan: float, ?wallReferenceLineOffsetLessOrEqual: float, ?wallReferenceLineOffsetGreaterOrEqual: float, ?wallTopLine: string, ?wallTopLineNot: string, ?wallCutLine: string, ?wallCutLineNot: string, ?wallUncutLine: string, ?wallUncutLineNot: string, ?wallHatchForegroundPen: int, ?wallHatchForegroundPenNot: int, ?wallContourPen: int, ?wallContourPenNot: int, ?wallTopLinePen: int, ?wallTopLinePenNot: int, ?wallCutHatchBackgroundPen: int, ?wallCutHatchBackgroundPenNot: int, ?wallHatchBackgroundPen: int, ?wallHatchBackgroundPenNot: int, ?wallUncutLinePen: int, ?wallUncutLinePenNot: int, ?wallOutsideSurface: string, ?wallOutsideSurfaceNot: string, ?wallInsideSurface: string, ?wallInsideSurfaceNot: string, ?wallSideSurface: string, ?wallSideSurfaceNot: string, ?wallParentIdIs: string, ?wallParentIdIsNot: string, ?wallParentIdContains: string, ?wallParentIdNotContains: string, ?wallParentIdStartsWith: string, ?wallParentIdEndsWith: string, ?wallConnectedOpeningIdsIs: string, ?wallConnectedOpeningIdsIsNot: string, ?wallConnectedOpeningIdsContains: string, ?wallConnectedOpeningIdsNotContains: string, ?wallConnectedOpeningIdsStartsWith: string, ?wallConnectedOpeningIdsEndsWith: string, ?libraryPartNameIs: string, ?libraryPartNameIsNot: string, ?libraryPartNameContains: string, ?libraryPartNameNotContains: string, ?libraryPartNameStartsWith: string, ?libraryPartNameEndsWith: string, ?subTypeNameIs: string, ?subTypeNameIsNot: string, ?subTypeNameContains: string, ?subTypeNameNotContains: string, ?subTypeNameStartsWith: string, ?subTypeNameEndsWith: string, ?columnCoatingType: "Core"|"Finish"|"Other", ?columnCoatingTypeNot: "Core"|"Finish"|"Other", ?columnInclinationAngle: float, ?columnInclinationAngleNot: float, ?columnInclinationAngleLessThan: float, ?columnInclinationAngleGreaterThan: float, ?columnInclinationAngleLessOrEqual: float, ?columnInclinationAngleGreaterOrEqual: float, ?columnCrossSectionType: "Rectangular"|"Circular"|"Profiled", ?columnCoreDiameter: float, ?columnCoreDiameterNot: float, ?columnCoreDiameterLessThan: float, ?columnCoreDiameterGreaterThan: float, ?columnCoreDiameterLessOrEqual: float, ?columnCoreDiameterGreaterOrEqual: float, ?columnCoatingThickness: float, ?columnCoatingThicknessNot: float, ?columnCoatingThicknessLessThan: float, ?columnCoatingThicknessGreaterThan: float, ?columnCoatingThicknessLessOrEqual: float, ?columnCoatingThicknessGreaterOrEqual: float, ?columnBottomCrossSectionHeightCut: float, ?columnBottomCrossSectionHeightCutNot: float, ?columnBottomCrossSectionHeightCutLessThan: float, ?columnBottomCrossSectionHeightCutGreaterThan: float, ?columnBottomCrossSectionHeightCutLessOrEqual: float, ?columnBottomCrossSectionHeightCutGreaterOrEqual: float, ?columnBottomCrossSectionHeightPerpendicular: float, ?columnBottomCrossSectionHeightPerpendicularNot: float, ?columnBottomCrossSectionHeightPerpendicularLessThan: float, ?columnBottomCrossSectionHeightPerpendicularGreaterThan: float, ?columnBottomCrossSectionHeightPerpendicularLessOrEqual: float, ?columnBottomCrossSectionHeightPerpendicularGreaterOrEqual: float, ?columnTopCrossSectionHeightCut: float, ?columnTopCrossSectionHeightCutNot: float, ?columnTopCrossSectionHeightCutLessThan: float, ?columnTopCrossSectionHeightCutGreaterThan: float, ?columnTopCrossSectionHeightCutLessOrEqual: float, ?columnTopCrossSectionHeightCutGreaterOrEqual: float, ?columnTopCrossSectionHeightPerpendicular: float, ?columnTopCrossSectionHeightPerpendicularNot: float, ?columnTopCrossSectionHeightPerpendicularLessThan: float, ?columnTopCrossSectionHeightPerpendicularGreaterThan: float, ?columnTopCrossSectionHeightPerpendicularLessOrEqual: float, ?columnTopCrossSectionHeightPerpendicularGreaterOrEqual: float, ?columnProfileCoreHeight: float, ?columnProfileCoreHeightNot: float, ?columnProfileCoreHeightLessThan: float, ?columnProfileCoreHeightGreaterThan: float, ?columnProfileCoreHeightLessOrEqual: float, ?columnProfileCoreHeightGreaterOrEqual: float, ?columnCoreHeightDiameterRatio: float, ?columnCoreHeightDiameterRatioNot: float, ?columnCoreHeightDiameterRatioLessThan: float, ?columnCoreHeightDiameterRatioGreaterThan: float, ?columnCoreHeightDiameterRatioLessOrEqual: float, ?columnCoreHeightDiameterRatioGreaterOrEqual: float, ?columnBottomCrossSectionWidthCut: float, ?columnBottomCrossSectionWidthCutNot: float, ?columnBottomCrossSectionWidthCutLessThan: float, ?columnBottomCrossSectionWidthCutGreaterThan: float, ?columnBottomCrossSectionWidthCutLessOrEqual: float, ?columnBottomCrossSectionWidthCutGreaterOrEqual: float, ?columnBottomCrossSectionWidthPerpendicular: float, ?columnBottomCrossSectionWidthPerpendicularNot: float, ?columnBottomCrossSectionWidthPerpendicularLessThan: float, ?columnBottomCrossSectionWidthPerpendicularGreaterThan: float, ?columnBottomCrossSectionWidthPerpendicularLessOrEqual: float, ?columnBottomCrossSectionWidthPerpendicularGreaterOrEqual: float, ?columnTopCrossSectionWidthCut: float, ?columnTopCrossSectionWidthCutNot: float, ?columnTopCrossSectionWidthCutLessThan: float, ?columnTopCrossSectionWidthCutGreaterThan: float, ?columnTopCrossSectionWidthCutLessOrEqual: float, ?columnTopCrossSectionWidthCutGreaterOrEqual: float, ?columnTopCrossSectionWidthPerpendicular: float, ?columnTopCrossSectionWidthPerpendicularNot: float, ?columnTopCrossSectionWidthPerpendicularLessThan: float, ?columnTopCrossSectionWidthPerpendicularGreaterThan: float, ?columnTopCrossSectionWidthPerpendicularLessOrEqual: float, ?columnTopCrossSectionWidthPerpendicularGreaterOrEqual: float, ?columnCoreWidth: float, ?columnCoreWidthNot: float, ?columnCoreWidthLessThan: float, ?columnCoreWidthGreaterThan: float, ?columnCoreWidthLessOrEqual: float, ?columnCoreWidthGreaterOrEqual: float, ?columnProfileCoreWidth: float, ?columnProfileCoreWidthNot: float, ?columnProfileCoreWidthLessThan: float, ?columnProfileCoreWidthGreaterThan: float, ?columnProfileCoreWidthLessOrEqual: float, ?columnProfileCoreWidthGreaterOrEqual: float, ?columnCoveringHatch: string, ?columnCoveringHatchNot: string, ?columnCoatingHatch: string, ?columnCoatingHatchNot: string, ?columnCoreForegroundPen: int, ?columnCoreForegroundPenNot: int, ?columnCoatingForegroundPen: int, ?columnCoatingForegroundPenNot: int, ?columnCoveringHatchForegroundPen: int, ?columnCoveringHatchForegroundPenNot: int, ?columnCoveringHatchBackgroundPen: int, ?columnCoveringHatchBackgroundPenNot: int, ?columnCoatingBackgroundPen: int, ?columnCoatingBackgroundPenNot: int, ?columnCoreBackgroundPen: int, ?columnCoreBackgroundPenNot: int, ?columnHiddenLinePen: int, ?columnHiddenLinePenNot: int, ?columnHiddenLineType: string, ?columnHiddenLineTypeNot: string, ?columnCoreSurface: string, ?columnCoreSurfaceNot: string, ?columnCoatingSurface: string, ?columnCoatingSurfaceNot: string, ?columnExtrusionSurface: string, ?columnExtrusionSurfaceNot: string, ?beamAxisPen: int, ?beamAxisPenNot: int, ?beamAxisLineType: string, ?beamAxisLineTypeNot: string, ?beamEndSurface: string, ?beamEndSurfaceNot: string, ?beamRightSurface: string, ?beamRightSurfaceNot: string, ?beamLeftSurface: string, ?beamLeftSurfaceNot: string, ?beamBottomSurface: string, ?beamBottomSurfaceNot: string, ?beamTopSurface: string, ?beamTopSurfaceNot: string, ?slabReferencePlaneLocation: "Top"|"CoreTop"|"CoreBottom"|"Bottom", ?slabReferencePlaneLocationNot: "Top"|"CoreTop"|"CoreBottom"|"Bottom", ?slabEdgeAngle: "Vertical"|"Custom", ?slabEdgeAngleNot: "Vertical"|"Custom", ?slabDefaultEdgeAngle: float, ?slabDefaultEdgeAngleNot: float, ?slabDefaultEdgeAngleLessThan: float, ?slabDefaultEdgeAngleGreaterThan: float, ?slabDefaultEdgeAngleLessOrEqual: float, ?slabDefaultEdgeAngleGreaterOrEqual: float, ?slabCutLinePen: int, ?slabCutLinePenNot: int, ?slabConstructionMaterialFill: string, ?slabConstructionMaterialFillNot: string, ?roofCutBodyType: "ContoursDown"|"ReferenceLineDown", ?roofCutBodyTypeNot: "ContoursDown"|"ReferenceLineDown", ?roofLevelNumber: int, ?roofLevelNumberNot: int, ?roofLevelNumberLessThan: int, ?roofLevelNumberGreaterThan: int, ?roofLevelNumberLessOrEqual: int, ?roofLevelNumberGreaterOrEqual: int, ?roofEaveOverhangType: "Offset"|"Manual", ?roofEdgeAngle: "Vertical"|"Perpendicular"|"Custom", ?roofEdgeAngleNot: "Vertical"|"Perpendicular"|"Custom", ?roofEaveOverhang: float, ?roofEaveOverhangNot: float, ?roofEaveOverhangLessThan: float, ?roofEaveOverhangGreaterThan: float, ?roofEaveOverhangLessOrEqual: float, ?roofEaveOverhangGreaterOrEqual: float, ?roofGeometryType: "SinglePanel"|"MultiplePanels", ?roofGeometryTypeNot: "SinglePanel"|"MultiplePanels", ?roofPitch: float, ?roofPitchNot: float, ?roofPitchLessThan: float, ?roofPitchGreaterThan: float, ?roofPitchLessOrEqual: float, ?roofPitchGreaterOrEqual: float, ?shellCutBodyType: "Editable"|"ExtrudeUp"|"ExtrudeDown", ?shellTiltAngle: float, ?shellTiltAngleNot: float, ?shellTiltAngleLessThan: float, ?shellTiltAngleGreaterThan: float, ?shellTiltAngleLessOrEqual: float, ?shellTiltAngleGreaterOrEqual: float, ?shellGeometryType: "Extrude"|"Revolved"|"Ruled", ?hatchFill: string, ?hatchFillNot: string, ?lineAttribute: string, ?lineAttributeNot: string, ?fontIs: string, ?fontContains: string, ?fontNotContains: string, ?penReplacement: "None"|"ForegroundOnly"|"BackgroundOnly"|"Both", ?penReplacementNot: "None"|"ForegroundOnly"|"BackgroundOnly"|"Both", ?linePenContains: int, ?linePenNotContains: int, ?textPenIs: int, ?textPenContains: int, ?textPenNotContains: int, ?hatchContourPen: int, ?hatchContourPenNot: int, ?openingEndSurface: string, ?openingEndSurfaceNot: string, ?openingExtrusionSurface: string, ?openingExtrusionSurfaceNot: string, ?curtainWallFrameCutLine: string, ?curtainWallFrameCutLineNot: string, ?curtainWallPanelCutLine: string, ?curtainWallPanelCutLineNot: string, ?curtainWallFrameCutLinePen: int, ?curtainWallFrameCutLinePenNot: int, ?curtainWallPanelCutLinePen: int, ?curtainWallPanelCutLinePenNot: int, ?constructionMaterial: string, ?constructionMaterialNot: string, ?surface: string, ?surfaceNot: string, ?constructionMaterialIdIs: string, ?constructionMaterialIdIsNot: string, ?constructionMaterialIdContains: string, ?constructionMaterialIdNotContains: string, ?constructionMaterialIdStartsWith: string, ?constructionMaterialIdEndsWith: string, ?constructionMaterialNameIs: string, ?constructionMaterialNameIsNot: string, ?constructionMaterialNameContains: string, ?constructionMaterialNameNotContains: string, ?constructionMaterialNameStartsWith: string, ?constructionMaterialNameEndsWith: string, ?surfaceNameIs: string, ?surfaceNameIsNot: string, ?surfaceNameContains: string, ?surfaceNameNotContains: string, ?surfaceNameStartsWith: string, ?surfaceNameEndsWith: string, ?renovationFilterIs: string, ?renovationFilterIsNot: string, ?structuralFunction: "LoadBearing"|"NonLoadBearing"|"Undefined", ?structuralFunctionNot: "LoadBearing"|"NonLoadBearing"|"Undefined", ?position: "Exterior"|"Interior"|"Undefined", ?positionNot: "Exterior"|"Interior"|"Undefined", ?variantStateIs: string, ?variantStateIsNot: string, ?variantSetIs: string, ?variantSetIsNot: string, ?elementIdIs: string, ?elementIdIsNot: string, ?elementIdLessThan: string, ?elementIdGreaterThan: string, ?elementIdLessOrEqual: string, ?elementIdGreaterOrEqual: string, ?elementIdContains: string, ?elementIdNotContains: string, ?elementIdStartsWith: string, ?elementIdEndsWith: string, ?uniqueIdIs: string, ?uniqueIdIsNot: string, ?uniqueIdContains: string, ?uniqueIdNotContains: string, ?uniqueIdStartsWith: string, ?uniqueIdEndsWith: string, ?linkMainIdIs: string, ?linkMainIdIsNot: string, ?linkMainIdLessThan: string, ?linkMainIdGreaterThan: string, ?linkMainIdLessOrEqual: string, ?linkMainIdGreaterOrEqual: string, ?linkMainIdContains: string, ?linkMainIdNotContains: string, ?linkMainIdStartsWith: string, ?linkMainIdEndsWith: string, ?linkedElementIdIs: string, ?linkedElementIdIsNot: string, ?linkedElementIdLessThan: string, ?linkedElementIdGreaterThan: string, ?linkedElementIdLessOrEqual: string, ?linkedElementIdGreaterOrEqual: string, ?linkedElementIdContains: string, ?linkedElementIdNotContains: string, ?linkedElementIdStartsWith: string, ?linkedElementIdEndsWith: string, ?nameIs: string, ?nameIsNot: string, ?nameContains: string, ?nameNotContains: string, ?nameStartsWith: string, ?nameEndsWith: string, ?hasLinkSource: bool, ?hasLinkSourceNot: bool, ?missingVariant: bool, ?profileStretchHeight: float, ?profileStretchHeightNot: float, ?profileStretchHeightLessThan: float, ?profileStretchHeightGreaterThan: float, ?profileStretchHeightLessOrEqual: float, ?profileStretchHeightGreaterOrEqual: float, ?profileStretchWidth: float, ?profileStretchWidthNot: float, ?profileStretchWidthLessThan: float, ?profileStretchWidthGreaterThan: float, ?profileStretchWidthLessOrEqual: float, ?profileStretchWidthGreaterOrEqual: float, ?profileNominalHeight: float, ?profileNominalHeightNot: float, ?profileNominalHeightLessThan: float, ?profileNominalHeightGreaterThan: float, ?profileNominalHeightLessOrEqual: float, ?profileNominalHeightGreaterOrEqual: float, ?profileTotalHeight: float, ?profileTotalHeightNot: float, ?profileTotalHeightLessThan: float, ?profileTotalHeightGreaterThan: float, ?profileTotalHeightLessOrEqual: float, ?profileTotalHeightGreaterOrEqual: float, ?profileTotalWidth: float, ?profileTotalWidthNot: float, ?profileTotalWidthLessThan: float, ?profileTotalWidthGreaterThan: float, ?profileTotalWidthLessOrEqual: float, ?profileTotalWidthGreaterOrEqual: float, ?profileNominalWidth: float, ?profileNominalWidthNot: float, ?profileNominalWidthLessThan: float, ?profileNominalWidthGreaterThan: float, ?profileNominalWidthLessOrEqual: float, ?profileNominalWidthGreaterOrEqual: float, ?profileParameter: {name: string, ?equals: float, ?notEquals: float, ?lessThan: float, ?greaterThan: float, ?lessOrEqual: float, ?greaterOrEqual: float}, ?customPropertyBool: {name: string, group: string, ?equals: bool, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyString: {name: string, group: string, ?equals: string, ?notEquals: string, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyNumber: {name: string, group: string, ?equals: float, ?notEquals: float, ?lessThan: float, ?greaterThan: float, ?lessOrEqual: float, ?greaterOrEqual: float, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyInteger: {name: string, group: string, ?equals: int, ?notEquals: int, ?lessThan: int, ?greaterThan: int, ?lessOrEqual: int, ?greaterOrEqual: int, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}}
- **GraphicOverrideElementType**: "Wall"|"Column"|"Beam"|"Slab"|"Roof"|"Shell"|"Stair"|"Railing"|"CurtainWall"|"Opening"|"Mesh"|"Morph"|"Dimension"|"LevelDimension"|"RadialDimension"|"AngleDimension"|"Text"|"ChangeMarker"|"Hatch"|"Line"|"Arc"|"PolyLine"|"Spline"|"Hotspot"|"Section"|"Elevation"|"InteriorElevation"|"Detail"|"Worksheet"|"Camera"|"Figure"|"Drawing"|"StructuralLink"|"StructuralSupport"|"LinearLoad"|"PointLoad"|"SurfaceLoad"|"DuctRouting"|"CableCarrierRouting"|"PipeRouting"
- **GraphicOverrideFillTypes**: {cutFill: bool, coverFill: bool, draftingFill: bool}
- **GraphicOverrideRuleId**: {guid: Guid}
- **GraphicOverrideRuleIdArrayItem**: {graphicOverrideRuleId: GraphicOverrideRuleId}
- **GraphicOverrideRuleIdOrError**: GraphicOverrideRuleIdArrayItem | ErrorItem
- **GraphicOverrideStyle**: {?lineType: AttributeId, ?lineMarkerTextPen: int, ?fillType: AttributeId, ?fillTypeAppliesTo: GraphicOverrideFillTypes, ?fillForegroundPen: int, ?fillForegroundPenAppliesTo: GraphicOverrideFillTypes, ?fillBackgroundPen: int, ?fillBackgroundColor: ColorRGB, ?fillBackgroundPenAppliesTo: GraphicOverrideFillTypes, ?surface: AttributeId, ?surfaceColor: ColorRGB, ?surfaceAppliesTo: GraphicOverrideSurfaceTypes, ?showSkinSeparators: bool, ?overridePenColorAndThickness: bool, ?hiddenContours: GraphicOverrideSurfaceTypes, ?overrideContours: bool}
- **GraphicOverrideSurfaceTypes**: {cutSurface: bool, uncutSurface: bool}
- **GroupId**: {guid: Guid}
- **GroupIdArrayItem**: {groupId: GroupId}
- **GroupIdOrError**: GroupIdArrayItem | ErrorItem
- **Guid**: string
- **GuidId**: {guid: Guid}
- **HatchDetails**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?holes: Holes2D, ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool, zCoordinate: float}
- **HatchOrientation**: {type: HatchOrientationType, origin: Coordinate2D, matrix00: float, matrix10: float, matrix01: float, matrix11: float, innerRadius: float}
- **HatchOrientationType**: "Global"|"Rotated"|"Distorted"|"Centered"
- **HatchSettings**: {?coordinates: [Coordinate2D], ?arcs: [PolyArc], ?holes: Holes2D, ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool}
- **Hole2D**: any | any
- **Hole3D**: {polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc]}
- **Holes2D**: [Hole2D]
- **Holes3D**: [Hole3D]
- **Hotlink**: {location: string, ?hotlinkNodeId: HotlinkNodeId, ?name: string, ?type: HotlinkType, ?children: Hotlinks}
- **HotlinkDetails**: {hotlinkType: HotlinkType, hotlinkNodeId: HotlinkNodeId, origin: Coordinate3D, rotationAngle: float, mirrored: bool, ?floorDifference: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool}
- **HotlinkInstanceChange**: {elementId: ElementId, ?origin: HotlinkOrigin, ?rotationAngle: float, ?mirrored: bool, ?floorDifference: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool, ?layerIndex: int}
- **HotlinkInstanceCreation**: {hotlinkNodeId: HotlinkNodeId, origin: HotlinkOrigin, ?rotationAngle: float, ?mirrored: bool, ?floorIndex: int, ?floorDifference: int, ?layerIndex: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool}
- **HotlinkNodeCreated**: {hotlinkNodeId: HotlinkNodeId, existing: bool}
- **HotlinkNodeCreatedOrError**: HotlinkNodeCreated | ErrorItem
- **HotlinkNodeId**: {guid: Guid}
- **HotlinkOrigin**: {x: float, y: float, ?z: float}
- **HotlinkType**: "Module"|"XRef"
- **Hotlinks**: [Hotlink]
- **HotspotDetails**: {position: Coordinate2D, height: float, ?penIndex: int}
- **HotspotSettings**: {?position: Coordinate2D, ?height: float, ?penIndex: int}
- **IFCElementsToExport**: "EntireProject"|"VisibleElementsOnAllStories"|"AllElementsOnCurrentStory"|"VisibleElementsOnCurrentStory"|"SelectedElementsOnly"
- **IFCExportTranslator**: {name: string, preview: bool}
- **InteriorElevationData**: {nodeCoordinates: [Coordinate2D], ?depth: float, ?name: string, ?id: string, ?floorIndex: int}
- **IssueCommentStatus**: "Error"|"Warning"|"Info"|"Unknown"
- **IssueElementType**: "Creation"|"Highlight"|"Deletion"|"Modification"
- **IssueId**: {guid: Guid}
- **IssueIdArrayItem**: {issueId: IssueId}
- **Issues**: [IssueIdArrayItem]
- **Justification**: "Left"|"Center"|"Right"|"Full"
- **KeynoteAutoTextTokens**: {keyToken: string, titleToken: string, descriptionToken: string, referenceToken: string}
- **KeynoteAutoTextTokensOrError**: KeynoteAutoTextTokens | ErrorItem
- **KeynoteAutoTextTokensOrErrors**: [KeynoteAutoTextTokensOrError]
- **KeynoteFolderDetails**: {keynoteFolderId: KeynoteFolderId, key: string, title: string, reference: string, uiText: string, subFolders: [KeynoteFolderDetails], items: [KeynoteItemDetails]}
- **KeynoteFolderId**: {guid: Guid}
- **KeynoteFolderIdArrayItem**: {keynoteFolderId: KeynoteFolderId}
- **KeynoteFolderIdOrError**: KeynoteFolderIdArrayItem | ErrorItem
- **KeynoteFolderIdsOrErrors**: [KeynoteFolderIdOrError]
- **KeynoteItemDetails**: {keynoteItemId: KeynoteItemId, key: string, title: string, description: string, reference: string, uiText: string}
- **KeynoteItemId**: {guid: Guid}
- **KeynoteItemIdArrayItem**: {keynoteItemId: KeynoteItemId}
- **KeynoteItemIdOrError**: KeynoteItemIdArrayItem | ErrorItem
- **KeynoteItemIdsOrErrors**: [KeynoteItemIdOrError]
- **LabelArrowType**: "EmptyCircle"|"CrossCircle"|"FullCircle"|"SlashLine15"|"OpenArrow15"|"ClosedArrow15"|"FullArrow15"|"SlashLine30"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"OpenArrow45"|"ClosedArrow45"|"FullArrow45"|"SlashLine60"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine90"|"PepitaCircle"|"BandArrow"|"HalfArrowCcw15"|"HalfArrowCw15"|"HalfArrowCcw30"|"HalfArrowCw30"|"HalfArrowCcw45"|"HalfArrowCw45"|"HalfArrowCcw60"|"HalfArrowCw60"|"SlashLine75"
- **LabelClass**: "Text"|"Symbol"
- **LabelDetails**: {?libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, begCoordinate: Coordinate2D, midCoordinate: Coordinate2D, endCoordinate: Coordinate2D, hasLeaderLine: bool, labelClass: LabelClass, leaderLine: LabelLeaderLineDetails, ?style: TextStyleDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?text: string, ?paragraphCount: int, ?runs: [TextRunDetails]}
- **LabelLeaderLineAnchorPoint**: "Middle"|"Top"|"Bottom"|"Underlined"
- **LabelLeaderLineDetails**: {?penIndex: int, ?lineTypeId: AttributeId, ?contourOffset: float, ?framed: bool, ?hasLeaderLine: bool, ?anchorPoint: LabelLeaderLineAnchorPoint, ?leaderShape: "Segmented"|"Splinear"|"SquareRoot", ?squareRootAngle: float, ?arrowType: LabelArrowType, ?arrowVisible: bool, ?arrowPenIndex: int, ?arrowSize: float, ?hideWithBaseElem: bool, ?begCoordinate: Coordinate2D, ?midCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D}
- **LabelLeaderLineSettableDetails**: {?penIndex: int, ?lineTypeId: AttributeId, ?contourOffset: float, ?framed: bool, ?hasLeaderLine: bool, ?anchorPoint: LabelLeaderLineAnchorPoint, ?leaderShape: "Segmented"|"Splinear"|"SquareRoot", ?squareRootAngle: float, ?arrowType: LabelArrowType, ?arrowVisible: bool, ?arrowPenIndex: int, ?arrowSize: float, ?hideWithBaseElem: bool}
- **LabelSymbolStyleSettableDetails**: {?textWay: SymbolLabelTextDirection, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?flipEnabled: bool, ?nonBreaking: bool, ?textSize: float, ?useBackgroundFill: bool, ?backgroundFillPenIndex: int, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool}
- **LayerAttribute**: {attributeId: AttributeId, index: int, name: string, ?isHidden: bool, ?isLocked: bool, ?isWireframe: bool, ?intersectionGroupNr: int}
- **LayerAttributeField**: "isHidden"|"isLocked"|"isWireframe"|"intersectionGroupNr"
- **LayerAttributeOrError**: LayerAttribute | ErrorItem
- **LayerCombinationAttribute**: {layerCombination: LayerCombinationAttributeDetails}
- **LayerCombinationAttributeDetails**: {attributeId: AttributeId, ?attributeIndex: int, name: string, layers: LayersOfLayerCombination}
- **LayerCombinationAttributeOrError**: LayerCombinationAttribute | ErrorItem
- **LayersOfLayerCombination**: [{attributeId: AttributeId, isHidden: bool, isLocked: bool, isWireframe: bool, intersectionGroupNr: int}]
- **LayoutCustomData**: {customSchemeKey: string, ?customSchemeName: string, customSchemeValue: string}
- **LayoutCustomDataToSet**: {?customSchemeKey: string, ?customSchemeName: string, customSchemeValue: string}
- **LayoutInfo**: {id: string, databaseId: DatabaseId, name: string, masterLayoutName: string, width: float, height: float, subsetId: string, subsetName: string, ownerUser: string, ?customSchemeData: RevisionCustomSchemeData}
- **LengthType**: "Meter"|"Decimeter"|"Centimeter"|"Millimeter"|"FootFracInch"|"FootDecInch"|"DecFoot"|"FracInch"|"DecInch"
- **LevelDimensionDetails**: {position: Coordinate2D, level: float, staticLevel: bool, ?ownerElementId: ElementId, ?ownerElementType: ElementType, dimForm: int, needPlus: bool, pen: int, textHeight: float, textPen: int, markerSize: float, angle: float, origin: DimensionOrigin}
- **LibPartBasedElementDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType}
- **LibPartDetails**: {name: string, parentUnID: LibPartUnId, ownUnID: LibPartUnId}
- **LibPartUnId**: {guid: Guid}
- **Library**: {name: string, path: string, type: string, ?available: bool, ?readOnly: bool, ?twServerUrl: string, ?urlWebLibrary: string}
- **LibraryFileAddition**: {inputPath: string, outputPath: string, ?type: LibraryPartType}
- **LibraryFileAdditions**: [LibraryFileAddition]
- **LibraryLocation**: {path: string}
- **LibraryPartType**: "Spec"|"Window"|"Door"|"Object"|"Lamp"|"Room"|"Property"|"PlanSign"|"Label"|"Macro"|"Pict"|"Picture"|"ListScheme"|"Skylight"|"OpeningSymbol"|"Unknown"
- **LineAttribute**: {attributeId: AttributeId, index: int, name: string, ?scaleWithPlan: bool, ?defineScale: float, ?lineType: "Solid"|"Dashed"|"Symbol", ?period: float, ?height: float, ?dashItems: [LineDashItem], ?lineItems: [LineSymbolItem]}
- **LineAttributeField**: "scaleWithPlan"|"defineScale"|"lineType"|"period"|"height"|"dashItems"|"lineItems"
- **LineAttributeOrError**: LineAttribute | ErrorItem
- **LineDashItem**: {dash: float, gap: float}
- **LineDetails**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **LineSettings**: {?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **LineSymbolItem**: {itemType: string, centerOffset: float, length: float, begPos: Coordinate2D, endPos: Coordinate2D, radius: float, beginAngle: float, endAngle: float}
- **LineSymbolItemData**: {itemType: string, ?centerOffset: float, ?length: float, ?begPos: Coordinate2D, ?endPos: Coordinate2D, ?radius: float, ?beginAngle: float, ?endAngle: float}
- **LinkToSettings**: {?homeStoryDifference: int, ?newCreationMode: bool}
- **MEPAngleSet**: {name: string, angles: [float]}
- **MEPBranchPreferenceTable**: {guid: string, name: string, rows: [{mainAxisReferenceId: int, branchAxisReferenceId: int, ?branchAxisAngle: float, mainAxisDiameter: float, branchAxisDiameter: float, length: float, branchOffset: float, connectionLength: float, ?description: string}]}
- **MEPComponentType**: "Terminal"|"Accessory"|"Equipment"|"Fitting"
- **MEPConnectionResult**: {?deletedRoutingElementId: ElementId, ?splitRoutingElementId: ElementId, ?createdBranchId: ElementId}
- **MEPConnectionResultOrError**: MEPConnectionResult | ErrorItem
- **MEPConnectionResultsOrErrors**: [MEPConnectionResultOrError]
- **MEPCrossSectionShape**: "Rectangular"|"Circular"|"Oval"|"UShape"
- **MEPDistributionSystem**: {domain: MEPDomainOrUnknown, ?mepSystemId: AttributeId, elements: Elements}
- **MEPDomain**: "Ventilation"|"Piping"|"CableCarrier"
- **MEPDomainOrUnknown**: "Ventilation"|"Piping"|"CableCarrier"|"Unknown"
- **MEPElbowPreferenceTable**: {guid: string, name: string, rows: [{referenceId: int, ?angle: float, diameter: float, radius: float, ?description: string}]}
- **MEPElement**: {elementId: ElementId, type: MEPElementType, domain: string}
- **MEPElementPorts**: {ports: [MEPPortDetails]}
- **MEPElementPortsOrError**: MEPElementPorts | ErrorItem
- **MEPElementPortsOrErrors**: [MEPElementPortsOrError]
- **MEPElementType**: "RoutingElement"|"RigidSegment"|"Elbow"|"Transition"|"Branch"|"Terminal"|"Accessory"|"Equipment"|"Fitting"|"FlexibleSegment"|"TakeOff"|"ElectricalPanel"|"ElectricalDevice"
- **MEPOrientation**: {direction: Coordinate3D, rotation: Coordinate3D}
- **MEPPhysicalSystemDetails**: {physicalSystemId: MEPPhysicalSystemId, name: string, ?rootElementId: ElementId, ?mepSystemId: AttributeId}
- **MEPPhysicalSystemDetailsOrError**: MEPPhysicalSystemDetails | ErrorItem
- **MEPPhysicalSystemId**: {guid: Guid}
- **MEPPhysicalSystemIdOrError**: {physicalSystemId: MEPPhysicalSystemId} | ErrorItem
- **MEPPortDetails**: {portId: Guid, name: string, position: Coordinate3D, direction: Coordinate3D, shape: string, width: float, height: float, domain: MEPDomainOrUnknown, mepSystemId: AttributeId, isPhysicallyConnected: bool, ?connectedPortId: Guid, ?connectedElementId: ElementId}
- **MEPPreferenceRow**: {referenceId: int, diameter: float, ?description: string}
- **MEPPreferenceTable**: {guid: string, rows: [MEPPreferenceRow]}
- **MEPPreferenceTableDomain**: "Piping"|"Ventilation"
- **MEPReferenceSet**: {name: string, referenceIds: [int]}
- **MEPRoutingElementDetails**: {domain: MEPDomainOrUnknown, mepSystemId: AttributeId, polyline: [Coordinate3D], segments: [MEPRoutingSegmentDetails], nodes: [MEPRoutingNodeDetails]}
- **MEPRoutingElementDetailsOrError**: MEPRoutingElementDetails | ErrorItem
- **MEPRoutingElementDetailsOrErrors**: [MEPRoutingElementDetailsOrError]
- **MEPRoutingNodeDetails**: {elementId: ElementId, position: Coordinate3D}
- **MEPRoutingSegmentDetails**: {elementId: ElementId, crossSectionWidth: float, crossSectionHeight: float, crossSectionShape: string, ?crossSectionReferenceId: int, ?preferenceTableId: Guid}
- **MEPSystemAttribute**: {attributeId: AttributeId, index: int, name: string, ?domain: [MEPDomain], ?contourPen: int, ?fillPen: int, ?fillBackgroundPen: int, ?centerLinePen: int, ?fillId: AttributeIdArrayItem, ?centerLineTypeId: AttributeIdArrayItem, ?materialId: AttributeIdArrayItem, ?insulationMaterialId: AttributeIdArrayItem}
- **MEPSystemAttributeField**: "domain"|"contourPen"|"fillPen"|"fillBackgroundPen"|"centerLinePen"|"fillId"|"centerLineTypeId"|"materialId"|"insulationMaterialId"
- **MEPSystemAttributeOrError**: MEPSystemAttribute | ErrorItem
- **MEPSystemGroupDetails**: {systemGroupId: MEPSystemGroupId, name: string, physicalSystems: [MEPPhysicalSystemDetailsOrError]}
- **MEPSystemGroupDetailsOrError**: MEPSystemGroupDetails | ErrorItem
- **MEPSystemGroupId**: {guid: Guid}
- **MEPSystemGroupIdOrError**: {systemGroupId: MEPSystemGroupId} | ErrorItem
- **MEPTransitionPreferenceTable**: {guid: string, name: string, rows: [{beginReferenceId: int, endReferenceId: int, beginDiameter: float, endDiameter: float, ?length: float, ?angle: float, ?description: string}]}
- **ManualZoneGeometry**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D}
- **MeshDetails**: {?floorIndex: int, level: float, skirtType: MeshSkirtType, skirtLevel: float, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [MeshSubline]}
- **MeshModificationData**: {?floorIndex: int, ?level: float, ?skirtType: MeshSkirtType, ?skirtLevel: float, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, ?polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [MeshSubline]}
- **MeshRidges**: "AllSharp"|"AllSmooth"|"UserDefined"
- **MeshSkirtType**: "SurfaceOnlyWithoutSkirt"|"WithSkirt"|"SolidBodyWithSkirt"
- **MeshSubline**: {coordinates: [Coordinate3D]}
- **MorphBody**: {?bodyType: "Solid"|"Surface", ?isClosed: bool, ?edgeDefault: "HardVisible"|"HardHidden"|"SoftHidden", vertices: [Coordinate3D], ?polygons: [MorphPolygon], ?wireEdges: [{vertexIds: [int]}], ?edgeOverrides: [{vertexIds: [int], ?hidden: bool, ?smooth: bool, ?silhouetteOnly: bool}]}
- **MorphDetails**: {origin: Coordinate3D, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?buildingMaterialId: AttributeId, ?surfaceId: AttributeId, body: MorphBody, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float}
- **MorphPolygon**: {vertexIds: [int], ?filled: bool, ?holes: [MorphPolygonHole], ?surfaceId: AttributeId}
- **MorphPolygonHole**: {vertexIds: [int]}
- **MorphQuantities**: {volume: float, surface: float, floorPlanArea: float, floorPlanPerimeter: float, height: float}
- **NavigatorItem**: {navigatorItemId: NavigatorItemId, type: NavigatorItemType, name: string, prefix: string, uiId: string, customUiId: bool, customName: bool, isIndependent: bool, ?sourceNavigatorItemId: NavigatorItemId, ?children: [NavigatorItemArrayItem]}
- **NavigatorItemArrayItem**: {navigatorItem: NavigatorItem}
- **NavigatorItemId**: {guid: Guid}
- **NavigatorItemIdArrayItem**: {navigatorItemId: NavigatorItemId}
- **NavigatorItemIdOrDatabaseIdAndWindowType**: NavigatorItemIdArrayItem | DatabaseIdAndWindowType
- **NavigatorItemIdOrError**: NavigatorItemIdArrayItem | ErrorItem
- **NavigatorItemIds**: [NavigatorItemIdArrayItem]
- **NavigatorItemType**: "UndefinedItem"|"ProjectItem"|"StoryItem"|"SectionItem"|"DetailDrawingItem"|"PerspectiveItem"|"AxonometryItem"|"ListItem"|"ScheduleItem"|"TocItem"|"CameraItem"|"CameraSetItem"|"InfoItem"|"HelpItem"|"LayoutItem"|"MasterLayoutItem"|"BookItem"|"MasterFolderItem"|"SubSetItem"|"TextListItem"|"ElevationItem"|"InteriorElevationItem"|"WorksheetDrawingItem"|"DocumentFrom3DItem"|"FolderItem"|"DrawingItem"|"UnknownItem"
- **NewClassificationItems**: [{classificationSystemId: ClassificationSystemId, classificationItemDetails: ClassificationItemDetails, ?parentClassificationItemId: ClassificationItemId, ?nextClassificationItemId: ClassificationItemId}]
- **NonLocalizedValueEnumId**: {type: "nonLocalizedValue", nonLocalizedValue: string}
- **NormalAngleListPropertyValue**: {type: "angleList", status: "normal", value: [float]}
- **NormalAnglePropertyValue**: {type: "angle", status: "normal", value: float}
- **NormalAreaListPropertyValue**: {type: "areaList", status: "normal", value: [float]}
- **NormalAreaPropertyValue**: {type: "area", status: "normal", value: float}
- **NormalBooleanListPropertyValue**: {type: "booleanList", status: "normal", value: [bool]}
- **NormalBooleanPropertyValue**: {type: "boolean", status: "normal", value: bool}
- **NormalIntegerListPropertyValue**: {type: "integerList", status: "normal", value: [int]}
- **NormalIntegerPropertyValue**: {type: "integer", status: "normal", value: int}
- **NormalLengthListPropertyValue**: {type: "lengthList", status: "normal", value: [float]}
- **NormalLengthPropertyValue**: {type: "length", status: "normal", value: float}
- **NormalMultiEnumPropertyValue**: {type: "multiEnum", status: "normal", value: EnumValueIds}
- **NormalNumberListPropertyValue**: {type: "numberList", status: "normal", value: [float]}
- **NormalNumberPropertyValue**: {type: "number", status: "normal", value: float}
- **NormalOrUserUndefinedPropertyValue**: NormalNumberPropertyValue | NormalIntegerPropertyValue | NormalStringPropertyValue | NormalBooleanPropertyValue | NormalLengthPropertyValue | NormalAreaPropertyValue | NormalVolumePropertyValue | NormalAnglePropertyValue | NormalNumberListPropertyValue | NormalIntegerListPropertyValue | NormalStringListPropertyValue | NormalBooleanListPropertyValue | NormalLengthListPropertyValue | NormalAreaListPropertyValue | NormalVolumeListPropertyValue | NormalAngleListPropertyValue | NormalSingleEnumPropertyValue | NormalMultiEnumPropertyValue | UserUndefinedPropertyValue
- **NormalSingleEnumPropertyValue**: {type: "singleEnum", status: "normal", value: EnumValueId}
- **NormalStringListPropertyValue**: {type: "stringList", status: "normal", value: [string]}
- **NormalStringPropertyValue**: {type: "string", status: "normal", value: string}
- **NormalVolumeListPropertyValue**: {type: "volumeList", status: "normal", value: [float]}
- **NormalVolumePropertyValue**: {type: "volume", status: "normal", value: float}
- **NotAvailablePropertyValue**: {type: PropertyDataType, status: "notAvailable"}
- **NotYetSupportedElementTypeDetails**: {error: string}
- **ObjectDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, origin: Coordinate3D, dimensions: Coordinate3D, angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?lightColor: ColorRGB, ?lightIsOn: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings}
- **OpeningRelationsOfElement**: {openingRelations: {?fromRoom: ElementId, ?toRoom: ElementId}}
- **OverriddenMaterial**: {overridden: bool, ?attributeId: AttributeId}
- **OverriddenPen**: {overridden: bool, ?penIndex: int}
- **PenData**: {index: int, ?color: ColorRGB, ?width: float, ?description: string}
- **PenTableAttribute**: {attributeId: AttributeId, index: int, name: string, ?isActiveForModel: bool, ?isActiveForLayout: bool, ?pens: [PenTablePen]}
- **PenTableAttributeField**: "isActiveForModel"|"isActiveForLayout"|"pens"
- **PenTableAttributeOrError**: PenTableAttribute | ErrorItem
- **PenTablePen**: {index: int, color: ColorRGB, width: float, description: string}
- **PerspectiveProjectionParameters**: {cameraPosition: Coordinate3D, targetPosition: Coordinate3D, distance: float, azimuth: float, viewCone: float, rollAngle: float, isTwoPointPersp: bool}
- **PolyArc**: {begIndex: int, endIndex: int, arcAngle: float}
- **PolylineDetails**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **PolylineSettings**: {?coordinates: [Coordinate2D], ?arcs: [PolyArc], ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **PossibleEnumValues**: [{enumValue: EnumValue}]
- **PossibleNumericValues**: [{?value: float, ?flag: string, ?stepBegin: float, ?stepValue: float, ?description: string}]
- **PossibleStringValues**: [string]
- **ProfileAttribute**: {attributeId: AttributeId, index: int, name: string, ?wallType: bool, ?beamType: bool, ?coluType: bool, ?handrailType: bool, ?otherGDLObjectType: bool, ?useWith: [ProfileUseWith], ?width: float, ?height: float, ?minimumWidth: float, ?minimumHeight: float, ?widthStretchable: bool, ?heightStretchable: bool, ?hasCoreSkin: bool, ?profileModifiers: [ProfileModifier], ?skins: [ProfileSkin]}
- **ProfileAttributeField**: "wallType"|"beamType"|"coluType"|"handrailType"|"otherGDLObjectType"|"useWith"|"width"|"height"|"minimumWidth"|"minimumHeight"|"widthStretchable"|"heightStretchable"|"hasCoreSkin"|"profileModifiers"|"skins"|"skinOutlines"
- **ProfileAttributeOrError**: ProfileAttribute | ErrorItem
- **ProfileEdge**: {?buildingMaterialId: AttributeIdArrayItem, ?pen: int, ?lineTypeId: AttributeIdArrayItem, ?isVisibleLine: bool, ?isCutEndLine: bool, ?isInnerLine: bool}
- **ProfileEdgeOverride**: {edgeIndex: int, ?pen: int, ?isVisibleLine: bool, ?lineTypeId: AttributeIdArrayItem, ?buildingMaterialId: AttributeIdArrayItem}
- **ProfileModifier**: {?name: string, ?value: float}
- **ProfileSkin**: {?skinId: string, ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edges: [ProfileEdge], ?outlineCoords: [Coordinate2D], ?outlineSubPolyEnds: [int], ?outlineArcs: [{begIndex: int, endIndex: int, arcAngle: float}]}
- **ProfileSkinContour**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc]}
- **ProfileSkinData**: {contours: [ProfileSkinContour], ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edgeOverrides: [ProfileEdgeOverride]}
- **ProfileUseWith**: "Wall"|"Beam"|"Column"|"Handrail"|"Other"
- **ProjectInfoField**: {projectInfoId: string, projectInfoName: string, projectInfoValue: string}
- **ProjectInfoFieldData**: {projectInfoName: string, ?projectInfoValue: string}
- **ProjectInfoFields**: [ProjectInfoField]
- **ProjectLocation**: {longitude: float, latitude: float, altitude: float, north: float}
- **ProjectLocationUpdate**: {?longitude: float, ?latitude: float, ?altitude: float, ?north: float}
- **PropertyAvailabilityUpdate**: {?set: [ClassificationItemIdArrayItem], ?add: [ClassificationItemIdArrayItem], ?remove: [ClassificationItemIdArrayItem]}
- **PropertyDataType**: "number"|"integer"|"string"|"boolean"|"length"|"area"|"volume"|"angle"|"numberList"|"integerList"|"stringList"|"booleanList"|"lengthList"|"areaList"|"volumeList"|"angleList"|"singleEnum"|"multiEnum"
- **PropertyDefaultValue**: BasicDefaultValue | ExpressionDefaultValue
- **PropertyDefinition**: {name: string, description: string, type: PropertyDataType, isEditable: bool, ?defaultValue: PropertyDefaultValue, ?possibleEnumValues: PossibleEnumValues, availability: [ClassificationItemIdArrayItem], group: {?propertyGroupId: PropertyGroupId, ?name: string}}
- **PropertyDefinitionArrayItem**: {propertyDefinition: PropertyDefinition}
- **PropertyDefinitionUpdate**: {propertyId: PropertyId, ?name: string, ?description: string, ?groupId: PropertyGroupId, ?defaultValue: PropertyDefaultValue, ?expressions: [string], ?availability: PropertyAvailabilityUpdate, ?possibleEnumValues: EnumValuesToAdd, ?renameEnumValues: [PropertyEnumValueRename], ?removeEnumValues: [PropertyEnumValueRemoval], ?enumOrder: [string]}
- **PropertyDetails**: {?possibleEnumValues: PossibleEnumValues, propertyId: PropertyId, propertyType: "StaticBuiltIn"|"DynamicBuiltIn"|"Custom", propertyGroupName: string, propertyName: string, propertyCollectionType: "Undefined"|"Single"|"List"|"SingleChoiceEnumeration"|"MultipleChoiceEnumeration", propertyValueType: "Undefined"|"Integer"|"Real"|"String"|"Boolean"|"Guid", propertyMeasureType: "Undefined"|"Default"|"Length"|"Area"|"Volume"|"Angle", propertyIsEditable: bool, isExpressionBased: bool, ?expressions: [string], ?propertyGroupId: PropertyGroupId, ?propertyDescription: string, ?defaultValueDisplay: string, ?availability: [ClassificationItemIdArrayItem], ?defaultEnumValueIds: [GuidId]}
- **PropertyEnumValueRemoval**: {enumValueId: GuidId}
- **PropertyEnumValueRename**: {enumValueId: GuidId, displayValue: string, ?nonLocalizedValue: string}
- **PropertyGroup**: {name: string, ?description: string}
- **PropertyGroupArrayItem**: {propertyGroup: PropertyGroup}
- **PropertyGroupDetails**: {propertyGroupId: PropertyGroupId, name: string, ?description: string, isCustom: bool}
- **PropertyGroupId**: {guid: Guid}
- **PropertyGroupIdArrayItem**: {propertyGroupId: PropertyGroupId}
- **PropertyGroupUpdate**: {propertyGroupId: PropertyGroupId, ?name: string, ?description: string}
- **PropertyId**: {guid: Guid}
- **PropertyIdArrayItem**: {propertyId: PropertyId}
- **PropertyIdOrError**: PropertyIdArrayItem | ErrorItem
- **PropertyIdOrErrorArray**: [PropertyIdOrError]
- **PropertyIds**: [PropertyIdArrayItem]
- **PropertyImportConflictPolicy**: "append"|"replace"|"skip"
- **PropertyValue**: {value: string}
- **PropertyValueArrayItem**: {propertyValue: PropertyValue}
- **PropertyValueDetails**: NormalOrUserUndefinedPropertyValue | NotAvailablePropertyValue
- **PropertyValueOrErrorItem**: PropertyValueArrayItem | ErrorItem
- **PropertyValues**: [PropertyValueOrErrorItem]
- **PropertyValuesArrayItem**: {propertyValues: PropertyValues}
- **PropertyValuesOrError**: PropertyValuesArrayItem | ErrorItem
- **PropertyValuesOrErrorArray**: [PropertyValuesOrError]
- **RevisionChange**: {id: string, description: string, lastModifiedTime: string, modifiedByUser: string, isIssued: bool, ?firstRevisionIssueId: RevisionIssueId, isArchived: bool, ?customSchemeData: RevisionCustomSchemeData}
- **RevisionChangesArrayItem**: {?revisionChanges: [RevisionChange]}
- **RevisionChangesOfEntities**: RevisionChangesArrayItem | ErrorItem
- **RevisionCustomSchemeData**: [RevisionCustomSchemeEntry]
- **RevisionCustomSchemeEntry**: {customSchemeKey: Guid, customSchemeValue: string}
- **RevisionIssue**: {revisionIssueId: RevisionIssueId, id: string, description: string, issueTime: string, issuedByUser: string, overrideRevisionIDOfAllIncludedLayouts: bool, createNewRevisionInAllIncludedLayouts: bool, ?markersVisibleSinceIndex: int, isIssued: bool, ?documentRevisions: DocumentRevisionReferences, ?customSchemeData: RevisionCustomSchemeData}
- **RevisionIssueId**: {guid: Guid}
- **RoofDetails**: {roofClass: "SinglePlane"|"MultiPlane", structureType: RoofStructureType, thickness: float, level: float, zCoordinate: float, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?angle: float, ?pivotLine: RoofDetailsPivotLine, ?eavesOverhang: float, ?levels: [RoofDetailsLevel], ?pivotPolygonOutline: [Coordinate2D], polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D}
- **RoofDetailsLevel**: {height: float, angle: float}
- **RoofDetailsPivotLine**: {begin: Coordinate2D, end: Coordinate2D}
- **RoofLevel**: {levelHeight: float, levelAngle: float}
- **RoofOrShellRelationsOfElement**: {roofOrShellRelations: {connectedRooms: Elements}}
- **RoofPivotLine**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D}
- **RoofQuantities**: {volume: float, volumeConditional: float, grossVolume: float, topSurface: float, bottomSurface: float, edgeSurface: float, topSurfaceConditional: float, bottomSurfaceConditional: float, grossTopSurface: float, grossBottomSurface: float, grossEdgeSurface: float, contourArea: float, perimeter: float, holesSurface: float, holesPerimeter: float, openingsSurface: float, ridgesLength: float, valleysLength: float, hipsLength: float, gablesLength: float, eavesLength: float, peaksLength: float}
- **RoofStructureType**: "Basic"|"Composite"
- **SetGDLParameterArray**: [SetGDLParameterDetails]
- **SetGDLParameterByIndexDetails**: {index: int, ?index1: int, ?index2: int, value: any}
- **SetGDLParameterByNameDetails**: {name: string, ?index1: int, ?index2: int, value: any}
- **SetGDLParameterDetails**: SetGDLParameterByNameDetails | SetGDLParameterByIndexDetails
- **ShellQuantities**: {volume: float, volumeConditional: float, grossVolume: float, referenceSurface: float, oppositeSurface: float, edgeSurface: float, referenceSurfaceConditional: float, oppositeSurfaceConditional: float, grossReferenceSurface: float, grossOppositeSurface: float, grossEdgeSurface: float, perimeter: float, holesSurface: float, holesPerimeter: float, floorPlanArea: float}
- **SlabDetails**: {thickness: float, level: float, offsetFromTop: float, zCoordinate: float, polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], holes: Holes2D, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?floorFill: FloorFill}
- **SlabQuantities**: {volume: float, volumeConditional: float, grossVolume: float, topSurface: float, bottomSurface: float, edgeSurface: float, topSurfaceConditional: float, bottomSurfaceConditional: float, grossTopSurface: float, grossBottomSurface: float, grossEdgeSurface: float, perimeter: float, holesSurface: float, holesPerimeter: float}
- **SlabReferencePlaneLocation**: "Top"|"CoreTop"|"CoreBottom"|"Bottom"
- **SlabStructureType**: "Basic"|"Composite"
- **SolidLinkData**: {targetId: ElementId, operatorId: ElementId, operation: SolidOperationType, ?linkFlags: SolidLinkFlags}
- **SolidLinkFlags**: {inheritOperatorAttributes: bool, skipPolygonHoles: bool}
- **SolidLinkReference**: {targetId: ElementId, operatorId: ElementId}
- **SolidLinksOfElement**: {solidLinksWithTheGivenTarget: [{operatorId: ElementId, operation: SolidOperationType, linkFlags: SolidLinkFlags}], solidLinksWithTheGivenOperator: [{targetId: ElementId, operation: SolidOperationType, linkFlags: SolidLinkFlags}]}
- **SolidOperationType**: "Subtraction"|"SubtractionUpwards"|"SubtractionDownwards"|"Intersection"|"Addition"
- **SpecialFolderPath**: {path: string}
- **SpecialFolderPathOrError**: SpecialFolderPath | ErrorItem
- **SpecialFolderPathsOrErrors**: [SpecialFolderPathOrError]
- **SpecialFolderType**: "ApplicationPrefs"|"GraphisoftPrefs"|"GraphisoftHome"|"Cache"|"Data"|"UserDocuments"|"Temporary"|"Application"|"Defaults"|"WebObjects"|"Templates"|"Help"|"EmbeddedProjectLibrary"|"EmbeddedProjectLibraryHotlink"|"ProjectPreviews"
- **SplineDetails**: {coordinates: [Coordinate2D], closed: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **SplineSettings**: {?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **StoriesParameters**: [StoryParameters]
- **StoriesSettings**: [StorySettings]
- **StoryParameters**: {index: int, floorId: int, dispOnSections: bool, level: float, ?height: float, name: string, ?ifcId: string}
- **StorySettings**: {?index: int, dispOnSections: bool, level: float, name: string}
- **StoryVisibility**: {?showOnHome: bool, ?showAllAbove: bool, ?showAllBelow: bool, ?showRelAbove: int, ?showRelBelow: int}
- **SuccessfulExecutionResult**: {success: true}
- **SurfaceAttribute**: {attributeId: AttributeId, index: int, name: string, ?materialType: SurfaceType, ?ambientReflection: float, ?diffuseReflection: float, ?specularReflection: float, ?transparency: float, ?shine: float, ?transparencyAttenuation: float, ?emissionAttenuation: float, ?surfaceColor: ColorRGB, ?specularColor: ColorRGB, ?emissionColor: ColorRGB, ?fillId: AttributeIdArrayItem, ?texture: Texture}
- **SurfaceAttributeField**: "materialType"|"ambientReflection"|"diffuseReflection"|"specularReflection"|"transparency"|"shine"|"transparencyAttenuation"|"emissionAttenuation"|"surfaceColor"|"specularColor"|"emissionColor"|"fillId"|"texture"
- **SurfaceAttributeOrError**: SurfaceAttribute | ErrorItem
- **SurfaceType**: "General"|"Simple"|"Matte"|"Metal"|"Plastic"|"Glass"|"Glowing"|"Constant"
- **SurveyPoint**: {position: SurveyPointPosition, positionInProject: Coordinate3D, geoReferencingParameters: GeoReferencingParameters}
- **SurveyPointPosition**: {eastings: float, northings: float, elevation: float}
- **SurveyPointPositionUpdate**: {?eastings: float, ?northings: float, ?elevation: float}
- **SurveyPointUpdate**: {?position: SurveyPointPositionUpdate, ?positionInProject: Coordinate3D, ?geoReferencingParameters: GeoReferencingParametersUpdate}
- **SymbolLabelTextDirection**: "Parallel"|"Horizontal"|"Vertical"|"General"
- **TextBoxAnchor**: "LeftTop"|"MiddleTop"|"RightTop"|"LeftMiddle"|"MiddleMiddle"|"RightMiddle"|"LeftBottom"|"MiddleBottom"|"RightBottom"
- **TextDetails**: {text: string, position: Coordinate2D, angle: float, height: float, pen: int, justification: Justification, zCoordinate: float, style: TextStyleDetails, paragraphCount: int, ?runs: [TextRunDetails]}
- **TextRunDetails**: {text: string, ?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?heightOverride: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool}
- **TextSettings**: {?text: string, ?position: Coordinate2D, ?angle: float, ?height: float, ?justification: Justification}
- **TextStyleDetails**: {?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?justification: Justification, ?height: float, ?spacing: float, ?angle: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool, ?widthFactor: float, ?charSpaceFactor: float, ?fixedSize: bool, ?usedContour: bool, ?usedFill: bool, ?contourPenIndex: int, ?fillPenIndex: int, ?anchor: TextBoxAnchor, ?fixedAngle: bool, ?contourOffset: float, ?flipEnabled: bool, ?textFrameShape: "Rectangle"|"Circle"|"RoundedRectangle"|"Pill", ?textFrameSizeFixed: bool, ?textFrameFixedWidth: float, ?textFrameFixedHeight: float, ?lineCount: int, ?boxWidth: float, ?boxHeight: float}
- **TextStyleSettableDetails**: {?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?justification: Justification, ?height: float, ?spacing: float, ?angle: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool, ?widthFactor: float, ?charSpaceFactor: float, ?fixedSize: bool, ?usedContour: bool, ?usedFill: bool, ?contourPenIndex: int, ?fillPenIndex: int, ?anchor: TextBoxAnchor, ?fixedAngle: bool, ?contourOffset: float, ?flipEnabled: bool, ?textFrameShape: "Rectangle"|"Circle"|"RoundedRectangle"|"Pill", ?textFrameSizeFixed: bool, ?textFrameFixedWidth: float, ?textFrameFixedHeight: float}
- **Texture**: {name: string, ?rotationAngle: float, ?xSize: float, ?ySize: float, ?FillRectangle: bool, ?FitPicture: bool, ?mirrorX: bool, ?mirrorY: bool, ?useAlphaChannel: bool, ?alphaChannelChangesTransparency: bool, ?alphaChannelChangesSurfaceColor: bool, ?alphaChannelChangesAmbientColor: bool, ?alphaChannelChangesSpecularColor: bool, ?alphaChannelChangesDiffuseColor: bool}
- **TextureProjectionType**: "Invalid"|"Planar"|"Default"|"Cylindric"|"Spheric"|"Box"
- **TrimType**: "KeepInside"|"KeepOutside"|"KeepAll"|"No"
- **TypeSpecificDetails**: HotlinkDetails | WallDetails | BeamDetails | SlabDetails | RoofDetails | ColumnDetails | DetailWorksheetDetails | WindowDoorDetails | LibPartBasedElementDetails | ObjectDetails | PolylineDetails | ZoneDetails | CurtainWallDetails | CurtainWallSegmentDetails | CurtainWallPanelDetails | CurtainWallFrameDetails | MeshDetails | MorphDetails | DrawingDetails | LabelDetails | TextDetails | LevelDimensionDetails | NotYetSupportedElementTypeDetails
- **TypeSpecificSettings**: WallSettings | ZoneSettings | LineSettings | ArcSettings | HotspotSettings | SplineSettings | PolylineSettings | HatchSettings | DrawingSettings | TextSettings
- **User**: {userId: float, userName: string}
- **UserUndefinedPropertyValue**: {type: PropertyDataType, status: "userUndefined"}
- **ViewDepthLimitation**: "ToFloorPlanRange"|"ToAbsoluteLimit"|"EntireElement"
- **ViewSettings**: {?modelViewOptions: string, ?layerCombination: string, ?dimensionStyle: string, ?penSetName: string, ?graphicOverrideCombination: string, ?drawingScale: int, ?saveZoom: bool, ?ignoreSavedZoom: bool, ?zoom: Zoom, ?rotation: float, ?structureDisplay: "EntireStructure"|"CoreOnly"|"WithoutFinishes"|"StructureOnly", ?renovationFilterGuid: GuidId, ?d3styleName: string, ?renderingSceneName: string, ?usePhotoRendering: bool}
- **ViewSettingsOrError**: ViewSettings | ErrorItem
- **ViewTransformations**: {zoom: Zoom, rotation: float}
- **ViewTransformationsOrError**: ViewTransformations | ErrorItem
- **VolumeType**: "CubicMeter"|"Liter"|"CubicCentimeter"|"CubicMillimeter"|"CubicFoot"|"CubicInch"|"CubicYard"|"Gallon"
- **WallDetails**: {geometryType: WallGeometryType, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, zCoordinate: float, ?flipped: bool, height: float, bottomOffset: float, offset: float, ?arcAngle: float, ?begThickness: float, ?endThickness: float, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?structureType: WallStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?referenceLineLocation: WallReferenceLineLocation, ?profileType: WallProfileType, ?slantAlpha: float, ?slantBeta: float, ?topOffset: float, ?relativeTopStory: float, ?zoneRel: WallZoneRelation, ?visibility: StoryVisibility, ?isAutoOnStoryVisibility: bool, ?referenceMaterial: OverriddenMaterial, ?oppositeMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?contourPen: int, ?contourPen3D: int, ?contourLineTypeId: AttributeId, ?belowViewLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?connectionPriority: int, ?useCompositePriority: bool, ?junctionSequence: int, ?linkToSettings: LinkToSettings, ?inheritEndSurface: bool, ?alignTexture: bool, ?offsetFromOutside: float, ?polyCanChange: bool, ?materialsChained: bool, ?logHeight: float, ?hasWindow: bool, ?hasDoor: bool}
- **WallGeometryType**: "Straight"|"Trapezoid"|"Polygonal"
- **WallModificationGeometryType**: "Straight"|"Trapezoid"
- **WallModificationProfileType**: "Normal"|"Slanted"|"Trapez"
- **WallProfileType**: "Normal"|"Slanted"|"Trapez"|"Poly"
- **WallQuantities**: {volume: float, volumeConditional: float, grossVolume: float, referenceSideSurface: float, oppositeSideSurface: float, edgeSurface: float, referenceSideSurfaceConditional: float, oppositeSideSurfaceConditional: float, grossReferenceSideSurface: float, grossOppositeSideSurface: float, length: float, referenceSideLength: float, oppositeSideLength: float, centerLength: float, referenceLineLength: float, minHeight: float, maxHeight: float, area: float, perimeter: float, windowsSurface: float, doorsSurface: float, emptyOpeningsSurface: float, emptyOpeningsVolume: float}
- **WallReferenceLineLocation**: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside"
- **WallRelations**: {wallConnections: EndpointConnections}
- **WallSettings**: {?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?height: float, ?bottomOffset: float, ?offset: float, ?begThickness: float, ?endThickness: float}
- **WallStructureType**: "Basic"|"Composite"|"Profile"
- **WallZoneRelation**: "Boundary"|"ReduceArea"|"None"|"SubtractFromZone"
- **WindowDoorDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, width: float, height: float, sillHeight: float, centerOffset: float, reflected: bool, refSide: bool, oSide: bool}
- **WindowType**: "FloorPlan"|"Section"|"Details"|"3DModel"|"Layout"|"Drawing"|"CustomText"|"CustomDraw"|"MasterLayout"|"Elevation"|"InteriorElevation"|"Worksheet"|"Report"|"3DDocument"|"External3D"|"Movie3D"|"MovieRendering"|"Rendering"|"ModelCompare"|"Interactive Schedule"|"Unknown"
- **ZoneBoundariesOfZonesWrapper**: {zoneBoundariesOfZones: [ZoneBoundariesOrError]}
- **ZoneBoundariesOrError**: ZoneBoundariesWrapper | ErrorItem
- **ZoneBoundariesWrapper**: {zoneBoundaries: [{connectedElementId: ElementId, isExternal: bool, neighbouringZoneElementId: ElementId, area: float, polygonOutline: [Coordinate3D]}]}
- **ZoneBoundaryPart**: {elementId: ElementId, ?roomEdgeIndex: int, begDistance: float, endDistance: float}
- **ZoneCategoryAttribute**: {attributeId: AttributeId, index: int, name: string, ?categoryCode: string, ?color: ColorRGB, ?stampName: string, ?stampMainGuid: string, ?stampRevGuid: string}
- **ZoneCategoryAttributeField**: "categoryCode"|"color"|"stampName"|"stampMainGuid"|"stampRevGuid"
- **ZoneCategoryAttributeOrError**: ZoneCategoryAttribute | ErrorItem
- **ZoneCreationGeometry**: AutomaticZoneGeometry | ManualZoneGeometry
- **ZoneDetails**: {name: string, numberStr: string, categoryAttributeId: AttributeId, stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, isManual: bool, polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, zCoordinate: float}
- **ZoneQuantities**: {area: float, netArea: float, calculatedArea: float, perimeter: float, netPerimeter: float, volume: float, height: float, wallsPerimeter: float, wallsSurface: float, doorsSurface: float, windowsSurface: float}
- **ZoneRelations**: {elementsGroupedByType: [ElementsOfElementType], wallParts: [ZoneBoundaryPart], beamParts: [ZoneBoundaryPart], curtainWallSegmentParts: [ZoneBoundaryPart]}
- **ZoneRelationsOfElement**: {zoneRelations: ZoneRelations}
- **ZoneSettings**: {?stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool}
- **Zoom**: {xMin: float, yMin: float, xMax: float, yMax: float}

## Application Commands

### GetAddOnVersion
# Retrieves the version of the Tapir Additional JSON Commands Add-On. (since 0.1.0)
  → version: string

### GetArchicadLocation
# Retrieves the location of the currently running Archicad executable. (since 0.1.0)
  → archicadLocation: string

### QuitArchicad
# Performs a quit operation on the currently running Archicad instance. (since 0.1.0)
  → ExecutionResult

### GetPointFromUser
# Asks the designer to click a point in the current window and returns it. Archicad waits for the click or for Escape, and every other JSON command queues behind this one until then; the call fails when the input is cancelled. (since 1.5.9)
  ?prompt: string
  → position: Coordinate3D

### GetCurrentWindowType
# Returns the type of the current (active) window. (since 1.0.7)
  → currentWindowType: WindowType

### ChangeWindow
# Changes the current (active) window to the given window. With windowType 'FloorPlan' and a storyIndex it also activates that story on the floor plan. (since 1.3.1)
# storyIndex with windowType 'FloorPlan' switches the active story since 1.7.0 (#752; a silent no-op before). AC25/AC26 reject navigatorItemId.
  NavigatorItemIdOrDatabaseIdAndWindowType
  → ExecutionResult

### GetUserGSID
# Get the current registered User-GSID and OrganizationsID. Requires Archicad 27 or later. (since 1.5.6) [AC27+]
  → userId: string, ?organizationIds: [string]

### ShowAlert
# Display a dialog with up to three buttons. (since 1.5.6)
  alertType: "information"|"warning"|"error", title: string, message: string, ?subMessage: string, button1: string, ?button2: string, ?button3: string
  → clickedButton: int

### GetSpecialFolders
# Retrieves the filesystem paths of the special folders of the running Archicad (preferences, cache, data, temporary, application, defaults, templates, help, embedded project library, etc.). (since 1.5.6)
  folderTypes: [SpecialFolderType]
  → folderPaths: SpecialFolderPathsOrErrors

## Project Commands

### GetProjectInfo
# Retrieves information about the currently loaded project. (since 0.1.0)
  → isUntitled: bool, isTeamwork: bool, ?projectLocation: string, ?projectPath: string, ?projectName: string

### GetProjectInfoFields
# Retrieves the names and values of all project info fields. (since 0.1.2)
  → fields: ProjectInfoFields

### SetProjectInfoField
# Sets the value of a project info field. (since 0.1.2)
  projectInfoId: string, projectInfoValue: string

### CreateProjectInfoFields
# Creates one or more custom project info fields. (since 1.5.2)
  projectInfoFields: [ProjectInfoFieldData]
  → fields: ProjectInfoFields

### DeleteProjectInfoFields
# Deletes one or more custom project info fields. Hardcoded fields cannot be deleted. (since 1.5.4)
  projectInfoIds: [string]
  → executionResults: ExecutionResults

### GetStories
# Retrieves information about the story structure of the currently loaded project: index, floor id, name, level, height and, from Archicad 28, the IFC GlobalId of each story. (since 1.1.5)
  → firstStory: int, lastStory: int, actStory: int, skipNullFloor: bool, stories: StoriesParameters

### SetStories
# Sets the story sructure of the currently loaded project. (since 1.1.5)
  stories: StoriesSettings
  → ExecutionResult

### GetAutoTextKeys
# Retrieves the available autotext keys (name and embeddable key), optionally for a specific element. Embed a key in a Text or Label content by surrounding it with '<' and '>'. (since 1.5.9)
  ?elementId: ElementId
  → autoTextKeys: [{name: string, key: string}]

### GetAutoTextName
# Retrieves the display names of one or more autotext keys (as returned inside a '<...>' embedded key), with a direct guid lookup for property-based keys instead of enumerating every property definition. (since 1.5.9)
  keys: [AutoTextKeyValue]
  → autoTextNames: AutoTextNamesOrErrors

### GetHotlinks
# Gets the file system locations (path) of the hotlink modules. The hotlinks can have tree hierarchy in the project. (since 0.1.0)
  → hotlinks: Hotlinks

### CreateHotlinkNodes
# Creates hotlink module nodes from source files. A node that already points at the same file is returned instead of duplicated (Archicad 26 and later; 25 cannot see an unplaced node). (since 1.5.9) [AC26+]
  hotlinkNodes[]: sourceLocation: string, ?name: string, ?storyRangeType: "AllStories"|"SingleStory", ?refFloorIndex: int
  → hotlinkNodes: [HotlinkNodeCreatedOrError]

### CreateHotlinkInstances
# Places instances of hotlink module nodes at an origin, rotation and mirroring. (since 1.5.9)
  hotlinkInstances: [HotlinkInstanceCreation]
  → elements: ElementIdsOrErrors

### ChangeHotlinkInstances
# Moves, rotates or mirrors placed hotlink instances by changing their transformation. MoveElements and RotateElements do not work on hotlink instances. (since 1.5.9)
  hotlinkInstances: [HotlinkInstanceChange]
  → executionResults: ExecutionResults

### UpdateHotlinks
# Re-reads the source files of hotlink module nodes and refreshes their cached content in the project, as the Hotlink Manager's Update button does. (since 1.7.1)
  hotlinkNodes[]: hotlinkNodeId: HotlinkNodeId
  → executionResults: ExecutionResults

### ChangeHotlinkNodes
# Repoints hotlink module nodes at other source files, as the Hotlink Manager's Relink button does. Follow it with UpdateHotlinks to re-read the content. (since 1.7.1)
  hotlinkNodes[]: hotlinkNodeId: HotlinkNodeId, sourceLocation: string
  → executionResults: ExecutionResults

### OpenProject
# Opens the given project. (since 1.0.7)
  projectFilePath: string
  → ExecutionResult

### CloseProject
# Closes the currently opened project. (since 1.3.1)
  → ExecutionResult

### SaveProject
# Saves the currently opened project. (since 1.3.1)
  ?projectPath: string
  → ExecutionResult

### SaveAsModuleFile
# Saves the given elements, or the current selection, as a hotlink module (.mod) file. (since 1.5.9)
  moduleFilePath: string, ?elements: Elements
  → ExecutionResult

### SaveProjectAsArchive
# Saves the open project as an archive (.pla) file, with the library parts it uses inside. (since 1.6.0)
  archiveFilePath: string, ?includeLibraryParts: bool, ?includeProperties: bool, ?includeTextures: bool, ?includeBackgroundPicture: bool
  → ExecutionResult

### SaveCurrentWindowAsImage
# Saves what the current window shows as an image file (png, jpg, bmp, tiff or gif), as File > Save as does with a picture format. (since 1.7.1)
  imageFilePath: string, ?format: "png"|"jpg"|"bmp"|"tiff"|"gif", ?colorDepth: "blackAndWhite"|"16Colors"|"256Colors"|"16Grays"|"256Grays"|"trueColor"|"trueColorWithAlpha", ?dithered: bool, ?entireDrawing: bool
  → imageFilePath: string, ?zoom: Zoom, ?rotation: float

### GetCalculationUnits
# Gets the project calculation units. (since 1.4.0)
  → length: {unit: LengthType, accuracy: AccuracyType, decimals: int, ?roundInch: int}, area: {unit: AreaType, accuracy: AccuracyType, decimals: int}, volume: {unit: VolumeType, accuracy: AccuracyType, decimals: int}, angle: {unit: AngleType, decimals: int, accuracy: int}

### GetGeoLocation
# Gets the project location details. (since 1.1.6)
  → projectLocation: ProjectLocation, surveyPoint: SurveyPoint

### SetGeoLocation
# Sets the project location details. (since 1.2.9)
  ?projectLocation: ProjectLocationUpdate, ?surveyPoint: SurveyPointUpdate
  → ExecutionResult

### PrintView
# Prints from the current view. (since 1.3.1)
  ?grid: bool, ?fixText: bool, ?scale: int, ?printArea: "currentView"|"entireDrawing"|"marquee"
  → ExecutionResult

### RebuildView
# Rebuilds the current view. (since 1.5.0)
  ?regenerate: bool
  → ExecutionResult

## Element Commands

### GetSelectedElements
# Gets the list of the currently selected elements. (since 0.1.0)
  → elements: Elements

### GetElementsByType
# Returns the identifier of every element of the given type on the plan. It works for any type. Use the optional filter parameter for filtering. (since 1.0.7)
  elementType: ElementType, ?filters: [ElementFilter], ?databases: Databases
  → ElementsWithExecutionResultsOrError

### GetAllElements
# Returns the identifier of all elements on the plan. Use the optional filter parameter for filtering. (since 1.0.7)
  ?filters: [ElementFilter], ?databases: Databases
  → ElementsWithExecutionResultsOrError

### ChangeSelectionOfElements
# Adds/removes a number of elements to/from the current selection. (since 1.0.7)
  ?addElementsToSelection: Elements, ?removeElementsFromSelection: Elements
  → executionResultsOfAddToSelection: ExecutionResults, executionResultsOfRemoveFromSelection: ExecutionResults

### FilterElements
# Tests an elements by the given criterias. (since 1.0.7)
  elements: Elements, ?filters: [ElementFilter]
  → elements: Elements

### GetDetailsOfElements
# Gets the details of the given elements (geometry parameters etc). Use the optional fields parameter to return only the fields you need and skip the computation of the others (for example floorPlanPolygons). (since 1.5.7)
  elements: Elements, ?fields: [ElementDetailsField]
  → detailsOfElements: [{type: ElementType, id: string, floorIndex: float, layerIndex: float, drawIndex: float, ?hotlinkId: ElementId, details: TypeSpecificDetails, ?floorPlanPolygons: [{?coordinates: [Coordinate2D]}]}]

### SetDetailsOfElements
# Sets the details of the given elements (floor, layer, order etc). (since 1.0.7)
  elementsWithDetails[]: elementId: ElementId, details: {?floorIndex: float, ?layerIndex: float, ?drawIndex: float, ?typeSpecificDetails: TypeSpecificSettings}
  → executionResults: ExecutionResults

### Get3DBoundingBoxes
# Get the 3D bounding box of elements. The bounding box is calculated from the global origin in the 3D view. The output is the array of the bounding boxes respective to the input array of elements. (since 1.1.2)
  elements: Elements
  → boundingBoxes3D: BoundingBoxes3D

### Get3DGeometryOfElements
# Gets the 3D geometry of elements as the solid bodies of their 3D model: a vertex list in world coordinates and the planar faces (with their holes) referencing it, each face with its surface attribute when that is a project attribute. The bodies of the subelements of a Stair, Railing or Curtain Wall are included. The output is aligned with the input array of elements. The 3D model of the elements is generated as needed, so many elements can take a while. (since 1.7.2)
  elements: Elements
  → geometries3D: [{bodies: [Body3D]} | ErrorItem]

### GetQuantitiesOfElements
# Gets the quantities of the given elements calculated by Archicad (volumes, surfaces, lengths etc.), together with the volume and projected area per building material (one item per skin of composite and complex profile elements, one item for basic elements). Supported types: Wall, Column, Beam, Slab, Roof, Shell, Morph, Zone, ColumnSegment, BeamSegment. Use the optional minOpeningSize parameter to control the conditional values. (since 1.7.2)
  elements: Elements, ?minOpeningSize: float
  → quantitiesOfElements: [{type: ElementType, quantities: ElementQuantities, composites: [{buildingMaterialId: AttributeIdArrayItem, volume: float, projectedArea: float, isCore: bool, isFinish: bool, ?subElementId: ElementId}]} | ErrorItem]

### GetSubelementsOfHierarchicalElements
# Gets the subelements of the given hierarchical elements. (since 1.0.6)
  elements: Elements
  → subelements: [{?cWallSegments: Elements, ?cWallFrames: Elements, ?cWallPanels: Elements, ?cWallJunctions: Elements, ?cWallAccessories: Elements, ?stairRisers: Elements, ?stairTreads: Elements, ?stairStructures: Elements, ?railingNodes: Elements, ?railingSegments: Elements, ?railingPosts: Elements, ?railingRailEnds: Elements, ?railingRailConnections: Elements, ?railingHandrailEnds: Elements, ?railingHandrailConnections: Elements, ?railingToprailEnds: Elements, ?railingToprailConnections: Elements, ?railingRails: Elements, ?railingToprails: Elements, ?railingHandrails: Elements, ?railingPatterns: Elements, ?railingInnerPosts: Elements, ?railingPanels: Elements, ?railingBalusterSets: Elements, ?railingBalusters: Elements, ?beamSegments: Elements, ?columnSegments: Elements}]

### GetConnectedElements
# Gets the elements hosted by (connected to) the given owner elements, filtered to the given element type: for example the Windows or Doors of a Wall, the frames, panels, junctions and accessories of a Curtain Wall, the risers, treads and structures of a Stair, or the posts, rails and panels of a Railing. (since 1.1.4)
  elements: Elements, connectedElementType: ElementType
  → ConnectedElementsOrError

### GetSectionElements
# Gets the elements drawn in the given section, elevation or interior elevation databases, each with the owner element it was generated from. This is the only command that returns raw section element identifiers - every other listing command converts them to their owner - so it is the way to obtain the sectionElementId that CreateAssociativeDimensionsOnSection requires. (since 1.5.8)
  ?databases: Databases
  → sectionElements: [{sectionElementId: ElementId, ownerElementId: ElementId, ?ownerElementType: ElementType}], ?executionResultForDatabases: ExecutionResults

### GetRelationsOfElements
# Gets the type-specific relations of the given elements: endpoint and reference line connections of walls, beams and beam segments, boundary elements and boundary sections of zones, the zones on the two sides of windows, doors, skylights and curtain wall panels, and the zones connected to roofs and shells. Available from Archicad 26. (since 1.5.7)
  elements: Elements, ?otherElementType: ElementType
  → relations: [ElementRelationsOrError]

### GetZoneBoundaries
# Gets the boundaries of the given Zones (connected elements, neighbour zones, etc.). Accepts either a single zoneElementId or a list of zones. Prefer the list: the expensive boundary recalculation runs once per call, so querying many Zones in one call is much faster than calling the command once per Zone. (since 1.2.3)
  ?zoneElementId: ElementId, ?zones: Elements
  → ZoneBoundariesOrError | ZoneBoundariesOfZonesWrapper

### UpdateZones
# Updates all Zones (recalculates their geometry, updates their Zone Stamps and the connected elements). (since 1.5.4)
  ?keepStampPosition: bool, ?undoTopTrim: bool, ?undoBottomTrim: bool
  → ExecutionResult

### GetCollisions
# Detect collisions between the given two groups of elements. (since 1.2.2)
  elementsGroup1: Elements, elementsGroup2: Elements, ?settings: {volumeTolerance: float, performSurfaceCheck: bool, surfaceTolerance: float}
  → collisions: [{elementId1: ElementId, elementId2: ElementId, hasBodyCollision: bool, hasClearenceCollision: bool}]

### HighlightElements
# Highlights the elements given in the elements array. In case of empty elements array removes all previously set highlights. (since 1.0.3)
  elements: Elements, highlightedColors: [[int]], ?wireframe3D: bool, ?nonHighlightedColor: [int]
  → ExecutionResult

### MoveElements
# Moves elements with a given vector. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 1.0.2)
  elementsWithMoveVectors[]: elementId: ElementId, moveVector: {x: float, y: float, z: float}, ?copy: bool
  → executionResults: ExecutionResults

### RotateElements
# Rotates elements around a reference point. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 1.5.3)
  elementsWithRotations[]: elementId: ElementId, rotation: {beginPoint: Coordinate2D, endPoint: Coordinate2D, origin: Coordinate2D}, ?copy: bool
  → executionResults: ExecutionResults

### DeleteElements
# Deletes elements. Returns an execution result for each input element: an element that could not be deleted (for example because its layer is locked) gets a failed execution result instead of being skipped silently. (since 1.2.1)
  elements: Elements
  → executionResults: ExecutionResults

### LockElements
# Locks the given elements. Manual lock, not teamwork! (since 1.5.2)
  elements: Elements
  → ExecutionResult

### UnlockElements
# Unlocks the given elements. Manual lock, not teamwork! (since 1.5.2)
  elements: Elements
  → ExecutionResult

### GetGDLParametersOfElements
# Gets all the GDL parameters (name, type, value) of the given elements. (since 1.5.7)
  elements: Elements
  → gdlParametersOfElements: [GDLParameterList]

### SetGDLParametersOfElements
# Sets the given GDL parameters of the given elements. (since 1.5.7)
  elementsWithGDLParameters[]: elementId: ElementId, gdlParameters: SetGDLParameterArray
  → executionResults: ExecutionResults

### GetMarkerParametersOfElements
# Gets the marker library part and the marker's GDL parameters (name, type, value) of the given Window and Door elements. The marker is the stamp drawn next to the opening on the floor plan; its parameters are separate from the opening's own GDL parameters, which GetGDLParametersOfElements returns. (since 1.7.1)
  elements: Elements
  → markerParametersOfElements: [{?libPart: LibPartDetails, parameters: [{name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, value: any, ?valueDescription: string, ?itemDescriptions: [string], flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"]}]} | ErrorItem]

### SetMarkerParametersOfElements
# Sets the given GDL parameters of the marker of the given Window and Door elements. The opening's own settings and the other marker parameters are left as they are. (since 1.7.1)
  elementsWithMarkerParameters[]: elementId: ElementId, markerParameters: [{name: string, value: any} | {index: int, value: any}]
  → executionResults: ExecutionResults

### CreateColumns
# Creates Column elements based on the given parameters. (since 1.0.3)
  columnsData[]: ?favoriteName: string, coordinates: {x: float, y: float, z: float}, ?height: float, ?axisRotationAngle: float, ?slantAngle: float, ?isSlanted: bool, ?slantDirectionAngle: float, ?width: float, ?depth: float, ?coreAnchor: ColumnCoreAnchor, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateWalls
# Creates Wall elements based on the given parameters. (since 1.4.0)
  wallsData[]: ?favoriteName: string, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?floorIndex: int, ?zCoordinate: float, ?height: float, ?thickness: float, ?offset: float, ?arcAngle: float, ?referenceLineLocation: WallReferenceLineLocation, ?structureType: WallStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?contourPen: int, ?contourPen3D: int, ?contourLineTypeId: AttributeId, ?belowViewLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?useCompositePriority: bool, ?linkToSettings: LinkToSettings, ?inheritEndSurface: bool, ?alignTexture: bool, ?polyCanChange: bool, ?materialsChained: bool, ?logHeight: float
  → elements: ElementIdsOrErrors

### CreateBeams
# Creates Beam elements based on the given parameters. (since 1.4.0)
  beamsData[]: ?favoriteName: string, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?floorIndex: int, zCoordinate: float, ?offset: float, ?slantAngle: float, ?isSlanted: bool, ?profileAngle: float, ?arcAngle: float, ?verticalCurveHeight: float, ?width: float, ?height: float, ?anchorPoint: BeamAnchorPoint, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId
  → elements: ElementIdsOrErrors

### CreateStairs
# Creates Stair elements based on the given baseline and parameters. (since 1.5.0)
  stairsData[]: ?favoriteName: string, baseLinePoints: [Coordinate2D], zCoordinate: float, ?floorIndex: int, ?totalHeight: float, ?flightWidth: float, ?stepNum: int, ?riserHeight: float, ?treadDepth: float, ?finishVisible: bool
  → elements: ElementIdsOrErrors

### CreateSlabs
# Creates Slab elements based on the given parameters. (since 1.0.3)
  slabsData[]: ?favoriteName: string, level: float, ?thickness: float, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateWindows
# Creates Window elements in host walls based on the given parameters. (since 1.4.0)
  windowsData[]: ownerWallId: ElementId, centerOffset: float, ?sillHeight: float, ?width: float, ?height: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?libraryPartName: string, ?favoriteName: string
  → elements: ElementIdsOrErrors

### CreateDoors
# Creates Door elements in host walls based on the given parameters. (since 1.4.0)
  doorsData[]: ownerWallId: ElementId, centerOffset: float, ?sillHeight: float, ?width: float, ?height: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?libraryPartName: string, ?favoriteName: string
  → elements: ElementIdsOrErrors

### CreateOpenings
# Creates Opening elements in the given host elements. (since 1.4.0)
  openingsData[]: ownerElementId: ElementId, basePoint: Coordinate3D, ?width: float, ?height: float
  → elements: ElementIdsOrErrors

### CreateMorphs
# Creates Morph elements from simple box definitions. (since 1.4.0)
  morphsData[]: basePoint: Coordinate3D, ?size: Dimensions3D, ?body: MorphBody, ?buildingMaterialId: AttributeId, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?surfaceId: AttributeId, ?topExpansion: float, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateRoofs
# Creates Roof elements based on footprint, level and roof profile data. Creates a multi-plane roof by default; pass 'pivotLine' (and optionally 'angle') to create a single-plane roof instead. (since 1.4.0)
# ⚠ Releases <=1.5.5: NON-FUNCTIONAL (stub, #467) — model roofs as Slab/Morph instead. FIXED since release 1.5.6 (#482): multi-plane works; NEW ?pivotLine:{begCoordinate,endCoordinate} + ?angle (rad) for single-plane (the plane rises to the left of the line direction).
  roofsData[]: level: float, ?floorIndex: int, ?thickness: float, polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?pivotLine: RoofPivotLine, ?angle: float, ?eavesOverhang: float, ?levels: [RoofLevel], ?structureType: RoofStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateCurtainWalls
# Creates Curtain Wall elements along a reference polyline with a column (primary) and row (secondary) pattern. The frame and panel classes come from the favorite or from the Curtain Wall tool defaults; the pattern cells can assign them to the grid. (since 1.7.2)
  curtainWallsData[]: ?favoriteName: string, coordinates: [Coordinate2D], ?zCoordinate: float, ?floorIndex: int, ?height: float, ?primaryPattern: CurtainWallPattern, ?secondaryPattern: CurtainWallPattern, ?cells: [CurtainWallPatternCell]
  → elements: ElementIdsOrErrors

### CreateAssociativeDimensions
# Creates associative linear dimensions from explicit witness point references. (since 1.4.0)
  dimensionsData[]: referencePoint: Coordinate2D, direction: Coordinate2D, ?floorIndex: float, witnessPoints: [AssociativeWitnessPoint]
  → elements: ElementIdsOrErrors

### CreateAssociativeDimensionsOnSection
# Creates associative linear dimensions on section elements using common wall, slab, beam, column and opening presets. The preset points of multiple section elements can be merged into one continuous dimension chain via sectionElementIds. (since 1.4.0)
  dimensionsData[]: ?sectionElementId: ElementId, ?sectionElementIds: [ElementId], referencePoint: Coordinate2D, preset: "WallCompositeFaces"|"WallSkinBorders"|"SlabCompositeFaces"|"SlabSkinBorders"|"BeamOrColumnRefLineEndPoints"|"BeamOrColumnBoundingBoxCorners"|"DoorWindowWallHoleCorners"|"DoorWindowModelHotspots", ?direction: Coordinate2D, ?skinBorderIndices: [int], ?beginPlane: bool, ?totalSizePlane: bool, ?placeOnTop: bool
  → elements: ElementIdsOrErrors

### CreateWallThicknessDimensions
# Creates associative wall thickness dimensions for the given walls. (since 1.4.0)
  dimensionsData[]: wallId: ElementId, referencePoint: Coordinate2D, direction: Coordinate2D
  → elements: ElementIdsOrErrors

### GetDimensionData
# Gets witness point data (coordinates, measured values) from existing dimension chains. (since 1.5.0)
  elements[]: elementId: ElementId
  → dimensionsData: [DimensionDataOrError]

### CreateZones
# Creates Zone elements based on the given parameters. (since 1.1.8)
  zonesData[]: ?favoriteName: string, ?floorIndex: float, name: string, numberStr: string, ?categoryAttributeId: AttributeId, ?stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, geometry: ZoneCreationGeometry
  → elements: ElementIdsOrErrors

### CreatePolylines
# Creates Polyline elements based on the given parameters. (since 1.1.5)
  polylinesData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, ?linePenIndex: int, ?lineTypeIndex: int, ?penWeightMm: float, ?roomSeparator: bool, coordinates: [Coordinate2D], ?arcs: [PolyArc]
  → elements: ElementIdsOrErrors

### CreateLineElements
# Creates Line elements based on the given parameters. (since 1.5.6)
  linesData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateArcs
# Creates Arc elements based on the given parameters. (since 1.5.6)
  arcsData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, origin: Coordinate2D, radius: float, begAngle: float, endAngle: float, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateCircles
# Creates Circle elements based on the given parameters. (since 1.5.6)
  circlesData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, origin: Coordinate2D, radius: float, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateHotspots
# Creates Hotspot elements based on the given parameters. (since 1.5.6)
  hotspotsData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, position: Coordinate2D, ?height: float, ?penIndex: int
  → elements: ElementIdsOrErrors

### CreateHatches
# Creates Hatch elements based on the given parameters. (since 1.5.6)
  hatchesData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, coordinates: [Coordinate2D], ?arcs: [PolyArc], ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool
  → elements: ElementIdsOrErrors

### CreateSplines
# Creates Spline elements based on the given parameters. (since 1.5.6)
  splinesData[]: ?favoriteName: string, ?floorInd: float, ?layerIndex: int, coordinates: [Coordinate2D], ?closed: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateObjects
# Creates Object elements based on the given parameters. (since 1.5.7)
  objectsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings, ?floorIndex: int, ?favoriteName: string
  → elements: ElementIdsOrErrors

### CreateLamps
# Creates Lamp elements based on the given parameters. (since 1.5.7)
  lampsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings, ?lightColor: ColorRGB, ?lightIsOn: bool, ?floorIndex: int, ?favoriteName: string
  → elements: ElementIdsOrErrors

### GetGridElementDefaults
# Returns the Grid Tool defaults: library part, size and GDL parameters of a new grid element. Needs Archicad 26 or later. (since 1.7.2) [AC26+]
  → ?elementId: ElementId, variation: string, floorIndex: int, layerIndex: int, pos: Coordinate2D, angle: float, length: float, xRatio: float, yRatio: float, useXYFixSize: bool, level: float, libInd: int, libraryPartName: string, parameters: [{name: string, displayName: string, type: string, ?value: any, ?dimension1: int, ?dimension2: int}]

### GetGridElements
# Lists the grid elements (placed with the Grid Tool or created by CreateGridElements) with their position, angle, size, library part and optionally GDL parameters. Needs Archicad 26 or later. (since 1.7.2) [AC26+]
  ?includeParameters: bool
  → gridElements: [{elementId: ElementId, variation: string, floorIndex: int, layerIndex: int, pos: Coordinate2D, angle: float, length: float, xRatio: float, yRatio: float, useXYFixSize: bool, level: float, libInd: int, libraryPartName: string, ?parameters: [{name: string, displayName: string, type: string, ?value: any, ?dimension1: int, ?dimension2: int}]}]

### CreateGridElements
# Creates grid elements, the elements the Grid Tool places, from begin and end coordinates, with optional story, layer and GDL parameters. Needs Archicad 26 or later. (since 1.7.2) [AC26+]
  gridElements[]: begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?lengthMode: "length"|"none", ?floorIndex: int, ?layerIndex: int, ?parameters: [{name: string, value: any}]
  → elements: ElementIdsOrErrors, warnings: [string]

### CreateMeshes
# Creates Mesh elements based on the given parameters. (since 1.1.9)
  meshesData[]: ?favoriteName: string, ?floorIndex: int, ?level: float, ?skirtType: MeshSkirtType, ?skirtLevel: float, ?buildingMaterialId: AttributeId, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [MeshSubline]
  → elements: ElementIdsOrErrors

### CreateLabels
# Creates Label elements based on the given parameters. (since 1.2.5)
  labelsData[]: ?favoriteName: string, ?parentElementId: ElementId, ?labelClass: LabelClass, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?leaderLine: LabelLeaderLineSettableDetails, ?begCoordinate: Coordinate2D, ?midCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?floorInd: float
  → elements: ElementIdsOrErrors

### CreateTexts
# Creates standalone Text elements based on the given parameters. (since 1.5.0)
  textsData[]: ?favoriteName: string, coordinate: Coordinate3D, ?text: string, ?runs: [TextRunDetails], ?height: float, ?pen: int, ?angle: float, ?justification: Justification, ?style: TextStyleSettableDetails, ?floorIndex: int, ?layerIndex: int
  → elements: ElementIdsOrErrors

### CreateLevelDimensions
# Creates Level Dimension elements (the Level Dimension tool) based on the given parameters. With a parentElementId the dimension is associative: it shows the height of the parent element (Mesh, Slab, Roof ...) at its position and follows the element when it changes. (since 1.7.2)
  levelDimensionsData[]: ?favoriteName: string, position: Coordinate2D, ?parentElementId: ElementId, ?level: float, ?floorIndex: int, ?layerIndex: int, ?pen: int, ?textHeight: float, ?textPen: int, ?dimForm: int, ?needPlus: bool, ?markerSize: float, ?angle: float, ?origin: DimensionOrigin
  → elements: ElementIdsOrErrors

### ModifyWalls
# Modifies Wall elements based on the given parameters. (since 1.4.0)
  wallsWithDetails[]: elementId: ElementId, ?geometryType: WallModificationGeometryType, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?arcAngle: float, ?height: float, ?thickness: float, ?bottomOffset: float, ?offset: float, ?structureType: WallStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?referenceLineLocation: WallReferenceLineLocation, ?profileType: WallModificationProfileType, ?slantAlpha: float, ?slantBeta: float, ?topOffset: float, ?relativeTopStory: float, ?zoneRel: WallZoneRelation, ?visibility: StoryVisibility, ?isAutoOnStoryVisibility: bool, ?referenceMaterial: OverriddenMaterial, ?oppositeMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?contourPen: int, ?contourPen3D: int, ?contourLineTypeId: AttributeId, ?belowViewLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?useCompositePriority: bool, ?linkToSettings: LinkToSettings, ?inheritEndSurface: bool, ?alignTexture: bool, ?polyCanChange: bool, ?materialsChained: bool, ?logHeight: float
  → executionResults: ExecutionResults

### ModifyBeams
# Modifies Beam elements based on the given parameters. (since 1.4.0)
  beamsWithDetails[]: elementId: ElementId, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?level: float, ?offset: float, ?slantAngle: float, ?arcAngle: float, ?verticalCurveHeight: float, ?beamShape: "Straight"|"HorizontallyCurved"|"VerticallyCurved", ?isSlanted: bool, ?isFlipped: bool, ?profileAngle: float, ?anchorPoint: BeamAnchorPoint, ?width: float, ?height: float, ?isWidthAndHeightLinked: bool, ?circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?holes: [BeamHoleModification], ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → executionResults: ExecutionResults

### ModifySlabs
# Modifies Slab elements based on the given parameters. (since 1.4.0)
  slabsWithDetails[]: elementId: ElementId, ?zCoordinate: float, ?thickness: float, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?floorFill: FloorFill
  → executionResults: ExecutionResults

### ModifyColumns
# Modifies Column elements based on the given parameters. (since 1.4.0)
  columnsWithDetails[]: elementId: ElementId, ?origin: Coordinate2D, ?zCoordinate: float, ?height: float, ?bottomOffset: float, ?axisRotationAngle: float, ?coreAnchor: ColumnCoreAnchor, ?isSlanted: bool, ?slantAngle: float, ?slantDirectionAngle: float, ?isFlipped: bool, ?wrapping: bool, ?topOffset: float, ?relativeTopStory: float, ?width: float, ?depth: float, ?isWidthAndHeightLinked: bool, ?circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → executionResults: ExecutionResults

### ModifyWindows
# Modifies Window elements based on the given parameters. (since 1.4.0)
  windowsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float
  → executionResults: ExecutionResults

### ModifyDoors
# Modifies Door elements based on the given parameters. (since 1.4.0)
  doorsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float
  → executionResults: ExecutionResults

### ModifyMorphs
# Modifies Morph elements based on the given parameters. (since 1.4.0)
  morphsWithDetails[]: elementId: ElementId, ?translation: Coordinate3D, ?rotationDegreesZ: float, ?buildingMaterialId: AttributeId, ?body: MorphBody, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?surfaceId: AttributeId, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float
  → executionResults: ExecutionResults

### ModifyRoofs
# Modifies multi-plane Roof elements based on the given parameters. (since 1.4.0)
  roofsWithDetails[]: elementId: ElementId, ?level: float, ?thickness: float, ?eavesOverhang: float, ?levels: [RoofLevel], ?structureType: RoofStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D
  → executionResults: ExecutionResults

### ModifyMeshes
# Modifies the attributes of Mesh elements based on the given parameters. (since 1.5.4)
  meshesData[]: elementId: ElementId, meshData: MeshModificationData
  → executionResults: ExecutionResults

### ModifyObjects
# Modifies Object elements based on the given parameters. (since 1.5.7)
  objectsWithDetails[]: elementId: ElementId, ?coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings
  → executionResults: ExecutionResults

### ModifyLamps
# Modifies Lamp elements based on the given parameters. (since 1.5.7)
  lampsWithDetails[]: elementId: ElementId, ?coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings, ?lightColor: ColorRGB, ?lightIsOn: bool
  → executionResults: ExecutionResults

### ModifyTexts
# Modifies standalone Text elements based on the given parameters. (since 1.5.9)
  textsWithDetails[]: elementId: ElementId, ?coordinate: Coordinate3D, ?floorIndex: int, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails
  → executionResults: ExecutionResults

### ModifyLabels
# Modifies Label elements based on the given parameters. (since 1.5.9)
  labelsWithDetails[]: elementId: ElementId, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?leaderLine: LabelLeaderLineSettableDetails
  → executionResults: ExecutionResults

### GetElementPreviewImage
# Returns the preview image of the given element. (since 1.2.7)
  elementId: ElementId, ?imageType: "2D"|"Section"|"3D", ?format: "png"|"jpg", ?width: int, ?height: int
  → previewImage: string

### GetRoomImage
# Returns the room image of the given zone. (since 1.2.7)
  zoneId: ElementId, ?format: "png"|"jpg", ?width: int, ?height: int, ?offset: float, ?scale: float, ?backgroundColor: ColorRGB
  → roomImage: string

### SetElementNotificationClient
# Sets up a new notification client to receive element events. (since 1.2.8)
  ?host: string, port: int, ?notifyOnNewElement: bool, ?notifyOnModificationOfAnElement: bool, ?notifyOnReservationChanges: bool
  → ExecutionResult

### RemoveElementNotificationClient
# Removes an element notification client. (since 1.2.8)
  ?host: string, port: int
  → ExecutionResult

## Element grouping Commands

### CreateGroups
# Creates groups of the passed elements (since 1.4.0)
  elementGroups: [ElementGroupParameters]
  → groupGuids: [GroupIdOrError]

### GetGroupsOfElements
# Gets the identifier of the group that directly contains each given element. Returns an error for elements that are not part of any group. (since 1.5.6)
  elements: Elements
  → groupGuids: [GroupIdOrError]

### GetElementsOfGroups
# Gets the elements directly contained by each given group. (since 1.5.6)
  groups: [GroupIdArrayItem]
  → elementsOfGroups: [ElementsWrapperOrError]

### GetSuspendGroupsMode
# Gets the current state of the Suspend Groups mode. (since 1.5.6)
  → suspendGroups: bool

### SetSuspendGroupsMode
# Turns the Suspend Groups mode on or off. Suspend groups to perform operations on elements that are part of a group; remember to restore the previous state afterwards. (since 1.5.6)
  suspendGroups: bool
  → executionResult: ExecutionResult

## Favorites Commands

### GetFavoritesByType
# Returns a list of the names of all favorites with the given element type (since 1.2.2)
  elementType: ElementType
  → FavoritesOrError

### GetFavoritePreviewImage
# Returns the preview image of the given favorite. (since 1.2.7)
  favorite: string, ?imageType: "2D"|"Section"|"3D", ?format: "png"|"jpg", ?width: int, ?height: int
  → previewImage: string

### ApplyFavoritesToElementDefaults
# Apply the given favorites to element defaults. (since 1.1.2)
  favorites: Favorites
  → executionResults: ExecutionResults

### CreateFavoritesFromElements
# Create favorites from the given elements. (since 1.1.2)
  favoritesFromElements[]: elementId: ElementId, favorite: string, ?folder: [string]
  → executionResults: ExecutionResults

### ImportFavorites
# Import Favorites from a .prefs file or folder into the current project. (since 1.5.0)
  path: string, ?targetFolder: [string], ?importFolders: bool, ?conflictPolicy: "Error"|"Skip"|"Overwrite"|"Append"
  → ?firstConflictName: string

### ExportFavorites
# Export the project's Favorites to a .prefs file or folder. (since 1.5.0)
  path: string, ?names: [string]
  → ExecutionResult

### ApplyFavoritesToElements
# Apply the given favorites to existing elements. Only settings-type parameters are changed - geometry (position, floor, and dimensions such as a Wall's height) is left untouched, so applying a Favorite never moves or resizes the target element. For the hierarchical types (Stair, Railing, Curtain Wall) the settings of the sub-elements are not applied, because they are inseparable from the Favorite's own geometry. By default settings, classifications, categories and properties are all applied; each can be opted out of individually. (since 1.5.4)
  favoritesToApply: [{elementId: ElementId, favorite: string}], ?applySettings: bool, ?applyClassifications: bool, ?applyCategories: bool, ?applyProperties: bool
  → executionResults: ExecutionResults

### UpdateFavoritesFromElements
# Update existing favorites from the given elements. (since 1.5.4)
  favoritesFromElements: [FavoritesFromElementUpdate]
  → executionResults: ExecutionResults

### RenameFavorites
# Rename existing favorites. (since 1.5.4)
  renames: [FavoriteRename]
  → executionResults: ExecutionResults

### DeleteFavorites
# Delete existing favorites. (since 1.5.4)
  favorites: Favorites
  → executionResults: ExecutionResults

## Property Commands

### GetAllProperties
# Returns all user defined and built-in properties. (since 1.1.3)
  → properties: [PropertyDetails], ?propertyGroups: [PropertyGroupDetails]

### GetPropertyValuesOfElements
# Returns the property values of the elements for the given property. It works for subelements of hierarchal elements also. (since 1.0.6)
  elements: Elements, properties: PropertyIds
  → propertyValuesForElements: PropertyValuesOrErrorArray

### SetPropertyValuesOfElements
# Sets the property values of elements. It works for subelements of hierarchal elements also. (since 1.0.6)
  elementPropertyValues: ElementPropertyValues
  → executionResults: ExecutionResults

### GetPropertyValuesOfAttributes
# Returns the property values of the attributes for the given property. (since 1.1.8)
  attributeIds: AttributeIds, properties: PropertyIds
  → propertyValuesForAttributes: PropertyValuesOrErrorArray

### SetPropertyValuesOfAttributes
# Sets the property values of attributes. (since 1.1.8)
  attributePropertyValues: AttributePropertyValues
  → executionResults: ExecutionResults

### CreatePropertyGroups
# Creates Property Groups based on the given parameters. (since 1.0.7)
  propertyGroups: [PropertyGroupArrayItem]
  → propertyGroupIds: [PropertyGroupIdArrayItem]

### DeletePropertyGroups
# Deletes the given Custom Property Groups. (since 1.0.9)
  propertyGroupIds: [PropertyGroupIdArrayItem]
  → executionResults: ExecutionResults

### CreatePropertyDefinitions
# Creates Custom Property Definitions based on the given parameters. (since 1.0.9)
  propertyDefinitions: [PropertyDefinitionArrayItem]
  → propertyIds: PropertyIdOrErrorArray

### DeletePropertyDefinitions
# Deletes the given Custom Property Definitions. (since 1.0.9)
  propertyIds: [PropertyIdArrayItem]
  → executionResults: ExecutionResults

### UpdatePropertyDefinitions
# Updates existing Custom Property Definitions in place, keeping their guid: name, description, group, default value or expressions, availability, and enum options (add, rename, remove, reorder). (since 1.5.4)
  propertyDefinitions: [PropertyDefinitionUpdate]
  → executionResults: ExecutionResults

### UpdatePropertyGroups
# Updates the name and/or description of existing Custom Property Groups, keeping their guid. (since 1.6.0)
  propertyGroups: [PropertyGroupUpdate]
  → executionResults: ExecutionResults

### ImportPropertiesXml
# Imports a Property Manager XML export, with the given policy for names that already exist. Returns the property definitions it created and removed. (since 1.6.0)
  xml: string, conflictPolicy: PropertyImportConflictPolicy
  → executionResult: ExecutionResult, created: [GuidId], removed: [GuidId]

## Classification Commands

### GetClassificationsOfElements
# Returns the classification of the given elements in the given classification systems. It works for subelements of hierarchal elements also. (since 1.0.7)
  elements: Elements, classificationSystemIds: ClassificationSystemIds
  → elementClassifications: ElementClassificationsOrErrors

### SetClassificationsOfElements
# Sets the classifications of elements. In order to set the classification of an element to unclassified, omit the classificationItemId field. It works for subelements of hierarchal elements also. (since 1.0.7)
  elementClassifications: ElementClassifications
  → executionResults: ExecutionResults

### CreateClassificationSystems
# Creates Classification Systems including Classification Items based on the given parameters. (since 1.5.0)
  classificationSystemsWithItems: ClassificationSystemsWithItems
  → executionResults: ExecutionResults

### CreateClassificationItems
# Creates Classification Items in the given Classification Systems based on the given parameters. (since 1.5.0)
  newClassificationItems: NewClassificationItems
  → executionResults: ExecutionResults

### DeleteClassificationSystems
# Deletes the given Classification Systems. (since 1.5.2)
  classificationSystemIds: ClassificationSystemIds
  → executionResults: ExecutionResults

### DeleteClassificationItems
# Deletes the given Classification Items. (since 1.5.2)
  classificationItemIds: ClassificationItemIds
  → executionResults: ExecutionResults

### UpdateClassificationSystems
# Updates the name, description, source, version and/or date of existing Classification Systems, keeping their guid. (since 1.6.0)
  classificationSystems: [ClassificationSystemUpdate]
  → executionResults: ExecutionResults

### UpdateClassificationItems
# Updates the id (code), name and/or description of existing Classification Items, keeping their guid and so the elements classified with them. Items cannot be moved to another parent. (since 1.6.0)
  classificationItems: [ClassificationItemUpdate]
  → executionResults: ExecutionResults

### ImportClassificationsXml
# Imports a Classification Manager XML export, with the given policies for systems and items that already exist. Returns the systems and items it created and removed. (since 1.6.0)
  xml: string, systemConflictPolicy: ClassificationSystemConflictPolicy, itemConflictPolicy: ClassificationItemConflictPolicy
  → executionResult: ExecutionResult, created: [GuidId], removed: [GuidId]

## Attribute Commands

### GetAttributesByType
# Returns the details of every attribute of the given type. (since 1.1.3)
  attributeType: AttributeType
  → AttributeHeadersOrError

### DeleteAttributes
# Deletes the given attributes. (since 1.5.4)
  attributesToDelete[]: attributeType: AttributeType, attributeId: AttributeIdArrayItem
  → executionResults: ExecutionResults

### CreateLayers
# Creates or overwrites Layer attributes based on the given parameters. (since 1.0.3)
  ?overwriteExisting: bool
  layerDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?isHidden: bool, ?isLocked: bool, ?isWireframe: bool, ?intersectionGroupNr: int
  → attributeIds: AttributeIdsOrErrors

### CreateLayerCombinations
# Creates or overwrites Layer Combination attributes based on the given parameters. (since 1.2.4)
  ?overwriteExisting: bool
  layerCombinationDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, layers: LayersOfLayerCombination
  → attributeIds: AttributeIdsOrErrors

### CreateLines
# Creates or overwrites Line attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  lineDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?scaleWithPlan: bool, ?defineScale: float, ?lineType: string, ?period: float, ?height: float, ?dashItems: [LineDashItem], ?lineItems: [LineSymbolItemData]
  → attributeIds: AttributeIdsOrErrors

### CreateFills
# Creates or overwrites Fill attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  fillDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?subType: string, ?scaleWithPlan: bool, ?useForWalls: bool, ?useForDraft: bool, ?useForCover: bool, ?horizontalSpacing: float, ?verticalSpacing: float, ?angle: float, ?bitPattern: string, ?gradientStart: Coordinate2D, ?gradientEnd: Coordinate2D, ?percent: float, ?texture: Texture, ?lineItems: [FillLineItem], ?symbolLines: [FillSymbolLine], ?symbolArcs: [FillSymbolArc], ?symbolHotspots: [Coordinate2D]
  → attributeIds: AttributeIdsOrErrors

### CreateZoneCategories
# Creates or overwrites Zone Category attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  zoneCategoryDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?categoryCode: string, ?color: ColorRGB, ?stampName: string, ?stampMainGuid: string, ?stampRevGuid: string
  → attributeIds: AttributeIdsOrErrors

### CreateMEPSystems
# Creates or overwrites MEP System attributes (domain, pens, fill, center line type, surface and insulation surface) based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  mepSystemDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?domain: MEPDomain, ?contourPen: int, ?fillPen: int, ?fillBackgroundPen: int, ?centerLinePen: int, ?fillId: AttributeIdArrayItem, ?centerLineTypeId: AttributeIdArrayItem, ?materialId: AttributeIdArrayItem, ?insulationMaterialId: AttributeIdArrayItem
  → attributeIds: AttributeIdsOrErrors

### CreatePenTables
# Creates or overwrites Pen Table attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  penTableDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?isActiveForModel: bool, ?isActiveForLayout: bool, ?sourceAttributeId: AttributeIdArrayItem, ?pens: [PenData]
  → attributeIds: AttributeIdsOrErrors

### CreateProfiles
# Creates or overwrites Profile attributes as a copy of an existing Profile's geometry, based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  profileDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?sourceAttributeId: AttributeIdArrayItem, ?wallType: bool, ?beamType: bool, ?coluType: bool, ?handrailType: bool, ?otherGDLObjectType: bool, ?skinOverrides: [{skinId: string, ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edgeOverrides: [ProfileEdgeOverride]}], ?newSkins: [ProfileSkinData], ?replaceSkins: bool
  → attributeIds: AttributeIdsOrErrors

### CreateBuildingMaterials
# Creates or overwrites Building Material attributes based on the given parameters. (since 1.0.1)
  ?overwriteExisting: bool
  buildingMaterialDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?id: string, ?manufacturer: string, ?description: string, ?connPriority: int, ?cutFillIndex: int, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutSurfaceIndex: int, ?thermalConductivity: float, ?density: float, ?heatCapacity: float, ?embodiedEnergy: float, ?embodiedCarbon: float, ?showUncutLines: bool, ?collisionDetection: bool, ?cutFillOrientation: string
  → attributeIds: AttributeIdsOrErrors

### CreateComposites
# Creates or overwrites Composite attributes based on the given parameters. (since 1.0.2)
  ?overwriteExisting: bool
  compositeDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?useWith: [string], skins: [{type: string, buildingMaterialId: AttributeIdArrayItem, framePen: int, thickness: float}], separators: [{lineTypeId: AttributeIdArrayItem, linePen: int}]
  → attributeIds: AttributeIdsOrErrors

### CreateSurfaces
# Creates or overwrites Surface attributes based on the given parameters. (since 1.2.2)
  ?overwriteExisting: bool
  surfaceDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?materialType: SurfaceType, ?ambientReflection: float, ?diffuseReflection: float, ?specularReflection: float, ?transparency: float, ?shine: float, ?transparencyAttenuation: float, ?emissionAttenuation: float, ?surfaceColor: ColorRGB, ?specularColor: ColorRGB, ?emissionColor: ColorRGB, ?fillId: AttributeIdArrayItem, ?texture: Texture
  → attributeIds: AttributeIdsOrErrors

### GetBuildingMaterialPhysicalProperties
# Retrieves the physical properties of the given Building Materials. (since 0.1.3)
  attributeIds: AttributeIds
  → properties: BuildingMaterialPhysicalPropertiesList

### GetLayerCombinations
# Returns the details of layer combination attributes. (since 1.2.4)
  attributes: AttributeIds
  → layerCombinations: [LayerCombinationAttributeOrError]

### GetLines
# Returns the details of the given Line attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [LineAttributeField]
  → lines: [LineAttributeOrError]

### GetFills
# Returns the details of the given Fill attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [FillAttributeField]
  → fills: [FillAttributeOrError]

### GetZoneCategories
# Returns the details of the given Zone Category attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [ZoneCategoryAttributeField]
  → zoneCategories: [ZoneCategoryAttributeOrError]

### GetMEPSystems
# Returns the details of the given MEP System attributes (domain, pens, fill, center line type, surface and insulation surface). (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [MEPSystemAttributeField]
  → mepSystems: [MEPSystemAttributeOrError]

### GetPenTables
# Returns the details of the given Pen Table attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [PenTableAttributeField]
  → penTables: [PenTableAttributeOrError]

### GetProfiles
# Returns the details of the given Profile attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [ProfileAttributeField]
  → profiles: [ProfileAttributeOrError]

### GetComposites
# Returns the details of the given Composite attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [CompositeAttributeField]
  → composites: [CompositeAttributeOrError]

### GetSurfaces
# Returns the details of the given Surface attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [SurfaceAttributeField]
  → surfaces: [SurfaceAttributeOrError]

### GetLayers
# Returns the details of the given Layer attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [LayerAttributeField]
  → layers: [LayerAttributeOrError]

### GetBuildingMaterials
# Returns the details of the given Building Material attributes. (since 1.5.4)
  attributeIds: AttributeIds, ?fields: [BuildingMaterialAttributeField]
  → buildingMaterials: [BuildingMaterialAttributeOrError]

### GetGraphicOverrideRules
# Gets all graphic override rules of the project, with their rule group, criterion and style. Available from Archicad 27. (since 1.7.2)
  → graphicOverrideRules: [{graphicOverrideRuleId: GraphicOverrideRuleId, name: string, ?ruleGroupName: string, criterionXML: string, style: GraphicOverrideStyle}]

### CreateGraphicOverrideRules
# Creates graphic override rules. The criterion is given as Archicad's criterion XML or as structured conditions. The rule group is created when no rule group has the given name. Available from Archicad 27. (since 1.7.2)
  graphicOverrideRules[]: name: string, ruleGroupName: string, ?criterionXML: string, ?criterion: GraphicOverrideCriterion, ?style: GraphicOverrideStyle
  → graphicOverrideRuleIds: [GraphicOverrideRuleIdOrError]

### ModifyGraphicOverrideRules
# Modifies the name, criterion or style of graphic override rules. The criterion is given as Archicad's criterion XML or as structured conditions. A given style replaces the whole style of the rule. Available from Archicad 27. (since 1.7.2)
  graphicOverrideRules[]: graphicOverrideRuleId: GraphicOverrideRuleId, ?name: string, ?criterionXML: string, ?criterion: GraphicOverrideCriterion, ?style: GraphicOverrideStyle
  → executionResults: ExecutionResults

### DeleteGraphicOverrideRules
# Deletes graphic override rules. They are also removed from the combinations that contain them. Available from Archicad 27. (since 1.7.2)
  graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]
  → executionResults: ExecutionResults

### GetGraphicOverrideCombinations
# Gets all graphic override combinations of the project with the rules they contain. Available from Archicad 27. (since 1.7.2)
  → graphicOverrideCombinations: [{graphicOverrideCombinationId: GraphicOverrideCombinationId, name: string, graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]}]

### CreateGraphicOverrideCombinations
# Creates graphic override combinations from existing rules. Available from Archicad 27. (since 1.7.2)
  graphicOverrideCombinations[]: name: string, graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]
  → graphicOverrideCombinationIds: [GraphicOverrideCombinationIdOrError]

### DeleteGraphicOverrideCombinations
# Deletes graphic override combinations. Their rules are kept. Available from Archicad 27. (since 1.7.2)
  graphicOverrideCombinationIds: [GraphicOverrideCombinationIdArrayItem]
  → executionResults: ExecutionResults

### GetGraphicOverrideRuleGroups
# Gets all graphic override rule groups of the project with the rules they contain, empty groups included. Available from Archicad 27. (since 1.7.2)
  → graphicOverrideRuleGroups: [{name: string, graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]}]

### DeleteGraphicOverrideRuleGroups
# Deletes graphic override rule groups, found by name. A group that still contains rules is kept unless its rules are moved to another group or deleted with it. Available from Archicad 27. (since 1.7.2)
  ruleGroupNames: [string], ?moveRulesToGroup: string, ?deleteRules: bool
  → executionResults: ExecutionResults

## IFC Commands

### IFCFileOperation
# Executes an IFC file operation: opens or merges an IFC file, or saves the project as an IFC file. A save can name the export translator to use. (since 1.2.6)
  method: "save"|"merge"|"open", ifcFilePath: string, ?fileType: "ifc"|"ifcxml"|"ifczip"|"ifcxmlzip", ?translatorName: string, ?elementsToExport: IFCElementsToExport
  → ExecutionResult

### GetIFCExportTranslators
# Lists the IFC export translators of the project, the preview translator first. Pass one of the names to IFCFileOperation as translatorName. (since 1.6.0)
  → translators: [IFCExportTranslator]

### GetElementsByIFCIds
# Retrieves the elements by the given IFC identifiers. (since 1.5.1)
  ifcIds: [string]
  → elementsByIFCIds: ElementsByIFCIds

### GetIFCIdsOfElements
# Retrieves the IFC identifiers of the given elements. (since 1.5.1)
  elements: Elements
  → elementIFCIds: ElementIFCIdsOrErrors

### GetIFCTypeOfElements
# Retrieves the IFC types of the given elements. (since 1.5.1)
  elements: Elements
  → elementIFCTypes: ElementIFCTypesOrErrors

### GetIFCPropertiesOfElements
# Retrieves the IFC properties of the given elements. (since 1.5.1)
  elements: Elements
  → elementIFCProperties: ElementIFCPropertiesOrErrors

### SetIFCPropertiesOfElements
# Sets local IFC properties on elements by creating or modifying single value (IfcPropertySingleValue) properties in the given property sets. Available only in Archicad 25, 26 and 27 for now. (since 1.7.0)
  elementIFCPropertyValues[]: elementId: ElementId, propertySetName: string, propertyName: string, type: string, value: any
  → executionResults: ExecutionResults

## Library Commands

### GetLibraries
# Gets the list of loaded libraries. (since 1.0.1)
  → libraries: [Library]

### ReloadLibraries
# Executes the reload libraries command. (since 1.0.0)
  → ExecutionResult

### AddFilesToEmbeddedLibrary
# Adds the given files into the embedded library. With the overwriteExisting flag an embedded library item already existing on an outputPath is replaced (Archicad 27 or newer). (since 1.2.2)
  files: LibraryFileAdditions, ?overwriteExisting: bool
  → executionResults: ExecutionResults

### DeleteEmbeddedLibraryItems
# Deletes the given items from the embedded library. The path of an item is the same relative path that AddFilesToEmbeddedLibrary takes as outputPath. Available from Archicad 27. (since 1.6.0)
  embeddedLibraryItems[]: path: string
  → executionResults: ExecutionResults

### SetLibraries
# Makes the given folders the project's local libraries; built-in, embedded, server and web libraries are kept. Set the libraries before opening a file that needs them and the missing-library dialog does not appear. (since 1.5.9)
  libraries: [LibraryLocation]
  → ExecutionResult

### AddLibraries
# Adds the given folders to the project's local libraries, skipping any already loaded. (since 1.5.9)
  libraries: [LibraryLocation]
  → ExecutionResult

### GetAvailableLibraryParts
# Lists library parts currently available to the project. Filter by typeId (e.g. 'Door', 'Window', 'Object', 'Lamp'). (since 1.5.0)
  ?filterByTypeId: LibraryPartType
  → libraryParts: [{?guid: string, ?index: int, ?documentName: string, ?fileName: string, ?typeId: LibraryPartType}], skippedCount: int, ?skippedSample: [{?index: int, ?code: int}]

## Teamwork Commands

### TeamworkSend
# Performs a send operation on the currently opened Teamwork project. (since 0.1.0)
  → ExecutionResult

### TeamworkReceive
# Performs a receive operation on the currently opened Teamwork project. (since 0.1.0)
  → ExecutionResult

### ReserveElements
# Reserves elements in Teamwork mode. (since 1.1.4)
  elements: Elements
  → executionResult: ExecutionResult, ?conflicts: [{elementId: ElementId, user: User}]

### ReleaseElements
# Releases elements in Teamwork mode. (since 1.1.4)
  elements: Elements
  → ExecutionResult

### ReserveLockableObjectSet
# Reserves a non-element lockable object set (attributes, favorites, project info, project preferences, etc.) in Teamwork mode. The object set is given by its Archicad API name, e.g. 'Composites', 'LayerSettingsDialog' or 'ProjectInfo'. (since 1.7.1)
  objectSetName: string
  → executionResult: ExecutionResult, ?conflicts: [User]

### ReleaseLockableObjectSet
# Releases a non-element lockable object set reserved with ReserveLockableObjectSet in Teamwork mode. (since 1.7.1)
  objectSetName: string
  → ExecutionResult

### GetLockableObjectSetStatus
# Returns the Teamwork reservation status of a non-element lockable object set and the users who hold it. (since 1.7.1)
  objectSetName: string
  → status: "Free"|"Editable"|"Locked"|"NotAvailable"|"NotExist", ?conflicts: [User]

### ReserveHotlinkCacheManagement
# Reserves the Hotlink and XRef management in Teamwork mode, which is needed before changing hotlink nodes. (since 1.7.1)
  → executionResult: ExecutionResult, ?conflicts: [User]

### ReleaseHotlinkCacheManagement
# Releases the Hotlink and XRef management in Teamwork mode. (since 1.7.1)
  → ExecutionResult

## Navigator Commands

### PublishPublisherSet
# Performs a publish operation on the currently opened project. Only the given publisher set will be published. (since 0.1.0)
  publisherSetName: string, ?outputPath: string, ?selectedNavigatorItemIds: NavigatorItemIds

### UpdateDrawings
# Performs a drawing update on the given elements. (since 1.1.4)
  elements: Elements
  → ExecutionResult

### GetDatabaseIdFromNavigatorItemId
# Gets the ID of the database associated with the supplied navigator item id (since 1.1.4)
  navigatorItemIds: NavigatorItemIds
  → databases: Databases

### CreateDetails
# Creates independent Detail databases. (since 1.4.0)
  detailsData[]: name: string, referenceId: string
  → databases: DatabaseIdsOrErrors

### CreateWorksheets
# Creates independent Worksheet databases. (since 1.4.0)
  worksheetsData[]: name: string, referenceId: string
  → databases: DatabaseIdsOrErrors

### CreateLayout
# Creates Layouts and their backing master layouts. (since 1.4.0)
  layoutsData[]: ?masterLayoutName: string, ?masterNavigatorItemId: NavigatorItemId, layoutName: string, ?parentNavigatorItemId: NavigatorItemId, ?paperWidth: float, ?paperHeight: float, ?layoutParameters: {?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?displayMasterLayoutBelow: bool}
  → databases: DatabaseIdsOrErrors

### CreateLayoutSubset
# Creates Layout Book subsets. (since 1.4.0)
  subsetsData[]: name: string, ?parentNavigatorItemId: NavigatorItemId, ?ownPrefix: string, ?customNumber: string, ?numberingStyle: "Undefined"|"abc"|"ABC"|"1"|"01"|"001"|"0001"|"noID", ?startAt: int, ?continueNumbering: bool, ?useUpperPrefix: bool, ?includeToIDSequence: bool, ?customNumbering: bool, ?addOwnPrefix: bool
  → navigatorItems: [NavigatorItemIdOrError]

### CreateDrawings
# Creates Drawing elements on the specified or active layout from navigator items. (since 1.4.0)
  drawingsData[]: navigatorItemId: NavigatorItemId, ?layoutDatabaseId: DatabaseId, ?name: string, ?nameType: DrawingNameType, position: Coordinate2D, ?scale: float, ?angle: float, ?drawingScale: float, ?modelOffset: Coordinate2D, ?clipPolygon: [Coordinate2D]
  → elements: ElementIdsOrErrors

### ChangeDrawingLink
# Relinks a Drawing to a different source navigator item. Archicad has no in-place relink API, so this recreates the Drawing against the new source and deletes the original - the returned elementId is a NEW guid, not the input one. The Drawing Title marker's own position is not preserved (undocumented Archicad limitation). (since 1.5.7)
  drawingsWithNewLinks[]: elementId: ElementId, navigatorItemId: NavigatorItemId, layoutDatabaseId: DatabaseId
  → elements: [ElementIdOrError]

### GetLayoutSettings
# Gets settings of layouts, including Layout Info Panel custom data fields. (since 1.1.7)
  layoutDatabaseIds[]: ?databaseId: DatabaseId, ?navigatorItemId: NavigatorItemId
  → layoutSettings: [{?layoutName: string, ?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?displayMasterLayoutBelow: bool, ?customData: [LayoutCustomData]}]

### SetLayoutSettings
# Sets settings of layouts, including Layout Info Panel custom data fields. (since 1.1.7)
  layoutsData[]: ?layoutDatabaseId: DatabaseId, ?layoutNavigatorItemId: NavigatorItemId, ?layoutName: string, ?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?showMasterBelow: bool, ?customData: [LayoutCustomDataToSet]
  → executionResults: ExecutionResults

### GetLayoutCustomScheme
# Gets the Layout Info Panel custom field definitions (name and key) from Book Settings. (since 1.1.7)
  → customScheme: [{customSchemeKey: string, customSchemeName: string}]

### GetModelViewOptions
# Gets all model view options (since 1.1.4)
  → modelViewOptions: [{name: string}]

### GetViewSettings
# Gets the view settings of navigator items (since 1.1.4)
  navigatorItemIds: NavigatorItemIds
  → viewSettings: [ViewSettingsOrError]

### SetViewSettings
# Sets the view settings of navigator items (since 1.1.4)
  navigatorItemIdsWithViewSettings[]: navigatorItemId: NavigatorItemId, viewSettings: ViewSettings
  → executionResults: ExecutionResults

### GetActiveGraphicalOverrideCombination
# Gets the graphic override combination applied to the current window, with its id and name. The response is empty when no combination is applied. This is the combination of the window itself, not the one stored in a saved view (see GetViewSettings). Available from Archicad 30. (since 1.7.2)
  → ?combinationId: {guid: Guid}, ?name: string

### SetActiveGraphicalOverrideCombination
# Applies a graphic override combination, given by id or by name, to the current window. The current window must be a model window (floor plan, section, elevation, 3D, ...). To remove the overrides, apply the project's 'No Overrides' combination. The saved view is not changed (see SetViewSettings for that). Available from Archicad 30. (since 1.7.2)
  ?combinationId: {guid: Guid}, ?name: string
  → ExecutionResult

### GetView2DTransformations
# Get zoom and rotation of 2D views (since 1.1.7)
  ?navigatorItemIds: NavigatorItemIds, ?databases: Databases
  → transformations: [ViewTransformationsOrError]

### SetViewRotation
# Set the rotation angle of 2D views via their floor plan database. (since 1.1.7)
  navigatorItemIdsWithRotation[]: navigatorItemId: NavigatorItemId, rotation: float
  → executionResults: ExecutionResults

### CloneProjectMapItemToViewMap
# Clones Project Map viewpoints into a specified View Map folder. (since 1.1.7)
  viewsData[]: navigatorItemId: NavigatorItemId, parentNavigatorItemId: NavigatorItemId
  → navigatorItems: [NavigatorItemIdOrError]

### CreateViewsInViewMap
# Creates independent (non-clone) navigator views in a specified View Map folder, by copying database and settings from source items. (since 1.1.7)
  viewsData[]: navigatorItemId: NavigatorItemId, parentNavigatorItemId: NavigatorItemId, ?name: string
  → navigatorItems: [NavigatorItemIdOrError]

### CreateViewMapFolder
# Creates a new folder in the View Map. (since 1.1.7)
  folderName: string, ?parentNavigatorItemId: NavigatorItemId
  → navigatorItemId: NavigatorItemId

### Set3DCutPlanes
# Sets the 3D cut planes. (since 1.3.1)
  ?cutPlanes[]: pa: float, pb: float, pc: float, pd: float
  → ExecutionResult

### Get3DProjectionSettings
# Gets the 3D projection settings of the 3D window: whether it is perspective or axonometric, the camera and target position, view cone, roll angle, distance and azimuth of a perspective, or the transformation matrix of an axonometry. (since 1.7.1)
  → isPersp: bool, ?cameraElementId: ElementId, ?activeCameraSetElementId: ElementId, ?perspective: PerspectiveProjectionParameters, ?axonometric: {transformationMatrix: [float]}

### Set3DProjectionSettings
# Sets a perspective projection for the 3D window. Every perspective parameter is required: read a known good set with Get3DProjectionSettings and pass it back, with the values to change replaced. (since 1.7.1)
  perspective: PerspectiveProjectionParameters
  → ExecutionResult

### FitInWindow
# Zooms to the given elements or fits everything in the window. (since 1.3.1)
  ?elements: Elements
  → ExecutionResult

### CreateSections
# Creates Section elements on the floor plan. (since 1.5.0)
  sectionsData[]: startCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?depth: float, ?name: string, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateInteriorElevations
# Creates Interior Elevation elements on the floor plan. Every consecutive pair of the given points becomes one segment, each with its own viewpoint - feed it the corner points of a room to get an interior elevation of that room. (since 1.5.8)
  interiorElevationsData: [InteriorElevationData]
  → elements: ElementIdsOrErrors

### MoveNavigatorItem
# Moves a navigator item to a new parent in the navigator tree. (since 1.1.7)
  navigatorItemIdToMove: NavigatorItemId, parentNavigatorItemId: NavigatorItemId, ?previousNavigatorItemId: NavigatorItemId
  → ExecutionResult

### RenameNavigatorItem
# Renames a navigator item or changes its ID. Fails when Archicad does not apply the new name (e.g. on Project Map schedule items, which are named by their scheme). With customName false the item drops its custom name and follows its Project Map source again. (since 1.1.7)
  navigatorItemId: NavigatorItemId, ?newName: string, ?newId: string, ?customName: bool
  → ExecutionResult

### DeleteNavigatorItems
# Deletes navigator items from the navigator tree. (since 1.1.7)
  navigatorItemIds: NavigatorItemIds
  → executionResults: ExecutionResults

### GetNavigatorItemTree
# Returns the full navigator item tree for the specified map. (since 1.1.7)
  navigatorMapId: "PublicViewMap"|"ProjectMap"|"LayoutBook"|"PublisherSets", ?publisherSetName: string
  → navigatorItemTree: NavigatorItem

## Graphic Override Commands

### CreateGraphicalOverrideRule
# Creates or overwrites a graphic override rule in a rule group: name, criterion XML, surface color and line pen. Needs Archicad 27 or later. (since 1.7.2) [AC27+]
  name: string, ?ruleGroupName: string, ?criterionXML: string, ?surfaceRGB: {red: float, green: float, blue: float}, ?linePenIndex: int, ?overrideContours: bool
  → ruleId: GuidId

### GetGraphicalOverrideRules
# Returns every graphic override rule with its criterion XML. Needs Archicad 27 or later. (since 1.7.2) [AC27+]
  → rules: [{ruleId: GuidId, name: string, ruleGroupName: string, criterionXML: string}]

### CreateGraphicalOverrideCombination
# Creates a graphic override combination from rule names, or replaces the rules of an existing one. Needs Archicad 27 or later. (since 1.7.2) [AC27+]
  name: string, ruleNames: [string]
  → combinationId: GuidId

## Issue Management Commands

### CreateIssue
# Creates a new issue. (since 1.0.2)
  name: string, ?parentIssueId: IssueId, ?tagText: string
  → issueId: IssueId

### DeleteIssue
# Deletes the specified issue. (since 1.0.2)
  issueId: IssueId, ?acceptAllElements: bool
  → ExecutionResult

### GetIssues
# Retrieves information about existing issues. (since 1.0.2)
  → issues: [{issueId: IssueId, name: string, parentIssueId: IssueId, creaTime: int, modiTime: int, tagText: string, tagTextElementId: ElementId, isTagTextElemVisible: bool}]

### AddCommentToIssue
# Adds a new comment to the specified issue. (since 1.0.6)
  issueId: IssueId, ?author: string, ?status: IssueCommentStatus, text: string
  → ExecutionResult

### GetCommentsFromIssue
# Retrieves comments information from the specified issue. (since 1.0.6)
  issueId: IssueId
  → comments: [{guid: Guid, author: string, text: string, status: IssueCommentStatus, creaTime: int}]

### AttachElementsToIssue
# Attaches elements to the specified issue. (since 1.0.6)
  issueId: IssueId, elements: Elements, type: IssueElementType
  → ExecutionResult

### DetachElementsFromIssue
# Detaches elements from the specified issue. (since 1.0.6)
  issueId: IssueId, elements: Elements
  → ExecutionResult

### GetElementsAttachedToIssue
# Retrieves attached elements of the specified issue, filtered by attachment type. (since 1.0.6)
  issueId: IssueId, type: IssueElementType
  → elements: Elements

### ExportIssuesToBCF
# Exports specified issues to a BCF file. (since 1.0.6)
  ?issues: Issues, exportPath: string, useExternalId: bool, alignBySurveyPoint: bool
  → ExecutionResult

### ImportIssuesFromBCF
# Imports issues from the specified BCF file. (since 1.0.6)
  importPath: string, alignBySurveyPoint: bool
  → ExecutionResult

## Revision Management Commands

### GetRevisionIssues
# Retrieves all issues. (since 1.1.9)
  → revisionIssues: [RevisionIssue]

### GetRevisionChanges
# Retrieves all changes. (since 1.1.9)
  → revisionChanges: [RevisionChange]

### GetDocumentRevisions
# Retrieves all document revisions. (since 1.1.9)
  → documentRevisions: [DocumentRevision]

### GetCurrentRevisionChangesOfLayouts
# Retrieves all changes belong to the last revision of the given layouts. (since 1.1.9)
  layoutDatabaseIds: Databases
  → currentRevisionChangesOfLayouts: RevisionChangesOfEntities

### GetRevisionChangesOfElements
# Retrieves the changes belong to the given elements. (since 1.1.9)
  elements: Elements
  → revisionChangesOfElements: RevisionChangesOfEntities

## Design Options Commands

### GetDesignOptions
# Retrieves information about existing design options. Available from Archicad 29. (since 1.2.9)
  → designOptions: [DesignOptionDetails]

### GetDesignOptionSets
# Retrieves information about existing design option sets. Available from Archicad 29. (since 1.2.9)
  → designOptionSets: [{designOptionSetId: GuidId, name: string, designOptions: [DesignOptionIdArrayItem]}]

### GetDesignOptionCombinations
# Retrieves information about existing design option combinations. (since 1.2.9)
  → designOptionCombinations: [DesignOptionCombinationDetails]

### GetElementsOfDesignOptions
# Retrieves the elements associated with the given design options. Available from Archicad 29. (since 1.5.1)
  designOptions: [DesignOptionIdArrayItem]
  → elementsOfDesignOptions: [ElementsOfDesignOptionOrError]

### GetDesignOptionForElements
# Retrieves the design option association for the specified elements. Available from Archicad 29. (since 1.5.1)
  elements: Elements
  → designOptionForElements: [{elementId: ElementId, type: DesignOptionLinkType, ?designOption: DesignOptionDetails}]

### CreateDesignOptionSets
# Creates new design option sets with the given names. Available from Archicad 29. (since 1.5.1)
  designOptionSets: [string]
  → executionResults: ExecutionResults

### CreateDesignOptions
# Creates new design options with the given parameters. Available from Archicad 29. (since 1.5.1)
  designOptions: [DesignOptionData]
  → designOptionIdsOrErrors: DesignOptionIdsOrErrors

### CreateDesignOptionCombinations
# Creates new design option combinations with the given parameters. Available from Archicad 29. (since 1.5.1)
  designOptionCombinations: [DesignOptionCombinationData]
  → designOptionCombinationIdsOrErrors: DesignOptionCombinationIdsOrErrors

### SetActiveDesignOptionsInCombinations
# Sets active design options in the given combinations. Available from Archicad 29. (since 1.5.1)
  activeDesignOptionsInCombinations[]: designOptionCombinationId: DesignOptionCombinationId, activeDesignOptions: [DesignOptionIdArrayItem]
  → executionResults: ExecutionResults

### MoveElementsToDesignOptions
# Moves the given elements into the given design options. Use NULLGuid for design option to remove the element from any design options and move it to the main model. Available from Archicad 29. (since 1.5.1)
  elementDesignOptionPairs[]: elementId: ElementId, designOptionId: DesignOptionId
  → executionResults: ExecutionResults

### MoveDesignOptionsToAnotherSet
# Moves the given design options to another sets. Available from Archicad 29. (since 1.5.1)
  designOptionAndSetPairs[]: designOptionId: DesignOptionId, setName: string
  → executionResults: ExecutionResults

### RenameDesignOptions
# Changes the name and/or the string id of the given design options. Available from Archicad 29. (since 1.7.1)
  designOptions[]: designOptionId: DesignOptionId, ?name: string, ?id: string
  → executionResults: ExecutionResults

### RenameDesignOptionSets
# Changes the name of the given design option sets. Available from Archicad 29. (since 1.7.1)
  designOptionSets[]: designOptionSetId: DesignOptionSetId, name: string
  → executionResults: ExecutionResults

### RenameDesignOptionCombinations
# Changes the name of the given design option combinations. Available from Archicad 29. (since 1.7.1)
  designOptionCombinations[]: designOptionCombinationId: DesignOptionCombinationId, name: string
  → executionResults: ExecutionResults

### DeleteDesignOptions
# Deletes the given design options. Available from Archicad 29. (since 1.7.1)
  designOptions: [DesignOptionIdArrayItem]
  → executionResults: ExecutionResults

### DeleteDesignOptionSets
# Deletes the given design option sets. Available from Archicad 29. (since 1.7.1)
  designOptionSets: [DesignOptionSetIdArrayItem]
  → executionResults: ExecutionResults

### DeleteDesignOptionCombinations
# Deletes the given design option combinations. Available from Archicad 29. (since 1.7.1)
  designOptionCombinations: [DesignOptionCombinationIdArrayItem]
  → executionResults: ExecutionResults

## Keynote Commands

### GetKeynoteTree
# Retrieves the whole keynote folder and item hierarchy. The technical root folder is not included in the output; the top-level folders and items are returned directly. Available from Archicad 28. (since 1.5.6)
  → foldersInRoot: [KeynoteFolderDetails], itemsInRoot: [KeynoteItemDetails]

### GetKeynoteAutoTexts
# Retrieves the autotext tokens of the given keynote items. The tokens can be used as label text content to reference the fields of a keynote item. Available from Archicad 28. (since 1.5.6)
  keynoteItems: [KeynoteItemIdArrayItem]
  → autoTexts: KeynoteAutoTextTokensOrErrors

### CreateKeynoteFolders
# Creates keynote folders under the given parent folders (or under the root folder). Available from Archicad 28. (since 1.5.6)
  foldersData[]: ?parentFolderId: KeynoteFolderId, key: string, title: string
  → keynoteFolderIdsOrErrors: KeynoteFolderIdsOrErrors

### CreateKeynoteItems
# Creates keynote items in the given parent folders (or in the root folder). Available from Archicad 28. (since 1.5.6)
  itemsData[]: ?parentFolderId: KeynoteFolderId, key: string, ?title: string, ?description: string, ?reference: string
  → keynoteItemIdsOrErrors: KeynoteItemIdsOrErrors

### ModifyKeynoteFolders
# Modifies the key, title or reference of the given keynote folders. Available from Archicad 28. (since 1.5.6)
  foldersData[]: keynoteFolderId: KeynoteFolderId, ?key: string, ?title: string, ?reference: string
  → executionResults: ExecutionResults

### ModifyKeynoteItems
# Modifies the key, title, description or reference of the given keynote items. Available from Archicad 28. (since 1.5.6)
  itemsData[]: keynoteItemId: KeynoteItemId, ?key: string, ?title: string, ?description: string, ?reference: string
  → executionResults: ExecutionResults

### DeleteKeynoteFolders
# Deletes the given keynote folders including their content. Available from Archicad 28. (since 1.5.6)
  keynoteFolderIds: [KeynoteFolderIdArrayItem]
  → executionResults: ExecutionResults

### DeleteKeynoteItems
# Deletes the given keynote items. Available from Archicad 28. (since 1.5.6)
  keynoteItemIds: [KeynoteItemIdArrayItem]
  → executionResults: ExecutionResults

### CreateKeynoteLabels
# Creates Label elements that reference the given keynote items via autotext. Available from Archicad 28. (since 1.5.6)
  labelsData[]: keynoteItemId: KeynoteItemId, position: Coordinate2D, ?contentFields: ["Key"|"Title"|"Description"|"Reference"]
  → elements: ElementIdsOrErrors

## MEP Commands

### GetMEPElements
# Retrieves the MEP (Mechanical, Electrical, Plumbing) elements of the project, optionally filtered by type and domain. MEP elements are ordinary elements, so the generic element commands work on them as well (for example they can be deleted with the DeleteElements command). Available from Archicad 28. (since 1.5.6)
  ?elementTypes: [MEPElementType], ?domains: [MEPDomain]
  → elements: [MEPElement]

### GetMEPRoutingElements
# Retrieves the details of the given MEP routing elements: domain, MEP system, route polyline, segments with cross section data (shape, size, preference table and reference id) and nodes. Available from Archicad 28. (since 1.5.6)
  elements: Elements
  → routingElements: MEPRoutingElementDetailsOrErrors

### GetMEPPorts
# Retrieves the ports of the given MEP elements including position, shape, size and connection status. Available from Archicad 28. (since 1.5.6)
  elements: Elements
  → elementPorts: MEPElementPortsOrErrors

### GetMEPDistributionSystems
# Retrieves the MEP distribution systems of the project with their domain, MEP system attribute and member elements. Available from Archicad 28. (since 1.5.6)
  → distributionSystems: [MEPDistributionSystem]

### CreateMEPRoutingElements
# Creates MEP routing elements (duct, pipe or cable carrier routes) along the given polylines with optional cross section data (shape, size, preference table and reference id), MEP system and layer (also set on the segments, elbows and transitions). Available from Archicad 28. (since 1.5.6)
  routingElementsData[]: domain: MEPDomain, nodeCoordinates: [Coordinate3D], ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionShape: MEPCrossSectionShape, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?mepSystemId: AttributeId, ?layerIndex: int
  → elements: ElementIdsOrErrors

### CreateMEPElements
# Creates MEP elements (Terminal, Accessory, Equipment or Fitting) at the given positions. Available from Archicad 28. (since 1.5.6)
  elementsData[]: type: MEPComponentType, ?domain: MEPDomain, position: Coordinate3D, ?orientationDirection: Coordinate3D, ?orientationRotation: Coordinate3D
  → elements: ElementIdsOrErrors

### ModifyMEPRoutingElements
# Modifies the given MEP routing elements: MEP system, cross section data (shape, size, preference table and reference id) of all segments and node positions. Available from Archicad 28. (since 1.5.6)
  routingElementsData[]: elementId: ElementId, ?mepSystemId: AttributeId, ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionShape: MEPCrossSectionShape, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?nodePositions: [Coordinate3D]
  → executionResults: ExecutionResults

### ConnectMEPElements
# Connects MEP routing elements to other MEP elements or routes. Merges routes, splits routes or creates branch elements as needed. Available from Archicad 28. (since 1.5.6)
  connectionsData[]: routingElementId: ElementId, connectToId: ElementId
  → connectionResults: MEPConnectionResultsOrErrors

### GetMEPPreferenceTables
# Gets the circular cross section preference tables (referenceId, diameter, description) and the reference set of the Piping or Ventilation domain, optionally with the elbow, branch and transition preference tables. The angle set and the transition tables are available from Archicad 29. Available from Archicad 28. (since 1.5.7)
  domain: MEPPreferenceTableDomain, ?includeFittingTables: bool
  → tables: [MEPPreferenceTable], referenceSet: MEPReferenceSet, ?angleSet: MEPAngleSet, ?elbowTables: [MEPElbowPreferenceTable], ?branchTables: [MEPBranchPreferenceTable], ?transitionTables: [MEPTransitionPreferenceTable]

### GetMEPSystemGroups
# Gets the MEP system groups of the project with their physical systems: name, root element and MEP system. Available from Archicad 29. (since 1.7.2)
  → systemGroups: [MEPSystemGroupDetailsOrError]

### CreateMEPSystemGroups
# Creates MEP system groups. Available from Archicad 29. (since 1.7.2)
  systemGroupsData[]: name: string
  → systemGroups: [MEPSystemGroupIdOrError]

### CreateMEPPhysicalSystems
# Creates physical systems in MEP system groups, optionally with a root element and an MEP system as their category. Available from Archicad 29. (since 1.7.2)
  physicalSystemsData[]: systemGroupId: MEPSystemGroupId, name: string, ?rootElementId: ElementId, ?mepSystemId: AttributeId
  → physicalSystems: [MEPPhysicalSystemIdOrError]

### GetElectricalPanels
# Gets the electrical panels (distribution boards) of the project or the given ones: name, circuit naming, circuits, parent circuit, placement and the connected and demand loads in total and per phase. Available from Archicad 30. (since 1.7.2)
  ?elements: Elements
  → electricalPanels: [ElectricalPanelDetailsOrError]

### GetElectricalCircuits
# Gets the given electrical circuits, the circuits of the given panels, or every circuit of the project: name, description, owner panel, connected devices and panels, voltage, phases, wiring type, loads, voltage drop and estimated cable length. Available from Archicad 30. (since 1.7.2)
  ?elements: Elements, ?electricalPanels: Elements
  → electricalCircuits: [ElectricalCircuitDetailsOrError]

### GetElectricalDevices
# Gets the electrical devices (lights, sockets and other consumers) of the project or the given ones: parent circuit, placement, apparent power, load classification, demand load and directly connected MEP elements. Available from Archicad 30. (since 1.7.2)
  ?elements: Elements
  → electricalDevices: [ElectricalDeviceDetailsOrError]

### GetElectricalProjectSettings
# Gets the electrical project settings: the default voltage, the wiring types with their cross-sectional area and the load classifications with their demand factor. Available from Archicad 30. (since 1.7.2)
  → voltage: float, wiringTypes: [{name: string, crossSectionalArea: float}], loadClassifications: [{name: string, demandFactor: float}]

### CreateElectricalPanels
# Places electrical panels with the default settings of the Electrical Panel tool, optionally with the given library part, size, rotation, mirroring, panel name and circuit naming. Available from Archicad 30. (since 1.7.2)
  electricalPanelsData[]: position: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float, ?panelName: string, ?circuitNamePrefix: string, ?circuitIdStyle: int
  → elements: ElementIdsOrErrors

### CreateElectricalDevices
# Places electrical devices with the default settings of the Electrical Device tool, optionally with the given library part, size, rotation, mirroring, apparent power and load classification, and connects them to a circuit. Available from Archicad 30. (since 1.7.2)
  electricalDevicesData[]: position: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float, ?apparentPower: int, ?isApparentPowerEnabled: bool, ?loadClassificationName: string, ?circuitId: ElementId
  → elements: ElementIdsOrErrors

### ModifyElectricalPanels
# Modifies the name, circuit naming and placement (anchor point, orientation, rotation, mirroring, library part, size) of electrical panels. Available from Archicad 30. (since 1.7.2)
  electricalPanelsData[]: elementId: ElementId, ?panelName: string, ?circuitNamePrefix: string, ?circuitIdStyle: int, ?anchorPoint: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float
  → executionResults: ExecutionResults

### CreateElectricalCircuits
# Adds new circuits to electrical panels, optionally with the given description, voltage, wiring type and used phases. Available from Archicad 30. (since 1.7.2)
  electricalCircuitsData[]: electricalPanelId: ElementId, ?description: string, ?voltage: float, ?wiringTypeName: string, ?isPhaseAUsed: bool, ?isPhaseBUsed: bool, ?isPhaseCUsed: bool
  → elements: ElementIdsOrErrors

### DeleteElectricalCircuits
# Removes electrical circuits from their panels. Available from Archicad 30. (since 1.7.2)
  electricalCircuits: Elements
  → executionResults: ExecutionResults

### ModifyElectricalCircuits
# Modifies the description, voltage, wiring type and used phases of electrical circuits. Available from Archicad 30. (since 1.7.2)
  electricalCircuitsData[]: elementId: ElementId, ?description: string, ?voltage: float, ?wiringTypeName: string, ?isPhaseAUsed: bool, ?isPhaseBUsed: bool, ?isPhaseCUsed: bool
  → executionResults: ExecutionResults

### ModifyElectricalDevices
# Modifies the apparent power, load classification and placement (anchor point, orientation, rotation, mirroring, library part, size) of electrical devices. Available from Archicad 30. (since 1.7.2)
  electricalDevicesData[]: elementId: ElementId, ?apparentPower: int, ?isApparentPowerEnabled: bool, ?loadClassificationName: string, ?anchorPoint: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float
  → executionResults: ExecutionResults

### ConnectToElectricalCircuits
# Connects electrical devices, or panels as sub-panels, to electrical circuits. Available from Archicad 30. (since 1.7.2)
  connectionsData[]: elementId: ElementId, circuitId: ElementId
  → executionResults: ExecutionResults

### ModifyElectricalProjectSettings
# Modifies the electrical project settings: sets the default voltage and adds or removes wiring types and load classifications. Available from Archicad 30. (since 1.7.2)
  ?voltage: float, ?wiringTypesToAdd: [{name: string, crossSectionalArea: float}], ?wiringTypesToRemove: [string], ?loadClassificationsToAdd: [{name: string, demandFactor: float}], ?loadClassificationsToRemove: [string]
  → ExecutionResult

## Solid Element Operation Commands

### CreateSolidElementLinks
# Creates solid element operation links between target and operator elements. (since 1.5.4)
  solidLinks: [SolidLinkData]
  → executionResults: ExecutionResults

### RemoveSolidElementLinks
# Removes solid element operation links between target and operator elements. (since 1.5.4)
  solidLinks: [SolidLinkReference]
  → executionResults: ExecutionResults

### GetSolidElementLinks
# Returns solid element operation links for each queried element, grouped by role (target or operator). (since 1.5.4)
  elements: Elements
  → solidLinks: [SolidLinksOfElement]

### TrimElements
# Trims construction elements with a roof or shell: the roofs and shells in the list, or one given trimming element with a trim type. (since 1.5.9)
  elements: Elements, ?trimmingElement: ElementId, ?trimType: TrimType
  → ExecutionResult

### RemoveElementTrims
# Removes the trim between an element and the roof or shell trimming it. (since 1.5.9)
  elementPairs[]: elementId: ElementId, trimmingElementId: ElementId
  → executionResults: ExecutionResults

### GetElementTrims
# Which roofs and shells trim each queried element, with the trim type, and which elements it trims. (since 1.5.9)
  elements: Elements
  → elementTrims: [ElementTrimsOrError]

## Script UI Commands

### ShowScriptUI
# Shows the given HTML content in a native Archicad palette (a tkinter alternative for Python scripts). (since 1.5.4)
  htmlContent: string, ?width: int, ?height: int, ?title: string, ?resizable: bool, ?zoomEnabled: bool, ?zoomLevel: float, ?scrollBarsVisible: bool, ?contextMenuEnabled: bool, ?navigationDisabled: bool, ?allowSelfSignedCertificates: bool, ?clearCookies: bool, ?autoHeight: bool
  → ExecutionResult

### GetScriptUIResult
# Retrieves and clears the result last submitted from the Script UI palette's page (via window.ACAPI.SubmitResult), if any, and reports whether the palette is still open, so a waiting script can stop when the user closes it. (since 1.5.4)
  → hasResult: bool, ?result: string, isOpen: bool

## Developer Commands

### GenerateDocumentation
# Generates files for the documentation. Used by Tapir developers only. (since 1.0.7)
  destinationFolder: string
  → ExecutionResult
