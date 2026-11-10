# Tapir Archicad Commands v2.0.0

Generated from Tapir 2.0.0's command reference (789 commands) by
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
- `(since x.y.z)` = the first Tapir release that registers the command (taken from the release tags; the version a command is registered with in the source can be one release too early); `[AC27+]` and similar = Archicad versions named in the description
- Types: float, int, bool, string; other names are the shared types below

## Cross-cutting notes (verified live)
- `floorIndex` is available in all create commands, with split semantics: `CreateWalls` `z` is RELATIVE to the story, all other create commands take `z` ABSOLUTE (`floorIndex` only pins the home story).
- GDL array parameters are editable (since 1.5.4, #455); since 1.7.2 they are written through the API (#558).
- Reads of attribute details (`GetLayers`, `GetBuildingMaterials`, ...) need `attributeIds`; list them first with `GetAttributesByType`.
- Layout and navigator work starts from `GetNavigatorItemTree` (item ids); `SetLayoutSettings` sizes apply to master layouts only - verify by reading back.

## Shared Types

- **AccuracyType**: "Off"|"ShowSmall5"|"ShowSmall25"|"ShowSmall1"|"ShowSmall01"|"InchCaseFractions"
- **ActionCenterCheck**: "Hotlinks"|"All"|"Libraries"|"Drawings"|"Licenses"
- **AddOnViewpointDetails**: {viewpointId: {guid: Guid}, ?parentViewpointId: {guid: Guid}, itemType: "Root"|"Group"|"Leaf"|"Undefined", displayId: string, displayName: string, viewSettingsFlags: int, data: string}
- **AddOnViewpointModificationData**: {viewpointId: {guid: Guid}, ?displayId: string, ?displayName: string, ?viewSettingsFlags: int, ?data: string}
- **AddOnViewpointType**: "Root"|"Group"|"Leaf"
- **AnalyticalCoordSysDirection**: "Global"|"Local"
- **AnalyticalCoordinateSystem**: {xVector: Coordinate3D, yVector: Coordinate3D}
- **AnalyticalCrossSection**: {?crossSectionType: "Rectangle"|"Circle"|"Attribute"|"Custom", ?width: float, ?height: float, ?veneerThickness: float, ?profileAttrIndex: int, ?materialAttrIndices: [int], ?profileParameters: [{parameterId: GuidId, value: float}], ?alignment: "TopLeft"|"Top"|"TopRight"|"Left"|"Center"|"Right"|"BottomLeft"|"Bottom"|"BottomRight"|"None"}
- **AnalyticalCurve**: {?type: "Line"|"Arc"|"Spline"|"Bezier"|"Ellipse", begNode: AnalyticalNode, endNode: AnalyticalNode, midCoords: [Coordinate3D]}
- **AnalyticalCurveMember**: {?analyticalMemberType: AnalyticalMemberType, ?elemGuid: GuidId, ?crossSection: AnalyticalCrossSection, ?curve: AnalyticalCurve, ?internalNodes: [AnalyticalNode], ?rotationAngle: float, ?ey: float, ?eyVector: Coordinate3D, ?ez: float, ?ezVector: Coordinate3D, ?layerAttrIndex: int, ?FEMType: "Standard"|"AxialForceOnly"|"CompressionOnly"|"TensionOnly", ?varyingSegmentList: [{begProfile: AnalyticalCrossSection, ?endProfile: AnalyticalCrossSection, span: float}]}
- **AnalyticalCurveMemberDetails**: {curveMember: AnalyticalCurveMember, connections: AnalyticalMemberConnections}
- **AnalyticalCurveMemberStretch**: {begAdditionalLength: float, endAdditionalLength: float}
- **AnalyticalCurveMemberStretchUpdate**: {elementId: ElementId, begAdditionalLength: float, endAdditionalLength: float}
- **AnalyticalEdgeLoad**: {loadSettings: {loadCaseId: GuidId, loadForceType: AnalyticalLoadForceType, loadDistributionType: "Uniform"|"Trapezoid", coordinateSystemType: AnalyticalCoordSysDirection, startValue: Coordinate3D, endValue: Coordinate3D}, loadedMemberPartRef: AnalyticalMemberPartRef}
- **AnalyticalEdgeLoadCustomData**: {curve: [AnalyticalCurve]}
- **AnalyticalEdgeLoadDetails**: {edgeLoad: AnalyticalEdgeLoad, customData: AnalyticalEdgeLoadCustomData, geometry: AnalyticalEdgeLoadCustomData}
- **AnalyticalExportIdMapping**: {edges: AnalyticalExportMappingTable, vertices: AnalyticalExportMappingTable}
- **AnalyticalExportMappingTable**: {items: [{partId: AnalyticalInternalMemberPartId, elemPartIds: [{memberGuid: GuidId, contourIndex: int, edgeOrVertexIndex: int}]}]}
- **AnalyticalImportIdMapping**: {edges: AnalyticalImportMappingTable, vertices: AnalyticalImportMappingTable}
- **AnalyticalImportMappingTable**: {items: [{elemPartId: {memberGuid: GuidId, contourIndex: int, edgeOrVertexIndex: int}, memberPartRef: AnalyticalMemberPartRef}]}
- **AnalyticalInternalMemberPartId**: {?contourIdx: int, ?edgeOrVertexIdx: int, ?edgeFragmentIndex: int}
- **AnalyticalLink**: {linkSettings: {geometry: "Link1D"|"Link2D", type: "Rigid"|"Spring", rigidSettings: {startConnectionType: "RigidConnection"|"HingeConnection", endConnectionType: "RigidConnection"|"HingeConnection"}, springSettings: {direction: AnalyticalCoordSysDirection, translation: {kxType: AnalyticalRigidityType, ?kxValue: float, kyType: AnalyticalRigidityType, ?kyValue: float, kzType: AnalyticalRigidityType, ?kzValue: float, ?resistanceFx: bool, ?fxValue: float, ?resistanceFy: bool, ?fyValue: float, ?resistanceFz: bool, ?fzValue: float}, rotation: {kxxType: AnalyticalRigidityType, ?kxxValue: float, kyyType: AnalyticalRigidityType, ?kyyValue: float, kzzType: AnalyticalRigidityType, ?kzzValue: float, ?resistanceMx: bool, ?mxValue: float, ?resistanceMy: bool, ?myValue: float, ?resistanceMz: bool, ?mzValue: float}}}, startElementPartRef: AnalyticalMemberPartRef, endElementPartRef: AnalyticalMemberPartRef}
- **AnalyticalLinkDetails**: {link: AnalyticalLink, geometry: AnalyticalLinkGeometry}
- **AnalyticalLinkGeometry**: {coordinates: [Coordinate3D], translationStiffnessVector: Coordinate3D, rotationStiffnessVector: Coordinate3D, curves: [AnalyticalCurve]}
- **AnalyticalLoadCase**: {loadCaseId: GuidId, name: string, ?description: string, ?actionType: AnalyticalLoadCaseActionType, loadGroupId: GuidId, ?loadType: AnalyticalLoadCaseLoadType, ?duration: AnalyticalLoadCaseDuration}
- **AnalyticalLoadCaseActionType**: "PermanentAction"|"VariableAction"|"AccidentalAction"
- **AnalyticalLoadCaseData**: {name: string, ?description: string, actionType: AnalyticalLoadCaseActionType, loadGroupId: GuidId, loadType: AnalyticalLoadCaseLoadType, ?duration: AnalyticalLoadCaseDuration}
- **AnalyticalLoadCaseDuration**: "LongDuration"|"MediumDuration"|"ShortDuration"|"InstantaneousDuration"
- **AnalyticalLoadCaseIdArrayItem**: {loadCaseId: GuidId}
- **AnalyticalLoadCaseLoadType**: "SelfWeightLoad"|"PrestressLoad"|"DynamicLoad"|"StaticLoad"|"TemperatureLoad"|"WindLoad"|"SnowLoad"|"MaintenanceLoad"|"FireLoad"|"MovingLoad"|"SeismicLoad"|"StandardLoad"|"OthersLoad"
- **AnalyticalLoadCombination**: {loadCombinationId: GuidId, name: string, ?description: string, ?category: AnalyticalLoadCombinationCategory, ?nationalStandard: AnalyticalLoadCombinationNationalStandard, ?type: AnalyticalLoadCombinationType, loadFactors: [AnalyticalLoadFactor]}
- **AnalyticalLoadCombinationCategory**: "ULS"|"SLS"|"ALS"|"ANS"|"NotDefined"
- **AnalyticalLoadCombinationData**: {name: string, ?description: string, category: AnalyticalLoadCombinationCategory, ?nationalStandard: AnalyticalLoadCombinationNationalStandard, ?type: AnalyticalLoadCombinationType, ?loadFactors: [AnalyticalLoadFactor]}
- **AnalyticalLoadCombinationIdArrayItem**: {loadCombinationId: GuidId}
- **AnalyticalLoadCombinationNationalStandard**: "ENULSSTRGEOSetB"|"ENULSSTRGEOSetC"|"ENAccidental1"|"ENAccidental2"|"ENSeismic"|"ENSLSCharacteristic"|"ENSLSFrequent"|"ENSLSQuasipermanent"|"IBCLRFDultimate"|"IBCASDultimate"|"IBCASDserviceability"|"IBCASDseismic"|"IBCLRFDseismic"
- **AnalyticalLoadCombinationType**: "Envelope"|"Linear"|"Nonlinear"
- **AnalyticalLoadFactor**: {loadCaseId: GuidId, ?factor: float, multiplier: float}
- **AnalyticalLoadForceType**: "Force"|"Moment"
- **AnalyticalLoadGroup**: {loadGroupId: GuidId, name: string, ?groupType: AnalyticalLoadGroupType, ?relation: AnalyticalLoadGroupRelation, ?loadType: string}
- **AnalyticalLoadGroupData**: {name: string, groupType: AnalyticalLoadGroupType, relation: AnalyticalLoadGroupRelation, ?loadType: string}
- **AnalyticalLoadGroupIdArrayItem**: {loadGroupId: GuidId}
- **AnalyticalLoadGroupRelation**: "ExclusiveRelation"|"StandardRelation"|"TogetherRelation"
- **AnalyticalLoadGroupType**: "PermanentLoad"|"VariableLoad"|"AccidentalLoad"|"SeismicLoad"|"MovingLoad"|"TensioningLoad"|"FireLoad"
- **AnalyticalMemberConnections**: [GuidId]
- **AnalyticalMemberCoordinateSystemRequest**: {memberPartRef: AnalyticalMemberPartRef, ?intersectingMemberPartRef: AnalyticalMemberPartRef}
- **AnalyticalMemberPartRef**: {elemGuid: GuidId, partRefType: "BegVertex"|"EndVertex"|"CustomVertex"|"Edge"|"RatioEdge"|"Surface"|"CustomSurface"|"CustomEdge", ?partId: AnalyticalInternalMemberPartId, ?customVertexData: {?customVertexCoord: Coordinate3D}, ?ratioEdgeData: {?ratioStart: float, ?ratioEnd: float}}
- **AnalyticalMemberType**: "Unknown"|"Beam"|"Column"|"Roof"|"Slab"|"Wall"
- **AnalyticalModelVariation**: {?amVariationGuid: GuidId, ?renovationFilterGuid: GuidId, ?layerConnectionClassIds: [int | {layerIndex: int, connectionClassId: int}]}
- **AnalyticalNode**: {nodeId: int, coord: Coordinate3D}
- **AnalyticalPointLoad**: {loadSettings: {loadCaseId: GuidId, loadForceType: AnalyticalLoadForceType, coordinateSystemType: AnalyticalCoordSysDirection, xValue: float, yValue: float, zValue: float}, loadedMemberPartRef: AnalyticalMemberPartRef}
- **AnalyticalPointLoadDetails**: {pointLoad: AnalyticalPointLoad, geometry: {coordinate: Coordinate3D}}
- **AnalyticalRelease**: {guid: GuidId, releaseDescriptions: [{ux: AnalyticalRigidityType, ?stiffnessX: float, uy: AnalyticalRigidityType, ?stiffnessY: float, uz: AnalyticalRigidityType, ?stiffnessZ: float, fix: AnalyticalRigidityType, ?stiffnessFix: float, fiy: AnalyticalRigidityType, ?stiffnessFiy: float, fiz: AnalyticalRigidityType, ?stiffnessFiz: float, amPartRef: AnalyticalMemberPartRef}]}
- **AnalyticalRigidityType**: "Free"|"Rigid"|"Custom"|"RigidCompressionOnly"|"RigidTensionOnly"|"CustomCompressionOnly"|"CustomTensionOnly"
- **AnalyticalSegmentedSurfaceMemberDetails**: {segmentedSurfaceMembers: [AnalyticalSurfaceMember], ?idMapping: AnalyticalExportIdMapping, connections: AnalyticalMemberConnections}
- **AnalyticalSupport**: {supportSettings: {supportType: "SimplePoint"|"SingleLine"|"Surface", supportValues: {xType: AnalyticalRigidityType, ?xValue: float, yType: AnalyticalRigidityType, ?yValue: float, zType: AnalyticalRigidityType, ?zValue: float, rxType: AnalyticalRigidityType, ?rxValue: float, ryType: AnalyticalRigidityType, ?ryValue: float, rzType: AnalyticalRigidityType, ?rzValue: float}, coordinateSystem: AnalyticalCoordSysDirection}, supportedMemberPartRef: AnalyticalMemberPartRef}
- **AnalyticalSupportDetails**: {support: AnalyticalSupport, geometry: AnalyticalSupportGeometry}
- **AnalyticalSupportGeometry**: {coordinates: [Coordinate3D], translationStiffnessVector: Coordinate3D, rotationStiffnessVector: Coordinate3D}
- **AnalyticalSurfaceLoad**: {loadSettings: {loadCaseId: GuidId, coordinateSystemType: AnalyticalCoordSysDirection, xValue: float, yValue: float, zValue: float}, loadedMemberPartRef: AnalyticalMemberPartRef}
- **AnalyticalSurfaceLoadCustomData**: {contour: [AnalyticalCurve]}
- **AnalyticalSurfaceLoadDetails**: {surfaceLoad: AnalyticalSurfaceLoad, customData: AnalyticalSurfaceLoadCustomData, geometry: AnalyticalSurfaceLoadCustomData}
- **AnalyticalSurfaceMember**: {?analyticalMemberType: AnalyticalMemberType, ?elemGuid: GuidId, ?surface: {?surfaceType: "Plane"|"Cylinder", ?planeSurface: {?basePoint: Coordinate3D, ?normalVector: Coordinate3D}, ?cylinderSurface: {?basePoint: Coordinate3D, ?axisDirection: Coordinate3D, ?referenceRay: Coordinate3D}}, ?contour: [AnalyticalCurve], ?holeContours: [{contour: [AnalyticalCurve]}], ?internalNodes: [AnalyticalNode], ?thickness: float, ?lcsXVector: Coordinate3D, ?ez: float, ?ezVector: Coordinate3D, ?materialAttrIndex: int, ?layerAttrIndex: int, ?FEMType: "Plate"|"Wall"|"Shell", ?groupId: GuidId}
- **AnalyticalSurfaceMemberDetails**: {surfaceMember: AnalyticalSurfaceMember, ?idMapping: AnalyticalExportIdMapping, connections: AnalyticalMemberConnections}
- **AnalyticalVisibilitySettings**: {?visibilityMode: "AnalyticalModelOnly"|"AnalyticalModelWithinEntireModel", ?isAnalyticalModelVisible: bool, ?areMembersTransparent: bool, ?areSymbolsTransparent: bool, ?areNodesVisible: bool, ?areReleasesVisible: bool, ?areCrossSectionsVisible: bool, ?areCoordinationProfilesVisible: bool, ?areLocalCoordSystemsVisible: bool, ?loadVisibilityMode: "FilterByActive"|"HideAll"|"ShowAll"}
- **AngleType**: "DecimalDegree"|"DegreeMinSec"|"Grad"|"Radian"|"Surveyors"
- **AngleUnitFormat**: {unit: AngleType, decimals: int, accuracy: int}
- **ArcDetails**: {origin: Coordinate2D, radius: float, angle: float, ratio: float, ?begAngle: float, ?endAngle: float, reflected: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **ArcSettings**: {?origin: Coordinate2D, ?radius: float, ?angle: float, ?ratio: float, ?begAngle: float, ?endAngle: float, ?reflected: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **AreaType**: "SquareMeter"|"SquareCentimeter"|"SquareMillimeter"|"SquareFoot"|"SquareInch"
- **AssociativeWitnessPoint**: {?elementId: ElementId, ?coordinate: Coordinate2D, ?line: bool, ?inIndex: int, ?special: int, ?nodeType: int, ?nodeStatus: int, ?nodeId: float}
- **AttributeBuiltInPropertyValues**: {attributeId: AttributeId, properties: [BuiltInPropertyValue]}
- **AttributeClassification**: {attributeId: AttributeId, classificationId: ClassificationId}
- **AttributeClassifications**: {classificationIds: [ClassificationId]}
- **AttributeCreationInfo**: {method: AttributeCreationMethod, methodDescription: string, source: string, creatorUserName: string, creationTime: int}
- **AttributeCreationMethod**: "AddOn"|"Merge"|"Paste"|"New"|"Import"|"Explode"|"Duplicate"|"Hotlink"|"XRef"|"Library"|"LibraryMaster"|"Unspecified"
- **AttributeFolder**: {attributeType: AttributeType, path: [string]}
- **AttributeFolderRename**: {attributeType: AttributeType, path: [string], newName: string}
- **AttributeFolders**: [AttributeFolder]
- **AttributeHeaders**: [{attributeId: AttributeId, index: float, name: string, ?folderPath: [string], modificationTime: int, ?creationInfo: AttributeCreationInfo}]
- **AttributeHeadersOrError**: AttributeHeadersWrapper | ErrorItem
- **AttributeHeadersWrapper**: {attributes: AttributeHeaders}
- **AttributeId**: {guid: Guid}
- **AttributeIdArrayItem**: {attributeId: AttributeId}
- **AttributeIdOrError**: AttributeIdArrayItem | ErrorItem
- **AttributeIds**: [AttributeIdArrayItem]
- **AttributeIdsOrErrors**: [AttributeIdOrError]
- **AttributePropertyDefinitionFilter**: "UserDefined"|"FundamentalBuiltIn"|"All"
- **AttributePropertyIds**: {propertyIds: PropertyIds}
- **AttributePropertyValue**: {attributeId: AttributeId, propertyId: PropertyId, propertyValue: PropertyValue}
- **AttributePropertyValueStatus**: {?propertyValue: PropertyValue, isAvailable: bool, isEditable: bool, isVisible: bool}
- **AttributePropertyValues**: [AttributePropertyValue]
- **AttributePropertyValuesResult**: {propertyValues: [PropertyValueArrayItem | AttributePropertyValueStatus | ErrorItem]}
- **AttributeType**: "Layer"|"Line"|"Fill"|"Composite"|"Surface"|"LayerCombination"|"ZoneCategory"|"Profile"|"PenTable"|"MEPSystem"|"OperationProfile"|"BuildingMaterial"
- **AttributeUserData**: {pairs: UserDataPairs}
- **AutoTextKeyValue**: string
- **AutoTextName**: {name: string}
- **AutoTextNameOrError**: AutoTextName | ErrorItem
- **AutoTextNamesOrErrors**: [AutoTextNameOrError]
- **AutomaticZoneGeometry**: {referencePosition: Coordinate2D}
- **AvailableLibraryPart**: {?guid: string, ?index: int, ?documentName: string, ?fileName: string, ?typeId: LibraryPartType, ?type: "Object"|"Image"|"Text"|"BinaryListCrit"|"Other"}
- **AxonometryProjectionType**: "YZ"|"XZ"|"XY"|"Frontal"|"Monometric"|"Isometric"|"Dimetric"|"Bottom"|"FrontalBottom"|"MonometricBottom"|"IsometricBottom"|"DimetricBottom"|"Parallel"|"Custom"|"Unknown"
- **BasicDefaultValue**: {basicDefaultValue: PropertyValueDetails}
- **BeamAnchorPoint**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **BeamDetails**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, zCoordinate: float, level: float, offset: float, slantAngle: float, arcAngle: float, verticalCurveHeight: float, ?beamShape: "Straight"|"HorizontallyCurved"|"VerticallyCurved", ?isSlanted: bool, ?isFlipped: bool, ?profileAngle: float, ?anchorPoint: BeamAnchorPoint, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill, ?holes: [BeamHole], ?width: float, ?height: float, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?segments: [BeamSegmentSurfaces]}
- **BeamHole**: {holeId: float, type: BeamHoleType, ?showContour: bool, centerX: float, centerZ: float, width: float, ?height: float}
- **BeamHoleModification**: {type: BeamHoleType, ?showContour: bool, centerX: float, centerZ: float, width: float, ?height: float}
- **BeamHoleType**: "Rectangular"|"Circular"
- **BeamQuantities**: {volume: float, volumeConditional: float, holesVolume: float, area: float, leftLength: float, rightLength: float, topSurface: float, bottomSurface: float, leftSurface: float, rightSurface: float, endSurface: float, holesSurface: float, holesEdgeSurface: float, holesNumber: int, crossSectionAreaCutBegin: float, crossSectionAreaCutEnd: float}
- **BeamRelations**: {beamConnections: EndpointConnections}
- **BeamSegmentDetails**: {?ownerElementId: ElementId, structureType: SegmentStructureType, width: float, height: float, isWidthAndHeightLinked: bool, circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId}
- **BeamSegmentQuantities**: {volume: float, holesVolume: float, length: float, leftLength: float, rightLength: float, topSurface: float, bottomSurface: float, leftSurface: float, rightSurface: float, endSurface: float, holesSurface: float}
- **BeamSegmentRelations**: {beamSegmentConnections: EndpointConnections}
- **BeamSegmentSurfaces**: {leftMaterial: OverriddenMaterial, topMaterial: OverriddenMaterial, rightMaterial: OverriddenMaterial, bottomMaterial: OverriddenMaterial, endsMaterial: OverriddenMaterial, ?extrusionMaterial: OverriddenMaterial, materialsChained: bool}
- **Body3D**: {vertices: [Coordinate3D], polygons: [{vertexIds: [int], ?holes: [{vertexIds: [int]}], ?surfaceId: AttributeId}]}
- **BoundingBox2D**: {xMin: float, yMin: float, xMax: float, yMax: float}
- **BoundingBox2DArrayItem**: {boundingBox2D: BoundingBox2D}
- **BoundingBox2DOrError**: BoundingBox2DArrayItem | ErrorItem
- **BoundingBox3D**: {xMin: float, yMin: float, zMin: float, xMax: float, yMax: float, zMax: float}
- **BoundingBox3DArrayItem**: {boundingBox3D: BoundingBox3D}
- **BoundingBox3DOrError**: BoundingBox3DArrayItem | ErrorItem
- **BoundingBoxes2D**: [BoundingBox2DOrError]
- **BoundingBoxes3D**: [BoundingBox3DOrError]
- **BuildingMaterialAttribute**: {attributeId: AttributeId, index: int, name: string, ?id: string, ?manufacturer: string, ?description: string, ?connPriority: int, ?cutFillIndex: int, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutSurfaceIndex: int, ?cutFillOrientation: "ProjectOrigin"|"ElementOrigin"|"FitToSkin", ?thermalConductivity: float, ?density: float, ?heatCapacity: float, ?embodiedEnergy: float, ?embodiedCarbon: float, ?showUncutLines: bool, ?collisionDetection: bool}
- **BuildingMaterialAttributeField**: "id"|"manufacturer"|"description"|"connPriority"|"cutFillIndex"|"cutFillPen"|"cutFillBackgroundPen"|"cutSurfaceIndex"|"cutFillOrientation"|"thermalConductivity"|"density"|"heatCapacity"|"embodiedEnergy"|"embodiedCarbon"|"showUncutLines"|"collisionDetection"
- **BuildingMaterialAttributeOrError**: BuildingMaterialAttribute | ErrorItem
- **BuildingMaterialPhysicalProperties**: {thermalConductivity: float, density: float, heatCapacity: float, embodiedEnergy: float, embodiedCarbon: float}
- **BuildingMaterialPhysicalPropertiesArrayItem**: {properties: BuildingMaterialPhysicalProperties}
- **BuildingMaterialPhysicalPropertiesList**: [BuildingMaterialPhysicalPropertiesArrayItem]
- **BuiltInPropertyValue**: {propertyId: PropertyId, propertyValue: PropertyValue}
- **CalculationUnitAreaFormat**: {unit: AreaType, accuracy: AccuracyType, decimals: int}
- **CalculationUnitVolumeFormat**: {unit: VolumeType, accuracy: AccuracyType, decimals: int}
- **ChangeExecutionResult**: SuccessfulExecutionResult | WouldChangeExecutionResult | FailedExecutionResult
- **ChangeExecutionResults**: [ChangeExecutionResult]
- **ClassificationId**: {classificationSystemId: ClassificationSystemId, ?classificationItemId: ClassificationItemId}
- **ClassificationIdArrayItem**: {classificationId: ClassificationId}
- **ClassificationIdOrError**: ClassificationIdArrayItem | ErrorItem
- **ClassificationIdsOrErrors**: [ClassificationIdOrError]
- **ClassificationItemConflictPolicy**: "replace"|"skip"
- **ClassificationItemDetails**: {id: string, name: string, description: string, ?children: [ClassificationItemDetails]}
- **ClassificationItemElements**: {elements: Elements}
- **ClassificationItemId**: {guid: Guid}
- **ClassificationItemIdArrayItem**: {classificationItemId: ClassificationItemId}
- **ClassificationItemIdOrError**: ClassificationItemIdArrayItem | ErrorItem
- **ClassificationItemIds**: [ClassificationItemIdArrayItem]
- **ClassificationItemIdsOrErrors**: [ClassificationItemIdOrError]
- **ClassificationItemParent**: {classificationSystemId: ClassificationSystemId, ?parentClassificationItemId: ClassificationItemId}
- **ClassificationItemUpdate**: {classificationItemId: ClassificationItemId, ?id: string, ?name: string, ?description: string}
- **ClassificationItemVisibilities**: {visibilities: [ClassificationItemVisibility | ErrorItem]}
- **ClassificationItemVisibility**: {classificationItemId: ClassificationItemId, isVisible: bool}
- **ClassificationSystemConflictPolicy**: "merge"|"replace"|"skip"
- **ClassificationSystemDetails**: {name: string, description: string, source: string, version: string, date: Date}
- **ClassificationSystemId**: {guid: Guid}
- **ClassificationSystemIdArrayItem**: {classificationSystemId: ClassificationSystemId}
- **ClassificationSystemIdOrError**: ClassificationSystemIdArrayItem | ErrorItem
- **ClassificationSystemIds**: [ClassificationSystemIdArrayItem]
- **ClassificationSystemIdsOrErrors**: [ClassificationSystemIdOrError]
- **ClassificationSystemSummary**: {classificationSystemId: ClassificationSystemId, name: string, description: string, source: string, version: string, date: Date}
- **ClassificationSystemUpdate**: {classificationSystemId: ClassificationSystemId, ?name: string, ?description: string, ?source: string, ?version: string, ?date: Date}
- **ClassificationSystemsWithItems**: [{classificationSystem: ClassificationSystemDetails, classificationItems: [ClassificationItemDetails]}]
- **ColorRGB**: {red: float, green: float, blue: float}
- **ColumnCoreAnchor**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **ColumnDetails**: {origin: Coordinate2D, zCoordinate: float, height: float, bottomOffset: float, ?axisRotationAngle: float, ?coreAnchor: ColumnCoreAnchor, ?isSlanted: bool, ?slantAngle: float, ?slantDirectionAngle: float, ?isFlipped: bool, ?wrapping: bool, ?topOffset: float, ?relativeTopStory: float, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill, ?width: float, ?depth: float, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?segments: [ColumnSegmentSurfaces]}
- **ColumnQuantities**: {coreVolume: float, veneerVolume: float, coreGrossVolume: float, veneerGrossVolume: float, coreSurface: float, veneerSurface: float, coreGrossSurface: float, veneerGrossSurface: float, area: float, perimeter: float, minHeight: float, maxHeight: float, crossSectionAreaCutBegin: float, crossSectionAreaCutEnd: float}
- **ColumnSegmentDetails**: {?ownerElementId: ElementId, structureType: SegmentStructureType, width: float, depth: float, isWidthAndHeightLinked: bool, circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?veneer: ColumnVeneer}
- **ColumnSegmentQuantities**: {volume: float, grossVolume: float, coreVolume: float, coreGrossVolume: float, veneerVolume: float, veneerGrossVolume: float, coreSurface: float, veneerSideSurface: float, length: float, area: float, height: float, minHeight: float, maxHeight: float}
- **ColumnSegmentSurfaces**: {extrusionSurfaceMaterial: OverriddenMaterial, endsMaterial: OverriddenMaterial, materialsChained: bool, ?veneer: ColumnVeneer}
- **ColumnVeneer**: {?type: "Core"|"Finish"|"Other", ?thickness: float, ?buildingMaterialId: AttributeId}
- **ComponentId**: {guid: Guid}
- **CompositeAttribute**: {attributeId: AttributeId, index: int, name: string, ?useWith: [string], ?skins: [CompositeSkin], ?separators: [CompositeSeparator]}
- **CompositeAttributeField**: "useWith"|"skins"|"separators"
- **CompositeAttributeOrError**: CompositeAttribute | ErrorItem
- **CompositeSeparator**: {?lineTypeId: AttributeIdArrayItem, linePen: int}
- **CompositeSkin**: {type: CompositeSkinType, ?buildingMaterialId: AttributeIdArrayItem, framePen: int, thickness: float}
- **CompositeSkinType**: "Core"|"Finish"|"Other"
- **ConnectedElementsOrError**: ConnectedElementsWrapper | ErrorItem
- **ConnectedElementsWrapper**: {connectedElements: [{elements: Elements}]}
- **ConnectionItem**: {elementId: ElementId, connectedWithBeginPoint: bool}
- **ContainingDatabase**: {databaseId: DatabaseId, windowType: WindowType, name: string}
- **ConvertedUnitValue**: {convertedValue: string, extraAccuracy: string, unit: string}
- **Coordinate2D**: {x: float, y: float}
- **Coordinate3D**: {x: float, y: float, z: float}
- **CoordinateSystem3D**: {?origin: Coordinate3D, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D}
- **CoordinateWitnessPoint**: {?coordinate: Coordinate2D, ?coordinate3D: Coordinate3D, ?dimensionPosition: Coordinate2D, ?dimensionValue: float, ?witnessForm: "None"|"Small"|"Large"|"Fix"|"Unknown", ?witnessVal: float, ?baseElementId: ElementId, ?line: bool, ?inIndex: int, ?special: int, ?nodeType: int, ?nodeStatus: int, ?nodeId: float, ?textHeight: float, ?textPen: int, ?textFrame: bool}
- **CopiedLibraryPart**: {libraryPartName: string, ?unID: string, path: string}
- **CoverFill**: {use: bool, useFromSurface: bool, orientationComesFrom3D: bool, fillId: AttributeId, foregroundPen: int, backgroundPen: int, transformationType: "Global"|"Rotated"|"Distorted", transformation: CoverFillTransformation}
- **CoverFillOrientation**: {?type: HatchOrientationType, ?origo: Coordinate2D, ?matrix00: float, ?matrix10: float, ?matrix01: float, ?matrix11: float, ?innerRadius: float}
- **CoverFillTransformation**: {origin: Coordinate2D, xAxis: Coordinate2D, yAxis: Coordinate2D}
- **CreatedDatabase**: {databaseId: DatabaseId, ?navigatorItemId: NavigatorItemId}
- **CreatedProjectInfoField**: {?projectInfoId: string, ?projectInfoFieldId: ProjectInfoFieldId, projectInfoName: string, projectInfoValue: string}
- **CreatedProjectInfoFieldOrError**: CreatedProjectInfoField | ErrorItem
- **CreatedProjectInfoFieldsOrErrors**: [CreatedProjectInfoFieldOrError]
- **CriteriaPropertyObject**: {libraryPartIndex: int, ?name: string, ?guid: string}
- **CurtainWallAbsoluteBottom**: {absoluteBottom: float}
- **CurtainWallCrossingFrameType**: "None"|"FromBottomLeftToTopRight"|"FromTopLeftToBottomRight"
- **CurtainWallDetails**: {height: float, ?actualHeight: float, zCoordinate: float, referenceLine: [Coordinate2D], flipped: bool, angle: float, displayOption: DisplayOption, viewDepthLimitation: ViewDepthLimitation, visibility: StoryVisibility, isAutoOnStoryVisibility: bool, cutProjectionMode: ElemProjectionMode, uncutProjectionMode: ElemProjectionMode, overheadProjectionMode: ElemProjectionMode, cutFillPen: OverriddenPen, cutFillBackgroundPen: OverriddenPen, frameCutLinePen: int, ?frameCutLineTypeId: AttributeId, panelCutLinePen: int, ?panelCutLineTypeId: AttributeId, useFrameTypesAttributes: bool, usePanelTypesAttributes: bool, pen: int, belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId}
- **CurtainWallFrameDetails**: {?homeStoryLevel: float, begCoordinate: Coordinate3D, endCoordinate: Coordinate3D, orientationVector: Coordinate3D, panelConnectionHole: {d: float, w: float}, frameContour: {a1: float, a2: float, b1: float, b2: float}, segmentIndex: float, className: string, type: CurtainWallFrameType}
- **CurtainWallFrameType**: "Deleted"|"Division"|"Corner"|"Boundary"|"Custom"
- **CurtainWallPanelDetails**: {?homeStoryLevel: float, polygonCoordinates: [Coordinate3D], isHidden: bool, ?isDegenerate: bool, segmentIndex: float, className: string, frames: [ElementIdArrayItem]}
- **CurtainWallPattern**: {sizes: [float], ?logic: CurtainWallPatternLogic, ?origin: CurtainWallPatternOrigin, ?flexibleIndices: [int]}
- **CurtainWallPatternCell**: {columnIndex: int, rowIndex: int, ?panelClassIndex: int, ?rightPanelClassIndex: int, ?leftFrameClassIndex: int, ?bottomFrameClassIndex: int, ?crossingFrameType: CurtainWallCrossingFrameType, ?crossingFrameClassIndex: int}
- **CurtainWallPatternLogic**: "FixedSizes"|"BestDivision"
- **CurtainWallPatternOrigin**: "StartWithPattern"|"StartFromCenter"|"AlignToCenter"|"EndWithPattern"
- **CurtainWallSegmentDetails**: {begCoordinate: Coordinate3D, endCoordinate: Coordinate3D, extrusionVector: Coordinate3D, gridOrigin: Coordinate3D, gridAngle: float, ?homeStoryLevel: float, ?arcOrigin: Coordinate3D, ?isNegativeArc: bool}
- **CutPlane**: {pa: float, pb: float, pc: float, pd: float}
- **DatabaseById**: {?windowType: WindowType, databaseId: DatabaseId, ?storyIndex: int}
- **DatabaseByWindowType**: {windowType: WindowType, ?databaseId: DatabaseId, ?storyIndex: int}
- **DatabaseDetails**: {type: string, databaseId: DatabaseId, ?name: string, ?referenceId: string}
- **DatabaseId**: {guid: Guid}
- **DatabaseIdAndWindowType**: DatabaseByWindowType | DatabaseById
- **DatabaseIdArrayItem**: {databaseId: DatabaseId}
- **DatabaseIdOrError**: DatabaseIdArrayItem | ErrorItem
- **DatabaseIdsOrErrors**: [DatabaseIdOrError]
- **DatabaseType**: "Section"|"Elevation"|"InteriorElevation"|"Detail"|"Worksheet"|"DocumentFrom3D"|"Layout"|"MasterLayout"
- **Databases**: [DatabaseIdArrayItem]
- **Date**: string
- **DefaultPropertyAvailability**: {available: bool, visible: bool}
- **DeletionExecutionResult**: SuccessfulExecutionResult | WouldDeleteExecutionResult | FailedExecutionResult
- **DeletionExecutionResults**: [DeletionExecutionResult]
- **DesignOptionCombinationData**: {name: string, activeDesignOptions: [DesignOptionIdArrayItem]}
- **DesignOptionCombinationDetails**: {designOptionCombinationId: GuidId, name: string, ?activeDesignOptions: [DesignOptionIdArrayItem], ?isEditable: bool, ?notEditableError: Error}
- **DesignOptionCombinationId**: {guid: Guid}
- **DesignOptionCombinationIdArrayItem**: {designOptionCombinationId: DesignOptionCombinationId}
- **DesignOptionCombinationIdOrError**: DesignOptionCombinationIdArrayItem | ErrorItem
- **DesignOptionCombinationIdsOrErrors**: [DesignOptionCombinationIdOrError]
- **DesignOptionData**: {name: string, id: string, ownerSetName: string}
- **DesignOptionDeactivation**: {designOptionCombinationId: DesignOptionCombinationId, designOptions: [DesignOptionIdArrayItem]}
- **DesignOptionDetails**: {designOptionId: DesignOptionId, name: string, id: string, ownerSetName: string, ?isEditable: bool, ?notEditableError: Error}
- **DesignOptionId**: {guid: Guid}
- **DesignOptionIdArrayItem**: {designOptionId: DesignOptionId}
- **DesignOptionIdOrError**: DesignOptionIdArrayItem | ErrorItem
- **DesignOptionIdsOrErrors**: [DesignOptionIdOrError]
- **DesignOptionLinkType**: "NotExistingElement"|"MissingDesignOption"|"NotLinkedToAnyDesignOption"|"LinkedToDesignOption"
- **DesignOptionSetId**: {guid: Guid}
- **DesignOptionSetIdArrayItem**: {designOptionSetId: DesignOptionSetId}
- **DetailWorksheetDetails**: {basePoint: Coordinate2D, angle: float, markerId: ElementId, detailName: string, detailIdStr: string, isHorizontalMarker: bool, isWindowOpened: bool, clipPolygon: [Coordinate2D], linkData: {?referredView: ElementId, ?referredDrawing: ElementId, ?referredPMViewPoint: ElementId}}
- **DetailsOfElement**: {?elementId: ElementId, type: ElementType, id: string, floorIndex: float, layerIndex: float, drawIndex: float, ?hotlinkId: ElementId, details: TypeSpecificDetails, ?floorPlanPolygons: [{?coordinates: [Coordinate2D]}], ?infoString: string, ?compoundInfoString: string, ?libraryPartUnId: string, ?creatorToolUnId: string}
- **DimensionData**: {?elementId: ElementId, ?direction: Coordinate2D, ?dimensionLinePosition: Coordinate2D, ?appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", ?elevationOrigin: DimensionOrigin, ?witnessPoints: [CoordinateWitnessPoint], ?linePen: int, ?marker: {type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", pen: int}, ?defaultWitnessForm: "None"|"Small"|"Large"|"Fix"|"Unknown", ?defaultWitnessVal: float}
- **DimensionDataOrError**: DimensionData | ErrorItem
- **DimensionDetails**: {appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", elevationOrigin: DimensionOrigin, dimensionLinePosition: Coordinate2D, direction: Coordinate2D, witnessPointCount: int, linePen: int, marker: {type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", pen: int}, textHeight: float, textPen: int, textFrame: bool, defaultWitnessForm: "None"|"Small"|"Large"|"Fix"|"Unknown", defaultWitnessVal: float}
- **DimensionOrigin**: "ProjectZero"|"ReferenceLevel1"|"ReferenceLevel2"|"StoredOrigin"|"Altitude"
- **Dimensions3D**: {x: float, y: float, z: float}
- **DisplayOption**: "Standard"|"StandardWithAbstract"|"CutOnly"|"OutLinesOnly"|"AbstractAll"|"CutAll"
- **DisplayValueEnumId**: {type: "displayValue", displayValue: string}
- **Document3DAttributeOptions**: {?shouldUseUniformCutAttributes: bool, ?uniformLineType: int, ?uniformFillPen: int, ?uniformFillBkgPen: int, ?shouldUseUncutSurfaceFill: bool, ?uncutSurfaceBkgPen: int, ?shouldUseElemPen: bool, ?elemPen: int, ?shadFillPen: int, ?shadFill: int, ?shadFillBkgPen: int, ?shadContPen: int, ?hiddenEdgeLineType: int, ?hiddenEdgeLinePen: int}
- **Document3DBoundaryDisplay**: "UncutContours"|"NoContours"|"OverrideContours"
- **Document3DPlanConnection**: "Online"|"Offline"|"Drawing"
- **DocumentRevision**: {revisionId: DocumentRevisionId, id: string, finalId: string, ownerUser: string, status: "Actual"|"Issued", ?changes: [{id: string}], layoutInfo: LayoutInfo}
- **DocumentRevisionId**: {guid: Guid}
- **DocumentRevisionReference**: {revisionId: DocumentRevisionId}
- **DocumentRevisionReferences**: [DocumentRevisionReference]
- **DrawingAnchorPoint**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **DrawingColorMode**: "OriginalColors"|"BlackAndWhite"|"Grayscale"
- **DrawingContentBox**: {contentBox: BoundingBox2D}
- **DrawingDetails**: {pos: Coordinate2D, angle: float, ratio: float, drawingScale: float, modelOffset: Coordinate2D, isCutWithFrame: bool, bounds: BoundingBox2D, ?clipPolygon: [Coordinate2D], navigatorItemId: NavigatorItemId, nameType: DrawingNameType, ?customName: string, numberingType: DrawingNumberingType, ?customNumber: string, isInNumbering: bool, isScaleIncludedInAutotextAndIndex: bool, hasBorderLine: bool, borderLineTypeIndex: int, borderPenIndex: int, borderSize: float, penTableUsageMode: DrawingPenTableUsageMode, penTableIndex: int, colorMode: DrawingColorMode, isTransparentBackground: bool, rasterizeDPI: float, anchorPoint: DrawingAnchorPoint, useOwnOriginAsAnchor: bool, manualUpdate: bool, storedInProject: bool, ?status: DrawingStatus, ?linkType: DrawingLinkType, ?linkPath: string, titleLibraryPartIndex: float, ?titleElementId: ElementId}
- **DrawingLinkType**: "InternalView"|"ExternalView"|"Drawing"|"DXF_DWG"|"PDF"|"Image"|"PlotMaker"|"AddOn"|"Unknown"|"Other"
- **DrawingNameType**: "ViewOrSourceFileName"|"ViewIdAndName"|"CustomName"
- **DrawingNumberingGridLine**: {begC: Coordinate2D, endC: Coordinate2D, penIndex: int, lineTypeIndex: int}
- **DrawingNumberingType**: "ByLayout"|"ByViewId"|"CustomNumber"
- **DrawingPenTableUsageMode**: "OwnPenTable"|"ModelPenTable"|"PenTableIndex"
- **DrawingPrimitive**: {type: "Point"|"Line"|"Arc"|"Text"|"PLine"|"Tri"|"Poly"|"Pict"|"Ctrl_Beg"|"Ctrl_HatchBorderBeg"|"Ctrl_HatchBorderEnd"|"Ctrl_HatchLinesBeg"|"Ctrl_HatchLinesEnd"|"Ctrl_HoledimLinesBeg"|"Ctrl_HoledimLinesEnd"|"Ctrl_ArrowBeg"|"Ctrl_ArrowEnd"|"Ctrl_ElementRef"|"Ctrl_End"|"Ctrl_PlacedBorderBeg"|"Ctrl_PlacedBorderEnd"|"Ctrl_TextBeg"|"Ctrl_TextEnd"|"Ctrl_CWallPanelBeg"|"Ctrl_CWallPanelEnd"|"Ctrl_BackgroundFillBeg"|"Ctrl_BackgroundFillEnd"|"Ctrl_FrameBeg"|"Ctrl_FrameEnd"|"Unknown", ?layer: AttributeIdArrayItem, pen: int, drwIndex: int, renovationStatus: "Undefined"|"Existing"|"New"|"Demolished", ?lineType: AttributeIdArrayItem, ?determination: int, ?penWeight: float, ?solid: bool, ?loc: Coordinate2D, ?c1: Coordinate2D, ?c2: Coordinate2D, ?whole: bool, ?reflected: bool, ?orig: Coordinate2D, ?r: float, ?begAng: float, ?endAng: float, ?angle: float, ?ratio: float, ?font: int, ?faceBits: int, ?effectBits: int, ?anchor: string, ?just: string, ?heightMM: float, ?widthMM: float, ?widthFactor: float, ?charSpaceFactor: float, ?drawSegmentMode: int, ?nCoords: int, ?nSubPolys: int, ?nArcs: int, ?useRgb: bool, ?fillPen: int, ?rgbColor: {red: float, green: float, blue: float}, ?coordinates: [Coordinate2D], ?polygons: [{coordinates: [Coordinate2D]}], ?rotAngle: float, ?destBox: {xMin: float, yMin: float, xMax: float, yMax: float}, ?hatchBorder: {doFrame: bool, ?fill: AttributeIdArrayItem, fillPen: int, fillbkgPen: int, determination: int}, ?referencedElement: {elementId: ElementId, type: ElementType, drwIndex: int}}
- **DrawingSettings**: {?pos: Coordinate2D, ?angle: float, ?ratio: float, ?drawingScale: float, ?modelOffset: Coordinate2D, ?isCutWithFrame: bool, ?clipPolygon: [Coordinate2D], ?nameType: DrawingNameType, ?customName: string, ?numberingType: DrawingNumberingType, ?customNumber: string, ?isInNumbering: bool, ?isScaleIncludedInAutotextAndIndex: bool, ?hasBorderLine: bool, ?borderLineTypeIndex: int, ?borderPenIndex: int, ?borderSize: float, ?titleLibraryPartIndex: float, ?penTableUsageMode: DrawingPenTableUsageMode, ?penTableIndex: int, ?colorMode: DrawingColorMode, ?isTransparentBackground: bool, ?rasterizeDPI: float, ?anchorPoint: DrawingAnchorPoint, ?useOwnOriginAsAnchor: bool}
- **DrawingStatus**: "UpToDate"|"Modified"|"Unknown"
- **DryRun**: bool
- **DryRunFlag**: true
- **EditModeStateItem**: {inEditMode: bool, ?elementId: ElementId}
- **ElectricalCircuitConnectionData**: {elementId: ElementId, circuitId: ElementId}
- **ElectricalCircuitData**: {electricalPanelId: ElementId, ?description: string, ?voltage: float, ?wiringTypeName: string, ?isPhaseAUsed: bool, ?isPhaseBUsed: bool, ?isPhaseCUsed: bool}
- **ElectricalCircuitDetails**: {elementId: ElementId, name: string, description: string, ownerPanelId: ElementId, childDevices: Elements, childPanels: Elements, voltage: float, phases: string, isPhaseAUsed: bool, isPhaseBUsed: bool, isPhaseCUsed: bool, wiringTypeName: string, connectedLoad: ElectricalLoads, demandLoad: ElectricalLoads, voltageDrop: float, estimatedCableLength: float}
- **ElectricalCircuitDetailsOrError**: ElectricalCircuitDetails | ErrorItem
- **ElectricalCircuitModificationData**: {elementId: ElementId, ?description: string, ?voltage: float, ?wiringTypeName: string, ?isPhaseAUsed: bool, ?isPhaseBUsed: bool, ?isPhaseCUsed: bool}
- **ElectricalDeviceData**: {position: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float, ?apparentPower: int, ?isApparentPowerEnabled: bool, ?loadClassificationName: string, ?circuitId: ElementId}
- **ElectricalDeviceDetails**: {elementId: ElementId, ?parentCircuitId: ElementId, anchorPoint: Coordinate3D, orientation: MEPOrientation, rotation: float, isReflected: bool, libraryPartId: LibPartUnId, xSize: float, ySize: float, apparentPower: float, isApparentPowerEnabled: bool, loadClassificationName: string, demandLoad: float, connectedElements: Elements}
- **ElectricalDeviceDetailsOrError**: ElectricalDeviceDetails | ErrorItem
- **ElectricalDeviceModificationData**: {elementId: ElementId, ?apparentPower: int, ?isApparentPowerEnabled: bool, ?loadClassificationName: string, ?anchorPoint: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float}
- **ElectricalLoadClassification**: {name: string, demandFactor: float}
- **ElectricalLoads**: {total: float, phaseA: float, phaseB: float, phaseC: float}
- **ElectricalPanelData**: {position: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float, ?panelName: string, ?circuitNamePrefix: string, ?circuitIdStyle: int}
- **ElectricalPanelDetails**: {elementId: ElementId, panelName: string, circuitNamePrefix: string, circuitIdStyle: int, circuits: Elements, ?parentCircuitId: ElementId, anchorPoint: Coordinate3D, orientation: MEPOrientation, rotation: float, isReflected: bool, libraryPartId: LibPartUnId, xSize: float, ySize: float, connectedLoad: ElectricalLoads, demandLoad: ElectricalLoads}
- **ElectricalPanelDetailsOrError**: ElectricalPanelDetails | ErrorItem
- **ElectricalPanelModificationData**: {elementId: ElementId, ?panelName: string, ?circuitNamePrefix: string, ?circuitIdStyle: int, ?anchorPoint: Coordinate3D, ?orientation: MEPOrientation, ?rotation: float, ?isReflected: bool, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float}
- **ElectricalPanelToolDefaults**: {libraryPartId: LibPartUnId, panelName: string, circuitNamePrefix: string, circuitIdStyle: int, circuitDefaultCount: int}
- **ElectricalWiringType**: {name: string, crossSectionalArea: float}
- **ElemProjectionMode**: "Symbolic"|"Projected"|"Hybrid"
- **ElementAnalyticalRelease**: {elementId: ElementId, release: AnalyticalRelease}
- **ElementCategoryDetails**: {categoryId: ElementCategoryId, type: ElementCategoryType, name: string, values: [ElementCategoryValueDetails]}
- **ElementCategoryId**: {guid: Guid}
- **ElementCategoryType**: "StructuralFunction"|"Position"|"RenovationStatus"|"RenovationFilter"|"BRI"
- **ElementCategoryValue**: {type: ElementCategoryType, categoryId: ElementCategoryId, categoryValueId: ElementCategoryValueId, name: string}
- **ElementCategoryValueData**: {elementId: ElementId, type: ElementCategoryType, categoryValueId: ElementCategoryValueId}
- **ElementCategoryValueDetails**: {categoryValueId: ElementCategoryValueId, name: string, isVisibleOnUI: bool, usableAsCriteria: bool}
- **ElementCategoryValueId**: {guid: Guid}
- **ElementCategoryValues**: {categoryValues: [ElementCategoryValue]}
- **ElementClassification**: {elementId: ElementId, classificationId: ClassificationId}
- **ElementClassificationItemArray**: {classificationIds: [ClassificationId | ErrorItem]}
- **ElementClassificationOrError**: ElementClassificationItemArray | ErrorItem
- **ElementClassifications**: [ElementClassification]
- **ElementClassificationsOrErrors**: [ElementClassificationOrError]
- **ElementComponentId**: {elementId: ElementId, componentId: ComponentId}
- **ElementComponentIdArrayItem**: {elementComponentId: ElementComponentId}
- **ElementComponents**: [ElementComponentIdArrayItem]
- **ElementComponentsArrayItem**: {elementComponents: ElementComponents}
- **ElementComponentsOrError**: ElementComponentsArrayItem | ErrorItem
- **ElementComponentsOrErrorArray**: [ElementComponentsOrError]
- **ElementConvexPolygons**: {convexPolygons: [{vertices: [Coordinate3D]}]}
- **ElementDefaultClassification**: {elementType: ElementType, classificationId: ClassificationId}
- **ElementDescriptor**: {libraryPartIndex: int, ?name: string, ?guid: string, setIndex: int, index: int, status: ElementDescriptorStatus}
- **ElementDescriptorStatus**: "Normal"|"Deleted"|"Local"|"Unknown"
- **ElementDescriptors**: {descriptors: [ElementDescriptor]}
- **ElementDetailsAdditionalField**: "infoString"|"compoundInfoString"|"libraryPartUnId"|"creatorToolUnId"
- **ElementDetailsField**: "elementId"|"type"|"id"|"floorIndex"|"layerIndex"|"drawIndex"|"details"|"floorPlanPolygons"|"hotlinkId"
- **ElementDrawingPrimitives**: {primitives: [DrawingPrimitive]}
- **ElementFilter**: "IsEditable"|"IsVisibleByLayer"|"IsVisibleByRenovation"|"IsVisibleByStructureDisplay"|"IsVisibleIn3D"|"OnActualFloor"|"OnActualLayout"|"InMyWorkspace"|"IsIndependent"|"InCroppedView"|"HasAccessRight"|"IsOverriddenByRenovation"|"IncludeSubElemObjects"
- **ElementFromAnalyticalMember**: {elementId: ElementId, ?idMapping: AnalyticalImportIdMapping}
- **ElementFromAnalyticalMemberData**: any | any | any
- **ElementGeometry3D**: {bodies: [Body3D]}
- **ElementGroupParameters**: {elements: ElementOrGroupIds, ?parentGroupId: GroupId}
- **ElementHeaderFromOtherDatabase**: {?elementId: ElementId, ?type: ElementType, ?floorIndex: float, ?layerIndex: float, ?drawIndex: float, ?hotlinkId: ElementId, fromOtherDatabase: bool}
- **ElementIFCAttribute**: {name: string, valueType: string, ?value: string}
- **ElementIFCAttributeValue**: {elementId: ElementId, name: string, value: string}
- **ElementIFCAttributes**: {elementId: ElementId, ifcAttributes: [ElementIFCAttribute]}
- **ElementIFCAttributesOrError**: ElementIFCAttributes | ErrorItem
- **ElementIFCAttributesOrErrors**: [ElementIFCAttributesOrError]
- **ElementIFCClassificationReference**: {?identification: string, ?name: string, ?location: string, ?description: string, ?sort: string, ?relAssociatesClassificationName: string, referencedSource: {name: string, ?source: string, ?edition: string, ?editionDate: string, ?description: string, ?location: string}, ?source: "preview"|"local"}
- **ElementIFCClassificationReferenceRemoval**: {elementId: ElementId, referencedSource: {name: string}, ?identification: string}
- **ElementIFCClassificationReferenceUpdate**: {elementId: ElementId, ?identification: string, ?name: string, ?location: string, referencedSource: {name: string, ?edition: string, ?editionDate: string, ?description: string, ?location: string}}
- **ElementIFCClassificationReferences**: {elementId: ElementId, ifcClassificationReferences: [ElementIFCClassificationReference]}
- **ElementIFCClassificationReferencesOrError**: ElementIFCClassificationReferences | ErrorItem
- **ElementIFCClassificationReferencesOrErrors**: [ElementIFCClassificationReferencesOrError]
- **ElementIFCIds**: {elementId: ElementId, ifcId: string, externalIFCId: string, ?ifcGlobalId: string, ?externalIFCGlobalId: string}
- **ElementIFCIdsOrError**: ElementIFCIds | ErrorItem
- **ElementIFCIdsOrErrors**: [ElementIFCIdsOrError]
- **ElementIFCProperties**: {elementId: ElementId, ifcProperties: [ElementIFCProperty]}
- **ElementIFCPropertiesOrError**: ElementIFCProperties | ErrorItem
- **ElementIFCPropertiesOrErrors**: [ElementIFCPropertiesOrError]
- **ElementIFCProperty**: {propertySetName: string, name: string, value: string, ?valueType: string, ?propertyType: IFCPropertyType, ?enumerationReference: [string], ?source: IFCPropertySource}
- **ElementIFCPropertyRemoval**: {elementId: ElementId, propertySetName: string, propertyName: string}
- **ElementIFCPropertyValue**: {elementId: ElementId, propertySetName: string, propertyName: string, type: string, value: any}
- **ElementIFCType**: {elementId: ElementId, ifcType: string, typeObjectIFCType: string}
- **ElementIFCTypeOrError**: ElementIFCType | ErrorItem
- **ElementIFCTypesOrErrors**: [ElementIFCTypeOrError]
- **ElementId**: {guid: Guid}
- **ElementIdArrayItem**: {elementId: ElementId}
- **ElementIdOrError**: ElementIdArrayItem | ErrorItem
- **ElementIdsOrErrors**: [ElementIdOrError]
- **ElementInfoString**: {elementId: ElementId, infoString: string}
- **ElementLibraryPartTransformation**: {transformation: {location: Coordinate2D, angle: float, xRatio: float, yRatio: float}}
- **ElementLinkData**: {fromElementId: ElementId, toElementId: ElementId, ?flags: int}
- **ElementLinkDetails**: {elementId: ElementId, flags: int}
- **ElementLinkReference**: {fromElementId: ElementId, toElementId: ElementId}
- **ElementLinkedPropertyObjects**: {linkByCriteria: bool, individualLibraryPartIndex: int, ?individualLibraryPartName: string, ?individualLibraryPartGuid: string, criteriaPropertyObjects: [CriteriaPropertyObject]}
- **ElementLinks**: {links: [ElementLinkDetails]}
- **ElementLinksOrError**: ElementLinks | ErrorItem
- **ElementMEPRoutingParameters**: {elementId: ElementId, ?routingNodeParameters: MEPRoutingNodeParametersUpdate, ?routingSegmentParameters: MEPRoutingSegmentDefaults, ?elbowParameters: MEPElbowParameters, ?transitionParameters: MEPTransitionDefaults}
- **ElementMirrorData**: {elementId: ElementId, mirrorAxis: {beginPoint: Coordinate2D, endPoint: Coordinate2D}, ?copy: bool}
- **ElementOrGroupId**: ElementIdArrayItem | GroupIdArrayItem
- **ElementOrGroupIds**: [ElementOrGroupId]
- **ElementPropertyObject**: {libraryPartIndex: int, ?name: string, ?guid: string, isIndividuallyAssigned: bool}
- **ElementPropertyObjects**: {propertyObjects: [ElementPropertyObject]}
- **ElementPropertyValue**: any | any
- **ElementPropertyValues**: [ElementPropertyValue]
- **ElementQuantities**: WallQuantities | ColumnQuantities | BeamQuantities | SlabQuantities | RoofQuantities | ShellQuantities | MorphQuantities | ZoneQuantities | ColumnSegmentQuantities | BeamSegmentQuantities
- **ElementQuantityDetails**: {type: ElementType, quantities: ElementQuantities, composites: [{buildingMaterialId: AttributeIdArrayItem, volume: float, projectedArea: float, isCore: bool, isFinish: bool, ?subElementId: ElementId}]}
- **ElementRelationsOrError**: WallRelations | BeamRelations | BeamSegmentRelations | ZoneRelationsOfElement | OpeningRelationsOfElement | RoofOrShellRelationsOfElement | ErrorItem
- **ElementReservationState**: "Free"|"Editable"|"Locked"
- **ElementReservationStatus**: {status: ElementReservationState, ?reservedBy: User, ?owner: User}
- **ElementSetsOfElement**: {elementSets: [{elementSetId: {guid: Guid}}]}
- **ElementSurfaceQuantities**: {surfaces: [ElementSurfaceQuantity]}
- **ElementSurfaceQuantity**: {?surfaceId: AttributeIdArrayItem, buildingMaterialId: AttributeIdArrayItem, exposedArea: float}
- **ElementTextureCoordinates**: {bodies: [{polygons: [{point: Coordinate3D, u: float, v: float} | ErrorItem]} | ErrorItem]}
- **ElementTriangulation**: {triangles: [{vertices: [Coordinate2D]}]}
- **ElementTrims**: {trimmedBy: [{elementId: ElementId, trimType: TrimType}], trims: Elements}
- **ElementTrimsOrError**: ElementTrims | ErrorItem
- **ElementType**: "Wall"|"Column"|"Beam"|"Window"|"Door"|"Object"|"Lamp"|"Slab"|"Roof"|"Mesh"|"Dimension"|"RadialDimension"|"LevelDimension"|"AngleDimension"|"Text"|"Label"|"Zone"|"Hatch"|"Line"|"PolyLine"|"Arc"|"Circle"|"Spline"|"Hotspot"|"CutPlane"|"Camera"|"CamSet"|"Group"|"SectElem"|"Drawing"|"Picture"|"Detail"|"Elevation"|"InteriorElevation"|"Worksheet"|"Hotlink"|"CurtainWall"|"CurtainWallSegment"|"CurtainWallFrame"|"CurtainWallPanel"|"CurtainWallJunction"|"CurtainWallAccessory"|"Shell"|"Skylight"|"Morph"|"ChangeMarker"|"Stair"|"Riser"|"Tread"|"StairStructure"|"Railing"|"RailingToprail"|"RailingHandrail"|"RailingRail"|"RailingPost"|"RailingInnerPost"|"RailingBaluster"|"RailingPanel"|"RailingSegment"|"RailingNode"|"RailingBalusterSet"|"RailingPattern"|"RailingToprailEnd"|"RailingHandrailEnd"|"RailingRailEnd"|"RailingToprailConnection"|"RailingHandrailConnection"|"RailingRailConnection"|"RailingEndFinish"|"BeamSegment"|"ColumnSegment"|"Opening"|"Unknown"
- **ElementTypeFloorLayerFilter**: {?types: [ElementType], ?floorIndices: [int], ?layerIndices: [int]}
- **ElementTypeName**: {elementType: ElementType, name: string}
- **Elements**: [ElementIdArrayItem]
- **ElementsByIFCIds**: [{ifcId: string, elements: [ElementIdArrayItem]}]
- **ElementsOfDesignOption**: {designOptionId: DesignOptionId, elements: Elements}
- **ElementsOfDesignOptionOrError**: ElementsOfDesignOption | ErrorItem
- **ElementsOfElementType**: {elementType: ElementType, elements: Elements}
- **ElementsWithExecutionResults**: {elements: Elements, ?executionResultForDatabases: ExecutionResults}
- **ElementsWithExecutionResultsOrError**: ElementsWithExecutionResults | ErrorItem
- **ElementsWrapper**: {elements: Elements}
- **ElementsWrapperOrError**: ElementsWrapper | ErrorItem
- **EmbeddedLibraryFile**: {path: string}
- **EmbeddedLibraryItem**: {path: string}
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
- **FavoriteContents**: {name: string, folderPath: [string], classifications: ClassificationIdsOrErrors, categoryValues: [{type: ElementCategoryType, categoryId: ElementCategoryId, categoryValueId: ElementCategoryValueId, name: string}], properties: [{propertyId: PropertyId, ?propertyValue: PropertyValue, ?error: Error}]}
- **FavoriteCreationConflictPolicy**: "Error"|"Skip"|"OverwriteExisting"|"RenameNew"
- **FavoriteCreationOutcome**: "Created"|"Skipped"|"Overwritten"
- **FavoriteDefaults**: {favorite: string, elementType: ElementType, layerIndex: int, ?elementId: string, ?folder: [string], ?libPart: LibPartDetails, parameters: [StoredGDLParameter], ?marker: {elementType: ElementType, ?libPart: LibPartDetails, parameters: [StoredGDLParameter]}, subElements: [{elementType: ElementType, ?libPart: LibPartDetails, parameters: [StoredGDLParameter], subTypes: ["MainMarker"|"SHMarker"|"CommonMarker"|"CWFrameClass"|"CWPanelClass"|"CWJunction"|"CWAccessory"|"StairRiser"|"StairTread"|"StairStructure"|"StairFPDMarker"|"StairRCPDMarker"|"RailingNode"|"RailingSegment"|"RailingPost"|"RailingInnerPost"|"RailingRail"|"RailingHandrail"|"RailingToprail"|"RailingPanel"|"RailingBaluster"|"RailingPattern"|"RailingBalusterSet"|"RailingRailEnd"|"RailingHandrailEnd"|"RailingToprailEnd"|"RailingRailConnection"|"RailingHandrailConnection"|"RailingToprailConnection"|"RailingFinish"|"CWTag"|"NoElem"|"NoParams"]}]}
- **FavoriteDetails**: {favorite: string, elementType: string, classifications: [ClassificationIdArrayItem], properties: [{propertyId: PropertyId, propertyName: string, status: "HasValue"|"NotEvaluated"|"NotAvailable", isDefault: bool, ?propertyValue: PropertyValue, ?error: Error}], categoryValues: [{categoryId: GuidId, categoryName: string, categoryValueId: GuidId, categoryValueName: string}]}
- **FavoriteExportFormat**: "prefs"|"xml"|"legacyPRF"
- **FavoriteFileEntry**: {name: string, elementType: ElementType, folder: [string]}
- **FavoriteFolderDetails**: {name: string, path: [string], favorites: [string], subFolders: [FavoriteFolderDetails]}
- **FavoriteFromElement**: {elementId: ElementId, favorite: string, ?folder: [string]}
- **FavoriteImportConflictPolicy**: "Error"|"Skip"|"Overwrite"|"Append"|"OverwriteExisting"|"RenameNew"
- **FavoriteImportFormat**: "prefs"|"xml"|"legacyPRF"
- **FavoriteKeepField**: "id"|"layerIndex"|"width"|"height"|"sillHeight"|"referenceLineLocation"|"topOffset"|"relativeTopStory"
- **FavoriteNameAndFolder**: {name: string, ?folderPath: [string]}
- **FavoriteRename**: {oldName: string, newName: string}
- **FavoriteSettings**: {favorite: string, elementType: ElementType, ?folder: [string], ?libPart: LibPartDetails, parameters: [StoredGDLParameter], ?marker: {?libPart: LibPartDetails, parameters: [StoredGDLParameter]}, subElements: [FavoriteSubelement]}
- **FavoriteSettingsSource**: {?favoriteName: string, ?toolDefault: "Opening"}
- **FavoriteSubelement**: {subType: FavoriteSubelementType, elementType: ElementType, ?libPart: LibPartDetails, parameters: [StoredGDLParameter]}
- **FavoriteSubelementType**: "MainMarker"|"Other"
- **FavoriteSummary**: {name: string, ?elementType: ElementType, ?folder: [string]}
- **FavoriteToApply**: {elementId: ElementId, favorite: string}
- **Favorites**: [string]
- **FavoritesFromElementUpdate**: {elementId: ElementId, favorite: string}
- **FavoritesOrError**: FavoritesWrapper | ErrorItem
- **FavoritesWrapper**: {favorites: Favorites}
- **FillAttribute**: {attributeId: AttributeId, index: int, name: string, ?subType: FillSubType, ?scaleWithPlan: bool, ?useForWalls: bool, ?useForDraft: bool, ?useForCover: bool, ?horizontalSpacing: float, ?verticalSpacing: float, ?angle: float, ?bitPattern: string, ?gradientStart: Coordinate2D, ?gradientEnd: Coordinate2D, ?symbolOffset1: Coordinate2D, ?symbolOffset2: Coordinate2D, ?percent: float, ?texture: Texture, ?lineItems: [FillLineItem], ?symbolLines: [FillSymbolLine], ?symbolArcs: [FillSymbolArc], ?symbolHotspots: [Coordinate2D], ?symbolSolidFills: [FillSymbolSolidFill]}
- **FillAttributeField**: "subType"|"scaleWithPlan"|"useForWalls"|"useForDraft"|"useForCover"|"horizontalSpacing"|"verticalSpacing"|"angle"|"bitPattern"|"gradientStart"|"gradientEnd"|"symbolOffset1"|"symbolOffset2"|"percent"|"texture"|"lineItems"|"symbolLines"|"symbolArcs"|"symbolHotspots"|"symbolSolidFills"
- **FillAttributeOrError**: FillAttribute | ErrorItem
- **FillLineItem**: {frequency: float, direction: float, offsetLine: float, offset: Coordinate2D, ?lineLengths: [float]}
- **FillSubType**: "Vector"|"Solid"|"Empty"|"Symbol"|"LinearGradient"|"RadialGradient"
- **FillSymbolArc**: {begin: Coordinate2D, origin: Coordinate2D, angle: float}
- **FillSymbolLine**: {begin: Coordinate2D, end: Coordinate2D}
- **FillSymbolSolidFill**: {coordinates: [Coordinate2D], subPolygons: [int], ?arcs: [PolyArc]}
- **FloorFill**: {?use: bool, ?foregroundPen: int, ?backgroundPen: int, ?fillId: AttributeId, ?use3DHatching: bool, ?orientation: HatchOrientation}
- **FontDetails**: {fontIndex: int, fontName: string}
- **FoundLibraryPart**: {?name: string, ?path: string, ?index: int}
- **GDLParameterArray**: [GDLParameterDetails]
- **GDLParameterDetails**: {name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, value: any, ?valueDescription: string, isLocked: bool, flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"], ?possibleValues: PossibleStringValues | PossibleNumericValues, ?canHaveCustomValue: bool, ?itemDescriptions: [string]}
- **GDLParameterList**: {parameters: GDLParameterArray}
- **GeoReferencingParameters**: {crsName: string, description: string, geodeticDatum: string, verticalDatum: string, mapProjection: string, mapZone: string, xAxisAbscissa: float, xAxisOrdinate: float, scale: float}
- **GeoReferencingParametersUpdate**: {?crsName: string, ?description: string, ?geodeticDatum: string, ?verticalDatum: string, ?mapProjection: string, ?mapZone: string, ?xAxisAbscissa: float, ?xAxisOrdinate: float, ?scale: float}
- **GraphicOverrideCombinationId**: {guid: Guid}
- **GraphicOverrideCombinationIdArrayItem**: {graphicOverrideCombinationId: GraphicOverrideCombinationId}
- **GraphicOverrideCombinationIdOrError**: GraphicOverrideCombinationIdArrayItem | ErrorItem
- **GraphicOverrideCriterion**: {?and: [GraphicOverrideCriterion], ?or: [GraphicOverrideCriterion], ?criterionXML: string, ?elementType: GraphicOverrideElementType, ?elementTypeNot: GraphicOverrideElementType, ?libraryPartSubtype: {mainGuid: string, revGuid: string}, ?classification: string, ?classificationNot: string, ?classificationSystem: string, ?all3DTypes: bool, ?all2DTypes: bool, ?missingAttributes: bool, ?missingLibraryPart: bool, ?layer: string, ?layerNot: string, ?layerLocked: bool, ?layerVisible: bool, ?layerCombination: string, ?layerCombinationNot: string, ?layerNameIs: string, ?layerNameIsNot: string, ?layerNameContains: string, ?layerNameNotContains: string, ?layerNameStartsWith: string, ?layerNameEndsWith: string, ?compositeStructure: string, ?compositeStructureNot: string, ?complexProfile: string, ?complexProfileNot: string, ?compositeStructureNameIs: string, ?compositeStructureNameIsNot: string, ?compositeStructureNameContains: string, ?compositeStructureNameNotContains: string, ?compositeStructureNameStartsWith: string, ?compositeStructureNameEndsWith: string, ?complexProfileNameIs: string, ?complexProfileNameIsNot: string, ?complexProfileNameContains: string, ?complexProfileNameNotContains: string, ?complexProfileNameStartsWith: string, ?complexProfileNameEndsWith: string, ?roofConnected: bool, ?structureType: "Basic"|"Composite"|"ComplexProfile", ?seaLevelAltitude: float, ?seaLevelAltitudeNot: float, ?seaLevelAltitudeLessThan: float, ?seaLevelAltitudeGreaterThan: float, ?seaLevelAltitudeLessOrEqual: float, ?seaLevelAltitudeGreaterOrEqual: float, ?projectZeroAltitude: float, ?projectZeroAltitudeNot: float, ?projectZeroAltitudeLessThan: float, ?projectZeroAltitudeGreaterThan: float, ?projectZeroAltitudeLessOrEqual: float, ?projectZeroAltitudeGreaterOrEqual: float, ?groundFloorAltitude: float, ?groundFloorAltitudeNot: float, ?groundFloorAltitudeLessThan: float, ?groundFloorAltitudeGreaterThan: float, ?groundFloorAltitudeLessOrEqual: float, ?groundFloorAltitudeGreaterOrEqual: float, ?roofAltitude: float, ?roofAltitudeNot: float, ?roofAltitudeLessThan: float, ?roofAltitudeGreaterThan: float, ?roofAltitudeLessOrEqual: float, ?roofAltitudeGreaterOrEqual: float, ?floorIndex: int, ?sillHeight: float, ?sillHeightNot: float, ?sillHeightLessThan: float, ?sillHeightGreaterThan: float, ?sillHeightLessOrEqual: float, ?sillHeightGreaterOrEqual: float, ?lintelHeight: float, ?lintelHeightNot: float, ?lintelHeightLessThan: float, ?lintelHeightGreaterThan: float, ?lintelHeightLessOrEqual: float, ?lintelHeightGreaterOrEqual: float, ?screedThickness: float, ?screedThicknessNot: float, ?screedThicknessLessThan: float, ?screedThicknessGreaterThan: float, ?screedThicknessLessOrEqual: float, ?screedThicknessGreaterOrEqual: float, ?linkedUpperStoryAbsolute: int, ?linkedUpperStoryRelative: int, ?mepDiameter: float, ?mepDiameterNot: float, ?mepDiameterLessThan: float, ?mepDiameterGreaterThan: float, ?mepDiameterLessOrEqual: float, ?mepDiameterGreaterOrEqual: float, ?mepDiameter2: float, ?mepDiameter2Not: float, ?mepDiameter2LessThan: float, ?mepDiameter2GreaterThan: float, ?mepDiameter2LessOrEqual: float, ?mepDiameter2GreaterOrEqual: float, ?mepDN: int, ?mepDNNot: int, ?mepDNLessThan: int, ?mepDNGreaterThan: int, ?mepDNLessOrEqual: int, ?mepDNGreaterOrEqual: int, ?mepDN2: int, ?mepDN2Not: int, ?mepDN2LessThan: int, ?mepDN2GreaterThan: int, ?mepDN2LessOrEqual: int, ?mepDN2GreaterOrEqual: int, ?mepHeight: float, ?mepHeightNot: float, ?mepHeightLessThan: float, ?mepHeightGreaterThan: float, ?mepHeightLessOrEqual: float, ?mepHeightGreaterOrEqual: float, ?mepHeight2: float, ?mepHeight2Not: float, ?mepHeight2LessThan: float, ?mepHeight2GreaterThan: float, ?mepHeight2LessOrEqual: float, ?mepHeight2GreaterOrEqual: float, ?mepWidth: float, ?mepWidthNot: float, ?mepWidthLessThan: float, ?mepWidthGreaterThan: float, ?mepWidthLessOrEqual: float, ?mepWidthGreaterOrEqual: float, ?mepWidth2: float, ?mepWidth2Not: float, ?mepWidth2LessThan: float, ?mepWidth2GreaterThan: float, ?mepWidth2LessOrEqual: float, ?mepWidth2GreaterOrEqual: float, ?mepAngle: float, ?mepAngleNot: float, ?mepAngleLessThan: float, ?mepAngleGreaterThan: float, ?mepAngleLessOrEqual: float, ?mepAngleGreaterOrEqual: float, ?mepCustomAngle: float, ?mepCustomAngleNot: float, ?mepCustomAngleLessThan: float, ?mepCustomAngleGreaterThan: float, ?mepCustomAngleLessOrEqual: float, ?mepCustomAngleGreaterOrEqual: float, ?mepInsulationThickness: float, ?mepInsulationThicknessNot: float, ?mepInsulationThicknessLessThan: float, ?mepInsulationThicknessGreaterThan: float, ?mepInsulationThicknessLessOrEqual: float, ?mepInsulationThicknessGreaterOrEqual: float, ?mepLength: float, ?mepLengthNot: float, ?mepLengthLessThan: float, ?mepLengthGreaterThan: float, ?mepLengthLessOrEqual: float, ?mepLengthGreaterOrEqual: float, ?mepDescriptionIs: string, ?mepDescriptionIsNot: string, ?mepDescriptionContains: string, ?mepDescriptionNotContains: string, ?mepDescriptionStartsWith: string, ?mepDescriptionEndsWith: string, ?mepMaterialNameIs: string, ?mepMaterialNameIsNot: string, ?mepMaterialNameContains: string, ?mepMaterialNameNotContains: string, ?mepMaterialNameStartsWith: string, ?mepMaterialNameEndsWith: string, ?wallComplexity: "Straight"|"Slanted"|"DoubleSlanted", ?wallComplexityNot: "Straight"|"Slanted"|"DoubleSlanted", ?wallLevelOffset: float, ?wallLevelOffsetNot: float, ?wallLevelOffsetLessThan: float, ?wallLevelOffsetGreaterThan: float, ?wallLevelOffsetLessOrEqual: float, ?wallLevelOffsetGreaterOrEqual: float, ?wallTopOffset: float, ?wallTopOffsetNot: float, ?wallTopOffsetLessThan: float, ?wallTopOffsetGreaterThan: float, ?wallTopOffsetLessOrEqual: float, ?wallTopOffsetGreaterOrEqual: float, ?wallReferenceLinePosition: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside", ?wallReferenceLinePositionNot: "Outside"|"Center"|"Inside"|"CoreOutside"|"CoreCenter"|"CoreInside", ?wallOutsideAngle: float, ?wallOutsideAngleNot: float, ?wallOutsideAngleLessThan: float, ?wallOutsideAngleGreaterThan: float, ?wallOutsideAngleLessOrEqual: float, ?wallOutsideAngleGreaterOrEqual: float, ?wallInsideAngle: float, ?wallInsideAngleNot: float, ?wallInsideAngleLessThan: float, ?wallInsideAngleGreaterThan: float, ?wallInsideAngleLessOrEqual: float, ?wallInsideAngleGreaterOrEqual: float, ?wallThickness: float, ?wallThicknessNot: float, ?wallThicknessLessThan: float, ?wallThicknessGreaterThan: float, ?wallThicknessLessOrEqual: float, ?wallThicknessGreaterOrEqual: float, ?wallHeight: float, ?wallHeightNot: float, ?wallHeightLessThan: float, ?wallHeightGreaterThan: float, ?wallHeightLessOrEqual: float, ?wallHeightGreaterOrEqual: float, ?wallProfileHeight: float, ?wallProfileHeightNot: float, ?wallProfileHeightLessThan: float, ?wallProfileHeightGreaterThan: float, ?wallProfileHeightLessOrEqual: float, ?wallProfileHeightGreaterOrEqual: float, ?wallHeightReversed: bool, ?wallWidth: float, ?wallWidthNot: float, ?wallWidthLessThan: float, ?wallWidthGreaterThan: float, ?wallWidthLessOrEqual: float, ?wallWidthGreaterOrEqual: float, ?wallProfileWidth: float, ?wallProfileWidthNot: float, ?wallProfileWidthLessThan: float, ?wallProfileWidthGreaterThan: float, ?wallProfileWidthLessOrEqual: float, ?wallProfileWidthGreaterOrEqual: float, ?objectLength: float, ?objectLengthNot: float, ?objectLengthLessThan: float, ?objectLengthGreaterThan: float, ?objectLengthLessOrEqual: float, ?objectLengthGreaterOrEqual: float, ?jambThickness1: float, ?jambThickness1Not: float, ?jambThickness1LessThan: float, ?jambThickness1GreaterThan: float, ?jambThickness1LessOrEqual: float, ?jambThickness1GreaterOrEqual: float, ?jambThickness2: float, ?jambThickness2Not: float, ?jambThickness2LessThan: float, ?jambThickness2GreaterThan: float, ?jambThickness2LessOrEqual: float, ?jambThickness2GreaterOrEqual: float, ?curtainWallPanelOffset: float, ?curtainWallPanelOffsetNot: float, ?curtainWallPanelOffsetLessThan: float, ?curtainWallPanelOffsetGreaterThan: float, ?curtainWallPanelOffsetLessOrEqual: float, ?curtainWallPanelOffsetGreaterOrEqual: float, ?stairRiserInclineAngle: float, ?stairRiserInclineAngleNot: float, ?stairRiserInclineAngleLessThan: float, ?stairRiserInclineAngleGreaterThan: float, ?stairRiserInclineAngleLessOrEqual: float, ?stairRiserInclineAngleGreaterOrEqual: float, ?stairMinHeadroom: float, ?stairMinHeadroomNot: float, ?stairMinHeadroomLessThan: float, ?stairMinHeadroomGreaterThan: float, ?stairMinHeadroomLessOrEqual: float, ?stairMinHeadroomGreaterOrEqual: float, ?stairInvalidHeight: bool, ?stairDefaultWidth: float, ?stairDefaultWidthNot: float, ?stairDefaultWidthLessThan: float, ?stairDefaultWidthGreaterThan: float, ?stairDefaultWidthLessOrEqual: float, ?stairDefaultWidthGreaterOrEqual: float, ?stairSlope: float, ?stairSlopeNot: float, ?stairSlopeLessThan: float, ?stairSlopeGreaterThan: float, ?stairSlopeLessOrEqual: float, ?stairSlopeGreaterOrEqual: float, ?stairMaxRiserHeight: float, ?stairMaxRiserHeightNot: float, ?stairMaxRiserHeightLessThan: float, ?stairMaxRiserHeightGreaterThan: float, ?stairMaxRiserHeightLessOrEqual: float, ?stairMaxRiserHeightGreaterOrEqual: float, ?stairMinRiserHeight: float, ?stairMinRiserHeightNot: float, ?stairMinRiserHeightLessThan: float, ?stairMinRiserHeightGreaterThan: float, ?stairMinRiserHeightLessOrEqual: float, ?stairMinRiserHeightGreaterOrEqual: float, ?stairMaxGoing: float, ?stairMaxGoingNot: float, ?stairMaxGoingLessThan: float, ?stairMaxGoingGreaterThan: float, ?stairMaxGoingLessOrEqual: float, ?stairMaxGoingGreaterOrEqual: float, ?stairMinGoing: float, ?stairMinGoingNot: float, ?stairMinGoingLessThan: float, ?stairMinGoingGreaterThan: float, ?stairMinGoingLessOrEqual: float, ?stairMinGoingGreaterOrEqual: float, ?stairRiserCount: int, ?stairRiserCountNot: int, ?stairRiserCountLessThan: int, ?stairRiserCountGreaterThan: int, ?stairRiserCountLessOrEqual: int, ?stairRiserCountGreaterOrEqual: int, ?stairStepCount: int, ?stairStepCountNot: int, ?stairStepCountLessThan: int, ?stairStepCountGreaterThan: int, ?stairStepCountLessOrEqual: int, ?stairStepCountGreaterOrEqual: int, ?stairStepCountPerFlight: int, ?classificationIs: string, ?classificationIsNot: string, ?classificationChildOf: string, ?classificationNotChildOf: string, ?classificationHasValue: bool, ?classificationHasNoValue: bool, ?morphBodyType: "NonSolid"|"Solid", ?morphBodyTypeNot: "NonSolid"|"Solid", ?beamCrossSectionType: "Rectangular"|"Profiled"|"Circular", ?hatchCategory: "Drafting"|"Cover"|"Cut"|"BuildingMaterialCut"|"SurfaceColor"|"SurfaceCover"|"SurfaceTexture", ?openingShape: "Square"|"Rectangle"|"Circle"|"Ellipse"|"Polygonal", ?openingShapeNot: "Square"|"Rectangle"|"Circle"|"Ellipse"|"Polygonal", ?openingLimits: "Infinite"|"BothSides"|"OneSide", ?openingLimitsNot: "Infinite"|"BothSides"|"OneSide", ?openingOrientation: "Vertical"|"Horizontal"|"Aligned"|"Custom", ?openingOrientationNot: "Vertical"|"Horizontal"|"Aligned"|"Custom", ?textAlignment: "Left"|"Center"|"Right"|"Justified", ?textStyle: ["Bold"|"Italic"|"Underline"|"Strikethrough"|"Superscript"|"Subscript"], ?textLineSpacing: int, ?meshEdgePen: int, ?meshSkirtSurface: string, ?meshSkirtSurfaceNot: string, ?dimensionMarkerSize: float, ?dimensionMarkerSizeNot: float, ?dimensionMarkerSizeLessThan: float, ?dimensionMarkerSizeGreaterThan: float, ?dimensionMarkerSizeLessOrEqual: float, ?dimensionMarkerSizeGreaterOrEqual: float, ?dimensionMarkerPen: int, ?dimensionMarkerPenContains: int, ?dimensionPointerPenContains: int, ?dimensionPointerLineTypeContains: string, ?stairRisersPerFlight: int, ?renovationStatus: "Existing"|"ToBeDemolished"|"New", ?variantSetNameContains: string, ?variantNameContains: string, ?mepOpenConnection: bool, ?profileParameterList: {name: string, equals: float}, ?wallGeometryType: "Uniform"|"Trapezoid"|"Polygonal", ?wallGeometryTypeNot: "Uniform"|"Trapezoid"|"Polygonal", ?wallReferenceLineOffset: float, ?wallReferenceLineOffsetNot: float, ?wallReferenceLineOffsetLessThan: float, ?wallReferenceLineOffsetGreaterThan: float, ?wallReferenceLineOffsetLessOrEqual: float, ?wallReferenceLineOffsetGreaterOrEqual: float, ?wallTopLine: string, ?wallTopLineNot: string, ?wallCutLine: string, ?wallCutLineNot: string, ?wallUncutLine: string, ?wallUncutLineNot: string, ?wallHatchForegroundPen: int, ?wallHatchForegroundPenNot: int, ?wallContourPen: int, ?wallContourPenNot: int, ?wallTopLinePen: int, ?wallTopLinePenNot: int, ?wallCutHatchBackgroundPen: int, ?wallCutHatchBackgroundPenNot: int, ?wallHatchBackgroundPen: int, ?wallHatchBackgroundPenNot: int, ?wallUncutLinePen: int, ?wallUncutLinePenNot: int, ?wallOutsideSurface: string, ?wallOutsideSurfaceNot: string, ?wallInsideSurface: string, ?wallInsideSurfaceNot: string, ?wallSideSurface: string, ?wallSideSurfaceNot: string, ?wallParentIdIs: string, ?wallParentIdIsNot: string, ?wallParentIdContains: string, ?wallParentIdNotContains: string, ?wallParentIdStartsWith: string, ?wallParentIdEndsWith: string, ?wallConnectedOpeningIdsIs: string, ?wallConnectedOpeningIdsIsNot: string, ?wallConnectedOpeningIdsContains: string, ?wallConnectedOpeningIdsNotContains: string, ?wallConnectedOpeningIdsStartsWith: string, ?wallConnectedOpeningIdsEndsWith: string, ?libraryPartNameIs: string, ?libraryPartNameIsNot: string, ?libraryPartNameContains: string, ?libraryPartNameNotContains: string, ?libraryPartNameStartsWith: string, ?libraryPartNameEndsWith: string, ?subTypeNameIs: string, ?subTypeNameIsNot: string, ?subTypeNameContains: string, ?subTypeNameNotContains: string, ?subTypeNameStartsWith: string, ?subTypeNameEndsWith: string, ?columnCoatingType: "Core"|"Finish"|"Other", ?columnCoatingTypeNot: "Core"|"Finish"|"Other", ?columnInclinationAngle: float, ?columnInclinationAngleNot: float, ?columnInclinationAngleLessThan: float, ?columnInclinationAngleGreaterThan: float, ?columnInclinationAngleLessOrEqual: float, ?columnInclinationAngleGreaterOrEqual: float, ?columnCrossSectionType: "Rectangular"|"Circular"|"Profiled", ?columnCoreDiameter: float, ?columnCoreDiameterNot: float, ?columnCoreDiameterLessThan: float, ?columnCoreDiameterGreaterThan: float, ?columnCoreDiameterLessOrEqual: float, ?columnCoreDiameterGreaterOrEqual: float, ?columnCoatingThickness: float, ?columnCoatingThicknessNot: float, ?columnCoatingThicknessLessThan: float, ?columnCoatingThicknessGreaterThan: float, ?columnCoatingThicknessLessOrEqual: float, ?columnCoatingThicknessGreaterOrEqual: float, ?columnBottomCrossSectionHeightCut: float, ?columnBottomCrossSectionHeightCutNot: float, ?columnBottomCrossSectionHeightCutLessThan: float, ?columnBottomCrossSectionHeightCutGreaterThan: float, ?columnBottomCrossSectionHeightCutLessOrEqual: float, ?columnBottomCrossSectionHeightCutGreaterOrEqual: float, ?columnBottomCrossSectionHeightPerpendicular: float, ?columnBottomCrossSectionHeightPerpendicularNot: float, ?columnBottomCrossSectionHeightPerpendicularLessThan: float, ?columnBottomCrossSectionHeightPerpendicularGreaterThan: float, ?columnBottomCrossSectionHeightPerpendicularLessOrEqual: float, ?columnBottomCrossSectionHeightPerpendicularGreaterOrEqual: float, ?columnTopCrossSectionHeightCut: float, ?columnTopCrossSectionHeightCutNot: float, ?columnTopCrossSectionHeightCutLessThan: float, ?columnTopCrossSectionHeightCutGreaterThan: float, ?columnTopCrossSectionHeightCutLessOrEqual: float, ?columnTopCrossSectionHeightCutGreaterOrEqual: float, ?columnTopCrossSectionHeightPerpendicular: float, ?columnTopCrossSectionHeightPerpendicularNot: float, ?columnTopCrossSectionHeightPerpendicularLessThan: float, ?columnTopCrossSectionHeightPerpendicularGreaterThan: float, ?columnTopCrossSectionHeightPerpendicularLessOrEqual: float, ?columnTopCrossSectionHeightPerpendicularGreaterOrEqual: float, ?columnProfileCoreHeight: float, ?columnProfileCoreHeightNot: float, ?columnProfileCoreHeightLessThan: float, ?columnProfileCoreHeightGreaterThan: float, ?columnProfileCoreHeightLessOrEqual: float, ?columnProfileCoreHeightGreaterOrEqual: float, ?columnCoreHeightDiameterRatio: float, ?columnCoreHeightDiameterRatioNot: float, ?columnCoreHeightDiameterRatioLessThan: float, ?columnCoreHeightDiameterRatioGreaterThan: float, ?columnCoreHeightDiameterRatioLessOrEqual: float, ?columnCoreHeightDiameterRatioGreaterOrEqual: float, ?columnBottomCrossSectionWidthCut: float, ?columnBottomCrossSectionWidthCutNot: float, ?columnBottomCrossSectionWidthCutLessThan: float, ?columnBottomCrossSectionWidthCutGreaterThan: float, ?columnBottomCrossSectionWidthCutLessOrEqual: float, ?columnBottomCrossSectionWidthCutGreaterOrEqual: float, ?columnBottomCrossSectionWidthPerpendicular: float, ?columnBottomCrossSectionWidthPerpendicularNot: float, ?columnBottomCrossSectionWidthPerpendicularLessThan: float, ?columnBottomCrossSectionWidthPerpendicularGreaterThan: float, ?columnBottomCrossSectionWidthPerpendicularLessOrEqual: float, ?columnBottomCrossSectionWidthPerpendicularGreaterOrEqual: float, ?columnTopCrossSectionWidthCut: float, ?columnTopCrossSectionWidthCutNot: float, ?columnTopCrossSectionWidthCutLessThan: float, ?columnTopCrossSectionWidthCutGreaterThan: float, ?columnTopCrossSectionWidthCutLessOrEqual: float, ?columnTopCrossSectionWidthCutGreaterOrEqual: float, ?columnTopCrossSectionWidthPerpendicular: float, ?columnTopCrossSectionWidthPerpendicularNot: float, ?columnTopCrossSectionWidthPerpendicularLessThan: float, ?columnTopCrossSectionWidthPerpendicularGreaterThan: float, ?columnTopCrossSectionWidthPerpendicularLessOrEqual: float, ?columnTopCrossSectionWidthPerpendicularGreaterOrEqual: float, ?columnCoreWidth: float, ?columnCoreWidthNot: float, ?columnCoreWidthLessThan: float, ?columnCoreWidthGreaterThan: float, ?columnCoreWidthLessOrEqual: float, ?columnCoreWidthGreaterOrEqual: float, ?columnProfileCoreWidth: float, ?columnProfileCoreWidthNot: float, ?columnProfileCoreWidthLessThan: float, ?columnProfileCoreWidthGreaterThan: float, ?columnProfileCoreWidthLessOrEqual: float, ?columnProfileCoreWidthGreaterOrEqual: float, ?columnCoveringHatch: string, ?columnCoveringHatchNot: string, ?columnCoatingHatch: string, ?columnCoatingHatchNot: string, ?columnCoreForegroundPen: int, ?columnCoreForegroundPenNot: int, ?columnCoatingForegroundPen: int, ?columnCoatingForegroundPenNot: int, ?columnCoveringHatchForegroundPen: int, ?columnCoveringHatchForegroundPenNot: int, ?columnCoveringHatchBackgroundPen: int, ?columnCoveringHatchBackgroundPenNot: int, ?columnCoatingBackgroundPen: int, ?columnCoatingBackgroundPenNot: int, ?columnCoreBackgroundPen: int, ?columnCoreBackgroundPenNot: int, ?columnHiddenLinePen: int, ?columnHiddenLinePenNot: int, ?columnHiddenLineType: string, ?columnHiddenLineTypeNot: string, ?columnCoreSurface: string, ?columnCoreSurfaceNot: string, ?columnCoatingSurface: string, ?columnCoatingSurfaceNot: string, ?columnExtrusionSurface: string, ?columnExtrusionSurfaceNot: string, ?beamAxisPen: int, ?beamAxisPenNot: int, ?beamAxisLineType: string, ?beamAxisLineTypeNot: string, ?beamEndSurface: string, ?beamEndSurfaceNot: string, ?beamRightSurface: string, ?beamRightSurfaceNot: string, ?beamLeftSurface: string, ?beamLeftSurfaceNot: string, ?beamBottomSurface: string, ?beamBottomSurfaceNot: string, ?beamTopSurface: string, ?beamTopSurfaceNot: string, ?slabReferencePlaneLocation: "Top"|"CoreTop"|"CoreBottom"|"Bottom", ?slabReferencePlaneLocationNot: "Top"|"CoreTop"|"CoreBottom"|"Bottom", ?slabEdgeAngle: "Vertical"|"Custom", ?slabEdgeAngleNot: "Vertical"|"Custom", ?slabDefaultEdgeAngle: float, ?slabDefaultEdgeAngleNot: float, ?slabDefaultEdgeAngleLessThan: float, ?slabDefaultEdgeAngleGreaterThan: float, ?slabDefaultEdgeAngleLessOrEqual: float, ?slabDefaultEdgeAngleGreaterOrEqual: float, ?slabCutLinePen: int, ?slabCutLinePenNot: int, ?slabConstructionMaterialFill: string, ?slabConstructionMaterialFillNot: string, ?roofCutBodyType: "ContoursDown"|"ReferenceLineDown", ?roofCutBodyTypeNot: "ContoursDown"|"ReferenceLineDown", ?roofLevelNumber: int, ?roofLevelNumberNot: int, ?roofLevelNumberLessThan: int, ?roofLevelNumberGreaterThan: int, ?roofLevelNumberLessOrEqual: int, ?roofLevelNumberGreaterOrEqual: int, ?roofEaveOverhangType: "Offset"|"Manual", ?roofEdgeAngle: "Vertical"|"Perpendicular"|"Custom", ?roofEdgeAngleNot: "Vertical"|"Perpendicular"|"Custom", ?roofEaveOverhang: float, ?roofEaveOverhangNot: float, ?roofEaveOverhangLessThan: float, ?roofEaveOverhangGreaterThan: float, ?roofEaveOverhangLessOrEqual: float, ?roofEaveOverhangGreaterOrEqual: float, ?roofGeometryType: "SinglePanel"|"MultiplePanels", ?roofGeometryTypeNot: "SinglePanel"|"MultiplePanels", ?roofPitch: float, ?roofPitchNot: float, ?roofPitchLessThan: float, ?roofPitchGreaterThan: float, ?roofPitchLessOrEqual: float, ?roofPitchGreaterOrEqual: float, ?shellCutBodyType: "Editable"|"ExtrudeUp"|"ExtrudeDown", ?shellTiltAngle: float, ?shellTiltAngleNot: float, ?shellTiltAngleLessThan: float, ?shellTiltAngleGreaterThan: float, ?shellTiltAngleLessOrEqual: float, ?shellTiltAngleGreaterOrEqual: float, ?shellGeometryType: "Extrude"|"Revolved"|"Ruled", ?hatchFill: string, ?hatchFillNot: string, ?lineAttribute: string, ?lineAttributeNot: string, ?fontIs: string, ?fontContains: string, ?fontNotContains: string, ?penReplacement: "None"|"ForegroundOnly"|"BackgroundOnly"|"Both", ?penReplacementNot: "None"|"ForegroundOnly"|"BackgroundOnly"|"Both", ?linePenContains: int, ?linePenNotContains: int, ?textPenIs: int, ?textPenContains: int, ?textPenNotContains: int, ?hatchContourPen: int, ?hatchContourPenNot: int, ?openingEndSurface: string, ?openingEndSurfaceNot: string, ?openingExtrusionSurface: string, ?openingExtrusionSurfaceNot: string, ?curtainWallFrameCutLine: string, ?curtainWallFrameCutLineNot: string, ?curtainWallPanelCutLine: string, ?curtainWallPanelCutLineNot: string, ?curtainWallFrameCutLinePen: int, ?curtainWallFrameCutLinePenNot: int, ?curtainWallPanelCutLinePen: int, ?curtainWallPanelCutLinePenNot: int, ?constructionMaterial: string, ?constructionMaterialNot: string, ?surface: string, ?surfaceNot: string, ?constructionMaterialIdIs: string, ?constructionMaterialIdIsNot: string, ?constructionMaterialIdContains: string, ?constructionMaterialIdNotContains: string, ?constructionMaterialIdStartsWith: string, ?constructionMaterialIdEndsWith: string, ?constructionMaterialNameIs: string, ?constructionMaterialNameIsNot: string, ?constructionMaterialNameContains: string, ?constructionMaterialNameNotContains: string, ?constructionMaterialNameStartsWith: string, ?constructionMaterialNameEndsWith: string, ?surfaceNameIs: string, ?surfaceNameIsNot: string, ?surfaceNameContains: string, ?surfaceNameNotContains: string, ?surfaceNameStartsWith: string, ?surfaceNameEndsWith: string, ?renovationFilterIs: string, ?renovationFilterIsNot: string, ?structuralFunction: "LoadBearing"|"NonLoadBearing"|"Undefined", ?structuralFunctionNot: "LoadBearing"|"NonLoadBearing"|"Undefined", ?position: "Exterior"|"Interior"|"Undefined", ?positionNot: "Exterior"|"Interior"|"Undefined", ?variantStateIs: string, ?variantStateIsNot: string, ?variantSetIs: string, ?variantSetIsNot: string, ?elementIdIs: string, ?elementIdIsNot: string, ?elementIdLessThan: string, ?elementIdGreaterThan: string, ?elementIdLessOrEqual: string, ?elementIdGreaterOrEqual: string, ?elementIdContains: string, ?elementIdNotContains: string, ?elementIdStartsWith: string, ?elementIdEndsWith: string, ?uniqueIdIs: string, ?uniqueIdIsNot: string, ?uniqueIdContains: string, ?uniqueIdNotContains: string, ?uniqueIdStartsWith: string, ?uniqueIdEndsWith: string, ?linkMainIdIs: string, ?linkMainIdIsNot: string, ?linkMainIdLessThan: string, ?linkMainIdGreaterThan: string, ?linkMainIdLessOrEqual: string, ?linkMainIdGreaterOrEqual: string, ?linkMainIdContains: string, ?linkMainIdNotContains: string, ?linkMainIdStartsWith: string, ?linkMainIdEndsWith: string, ?linkedElementIdIs: string, ?linkedElementIdIsNot: string, ?linkedElementIdLessThan: string, ?linkedElementIdGreaterThan: string, ?linkedElementIdLessOrEqual: string, ?linkedElementIdGreaterOrEqual: string, ?linkedElementIdContains: string, ?linkedElementIdNotContains: string, ?linkedElementIdStartsWith: string, ?linkedElementIdEndsWith: string, ?nameIs: string, ?nameIsNot: string, ?nameContains: string, ?nameNotContains: string, ?nameStartsWith: string, ?nameEndsWith: string, ?hasLinkSource: bool, ?hasLinkSourceNot: bool, ?missingVariant: bool, ?profileStretchHeight: float, ?profileStretchHeightNot: float, ?profileStretchHeightLessThan: float, ?profileStretchHeightGreaterThan: float, ?profileStretchHeightLessOrEqual: float, ?profileStretchHeightGreaterOrEqual: float, ?profileStretchWidth: float, ?profileStretchWidthNot: float, ?profileStretchWidthLessThan: float, ?profileStretchWidthGreaterThan: float, ?profileStretchWidthLessOrEqual: float, ?profileStretchWidthGreaterOrEqual: float, ?profileNominalHeight: float, ?profileNominalHeightNot: float, ?profileNominalHeightLessThan: float, ?profileNominalHeightGreaterThan: float, ?profileNominalHeightLessOrEqual: float, ?profileNominalHeightGreaterOrEqual: float, ?profileTotalHeight: float, ?profileTotalHeightNot: float, ?profileTotalHeightLessThan: float, ?profileTotalHeightGreaterThan: float, ?profileTotalHeightLessOrEqual: float, ?profileTotalHeightGreaterOrEqual: float, ?profileTotalWidth: float, ?profileTotalWidthNot: float, ?profileTotalWidthLessThan: float, ?profileTotalWidthGreaterThan: float, ?profileTotalWidthLessOrEqual: float, ?profileTotalWidthGreaterOrEqual: float, ?profileNominalWidth: float, ?profileNominalWidthNot: float, ?profileNominalWidthLessThan: float, ?profileNominalWidthGreaterThan: float, ?profileNominalWidthLessOrEqual: float, ?profileNominalWidthGreaterOrEqual: float, ?profileParameter: {name: string, ?equals: float, ?notEquals: float, ?lessThan: float, ?greaterThan: float, ?lessOrEqual: float, ?greaterOrEqual: float}, ?customPropertyBool: {name: string, group: string, ?equals: bool, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyString: {name: string, group: string, ?equals: string, ?notEquals: string, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyNumber: {name: string, group: string, ?equals: float, ?notEquals: float, ?lessThan: float, ?greaterThan: float, ?lessOrEqual: float, ?greaterOrEqual: float, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}, ?customPropertyInteger: {name: string, group: string, ?equals: int, ?notEquals: int, ?lessThan: int, ?greaterThan: int, ?lessOrEqual: int, ?greaterOrEqual: int, ?hasDefaultValue: bool, ?hasCustomValue: bool, ?isAvailable: bool, ?isNotAvailable: bool, ?isUndefined: bool, ?isNotUndefined: bool}}
- **GraphicOverrideElementType**: "Wall"|"Column"|"Beam"|"Slab"|"Roof"|"Shell"|"Stair"|"Railing"|"CurtainWall"|"Opening"|"Mesh"|"Morph"|"Dimension"|"LevelDimension"|"RadialDimension"|"AngleDimension"|"Text"|"ChangeMarker"|"Hatch"|"Line"|"Arc"|"PolyLine"|"Spline"|"Hotspot"|"Section"|"Elevation"|"InteriorElevation"|"Detail"|"Worksheet"|"Camera"|"Figure"|"Drawing"|"StructuralLink"|"StructuralSupport"|"LinearLoad"|"PointLoad"|"SurfaceLoad"|"DuctRouting"|"CableCarrierRouting"|"PipeRouting"|"Window"|"Door"|"Zone"|"Label"|"Object"|"Lamp"|"GridElement"|"Skylight"|"CornerWindow"|"WallEnd"|"DuctBranch"|"DuctTerminal"|"DuctAccessory"|"DuctFitting"|"DuctFlexibleSegment"|"CableCarrierBranch"|"CableCarrierFitting"|"PipeBranch"|"PipeTerminal"|"PipeAccessory"|"PipeFitting"|"Equipment"|"AllTypes"
- **GraphicOverrideFillTypes**: {cutFill: bool, coverFill: bool, draftingFill: bool}
- **GraphicOverrideRule**: {graphicOverrideRuleId: GraphicOverrideRuleId, name: string, ?ruleGroupName: string, criterionXML: string, ?criterion: GraphicOverrideCriterion, style: GraphicOverrideStyle}
- **GraphicOverrideRuleGroupRename**: {name: string, newName: string}
- **GraphicOverrideRuleId**: {guid: Guid}
- **GraphicOverrideRuleIdArrayItem**: {graphicOverrideRuleId: GraphicOverrideRuleId}
- **GraphicOverrideRuleIdOrError**: GraphicOverrideRuleIdArrayItem | ErrorItem
- **GraphicOverrideRuleMove**: {graphicOverrideRuleId: GraphicOverrideRuleId, ruleGroupName: string, ?beforeGraphicOverrideRuleId: GraphicOverrideRuleId}
- **GraphicOverrideRuleOrError**: GraphicOverrideRule | ErrorItem
- **GraphicOverrideRuleReference**: {name: string, ?ruleGroupName: string}
- **GraphicOverrideStyle**: {?lineType: AttributeId, ?lineMarkerTextPen: int, ?fillType: AttributeId, ?fillTypeAppliesTo: GraphicOverrideFillTypes, ?fillForegroundPen: int, ?fillForegroundPenAppliesTo: GraphicOverrideFillTypes, ?fillBackgroundPen: int, ?fillBackgroundColor: ColorRGB, ?fillBackgroundPenAppliesTo: GraphicOverrideFillTypes, ?surface: AttributeId, ?surfaceColor: ColorRGB, ?surfaceAppliesTo: GraphicOverrideSurfaceTypes, ?showSkinSeparators: bool, ?overridePenColorAndThickness: bool, ?hiddenContours: GraphicOverrideSurfaceTypes, ?overrideContours: bool}
- **GraphicOverrideSurfaceTypes**: {cutSurface: bool, uncutSurface: bool}
- **GroupId**: {guid: Guid}
- **GroupIdArrayItem**: {groupId: GroupId}
- **GroupIdOrError**: GroupIdArrayItem | ErrorItem
- **Guid**: string
- **GuidId**: {guid: Guid}
- **HatchDetails**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?holes: Holes2D, ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool, ?fillOrientation: HatchOrientation, zCoordinate: float}
- **HatchOrientation**: {?type: HatchOrientationType, ?origin: Coordinate2D, ?matrix00: float, ?matrix10: float, ?matrix01: float, ?matrix11: float, ?innerRadius: float}
- **HatchOrientationType**: "Global"|"Rotated"|"Distorted"|"Centered"
- **HatchSettings**: {?coordinates: [Coordinate2D], ?arcs: [PolyArc], ?holes: Holes2D, ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool, ?fillOrientation: HatchOrientation}
- **HierarchicalElementOwner**: {ownerElementId: ElementId, hierarchicalElementType: "MainElement"|"ChildElement"|"SingleElement"}
- **HierarchicalOwnerMode**: "root"|"parent"
- **Hole2D**: any | any
- **Hole3D**: {polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc]}
- **Holes2D**: [Hole2D]
- **Holes3D**: [Hole3D]
- **Hotlink**: {location: string, ?hotlinkNodeId: HotlinkNodeId, ?name: string, ?type: HotlinkType, ?instances: Elements, ?children: Hotlinks}
- **HotlinkDetails**: {hotlinkType: HotlinkType, hotlinkNodeId: HotlinkNodeId, origin: Coordinate3D, rotationAngle: float, mirrored: bool, ?floorDifference: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool}
- **HotlinkInstanceChange**: {elementId: ElementId, ?origin: HotlinkOrigin, ?rotationAngle: float, ?mirrored: bool, ?floorDifference: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool, ?layerIndex: int}
- **HotlinkInstanceCreation**: {hotlinkNodeId: HotlinkNodeId, origin: HotlinkOrigin, ?rotationAngle: float, ?mirrored: bool, ?floorIndex: int, ?floorDifference: int, ?layerIndex: int, ?skipNested: bool, ?suspendFixAngle: bool, ?ignoreTopFloorLinks: bool, ?relinkWallOpenings: bool, ?adjustLevelDiffs: bool}
- **HotlinkNodeCreated**: {hotlinkNodeId: HotlinkNodeId, existing: bool}
- **HotlinkNodeCreatedOrError**: HotlinkNodeCreated | ErrorItem
- **HotlinkNodeId**: {guid: Guid}
- **HotlinkOrigin**: {x: float, y: float, ?z: float}
- **HotlinkOwnersOfElement**: {isInHotlink: bool, ?hotlinkElementId: ElementId, ?hotlinkInstanceId: ElementId}
- **HotlinkOwnersOfElementOrError**: HotlinkOwnersOfElement | ErrorItem
- **HotlinkProxyElement**: {proxyElementId: ElementId, sourceElementId: ElementId}
- **HotlinkProxyElementTable**: {proxyElements: [HotlinkProxyElement]}
- **HotlinkSourceReference**: {location: string}
- **HotlinkSourceStatusResult**: {status: "AuthCanceld"|"SourceMissing"|"SourceAvailable"|"SourceNotAccessible"|"SourceIncompatible"|"SourceOffline"}
- **HotlinkType**: "Module"|"XRef"
- **Hotlinks**: [Hotlink]
- **HotspotDetails**: {position: Coordinate2D, height: float, ?penIndex: int}
- **HotspotSettings**: {?position: Coordinate2D, ?height: float, ?penIndex: int}
- **IFCElementsToExport**: "EntireProject"|"VisibleElementsOnAllStories"|"AllElementsOnCurrentStory"|"VisibleElementsOnCurrentStory"|"SelectedElementsOnly"
- **IFCExportTranslator**: {name: string, preview: bool}
- **IFCObject**: {hashValue: int, ?elementId: ElementId, ?ifcType: string, ?globalId: string}
- **IFCObjectWithChildren**: {object: IFCObject, children: [IFCObject]}
- **IFCObjectWithParents**: {object: IFCObject, parents: [IFCObject]}
- **IFCPropertySource**: "preview"|"local"
- **IFCPropertyType**: "SingleValue"|"ListValue"|"BoundedValue"|"EnumeratedValue"|"TableValue"
- **IFCSpatialStructureOfElement**: {elementId: ElementId, storyIndex: int}
- **InputConstraint**: {type: "X"|"Y"|"Z"|"Angle"|"Distance", value: float, ?fromLastPoint: bool}
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
- **LabelDetails**: {?libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, begCoordinate: Coordinate2D, midCoordinate: Coordinate2D, endCoordinate: Coordinate2D, hasLeaderLine: bool, labelClass: LabelClass, leaderLine: LabelLeaderLineDetails, ?style: TextStyleDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?text: string, ?rawText: string, ?paragraphCount: int, ?runs: [TextRunDetails]}
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
- **LayoutInsertionPosition**: "first"|"last"
- **LayoutSubsetSettings**: {name: string, ownPrefix: string, customNumber: string, numberingStyle: "Undefined"|"abc"|"ABC"|"1"|"01"|"001"|"0001"|"noID", startAt: int, continueNumbering: bool, useUpperPrefix: bool, includeToIDSequence: bool, customNumbering: bool, addOwnPrefix: bool}
- **LengthType**: "Meter"|"Decimeter"|"Centimeter"|"Millimeter"|"FootFracInch"|"FootDecInch"|"DecFoot"|"FracInch"|"DecInch"
- **LevelDimensionDetails**: {position: Coordinate2D, level: float, staticLevel: bool, ?ownerElementId: ElementId, ?ownerElementType: ElementType, dimForm: int, needPlus: bool, pen: int, textHeight: float, textPen: int, markerSize: float, angle: float, origin: DimensionOrigin}
- **LibPartBasedElementDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType}
- **LibPartDetails**: {name: string, parentUnID: LibPartUnId, ownUnID: LibPartUnId}
- **LibPartUnId**: {guid: Guid}
- **Library**: {name: string, path: string, type: string, ?available: bool, ?readOnly: bool, ?twServerUrl: string, ?urlWebLibrary: string, ?package: LibraryPackage}
- **LibraryFileAddition**: {inputPath: string, outputPath: string, ?type: LibraryPartType}
- **LibraryFileAdditions**: [LibraryFileAddition]
- **LibraryLocation**: {path: string}
- **LibraryOfLibraryPart**: {?library: {?displayName: string, ?path: string, ?isEmbedded: bool, ?isBuiltIn: bool, ?isPackage: bool, ?isLocal: bool, ?isMissing: bool}, ?libraryTreePath: [string], ?error: {?code: int, ?message: string}}
- **LibraryPackage**: {?packageId: string, ?mainVersion: int, ?subVersion: int, ?minArchicadVersion: int, ?minArchicadBuildNumber: int, ?dependencies: [{name: string, packageId: string, version: int}]}
- **LibraryPartByIndex**: {index: int}
- **LibraryPartCopyData**: {?libraryPartName: string, ?elementId: ElementId, newName: string, ?targetFolder: string, ?keepMainGuid: bool}
- **LibraryPartCreationDetails**: {name: string, unId: string, guid: string, index: int, path: string}
- **LibraryPartData**: {name: string, ?parentId: string, ?parentName: string, ?type: LibraryPartType, ?path: string, ?a: float, ?b: float, ?masterScript: string, ?script2D: string, ?script3D: string, ?parameterScript: string, ?uiScript: string, ?propertiesScript: string, ?parameters: [{name: string, type: "Integer"|"Length"|"Angle"|"RealNumber"|"LightSwitch"|"RGBColor"|"Intensity"|"LineType"|"Material"|"FillPattern"|"PenColor"|"String"|"Boolean"|"Separator"|"Title"|"BuildingMaterial"|"Profile", ?value: float | string | bool, ?description: string, ?isHidden: bool}]}
- **LibraryPartDetails**: {?name: string, ?path: string, ?index: int, ?libraryTreePath: {parts: [string], lastPart: string, isRoot: bool, ?parentParts: [string], ?teamworkId: string}, ?library: {?name: string, ?localizedName: string, ?path: string, ?isServer: bool, ?twServerPath: string, ?twServerUrl: string}, ?gsmObject: {?guid: string, ?isSubType: bool, ?subTypeGuid: string, ?isInSubTypeOf: bool, ?isUIDefault: bool, ?license: string, ?licenseVersion: string, contents: {interfaceScript: bool, forwardMigrationScript: bool, backwardMigrationScript: bool, 2dVectorImage: bool, previewPicture: bool, gdlPictures: bool, ?darkPreviewPicture: bool, ?darkGdlPictures: bool}, ?scripts: {?interface: string, ?forwardMigration: string, ?backwardMigration: string}}}
- **LibraryPartDoorWindowDetails**: {mirThick: float, wallInset: float, leftFram: float, righFram: float, topFram: float, botFram: float, orientation: int, contours3D: bool}
- **LibraryPartFileInfo**: {path: string, ?unID: string, ?subTypeUnID: string, scripts: object}
- **LibraryPartIdentifier**: any | any | any
- **LibraryPartIdentity**: {path: string, unId: string, ?mainGuid: Guid, ?revisionGuid: Guid, ?refGuid: Guid, ?lockStatus: "Free"|"Editable"|"Locked"|"NotAvailable"|"NotExist", isServerLibraryPart: bool}
- **LibraryPartIndexAndPassword**: {index: int, ?password: string}
- **LibraryPartIndexOrPath**: any | any
- **LibraryPartKind**: "All"|"Object"|"Image"|"Text"
- **LibraryPartMetadata**: {?author: string, ?keywords: string, ?license: string, ?licenseVersion: string, ?password: string, ?placeable: bool, ?uiDefault: bool, ?isSubtype: bool, ?hierarchicalPagesUsed: bool}
- **LibraryPartMetadataDetails**: {description: string, keywords: string, author: string, isPlaceable: bool, isPasswordProtected: bool, isHierarchicalPagesUsed: bool}
- **LibraryPartMetadataUpdate**: {name: string, metadata: LibraryPartMetadata}
- **LibraryPartName**: {name: string}
- **LibraryPartNameOrGuid**: {?name: string, ?guid: string}
- **LibraryPartNameOrIndex**: any | any
- **LibraryPartObjectDetails**: {fixSize: bool, autoHotspot: bool}
- **LibraryPartOriginalLocation**: {path: string}
- **LibraryPartParameterValues**: {name: string, parameters: [{name: string, type: "Integer"|"Length"|"Angle"|"RealNumber"|"LightSwitch"|"RGBColor"|"Intensity"|"LineType"|"Material"|"FillPattern"|"PenColor"|"String"|"Boolean"|"BuildingMaterial"|"Profile", ?dimension1: int, ?dimension2: int, value: any, ?description: string}]}
- **LibraryPartReadableScriptType**: "master"|"parameter"|"2d"|"3d"|"properties"
- **LibraryPartScript**: {present: bool, ?script: string}
- **LibraryPartScriptType**: "master"|"parameter"|"2d"|"3d"|"properties"|"interface"|"forwardMigration"|"backwardMigration"
- **LibraryPartScripts**: {?master: string, ?parameter: string, ?2d: string, ?3d: string, ?properties: string, ?interface: string, ?forwardMigration: string, ?backwardMigration: string}
- **LibraryPartScriptsDetails**: {libraryPartName: string, ?unID: string, scripts: object}
- **LibraryPartScriptsUpdate**: any | any
- **LibraryPartSearchResult**: {index: int, name: string, ?fileName: string, unId: string, ?parentUnId: string, ?typeId: LibraryPartType}
- **LibraryPartSections**: {index: int, sections: [{sectionType: string, subIdent: int, ?size: int, ?isText: bool}]}
- **LibraryPartType**: "Spec"|"Window"|"Door"|"Object"|"Lamp"|"Room"|"Property"|"PlanSign"|"Label"|"Macro"|"Pict"|"Picture"|"ListScheme"|"Skylight"|"OpeningSymbol"|"Unknown"
- **LibraryToRemove**: any | any
- **LineAttribute**: {attributeId: AttributeId, index: int, name: string, ?scaleWithPlan: bool, ?defineScale: float, ?lineType: "Solid"|"Dashed"|"Symbol", ?period: float, ?height: float, ?dashItems: [LineDashItem], ?lineItems: [LineSymbolItem]}
- **LineAttributeField**: "scaleWithPlan"|"defineScale"|"lineType"|"period"|"height"|"dashItems"|"lineItems"
- **LineAttributeOrError**: LineAttribute | ErrorItem
- **LineDashItem**: {dash: float, gap: float}
- **LineDetails**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **LineSettings**: {?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **LineSymbolItem**: {itemType: string, centerOffset: float, length: float, begPos: Coordinate2D, endPos: Coordinate2D, radius: float, beginAngle: float, endAngle: float}
- **LineSymbolItemData**: {itemType: string, ?centerOffset: float, ?length: float, ?begPos: Coordinate2D, ?endPos: Coordinate2D, ?radius: float, ?beginAngle: float, ?endAngle: float}
- **LinkToSettings**: {?homeStoryDifference: int, ?newCreationMode: bool}
- **MEPAngleSet**: {name: string, ?isEditable: bool, angles: [float], ?angleDetails: [{angle: float, ?isDefined: bool}]}
- **MEPBranchPreferenceTable**: {guid: string, name: string, ?isEditable: bool, rows: [{?index: MEPPreferenceRowIndex, mainAxisReferenceId: int, branchAxisReferenceId: int, ?branchAxisAngle: float, mainAxisDiameter: float, branchAxisDiameter: float, length: float, branchOffset: float, connectionLength: float, ?description: string, ?isValid: bool}]}
- **MEPComponentType**: "Terminal"|"Accessory"|"Equipment"|"Fitting"
- **MEPConnectionData**: {routingElementId: ElementId, connectToId: ElementId}
- **MEPConnectionResult**: {?deletedRoutingElementId: ElementId, ?splitRoutingElementId: ElementId, ?createdBranchId: ElementId}
- **MEPConnectionResultOrError**: MEPConnectionResult | ErrorItem
- **MEPConnectionResultsOrErrors**: [MEPConnectionResultOrError]
- **MEPConnectionStyle**: "SimpleBody"|"Flanged"|"Welded"
- **MEPCrossSectionShape**: "Rectangular"|"Circular"|"Oval"|"UShape"
- **MEPCutPlanePosition**: "AtUpperDisplayLimit"|"ByViewSettings"
- **MEPDistributionSystem**: {domain: MEPDomainOrUnknown, ?mepSystemId: AttributeId, elements: Elements, ?physicalSystemIds: [MEPPhysicalSystemId], ?tree: [MEPDistributionSystemTreeNode]}
- **MEPDistributionSystemTreeNode**: {elementId: ElementId, depth: int, ?previousElementId: ElementId, ?connectedPortIdOfPreviousElement: string, ?connectedPortIdOfThisElement: string, nextElements: Elements}
- **MEPDomain**: "Ventilation"|"Piping"|"CableCarrier"
- **MEPDomainOrUnknown**: "Ventilation"|"Piping"|"CableCarrier"|"Unknown"
- **MEPDomainToolDefaults**: {domain: MEPDomain, ?routingElement: {mepSystemId: AttributeId, ?branchPreferenceTableId: Guid, ?cutPlanePosition: MEPCutPlanePosition, ?floorPlanDisplayOption: MEPFloorPlanDisplayOption, ?showProjection: MEPShowProjection, ?onStoryVisibility: MEPOnStoryVisibility, routingSegment: {?crossSectionShape: MEPCrossSectionShape, ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?anchor: string, ?referenceLineOffsetX: float, ?referenceLineOffsetY: float, ?wallThickness: float, ?flangeSize: float, ?connectionStyle: MEPConnectionStyle}, routingNode: {?preferredTransitionPlacement: MEPPreferredTransitionPlacement, ?elbow: {?factorRadius: float, ?preferenceTableId: Guid}, ?transition: {?angle: float, ?offsetY: float, ?offsetZ: float, ?preferenceTableId: Guid}}}, ?rigidSegment: {?shape: MEPCrossSectionShape, ?width: float, ?height: float, ?insulationThickness: float}, ?branch: MEPElementDefaultDetails, ?flexibleSegment: {shape: MEPCrossSectionShape, width: float, height: float}, ?terminal: MEPElementDefaultDetails, ?accessory: MEPElementDefaultDetails, ?fitting: MEPElementDefaultDetails}
- **MEPElbowParameters**: {?factorRadius: float, ?preferenceTableId: Guid}
- **MEPElbowPreferenceTable**: {guid: string, name: string, ?isEditable: bool, rows: [{?index: MEPPreferenceRowIndex, referenceId: int, ?angle: float, diameter: float, radius: float, ?description: string, ?isValid: bool}]}
- **MEPElement**: {elementId: ElementId, type: MEPElementType, domain: string, ?localizedTypeName: string}
- **MEPElementData**: {type: MEPComponentType, ?domain: MEPDomain, position: Coordinate3D, ?libraryPartId: LibPartUnId, ?xSize: float, ?ySize: float, ?mepSystemId: AttributeId, ?ports: [MEPPortCreationData], ?orientationDirection: Coordinate3D, ?orientationRotation: Coordinate3D, ?floorIndex: int, ?defaults: {?insulationThickness: float, ?removeInsulation: bool}}
- **MEPElementDefaultDetails**: {libraryPartId: LibPartUnId, ?insulationThickness: float, ports: [MEPPortDefaultDetails]}
- **MEPElementDetails**: {elementId: ElementId, type: MEPElementType, domain: string, ?insulationThickness: float, ?routingSegmentId: ElementId, ?routingNodeId: ElementId, ?controlPoints: [Coordinate3D], ?polyline: MEPFlexibleSegmentPolyline, ?factorRadius: float, ?preferenceTableId: Guid, ?branchAngle: float, ?branchLength: float, ?offsetY: float, ?offsetZ: float, ?widerPortId: Guid, ?narrowerPortId: Guid, ?isControlledByPreference: bool}
- **MEPElementModificationData**: {elementId: ElementId, ?anchorPoint: Coordinate3D, ?orientation: MEPOrientation, ?libraryPartId: LibPartUnId, ?controlPoints: [Coordinate3D], ?polyline: MEPFlexibleSegmentPolyline, ?width: float, ?height: float}
- **MEPElementPorts**: {ports: [MEPPortDetails]}
- **MEPElementPortsOrError**: MEPElementPorts | ErrorItem
- **MEPElementPortsOrErrors**: [MEPElementPortsOrError]
- **MEPElementType**: "RoutingElement"|"RigidSegment"|"Elbow"|"Transition"|"Branch"|"Terminal"|"Accessory"|"Equipment"|"Fitting"|"FlexibleSegment"|"TakeOff"|"ElectricalPanel"|"ElectricalDevice"|"ElectricalCircuit"
- **MEPFlexibleSegmentCreationData**: {domain: MEPDomain, ?controlPoints: [Coordinate3D], ?startOrientation: MEPOrientation, ?endOrientation: MEPOrientation, ?polyline: MEPFlexibleSegmentPolyline, ?startDirection: Coordinate3D, ?endDirection: Coordinate3D}
- **MEPFlexibleSegmentPolyline**: [{type: "Line"|"Spline", ?begin: Coordinate3D, ?end: Coordinate3D, ?controlPoints: [Coordinate3D]}]
- **MEPFloorPlanDisplayOption**: "Projected"|"ProjectedWithOverhead"|"Symbolic"|"ByMVO"
- **MEPFlowDirection**: "FlowNotDefined"|"FlowIn"|"FlowOut"
- **MEPOnStoryVisibility**: "AllRelevantStories"|"HomeStoryOnly"
- **MEPOrientation**: {direction: Coordinate3D, rotation: Coordinate3D}
- **MEPPhysicalSystemData**: {systemGroupId: MEPSystemGroupId, name: string, ?rootElementId: ElementId, ?mepSystemId: AttributeId}
- **MEPPhysicalSystemDetails**: {physicalSystemId: MEPPhysicalSystemId, name: string, ?isEditable: bool, ?rootElementId: ElementId, ?mepSystemId: AttributeId}
- **MEPPhysicalSystemDetailsOrError**: MEPPhysicalSystemDetails | ErrorItem
- **MEPPhysicalSystemId**: {guid: Guid}
- **MEPPhysicalSystemIdArrayItem**: {physicalSystemId: MEPPhysicalSystemId}
- **MEPPhysicalSystemIdOrError**: {physicalSystemId: MEPPhysicalSystemId} | ErrorItem
- **MEPPhysicalSystemModificationData**: {physicalSystemId: MEPPhysicalSystemId, ?name: string, ?rootElementId: ElementId, ?mepSystemId: AttributeId}
- **MEPPhysicalSystemsOfElement**: {physicalSystemIds: [MEPPhysicalSystemId]}
- **MEPPortConnectability**: {isConnectable: bool}
- **MEPPortCreationData**: {portIndex: int, ?mepSystemId: AttributeId, ?shape: MEPCrossSectionShape, ?width: float, ?height: float, ?diameter: float}
- **MEPPortDefaultDetails**: {index: int, ?domain: MEPDomain, ?name: string, ?shape: MEPCrossSectionShape, ?width: float, ?height: float, ?diameter: float, ?wallThickness: float, ?flowDirection: MEPFlowDirection, ?flangeSize: float, ?connectionStyle: MEPConnectionStyle, ?mepSystemId: AttributeId}
- **MEPPortDetails**: {portId: Guid, ?mepElementId: ElementId, name: string, position: Coordinate3D, direction: Coordinate3D, shape: string, width: float, height: float, domain: MEPDomainOrUnknown, mepSystemId: AttributeId, ?isPhysicallyConnected: bool, ?isConnected: bool, ?connectionStyle: MEPConnectionStyle, ?flowDirection: MEPFlowDirection, ?nominalSize: string, ?outerDiameter: float, ?wallThickness: float, ?flangeSize: float, ?connectedPortId: Guid, ?connectedElementId: ElementId}
- **MEPPortModificationData**: {portId: Guid, ?shape: MEPCrossSectionShape, ?connectionStyle: MEPConnectionStyle, ?flowDirection: MEPFlowDirection, ?outerDiameter: float, ?nominalSize: string}
- **MEPPortPair**: {portId: Guid, otherPortId: Guid}
- **MEPPreferenceRow**: {?index: MEPPreferenceRowIndex, referenceId: int, diameter: float, ?wallThickness: float, ?description: string, ?isValid: bool}
- **MEPPreferenceRowAddition**: {key: MEPPreferenceRowKey, ?values: MEPPreferenceRowValues}
- **MEPPreferenceRowAdditionResult**: {success: true, index: int}
- **MEPPreferenceRowChange**: {index: MEPPreferenceRowIndex, ?delete: bool, ?diameter: float, ?wallThickness: float, ?value: float, ?radius: float, ?mainAxisDiameter: float, ?branchAxisDiameter: float, ?length: float, ?branchOffset: float, ?connectionLength: float, ?beginDiameter: float, ?endDiameter: float, ?angle: float, ?description: string, ?referenceId: int, ?mainAxisReferenceId: int, ?branchAxisReferenceId: int, ?beginReferenceId: int, ?endReferenceId: int, ?branchAxisAngle: float, ?isValid: bool}
- **MEPPreferenceRowDetails**: {key: MEPPreferenceRowKey, valid: bool, values: MEPPreferenceRowValues}
- **MEPPreferenceRowIndex**: int
- **MEPPreferenceRowKey**: {?shape: "Circular"|"Rectangular", ?index: int, ?referenceId: int, ?angle: float, ?mainAxisReferenceId: int, ?branchAxisReferenceId: int, ?branchAxisAngle: float, ?beginReferenceId: int, ?endReferenceId: int}
- **MEPPreferenceRowUpdate**: {key: MEPPreferenceRowKey, values: MEPPreferenceRowValues}
- **MEPPreferenceRowUpdateResult**: {success: true, ?index: int}
- **MEPPreferenceRowValues**: {?value: float, ?diameter: float, ?wallThickness: float, ?radius: float, ?mainAxisDiameter: float, ?branchAxisDiameter: float, ?length: float, ?branchOffset: float, ?connectionLength: float, ?beginDiameter: float, ?endDiameter: float, ?angle: float, ?description: string}
- **MEPPreferenceTable**: {guid: string, ?name: string, ?isEditable: bool, ?useIndividualSegmentLengths: bool, ?minimumSegmentationLength: float, ?maximumSegmentationLength: float, rows: [MEPPreferenceRow]}
- **MEPPreferenceTableAddition**: {type: MEPPreferenceTableType, name: string}
- **MEPPreferenceTableChange**: {guid: string, ?name: string, ?isEditable: bool, ?useIndividualSegmentLengths: bool, ?minimumSegmentationLength: float, ?maximumSegmentationLength: float, ?rows: [MEPPreferenceRowChange], ?newRows: [{value: float, ?description: string}]}
- **MEPPreferenceTableContainer**: {domain: MEPPreferenceTableDomain, exists: bool, tables: [{tableId: MEPPreferenceTableId, name: string, exists: bool, sizes: {?Circular: int, ?Rectangular: int}}]}
- **MEPPreferenceTableCreationResult**: {success: true, tableId: MEPPreferenceTableId}
- **MEPPreferenceTableDomain**: "Piping"|"Ventilation"|"CableCarrier"
- **MEPPreferenceTableId**: {guid: Guid}
- **MEPPreferenceTableType**: "Segment"|"Elbow"|"Branch"|"Transition"
- **MEPPreferredTransitionPlacement**: "SmallToLarge"|"LargeToSmall"
- **MEPReferenceSet**: {name: string, ?isEditable: bool, referenceIds: [int], ?referenceIdDetails: [{referenceId: int, ?isDefined: bool}]}
- **MEPRigidSegmentParameters**: {?width: float, ?height: float, ?shape: MEPCrossSectionShape}
- **MEPRoutingAnchor**: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight"
- **MEPRoutingElementData**: {domain: MEPDomain, nodeCoordinates: [Coordinate3D], ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionShape: MEPCrossSectionShape, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?mepSystemId: AttributeId, ?layerIndex: int, ?floorIndex: int, ?defaults: {?routingNode: {?elbow: {?preferenceTableId: Guid, ?factorRadius: float}, ?transition: {?preferenceTableId: Guid}}}}
- **MEPRoutingElementDetails**: {domain: MEPDomainOrUnknown, mepSystemId: AttributeId, ?floorIndex: int, ?offsetFromHomeStory: float, ?branchPreferenceTableId: Guid, ?logicallyConnectedPortIdAtRouteBegin: Guid, ?logicallyConnectedPortIdAtRouteEnd: Guid, ?cutPlanePosition: MEPCutPlanePosition, ?floorPlanDisplayOption: MEPFloorPlanDisplayOption, ?showProjection: MEPShowProjection, ?onStoryVisibility: MEPOnStoryVisibility, polyline: [Coordinate3D], segments: [MEPRoutingSegmentDetails], nodes: [MEPRoutingNodeDetails]}
- **MEPRoutingElementDetailsOrError**: MEPRoutingElementDetails | ErrorItem
- **MEPRoutingElementDetailsOrErrors**: [MEPRoutingElementDetailsOrError]
- **MEPRoutingElementModificationData**: {elementId: ElementId, ?mepSystemId: AttributeId, ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionShape: MEPCrossSectionShape, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?branchPreferenceTableId: Guid, ?anchor: MEPRoutingAnchor, ?referenceLineOffsetX: float, ?referenceLineOffsetY: float, ?wallThickness: float, ?flangeSize: float, ?insulationThickness: float, ?connectionStyle: MEPConnectionStyle, ?preferredTransitionPlacement: MEPPreferredTransitionPlacement, ?cutPlanePosition: MEPCutPlanePosition, ?floorPlanDisplayOption: MEPFloorPlanDisplayOption, ?showProjection: MEPShowProjection, ?onStoryVisibility: MEPOnStoryVisibility, ?nodePositions: [Coordinate3D]}
- **MEPRoutingNodeDetails**: {elementId: ElementId, ?routingElementId: ElementId, position: Coordinate3D, ?incomingSegmentId: ElementId, ?outgoingSegmentId: ElementId, ?preferredTransitionPlacement: MEPPreferredTransitionPlacement, ?elbows: Elements, ?transitions: Elements}
- **MEPRoutingNodeParameters**: {?preferredTransitionPlacement: "SmallToLarge"|"LargeToSmall", ?elbow: MEPElbowParameters, ?transition: MEPTransitionParameters}
- **MEPRoutingNodeParametersUpdate**: {?elbow: {?factorRadius: float, ?preferenceTableId: Guid}, ?transition: {?preferenceTableId: Guid}}
- **MEPRoutingParameters**: {elementId: ElementId, type: "RoutingElement"|"RoutingNode"|"RoutingSegment", ?routingNodeParameters: MEPRoutingNodeParameters, ?routingSegmentParameters: MEPRoutingSegmentParameters, ?elbowParameters: MEPElbowParameters, ?transitionParameters: MEPTransitionParameters, ?rigidSegmentParameters: MEPRigidSegmentParameters}
- **MEPRoutingSegmentDefaults**: {?crossSectionShape: MEPCrossSectionShape, ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionReferenceId: int, ?preferenceTableId: Guid}
- **MEPRoutingSegmentDetails**: {elementId: ElementId, ?routingElementId: ElementId, crossSectionWidth: float, crossSectionHeight: float, crossSectionShape: string, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?beginNodeId: ElementId, ?endNodeId: ElementId, ?anchor: MEPRoutingAnchor, ?referenceLineOffsetX: float, ?referenceLineOffsetY: float, ?wallThickness: float, ?flangeSize: float, ?insulationThickness: float, ?connectionStyle: MEPConnectionStyle, ?rigidSegments: Elements}
- **MEPRoutingSegmentParameters**: {?crossSectionShape: MEPCrossSectionShape, ?crossSectionWidth: float, ?crossSectionHeight: float, ?crossSectionReferenceId: int, ?preferenceTableId: Guid, ?anchor: string, ?referenceLineOffsetX: float, ?referenceLineOffsetY: float, ?wallThickness: float, ?flangeSize: float, ?connectionStyle: "SimpleBody"|"Flanged"|"Welded"}
- **MEPShowProjection**: "ToFloorPlanRange"|"ToAbsoluteDisplayLimit"|"EntireElement"
- **MEPSystemAttribute**: {attributeId: AttributeId, index: int, name: string, ?domain: [MEPDomain], ?contourPen: int, ?fillPen: int, ?fillBackgroundPen: int, ?centerLinePen: int, ?fillId: AttributeIdArrayItem, ?centerLineTypeId: AttributeIdArrayItem, ?materialId: AttributeIdArrayItem, ?insulationMaterialId: AttributeIdArrayItem}
- **MEPSystemAttributeField**: "domain"|"contourPen"|"fillPen"|"fillBackgroundPen"|"centerLinePen"|"fillId"|"centerLineTypeId"|"materialId"|"insulationMaterialId"
- **MEPSystemAttributeOrError**: MEPSystemAttribute | ErrorItem
- **MEPSystemGroupData**: {name: string}
- **MEPSystemGroupDetails**: {systemGroupId: MEPSystemGroupId, name: string, ?isEditable: bool, physicalSystems: [MEPPhysicalSystemDetailsOrError]}
- **MEPSystemGroupDetailsOrError**: MEPSystemGroupDetails | ErrorItem
- **MEPSystemGroupId**: {guid: Guid}
- **MEPSystemGroupIdOrError**: {systemGroupId: MEPSystemGroupId} | ErrorItem
- **MEPSystemGroupModificationData**: {systemGroupId: MEPSystemGroupId, name: string}
- **MEPTakeOffCreationData**: {?domain: MEPDomain, segmentId: ElementId, distanceFromBeginning: float, ?rotationAroundMainAxis: float, ?length: float, ?defaults: {?removeInsulation: bool}}
- **MEPTransitionDefaults**: {?preferenceTableId: Guid}
- **MEPTransitionParameters**: {?angle: float, ?offsetY: float, ?offsetZ: float, ?preferenceTableId: Guid}
- **MEPTransitionPreferenceTable**: {guid: string, name: string, ?isEditable: bool, rows: [{?index: MEPPreferenceRowIndex, beginReferenceId: int, endReferenceId: int, beginDiameter: float, endDiameter: float, ?length: float, ?angle: float, ?description: string, ?isValid: bool}]}
- **MEPValuePreferenceTable**: {guid: string, ?name: string, ?isEditable: bool, ?useIndividualSegmentLengths: bool, ?minimumSegmentationLength: float, ?maximumSegmentationLength: float, rows: [{?index: MEPPreferenceRowIndex, value: float, ?description: string}]}
- **ManualZoneGeometry**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D}
- **MergedElements**: {mergedElements: Elements}
- **MergedElementsOrError**: MergedElements | ErrorItem
- **MeshDetails**: {?floorIndex: int, level: float, skirtType: MeshSkirtType, skirtLevel: float, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [MeshSubline]}
- **MeshModificationData**: {?floorIndex: int, ?level: float, ?skirtType: MeshSkirtType, ?skirtLevel: float, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, ?polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: [Hole3D], ?sublines: [MeshSubline]}
- **MeshRidges**: "AllSharp"|"AllSmooth"|"UserDefined"
- **MeshSkirtType**: "SurfaceOnlyWithoutSkirt"|"WithSkirt"|"SolidBodyWithSkirt"
- **MeshSubline**: {coordinates: [Coordinate3D]}
- **MissingLibraryPartName**: {elementId: ElementId, libPartName: string}
- **Model3DCount**: {componentType: "Body"|"Pgon"|"Pedg"|"Edge"|"Vert"|"Vect"|"Umat"|"Lght", count: int}
- **ModelViewOptionId**: {guid: Guid}
- **MorphBody**: {?bodyType: "Solid"|"Surface", ?isClosed: bool, ?edgeDefault: "HardVisible"|"HardHidden"|"SoftHidden", vertices: [Coordinate3D], ?polygons: [MorphPolygon], ?wireEdges: [{vertexIds: [int]}], ?edgeOverrides: [{vertexIds: [int], ?hidden: bool, ?smooth: bool, ?silhouetteOnly: bool}]}
- **MorphDetails**: {origin: Coordinate3D, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?buildingMaterialId: AttributeId, ?surfaceId: AttributeId, body: MorphBody, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float}
- **MorphPolygon**: {vertexIds: [int], ?filled: bool, ?holes: [MorphPolygonHole], ?surfaceId: AttributeId}
- **MorphPolygonHole**: {vertexIds: [int]}
- **MorphQuantities**: {volume: float, surface: float, floorPlanArea: float, floorPlanPerimeter: float, height: float}
- **NameKind**: "Story"|"Layer"|"LayerCombination"|"BuildingMaterial"|"Composite"|"Profile"|"Surface"|"Fill"|"Line"|"ZoneCategory"|"ElementType"|"Property"|"Classification"
- **NameMatch**: {kind: NameKind, name: string, match: "exact"|"normalized"|"words"|"contains"|"similar", score: float, ?storyIndex: int, ?level: float, ?attributeId: AttributeId, ?attributeIndex: int, ?elementType: ElementType, ?propertyId: PropertyId, ?propertyGroupId: PropertyGroupId, ?propertyGroupName: string, ?propertyType: "StaticBuiltIn"|"DynamicBuiltIn"|"Custom", ?propertyCollectionType: "Undefined"|"Single"|"List"|"SingleChoiceEnumeration"|"MultipleChoiceEnumeration", ?propertyValueType: "Undefined"|"Integer"|"Real"|"String"|"Boolean"|"Guid", ?propertyMeasureType: "Undefined"|"Default"|"Length"|"Area"|"Volume"|"Angle", ?propertyIsEditable: bool, ?availability: ClassificationItemIds, ?classificationSystemId: ClassificationSystemId, ?classificationSystemName: string, ?classificationItemId: ClassificationItemId, ?classificationItemCode: string}
- **NavigatorItem**: {navigatorItemId: NavigatorItemId, type: NavigatorItemType, name: string, prefix: string, uiId: string, customUiId: bool, customName: bool, isIndependent: bool, ?sourceNavigatorItemId: NavigatorItemId, ?childCount: int, ?children: [NavigatorItemArrayItem]}
- **NavigatorItemArrayItem**: {navigatorItem: NavigatorItem}
- **NavigatorItemId**: {guid: Guid}
- **NavigatorItemIdArrayItem**: {navigatorItemId: NavigatorItemId}
- **NavigatorItemIdOrDatabaseIdAndWindowType**: NavigatorItemIdArrayItem | DatabaseIdAndWindowType
- **NavigatorItemIdOrError**: NavigatorItemIdArrayItem | ErrorItem
- **NavigatorItemIds**: [NavigatorItemIdArrayItem]
- **NavigatorItemType**: "UndefinedItem"|"ProjectItem"|"StoryItem"|"SectionItem"|"DetailDrawingItem"|"PerspectiveItem"|"AxonometryItem"|"ListItem"|"ScheduleItem"|"TocItem"|"CameraItem"|"CameraSetItem"|"InfoItem"|"HelpItem"|"LayoutItem"|"MasterLayoutItem"|"BookItem"|"MasterFolderItem"|"SubSetItem"|"TextListItem"|"ElevationItem"|"InteriorElevationItem"|"WorksheetDrawingItem"|"DocumentFrom3DItem"|"FolderItem"|"DrawingItem"|"UnknownItem"
- **NavigatorParentItem**: {navigatorItemId: NavigatorItemId, type: NavigatorItemType, name: string}
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
- **NoteAutoTextKeyword**: {keyword: string}
- **NoteAutotextDetails**: {autotextId: int, elementTypes: [ElementType]}
- **ObjectDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, origin: Coordinate3D, dimensions: Coordinate3D, angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?lightColor: ColorRGB, ?lightIsOn: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings}
- **OpeningRelationsOfElement**: {openingRelations: {?fromRoom: ElementId, ?toRoom: ElementId}}
- **OpeningRevealOffsetData**: {elementId: ElementId, ?coreOffset: float, ?sideOffset: float}
- **OpeningRevealOffsets**: {coreOffset: float, sideOffset: float}
- **OverriddenMaterial**: {overridden: bool, ?attributeId: AttributeId}
- **OverriddenPen**: {overridden: bool, ?penIndex: int}
- **OverriddenValue**: {overridden: bool, ?attributeId: AttributeId, ?penIndex: int, ?color: {red: float, green: float, blue: float}}
- **PartialStructureDisplay**: "EntireStructure"|"CoreOnly"|"WithoutFinishes"|"StructureOnly"
- **PenData**: {index: int, ?color: ColorRGB, ?width: float, ?description: string}
- **PenTableAttribute**: {attributeId: AttributeId, index: int, name: string, ?isActiveForModel: bool, ?isActiveForLayout: bool, ?pens: [PenTablePen]}
- **PenTableAttributeField**: "isActiveForModel"|"isActiveForLayout"|"pens"
- **PenTableAttributeOrError**: PenTableAttribute | ErrorItem
- **PenTablePen**: {index: int, color: ColorRGB, width: float, description: string}
- **PerspectiveProjectionParameters**: {cameraPosition: Coordinate3D, targetPosition: Coordinate3D, distance: float, azimuth: float, viewCone: float, rollAngle: float, isTwoPointPersp: bool, ?sun: ProjectionSunSettings}
- **PlaceSettingsUpdate**: {?longitude: float, ?latitude: float, ?altitude: float, ?north: float, ?year: int, ?month: int, ?day: int, ?hour: int, ?minute: int, ?second: int, ?sumTime: bool, ?timeZoneInMinutes: int, ?timeZoneOffset: int}
- **PlotterInfo**: {name: string, model: string}
- **PolyArc**: {begIndex: int, endIndex: int, arcAngle: float}
- **PolygonAncestry**: {contours: [PolygonContourAncestry]}
- **PolygonContourAncestry**: {vertices: [PolygonVertexAncestry], edges: [PolygonEdgeAncestry]}
- **PolygonEdgeAncestry**: {contourIndex: int, index: int}
- **PolygonInputMethod**: "General"|"Rect"|"RotRect"|"Polyline"
- **PolygonRegularizationData**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D}
- **PolygonVertexAncestry**: {contourIndex: int, index: int}
- **PolylineAncestry**: {vertices: [PolylineVertexAncestry], edges: [PolylineEdgeAncestry]}
- **PolylineDetails**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **PolylineEdgeAncestry**: {index: int}
- **PolylineRegularizationData**: {coordinates: [Coordinate2D], ?arcs: [PolyArc]}
- **PolylineSettings**: {?coordinates: [Coordinate2D], ?arcs: [PolyArc], ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **PolylineVertexAncestry**: {index: int}
- **PossibleEnumValues**: [{enumValue: EnumValue}]
- **PossibleNumericValues**: [{?value: float, ?flag: string, ?stepBegin: float, ?stepValue: float, ?description: string}]
- **PossibleStringValues**: [string]
- **PrinterInfo**: {name: string, portrait: bool}
- **PrinterPrintArea**: "currentView"|"entireDrawing"|"marquee"|"unknown"
- **ProductDomain**: "Architecture"|"MEP"
- **ProfileAttribute**: {attributeId: AttributeId, index: int, name: string, ?wallType: bool, ?beamType: bool, ?coluType: bool, ?handrailType: bool, ?otherGDLObjectType: bool, ?useWith: [ProfileUseWith], ?width: float, ?height: float, ?minimumWidth: float, ?minimumHeight: float, ?widthStretchable: bool, ?heightStretchable: bool, ?hasCoreSkin: bool, ?profileModifiers: [ProfileModifier], ?skins: [ProfileSkin]}
- **ProfileAttributeField**: "wallType"|"beamType"|"coluType"|"handrailType"|"otherGDLObjectType"|"useWith"|"width"|"height"|"minimumWidth"|"minimumHeight"|"widthStretchable"|"heightStretchable"|"hasCoreSkin"|"profileModifiers"|"skins"|"skinOutlines"
- **ProfileAttributeOrError**: ProfileAttribute | ErrorItem
- **ProfileEdge**: {?buildingMaterialId: AttributeIdArrayItem, ?pen: int, ?lineTypeId: AttributeIdArrayItem, ?isVisibleLine: bool, ?isCutEndLine: bool, ?isInnerLine: bool}
- **ProfileEdgeOverride**: {edgeIndex: int, ?pen: int, ?isVisibleLine: bool, ?isInnerLine: bool, ?isCutEndLine: bool, ?lineTypeId: AttributeIdArrayItem, ?buildingMaterialId: AttributeIdArrayItem}
- **ProfileModifier**: {?name: string, ?value: float}
- **ProfileSkin**: {?skinId: string, ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edges: [ProfileEdge], ?outlineCoords: [Coordinate2D], ?outlineSubPolyEnds: [int], ?outlineArcs: [{begIndex: int, endIndex: int, arcAngle: float}]}
- **ProfileSkinContour**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc]}
- **ProfileSkinData**: {contours: [ProfileSkinContour], ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edgeOverrides: [ProfileEdgeOverride]}
- **ProfileUseWith**: "Wall"|"Beam"|"Column"|"Handrail"|"Other"
- **ProjectAttributes**: {attributesByType: [ProjectAttributesByType | ErrorItem]}
- **ProjectAttributesByType**: {attributeType: AttributeType, attributes: AttributeHeaders}
- **ProjectDataKey**: {name: string, guid: string, clientOnly: bool, ?teamworkOwner: User}
- **ProjectDataName**: string
- **ProjectDataReservationConflict**: {name: string, user: User}
- **ProjectDataValue**: {name: string, content: string}
- **ProjectDataValueData**: {name: string, content: string, ?clientOnly: bool, ?unique: bool}
- **ProjectInfoField**: {projectInfoId: string, projectInfoName: string, projectInfoValue: string}
- **ProjectInfoFieldData**: {projectInfoName: string, ?projectInfoValue: string, ?projectInfoGroupId: ProjectInfoGroupId}
- **ProjectInfoFieldId**: {guid: Guid}
- **ProjectInfoFieldIdArrayItem**: {projectInfoFieldId: ProjectInfoFieldId}
- **ProjectInfoFields**: [ProjectInfoField]
- **ProjectInfoGroup**: {projectInfoGroupId: ProjectInfoGroupId, name: string, fields: [ProjectInfoGroupField]}
- **ProjectInfoGroupField**: {projectInfoFieldId: ProjectInfoFieldId, name: string, value: string, ?projectInfoId: string}
- **ProjectInfoGroupId**: {guid: Guid}
- **ProjectInfoGroupIdArrayItem**: {projectInfoGroupId: ProjectInfoGroupId}
- **ProjectInfoGroupIdOrError**: ProjectInfoGroupIdArrayItem | ErrorItem
- **ProjectInfoGroupIdsOrErrors**: [ProjectInfoGroupIdOrError]
- **ProjectInfoGroupMove**: {projectInfoGroupId: ProjectInfoGroupId, ?beforeProjectInfoGroupId: ProjectInfoGroupId}
- **ProjectInfoGroupRename**: {projectInfoGroupId: ProjectInfoGroupId, name: string}
- **ProjectInfoGroups**: [ProjectInfoGroup]
- **ProjectLocation**: {longitude: float, latitude: float, altitude: float, north: float}
- **ProjectLocationUpdate**: {?longitude: float, ?latitude: float, ?altitude: float, ?north: float}
- **ProjectionSunSettings**: {?sunPositionOption: "Angles"|"DateAndTime", ?sunAzimuth: float, ?sunAltitude: float, ?year: int, ?month: int, ?day: int, ?hour: int, ?minute: int, ?second: int, ?summerTime: bool}
- **PropertyAvailabilityUpdate**: {?set: [ClassificationItemIdArrayItem], ?add: [ClassificationItemIdArrayItem], ?remove: [ClassificationItemIdArrayItem]}
- **PropertyDataType**: "number"|"integer"|"string"|"boolean"|"length"|"area"|"volume"|"angle"|"numberList"|"integerList"|"stringList"|"booleanList"|"lengthList"|"areaList"|"volumeList"|"angleList"|"singleEnum"|"multiEnum"
- **PropertyDefaultValue**: BasicDefaultValue | ExpressionDefaultValue
- **PropertyDefinition**: {name: string, description: string, type: PropertyDataType, isEditable: bool, ?defaultValue: PropertyDefaultValue, ?possibleEnumValues: PossibleEnumValues, availability: [ClassificationItemIdArrayItem], group: {?propertyGroupId: PropertyGroupId, ?name: string}}
- **PropertyDefinitionArrayItem**: {propertyDefinition: PropertyDefinition}
- **PropertyDefinitionType**: "StaticBuiltIn"|"DynamicBuiltIn"|"Custom"
- **PropertyDefinitionUpdate**: {propertyId: PropertyId, ?name: string, ?description: string, ?isEditable: bool, ?groupId: PropertyGroupId, ?defaultValue: PropertyDefaultValue, ?expressions: [string], ?availability: PropertyAvailabilityUpdate, ?possibleEnumValues: EnumValuesToAdd, ?renameEnumValues: [PropertyEnumValueRename], ?removeEnumValues: [PropertyEnumValueRemoval], ?enumOrder: [string]}
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
- **PropertyValueArrayItem**: {propertyValue: PropertyValue, ?isAvailable: bool}
- **PropertyValueDetails**: NormalOrUserUndefinedPropertyValue | NotAvailablePropertyValue
- **PropertyValueErrorItem**: {error: Error, ?isAvailable: bool}
- **PropertyValueOrErrorItem**: PropertyValueArrayItem | PropertyValueErrorItem
- **PropertyValues**: [PropertyValueOrErrorItem]
- **PropertyValuesArrayItem**: {propertyValues: PropertyValues}
- **PropertyValuesOrError**: PropertyValuesArrayItem | ErrorItem
- **PropertyValuesOrErrorArray**: [PropertyValuesOrError]
- **RailingDetails**: {referenceLine: [Coordinate2D], bottomOffset: float, zCoordinate: float, height: float, segmentHeights: [float], visibility: StoryVisibility, isAutoOnStoryVisibility: bool, referenceLinePen: int, contourPen: int}
- **RegularizedPolygon**: {polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], holes: Holes2D, ?ancestry: PolygonAncestry}
- **RegularizedPolygons**: {polygons: [RegularizedPolygon]}
- **RegularizedPolyline**: {coordinates: [Coordinate2D], arcs: [PolyArc], ?ancestry: PolylineAncestry}
- **RenovationFilterDetails**: {renovationFilterId: GuidId, name: string}
- **RenovationStatusName**: {status: "Existing"|"New"|"Demolished", name: string}
- **RevisionChange**: {id: string, description: string, lastModifiedTime: string, modifiedByUser: string, isIssued: bool, ?firstRevisionIssueId: RevisionIssueId, isArchived: bool, ?customSchemeData: RevisionCustomSchemeData}
- **RevisionChangeCustomSchemeItem**: {customSchemeKey: string, customSchemeName: string}
- **RevisionChangesArrayItem**: {revisionChanges: [RevisionChange]}
- **RevisionChangesOfEntities**: [RevisionChangesArrayItem | ErrorItem]
- **RevisionCustomSchemeData**: [RevisionCustomSchemeEntry]
- **RevisionCustomSchemeEntry**: {customSchemeKey: Guid, customSchemeValue: string}
- **RevisionIssue**: {revisionIssueId: RevisionIssueId, id: string, description: string, issueTime: string, issuedByUser: string, overrideRevisionIDOfAllIncludedLayouts: bool, createNewRevisionInAllIncludedLayouts: bool, ?markersVisibleSinceIndex: int, isIssued: bool, ?documentRevisions: DocumentRevisionReferences, ?customSchemeData: RevisionCustomSchemeData}
- **RevisionIssueId**: {guid: Guid}
- **RoofDetails**: {roofClass: "SinglePlane"|"MultiPlane", structureType: RoofStructureType, thickness: float, level: float, zCoordinate: float, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?materialsChained: bool, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?fillVisibility: StoryVisibility, ?cutBodyType: "Editable"|"ContoursDown"|"PivotLinesDown"|"UpwardsExtrusion"|"DownwardsExtrusion", ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?sectionContourPen: int, ?sectionContourLineTypeId: AttributeId, ?contourPen: int, ?contourLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?floorFill: ShellBaseFloorFill, ?angle: float, ?pivotLine: RoofDetailsPivotLine, ?eavesOverhang: float, ?levels: [RoofDetailsLevel], ?pivotPolygonOutline: [Coordinate2D], polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?edgeSideMaterials: [OverriddenMaterial], ?edgeTrims: [RoofEdgeTrim], ?pivotEdges: [{levels: [{angle: float, eavesOverhang: float, angleType: "Sloped"|"Gable"}]}]}
- **RoofDetailsLevel**: {height: float, angle: float}
- **RoofDetailsPivotLine**: {begin: Coordinate2D, end: Coordinate2D}
- **RoofEdgeTrim**: {?trimType: "Vertical"|"Perpendicular"|"Horizontal"|"CustomAngle"|"AlignWithCut", ?angle: float}
- **RoofLevel**: {levelHeight: float, levelAngle: float}
- **RoofOrShellRelationsOfElement**: {roofOrShellRelations: {connectedRooms: Elements}}
- **RoofPivotLine**: {begCoordinate: Coordinate2D, endCoordinate: Coordinate2D}
- **RoofQuantities**: {volume: float, volumeConditional: float, grossVolume: float, topSurface: float, bottomSurface: float, edgeSurface: float, topSurfaceConditional: float, bottomSurfaceConditional: float, grossTopSurface: float, grossBottomSurface: float, grossEdgeSurface: float, contourArea: float, perimeter: float, holesSurface: float, holesPerimeter: float, openingsSurface: float, ridgesLength: float, valleysLength: float, hipsLength: float, gablesLength: float, eavesLength: float, peaksLength: float}
- **RoofStructureType**: "Basic"|"Composite"
- **ScreenPoint**: {h: int, v: int}
- **ScreenPointInput**: {h: int, v: int}
- **SectionDetails**: {name: string, idStr: string, mainCoordinates: [Coordinate2D], depthCoordinates: [Coordinate2D], ?startCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?depth: float, ?viewDirection: Coordinate2D}
- **SectionElevationDetails**: {?name: string, ?id: string, ?linePenIndex: int, ?textPenIndex: int, ?lineTypeId: AttributeId, ?sectionLinePenIndex: int, ?sectionFillPenIndex: int, ?sectionFillBackgroundPenIndex: int, ?horizontalRange: "Infinite"|"Limited"|"ZeroDepth", ?verticalRange: "Infinite"|"Limited"|"FitToZoneRange", ?verticalRangeStoryBaseNumber: int, ?relativeToStory: bool, ?verticalRangeMin: float, ?verticalRangeMax: float, ?markerSize: float, ?showMarkerAtBeginning: bool, ?showMarkerAtEnd: bool, ?useElementPens: bool, ?showLineAtBeginning: bool, ?showLineAtMiddle: bool, ?showLineAtEnd: bool, ?textSize: float, ?fontIndex: int, ?effectVectorHatch: bool, ?effectVectorShadow: bool, ?effectSunFrom3D: bool, ?shadowFillId: AttributeId, ?shadowFillPenIndex: int, ?shadowFillBackgroundPenIndex: int, ?limitLineTypeId: AttributeId, ?limitLinePenIndex: int, ?continuous: bool, ?sunAzimuth: float, ?sunAltitude: float, ?useOneModelPen: bool, ?modelPenIndex: int, ?modelUncutSurfaceFillType: "PenColor"|"MaterialColorShaded"|"MaterialColorNonShaded", ?modelUncutSurfaceFillBackgroundPenIndex: int, ?useUncutSurfaceFill: bool, ?transparent: bool, ?markedDistantArea: bool, ?useOneDistantAreaPen: bool, ?distantAreaPenIndex: int, ?distantAreaUncutSurfaceFillBackgroundPenIndex: int, ?useUncutSurfaceFillInDistantArea: bool, ?storyHandleAppearance: "None"|"DisplayOnly"|"All", ?storyHandleLineTypeId: AttributeId, ?storyHandleLinePenIndex: int, ?storyHandleMarkerPenIndex: int, ?storyHandleUseSymbolPens: bool, ?storyHandleLeftMarkerVisible: bool, ?storyHandleRightMarkerVisible: bool, ?storyHandleLineVisible: bool, ?storyHandleLeftMarkerOffset: float, ?storyHandleRightMarkerOffset: float, ?storyHandleMarkerFontIndex: int, ?storyHandleMarkerTextSize: float, ?storyHandleMarkerSize: float, ?boundaryDisplayMode: "UncutContours"|"NoContours"|"OverrideContours", ?boundaryPenIndex: int, ?boundaryLineTypeId: AttributeId, ?showOnStories: "All"|"OneStory"|"InRange"|"PartRange", ?storyToShowOn: int, ?markerShowType: "MiddleMarker"|"WingMarkers", ?intendedPlanConnectivity: "Online"|"Offline"|"Drawing", ?distantAreaShadowFillId: AttributeId, ?distantAreaShadowFillPenIndex: int, ?distantAreaShadowFillBackgroundPenIndex: int, ?distantAreaUncutSurfaceFillType: "PenColor"|"MaterialColorShaded"|"MaterialColorNonShaded", ?currentPlanConnectivity: "Online"|"Offline"|"Drawing", ?isWindowOpened: bool, ?isActive: bool, ?isSourceMarker: bool, ?isInDrawingMode: bool, ?beginMarkerElementId: ElementIdArrayItem, ?middleMarkerElementId: ElementIdArrayItem, ?endMarkerElementId: ElementIdArrayItem}
- **SectionElevationDetailsOrError**: SectionElevationDetails | ErrorItem
- **SectionElevationSettableDetails**: {?linePenIndex: int, ?textPenIndex: int, ?lineTypeId: AttributeId, ?sectionLinePenIndex: int, ?sectionFillPenIndex: int, ?sectionFillBackgroundPenIndex: int, ?horizontalRange: "Infinite"|"Limited"|"ZeroDepth", ?verticalRange: "Infinite"|"Limited"|"FitToZoneRange", ?verticalRangeStoryBaseNumber: int, ?relativeToStory: bool, ?verticalRangeMin: float, ?verticalRangeMax: float, ?markerSize: float, ?showMarkerAtBeginning: bool, ?showMarkerAtEnd: bool, ?useElementPens: bool, ?showLineAtBeginning: bool, ?showLineAtMiddle: bool, ?showLineAtEnd: bool, ?textSize: float, ?fontIndex: int, ?effectVectorHatch: bool, ?effectVectorShadow: bool, ?effectSunFrom3D: bool, ?shadowFillId: AttributeId, ?shadowFillPenIndex: int, ?shadowFillBackgroundPenIndex: int, ?limitLineTypeId: AttributeId, ?limitLinePenIndex: int, ?continuous: bool, ?sunAzimuth: float, ?sunAltitude: float, ?useOneModelPen: bool, ?modelPenIndex: int, ?modelUncutSurfaceFillType: "PenColor"|"MaterialColorShaded"|"MaterialColorNonShaded", ?modelUncutSurfaceFillBackgroundPenIndex: int, ?useUncutSurfaceFill: bool, ?transparent: bool, ?markedDistantArea: bool, ?useOneDistantAreaPen: bool, ?distantAreaPenIndex: int, ?distantAreaUncutSurfaceFillBackgroundPenIndex: int, ?useUncutSurfaceFillInDistantArea: bool, ?storyHandleAppearance: "None"|"DisplayOnly"|"All", ?storyHandleLineTypeId: AttributeId, ?storyHandleLinePenIndex: int, ?storyHandleMarkerPenIndex: int, ?storyHandleUseSymbolPens: bool, ?storyHandleLeftMarkerVisible: bool, ?storyHandleRightMarkerVisible: bool, ?storyHandleLineVisible: bool, ?storyHandleLeftMarkerOffset: float, ?storyHandleRightMarkerOffset: float, ?storyHandleMarkerFontIndex: int, ?storyHandleMarkerTextSize: float, ?storyHandleMarkerSize: float, ?boundaryDisplayMode: "UncutContours"|"NoContours"|"OverrideContours", ?boundaryPenIndex: int, ?boundaryLineTypeId: AttributeId, ?showOnStories: "All"|"OneStory"|"InRange"|"PartRange", ?storyToShowOn: int, ?markerShowType: "MiddleMarker"|"WingMarkers", ?intendedPlanConnectivity: "Online"|"Offline"|"Drawing"}
- **SegmentStructureType**: "Basic"|"Profile"
- **SetGDLParameterArray**: [SetGDLParameterDetails]
- **SetGDLParameterByIndexDetails**: {index: int, ?index1: int, ?index2: int, value: any}
- **SetGDLParameterByNameDetails**: {name: string, ?index1: int, ?index2: int, value: any}
- **SetGDLParameterDetails**: SetGDLParameterByNameDetails | SetGDLParameterByIndexDetails
- **ShellBaseFloorFill**: {?use: bool, ?foregroundPen: int, ?backgroundPen: int, ?fillId: AttributeId, ?use3DHatching: bool, ?useFillLocBaseLine: bool, ?useSlantedFill: bool, ?orientation: HatchOrientation}
- **ShellCutPolygon**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?plane: CoordinateSystem3D, ?depth: float}
- **ShellDetails**: {shellClass: "Extruded"|"Revolved"|"Ruled", structureType: ShellStructureType, thickness: float, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?fillVisibility: StoryVisibility, ?cutBodyType: "Editable"|"ContoursDown"|"PivotLinesDown"|"UpwardsExtrusion"|"DownwardsExtrusion", ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?sectionContourPen: int, ?sectionContourLineTypeId: AttributeId, ?contourPen: int, ?contourLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?floorFill: ShellBaseFloorFill}
- **ShellEdgeTrim**: {trimType: "Vertical"|"Perpendicular"|"Horizontal"|"CustomAngle", ?angle: float}
- **ShellProfile**: {coordinates: [Coordinate2D], ?arcs: [PolyArc], ?closed: bool}
- **ShellQuantities**: {volume: float, volumeConditional: float, grossVolume: float, referenceSurface: float, oppositeSurface: float, edgeSurface: float, referenceSurfaceConditional: float, oppositeSurfaceConditional: float, grossReferenceSurface: float, grossOppositeSurface: float, grossEdgeSurface: float, perimeter: float, holesSurface: float, holesPerimeter: float, floorPlanArea: float}
- **ShellStructureType**: "Basic"|"Composite"
- **SkippedLibraryPart**: {?index: int, ?code: int}
- **SkylightDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, anchorPosition: Coordinate2D, ?anchorPoint: "BottomCenter"|"BottomLeft"|"BottomRight"|"TopCenter"|"TopLeft"|"TopRight", ?fixMode: "Horizontal"|"Vertical", anchorLevel: float, width: float, height: float, azimuthAngle: float, elevationAngle: float, ?reflected: bool, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?surfaceId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool}
- **SkylightHolePolygon**: {polygonOutline: [Coordinate2D], holes: Holes2D}
- **SlabDetails**: {thickness: float, level: float, offsetFromTop: float, zCoordinate: float, polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], holes: Holes2D, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?floorFill: FloorFill}
- **SlabQuantities**: {volume: float, volumeConditional: float, grossVolume: float, topSurface: float, bottomSurface: float, edgeSurface: float, topSurfaceConditional: float, bottomSurfaceConditional: float, grossTopSurface: float, grossBottomSurface: float, grossEdgeSurface: float, perimeter: float, holesSurface: float, holesPerimeter: float}
- **SlabReferencePlaneLocation**: "Top"|"CoreTop"|"CoreBottom"|"Bottom"
- **SlabStructureType**: "Basic"|"Composite"
- **SnapFilter**: {?base: "All"|"None"|"Edges"|"Nodes", ?include: [SnapType], ?exclude: [SnapType]}
- **SnapType**: "Wall"|"WallOn"|"Column"|"ColumnOn"|"Beam"|"BeamOn"|"Window"|"WindowOn"|"Door"|"DoorOn"|"Object"|"ObjectOn"|"Slab"|"SlabOn"|"Roof"|"RoofOn"|"Mesh"|"MeshOn"|"Shell"|"ShellOn"|"Morph"|"MorphOn"|"Skylight"|"SkylightOn"|"CurtainWall"|"CurtainWallOn"|"Stair"|"StairOn"|"Railing"|"RailingOn"|"Zone"|"ZoneOn"|"Hatch"|"HatchOn"|"Line"|"LineOn"|"PolyLine"|"PolyLineOn"|"Arc"|"ArcOn"|"Circle"|"CircleOn"|"Spline"|"SplineOn"|"Hotspot"|"Text"|"Label"|"Dimension"|"DimensionOn"
- **SolidLinkData**: {targetId: ElementId, operatorId: ElementId, operation: SolidOperationType, ?linkFlags: SolidLinkFlags}
- **SolidLinkFlags**: {inheritOperatorAttributes: bool, skipPolygonHoles: bool}
- **SolidLinkReference**: {targetId: ElementId, operatorId: ElementId}
- **SolidLinksOfElement**: {solidLinksWithTheGivenTarget: [{operatorId: ElementId, operation: SolidOperationType, linkFlags: SolidLinkFlags, ?linkTime: string}], solidLinksWithTheGivenOperator: [{targetId: ElementId, operation: SolidOperationType, linkFlags: SolidLinkFlags, ?linkTime: string}]}
- **SolidOperationType**: "Subtraction"|"SubtractionUpwards"|"SubtractionDownwards"|"Intersection"|"Addition"
- **SpecialFolderPath**: {path: string}
- **SpecialFolderPathOrError**: SpecialFolderPath | ErrorItem
- **SpecialFolderPathsOrErrors**: [SpecialFolderPathOrError]
- **SpecialFolderType**: "ApplicationPrefs"|"GraphisoftPrefs"|"GraphisoftHome"|"Cache"|"Data"|"UserDocuments"|"Temporary"|"Application"|"Defaults"|"WebObjects"|"Templates"|"Help"|"EmbeddedProjectLibrary"|"EmbeddedProjectLibraryHotlink"|"ProjectPreviews"
- **SplineDetails**: {coordinates: [Coordinate2D], closed: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId, zCoordinate: float}
- **SplineSettings**: {?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId}
- **StairBaselineData**: {baseLinePoints: [Coordinate2D], zCoordinate: float, ?floorIndex: int, ?totalHeight: float, ?flightWidth: float, ?stepNum: int, ?riserHeight: float, ?treadDepth: float, ?finishVisible: bool}
- **StairBaselineSolution**: {solution: StairBaselineSolutionState, baseLinePoints: [Coordinate2D], ?baseLineArcs: [PolyArc], totalHeight: float, flightWidth: float, stepNum: int, riserHeight: float, treadDepth: float}
- **StairBaselineSolutionState**: "Correct"|"Solved"|"NotSolved"
- **StairDetails**: {stepNum: int, riserHeight: float, treadDepth: float, flightWidth: float, totalHeight: float, level: float, zCoordinate: float, finishVisible: bool, baseLinePoints: [Coordinate2D], ?baseLineArcs: [PolyArc], ?baseLineEdges: [{segmentType: "Flight"|"Landing"|"DividedLanding"|"Unknown"}], ?baseLineVertices: [{turnType: "None"|"Landing"|"Winder"|"DividedLanding"|"Unknown", landingStartEdgeOffset: float, landingEndEdgeOffset: float, minLandingStartEdgeOffset: float, minLandingEndEdgeOffset: float}], ?stairDisplayType: "Custom"|"ByModelViewOptions"|"Unknown", ?floorPlanLayout: StairLayout, ?reflectedCeilingPlanLayout: StairLayout, ?structureVisibility: bool, ?structureSymbols: [{structureType: "UnderStructure"|"Stringer"|"Unknown", view: StairSymbolView, ?visibleLineTypeId: AttributeId, visibleLinePen: int, ?hiddenLineTypeId: AttributeId, hiddenLinePen: int, ?visibleFillId: AttributeId, visibleFillPen: int, visibleFillBackgroundPen: int, ?hiddenFillId: AttributeId, hiddenFillPen: int, hiddenFillBackgroundPen: int}], ?monolithStructureSymbols: [{view: StairSymbolView, part: StairSymbolPart, ?goingLineTypeId: AttributeId, goingLinePen: int, ?goingNosingLineTypeId: AttributeId, goingNosingLinePen: int, ?connectionLineTypeId: AttributeId, connectionLinePen: int, ?connectionDetailLineTypeId: AttributeId, connectionDetailLinePen: int, ?drainingFillId: AttributeId, drainingFillPen: int, drainingFillBackgroundPen: int, ?contourLineTypeId: AttributeId, contourLinePen: int}], ?structureVisibilityOnStories: [{view: StairSymbolView, uniformSymbolRepresentationEnabled: bool, stories: [{relevantStories: "AllStories"|"BelowRelevant"|"BottomRelevant"|"MiddleRelevant"|"TopRelevant"|"AboveRelevant"|"Unknown", structures: [{part: StairSymbolPart, structure: "Beam"|"Cantilevered"|"Stringer"|"Monolith"|"Unknown", visible: bool}], fills: [{part: StairSymbolPart, structureType: "UnderStructure"|"Stringer"|"Unknown", visible: bool}], monolithParts: [{part: StairSymbolPart, connectionVisible: bool, drainingVisible: bool, landingLineVisible: bool, structureGoingVisible: bool, structureGoingNosingVisible: bool}]}]}]}
- **StairGridType**: "NotRelevant"|"WithSingleBreaklineFull"|"NoBreaklineFull"|"BelowBreakline"|"AboveBreakline"|"MiddleBreakline"|"MiddleBreaklineFull"|"NoBreakMarkHidden"|"AboveBreakMarkHidden"|"BelowBreakMarkHidden"|"Multistory2DAllVisible"|"Multistory2DHiddenVisible"|"Multistory2DNoneVisibleHidden"|"WithBreakMarkAllVisible"|"WithBreakMarkHiddenVisible"|"Unknown"
- **StairLayout**: {visibility: StoryVisibility, isAutoOnStoryVisibility: bool, storyVisibility: "HomeStoryOnly"|"HomeAndOneStoryUp"|"HomeAndOneStoryDown"|"HomeAndOneStoryUpAndDown"|"OneStoryUp"|"OneStoryDown"|"AllStories"|"AllRelevantStories"|"AllRelevantAndOneStoryUp"|"AllRelevantAndOneStoryDown"|"Unknown", gridTypeAbove: StairGridType, gridTypeTop: StairGridType, gridTypeMiddle: StairGridType, gridTypeBottom: StairGridType, gridTypeBelow: StairGridType, showWalkingLine: bool, showNumbering: bool, showUpDownText: bool, showDescription: bool, showStructure: bool, breakLineAngleType: "AngleToVertical"|"AngleToHorizontal"|"NumberOfGoings"|"Unknown", breakLineAngle: float, breakLineAngleNumberOfGoings: int, breakLineDistance: float, breakLinePositionType: "FloorPlanCutPlaneHeight"|"CustomHeight"|"AtNthRiser"|"Unknown", upperBreakLineCustomPosition: float, lowerBreakLineCustomPosition: float, upperBreakLineNthRiserPosition: int, lowerBreakLineNthRiserPosition: int, overrideLineType: bool, ?lineTypeId: AttributeId, overridePen: bool, pen: int, overrideSymbolFill: bool, ?symbolFillId: AttributeId, symbolFillPen: int, symbolFillBackgroundPen: int}
- **StairSymbolPart**: "Visible"|"Hidden"|"Unknown"
- **StairSymbolView**: "FloorPlan"|"CeilingPlan"|"Unknown"
- **StoredGDLParameter**: {name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, ?value: any, ?valueDescription: string, ?itemDescriptions: [string], flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"]}
- **StoriesParameters**: [StoryParameters]
- **StoriesSettings**: [StorySettings]
- **StoryParameters**: {index: int, floorId: int, dispOnSections: bool, level: float, ?height: float, name: string, ?ifcId: string}
- **StorySettings**: {?index: int, dispOnSections: bool, level: float, name: string}
- **StoryVisibility**: {?showOnHome: bool, ?showAllAbove: bool, ?showAllBelow: bool, ?showRelAbove: int, ?showRelBelow: int}
- **Style3DDetails**: {name: string, ?engineId: int, ?model3D: int, ?transparency: bool, ?monochromeEnabled: bool, ?monochromeSurfaceColor: ColorRGB, ?monochromeContourColor: ColorRGB, ?backgroundAsInRendering: bool, ?chainBackgroundColors: bool, ?backgroundSkyColor: ColorRGB, ?backgroundColor: ColorRGB, ?shadingContours: int, ?vectorialSunShadow: int, ?vectorialHatching: bool, ?contourThickness: int, ?silhouetteThickness: int, ?vectorialHatchingThickness: int, ?shadowContourThickness: int, ?castShadowPercent: int, ?shadingPercent: int, ?shadowElevation: float, ?show3DHotSpotsOnly: bool}
- **SuccessfulExecutionResult**: {success: true}
- **SunDateTime**: {year: int, month: int, day: int, hour: int, minute: int, second: int, daylightSaving: bool}
- **SunDateTimeUpdate**: {?year: int, ?month: int, ?day: int, ?hour: int, ?minute: int, ?second: int, ?daylightSaving: bool}
- **SunPosition**: {azimuth: float, altitude: float}
- **SurfaceAttribute**: {attributeId: AttributeId, index: int, name: string, ?materialType: SurfaceType, ?ambientReflection: float, ?diffuseReflection: float, ?specularReflection: float, ?transparency: float, ?shine: float, ?transparencyAttenuation: float, ?emissionAttenuation: float, ?surfaceColor: ColorRGB, ?specularColor: ColorRGB, ?emissionColor: ColorRGB, ?fillId: AttributeIdArrayItem, ?texture: Texture}
- **SurfaceAttributeField**: "materialType"|"ambientReflection"|"diffuseReflection"|"specularReflection"|"transparency"|"shine"|"transparencyAttenuation"|"emissionAttenuation"|"surfaceColor"|"specularColor"|"emissionColor"|"fillId"|"texture"
- **SurfaceAttributeOrError**: SurfaceAttribute | ErrorItem
- **SurfaceType**: "General"|"Simple"|"Matte"|"Metal"|"Plastic"|"Glass"|"Glowing"|"Constant"
- **SurveyPoint**: {position: SurveyPointPosition, positionInProject: Coordinate3D, geoReferencingParameters: GeoReferencingParameters, ?isVisible: bool, ?isLocked: bool}
- **SurveyPointPosition**: {eastings: float, northings: float, elevation: float}
- **SurveyPointPositionUpdate**: {?eastings: float, ?northings: float, ?elevation: float}
- **SurveyPointUpdate**: {?position: SurveyPointPositionUpdate, ?positionInProject: Coordinate3D, ?geoReferencingParameters: GeoReferencingParametersUpdate, ?isVisible: bool, ?isLocked: bool}
- **SymbolLabelTextDirection**: "Parallel"|"Horizontal"|"Vertical"|"General"
- **TeamworkUser**: {userId: float, userName: string, fullName: string, isConnected: bool}
- **TextBoxAnchor**: "LeftTop"|"MiddleTop"|"RightTop"|"LeftMiddle"|"MiddleMiddle"|"RightMiddle"|"LeftBottom"|"MiddleBottom"|"RightBottom"
- **TextContentChange**: {elementId: ElementId, from: int, range: int, content: string}
- **TextDetails**: {text: string, ?rawText: string, position: Coordinate2D, angle: float, height: float, pen: int, justification: Justification, zCoordinate: float, style: TextStyleDetails, paragraphCount: int, ?runs: [TextRunDetails]}
- **TextMeasurement**: {length: float, longestLineIndex: int, lineLengths: [float], ?capitalSizeFactor: float}
- **TextRunDetails**: {text: string, ?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?heightOverride: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool}
- **TextSettings**: {?text: string, ?position: Coordinate2D, ?angle: float, ?height: float, ?justification: Justification}
- **TextStyleDetails**: {?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?justification: Justification, ?height: float, ?spacing: float, ?angle: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool, ?widthFactor: float, ?charSpaceFactor: float, ?fixedSize: bool, ?usedContour: bool, ?usedFill: bool, ?contourPenIndex: int, ?fillPenIndex: int, ?anchor: TextBoxAnchor, ?fixedAngle: bool, ?contourOffset: float, ?flipEnabled: bool, ?textFrameShape: "Rectangle"|"Circle"|"RoundedRectangle"|"Pill", ?textFrameSizeFixed: bool, ?textFrameFixedWidth: float, ?textFrameFixedHeight: float, ?lineCount: int, ?boxWidth: float, ?boxHeight: float, ?nonBreaking: bool}
- **TextStyleSettableDetails**: {?penIndex: int, ?fontIndex: int, ?fontName: string, ?bold: bool, ?italic: bool, ?underline: bool, ?justification: Justification, ?height: float, ?spacing: float, ?angle: float, ?effectStrikeout: bool, ?effectSuperscript: bool, ?effectSubscript: bool, ?effectProtected: bool, ?widthFactor: float, ?charSpaceFactor: float, ?fixedSize: bool, ?usedContour: bool, ?usedFill: bool, ?contourPenIndex: int, ?fillPenIndex: int, ?anchor: TextBoxAnchor, ?fixedAngle: bool, ?contourOffset: float, ?flipEnabled: bool, ?textFrameShape: "Rectangle"|"Circle"|"RoundedRectangle"|"Pill", ?textFrameSizeFixed: bool, ?textFrameFixedWidth: float, ?textFrameFixedHeight: float}
- **Texture**: {name: string, ?rotationAngle: float, ?xSize: float, ?ySize: float, ?FillRectangle: bool, ?FitPicture: bool, ?mirrorX: bool, ?mirrorY: bool, ?useAlphaChannel: bool, ?alphaChannelChangesTransparency: bool, ?alphaChannelChangesSurfaceColor: bool, ?alphaChannelChangesAmbientColor: bool, ?alphaChannelChangesSpecularColor: bool, ?alphaChannelChangesDiffuseColor: bool}
- **TextureProjectionType**: "Invalid"|"Planar"|"Default"|"Cylindric"|"Spheric"|"Box"
- **ToolDefaultClassifications**: {classificationIds: [ClassificationId]}
- **ToolDefaultProperties**: {properties: [ToolDefaultProperty]}
- **ToolDefaultProperty**: {propertyId: PropertyId, propertyName: string, propertyGroupId: PropertyGroupId, ?propertyValue: PropertyValue, ?error: Error}
- **ToolDefaultPropertyFilter**: "UserDefined"|"FundamentalBuiltIn"|"UserLevelBuiltIn"|"All"
- **TrimType**: "KeepInside"|"KeepOutside"|"KeepAll"|"No"
- **TypeSpecificDetails**: HotlinkDetails | WallDetails | BeamDetails | SlabDetails | RoofDetails | ShellDetails | ColumnDetails | ColumnSegmentDetails | BeamSegmentDetails | DetailWorksheetDetails | WindowDoorDetails | SkylightDetails | LibPartBasedElementDetails | ObjectDetails | PolylineDetails | ZoneDetails | RailingDetails | CurtainWallDetails | CurtainWallSegmentDetails | CurtainWallPanelDetails | CurtainWallFrameDetails | MeshDetails | MorphDetails | DrawingDetails | LabelDetails | TextDetails | LevelDimensionDetails | DimensionDetails | StairDetails | SectionDetails | NotYetSupportedElementTypeDetails
- **TypeSpecificSettings**: WallSettings | ZoneSettings | LineSettings | ArcSettings | HotspotSettings | SplineSettings | PolylineSettings | HatchSettings | DrawingSettings | TextSettings
- **UnitValueConversionData**: {value: float, preference: "WorkModel"|"WorkLayout"|"WorkAngle"|"DimLinear"|"DimAngle"|"DimRadial"|"DimLevel"|"DimElevation"|"DimDoorWindow"|"DimParapet"|"DimArea"|"CalcLength"|"CalcArea"|"CalcVolume"|"CalcAngle"}
- **UnusedLibraryPart**: {guid: string, index: int, documentName: string, fileName: string, typeId: LibraryPartType, isPlaceable: bool}
- **User**: {userId: float, userName: string}
- **UserDataKeysToDelete**: [string]
- **UserDataPair**: {key: string, value: string}
- **UserDataPairs**: [UserDataPair]
- **UserUndefinedPropertyValue**: {type: PropertyDataType, status: "userUndefined"}
- **ViewDepthLimitation**: "ToFloorPlanRange"|"ToAbsoluteLimit"|"EntireElement"
- **ViewImageFormat**: "png"|"jpg"
- **ViewImageSource**: "3DWindow"|"RenderingWindow"
- **ViewOptions**: {modelViewOptions: object, onScreenViewOptions: object}
- **ViewOptionsUpdate**: {?modelViewOptions: object, ?onScreenViewOptions: object}
- **ViewSettings**: {?modelViewOptions: string, ?layerCombination: string, ?dimensionStyle: string, ?penSetName: string, ?graphicOverrideCombination: string, ?drawingScale: int, ?saveZoom: bool, ?ignoreSavedZoom: bool, ?zoom: Zoom, ?saveFlags: {?zoom: bool, ?displayOptions: bool, ?layers: bool, ?drawingScale: bool, ?dimensions: bool, ?penSet: bool, ?structureDisplay: bool}, ?rotation: float, ?transformationMatrix: [float], ?translation: {x: float, y: float}, ?structureDisplay: "EntireStructure"|"CoreOnly"|"WithoutFinishes"|"StructureOnly", ?renovationFilterGuid: GuidId, ?renovationFilterName: string, ?d3styleName: string, ?renderingSceneName: string, ?usePhotoRendering: bool}
- **ViewSettingsOrError**: ViewSettings | ErrorItem
- **ViewTransformations**: {zoom: Zoom, rotation: float}
- **ViewTransformationsOrError**: ViewTransformations | ErrorItem
- **VisibleSkinStatus**: {hasVisibleSkin: bool}
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
- **WindowDoorDetails**: {libPart: LibPartDetails, ?ownerElementId: ElementId, ?ownerElementType: ElementType, width: float, height: float, sillHeight: float, centerOffset: float, reflected: bool, refSide: bool, oSide: bool, reveal: bool, revealDepthOffset: float, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectSectionAttributes: bool}
- **WindowToClose**: {databaseId: DatabaseId, ?windowType: WindowType}
- **WindowType**: "FloorPlan"|"Section"|"Details"|"3DModel"|"Layout"|"Drawing"|"CustomText"|"CustomDraw"|"MasterLayout"|"Elevation"|"InteriorElevation"|"Worksheet"|"Report"|"3DDocument"|"External3D"|"Movie3D"|"MovieRendering"|"Rendering"|"ModelCompare"|"Interactive Schedule"|"Unknown"
- **WouldChange**: {?oldValue: any, ?newValue: any}
- **WouldChangeExecutionResult**: {success: true, wouldChange: WouldChange}
- **WouldDeleteExecutionResult**: {success: true, wouldDelete: true}
- **ZoneBoundariesOfZonesWrapper**: {zoneBoundariesOfZones: [ZoneBoundariesOrError]}
- **ZoneBoundariesOrError**: ZoneBoundariesWrapper | ErrorItem
- **ZoneBoundariesWrapper**: {zoneBoundaries: [{connectedElementId: ElementId, isExternal: bool, neighbouringZoneElementId: ElementId, area: float, polygonOutline: [Coordinate3D]}]}
- **ZoneBoundaryPart**: {elementId: ElementId, ?roomEdgeIndex: int, begDistance: float, endDistance: float}
- **ZoneCategoryAttribute**: {attributeId: AttributeId, index: int, name: string, ?categoryCode: string, ?color: ColorRGB, ?stampName: string, ?stampMainGuid: string, ?stampRevGuid: string}
- **ZoneCategoryAttributeField**: "categoryCode"|"color"|"stampName"|"stampMainGuid"|"stampRevGuid"
- **ZoneCategoryAttributeOrError**: ZoneCategoryAttribute | ErrorItem
- **ZoneContourLine**: {?use: bool, ?pen: int, ?lineTypeId: AttributeId}
- **ZoneCoverFill**: {?use: bool, ?fillId: AttributeId, ?foregroundPen: int, ?backgroundPen: int}
- **ZoneCreationGeometry**: AutomaticZoneGeometry | ManualZoneGeometry
- **ZoneDetails**: {name: string, numberStr: string, categoryAttributeId: AttributeId, stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, isManual: bool, ?referencePosition: Coordinate2D, polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, zCoordinate: float, height: float, bottomOffset: float, topOffset: float, relativeTopStory: float, floorThickness: float, contourLine: ZoneContourLine, coverFill: ZoneCoverFill}
- **ZoneQuantities**: {area: float, netArea: float, calculatedArea: float, perimeter: float, netPerimeter: float, volume: float, height: float, wallsPerimeter: float, wallsSurface: float, doorsSurface: float, windowsSurface: float}
- **ZoneReduction**: {type: ZoneReductionType, percent: float, area: float, polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], holes: Holes2D}
- **ZoneReductionType**: "Rest"|"Wall"|"Column"|"Hatch"|"Gable"|"Unknown"
- **ZoneReductions**: {reductions: [ZoneReduction]}
- **ZoneRelations**: {elementsGroupedByType: [ElementsOfElementType], wallParts: [ZoneBoundaryPart], beamParts: [ZoneBoundaryPart], curtainWallSegmentParts: [ZoneBoundaryPart]}
- **ZoneRelationsOfElement**: {zoneRelations: ZoneRelations}
- **ZoneSettings**: {?name: string, ?numberStr: string, ?categoryAttributeId: AttributeId, ?stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, ?topOffset: float, ?relativeTopStory: float, ?floorThickness: float, ?referencePosition: Coordinate2D, ?contourLine: ZoneContourLine, ?coverFill: ZoneCoverFill}
- **Zoom**: {xMin: float, yMin: float, xMax: float, yMax: float}

## Application Commands

### GetAddOnVersion
# Retrieves the version of the Tapir Additional JSON Commands Add-On. (since 1.0.7)
  → version: string

### GetCommands
# Retrieves every command of the Tapir Add-On with its command group, the Tapir version it was introduced in and its description, so a script can check that a command exists before calling it. (since 2.0.0)
  → commands: [{name: string, group: string, version: string, description: string}]

### GetArchicadLocation
# Retrieves the location of the currently running Archicad executable. (since 1.0.7)
  → archicadLocation: string

### GetArchicadReleaseInfo
# Retrieves the main version, release version and build number of the running Archicad, with the caption of its window. (since 1.7.3)
  → mainVersion: int, releaseVersion: int, buildNumber: int, ?caption: string

### GetArchicadLicenseInfo
# Retrieves the license the running Archicad runs on: its type (Full, Education, Trial, Demo, Start or BIMcloud Team Client), the raw protection mode with its bits by name, and the highest Software Service Agreement (SSA) level of the license, so a script can warn before it uses a feature the license lacks. The SSA level is not available in Archicad 25. (since 2.0.0)
  → licenseType: "Full"|"Education"|"Trial"|"Demo"|"Start"|"BIMcloudTeamClient", protectionMode: int, licenseFlags: ["Site"|"NotForResale"|"School"|"PayPerUse"|"Network"|"Teamwork"|"Education"|"Start"|"Solo"|"LiveSubscription"|"OEM"|"SSA"|"EducationWithoutKey"|"Demo"|"Trial"|"BIMcloudTeamClient"], ?ssaLevel: "NoSSA"|"SSA"|"Forward"

### GetPrinterInfo
# Retrieves Archicad's current print settings: the print area, grid, fixed text size and scale (the settings PrintView takes). (since 1.7.3)
  → printArea: PrinterPrintArea, grid: bool, fixText: bool, scale: int

### GetPrinterAndPlotterInfo
# Retrieves the printer selected in Archicad, with its name and orientation, and the selected plotter, with its name and model. (since 1.8.0)
  → printer: PrinterInfo | ErrorItem, plotter: PlotterInfo | ErrorItem

### QuitArchicad
# Performs a quit operation on the currently running Archicad instance. (since 1.0.7)
  → ExecutionResult

### GetPointFromUser
# Asks the designer to click a point in the current window and returns it. Archicad waits for the click or for Escape, and every other JSON command queues behind this one until then; the call fails when the input is cancelled. (since 1.5.9)
  ?prompt: string, ?snapFilter: SnapFilter, ?constraint: InputConstraint
  → position: Coordinate3D

### ModelToScreen
# Converts model coordinates to pixel positions local to the current Archicad view window (not global desktop coordinates), using the current window's size, drawing scale and zoom. In a 3D window the coordinates are projected with the current camera; in other windows z is disregarded. Available from Archicad 29. (since 1.8.0)
  coordinates: [Coordinate3D]
  → screenPoints: [ScreenPoint | ErrorItem]

### ScreenToModel
# Converts pixel positions local to the current Archicad view window to 2D model coordinates of the current database, using the current window's size, drawing scale and zoom. It is a 2D mapping: it does not reconstruct a 3D point, and several model coordinates can map to the same pixel. (since 1.8.0)
  screenPoints: [ScreenPointInput]
  → coordinates: [Coordinate2D | ErrorItem]

### GetElementFromUser
# Asks the designer to click an element in the current window and returns its id, its type and the clicked point. A click on empty space or on an element of a type not asked for asks again. Archicad waits for the click or for Escape, and every other JSON command queues behind this one until then; cancelling returns cancelled. (since 1.7.3)
  ?prompt: string, ?elementTypes: [ElementType], ?snapFilter: SnapFilter, ?constraint: InputConstraint
  → ?elementId: ElementId, ?elementType: string, ?position: Coordinate3D, ?elementPosition: Coordinate3D, ?cancelled: bool

### GetCurrentTool
# Returns the tool active in the Toolbox: its element type, its variation (the subtype, e.g. Door, Skylight or a library part subtype of an add-on) and, for the tools of add-ons, its class id, in the form SetCurrentTool accepts. Nothing is returned when the active tool makes no element, e.g. the Arrow or the Marquee. (since 2.0.0)
  → ?elementType: ElementType, ?variation: string, ?classId: string

### SetCurrentTool
# Activates a tool in the Toolbox, given as GetCurrentTool or GetToolboxItems returns it; an empty input activates the Arrow. Archicad switches the tool once it processes its events, so GetCurrentTool may still return the previous tool right after this command. (since 2.0.0)
  ?elementType: ElementType, ?variation: string, ?classId: string
  → ExecutionResult

### GetToolboxItems
# Lists the tools of the Toolbox, the tools of add-ons included, in the form SetCurrentTool accepts, and the active tool. includeHidden also lists the tools without an icon, e.g. the Slab Accessory. (since 2.0.0)
  ?includeHidden: bool
  → toolboxItems: [{elementType: ElementType, ?variation: string, ?classId: string}], currentTool: {?elementType: ElementType, ?variation: string, ?classId: string}

### GetLineFromUser
# Waits for the user to input a line in the active Archicad window and returns start and end coordinates. (since 1.8.0)
  ?startPrompt: string, ?endPrompt: string, ?showRubberLineFeedback: bool, ?snapFilter: SnapFilter, ?constraint: InputConstraint
  → ?cancelled: bool, ?startPoint: Coordinate3D, ?endPoint: Coordinate3D

### GetArcFromUser
# Asks the designer to draw an arc in the current window - its center, its start point (which sets the radius) and its end point - with a rubber-band circle shown while drawing, and returns its center, radius, start and end angles, the angle it turns through, its direction and its start and end points. Archicad waits for the clicks or for Escape, and every other JSON command queues behind this one until then; cancelling returns cancelled. (since 2.0.0)
  ?centerPrompt: string, ?startPrompt: string, ?endPrompt: string, ?showRubberArcFeedback: bool, ?snapFilter: SnapFilter, ?constraint: InputConstraint
  → cancelled: bool, ?center: Coordinate3D, ?radius: float, ?startAngle: float, ?endAngle: float, ?arcAngle: float, ?clockwise: bool, ?startPoint: Coordinate3D, ?endPoint: Coordinate3D

### GetPolygonFromUser
# Waits for the user to input a polygon in the active Archicad window and returns its points and arcs. (since 1.8.0)
  ?startPrompt: string, ?prompt: string, ?method: PolygonInputMethod, ?snapFilter: SnapFilter, ?constraint: InputConstraint
  → cancelled: bool, ?points: [Coordinate2D], ?arcs: [PolyArc]

### GetMagicWandSettings
# Returns the settings of Archicad's Magic Wand Settings dialog: how curves are approximated with straight segments (a number of segments along arcs or circles, a largest deviation from the curve, or a segment length) and the trace method. Useful to know how the Magic Wand will trace a curve. Changes nothing in the project. (since 2.0.0)
  → curveApproximation: "SegmentsAlongArcs"|"SegmentsAlongCircles"|"DeviationFromCurves"|"SegmentLength"|"Unknown", segmentCount: int, maxDeviation: float, segmentLength: float, traceMethod: "Linear"|"BestMatch"|"Unknown"

### ConvertImages
# Converts base64 encoded images from one image format to another with Archicad's own image converters, for example a PNG preview image to JPEG. The formats are Bitmap, GIF, TIFF, JPEG and PNG, or the MIME type of another format Archicad can read or write. The output is aligned with the input array of images. Changes nothing in the project. (since 2.0.0)
  images[]: image: string, inputFormat: string, outputFormat: string
  → images: [{image: string} | ErrorItem]

### GetCurrentWindowType
# Returns the type of the current (active) window and, when it has one, the databaseId of the database it shows, which ChangeWindow takes to bring the window back after a script switched to another one. The saved view (View Map item) the window was opened from is not returned, as Archicad does not tell which one it was. (since 1.0.7)
  → currentWindowType: WindowType, ?databaseId: DatabaseId

### GetCurrentWindowDrawingScale
# Returns the drawing scale of the current (active) window, the scale shown in the bottom bar, as its denominator: 100.0 for 1:100, 20.0 for 1:20. Unlike GetViewSettings it needs no saved view. It reads the scale of the current database: the floor plan, a section, elevation, interior elevation, detail, worksheet or 3D document window, each of which has its own. Layouts always return 1.0. (since 1.7.3)
  → scale: float

### SetCurrentWindowDrawingScale
# Changes the drawing scale of the current (active) window, the scale shown in the bottom bar, to the given denominator: 100 for 1:100. It changes the scale of the current database: the floor plan, a section, elevation, interior elevation, detail, worksheet or 3D document window, each of which has its own. Layouts are always 1:1 and are rejected. The scale must be between 1 and 30000. The change is undoable. (since 1.7.3)
  scale: float, ?rebuild: bool
  → ExecutionResult

### ChangeWindow
# Changes the current (active) window to the given window. A databaseId on its own is enough; the window type is taken from the database. The databaseId of a worksheet or detail whose window was never opened opens its Project Map item instead (from Archicad 27). With windowType 'FloorPlan' and a storyIndex it also activates that story on the floor plan. windowType 'Report' on its own opens the Session Report window (from Archicad 26); its text cannot be read through the Archicad API. (since 1.3.1)
# storyIndex with windowType 'FloorPlan' switches the active story since 1.7.0 (#752; a silent no-op before). AC25/AC26 reject navigatorItemId.
  NavigatorItemIdOrDatabaseIdAndWindowType
  → ExecutionResult

### GetContainingDatabases
# Returns the database (window type, database id and name) that contains each of the given elements, from any database, not only the current one. Pass the windowType and databaseId to ChangeWindow to open it, for example to find an element placed on a layout. (since 1.7.3)
  elements: Elements
  → databases: [ContainingDatabase | ErrorItem]

### CloseWindows
# Closes the windows of the given databases (for example layouts, sections or details opened earlier with ChangeWindow), with one execution result per window; a window Archicad cannot close gets a failed result. Requires Archicad 27 or later. (since 1.8.0) [AC27+]
  windows: [WindowToClose]
  → executionResults: ExecutionResults

### RebuildCurrentDatabase
# Rebuilds the current database, the one the API works on (see ChangeWindow). Requires Archicad 27 or later. (since 1.8.0) [AC27+]
  → ExecutionResult

### DeleteGhostRecords
# Deletes the trace (ghost) record of each given parent database, which removes the trace reference shown in that database's window. A database without a trace reference gets a failed execution result. Not undoable. (since 1.8.0)
  databases: Databases
  → executionResults: ExecutionResults

### GetUserGSID
# Get the current registered User-GSID and OrganizationsID. Requires Archicad 27 or later. (since 1.5.6) [AC27+]
  → userId: string, ?organizationIds: [string]

### ShowAlert
# Display a dialog with up to three buttons. (since 1.5.6)
  alertType: "information"|"warning"|"error", title: string, message: string, ?subMessage: string, button1: string, ?button2: string, ?button3: string
  → clickedButton: int

### ShowNotificationBubble
# Shows a non-blocking notification bubble with a message in the current Archicad window, e.g. to report progress or a result without stopping the user as ShowAlert does. The bubble disappears by itself after the timeout. It is shown at a model coordinate or a pixel position of the current view, by default at the center of the current 2D view. Optionally it gets a large icon, is shown at most a given number of times, or is turned off, until the user runs 'Enable all informational messages'. Returns the bubble's settings read back from Archicad. Requires Archicad 29 or later. (since 2.0.0) [AC29+]
  message: string, ?icon: "none"|"information"|"warning"|"error", ?timeoutMilliseconds: int, ?coordinate: Coordinate3D, ?screenPoint: {h: int, v: int}, ?offset: {h: int, v: int}, ?largeIcon: "information"|"warning"|"error", ?redrawCountLimit: int, ?disabled: bool
  → ?text: string, icon: "none"|"information"|"warning"|"error"|"other", largeIcon: "none"|"information"|"warning"|"error"|"other", offset: {h: int, v: int}, timeoutMilliseconds: int, ?redrawCountLimit: int

### GetSpecialFolders
# Retrieves the filesystem paths of the special folders of the running Archicad (preferences, cache, data, temporary, application, defaults, templates, help, embedded project library, etc.). (since 1.5.6)
  folderTypes: [SpecialFolderType]
  → folderPaths: SpecialFolderPathsOrErrors

### GetEditModeState
# Tells whether Archicad is in a hierarchical editing mode (curtain wall, stair, beam or column editing), and which element is being edited. Read only: it never enters, leaves or cancels an editing mode. Commands that modify the project can fail while such a mode is active. The overall inEditMode flag requires Archicad 29 or later; the command requires Archicad 27 or later. (since 1.8.0) [AC29+]
  → ?inEditMode: bool, curtainWall: EditModeStateItem, stair: EditModeStateItem, beam: EditModeStateItem, column: EditModeStateItem

### GetArchicadVisibility
# Returns whether the Archicad application is shown or hidden. Supported on Windows only; on macOS it returns an error. (since 1.8.0)
  → isVisible: bool

### SetArchicadVisibility
# Hides or shows the Archicad application, e.g. to keep it out of the way while a batch runs. A script that hides Archicad must show it again, also when the script fails (e.g. in a finally block). Supported on Windows only; on macOS it returns an error. (since 1.8.0)
  isVisible: bool
  → ExecutionResult

### RunActionCenterChecks
# Runs the given checks of the Action Center (by default the hotlink check). A successful result means the check ran, not that nothing was found: Archicad does not report the outcome to the caller, it shows the Action Center tab when the check found an issue. (since 1.8.0)
  ?checks: [ActionCenterCheck]
  → executionResults: ExecutionResults

### RedrawCurrentDatabase
# Redraws the current database, even when its window is in the background. Only the visible region of its window is updated. (since 1.8.0)
  → ExecutionResult

### GetProductVersionInfo
# Retrieves the version information of the running Archicad: build number, language code, product family and version text, plus the product name, product type, main/update/hotfix versions, the available domains (Architecture, MEP) and the CEIP project identifier of the open project from Archicad 29. Requires Archicad 28 or later. (since 1.7.3)
  → ?productName: string, ?productType: string, productFamilyId: string, languageCode: string, buildNumber: int, versionString: string, ?mainVersion: string, ?updateVersion: string, ?hotfixVersion: string, ?versionNumbers: [int], ?availableDomains: [ProductDomain], ?ceipProjectId: string

### Get3DCutawayStatus
# Returns whether 3D Cutaway is on and whether the cutting planes are shown in the 3D window. In Archicad 25-27 the 3D window may need to be open. (since 1.7.3)
  → cutawayEnabled: bool, cuttingPlanesVisible: bool

### Set3DCutawayStatus
# Turns 3D Cutaway on or off and shows or hides the cutting planes in the 3D window. In Archicad 25-27 the 3D window may need to be open. (since 1.7.3)
  ?cutawayEnabled: bool, ?cuttingPlanesVisible: bool
  → ExecutionResult

### SetDialogAutoClose
# Turns the dialog auto close on or off. While it is on, Archicad closes the dialogs it would show with their default button instead of waiting for the user, so automation is not blocked by them. To have it on already while Archicad opens a project (before any command can be sent), set the TAPIR_DIALOG_AUTOCLOSE environment variable to true for the Archicad process before starting it. (since 1.7.3)
  enabled: bool
  → ExecutionResult

### GetDialogAutoClose
# Tells whether the dialog auto close is on, the same state SetDialogAutoClose writes, so a script can restore it afterwards. The state belongs to the running Archicad process: it is off when Archicad starts (unless the TAPIR_DIALOG_AUTOCLOSE environment variable is true), it stays as last set until Archicad quits, and it is shared by every add-on and script in that Archicad. (since 1.8.0)
  → enabled: bool

## Project Commands

### GetProjectInfo
# Retrieves information about the currently loaded project. (since 1.0.7)
  → isUntitled: bool, isTeamwork: bool, ?projectLocation: string, ?projectPath: string, ?projectName: string

### GetProjectInfoFields
# Retrieves the names and values of all project info fields. (since 1.0.7)
  → fields: ProjectInfoFields

### SetProjectInfoField
# Sets the value of a project info field. (since 1.0.7)
  projectInfoId: string, projectInfoValue: string

### CreateProjectInfoFields
# Creates one or more custom project info fields. From Archicad 30 the Project Info group of each field can be given; without it the field goes to the first group. (since 1.5.2)
  projectInfoFields: [ProjectInfoFieldData]
  → fields: CreatedProjectInfoFieldsOrErrors

### DeleteProjectInfoFields
# Deletes one or more custom project info fields, by their autotext keys or, from Archicad 30, by the ids of the fields of the Project Info groups. Hardcoded fields cannot be deleted. (since 1.5.4)
  ?projectInfoIds: [string], ?projectInfoFieldIds: [ProjectInfoFieldIdArrayItem]
  → executionResults: ExecutionResults

### RenameProjectInfoFields
# Renames custom fields of the Project Info groups. Fixed (built-in) fields cannot be renamed. Available from Archicad 30. (since 2.0.0)
  projectInfoFields[]: projectInfoFieldId: ProjectInfoFieldId, name: string
  → executionResults: ExecutionResults

### MoveProjectInfoFields
# Moves fields of the Project Info groups to a group, before another field of it or to its end. A subfield of a calculated field moves with its parent field. Available from Archicad 30. (since 2.0.0)
  projectInfoFields[]: projectInfoFieldId: ProjectInfoFieldId, projectInfoGroupId: ProjectInfoGroupId, ?beforeProjectInfoFieldId: ProjectInfoFieldId
  → executionResults: ExecutionResults

### GetProjectInfoGroups
# Retrieves the Project Info groups in their order, each with its fields: id, name, value and, when exactly one project info autotext has the name of the field, the autotext key that SetProjectInfoField takes. Available from Archicad 30. (since 1.8.0)
  → projectInfoGroups: ProjectInfoGroups

### CreateProjectInfoGroups
# Creates Project Info groups with the given names, at the end of the group list. Available from Archicad 30. (since 1.8.0)
  projectInfoGroups[]: name: string
  → projectInfoGroupIdsOrErrors: ProjectInfoGroupIdsOrErrors

### RenameProjectInfoGroups
# Renames Project Info groups. Available from Archicad 30. (since 1.8.0)
  projectInfoGroups: [ProjectInfoGroupRename]
  → executionResults: ExecutionResults

### DeleteProjectInfoGroups
# Deletes Project Info groups. A group that contains fixed (built-in) fields cannot be deleted. Available from Archicad 30. (since 1.8.0)
  projectInfoGroups: [ProjectInfoGroupIdArrayItem]
  → executionResults: ExecutionResults

### MoveProjectInfoGroups
# Moves Project Info groups before another group, or to the end of the group list when no other group is given. Available from Archicad 30. (since 1.8.0)
  projectInfoGroups: [ProjectInfoGroupMove]
  → executionResults: ExecutionResults

### GetStories
# Retrieves information about the story structure of the currently loaded project: index, floor id, name, level, height and, from Archicad 28, the IFC GlobalId of each story. (since 1.1.5)
  → firstStory: int, lastStory: int, actStory: int, skipNullFloor: bool, stories: StoriesParameters

### SetStories
# Sets the story sructure of the currently loaded project. (since 1.1.5)
  stories: StoriesSettings
  → ExecutionResult

### GetAutoTextKeys
# Retrieves the available autotext keys (name and embeddable key): the Project Info, layout, drawing, date and other autotexts Archicad lists, and the property based ones, optionally for a specific element. Embed a key in a Text or Label content by surrounding it with '<' and '>'. (since 1.5.9)
  ?elementId: ElementId
  → autoTextKeys: [{name: string, key: string}]

### GetAutoTextName
# Retrieves the display names of one or more autotext keys (as returned inside a '<...>' embedded key), with a direct guid lookup for property-based keys instead of enumerating every property definition. (since 1.5.9)
  keys: [AutoTextKeyValue]
  → autoTextNames: AutoTextNamesOrErrors

### GetAllAutoTextKeys
# Retrieves every autotext key Archicad knows (not only the property-based ones returned by GetAutoTextKeys) with its current value, resolved without an element context. (since 2.0.0)
  → autoTexts: [{key: string, value: string}]

### InterpretAutoTexts
# Resolves one or more autotexts (e.g. '<LAYOUTID>') to their values, optionally in the context of an element, so a key can be tested before it is written into a Text or Label. (since 2.0.0)
  autoTexts: [string], ?elementId: ElementId
  → values: [{value: string} | ErrorItem]

### GetNoteAutotexts
# Retrieves the autotexts available in the notes of an element type (e.g. a Dimension), each with the element types it is available for. The autotexts are identified by the numeric value of their API_NoteAutotextID. For a Dimension, the optional dimensionAppearance (Linear by default) chooses the dimension type. Needs Archicad 26 or later. (since 1.8.0) [AC26+]
  noteOwnerType: ElementType, ?dimensionAppearance: "Linear"|"Cumulative"|"Baseline"|"Elevation"
  → noteAutotexts: [NoteAutotextDetails]

### GetNoteAutoTextKeywords
# Retrieves the keywords of note autotexts (the autotexts of dimension, label and other element notes) by their numeric API_NoteAutotextID values. Available from Archicad 26. (since 1.7.3)
  autoTextIds: [int]
  → keywords: [NoteAutoTextKeyword | ErrorItem]

### GetHotlinks
# Gets the file system locations (path) of the hotlink modules and the instance elements placed from each node. The hotlinks can have tree hierarchy in the project. (since 1.0.7)
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

### BreakHotlinkNodes
# Breaks hotlink nodes, as the Hotlink Manager's Break Hotlink does: the elements of each node's placed instances stay in the project as ordinary elements, no longer tied to the source file. (since 1.8.0)
  hotlinkNodes[]: hotlinkNodeId: HotlinkNodeId
  → executionResults: ExecutionResults

### DeleteHotlinkNodes
# Deletes hotlink nodes together with their placed instances, as the Hotlink Manager's Delete does. (since 1.8.0)
  hotlinkNodes[]: hotlinkNodeId: HotlinkNodeId
  → executionResults: ExecutionResults

### GetHotlinkOwnersOfElements
# Tells for each element whether it comes from a hotlinked module, and returns the hotlink element that contains it and the hotlink instance it belongs to. Available from Archicad 27. (since 1.8.0)
  elements: Elements
  → hotlinkOwners: [HotlinkOwnersOfElementOrError]

### GetHotlinkProxyElementTable
# Maps the proxy elements of placed hotlink instances to the elements of the source file they were made from, so an element seen in a hotlinked module can be traced back to its source element. (since 1.7.3)
  hotlinkInstances: [ElementIdArrayItem]
  → proxyElementTables: [HotlinkProxyElementTable | ErrorItem]

### GetHotlinkSourceStatus
# Tells for each hotlink source file whether it is available, missing, not accessible, incompatible or offline. Available from Archicad 27. (since 1.8.0)
  hotlinks: [HotlinkSourceReference]
  → hotlinkSourceStatuses: [HotlinkSourceStatusResult | ErrorItem]

### OpenProject
# Opens the given project. The unsaved changes of the open project are discarded without asking: Archicad has no query for them, so call SaveProject first when they must be kept. (since 1.0.7)
  projectFilePath: string
  → ExecutionResult

### NewProject
# Starts a new, untitled project from the template set in Archicad's New Project settings, as File > New does; with newAndReset also the working environment is reset, as New and Reset All does. The unsaved changes of the open project are discarded, as with OpenProject. (since 1.7.3)
  ?newAndReset: bool
  → ExecutionResult

### CloseProject
# Closes the currently opened project. (since 1.3.1)
  → ExecutionResult

### SaveProject
# Saves the currently opened project, in place or to a given path. With overwrite false it refuses to replace an existing file at the path. (since 1.3.1)
  ?projectPath: string, ?overwrite: bool
  → ExecutionResult

### SaveAsModuleFile
# Saves the given elements, or the current selection, as a hotlink module (.mod) file. With overwrite false it refuses to replace an existing file. (since 1.5.9)
  moduleFilePath: string, ?overwrite: bool, ?elements: Elements
  → ExecutionResult

### SaveProjectAsArchive
# Saves the open project as an archive (.pla) file, with the library parts it uses inside. With overwrite false it refuses to replace an existing file. (since 1.6.0)
  archiveFilePath: string, ?overwrite: bool, ?includeLibraryParts: bool, ?includeProperties: bool, ?includeTextures: bool, ?includeBackgroundPicture: bool
  → ExecutionResult

### GetRenderingScenes
# Gets the names of the rendering scenes of the project (the Scene list of the PhotoRendering Settings palette), the most recently used first, and the name of the current scene. (since 1.8.0)
  → sceneNames: [string], ?currentSceneName: string

### SetCurrentRenderingScene
# Makes the given rendering scene the current one, as selecting it in the PhotoRendering Settings palette does. (since 1.8.0)
  sceneName: string
  → ExecutionResult

### PhotoRender
# Renders the 3D model with the current rendering scene, or with the given one, as Document > Creative Imaging > PhotoRender Projection does, and saves the image to a file (png, jpg, bmp, tiff or gif). The image size, resolution and quality come from the scene; a width, height or resolution given here is used for this render only, the scene is not changed. With overwrite false it refuses to replace an existing file. (since 1.8.0)
  imageFilePath: string, ?overwrite: bool, ?format: "png"|"jpg"|"bmp"|"tiff"|"gif", ?sceneName: string, ?width: int, ?height: int, ?resolution: int
  → ExecutionResult

### SaveCurrentWindowAsImage
# Saves what the current window shows as an image file (png, jpg, bmp, tiff or gif), as File > Save as does with a picture format. Master layout windows are not supported: save a layout that uses the master layout instead. With overwrite false it refuses to replace an existing file. (since 1.7.2)
  imageFilePath: string, ?overwrite: bool, ?format: "png"|"jpg"|"bmp"|"tiff"|"gif", ?colorDepth: "blackAndWhite"|"16Colors"|"256Colors"|"16Grays"|"256Grays"|"trueColor"|"trueColorWithAlpha", ?dithered: bool, ?entireDrawing: bool
  → imageFilePath: string, ?zoom: Zoom, ?rotation: float

### GetCurrentViewImage
# Returns what the 3D window, or the PhotoRendering window, shows as a base64 encoded png or jpg image with its size in pixels, without writing a file. Available from Archicad 30. (since 1.7.3)
  ?source: ViewImageSource, ?format: ViewImageFormat
  → image: string, width: int, height: int

### GetCalculationUnits
# Gets the project calculation units. (since 1.4.0)
  → length: {unit: LengthType, accuracy: AccuracyType, decimals: int, ?roundInch: int}, area: CalculationUnitAreaFormat, volume: CalculationUnitVolumeFormat, angle: AngleUnitFormat

### GetDimensionStandards
# Gets the dimension standards of the project (Options > Project Preferences > Dimensions) with their name and the unit, decimals and rounding of each dimension type, optionally only the one with the given name. Read-only. Available from Archicad 27. (since 1.8.0)
  ?name: string
  → dimensionStandards: [{index: int, name: string, settings: {linear: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, angle: {unit: AngleType, decimals: int, accuracy: int, hideZeroDecimals: bool}, radial: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, level: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, elevation: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, doorWindow: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, parapet: {unit: LengthType, decimals: int, showSmall5: int, roundInch: int, showZeroWhole: bool, showZeroInch: int, hideZeroDecimals: bool}, area: {unit: AreaType, decimals: int, hideZeroDecimals: bool}}}]

### GetExportTolerance
# Gets the export tolerance: the largest distance allowed between an arc and the straight segments that replace it when curves are segmented for export. Archicad only provides this value while an export is in progress, so outside an export the command returns an error saying so. (since 1.8.0)
  → arcTolerance: float

### GetLast3DDefaultLevels
# Gets the last 3D default levels of the given element types' defaults. (since 1.8.0)
  elementTypes: [ElementType]
  → levels: [float]

### SetLast3DDefaultLevels
# Sets the last 3D default levels of the given element types' defaults. (since 1.8.0)
  elementTypes: [ElementType], levels: [float]
  → ExecutionResult

### GetProjectPreferences
# Gets pages of the project preferences (Options > Project Preferences): the working units, the dimensions, the calculation units, the zones and the reference levels, and the Floor Plan Cut Plane Settings. Further pages may follow. (since 1.7.3)
  ?preferenceTypes: ["WorkingUnits"|"Dimensions"|"CalculationUnits"|"Zones"|"ReferenceLevels"|"FloorPlanCutPlane"]
  → ?workingUnits: {length: {unit: LengthType, decimals: int, roundInch: int}, area: {unit: AreaType, decimals: int}, volume: {unit: VolumeType, decimals: int}, angle: {unit: AngleType, decimals: int, accuracy: int}}, ?dimensions: {dimensionStandardIndex: int, linear: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, angle: {unit: AngleType, decimals: int, hideZeroDecimals: bool}, radial: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, level: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, elevation: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, doorWindow: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, parapet: {unit: LengthType, decimals: int, roundInch: int, accuracy: AccuracyType, showZeroWhole: bool, showZeroInch: bool, hideZeroDecimals: bool}, area: {unit: AreaType, decimals: int, hideZeroDecimals: bool}}, ?calculationUnits: {length: {unit: LengthType, accuracy: AccuracyType, decimals: int}, area: {unit: AreaType, accuracy: AccuracyType, decimals: int}, volume: {unit: VolumeType, accuracy: AccuracyType, decimals: int}, angle: {unit: AngleType, decimals: int, accuracy: int}}, ?zones: {lowCeilingAreaReduction: {activeHeightLimits: int, heightLimits: [{height: float, reductionPercent: float}], reductionPercentAboveHeightLimits: float}}, ?referenceLevels: {level1: {name: string, elevation: float}, level2: {name: string, elevation: float}}, ?floorPlanCutPlane: {cutPlaneHeight: float, topLevel: {relativeStory: int, offset: float}, bottomLevel: {relativeStory: int, offset: float}, absoluteDisplayLimit: float}

### SetProjectPreferences
# Changes pages of the project preferences (Options > Project Preferences): the working units, the dimensions, the calculation units, the zones and the reference levels, and the Floor Plan Cut Plane Settings. Only the given fields change, the rest of each page keeps its value. In Teamwork the PreferencesDialog lockable object set has to be reserved first (ReserveLockableObjectSet). Available from Archicad 27. (since 1.7.3)
  ?workingUnits: {?length: {?unit: LengthType, ?decimals: int, ?roundInch: int}, ?area: {?unit: AreaType, ?decimals: int}, ?volume: {?unit: VolumeType, ?decimals: int}, ?angle: {?unit: AngleType, ?decimals: int, ?accuracy: int}}, ?dimensions: {?dimensionStandardIndex: int, ?linear: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?angle: {?unit: AngleType, ?decimals: int, ?hideZeroDecimals: bool}, ?radial: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?level: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?elevation: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?doorWindow: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?parapet: {?unit: LengthType, ?decimals: int, ?roundInch: int, ?accuracy: AccuracyType, ?showZeroWhole: bool, ?showZeroInch: bool, ?hideZeroDecimals: bool}, ?area: {?unit: AreaType, ?decimals: int, ?hideZeroDecimals: bool}}, ?calculationUnits: {?length: {?unit: LengthType, ?accuracy: AccuracyType, ?decimals: int}, ?area: {?unit: AreaType, ?accuracy: AccuracyType, ?decimals: int}, ?volume: {?unit: VolumeType, ?accuracy: AccuracyType, ?decimals: int}, ?angle: {?unit: AngleType, ?decimals: int, ?accuracy: int}}, ?zones: {?lowCeilingAreaReduction: {?activeHeightLimits: int, ?heightLimits: [{?height: float, ?reductionPercent: float}], ?reductionPercentAboveHeightLimits: float}}, ?referenceLevels: {?level1: {?name: string, ?elevation: float}, ?level2: {?name: string, ?elevation: float}}, ?floorPlanCutPlane: {?cutPlaneHeight: float, ?topLevel: {?relativeStory: int, ?offset: float}, ?bottomLevel: {?relativeStory: int, ?offset: float}, ?absoluteDisplayLimit: float}
  → ?workingUnits: ExecutionResult, ?dimensions: ExecutionResult, ?calculationUnits: ExecutionResult, ?zones: ExecutionResult, ?referenceLevels: ExecutionResult, ?floorPlanCutPlane: ExecutionResult

### ConvertUnitValues
# Formats lengths, areas, volumes and angles (given in meters, square meters, cubic meters and radians) as Archicad shows them with the unit and rounding of the given Project Preference, returning the text, its extra accuracy decimals and the unit. The output is aligned with the input array of values. Available from Archicad 27. (since 1.8.0)
  values: [UnitValueConversionData]
  → convertedValues: [ConvertedUnitValue | ErrorItem]

### GetRenovationStatusNames
# Gets the names the running Archicad shows for the renovation statuses Existing, New and Demolished (localized). Available from Archicad 27. (since 1.8.0)
  → renovationStatuses: [RenovationStatusName | ErrorItem]

### GetGeoLocation
# Gets the project location details: the project location, and the survey point's position, geo-referencing parameters, visibility and lock state (the lock from Archicad 26). (since 1.1.6)
  → projectLocation: ProjectLocation, surveyPoint: SurveyPoint

### GetSurveyPointTransformation
# Gets the 3x4 matrix that transforms points from the Project Origin coordinate system into the Survey Point coordinate system, row by row, and its inverse when it is invertible. Read only. Available from Archicad 27. (since 1.7.3)
  → projectToSurvey: [float], ?surveyToProject: [float]

### SetGeoLocation
# Sets the project location details: the project location, and the survey point's position, geo-referencing parameters, visibility and lock state (the lock from Archicad 26). Omitted fields stay unchanged. (since 1.2.9)
  ?projectLocation: ProjectLocationUpdate, ?surveyPoint: SurveyPointUpdate
  → ExecutionResult

### SetPlaceSettings
# Changes the place settings of the project: location (longitude, latitude, altitude, north), date, time, summer time and time zone. Only the given fields change. Returns the settings read back, with the sun position Archicad calculated for them. Available from Archicad 27. (since 1.8.0)
  placeInfo: PlaceSettingsUpdate
  → placeInfo: {longitude: float, latitude: float, altitude: float, north: float, year: int, month: int, day: int, hour: int, minute: int, second: int, sumTime: bool, timeZoneInMinutes: int, timeZoneOffset: int, sunAngXY: float, sunAngZ: float}

### FindDimensionStandard
# Finds a dimension standard (Options > Project Preferences > Dimensions) by its name and returns its index, name and guid. Available from Archicad 27. (since 1.8.0)
  name: string
  → index: int, name: string, dimensionStandardId: GuidId

### GetProjectNotes
# Gets the Project Notes of the project (File > Info > Project Notes): client, project name, company, address, architect, draftsmen, project status, date of issue, keywords and notes. (since 1.7.3)
  → client: string, projectName: string, company: string, street: string, city: string, country: string, postalCode: string, architect: string, draftsmen: string, projectStatus: string, dateOfIssue: string, keywords: string, notes: string

### SetProjectNotes
# Changes the Project Notes of the project (File > Info > Project Notes). Only the given fields are changed; texts longer than the field Archicad stores are truncated. architect and draftsmen are full names that Archicad keeps as name parts: a new name is stored in the given name with the other parts cleared, and the parts of a name that is not given or not changed are kept. (since 1.7.3)
  ?client: string, ?projectName: string, ?company: string, ?street: string, ?city: string, ?country: string, ?postalCode: string, ?architect: string, ?draftsmen: string, ?projectStatus: string, ?dateOfIssue: string, ?keywords: string, ?notes: string
  → ExecutionResult

### GetSunSettings
# Gets the project's date and time (Options > Project Preferences > Location Settings), the sun position Archicad calculates for them at the project location, and the sun and ambient light settings. (since 1.8.0)
  → dateTime: SunDateTime, timeZoneInMinutes: int, timeZoneOffset: int, sunPosition: SunPosition, ?sunLight: {sunColor: ColorRGB, sunIntensity: int, ambientColor: ColorRGB, ambientIntensity: int}

### CalculateSunPosition
# Calculates the sun position (azimuth and altitude in degrees) for a date and time, at the project location unless another one is given, without changing the project. (since 1.8.0)
  ?dateTime: SunDateTimeUpdate, ?location: ProjectLocationUpdate
  → SunPosition

### GetCoordinateOrigins
# Gets the offset of the virtual coordinate system origin from the world origin, and the user origin of the current database. Use it to tell which origin the coordinates of different sources (elements, views, survey point) are relative to. (since 2.0.0)
  → ?virtualOriginOffset: Coordinate2D, ?userOrigin: Coordinate3D

### PrintView
# Prints from the current view. (since 1.3.1)
  ?grid: bool, ?fixText: bool, ?scale: int, ?printArea: "currentView"|"entireDrawing"|"marquee"
  → ExecutionResult

### RebuildView
# Rebuilds the current view. (since 1.5.0)
  ?regenerate: bool
  → ExecutionResult

### GetAutoIntersect
# Gets whether Auto-Intersection (Options > Auto-Intersection) is on. It changes what the wall and beam creation commands produce: with it on, the new elements are joined at their intersections. (since 1.8.0)
  → isOn: bool

### SetAutoIntersect
# Turns Auto-Intersection on or off. It is a setting of the running Archicad, not of the project; remember to restore the previous state afterwards. (since 1.8.0)
  isOn: bool
  → ExecutionResult

### ResolveNames
# Looks up words or phrases (for example from a user's question) among the names of the open project before they are passed to other commands: stories, layers, layer combinations, building materials, composites, profiles, surfaces, fills, lines, zone categories, element types (by API name and, from Archicad 27, by the name the Archicad interface shows), properties (by name, and by group and name together) and classifications (systems by name and version, items of every system by name and ID). For each name it returns 'found' with the items named exactly so, 'closeMatches' with the nearest names, best first (ranked by differences in case, accents, spacing and separators, shared words, one name containing the other and a few differing characters), or 'notFound' when nothing in the project is close, meaning the project has no such item and it must not be guessed. Each match carries what the other commands take: the story index, the attribute id and index, the elementType, the propertyId (with the property's group, value type and the classification items a custom property is available for), or the classificationSystemId and classificationItemId. Matching is lexical and deterministic. Read only. (since 2.0.0)
  ?maxCloseMatches: int
  names[]: name: string, ?kind: NameKind
  → results: [{name: string, status: "found"|"closeMatches"|"notFound", found: [NameMatch], closeMatches: [NameMatch]}]

## Custom Data Commands

### SetElementUserData
# Stores string values under keys on elements, for scripts to keep their own state per element (external database ids, sync timestamps, markers). The data is saved with the project as the user data of the Tapir add-on on the element and appears nowhere in the Archicad UI. The given keys are merged into what the element already holds: a key that exists gets the new value, other keys are left as they are, and the keys listed in keysToDelete are removed. Prefix the keys with the script's name so that scripts do not overwrite each other's data. One undo step per call; in a Teamwork project the element has to be reserved. (since 1.8.0)
  elementUserData[]: elementId: ElementId, ?userData: [{key: string, value: string}], ?keysToDelete: [string]
  → executionResults: ExecutionResults

### GetElementUserData
# Reads the values stored on elements by SetElementUserData: every key of each element, or only the given keys. (since 1.8.0)
  elements: Elements, ?keys: [string]
  → elementUserData: [{userData: [{key: string, value: string}]} | ErrorItem]

## Element Commands

### GetSelectedElements
# Gets the list of the currently selected elements. (since 1.0.7)
  → elements: Elements

### GetElementsByType
# Returns the identifier of every element of the given type on the plan. It works for any type. Use the optional filter parameter for filtering. Objects that belong to another element (zone stamps, the parts of stairs and railings) are left out unless the IncludeSubElemObjects filter is given. (since 1.0.7)
  elementType: ElementType, ?filters: [ElementFilter], ?databases: Databases
  → ElementsWithExecutionResultsOrError

### GetAllElements
# Returns the identifier of all elements on the plan. Use the optional filter parameter for filtering. Objects that belong to another element (zone stamps, the parts of stairs and railings) are left out unless the IncludeSubElemObjects filter is given. (since 1.0.7)
  ?filters: [ElementFilter], ?databases: Databases
  → ElementsWithExecutionResultsOrError

### CaptureElementState
# Captures the current state of the elements of the project and returns a stateId for it, so that GetElementChangesSince can later list what was created, modified and deleted since. The optional type selects how changes are detected (modification stamps by default, or the 3D model). The state is kept in a file in the temporary folder for the Archicad session only: it is lost when the project is closed or Archicad restarts, and ReleaseElementState frees it earlier. (since 1.8.0)
  ?type: "ModificationStamp"|"3DModel"
  → stateId: {guid: Guid}, type: "ModificationStamp"|"3DModel"

### GetElementChangesSince
# Returns the new, modified and deleted elements between a state captured by CaptureElementState and either another captured state (toStateId) or the current state of the project. Scripts that keep an external copy of the model use it to sync only what changed instead of re-reading every element. The changes come from Archicad's element difference generator, which tracks the model elements: 2D elements such as texts, labels and hatches can be missing from the lists, so read those directly. Fails for a stateId that is unknown - never captured, released, or lost because the project was closed or Archicad restarted. (since 1.8.0)
  stateId: {guid: Guid}, ?toStateId: {guid: Guid}
  → newElements: Elements, modifiedElements: Elements, deletedElements: Elements

### ReleaseElementState
# Frees a state captured by CaptureElementState. Every state is freed anyway when the project is closed or Archicad quits. (since 1.8.0)
  stateId: {guid: Guid}
  → ExecutionResult

### GetElementTypeNames
# Gets the localized names of the given element types, as the running Archicad shows them (for example 'Wand' for Wall in German Archicad). The output is aligned with the input array of element types. Available from Archicad 27. (since 1.7.3)
  elementTypes: [ElementType]
  → names: [ElementTypeName | ErrorItem]

### GetElementsInCreationOrder
# Returns the identifier of every element of the current database, or of the given databases, in the order the elements were created. (since 1.8.0)
  ?databases: Databases
  → ElementsWithExecutionResultsOrError

### ChangeSelectionOfElements
# Adds/removes a number of elements to/from the current selection. (since 1.0.7)
  ?addElementsToSelection: Elements, ?removeElementsFromSelection: Elements
  → executionResultsOfAddToSelection: ExecutionResults, executionResultsOfRemoveFromSelection: ExecutionResults

### DeselectAll
# Clears the selection in the current window. (since 2.0.0)
  → ExecutionResult

### GetMarquee
# Gets the marquee of the current window: its shape (rectangle, rotated rectangle or polygon), whether it is multi-story, and its outline as a polygon. Returns the type 'none' when there is no marquee. (since 2.0.0)
  → type: "none"|"rectangle"|"rotatedRectangle"|"polygon", ?multiStory: bool, ?box: BoundingBox2D, ?rotationAngle: float, ?polygon: [Coordinate2D]

### SetMarquee
# Draws a marquee in the current window from a polygon or a box (optionally rotated), single- or multi-story. Called without polygon and box it removes the marquee. (since 2.0.0)
  ?polygon: [Coordinate2D], ?box: BoundingBox2D, ?rotationAngle: float, ?multiStory: bool
  → ExecutionResult

### FilterElements
# Keeps the elements that match all the given criteria: Archicad's flag filters (filters), layer (layerIndices), home story (floorIndices), element type (elementTypes) and hotlink (fromHotlink, hotlinkIds). Within one criterion any of the listed values matches; an omitted criterion does not filter. (since 1.0.7)
  elements: Elements, ?filters: [ElementFilter], ?layerIndices: [int], ?floorIndices: [int], ?elementTypes: [ElementType], ?fromHotlink: bool, ?hotlinkIds: [ElementId]
  → elements: Elements

### GetElementsByCriteria
# Returns the elements, or with countOnly only their number, that match all the given criteria: element types, home stories, layers, Archicad's element filter flags and property criteria (a value compared in internal units, or a value status such as hasValue, isUserUndefined, isNotAvailable, isDefault or hasCustomValue). An unknown type, property or operator is an error, not ignored. Objects that belong to another element (zone stamps, the parts of stairs and railings) are left out unless the IncludeSubElemObjects filter is given. (since 2.0.0)
  ?types: [ElementType], ?floorIndices: [int], ?layerIndices: [int], ?filters: [ElementFilter], ?propertyCriteria: [{?propertyId: PropertyId, ?propertyName: string, ?propertyGroupName: string, ?operator: "equals"|"notEquals"|"contains"|"greaterThan"|"lessThan"|"greaterOrEqual"|"lessOrEqual"|"hasValue"|"hasAnyValue"|"isUndefined"|"isUserUndefined"|"isNotAvailable"|"isDefault"|"hasCustomValue", ?value: string}], ?countOnly: bool, ?limit: int
  → count: int, ?elements: Elements

### GetDetailsOfElements
# Gets the details of elements (geometry parameters etc). When elements is omitted, all elements matching the optional server-side filter (types, floorIndices, layerIndices) are queried; an empty elements list returns no details. Use the optional fields parameter to return only the fields you need (e.g. elementId, type, id, floorIndex) and skip the computation of the others (for example floorPlanPolygons). Use the optional additionalFields parameter to also get the info string, the compound info string, the library part unique ID and the creator tool unique ID. An element of another database (a layout, a section, a worksheet ...) returns only its header fields (type, floor index, layer, draw index) with fromOtherDatabase set to true. (since 1.0.7)
  ?elements: Elements, ?fields: [ElementDetailsField], ?filter: ElementTypeFloorLayerFilter, ?additionalFields: [ElementDetailsAdditionalField]
  → detailsOfElements: [DetailsOfElement | ElementHeaderFromOtherDatabase | ErrorItem]

### SetDetailsOfElements
# Sets the details of the given elements. Every element type: Element ID (id), story (floorIndex), layer (layerIndex) and display order (drawIndex). In typeSpecificDetails: Wall - start and end point, height, base offset, and the start and end thickness of a trapezoid wall; Zone - the ZoneSettings fields (the same as ModifyZones); Line - start and end point, pen, line type, room separator; Arc and Circle - origin, radius, angle, ratio, start and end angle (arcs only), reflected, pen, line type, room separator; Polyline - points and arcs, pen, line type, room separator; Spline - pen, line type, room separator; Hatch - outline, holes, contour pen, fill pen and background pen or colors, fill or building material, area display, room special and fill orientation; Hotspot - position, height, pen; Text - text, position, angle, height, justification; Label - the text of a text label; Drawing - position, angle, ratio, model offset, clip polygon (isCutWithFrame), name, ID and numbering, scale in Autotext, border, title library part, pen table (penTableUsageMode, penTableIndex), colorMode, isTransparentBackground, rasterizeDPI and the anchor (anchorPoint, useOwnOriginAsAnchor). Not written, because the Archicad API does not take them: the geometry of a Spline, the source of a Drawing (use ChangeDrawingLink), the Drawing Manager's update type and stored in project, and often a placed Drawing's drawingScale, which comes from its source view (the element's result then names the kept value). Other wall, slab, column, beam, stair and object settings are written by their Modify commands. An element Archicad does not let you edit (its layer is hidden or locked, it is locked, or it is not reserved by you in teamwork) gets a failed execution result naming the reason; a Drawing setting Archicad kept unchanged is named in a failed execution result too. (since 1.0.7)
  elementsWithDetails[]: elementId: ElementId, details: {?id: string, ?floorIndex: float, ?layerIndex: float, ?drawIndex: float, ?typeSpecificDetails: TypeSpecificSettings}
  → executionResults: ExecutionResults

### SetElementInfoStrings
# Sets the info string of the given elements: the Element ID shown in the Info Box, which GetDetailsOfElements returns as id. Returns one execution result per element. (since 1.8.0)
  elements: [ElementInfoString]
  → executionResults: ExecutionResults

### GetElementCategories
# Lists the element categories of the project (Structural Function, Position, Renovation Status, Renovation Filter and, in the German version, BRI) with their possible values. The names of the categories and values are localized: identify a category by its type and a value by its categoryValueId, never by name. (since 1.7.3)
  → categories: [ElementCategoryDetails]

### GetCategoryValuesOfElements
# Gets the category values (Structural Function, Position, Renovation Status ...) of the given elements, optionally only for the given category types. An element that has none of the requested categories (an annotation, for example) gets an error item. The names are localized: use the type and the categoryValueId in scripts. (since 1.7.3)
  elements: Elements, ?categories: [ElementCategoryType]
  → categoryValuesOfElements: [ElementCategoryValues | ErrorItem]

### GetCategoryValuesOfDefaults
# Gets the category values (Structural Function, Position, Renovation Status ...) of the tool defaults of the given element types, the values new elements of the type get, optionally only for the given category types. A category the default has no value in is listed without categoryValueId; an element type without any of the requested categories gets an error item. The names are localized: use the type and the categoryValueId in scripts. (since 1.8.0)
  elementTypes: [ElementType], ?categories: [ElementCategoryType]
  → categoryValuesOfDefaults: [{categoryValues: [{type: ElementCategoryType, categoryId: ElementCategoryId, ?categoryValueId: ElementCategoryValueId, ?name: string}]} | ErrorItem]

### SetCategoryValuesOfElements
# Sets the category values (Structural Function, Position, Renovation Status ...) of the given elements, one element and one category per item, in a single undoable step. The value must belong to the given category, as GetElementCategories lists them; an element without that category gets a failed execution result. The names are localized: use the type and the categoryValueId in scripts. With dryRun true nothing is changed and no undo step is created: the response has dryRun set to true, and each item that passes the checks made before writing gets wouldChange, with the element's value in the category now (oldValue) and the value a real run would set (newValue). (since 1.7.3)
  elementCategoryValues: [ElementCategoryValueData], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: ChangeExecutionResults

### Get3DBoundingBoxes
# Get the 3D bounding box of elements. The bounding box is calculated from the global origin in the 3D view. The output is the array of the bounding boxes respective to the input array of elements. An element without 3D geometry of its own gets an error item instead of a bounding box. Walls, Slabs, Roofs, Zones and Stairs are measured on their 3D model, so the box of a Wall includes its connections to other walls. The current window does not need to show the element: it works with a layout or a section open as well. (since 1.1.2)
  elements: Elements
  → boundingBoxes3D: BoundingBoxes3D

### Get2DBoundingBoxes
# Get the 2D bounding box of elements as Archicad draws them, in the coordinates of the database the element is in: the floor plan, a section, a worksheet, a layout or a master layout. Works for 2D elements (Line, PolyLine, Arc, Hatch, Text, Label, Dimension, Drawing ...) as well as for model elements; a Text's box covers its drawn lines, a Drawing's box its frame with the title. The current window does not need to show the element. The output is the array of the bounding boxes respective to the input array of elements. (since 2.0.0)
  elements: Elements
  → boundingBoxes2D: BoundingBoxes2D

### GetLibPartTransformations
# Gets the placement transformation of library part instances (Window, Door, Object, Lamp, Zone) as Archicad computes it: the location, the rotation angle and the x/y scaling. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → transformations: [ElementLibraryPartTransformation | ErrorItem]

### GetSnapPointsOfElements
# Gets the snap points (hotspots) of the given elements, of any element type: the points of an element that the cursor snaps to and dimensions attach to (for example the endpoints of a Wall's reference line or the vertices of a Slab), in world coordinates, each with the neig kind and subindex identifying which point of the element it is. For the 2D hotspots of library part instances see GetHotspotsOfElements. The output is aligned with the input array of elements. (since 2.0.0)
  elements: Elements
  → snapPointsOfElements: [{snapPoints: [{coordinate: Coordinate3D, neigId: int, inIndex: int}]} | ErrorItem]

### ConvertRevealOffsets
# Converts the reveal depth offset of windows and doors placed in walls between the two references Archicad uses: measured from the core skin of a composite wall, or from the wall side. Give exactly one of coreOffset or sideOffset per opening; both values are returned. For walls with a basic structure the two values are equal. The output is aligned with the input array of openings. Available from Archicad 27. (since 1.7.3)
  openings: [OpeningRevealOffsetData]
  → revealOffsets: [OpeningRevealOffsets | ErrorItem]

### Get3DGeometryOfElements
# Gets the 3D geometry of elements as the solid bodies of their 3D model: a vertex list in world coordinates and the planar faces (with their holes) referencing it, each face with its surface attribute when that is a project attribute. The bodies of the subelements of a Stair, Railing or Curtain Wall, and of the segments of a Column or Beam, are included. The output is aligned with the input array of elements. The 3D model of the elements is generated as needed, so many elements can take a while. (since 1.7.2)
  elements: Elements
  → geometries3D: [ElementGeometry3D | ErrorItem]

### GetElementConnections
# Gets the connections among the given elements: each pair of touching elements once, with the polygons of the surface where they touch, in world coordinates. The 3D model of the elements is generated with separate components in a temporary sight, so the 3D window is not changed. Also returns, aligned with the input array of elements, whether each element was found. Available from Archicad 28. (since 1.8.0)
  elements: Elements
  → connections: [{elementId1: ElementId, elementId2: ElementId, polygons: [{coordinates: [Coordinate3D]}]}], executionResults: ExecutionResults

### GetBodyMaterialsOfElements
# Gets the building material of each body of the 3D model of the given elements. The 3D model is generated with separate components in a temporary sight, so a composite structure has one body per skin and the 3D window is not changed. The output is aligned with the input array of elements. Available from Archicad 28. (since 1.8.0)
  elements: Elements
  → bodyMaterials: [{bodies: [{bodyIndex: int, ?buildingMaterialId: AttributeId, ?buildingMaterialName: string}]} | ErrorItem]

### GetCutPolygonsOfElements
# Cuts each body of the 3D model of the given elements with a plane and returns, for each body, its building material, the area of the cut surface and its polygons (outline and holes) in 2D coordinates of the plane. From Archicad 28 the 3D model is generated with separate components in a temporary sight, so a composite structure has one body per skin and the 3D window is not changed. Before Archicad 28 the bodies are those of the element's 3D model (a composite structure is one body) and their building materials are left out. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements, cutPlane: {basePoint: Coordinate3D, axisX: Coordinate3D, axisY: Coordinate3D, axisZ: Coordinate3D}
  → cutPolygons: [{bodies: [{bodyIndex: int, ?buildingMaterialId: AttributeId, ?buildingMaterialName: string, area: float, polygons: [{polygonOutline: [Coordinate2D], holes: Holes2D}]}]} | ErrorItem]

### GetElementAtCoordinate
# Finds the element of the given polygonal type (for example Slab, Roof, Mesh, Zone or Hatch) at a coordinate of the floor plan of the current database, the way a click there would. Use the optional filters parameter (the values of FilterElements) to consider only, for example, the elements visible by layer, and the optional z parameter to give the elevation of the point. Returns found: false when there is no such element. Useful together with GetPointFromUser. (since 1.7.3)
  elementType: ElementType, coordinate: Coordinate2D, ?z: float, ?filters: [ElementFilter]
  → found: bool, ?elementId: ElementId

### GetSkylightHolePolygons
# Gets the polygon of the hole each given Skylight cuts into its host Roof or Shell: the outline and any holes of it as 2D coordinates. The output is aligned with the input array of elements; an element that is not a Skylight gets an error item. (since 1.8.0)
  elements: Elements
  → skylightHolePolygons: [SkylightHolePolygon | ErrorItem]

### GetVisibleSkinStatus
# Checks whether elements have a visible skin in a given Partial Structure Display mode (EntireStructure, CoreOnly, WithoutFinishes or StructureOnly), e.g. a finish-only slab has none in CoreOnly. The current window is not changed. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements, structureDisplay: "EntireStructure"|"CoreOnly"|"WithoutFinishes"|"StructureOnly"
  → visibleSkinStatuses: [VisibleSkinStatus | ErrorItem]

### GetRoofPlanes
# Gets the single planes of roofs, without changing the roofs. A multi-plane roof is decomposed by Archicad into its planes, each returned with its part identifier and its details as a single-plane roof (slope, pivot line, level, outline with arcs and holes); a single-plane roof is returned as its only plane. The output is aligned with the input array of elements. (since 2.0.0)
  elements: Elements
  → roofPlanesOfElements: [{planes: [{?partId: {main: float, sub: float}, details: RoofDetails}]} | ErrorItem]

### GetCurtainWallAbsoluteBottoms
# Gets the absolute bottom level of curtain walls or their subelements (segments, frames, panels, junctions, accessories). The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → absoluteBottoms: [CurtainWallAbsoluteBottom | ErrorItem]

### GetQuantitiesOfElements
# Gets the quantities of the given elements calculated by Archicad (volumes, surfaces, lengths etc.), together with the volume and projected area per building material (one item per skin of composite and complex profile elements, one item for basic elements). Supported types: Wall, Column, Beam, Slab, Roof, Shell, Morph, Zone, ColumnSegment, BeamSegment. Use the optional minOpeningSize parameter to control the conditional values, and calculateInOneCall to calculate all the elements in one Archicad call. (since 1.7.2)
  elements: Elements, ?minOpeningSize: float, ?calculateInOneCall: bool
  → quantitiesOfElements: [ElementQuantityDetails | ErrorItem]

### TriangulatePolygonsOfElements
# Triangulates the plan polygon of the given elements, holes excluded, as Archicad does it: the outline of a Slab, Zone, Hatch or Mesh and the polygon of a Roof. Each triangle is given by the 2D coordinates of its three vertices. With convex: true, the faces of the 3D model of the elements (of any type) are decomposed into convex polygons instead, given by the 3D coordinates of their vertices. The output is aligned with the input array of elements; an element of another type gets an error item. (since 1.7.3)
  elements: Elements, ?convex: bool
  → triangulations: [ElementTriangulation | ElementConvexPolygons | ErrorItem]

### GetTextureCoordinates
# Gets the texture coordinates (u, v) of the faces of the 3D model of the given elements: per solid body, per face, at the first vertex of the face. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → textureCoordinates: [ElementTextureCoordinates | ErrorItem]

### GetSurfaceTypesOfElements
# Gets the surface type of every polygon of the 3D model of the given elements, as ACAPI_Polygon_PolygonId2SurfaceType returns it: for each element its polygons with their body index, polygon index, polygon id and the numeric API_SurfaceTypeID value. The model is generated with separate components in a temporary sight, so the 3D window is not changed. The output is aligned with the input array of elements. Available from Archicad 28. (since 1.8.0)
  elements: Elements
  → surfaceTypes: [{polygons: [{bodyIndex: int, polygonIndex: int, polygonId: int, surfaceType: int}]} | ErrorItem]

### Get3DModelCounts
# Gets the number of components of each type (bodies, polygons, polygon edges, edges, vertices, normal vectors, materials and lights) in the 3D model Archicad currently holds. Bodies, materials and lights are counted with ACAPI_ModelAccess_GetNum; the polygons, polygon edges, edges, vertices and normal vectors, which that function refuses to count, are summed over the bodies. A type that cannot be counted gets an error item. Available from Archicad 27. (since 1.8.0)
  → counts: [Model3DCount | ErrorItem]

### DeleteUserDataOfElements
# Deletes the user data this add-on stored on the given elements. Archicad keeps the user data of an element per add-on, so the data of other add-ons is left as it is. All deletions are one undo step. The output has one execution result per element, aligned with the input array of elements. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each element that exists gets wouldDelete. (since 2.0.0)
  elements: Elements, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### GetSurfaceQuantitiesOfElements
# Gets the exposed surface areas of the given elements calculated by Archicad: for each element one item per surface attribute and building material pair with the area that is not covered by the covering elements (for example the wall area behind a slab is taken off the wall's surface). The covering elements are the optional coverElements; by default every construction element of the project. The output is aligned with the input array of elements. (since 1.7.3)
  elements: Elements, ?coverElements: Elements
  → surfaceQuantitiesOfElements: [ElementSurfaceQuantities | ErrorItem]

### GetSubelementsOfHierarchicalElements
# Gets the subelements of the given hierarchical elements. From Archicad 28 the subelements of external hierarchical elements (for example MEP elements or elements of other add-ons) are returned as externalSubelements. (since 1.0.7)
  elements: Elements
  → subelements: [{?cWallSegments: Elements, ?cWallFrames: Elements, ?cWallPanels: Elements, ?cWallJunctions: Elements, ?cWallAccessories: Elements, ?stairRisers: Elements, ?stairTreads: Elements, ?stairStructures: Elements, ?railingNodes: Elements, ?railingSegments: Elements, ?railingPosts: Elements, ?railingRailEnds: Elements, ?railingRailConnections: Elements, ?railingHandrailEnds: Elements, ?railingHandrailConnections: Elements, ?railingToprailEnds: Elements, ?railingToprailConnections: Elements, ?railingRails: Elements, ?railingToprails: Elements, ?railingHandrails: Elements, ?railingPatterns: Elements, ?railingInnerPosts: Elements, ?railingPanels: Elements, ?railingBalusterSets: Elements, ?railingBalusters: Elements, ?beamSegments: Elements, ?columnSegments: Elements, ?externalSubelements: Elements}]

### GetHierarchicalElementOwners
# Gets the owner of each given element in its hierarchical element: the root (e.g. the Curtain Wall, Stair or Railing of a frame, tread or post) or the immediate parent. Also returns whether the given element is a main element, a subelement or not part of a hierarchical element. (since 1.7.3)
  elements: Elements, ?ownerMode: HierarchicalOwnerMode
  → owners: [HierarchicalElementOwner | ErrorItem]

### EditHierarchicalElement
# Opens the given hierarchical element (Curtain Wall, Stair, Railing, Beam or Column) in its hierarchical 3D editing mode, as the Edit button of the element does. Fails when Archicad is already in an editing mode. Limitation: while the editing mode is open, Archicad refuses every JSON command, this add-on's included, with error 4001 (ongoing user input), FinishHierarchicalEditing included, so the mode can only be left in Archicad, with the button of its edit mode palette (reported for Archicad 29). Requires Archicad 27 or later. (since 1.8.0)
  elementId: ElementId
  → ExecutionResult

### FinishHierarchicalEditing
# Finishes the current hierarchical editing mode (Curtain Wall, Stair, Railing, Beam or Column): accept true keeps the changes (OK), accept false discards them (Cancel). The accept parameter is required, so changes are never discarded silently. Fails when Archicad is not in such an editing mode. Limitation: while an editing mode is open, Archicad refuses JSON commands with error 4001 (ongoing user input) before they run, so this command cannot leave a mode opened by EditHierarchicalElement or in Archicad (reported for Archicad 29); leave it in Archicad instead. Requires Archicad 27 or later. (since 1.8.0)
  accept: bool
  → ExecutionResult

### GetConnectedElements
# Gets the elements hosted by (connected to) the given owner elements, filtered to the given element type: for example the Windows or Doors of a Wall, the frames, panels, junctions and accessories of a Curtain Wall, the risers, treads and structures of a Stair, or the posts, rails and panels of a Railing. (since 1.1.4)
  elements: Elements, connectedElementType: ElementType
  → ConnectedElementsOrError

### GetElementsInDrawOrder
# Returns the identifier of every element of the current database, or of the given databases, in Archicad's drawing order (the order set by Bring to Front and Send to Back), as ACAPI_DrawOrder_DrawOrderGetNext walks it. Use the optional elementType and filters parameters for filtering. Objects that belong to another element (zone stamps, the parts of stairs and railings) are left out unless the IncludeSubElemObjects filter is given. (since 1.7.3)
  ?elementType: ElementType, ?filters: [ElementFilter], ?databases: Databases
  → ElementsWithExecutionResultsOrError

### GetDrawingPrimitivesOfElements
# Returns the 2D drawing primitives (points, lines, arcs, texts, polylines, triangles, polygons, pictures) Archicad draws each given floor plan element from, in drawing order, as ACAPI_DrawingPrimitive_ShapePrimsExt decomposes it on every story and unclipped. Control items (type Ctrl_*) mark the beginning and the end of sub-parts such as hatches and texts. Texts are returned without their content and polylines without their vertices. A Ctrl_ElementRef item names the element it refers to: the drawing of a Wall ends with one for each Window and Door in it, while Windows and Doors give no primitives of their own. The floor plan must be the current database. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → drawingPrimitivesOfElements: [ElementDrawingPrimitives | ErrorItem]

### GetStoryControlPrimitives
# Returns the 2D drawing primitives of the story levels (story lines and their markers) drawn in the given section, elevation or interior elevation database, as ACAPI_DrawingPrimitive_DrawStoryControl draws them, in the same format as GetDrawingPrimitivesOfElements. The databaseId can be obtained with GetDatabaseIdFromNavigatorItemId. (since 1.8.0)
  databaseId: DatabaseId
  → primitives: [DrawingPrimitive]

### GetShapePrimitivesOfElements
# Returns the 2D drawing primitives of each given floor plan element in the same format as GetDrawingPrimitivesOfElements, but drawn as ACAPI_DrawingPrimitive_ShapePrims draws it by default (on the current story, clipped as Archicad clips it) instead of on every story and unclipped. With includeMarkers the objects attached to the elements (window and door markers, drawing titles, ...) are drawn with them or left out; Archicad's setting is changed back afterwards. An element on another story gets an error item. The floor plan must be the current database. The output is aligned with the input array of elements. (since 2.0.0)
  elements: Elements, ?includeMarkers: bool
  → shapePrimitivesOfElements: [ElementDrawingPrimitives | ErrorItem]

### GetSectionElements
# Gets the elements drawn in the given section, elevation or interior elevation databases, each with the owner element it was generated from. This is the only command that returns raw section element identifiers - every other listing command converts them to their owner - so it is the way to obtain the sectionElementId that CreateAssociativeDimensionsOnSection requires. (since 1.5.8)
  ?databases: Databases
  → sectionElements: [{sectionElementId: ElementId, ownerElementId: ElementId, ?ownerElementType: ElementType}], ?executionResultForDatabases: ExecutionResults

### GetRelationsOfElements
# Gets the type-specific relations of the given elements: endpoint and reference line connections of walls, beams and beam segments, boundary elements and boundary sections of zones, the zones on the two sides of windows, doors, skylights and curtain wall panels, and the zones connected to roofs and shells. Available from Archicad 26. (since 1.5.7)
  elements: Elements, ?otherElementType: ElementType
  → relations: [ElementRelationsOrError]

### LinkElements
# Creates persistent links between pairs of elements, each from one element to another, with an optional integer flags value per link. Scripts can record their own relations between elements this way (for example which label documents which column) instead of storing GUIDs in properties. The links are stored in the project and have no effect on geometry; they are independent from groups, hotlinks and solid element operations. A link is directional: it is returned by GetLinksOfElements for the element it starts from only, and removed by UnlinkElements. Undoable. (since 1.7.3)
  links: [ElementLinkData]
  → executionResults: ExecutionResults

### UnlinkElements
# Removes the links created by LinkElements between the given pairs of elements. The direction matters: the link starting from fromElementId and pointing to toElementId is removed. Undoable. (since 1.7.3)
  links: [ElementLinkReference]
  → executionResults: ExecutionResults

### GetLinksOfElements
# Gets the links created by LinkElements that start from the given elements: the linked element and the flags of each link. Links pointing to an element are not returned; query the elements they start from. Returns an error item for an element that does not exist. (since 1.7.3)
  elements: Elements
  → linksOfElements: [ElementLinksOrError]

### GetZoneBoundaries
# Gets the boundaries of the given Zones (connected elements, neighbour zones, etc.). Accepts either a single zoneElementId or a list of zones. Prefer the list: the expensive boundary recalculation runs once per call, so querying many Zones in one call is much faster than calling the command once per Zone. (since 1.2.3)
  ?zoneElementId: ElementId, ?zones: Elements
  → ZoneBoundariesOrError | ZoneBoundariesOfZonesWrapper

### GetZoneReductions
# Gets the area reductions of the given Zones, as the Zone Stamp's area calculation uses them: the polygons of the Zone covered by Walls, Columns, reducing Fills, sloping Roofs and low ceilings, each with its type, the percentage it is reduced by, its area and its outline with holes. Area calculations by local standards need these parts, which GetQuantitiesOfElements only gives as totals. The output is aligned with the input array of elements. (since 1.7.3)
  elements: Elements
  → reductionsOfZones: [ZoneReductions | ErrorItem]

### GetPropertyObjectsOfElements
# Gets the property objects of the given elements: the library parts of the old listing system (used by projects migrated from older Archicad versions) linked to each element by criteria or individually, with the library part's index (the same as the index returned by GetAvailableLibraryParts), name and guid. The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → propertyObjectsOfElements: [ElementPropertyObjects | ErrorItem]

### GetDescriptorsOfElements
# Gets the descriptors of the given elements: the listing descriptors in the property objects of each element, with the library part that declares them (index, name and guid), their listing database set and index, and their status (Normal, Deleted or Local). The output is aligned with the input array of elements. (since 1.8.0)
  elements: Elements
  → descriptorsOfElements: [ElementDescriptors | ErrorItem]

### GetLinkedPropertyObjectsOfElements
# Gets how property objects (the library parts of the old listing system) are linked to the given elements, or to the element defaults of the given element types: whether the property objects matching their criteria are linked, which of them match, and which one is assigned individually, each with the library part's index (the same as the index returned by GetAvailableLibraryParts), name and guid. The output is aligned with the input array of elements. (since 1.8.0)
  elements: [{elementId: ElementId} | {elementType: ElementType}]
  → linkedPropertyObjectsOfElements: [ElementLinkedPropertyObjects | ErrorItem]

### SetLinkedPropertyObjectsOfElements
# Sets how property objects (the library parts of the old listing system) are linked to the given elements, or to the element defaults of the given element types: whether the property objects matching their criteria are linked, and which one is assigned individually (0 removes the individual assignment). A link that is not given stays unchanged. All changes are made in one undoable step. (since 1.8.0)
  elementsWithLinkedPropertyObjects: [{elementId: ElementId, ?linkByCriteria: bool, ?individualLibraryPartIndex: int} | {elementType: ElementType, ?linkByCriteria: bool, ?individualLibraryPartIndex: int}]
  → executionResults: ExecutionResults

### UpdateZones
# Updates Zones (recalculates their geometry, updates their Zone Stamps and the connected elements): the selected Zones, every Zone when nothing is selected, or the Zones given in zones. Archicad runs the update right after the command has returned, on the Zones selected at that moment, so the new geometry can only be read with a later command. (since 1.5.4)
  ?keepStampPosition: bool, ?undoTopTrim: bool, ?undoBottomTrim: bool, ?zones: Elements
  → ExecutionResult

### SetZoneLabelingSettings
# Turns the automatic labeling of Zones on or off and selects the Label Favorite it places. Only the given settings are changed. Available from Archicad 28. (since 1.7.3)
  ?automaticLabeling: bool, ?favoriteName: string
  → ExecutionResult

### GetZoneLabelingSettings
# Returns whether the automatic labeling of Zones is on and the name of the Label Favorite it places. Available from Archicad 28. (since 1.8.0)
  → isAutomaticLabelingOn: bool, ?selectedFavoriteName: string

### GetCollisions
# Detect collisions between the given two groups of elements. (since 1.2.2)
  elementsGroup1: Elements, elementsGroup2: Elements, ?settings: {volumeTolerance: float, performSurfaceCheck: bool, surfaceTolerance: float}
  → collisions: [{elementId1: ElementId, elementId2: ElementId, hasBodyCollision: bool, hasClearenceCollision: bool}]

### HighlightElements
# Highlights the elements given in the elements array. In case of empty elements array removes all previously set highlights. On Archicad 25 nonHighlightedColor is ignored. (since 1.0.7)
  elements: Elements, highlightedColors: [[int]], ?wireframe3D: bool, ?nonHighlightedColor: [int]
  → ExecutionResult

### MoveElements
# Moves elements with a given vector. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 1.0.7)
  elementsWithMoveVectors[]: elementId: ElementId, moveVector: {x: float, y: float, z: float}, ?copy: bool
  → executionResults: ExecutionResults

### AlignElements
# Aligns elements on the floor plan or in the current 2D view to one edge of their plan bounding boxes (left, right, top or bottom) or to their middle (centerX, centerY), either of the whole set or of a reference element, by moving them in one undo step. The bounding boxes are those Get2DBoundingBoxes returns. Supported types: Wall, Column, Beam, Slab, Roof, Shell, Morph, Mesh, Zone, Object, Lamp, Stair, Railing, CurtainWall, Line, PolyLine, Arc, Circle, Spline, Hatch, Text and Hotspot. An element of another type (doors, windows and openings, which only slide along their host, subelements, dimensions, labels, ...) or one that cannot be edited gets a failed execution result naming the reason, and the other elements are still aligned. (since 2.0.0)
  elements: Elements, alignTo: "left"|"right"|"top"|"bottom"|"centerX"|"centerY", ?reference: ElementId
  → executionResults: ExecutionResults

### DistributeElements
# Distributes 3 or more elements on the floor plan or in the current 2D view evenly along X (horizontal) or Y (vertical), with equal distances between the middles of their plan bounding boxes (centers) or equal space between the boxes (gaps), by moving them in one undo step. The elements are taken in the order of their middles along the direction, and the two outermost stay where they are. The bounding boxes are those Get2DBoundingBoxes returns. Supported types: Wall, Column, Beam, Slab, Roof, Shell, Morph, Mesh, Zone, Object, Lamp, Stair, Railing, CurtainWall, Line, PolyLine, Arc, Circle, Spline, Hatch, Text and Hotspot. An element of another type (doors, windows and openings, which only slide along their host, subelements, dimensions, labels, ...) or one that cannot be edited gets a failed execution result naming the reason, and the other elements are still distributed. (since 2.0.0)
  elements: Elements, direction: "horizontal"|"vertical", mode: "centers"|"gaps"
  → executionResults: ExecutionResults

### SplitElements
# Splits each given element along a line (the infinite line through its begin and end point, like Archicad's Split command). The original element keeps one part, copies of it (Drag a Copy, so they keep the layer, classifications, properties and every other setting) get the others; all are returned, the original first. Supports straight walls without doors, windows or openings, straight unslanted single segment beams without holes or openings, and lines (their arrows stay at the original ends), which are split in two, the original keeping the part from its begin point; and slabs, meshes without level lines or points, fills and single contour polylines, whose polygon (holes and arcs included) or points are cut along the line into one part per piece, the original keeping the largest piece (a polyline: the piece with its begin point). Slab edges keep their trim and side surface, the edges along the line are vertical; the corners a mesh gets on the line take their height from the edge they lie on. An element the line does not cross is reported as notCut, an unsupported one as an error naming its type. One undo step. (since 2.0.0)
  elements: Elements, line: {begin: Coordinate2D, end: Coordinate2D}
  → results: [{elements: Elements} | {notCut: bool} | ErrorItem]

### CopyElementsToDatabase
# Copies 2D elements (lines, polylines, arcs, circles, splines, hotspots, texts, hatches, independent labels) from one database into another, e.g. from a worksheet into another worksheet, a detail or a layout, optionally moved by an offset. Returns the new elements in the order of the given ones. (since 2.0.0)
  elements: Elements, ?sourceDatabaseId: DatabaseId, targetDatabaseId: DatabaseId, ?offset: Coordinate2D
  → elements: ElementIdsOrErrors

### ElevateElements
# Moves elements vertically by a given offset in meters, like Edit > Move > Elevate. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 2.0.0)
  elementsWithElevations[]: elementId: ElementId, elevation: float, ?copy: bool
  → executionResults: ExecutionResults

### RotateElements
# Rotates elements around a reference point. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 1.5.3)
  elementsWithRotations[]: elementId: ElementId, rotation: {beginPoint: Coordinate2D, endPoint: Coordinate2D, origin: Coordinate2D}, ?copy: bool
  → executionResults: ExecutionResults

### MirrorElements
# Mirrors elements across an axis given by two points on the floor plan, optionally as a copy. An element that cannot be edited (its layer is hidden or locked, it is locked, or it is not available in teamwork) gets a failed execution result naming the reason instead of being skipped silently. (since 1.7.3)
  elementsWithMirrorAxes: [ElementMirrorData]
  → executionResults: ExecutionResults

### CopyElements
# Copies elements by an offset, like dragging a copy in Archicad, keeping all their settings. With count, copy n is moved by n times the offset, which makes a linear array. Returns the new elements of each given element, in the order of the given ones; an element Archicad cannot copy (a part of a curtain wall, stair or railing, a locked element or one on a hidden or locked layer, ...) gets an error naming the reason, and the other elements are still copied. All copies are one undo step. (since 2.0.0)
  elements: Elements, offset: Coordinate3D, ?count: int
  → copies: [{elements: Elements, ?error: Error}]

### RotateCopyElements
# Copies elements rotated around a center on the floor plan by an angle in radians, like rotating a copy in Archicad, keeping all their settings. With count, copy n is rotated by n times the angle, which makes a circular array. Returns the new elements of each given element, in the order of the given ones; an element Archicad cannot copy gets an error naming the reason, and the other elements are still copied. All copies are one undo step. (since 2.0.0)
  elements: Elements, center: Coordinate2D, angle: float, ?count: int
  → copies: [{elements: Elements, ?error: Error}]

### ScaleElements
# Scales elements on the floor plan or in the current 2D view by a factor around a center point with Archicad's Resize edit, in one undo step. Resize scales X and Y by the same ratio, so factorY, if given, must equal factor. Supported types: Wall, Column, Beam, Slab, Roof, Mesh, Zone, Line, PolyLine, Arc, Circle, Spline, Hatch and Hotspot. An element of another type (library parts such as objects, lamps, doors and windows, stairs, railings, curtain walls, shells, morphs, texts, subelements, dimensions, labels, ...) or one that cannot be edited gets a failed execution result naming the reason, and the other elements are still scaled. (since 2.0.0)
  elements: Elements, center: Coordinate2D, factor: float, ?factorY: float
  → executionResults: ExecutionResults

### DeleteElements
# Deletes elements. The zones of the call are deleted before all the other elements, so an automatic zone deleted together with its bounding walls is gone before its boundary is; deleting the boundary of an automatic zone without the zone itself can open Archicad's modal 'No closed polygon found' dialog, which blocks the command until someone clicks it in Archicad. Returns an execution result for each input element: an element that could not be deleted (for example because its layer is locked) or a guid that is not in the project gets a failed execution result instead of being skipped silently, and does not stop the other elements from being deleted. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each element that passes the checks made before deleting gets wouldDelete, so a script can preview a deletion before making it. (since 1.2.1)
  elements: Elements, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### DeleteSelectedElements
# Deletes the currently selected elements in one undo step, the same as pressing the Delete key. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true and lists the selected elements, with wouldDelete when there is at least one, or fails when one of them cannot be edited (Archicad then deletes none of them). (since 1.7.3)
  ?dryRun: DryRun
  → ?dryRun: DryRunFlag, success: bool, ?error: Error, ?wouldDelete: bool, ?elements: Elements

### LockElements
# Locks the given elements. Manual lock, not teamwork! (since 1.5.2)
  elements: Elements
  → ExecutionResult

### UnlockElements
# Unlocks the given elements. Manual lock, not teamwork! (since 1.5.2)
  elements: Elements
  → ExecutionResult

### RefreshElements
# Refreshes (rebuilds) the given elements, for example placed Objects, Windows and Doors that still show the old geometry after their library part's script or embedded file changed. Set force to true to run the parameter script of GDL-based elements too. The elements are looked up in the current database (floor plan, section or detail window). Returns an execution result for each input element. The refresh cannot be undone. (since 1.8.0)
  elements: Elements, ?force: bool
  → executionResults: ExecutionResults

### GetGDLParametersOfElements
# Gets all the GDL parameters (name, type, value) of the given elements. (since 1.0.7)
  elements: Elements
  → gdlParametersOfElements: [GDLParameterList]

### SetGDLParametersOfElements
# Sets the given GDL parameters of the given elements. An element Archicad does not let the user edit (its layer locked, the element locked, or not reserved by the user in Teamwork) gets a failed execution result naming that reason, whatever the parameter. On a Curtain Wall Frame, A, B, ac_frameWidth and ac_frameDepth mirror the frame's contour, which Archicad derives from the frame's settings, so they are rejected instead of reporting a change that does not take effect; a frame without a library part (an invisible Boundary frame, for example) has no GDL parameters. The parameters are read back after the change, and a written parameter Archicad did not keep (e.g. one it sets from the element's own settings, like AC_TextSize_1 of a label) gives a failed execution result naming it. With dryRun true no element is changed and no undo step is created: the parameters are written to the element's parameter list and its Parameter Script runs as in a real run, the response has dryRun set to true, and each element that passes the checks made before changing it gets wouldChange, listing the parameters a real run would change (the given ones and the ones the Parameter Script changes with them) with their old and new values. (since 1.0.7)
  ?dryRun: DryRun
  elementsWithGDLParameters[]: elementId: ElementId, gdlParameters: SetGDLParameterArray
  → ?dryRun: DryRunFlag, executionResults: ChangeExecutionResults

### GetMarkerParametersOfElements
# Gets the marker library part and the marker's GDL parameters (name, type, value) of the given Window and Door elements. The marker is the stamp drawn next to the opening on the floor plan; its parameters are separate from the opening's own GDL parameters, which GetGDLParametersOfElements returns. (since 1.7.1)
  elements: Elements
  → markerParametersOfElements: [{?libPart: LibPartDetails, parameters: [StoredGDLParameter]} | ErrorItem]

### SetMarkerParametersOfElements
# Sets the given GDL parameters of the marker of the given Window and Door elements. The opening's own settings and the other marker parameters are left as they are. (since 1.7.1)
  elementsWithMarkerParameters[]: elementId: ElementId, markerParameters: [{name: string, value: any} | {index: int, value: any}]
  → executionResults: ExecutionResults

### GetURLReferencesOfElements
# Gets the web link (URL reference) of the given elements: a URL with a description, shown in Archicad in the element's settings under Element Information > Link. An element without a link gets the error APIERR_NOUSERDATA. (since 1.8.0)
  elements: Elements
  → urlReferences: [{url: string, description: string} | ErrorItem]

### SetURLReferencesOfElements
# Sets the web link (URL reference) of the given elements: a URL with a description, shown in Archicad in the element's settings under Element Information > Link. Fails with APIERR_MOREUSER for an element that already holds a link. (since 1.8.0)
  elementsWithURLReferences[]: elementId: ElementId, url: string, ?description: string
  → executionResults: ExecutionResults

### ChangeLibraryPartOfElements
# Changes the library part of the given Object, Lamp, Window, Door, Skylight, Zone and symbol Label elements to another library part of the same type, given by name, index or guid, e.g. to replace missing library parts with ones from the loaded libraries. The elements themselves (guid, properties, classifications) are kept. Components of stairs and railings are not supported, even when they are reported as Objects. Optionally keeps the values of the GDL parameters with the same name and type, and the size (A and B). (since 1.8.0)
  elementsWithLibraryPart[]: elementId: ElementId, libraryPart: {name: string} | {index: int} | {guid: string}, ?keepParameters: bool, ?keepSize: bool
  → executionResults: ExecutionResults

### GetCalculatedParametersOfCurtainWallSubElements
# Gets the GDL parameters (name, type, value) of the given Curtain Wall Frame, Panel, Junction and Accessory elements as Archicad calculated them for their place in the curtain wall. GetGDLParametersOfElements returns the parameters the sub-element was set up with instead. (since 2.0.0)
  elements: Elements
  → calculatedParametersOfElements: [{parameters: [{name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, value: any, ?valueDescription: string, ?itemDescriptions: [string], flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"]}]} | ErrorItem]

### GetHotspotsOfElements
# Gets the 2D hotspots of the given library part instances (Objects, Lamps, Windows, Doors, Skylights, Zones, Curtain Wall parts, etc.), e.g. to dimension to them. (since 1.8.0)
  elements: Elements
  → hotspotsOfElements: [{hotspots: [Coordinate2D]} | ErrorItem]

### SetMarkerLibraryPartOfElements
# Changes which library part the marker of the given Window and Door elements uses, given by its name (find the available ones with GetAvailableLibraryParts); only a marker library part for the opening's type is accepted. The marker gets the new library part's default parameters, which SetMarkerParametersOfElements can change afterwards; the opening's own settings are left as they are. (since 2.0.0)
  elementsWithMarkerLibraryPart[]: elementId: ElementId, libraryPartName: string
  → executionResults: ExecutionResults

### RunParameterScriptOfElements
# Runs the parameter script of the library part of the given elements (objects, lamps, windows, doors, etc.), so that parameter values that depend on other parameters are updated, e.g. after SetGDLParametersOfElements. (since 1.7.3)
  elements: Elements
  → executionResults: ExecutionResults

### CreateColumns
# Creates Column elements based on the given parameters. Takes the same cut fill pens and cover fill as ModifyColumns, besides the position, size, slant, cross section and veneer; settings not given come from the Column tool defaults or the favorite. Not written by either command: the surfaces of the column segments, and the cut fill pens before Archicad 27. (since 1.0.7)
  columnsData[]: ?favoriteName: string, ?id: string, ?layerIndex: int, coordinates: {x: float, y: float, z: float}, ?height: float, ?axisRotationAngle: float, ?slantAngle: float, ?isSlanted: bool, ?slantDirectionAngle: float, ?width: float, ?depth: float, ?coreAnchor: ColumnCoreAnchor, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?veneer: ColumnVeneer, ?floorIndex: int, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → elements: ElementIdsOrErrors

### CreateWalls
# Creates Wall elements based on the given parameters. Takes the same wall settings as ModifyWalls, applied by the same code, except geometryType and profileType, which the new wall takes from the favorite or the Wall tool defaults (its plan outline is always Straight), and bottomOffset, which comes from zCoordinate. Neither command can write a Polygonal outline (it needs an outline polygon, which these commands do not take), connectionPriority or junctionSequence (Archicad ignores writes to them; GetDetailsOfElements reads them), and on Archicad 29 any story visibility other than 'Home story only' and 'All relevant stories'. (since 1.4.0)
  wallsData[]: ?favoriteName: string, ?id: string, ?layerIndex: int, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?floorIndex: int, ?zCoordinate: float, ?height: float, ?thickness: float, ?offset: float, ?arcAngle: float, ?referenceLineLocation: WallReferenceLineLocation, ?flipped: bool, ?slantAlpha: float, ?slantBeta: float, ?topOffset: float, ?relativeTopStory: float, ?zoneRel: WallZoneRelation, ?visibility: StoryVisibility, ?isAutoOnStoryVisibility: bool, ?referenceMaterial: OverriddenMaterial, ?oppositeMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?structureType: WallStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?contourPen: int, ?contourPen3D: int, ?contourLineTypeId: AttributeId, ?belowViewLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?useCompositePriority: bool, ?linkToSettings: LinkToSettings, ?inheritEndSurface: bool, ?alignTexture: bool, ?polyCanChange: bool, ?materialsChained: bool, ?logHeight: float
  → elements: ElementIdsOrErrors

### CreateBeams
# Creates Beam elements based on the given parameters. Takes the same cut fill pens and cover fill as ModifyBeams, besides the position, shape, slant and cross section; settings not given come from the Beam tool defaults or the favorite. Not written by either command: the surfaces of the beam segments, and the cut fill pens before Archicad 27. (since 1.4.0)
  beamsData[]: ?favoriteName: string, ?id: string, ?layerIndex: int, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?floorIndex: int, zCoordinate: float, ?offset: float, ?slantAngle: float, ?isSlanted: bool, ?profileAngle: float, ?arcAngle: float, ?verticalCurveHeight: float, ?width: float, ?height: float, ?anchorPoint: BeamAnchorPoint, ?circleBased: bool, ?isWidthAndHeightLinked: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → elements: ElementIdsOrErrors

### CreateStairs
# Creates Stair elements based on the given baseline and parameters, optionally with the segment type of each baseline edge and the turn at each baseline point (landings and winders). Accepts the same settings as ModifyStairs: the step values with their locks, the finish and structure visibility, the extra treads, the walking line, the numbering, the walking direction, and the tread, riser and structure settings of the flights and the landings; settings not given come from the Stair tool defaults or the favorite. (since 1.5.0)
  stairsData[]: ?favoriteName: string, ?id: string, baseLinePoints: [Coordinate2D], ?baselinePosition: "Left"|"Right"|"Center", ?baselineOffset: float, zCoordinate: float, ?floorIndex: int, ?totalHeight: float, ?flightWidth: float, ?stepNum: int, ?riserHeight: float, ?treadDepth: float, ?baseLineEdges: [{segmentType: "Flight"|"Landing"|"DividedLanding"}], ?baseLineVertices: [{turnType: "None"|"Landing"|"Winder"|"DividedLanding", ?minLandingStartEdgeOffset: float, ?minLandingEndEdgeOffset: float}], ?treadDepthLocked: bool, ?totalHeightLocked: bool, ?finishVisible: bool, ?extraTopTread: bool, ?extraBottomTread: bool, ?walkingLinePosition: "Left"|"Right"|"Center"|"Auto", ?walkingLineOffset: float, ?numberingType: "Treads"|"Risers", ?inputDirection: "Upward"|"Inverse", ?uniformFinish: bool, ?uniformMonolithAttributes: bool, ?uniformDrainings: bool, ?structureVisibility: bool, ?treads: [{role: "Run"|"Landing", ?visible: bool, ?thickness: float, ?offset: float, ?nosingType: "ByValue"|"BySlanting", ?nosingValue: float, ?nosingSlant: float}], ?risers: [{role: "Run"|"Landing", ?visible: bool, ?thickness: float, ?offset: float, ?crossSection: "Simple"|"Slanted", ?angle: float, ?position: "OnTread"|"BehindTread"}], ?structures: [{role: "Run"|"Landing", side: "LeftSide"|"RightSide"|"UnderSide", ?visible: bool, ?structureType: "Side"|"Monolith"|"BeamSupport"|"CantileveredSupport", ?bottomType: "Stepped"|"Flat"|"Smooth", ?thickness: float, ?horizontalThickness: float}]
  → elements: ElementIdsOrErrors

### SolveStairBaseline
# Runs the Archicad stair solver on the given Stair baselines and parameters without creating any element. Returns for each one whether the baseline was already correct, could be solved or could not be solved, with the baseline and the main stair settings after solving. Available from Archicad 27. (since 1.7.3)
  stairsData: [StairBaselineData]
  → solutions: [StairBaselineSolution | ErrorItem]

### CreateSlabs
# Creates Slab elements based on the given parameters. Takes the same surfaces (top, side, bottom), cut fill pens and floor fill as ModifySlabs, besides the outline, holes, level and structure; settings not given come from the Slab tool defaults or the favorite. Not written by either command: the surface of a single edge, and the cut fill pens before Archicad 27; of the floor fill orientation Archicad applies only the type through the API. (since 1.0.7)
  slabsData[]: ?favoriteName: string, ?id: string, ?layerIndex: int, level: float, ?thickness: float, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?floorIndex: int, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?floorFill: FloorFill
  → elements: ElementIdsOrErrors

### CreateWindows
# Creates Window elements in host walls based on the given parameters. (since 1.4.0)
  windowsData[]: ownerWallId: ElementId, ?width: float, ?height: float, ?sillHeight: float, centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectSectionAttributes: bool, ?libraryPartName: string, ?favoriteName: string
  → elements: ElementIdsOrErrors

### CreateDoors
# Creates Door elements in host walls based on the given parameters. (since 1.4.0)
  doorsData[]: ownerWallId: ElementId, ?width: float, ?height: float, ?sillHeight: float, centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectSectionAttributes: bool, ?libraryPartName: string, ?favoriteName: string
  → elements: ElementIdsOrErrors

### CreateOpenings
# Creates Opening elements in the given host elements. (since 1.4.0)
  openingsData[]: ownerElementId: ElementId, basePoint: Coordinate3D, ?width: float, ?height: float
  → elements: ElementIdsOrErrors

### GetOpeningDefault
# Returns the settings of the Opening tool defaults: the extrusion parameters (as GetOpeningDetails returns them) and the floor plan parameters (as GetOpeningFloorPlanParameters returns them). Available from Archicad 29. (since 1.7.3)
  → extrusionParameters: {?constraint: "ForcedVertical"|"ForcedHorizontal"|"Aligned"|"Free", ?limitType: "Infinite"|"Finite"|"HalfInfinite", ?linkedStatus: "Linked"|"NotLinked", ?shapeType: "Rectangular"|"Circular"|"Polygonal", ?width: float, ?height: float, anchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight", ?anchorAltitude: float, ?extrusionStartOffset: float, ?finiteBodyLength: float, isExtrusionSurfaceOverridden: bool, ?extrusionSurfaceId: AttributeId, isEndSurfaceOverridden: bool, ?endSurfaceId: AttributeId, areOverriddenSurfacesLinked: bool}, floorPlanParameters: {?floorPlanDisplayMode: "Symbolic"|"SymbolicCut"|"SymbolicOverhead"|"Projected", ?dividedOpeningMode: "Disconnected"|"Connected", ?openEdgeStyle: "Hide"|"ShowUncut"|"ShowOverhead", ?showReferenceAxis: bool, ?referenceAxisPen: int, ?referenceAxisLineTypeId: AttributeId, ?referenceAxisOverhang: float, ?cutSurfacesUseLineOfCutElements: bool, ?cutSurfacesLinePen: int, ?cutSurfacesLineTypeId: AttributeId, ?outlinesUseLineOfCutElements: bool, ?outlinesUncutLinePen: int, ?outlinesUncutLineTypeId: AttributeId, ?outlinesOverheadLinePen: int, ?outlinesOverheadLineTypeId: AttributeId, ?useCoverFills: bool, ?coverFillsUseFillsOfCutElements: bool, ?coverFillId: AttributeId, ?coverFillPen: int, ?coverFillBackgroundPen: int, ?coverFillOrientation: HatchOrientationType, ?coverFillTransformation: CoverFillTransformation, ?cutSymbolLibPartId: Guid, ?unCutSymbolLibPartId: Guid}

### SetOpeningDefault
# Changes the settings of the Opening tool defaults, with the names GetOpeningDefault returns. Only the given settings change. Available from Archicad 29. (since 1.8.0)
  ?extrusionParameters: {?constraint: "ForcedVertical"|"ForcedHorizontal"|"Aligned"|"Free", ?limitType: "Infinite"|"Finite"|"HalfInfinite", ?linkedStatus: "Linked"|"NotLinked", ?shapeType: "Rectangular"|"Circular"|"Polygonal", ?width: float, ?height: float, ?anchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight", ?anchorAltitude: float, ?extrusionStartOffset: float, ?finiteBodyLength: float, ?isExtrusionSurfaceOverridden: bool, ?extrusionSurfaceId: AttributeId, ?isEndSurfaceOverridden: bool, ?endSurfaceId: AttributeId, ?areOverriddenSurfacesLinked: bool}, ?floorPlanParameters: {?floorPlanDisplayMode: "Symbolic"|"SymbolicCut"|"SymbolicOverhead"|"Projected", ?dividedOpeningMode: "Disconnected"|"Connected", ?openEdgeStyle: "Hide"|"ShowUncut"|"ShowOverhead", ?showReferenceAxis: bool, ?referenceAxisPen: int, ?referenceAxisLineTypeId: AttributeId, ?referenceAxisOverhang: float, ?cutSurfacesUseLineOfCutElements: bool, ?cutSurfacesLinePen: int, ?cutSurfacesLineTypeId: AttributeId, ?outlinesUseLineOfCutElements: bool, ?outlinesUncutLinePen: int, ?outlinesUncutLineTypeId: AttributeId, ?outlinesOverheadLinePen: int, ?outlinesOverheadLineTypeId: AttributeId, ?useCoverFills: bool, ?coverFillsUseFillsOfCutElements: bool, ?coverFillId: AttributeId, ?coverFillPen: int, ?coverFillBackgroundPen: int, ?coverFillOrientation: HatchOrientationType, ?coverFillTransformation: CoverFillTransformation, ?cutSymbolLibPartId: Guid, ?unCutSymbolLibPartId: Guid, ?clearCutSymbol: bool, ?clearUnCutSymbol: bool}
  → elementType: ElementType

### PlaceOpenings
# Places openings with the Opening tool settings at points of their parent elements. A point off the parent element's surface is moved to the closest point of the surface. Each opening can be given its own extrusion and floor plan settings, which change only that opening and not the tool's settings. Available from Archicad 29. (since 1.8.0)
  openingsData[]: parentElementId: ElementId, point: Coordinate3D, ?extrusionParameters: {?constraint: "ForcedVertical"|"ForcedHorizontal"|"Aligned"|"Free", ?limitType: "Infinite"|"Finite"|"HalfInfinite", ?linkedStatus: "Linked"|"NotLinked", ?shapeType: "Rectangular"|"Circular"|"Polygonal", ?width: float, ?height: float, ?anchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight", ?anchorAltitude: float, ?extrusionStartOffset: float, ?finiteBodyLength: float, ?isExtrusionSurfaceOverridden: bool, ?extrusionSurfaceId: AttributeId, ?isEndSurfaceOverridden: bool, ?endSurfaceId: AttributeId, ?areOverriddenSurfacesLinked: bool}, ?floorPlanParameters: {?floorPlanDisplayMode: "Symbolic"|"SymbolicCut"|"SymbolicOverhead"|"Projected", ?dividedOpeningMode: "Disconnected"|"Connected", ?openEdgeStyle: "Hide"|"ShowUncut"|"ShowOverhead", ?showReferenceAxis: bool, ?referenceAxisPen: int, ?referenceAxisLineTypeId: AttributeId, ?referenceAxisOverhang: float, ?cutSurfacesUseLineOfCutElements: bool, ?cutSurfacesLinePen: int, ?cutSurfacesLineTypeId: AttributeId, ?outlinesUseLineOfCutElements: bool, ?outlinesUncutLinePen: int, ?outlinesUncutLineTypeId: AttributeId, ?outlinesOverheadLinePen: int, ?outlinesOverheadLineTypeId: AttributeId, ?useCoverFills: bool, ?coverFillsUseFillsOfCutElements: bool, ?coverFillId: AttributeId, ?coverFillPen: int, ?coverFillBackgroundPen: int, ?coverFillOrientation: HatchOrientationType, ?coverFillTransformation: CoverFillTransformation, ?cutSymbolLibPartId: Guid, ?unCutSymbolLibPartId: Guid, ?clearCutSymbol: bool, ?clearUnCutSymbol: bool}
  → elements: ElementIdsOrErrors

### GetOpeningFloorPlanParameters
# Returns the floor plan parameters of Opening elements: the floor plan display mode, the divided opening mode, the open edge style, the reference axis, the cut surface and outline lines, the cover fills and the cut and uncut symbols. Available from Archicad 29. (since 1.7.3)
  elements: Elements
  → openings: [{elementId: ElementId, floorPlanParameters: {?floorPlanDisplayMode: "Symbolic"|"SymbolicCut"|"SymbolicOverhead"|"Projected", ?dividedOpeningMode: "Disconnected"|"Connected", ?openEdgeStyle: "Hide"|"ShowUncut"|"ShowOverhead", showReferenceAxis: bool, referenceAxisPen: int, referenceAxisLineTypeId: AttributeId, referenceAxisOverhang: float, cutSurfacesUseLineOfCutElements: bool, cutSurfacesLinePen: int, cutSurfacesLineTypeId: AttributeId, outlinesUseLineOfCutElements: bool, outlinesUncutLinePen: int, outlinesUncutLineTypeId: AttributeId, outlinesOverheadLinePen: int, outlinesOverheadLineTypeId: AttributeId, useCoverFills: bool, coverFillsUseFillsOfCutElements: bool, coverFillId: AttributeId, coverFillPen: int, coverFillBackgroundPen: int, coverFillOrientation: HatchOrientationType, ?coverFillTransformation: CoverFillTransformation, ?cutSymbolLibPartId: Guid, ?unCutSymbolLibPartId: Guid}} | ErrorItem]

### SetOpeningFloorPlanParameters
# Changes the floor plan parameters of Opening elements returned by GetOpeningFloorPlanParameters, and sets or removes their cut and uncut symbols. Available from Archicad 29. (since 1.7.3)
  openingsWithFloorPlanParameters[]: elementId: ElementId, floorPlanParameters: {?floorPlanDisplayMode: "Symbolic"|"SymbolicCut"|"SymbolicOverhead"|"Projected", ?dividedOpeningMode: "Disconnected"|"Connected", ?openEdgeStyle: "Hide"|"ShowUncut"|"ShowOverhead", ?showReferenceAxis: bool, ?referenceAxisPen: int, ?referenceAxisLineTypeId: AttributeId, ?referenceAxisOverhang: float, ?cutSurfacesUseLineOfCutElements: bool, ?cutSurfacesLinePen: int, ?cutSurfacesLineTypeId: AttributeId, ?outlinesUseLineOfCutElements: bool, ?outlinesUncutLinePen: int, ?outlinesUncutLineTypeId: AttributeId, ?outlinesOverheadLinePen: int, ?outlinesOverheadLineTypeId: AttributeId, ?useCoverFills: bool, ?coverFillsUseFillsOfCutElements: bool, ?coverFillId: AttributeId, ?coverFillPen: int, ?coverFillBackgroundPen: int, ?coverFillOrientation: HatchOrientationType, ?coverFillTransformation: CoverFillTransformation, ?cutSymbolLibPartId: Guid, ?unCutSymbolLibPartId: Guid, ?clearCutSymbol: bool, ?clearUnCutSymbol: bool}
  → executionResults: ExecutionResults

### GetOpeningSymbolParameters
# Returns the GDL parameters of the cut and uncut floor plan symbols of Opening elements, in the format of GetGDLParametersOfElements. A symbol the opening does not have is left out. Available from Archicad 29. (since 1.8.0)
  elements: Elements
  → openings: [{elementId: ElementId, ?cutSymbolParameters: [{name: string, type: "Integer"|"Length"|"Angle"|"RealNumber"|"LightSwitch"|"RGBColor"|"Intensity"|"LineType"|"Material"|"FillPattern"|"PenColor"|"String"|"Boolean"|"BuildingMaterial"|"Profile", ?dimension1: int, ?dimension2: int, value: any}], ?unCutSymbolParameters: [{name: string, type: "Integer"|"Length"|"Angle"|"RealNumber"|"LightSwitch"|"RGBColor"|"Intensity"|"LineType"|"Material"|"FillPattern"|"PenColor"|"String"|"Boolean"|"BuildingMaterial"|"Profile", ?dimension1: int, ?dimension2: int, value: any}]} | ErrorItem]

### SetOpeningSymbolParameters
# Changes the GDL parameters of the cut and uncut floor plan symbols of Opening elements, in the format of SetGDLParametersOfElements. Only the given parameters are changed. Available from Archicad 29. (since 1.8.0)
  elements[]: elementId: ElementId, ?cutSymbolParameters: [{name: string, ?index1: int, ?index2: int, value: any}], ?unCutSymbolParameters: [{name: string, ?index1: int, ?index2: int, value: any}]
  → executionResults: ExecutionResults

### GetOpeningDetails
# Returns the details of Opening elements: whether they exist, the parent element, the cut and connected elements, the geometry (anchor point, extrusion direction, axes, polygon) and the extrusion parameters (constraint, limit type, linked status, shape type, size, anchor, offsets, surface overrides). Available from Archicad 29. (since 1.7.3)
  elements: Elements
  → openings: [{elementId: ElementId, exists: bool, ?parentElementId: ElementId, cutElements: [ElementIdArrayItem], ?connectedOpenings: [ElementIdArrayItem], geometry: {anchorPoint: Coordinate3D, extrusionDirection: Coordinate3D, xAxis: Coordinate3D, yAxis: Coordinate3D, ?polygon: [Coordinate2D]}, extrusionParameters: {?constraint: "ForcedVertical"|"ForcedHorizontal"|"Aligned"|"Free", ?limitType: "Infinite"|"Finite"|"HalfInfinite", ?linkedStatus: "Linked"|"NotLinked", ?shapeType: "Rectangular"|"Circular"|"Polygonal", ?width: float, ?height: float, anchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight", ?anchorAltitude: float, ?extrusionStartOffset: float, ?finiteBodyLength: float, isExtrusionSurfaceOverridden: bool, ?extrusionSurfaceId: AttributeId, isEndSurfaceOverridden: bool, ?endSurfaceId: AttributeId, areOverriddenSurfacesLinked: bool}} | ErrorItem]

### SetOpeningDetails
# Changes the details of Opening elements: the parent element, the cut elements, the polygon, a transformation of the geometry and the extrusion parameters (constraint, limit type, linked status, shape type, size, anchor, offsets, surface overrides) returned by GetOpeningDetails. Available from Archicad 29. (since 1.7.3)
  openingsWithDetails[]: elementId: ElementId, ?parentElementId: ElementId, ?addCutElements: [ElementIdArrayItem], ?removeCutElements: [ElementIdArrayItem], ?polygon: [Coordinate2D], ?transformation: [float], ?extrusionParameters: {?constraint: "ForcedVertical"|"ForcedHorizontal"|"Aligned"|"Free", ?limitType: "Infinite"|"Finite"|"HalfInfinite", ?linkedStatus: "Linked"|"NotLinked", ?shapeType: "Rectangular"|"Circular"|"Polygonal", ?width: float, ?height: float, ?anchor: "TopLeft"|"TopCenter"|"TopRight"|"MiddleLeft"|"Center"|"MiddleRight"|"BottomLeft"|"BottomCenter"|"BottomRight", ?anchorAltitude: float, ?extrusionStartOffset: float, ?finiteBodyLength: float, ?isExtrusionSurfaceOverridden: bool, ?extrusionSurfaceId: AttributeId, ?isEndSurfaceOverridden: bool, ?endSurfaceId: AttributeId, ?areOverriddenSurfacesLinked: bool}
  → executionResults: ExecutionResults

### CreateMorphs
# Creates Morph elements from simple box definitions or arbitrary bodies. Each item may name a favorite (favoriteName) to start from, a layer (layerIndex) and an Element ID (id); the given geometry and floor are kept. (since 1.4.0)
  morphsData[]: ?favoriteName: string, ?id: string, ?layerIndex: int, basePoint: Coordinate3D, ?size: Dimensions3D, ?body: MorphBody, ?buildingMaterialId: AttributeId, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?surfaceId: AttributeId, ?topExpansion: float, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateRoofs
# Creates Roof elements based on footprint, level and roof profile data. Creates a multi-plane roof by default; pass 'pivotLine' (and optionally 'angle') to create a single-plane roof instead. (since 1.4.0)
# ⚠ Releases <=1.5.5: NON-FUNCTIONAL (stub, #467) — model roofs as Slab/Morph instead. FIXED since release 1.5.6 (#482): multi-plane works; NEW ?pivotLine:{begCoordinate,endCoordinate} + ?angle (rad) for single-plane (the plane rises to the left of the line direction).
  roofsData[]: level: float, ?floorIndex: int, ?thickness: float, polygonCoordinates: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?pivotLine: RoofPivotLine, ?angle: float, ?eavesOverhang: float, ?levels: [RoofLevel], ?structureType: RoofStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateShells
# Creates extruded, revolved and ruled Shell elements from profile polylines, with thickness, structure, an optional clipping contour and holes. (since 2.0.0)
  shellsData[]: ?favoriteName: string, ?id: string, shellClass: "Extruded"|"Revolved"|"Ruled", ?floorIndex: int, ?basePlane: CoordinateSystem3D, profile: ShellProfile, ?thickness: float, ?isFlipped: bool, ?structureType: RoofStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?extrusionVector: Coordinate3D, ?extrusionStart: Coordinate3D, ?shapePlaneTilt: float, ?begPlaneTilt: float, ?endPlaneTilt: float, ?slantAngle: float, ?axis: CoordinateSystem3D, ?revolutionAngle: float, ?beginAngle: float, ?distortionAngle: float, ?segmentsByCircle: int, ?secondProfile: ShellProfile, ?profilePlane: CoordinateSystem3D, ?secondProfilePlane: CoordinateSystem3D, ?morphingRule: "Paired"|"Smooth", ?contour: ShellCutPolygon, ?holes: [ShellCutPolygon], ?begShapeEdgeTrim: ShellEdgeTrim, ?endShapeEdgeTrim: ShellEdgeTrim, ?begSideEdgeTrim: ShellEdgeTrim, ?endSideEdgeTrim: ShellEdgeTrim
  → elements: ElementIdsOrErrors

### CreateSkylights
# Creates Skylight elements with a roof or shell owner and a floor plan anchor position. It takes the same settings as ModifySkylights (anchor point, fix mode, width, height, azimuth and elevation angles, mirroring, floor plan display, pens, line types, section fill, surface and the library part flags) and optionally a library part; the settings not given come from the Skylight tool defaults or a favorite. Surface placement is handled by Archicad and has not yet been verified for this command. (since 2.0.0)
  skylightsData[]: ?favoriteName: string, ?id: string, ownerId: ElementId, ?libraryPartName: string, anchorPosition: Coordinate2D, ?anchorPoint: "BottomCenter"|"BottomLeft"|"BottomRight"|"TopCenter"|"TopLeft"|"TopRight", ?fixMode: "Horizontal"|"Vertical", ?width: float, ?height: float, ?azimuthAngle: float, ?elevationAngle: float, ?reflected: bool, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?surfaceId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool
  → elements: ElementIdsOrErrors

### ModifySkylights
# Modifies Skylight elements: anchor position and anchor point, fix mode, width, height, azimuth and elevation angles, mirroring, floor plan display option, pens, line types, section fill and pens, surface and the use-the-library-part's-settings flags - the same settings CreateSkylights takes and GetDetailsOfElements returns. Only the given settings change. Not written by this command: the owner roof or shell, the anchor level and the vertical link (Archicad places the skylight on its owner), the plane of a multi-plane roof it sits on, the dimension marker (a separate element) and the library part's own parameters (use SetGDLParametersOfElements). Archicad may set the elevation angle again from the owner. (since 2.0.0)
  skylightsWithDetails[]: elementId: ElementId, ?anchorPosition: Coordinate2D, ?anchorPoint: "BottomCenter"|"BottomLeft"|"BottomRight"|"TopCenter"|"TopLeft"|"TopRight", ?fixMode: "Horizontal"|"Vertical", ?width: float, ?height: float, ?azimuthAngle: float, ?elevationAngle: float, ?reflected: bool, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?surfaceId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool
  → executionResults: ExecutionResults

### CreateRailings
# Creates Railing elements along a reference polyline. Posts, rails, handrails, toprails, panels and balusters come from the favorite, from an existing railing (templateElementId) or from the Railing tool defaults; Archicad generates one node per vertex and one segment per pair of consecutive vertices. (since 1.8.0)
  railingsData[]: ?favoriteName: string, ?id: string, ?templateElementId: ElementId, coordinates: [Coordinate2D], ?floorIndex: int, ?bottomOffset: float, ?height: float
  → elements: ElementIdsOrErrors

### CreateRailingsFromPolyline
# Creates Railing elements along a 3D reference polyline: each node has its own elevation and segments can be arcs. Posts, rails, handrails, toprails, panels and balusters come from the favorite or from the Railing tool defaults. (since 2.0.0)
  railingsData[]: ?favoriteName: string, ?id: string, ?floorIndex: int, polylineCoordinates: [Coordinate3D], ?polylineArcs: [PolyArc], ?height: float
  → elements: ElementIdsOrErrors

### CreateCurtainWalls
# Creates Curtain Wall elements along a reference polyline with a column (primary) and row (secondary) pattern. The frame and panel classes come from the favorite or from the Curtain Wall tool defaults; the pattern cells can assign them to the grid. (since 1.7.2)
  curtainWallsData[]: ?favoriteName: string, ?id: string, coordinates: [Coordinate2D], ?zCoordinate: float, ?floorIndex: int, ?height: float, ?primaryPattern: CurtainWallPattern, ?secondaryPattern: CurtainWallPattern, ?cells: [CurtainWallPatternCell]
  → elements: ElementIdsOrErrors

### CreateAssociativeDimensions
# Creates associative dimensions from explicit witness point references: linear by default, or cumulative, baseline or elevation dimensions (appearance). A witness point can also be static, given by its coordinate instead of an element. (since 1.4.0)
  dimensionsData[]: ?favoriteName: string, ?textHeight: float, ?textPen: int, ?textFrame: bool, ?appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", ?elevationOrigin: DimensionOrigin, ?linePen: int, ?marker: {?type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", ?pen: int}, ?defaultWitnessForm: "None"|"Small"|"Large"|"Fix", ?defaultWitnessVal: float, referencePoint: Coordinate2D, direction: Coordinate2D, ?floorIndex: float, witnessPoints: [AssociativeWitnessPoint]
  → elements: ElementIdsOrErrors

### CreateAssociativeDimensionsOnSection
# Creates associative dimensions on section elements using common wall, slab, beam, column, door and window presets: linear by default, or cumulative, baseline or elevation dimensions (appearance), e.g. level marks. The preset points of multiple section elements can be merged into one continuous dimension chain via sectionElementIds. For Opening tool elements, which Archicad does not associate with dimensions, the OpeningEdges preset places fixed points at their edges instead. (since 1.4.0)
  dimensionsData[]: ?favoriteName: string, ?textHeight: float, ?textPen: int, ?textFrame: bool, ?appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", ?elevationOrigin: DimensionOrigin, ?linePen: int, ?marker: {?type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", ?pen: int}, ?defaultWitnessForm: "None"|"Small"|"Large"|"Fix", ?defaultWitnessVal: float, ?sectionElementId: ElementId, ?sectionElementIds: [ElementId], referencePoint: Coordinate2D, preset: "WallCompositeFaces"|"WallSkinBorders"|"SlabCompositeFaces"|"SlabSkinBorders"|"BeamOrColumnRefLineEndPoints"|"BeamOrColumnBoundingBoxCorners"|"DoorWindowWallHoleCorners"|"DoorWindowModelHotspots"|"OpeningEdges", ?direction: Coordinate2D, ?skinBorderIndices: [int], ?beginPlane: bool, ?totalSizePlane: bool, ?placeOnTop: bool
  → elements: ElementIdsOrErrors

### CreateWallThicknessDimensions
# Creates associative wall thickness dimensions for the given walls. (since 1.4.0)
  dimensionsData[]: ?favoriteName: string, ?textHeight: float, ?textPen: int, ?textFrame: bool, ?appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", ?elevationOrigin: DimensionOrigin, ?linePen: int, ?marker: {?type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", ?pen: int}, ?defaultWitnessForm: "None"|"Small"|"Large"|"Fix", ?defaultWitnessVal: float, wallId: ElementId, referencePoint: Coordinate2D, direction: Coordinate2D
  → elements: ElementIdsOrErrors

### ModifyAssociativeDimensions
# Changes the settings of existing linear dimensions (the Dimension tool's elements, also in sections): the dimension type, the elevation origin, the line pen, the marker type and pen, the text height, pen and frame and the witness line form and value, with the same keys as the dimension creation commands. The text and witness line settings are applied to every witness point. Not written: the witness points, the dimension line position and direction (use MoveElements), the marker size, the text content and position, the witness extension line, the layout and the hole and composite wall dimensioning settings. (since 2.0.0)
  dimensionsWithDetails[]: elementId: ElementId, ?textHeight: float, ?textPen: int, ?textFrame: bool, ?appearance: "Linear"|"Cumulative"|"Baseline"|"Elevation", ?elevationOrigin: DimensionOrigin, ?linePen: int, ?marker: {?type: "CrossLine"|"EmptyCircle"|"SlashLine60"|"OpenArrow30"|"ClosedArrow30"|"FullArrow30"|"SlashLine45"|"CrossCircle"|"OpenArrow90"|"ClosedArrow90"|"FullArrow90"|"FullCircle"|"PepitaCircle"|"BandArrow"|"OpenArrow60"|"ClosedArrow60"|"FullArrow60"|"SlashLine75", ?pen: int}, ?defaultWitnessForm: "None"|"Small"|"Large"|"Fix", ?defaultWitnessVal: float
  → executionResults: ExecutionResults

### GetDimensionData
# Gets the data of existing dimension chains: the line pen, the marker type and pen and the default witness line, and per witness point the coordinates, measured value, witness line and the text height, pen and frame. (since 1.5.0)
  elements[]: elementId: ElementId
  → dimensionsData: [DimensionDataOrError]

### GetOpeningTransformations
# Gets the placement of Opening elements, Windows, Doors and Skylights without changing them: a global-to-local transformation matrix, its inverse, and the origin and axes in world coordinates derived from the inverse. For Windows, Doors and Skylights the local-to-global matrix is the one Archicad returns, and mirrored ones give a left-handed matrix (isMirrored). For Opening elements it is built from the opening geometry (Archicad 29 and later): origin at the anchor point, the X and Y axes of the opening and Z = X × Y, which points against the extrusion direction. Needs Archicad 27 or later. (since 1.7.3) [AC29+]
  elements: Elements
  → openingTransformations: [{elementId: ElementId, globalToLocal: [float], localToGlobal: [float], origin: Coordinate3D, xAxis: Coordinate3D, yAxis: Coordinate3D, zAxis: Coordinate3D, determinant: float, isMirrored: bool} | ErrorItem]

### CreateZones
# Creates Zone elements based on the given parameters. Takes the same zone settings as ModifyZones (name, number, category, zone stamp, levels, contour line and cover fill), applied by the same helpers; the polygon or reference point is only set here. An item whose area would overlap an existing Zone on the same story fails with an error naming that Zone instead of opening Archicad's modal overlap warning, unless its allowOverlap is true. (since 1.1.8)
  zonesData[]: ?favoriteName: string, ?id: string, ?floorIndex: float, name: string, numberStr: string, ?categoryAttributeId: AttributeId, ?stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, ?contourLine: ZoneContourLine, ?coverFill: ZoneCoverFill, ?allowOverlap: bool, ?height: float, ?bottomOffset: float, ?topOffset: float, ?relativeTopStory: float, ?floorThickness: float, geometry: ZoneCreationGeometry
  → elements: ElementIdsOrErrors

### CreatePolylines
# Creates Polyline elements based on the given parameters. (since 1.1.5)
  ?databaseId: DatabaseId
  polylinesData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, ?linePenIndex: int, ?lineTypeIndex: int, ?penWeightMm: float, ?roomSeparator: bool, coordinates: [Coordinate2D], ?arcs: [PolyArc]
  → elements: ElementIdsOrErrors

### CreateLineElements
# Creates Line elements based on the given parameters. (since 1.5.6)
  ?databaseId: DatabaseId
  linesData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, begCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateArcs
# Creates Arc elements based on the given parameters. (since 1.5.6)
  ?databaseId: DatabaseId
  arcsData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, origin: Coordinate2D, radius: float, begAngle: float, endAngle: float, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateCircles
# Creates Circle elements based on the given parameters. (since 1.5.6)
  ?databaseId: DatabaseId
  circlesData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, origin: Coordinate2D, radius: float, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateHotspots
# Creates Hotspot elements based on the given parameters. (since 1.5.6)
  ?databaseId: DatabaseId
  hotspotsData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, position: Coordinate2D, ?height: float, ?penIndex: int
  → elements: ElementIdsOrErrors

### CreateHatches
# Creates Hatch elements based on the given parameters. A hatch can have holes, in the same format SetDetailsOfElements accepts for hatches. (since 1.5.6)
  ?databaseId: DatabaseId
  hatchesData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, coordinates: [Coordinate2D], ?arcs: [PolyArc], ?holes: Holes2D, ?contourPenIndex: int, ?fillPenIndex: int, ?fillBackgroundPenIndex: int, ?foregroundColor: ColorRGB, ?backgroundColor: ColorRGB, ?fillId: AttributeId, ?buildingMaterialId: AttributeId, ?roomSpecial: int, ?showArea: bool
  → elements: ElementIdsOrErrors

### CreateSplines
# Creates Spline elements based on the given parameters. (since 1.5.6)
  ?databaseId: DatabaseId
  splinesData[]: ?favoriteName: string, ?id: string, ?floorInd: float, ?layerIndex: int, coordinates: [Coordinate2D], ?closed: bool, ?roomSeparator: bool, ?linePenIndex: int, ?lineTypeId: AttributeId
  → elements: ElementIdsOrErrors

### CreateObjects
# Creates Object elements based on the given parameters. A library part named in libraryPartName starts from its own default size and GDL parameters, not from those of the part the Object tool holds; the dimensions and the GDL parameters given (by name, in parameters) override them. layerIndex places the element on a layer. With databaseId the objects are placed in that database, e.g. a worksheet, instead of the current one. (since 1.0.7)
  ?databaseId: DatabaseId
  objectsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings, ?floorIndex: int, ?favoriteName: string, ?id: string, ?parameters: [{name: string, value: any}], ?layerIndex: int
  → elements: ElementIdsOrErrors

### CreateLamps
# Creates Lamp elements based on the given parameters. A library part named in libraryPartName starts from its own default size and GDL parameters, not from those of the part the Lamp tool holds; the dimensions and the GDL parameters given (by name, in parameters) override them. layerIndex places the element on a layer. With databaseId the lamps are placed in that database, e.g. a worksheet, instead of the current one. (since 1.5.0)
  ?databaseId: DatabaseId
  lampsData[]: libraryPartName: string, coordinates: Coordinate3D, ?dimensions: Dimensions3D, ?angle: float, ?pen: int, ?lineTypeId: AttributeId, ?surfaceId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectMaterials: bool, ?useObjectSectionAttributes: bool, ?reflected: bool, ?useFixSize: bool, ?fixPoint: int, ?offset: Coordinate2D, ?useFixedAngle: bool, ?isAutoOnStoryVisibility: bool, ?visibility: StoryVisibility, ?linkToSettings: LinkToSettings, ?lightColor: ColorRGB, ?lightIsOn: bool, ?floorIndex: int, ?favoriteName: string, ?id: string, ?parameters: [{name: string, value: any}], ?layerIndex: int
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
# Creates Mesh elements based on the given parameters. (since 1.2.0)
  meshesData[]: ?favoriteName: string, ?id: string, ?floorIndex: int, ?level: float, ?skirtType: MeshSkirtType, ?skirtLevel: float, ?buildingMaterialId: AttributeId, ?ridges: MeshRidges, ?showLines: bool, ?contourPen: int, ?levelPen: int, ?lineTypeIndex: int, polygonCoordinates: [Coordinate3D], ?polygonArcs: [PolyArc], ?holes: Holes3D, ?sublines: [MeshSubline]
  → elements: ElementIdsOrErrors

### CreateLabels
# Creates Label elements based on the given parameters. (since 1.2.6)
  ?databaseId: DatabaseId
  labelsData[]: ?favoriteName: string, ?id: string, ?parentElementId: ElementId, ?labelClass: LabelClass, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?leaderLine: LabelLeaderLineSettableDetails, ?begCoordinate: Coordinate2D, ?midCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?floorInd: float
  → elements: ElementIdsOrErrors

### CreateTexts
# Creates standalone Text elements based on the given parameters. (since 1.5.0)
  ?databaseId: DatabaseId
  textsData[]: ?favoriteName: string, ?id: string, coordinate: Coordinate3D, ?text: string, ?runs: [TextRunDetails], ?height: float, ?pen: int, ?angle: float, ?justification: Justification, ?style: TextStyleSettableDetails, ?width: float, ?floorIndex: int, ?layerIndex: int
  → elements: ElementIdsOrErrors

### CreateLevelDimensions
# Creates Level Dimension elements (the Level Dimension tool) based on the given parameters. With a parentElementId the dimension is associative: it shows the height of the parent element (Mesh, Slab, Roof ...) at its position and follows the element when it changes. (since 1.7.2)
  levelDimensionsData[]: ?favoriteName: string, ?id: string, position: Coordinate2D, ?parentElementId: ElementId, ?level: float, ?floorIndex: int, ?layerIndex: int, ?pen: int, ?textHeight: float, ?textPen: int, ?dimForm: int, ?needPlus: bool, ?markerSize: float, ?angle: float, ?origin: DimensionOrigin
  → elements: ElementIdsOrErrors

### ModifyLevelDimensions
# Changes existing Level Dimension elements: the position of the marker and the settings CreateLevelDimensions takes (pen, text height and pen, marker type and size, plus sign, angle, origin), with the same keys. Not written: the parent element and the static level (delete and recreate the dimension to change them), the text content and the hide-with-base-element setting. (since 2.0.0)
  levelDimensionsWithDetails[]: elementId: ElementId, ?position: Coordinate2D, ?pen: int, ?textHeight: float, ?textPen: int, ?dimForm: int, ?needPlus: bool, ?markerSize: float, ?angle: float, ?origin: DimensionOrigin
  → executionResults: ExecutionResults

### ModifyWalls
# Modifies Wall elements based on the given parameters. Takes the same wall settings as CreateWalls, applied by the same code, plus geometryType (Straight or Trapezoid), profileType and bottomOffset. Neither command can write a Polygonal outline (it needs an outline polygon, which these commands do not take), connectionPriority or junctionSequence (Archicad ignores writes to them; GetDetailsOfElements reads them), and on Archicad 29 any story visibility other than 'Home story only' and 'All relevant stories'. (since 1.4.0)
  wallsWithDetails[]: elementId: ElementId, ?geometryType: WallModificationGeometryType, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?arcAngle: float, ?height: float, ?thickness: float, ?bottomOffset: float, ?offset: float, ?structureType: WallStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?profileId: AttributeId, ?referenceLineLocation: WallReferenceLineLocation, ?flipped: bool, ?profileType: WallModificationProfileType, ?slantAlpha: float, ?slantBeta: float, ?topOffset: float, ?relativeTopStory: float, ?zoneRel: WallZoneRelation, ?visibility: StoryVisibility, ?isAutoOnStoryVisibility: bool, ?referenceMaterial: OverriddenMaterial, ?oppositeMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?contourPen: int, ?contourPen3D: int, ?contourLineTypeId: AttributeId, ?belowViewLineTypeId: AttributeId, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?useCompositePriority: bool, ?linkToSettings: LinkToSettings, ?inheritEndSurface: bool, ?alignTexture: bool, ?polyCanChange: bool, ?materialsChained: bool, ?logHeight: float
  → executionResults: ExecutionResults

### ModifyBeams
# Modifies Beam elements based on the given parameters. CreateBeams takes the same cut fill pens and cover fill, and the same absolute zCoordinate of the reference line (with an optional floorIndex). Not written: the surfaces of the beam segments, and the cut fill pens before Archicad 27. (since 1.4.0)
  beamsWithDetails[]: elementId: ElementId, ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?zCoordinate: float, ?floorIndex: int, ?level: float, ?offset: float, ?slantAngle: float, ?arcAngle: float, ?verticalCurveHeight: float, ?beamShape: "Straight"|"HorizontallyCurved"|"VerticallyCurved", ?isSlanted: bool, ?isFlipped: bool, ?profileAngle: float, ?anchorPoint: BeamAnchorPoint, ?width: float, ?height: float, ?isWidthAndHeightLinked: bool, ?circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?holes: [BeamHoleModification], ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → executionResults: ExecutionResults

### ModifySlabs
# Modifies Slab elements based on the given parameters. CreateSlabs takes the same surfaces, cut fill pens and floor fill. Not written: the surface of a single edge, and the cut fill pens before Archicad 27. Of the cover fill orientation, Archicad applies only the type to a Slab through the API; a given origin or distortion matrix that did not stick gets a failed execution result, while the other details are applied. (since 1.4.0)
  slabsWithDetails[]: elementId: ElementId, ?zCoordinate: float, ?floorIndex: int, ?thickness: float, ?structureType: SlabStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?referencePlaneLocation: SlabReferencePlaneLocation, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?topMaterial: OverriddenMaterial, ?sideMaterial: OverriddenMaterial, ?bottomMaterial: OverriddenMaterial, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?floorFill: FloorFill
  → executionResults: ExecutionResults

### ModifyColumns
# Modifies Column elements based on the given parameters. CreateColumns takes the same cut fill pens and cover fill. Not written: the surfaces of the column segments, and the cut fill pens before Archicad 27. (since 1.4.0)
  columnsWithDetails[]: elementId: ElementId, ?origin: Coordinate2D, ?zCoordinate: float, ?floorIndex: int, ?height: float, ?bottomOffset: float, ?axisRotationAngle: float, ?coreAnchor: ColumnCoreAnchor, ?isSlanted: bool, ?slantAngle: float, ?slantDirectionAngle: float, ?isFlipped: bool, ?wrapping: bool, ?topOffset: float, ?relativeTopStory: float, ?width: float, ?depth: float, ?isWidthAndHeightLinked: bool, ?circleBased: bool, ?buildingMaterialId: AttributeId, ?profileId: AttributeId, ?veneer: ColumnVeneer, ?cutFillPen: OverriddenPen, ?cutFillBackgroundPen: OverriddenPen, ?coverFill: CoverFill
  → executionResults: ExecutionResults

### ModifyWindows
# Modifies Window elements based on the given parameters. (since 1.4.0)
  windowsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectSectionAttributes: bool
  → executionResults: ExecutionResults

### ModifyDoors
# Modifies Door elements based on the given parameters. (since 1.4.0)
  doorsWithDetails[]: elementId: ElementId, ?width: float, ?height: float, ?sillHeight: float, ?centerOffset: float, ?reflected: bool, ?refSide: bool, ?oSide: bool, ?reveal: bool, ?revealDepthOffset: float, ?displayOption: DisplayOption, ?pen: int, ?lineTypeId: AttributeId, ?cutLineTypeId: AttributeId, ?sectionFillId: AttributeId, ?sectionFillPen: int, ?sectionFillBackgroundPen: int, ?sectionContourPen: int, ?aboveViewLinePen: int, ?aboveViewLineTypeId: AttributeId, ?belowViewLinePen: int, ?belowViewLineTypeId: AttributeId, ?useObjectPens: bool, ?useObjectLineTypes: bool, ?useObjectSectionAttributes: bool
  → executionResults: ExecutionResults

### ModifyOpenings
# Modifies Opening elements: the width, the height and the base point CreateOpenings takes. Needs Archicad 28 or earlier; in Archicad 29 and later every item fails with a message pointing to SetOpeningDetails, which changes the size and the position of an opening there. (since 2.0.0)
  openingsWithDetails[]: elementId: ElementId, ?basePoint: Coordinate3D, ?width: float, ?height: float
  → executionResults: ExecutionResults

### ModifyMorphs
# Modifies Morph elements based on the given parameters. (since 1.4.0)
  morphsWithDetails[]: elementId: ElementId, ?translation: Coordinate3D, ?rotationDegreesZ: float, ?buildingMaterialId: AttributeId, ?body: MorphBody, ?xAxis: Coordinate3D, ?yAxis: Coordinate3D, ?zAxis: Coordinate3D, ?surfaceId: AttributeId, ?castShadow: bool, ?receiveShadow: bool, ?isAutoOnStoryVisibility: bool, ?showContour: StoryVisibility, ?showFill: StoryVisibility, ?linkToSettings: LinkToSettings, ?displayOption: DisplayOption, ?viewDepthLimitation: ViewDepthLimitation, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutLineType: AttributeId, ?cutLinePen: int, ?uncutLineType: AttributeId, ?uncutLinePen: int, ?overheadLineType: AttributeId, ?overheadLinePen: int, ?useCoverFillType: bool, ?outlineContourDisplay: bool, ?coverFillType: AttributeId, ?coverFillPen: int, ?coverFillBGPen: int, ?use3DHatching: bool, ?coverFillOrientation: CoverFillOrientation, ?useDistortedCoverFill: bool, ?textureProjectionType: TextureProjectionType, ?textureProjectionCoords: [Coordinate3D], ?level: float
  → executionResults: ExecutionResults

### ModifyRoofs
# Modifies single-plane and multi-plane Roof elements based on the given parameters. The plan outline, level, thickness and structure apply to both; angle, pivotLine and edgeTrims (the cut of each polygon edge) only to single-plane roofs; levels, eavesOverhang and pivotEdges only to multi-plane roofs. (since 1.4.0)
  roofsWithDetails[]: elementId: ElementId, ?level: float, ?floorIndex: int, ?thickness: float, ?eavesOverhang: float, ?levels: [RoofLevel], ?structureType: RoofStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId, ?polygonOutline: [Coordinate2D], ?polygonArcs: [PolyArc], ?holes: Holes2D, ?angle: float, ?pivotLine: {?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?begin: Coordinate2D, ?end: Coordinate2D}, ?edgeTrims: [{?trimType: "Vertical"|"Perpendicular"|"Horizontal"|"CustomAngle", ?angle: float}], ?pivotEdges: [{?levels: [{?angle: float, ?eavesOverhang: float, ?angleType: "Sloped"|"Gable"}]}]
  → executionResults: ExecutionResults

### ModifyShells
# Modifies the structure (Basic or Composite, building material or composite) of Shell elements based on the given parameters. (since 1.8.0)
  shellsWithDetails[]: elementId: ElementId, ?structureType: ShellStructureType, ?buildingMaterialId: AttributeId, ?compositeId: AttributeId
  → executionResults: ExecutionResults

### ModifyMeshes
# Modifies the attributes of Mesh elements based on the given parameters. (since 1.5.4)
  meshesData[]: elementId: ElementId, meshData: MeshModificationData
  → executionResults: ExecutionResults

### ModifyRailings
# Modifies Railing elements in place: the height of their segments, the bottom offset and the home story. The reference line, the nodes and segments, and the posts, rails and panels stay as they are. Each railing is read back after the change, and a value Archicad did not apply gets a failed execution result. (since 2.0.0)
  railingsWithDetails[]: elementId: ElementId, ?height: float, ?bottomOffset: float, ?floorIndex: int
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
  textsWithDetails[]: elementId: ElementId, ?coordinate: Coordinate3D, ?floorIndex: int, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails, ?width: float
  → executionResults: ExecutionResults

### ModifyLabels
# Modifies Label elements based on the given parameters. (since 1.5.9)
  labelsWithDetails[]: elementId: ElementId, ?text: string, ?runs: [TextRunDetails], ?style: TextStyleSettableDetails, ?symbolStyle: LabelSymbolStyleSettableDetails, ?leaderLine: LabelLeaderLineSettableDetails
  → executionResults: ExecutionResults

### ModifyCurtainWalls
# Modifies Curtain Wall elements in place, keeping their GUID, properties and classifications: the height, the bottom elevation and story, the reference line (with the same number of segments), and the column (primary) and row (secondary) pattern with its cell assignments, in the fields of CreateCurtainWalls. (since 1.8.0)
  curtainWallsWithDetails[]: elementId: ElementId, ?coordinates: [Coordinate2D], ?zCoordinate: float, ?floorIndex: int, ?height: float, ?primaryPattern: CurtainWallPattern, ?secondaryPattern: CurtainWallPattern, ?cells: [CurtainWallPatternCell]
  → executionResults: ExecutionResults

### ModifyCurtainWallFrames
# EXPERIMENTAL. Modifies single Curtain Wall Frames by their GUID: the frame contour (a1, a2, b1, b2), the frame class and the frame type. ACAPI_Element_Change does not take a frame on its own, so the change is written through the memo of the owner curtain wall, and read back to check that Archicad applied it. (since 2.0.0)
  framesWithDetails[]: frameId: ElementId, ?frameContour: {?a1: float, ?a2: float, ?b1: float, ?b2: float}, ?classIndex: int, ?type: "Invisible"|"GDL"|"InvisibleConnectedTurning"|"InvisibleConnectedStill"
  → executionResults: ExecutionResults

### ModifyStairs
# Modifies Stair elements in place, keeping their baseline and position: the flight width, total height, number of steps, riser height and going with their locks, the finish and structure visibility, the extra top and bottom treads, the walking line position and offset, the step numbering, the walking direction, the uniform finish, monolith and draining settings, and for the flights and the landings the tread and riser settings (presence, thickness, offset, nosing, riser cross section and position) and the structure of each side (presence, type, underside shape and thickness). CreateStairs accepts the same settings. Only the given settings are changed. Archicad solves the stair again within its baseline, so it may adjust the step values; read them back with GetDetailsOfElements. Not written by this command: the baseline with its landings and winders, the top link, the floor plan display (symbol and marker layout), the headroom and the stair rules; the subelements (treads, risers, structures) take the per-part settings above and cannot be written one by one through the API. (since 2.0.0)
  stairsWithDetails[]: elementId: ElementId, ?flightWidth: float, ?totalHeight: float, ?stepNum: int, ?riserHeight: float, ?treadDepth: float, ?treadDepthLocked: bool, ?totalHeightLocked: bool, ?finishVisible: bool, ?extraTopTread: bool, ?extraBottomTread: bool, ?walkingLinePosition: "Left"|"Right"|"Center"|"Auto", ?walkingLineOffset: float, ?numberingType: "Treads"|"Risers", ?inputDirection: "Upward"|"Inverse", ?uniformFinish: bool, ?uniformMonolithAttributes: bool, ?uniformDrainings: bool, ?structureVisibility: bool, ?treads: [{role: "Run"|"Landing", ?visible: bool, ?thickness: float, ?offset: float, ?nosingType: "ByValue"|"BySlanting", ?nosingValue: float, ?nosingSlant: float}], ?risers: [{role: "Run"|"Landing", ?visible: bool, ?thickness: float, ?offset: float, ?crossSection: "Simple"|"Slanted", ?angle: float, ?position: "OnTread"|"BehindTread"}], ?structures: [{role: "Run"|"Landing", side: "LeftSide"|"RightSide"|"UnderSide", ?visible: bool, ?structureType: "Side"|"Monolith"|"BeamSupport"|"CantileveredSupport", ?bottomType: "Stepped"|"Flat"|"Smooth", ?thickness: float, ?horizontalThickness: float}]
  → executionResults: ExecutionResults

### ChangeTextContent
# Replaces a range of the content of Text elements and text Labels, keeping the styles of the runs and the autotexts in the rest of the content. (since 1.8.0)
  contentChanges: [TextContentChange]
  → executionResults: ExecutionResults

### ModifyZones
# Modifies Zone elements: name, number, category, zone stamp, height, base offset, top link, floor thickness, contour line and cover fill - the same settings as CreateZones, applied by the same helpers. Only the given fields are changed. The polygon of a manual zone cannot be changed here (the change takes no polygon memo), nor the reference point of an automatic one (SetDetailsOfElements moves it). (since 1.8.0)
  zonesWithDetails[]: elementId: ElementId, ?name: string, ?numberStr: string, ?categoryAttributeId: AttributeId, ?stampPosition: Coordinate2D, ?stampAngle: float, ?fixedStampAngle: bool, ?height: float, ?bottomOffset: float, ?topOffset: float, ?relativeTopStory: float, ?floorThickness: float, ?contourLine: ZoneContourLine, ?coverFill: ZoneCoverFill
  → executionResults: ExecutionResults

### MeasureTexts
# Measures texts before placing them: the length of every line for a given font, style and height, on paper in millimetres or in the model at the current drawing scale, and the font's capital size factor. Creates nothing. (since 1.7.3)
  texts[]: text: string, ?fontIndex: int, ?fontName: string, height: float, ?bold: bool, ?italic: bool, ?underline: bool, ?slant: float, ?inModelUnits: bool
  → measurements: [TextMeasurement | ErrorItem]

### GetElementPreviewImage
# Returns the preview image of the given element. (since 1.2.7)
  elementId: ElementId, ?imageType: "2D"|"Section"|"3D", ?format: "png"|"jpg", ?width: int, ?height: int
  → previewImage: string

### GetRoomImage
# Returns the room image of the given zone. (since 1.2.7)
  zoneId: ElementId, ?format: "png"|"jpg", ?width: int, ?height: int, ?offset: float, ?scale: float, ?backgroundColor: ColorRGB
  → roomImage: string

### GetModelExtent
# Returns the 3D extent (xMin, yMin, zMin, xMax, yMax, zMax) of the current database, the region Archicad's Fit in Window would show. (since 2.0.0)
  → BoundingBox3D

### SetElementNotificationClient
# Sets up a new notification client to receive element events. (since 1.2.8)
  ?host: string, port: int, ?notifyOnNewElement: bool, ?notifyOnModificationOfAnElement: bool, ?elementTypesToObserve: [ElementType], ?notifyOnReservationChanges: bool, ?notifyOnSelectionChange: bool, ?notifyOnWindowChange: bool, ?notifyOnProjectEvents: bool, ?notifyOnAttributeReplacement: bool, ?notifyOnToolChange: bool, ?notifyOnViewEvents: bool, ?notifyOnLockableReservationChanges: bool, ?notifyOnToolDefaultChanges: bool, ?notifyOnAttributeChanges: bool, ?notifyOnClassificationChanges: bool, ?notifyOnPropertyDefinitionChanges: bool, ?notifyOnMarqueeChange: bool, ?notifyOn3DSettingsChanges: bool
  → ExecutionResult

### RemoveElementNotificationClient
# Removes an element notification client. (since 1.2.8)
  ?host: string, port: int
  → ExecutionResult

### RegularizePolygons
# Regularizes polygons with Archicad's own polygon regularization, before they are used to create slabs, zones or fills: removes duplicate points, fixes the orientation, resolves self-intersections and touching holes. Each input polygon gives 0, 1 or more valid polygons in the format of CreateSlabs, optionally with the input vertex and edge each result vertex and edge came from. Changes nothing in the project. (since 1.7.3)
  polygons: [PolygonRegularizationData], ?withAncestry: bool
  → results: [RegularizedPolygons | ErrorItem]

### RegularizePolylines
# Regularizes polylines with Archicad's own polyline regularization: removes repeated consecutive points. The result is in the format of CreatePolylines and may be empty, optionally with the input point and segment each result point and segment came from. Changes nothing in the project. (since 1.7.3)
  polylines: [PolylineRegularizationData], ?withAncestry: bool
  → results: [RegularizedPolyline | ErrorItem]

### GetSplineMaxDistances
# Measures how far the given 2D coordinates are from a segment of a Spline element, between two of its fit points, with its own Bezier handles: returns the largest distance, for example to check how well a polyline follows the spline. The output is aligned with the input array. Changes nothing in the project. (since 2.0.0)
  splines[]: elementId: ElementId, segmentIndex: int, coordinates: [Coordinate2D]
  → results: [{maxDistance: float} | ErrorItem]

## Element grouping Commands

### CreateGroups
# Creates groups of the passed elements (since 1.4.0)
  elementGroups: [ElementGroupParameters]
  → groupGuids: [GroupIdOrError]

### UngroupElements
# Ungroups the given groups one level, like Edit > Grouping > Ungroup: each group is dissolved, the elements and subgroups it directly contains stay. A group nested in another group is reported as failed; ungroup the containing group first. Returns an execution result per group. (since 1.7.3)
  groups: [GroupIdArrayItem]
  → executionResults: ExecutionResults

### GetGroupsOfElements
# Gets the identifier of the group that directly contains each given element. Returns an error for elements that are not part of any group. (since 1.5.6)
  elements: Elements
  → groupGuids: [GroupIdOrError]

### GetElementsOfGroups
# Gets the elements directly contained by each given group. (since 1.5.6)
  groups: [GroupIdArrayItem]
  → elementsOfGroups: [ElementsWrapperOrError]

### GetMainGroups
# Gets the top level group of each given group. A group that is not nested in another group is its own top level group. (since 1.8.0)
  groups: [GroupIdArrayItem]
  → mainGroups: [GroupIdOrError]

### GetAllElementsOfGroups
# Gets all the elements of each given group, including the elements of its nested groups. (since 1.8.0)
  groups: [GroupIdArrayItem]
  → elementsOfGroups: [ElementsWrapperOrError]

### GetAutoGroupMode
# Gets the current state of the Auto Group mode. (since 1.8.0)
  → autoGroup: bool

### GetElementSetData
# Gets the elements and the custom data of each given element set. Element sets are created by add-ons to link elements together; the custom data is returned as Base64 encoded bytes. (since 1.8.0)
  elementSets[]: elementSetId: {guid: Guid}
  → elementSets: [{elements: Elements, userData: {dataVersion: int, platformSign: int, data: string}} | ErrorItem]

### GetUserDataOfGroups
# Gets the user data an add-on attached to each given group: its version, platform sign, flags and bytes (base64 encoded), and, when its version is 1 (the layout SetUserDataOfGroups writes), its key-value pairs. Returns an error for groups that have no user data. (since 1.7.3)
  groups: [GroupIdArrayItem]
  → userDataOfGroups: [{userData: {dataVersion: int, platformSign: int, flags: int, data: string, ?pairs: UserDataPairs}} | ErrorItem]

### SetUserDataOfGroups
# Stores string values under keys in the user data of groups, for scripts to keep their own state on a group. The given pairs are merged into what each group already holds: a key that exists gets the new value, other keys are left as they are, and the keys listed in keysToDelete are removed. Prefix the keys with the script's name so that scripts do not overwrite each other's data. User data in another layout is left unchanged and reported as an error. One undo step per call. (since 1.8.0)
  groups: [GroupIdArrayItem], ?pairs: UserDataPairs, ?keysToDelete: UserDataKeysToDelete
  → executionResults: ExecutionResults

### GetSuspendGroupsMode
# Gets the current state of the Suspend Groups mode. (since 1.5.6)
  → suspendGroups: bool

### SetSuspendGroupsMode
# Turns the Suspend Groups mode on or off. Suspend groups to perform operations on elements that are part of a group; remember to restore the previous state afterwards. (since 1.5.6)
  suspendGroups: bool
  → executionResult: ExecutionResult

### CreateElementSets
# Creates element sets of the given elements. An element set is a hidden, persistent collection of elements (it is not a group and has no effect on selection or editing). (since 1.8.0)
  elementSets[]: elements: Elements
  → elementSets: [{elementSetId: {guid: Guid}} | ErrorItem]

### DeleteElementSets
# Deletes the given element sets. The elements of a set are not deleted. Only element sets created by the Tapir Add-On can be deleted; sets created by other add-ons are reported as failed. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each element set that a real run would delete gets wouldDelete. (since 1.8.0)
  ?dryRun: DryRun
  elementSets[]: elementSetId: {guid: Guid}
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### GetElementSetsOfElements
# Gets the element sets that contain each given element. Only element sets created by the Tapir Add-On are examined; sets created by other add-ons are not found. (since 1.7.3)
  elements: Elements
  → elementSetsOfElements: [ElementSetsOfElement | ErrorItem]

## Favorites Commands

### GetFavoritesByType
# Returns a list of the names of all favorites with the given element type (since 1.2.2)
  elementType: ElementType
  → FavoritesOrError

### GetAllFavorites
# Returns every Favorite of the project, or only those of the given element type, with its name and element type. Available from Archicad 29. (since 1.7.3)
  ?elementType: ElementType
  → favorites: [FavoriteSummary]

### GetFavoritePreviewImage
# Returns the preview image of the given favorite. (since 1.2.7)
  favorite: string, ?imageType: "2D"|"Section"|"3D", ?format: "png"|"jpg", ?width: int, ?height: int
  → previewImage: string

### GetFavoriteDetails
# Returns the classifications, property values and element category values stored in the given favorites, so they can be audited before elements are placed. Each property value comes with its evaluation status and default-value flag; the value itself is only returned when it has been evaluated. (since 1.8.0)
  favorites: Favorites
  → favoriteDetails: [FavoriteDetails | ErrorItem]

### ApplyFavoritesToElementDefaults
# Apply the given favorites to element defaults. (since 1.1.2)
  favorites: Favorites
  → executionResults: ExecutionResults

### CreateFavoritesFromElements
# Create favorites from the given elements. (since 1.1.2)
  favoritesFromElements: [FavoriteFromElement]
  → executionResults: ExecutionResults

### ImportFavorites
# Import Favorites from a .prefs file or folder into the current project. From Archicad 29 they can also be imported from a folder of Favorite files (xml format, all of them or the given fileNames) or from a legacy .prf file (legacyPRF format), with the conflict policies Error, Skip, OverwriteExisting and RenameNew. In a Teamwork project the Favorites lockable object set must be reserved first (see ReserveLockableObjectSet). (since 1.5.0)
  path: string, ?format: FavoriteImportFormat, ?fileNames: [string], ?targetFolder: [string], ?importFolders: bool, ?conflictPolicy: FavoriteImportConflictPolicy
  → ?firstConflictName: string

### ExportFavorites
# Export the project's Favorites to a .prefs file or folder. From Archicad 29 they can also be exported to a folder of Favorite files (xml format) or to a legacy .prf file (legacyPRF format). With overwrite false an export to a single file refuses to replace an existing file. (since 1.5.0)
  path: string, ?names: [string], ?format: FavoriteExportFormat, ?overwrite: bool
  → ExecutionResult

### ApplyFavoritesToElements
# Apply the given favorites to existing elements. Only settings-type parameters are changed - geometry (position, floor, and dimensions such as a Wall's height) is left untouched, so applying a Favorite never moves the target element. A Window or Door keeps its wall, marker and placement, and takes the Favorite's library part and parameters, size included. For the hierarchical types (Stair, Railing, Curtain Wall) the settings of the sub-elements are not applied, because they are inseparable from the Favorite's own geometry. By default settings, classifications, categories and properties are all applied; each can be opted out of individually. keepFields lists fields of the target (its ID, layer, an opening's width, height and sill height, a Wall's reference line location, height and top link) that are copied back after the Favorite has been applied, so that e.g. only the library part or the wall type changes. With favorite instead of favoritesToApply, one Favorite is read once and applied to the given elements, or to every element of its type that matches the filter. (since 1.5.4)
  ?favoritesToApply: [FavoriteToApply], ?favorite: string, ?elements: Elements, ?filter: ElementTypeFloorLayerFilter, ?applySettings: bool, ?applyClassifications: bool, ?applyCategories: bool, ?applyProperties: bool, ?keepFields: [FavoriteKeepField]
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

### GetFavoriteFolders
# Returns the folder tree of the Favorites palette from its root folder: the name and path of every folder and the names of the Favorites in it. Available from Archicad 29. (since 1.8.0)
  → rootFolder: FavoriteFolderDetails

### ReadFavoritesFile
# Read the Favorites of a .prefs file or folder without importing them, returning the name, element type and folder of each. Nothing in the project changes, so the result can be compared with the project's Favorites before ImportFavorites. (since 2.0.0)
  path: string
  → favorites: [FavoriteFileEntry]

### CreateFavoriteFolder
# Creates a folder in the Favorites palette, in the parent folder given by its path. Returns the new folder. Available from Archicad 29. (since 1.8.0)
  parentPath: [string], name: string
  → folder: FavoriteFolderDetails

### RenameFavoriteFolder
# Renames a folder of the Favorites palette given by its path. The root folder cannot be renamed. Returns the renamed folder. Available from Archicad 29. (since 1.8.0)
  path: [string], newName: string
  → folder: FavoriteFolderDetails

### DeleteFavoriteFolder
# Deletes a folder of the Favorites palette given by its path. Archicad deletes the folder's Favorites and subfolders with it, so a folder that is not empty is deleted only if recursive is true. The root folder cannot be deleted. Returns the deleted folder. Available from Archicad 29. (since 1.8.0)
  path: [string], ?recursive: bool
  → deletedFolder: FavoriteFolderDetails

### GetFavoriteSettings
# Reads the stored settings of the given favorites without applying them or placing an element: the element type, the folder, the library part and GDL parameters, the marker (library part and parameters) of Window and Door favorites, and the sub-elements. A favorite without a marker has no marker field, which is not an error. The other settings of the element (pens, layer, structure, etc.) are not returned. (since 1.7.3)
  favorites: Favorites
  → favoriteSettings: [FavoriteSettings | ErrorItem]

### CreateFavorite
# Creates a Favorite in the given folder from the settings of another Favorite or of the current Opening tool default. conflictPolicy says what happens when the name is taken: fail, skip, overwrite the existing Favorite's settings or create the new one under a free name. Available from Archicad 29. (since 1.8.0)
  name: string, ?folder: [string], source: FavoriteSettingsSource, ?conflictPolicy: FavoriteCreationConflictPolicy
  → name: string, ?folder: [string], outcome: FavoriteCreationOutcome

### ChangeFavorite
# Gives an existing Favorite the settings of another Favorite or of the current Opening tool default. Available from Archicad 29. (since 1.8.0)
  favoriteName: string, source: {?favoriteName: string, ?toolDefault: "Opening"}
  → ExecutionResult

### ApplyFavoriteToToolDefault
# Makes the settings of the given Favorite the settings of its tool, and returns the element type of that tool. Available from Archicad 29. (since 1.8.0)
  favoriteName: string
  → elementType: ElementType

### MoveFavoriteFolder
# Moves a folder of the Favorites palette, with its Favorites and subfolders, into another folder. Folders are given as their path of folder names from the root. Returns the new path of the folder. Available from Archicad 29. (since 1.8.0)
  folder: [string], targetFolder: [string]
  → folder: [string]

### GetFavoriteContents
# Returns the Favorites of a folder of the Favorites palette and of its subfolders (every Favorite when no folder is given), each with its folder path, classifications, element category values and property values, read through the Favorite manager. Available from Archicad 29. (since 2.0.0)
  ?folderPath: [string]
  → favorites: [FavoriteContents | ErrorItem]

### DeleteFavoritesWithManager
# Deletes the given Favorites through the Favorite manager, each found by name, optionally only in the given folder. One execution result for each. Available from Archicad 29. (since 2.0.0)
  favorites: [FavoriteNameAndFolder]
  → executionResults: ExecutionResults

### MoveFavorites
# Moves Favorites given by their names into a folder of the Favorites palette given by its path. Returns an execution result for each Favorite. Available from Archicad 29. (since 1.8.0)
  favorites: Favorites, targetPath: [string]
  → executionResults: ExecutionResults

### GetFavoriteDefaults
# Reads the element default stored in each given Favorite through the Favorite manager, without applying it or placing an element: the element type, the layer, the element ID, the folder, the library part and GDL parameters, the marker of every element type that has one, and the sub-elements with each of their kinds (Curtain Wall frames and panels, Stair treads and risers, Railing posts and rails, markers ...). Available from Archicad 29. (since 2.0.0)
  favorites: Favorites
  → favoriteDefaults: [FavoriteDefaults | ErrorItem]

### SearchFavorites
# Searches project favorites by keyword (matching favorite name or folder) and/or element type. (since 2.0.0)
  ?query: string, ?elementType: ElementType, ?limit: int
  → favorites: [FavoriteSummary]

## Property Commands

### GetAllProperties
# Returns all user defined and built-in properties. Optionally only the given properties or property types, and without the availability lists. (since 1.0.8)
  ?properties: PropertyIds, ?propertyTypes: [PropertyDefinitionType], ?includeAvailability: bool
  → properties: [PropertyDetails], ?propertyGroups: [PropertyGroupDetails]

### SearchProperties
# Searches properties by name or group substring with optional filtering by property type, value type, and collection type. (since 2.0.0)
  ?query: string, ?propertyGroup: string, ?propertyType: "StaticBuiltIn"|"DynamicBuiltIn"|"Custom", ?valueType: "Integer"|"Real"|"String"|"Boolean"|"Guid", ?collectionType: "Single"|"List"|"SingleChoiceEnumeration"|"MultipleChoiceEnumeration", ?includeEnumValues: bool, ?includeAvailability: bool, ?limit: int
  → properties: [PropertyDetails]

### GetPropertyValuesOfElements
# Returns the property values of the elements for the given property. It works for subelements of hierarchal elements also. With includeAvailability it also tells whether each property is available for the element. (since 1.0.7)
  elements: Elements, properties: PropertyIds, ?includeAvailability: bool, ?useSIUnits: bool
  → propertyValuesForElements: PropertyValuesOrErrorArray

### SetPropertyValuesOfElements
# Sets the property values of elements. It works for subelements of hierarchal elements also. With valueStatus an element's value can also be reset to the default value of the property (Default) or made undefined (UserUndefined, from 1.8.1). With dryRun true nothing is changed and no undo step is created: the response has dryRun set to true, and each item that passes the checks made before writing gets wouldChange, with the element's value now (oldValue) and the value a real run would write (newValue), both as GetPropertyValuesOfElements gives them. (since 1.0.7)
  elementPropertyValues: ElementPropertyValues, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: ChangeExecutionResults

### GetComponentsOfElements
# Returns the components of the elements: the building material skins of composite walls, slabs, roofs and shells, and the parts of complex profile walls, beams and columns. The components have their own property values (building material, thickness, area, volume and the properties of the building material); read them with GetPropertyValuesOfElementComponents. (since 2.0.0)
  elements: Elements
  → componentsOfElements: ElementComponentsOrErrorArray

### GetPropertyDefinitionsOfElementComponents
# Returns the property definitions available on the given element components, optionally filtered to user defined or built-in ones. (since 2.0.0)
  elementComponents: ElementComponents, ?filter: "UserDefined"|"BuiltIn"|"All"
  → propertyDefinitionsOfElementComponents: [{propertyDefinitions: [{propertyId: PropertyId, propertyName: string, propertyType: PropertyDefinitionType}]} | ErrorItem]

### GetPropertyValuesOfElementComponents
# Returns the property values of the given element components for the given properties, in the shape of GetPropertyValuesOfElements. Use GetComponentsOfElements to list the components of an element. (since 2.0.0)
  elementComponents: ElementComponents, properties: PropertyIds
  → propertyValuesForElementComponents: PropertyValuesOrErrorArray

### SetPropertyValuesOfElementDefaults
# Sets the property values of the tool defaults (the settings new elements get) of element types, so every element placed afterwards gets them, without saving and applying a favorite. (since 2.0.0)
  elementDefaultPropertyValues[]: elementType: ElementType, propertyId: PropertyId, propertyValue: PropertyValue
  → executionResults: ExecutionResults

### GetPropertyValuesOfAttributes
# Returns the property values of the attributes for the given property. With includeStatus it also returns whether each property is available, editable and visible for the attribute (from 1.7.3). (since 1.1.8)
  attributeIds: AttributeIds, properties: PropertyIds, ?includeStatus: bool
  → propertyValuesForAttributes: [AttributePropertyValuesResult | ErrorItem]

### SetPropertyValuesOfAttributes
# Sets the property values of attributes. (since 1.1.8)
  attributePropertyValues: AttributePropertyValues
  → executionResults: ExecutionResults

### SetBuiltInPropertyValuesOfAttributes
# Sets built-in property values of attributes, writing the values of each attribute together. Custom properties are refused; set them with SetPropertyValuesOfAttributes. Returns one execution result per value. (since 1.8.0)
  attributes: [AttributeBuiltInPropertyValues]
  → executionResults: ExecutionResults

### SetPropertyValueOfAttributes
# Sets one property value on several attributes (for example Building Materials) in one undo step. If the property is not available for any of the given attributes, no attribute is changed. (since 2.0.0)
  propertyId: PropertyId, propertyValue: PropertyValue, attributeIds: AttributeIds
  → ExecutionResult

### GetPropertyDefinitionsOfAttributes
# Returns the property definitions of the given attributes (for example Building Materials): the user defined, the fundamental built-in, or all of them. (since 1.7.3)
  attributeIds: AttributeIds, ?filter: AttributePropertyDefinitionFilter
  → propertyDefinitionsOfAttributes: [AttributePropertyIds | ErrorItem]

### GetPropertiesOfToolDefaults
# Returns the property definitions of the tool defaults (the settings new elements get) of the given element types, filtered by kind (all by default), and optionally the value of each property in the tool default. (since 1.8.0)
  elementTypes: [ElementType], ?filter: ToolDefaultPropertyFilter, ?includeValues: bool
  → propertiesOfToolDefaults: [ToolDefaultProperties | ErrorItem]

### AddPropertyToAttributes
# Makes an existing custom property available for the given attributes (for example Building Materials), in one undo step. Available in Archicad 25, 26 and 27 only. (since 1.7.3)
  propertyId: PropertyId, attributeIds: AttributeIds
  → ExecutionResult

### RemovePropertyFromAttributes
# Makes a custom property unavailable for the given attributes (for example Building Materials), in one undo step. Available in Archicad 25, 26 and 27 only. With dryRun true nothing is changed and no undo step is created: the response has dryRun set to true, and wouldDelete when the property and every attribute exist. (since 1.7.3)
  propertyId: PropertyId, attributeIds: AttributeIds, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, success: bool, ?error: Error, ?wouldDelete: true

### CreatePropertyGroups
# Creates Property Groups based on the given parameters. (since 1.0.7)
  propertyGroups: [PropertyGroupArrayItem]
  → propertyGroupIds: [PropertyGroupIdArrayItem]

### DeletePropertyGroups
# Deletes the given Custom Property Groups. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each property group that exists gets wouldDelete. (since 1.1.1)
  propertyGroupIds: [PropertyGroupIdArrayItem], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### CreatePropertyDefinitions
# Creates Custom Property Definitions based on the given parameters. (since 1.1.1)
  propertyDefinitions: [PropertyDefinitionArrayItem]
  → propertyIds: PropertyIdOrErrorArray

### DeletePropertyDefinitions
# Deletes the given Custom Property Definitions. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each property that exists gets wouldDelete. (since 1.1.1)
  propertyIds: [PropertyIdArrayItem], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

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

### GetPropertyValuesOfElementDefaults
# Returns the values of the given properties in the current tool default of an element type, which new elements of that type get. It reads the native tool default of the generic variation of the type, not a Favorite that is not applied. A property that is not available for the tool default is reported as an error. (since 2.0.0)
  elementType: ElementType, properties: PropertyIds
  → propertyValues: PropertyValues

### ModifyPropertyValueOfElements
# Sets one property value on all the given elements in a single step. If the property is not available for any of the elements, none of them is changed. (since 1.8.0)
  elements: Elements, propertyId: PropertyId, propertyValue: PropertyValue
  → ExecutionResult

### GetPropertyExpressionReferences
# Returns the strings that refer to the given properties in property expressions. (since 2.0.0)
  propertyIds: PropertyIds
  → references: [{reference: string} | ErrorItem]

### CheckPropertyValues
# Checks whether the given values are acceptable for the given property definitions, without changing anything. (since 2.0.0)
  propertyValues[]: propertyId: PropertyId, propertyValue: PropertyValue
  → results: [{isValid: bool, ?error: Error} | ErrorItem]

### GetPropertyEditability
# Tells whether the values of the given properties can be modified, and whether the properties are visible, for the given elements. Also tells whether they can be modified in the tool defaults of element types (from Archicad 26) and in the default values of the property definitions themselves. Unknown elements, element types and properties are reported as errors, not as locked properties. (since 2.0.0)
  properties: PropertyIds, ?elements: Elements, ?elementTypes: [ElementType], ?propertyDefinitionDefaults: bool
  → ?editabilityOfElements: [{propertyEditabilities: [{editable: bool, visible: bool} | ErrorItem]} | ErrorItem], ?editabilityOfElementTypeDefaults: [{propertyEditabilities: [{editable: bool} | ErrorItem]} | ErrorItem], ?editabilityOfPropertyDefinitionDefaults: [{editable: bool} | ErrorItem]

### GetPropertyAvailabilityOfDefaults
# Tells whether the given properties are available and whether they are visible in the current tool default of an element type, before creating new elements. It checks the native tool default only, not a Favorite that is not applied. Unknown properties are reported as errors, not as unavailable. Available from Archicad 26. (since 1.8.0)
  elementType: ElementType, properties: PropertyIds
  → propertyAvailabilities: [DefaultPropertyAvailability | ErrorItem]

### MakePropertyAvailableForElements
# Makes a property definition available for all the given elements. Available in Archicad 25, 26 and 27. (since 1.7.3)
  elements: Elements, propertyId: PropertyId
  → ExecutionResult

### MakePropertyUnavailableForElements
# Makes a property definition unavailable for all the given elements. Available in Archicad 25, 26 and 27. (since 1.7.3)
  elements: Elements, propertyId: PropertyId
  → ExecutionResult

## Classification Commands

### GetClassificationsOfElements
# Returns the classification of the given elements in the given classification systems. It works for subelements of hierarchal elements also. (since 1.0.7)
  elements: Elements, classificationSystemIds: ClassificationSystemIds
  → elementClassifications: ElementClassificationsOrErrors

### GetElementsByClassification
# Returns the elements classified with the given classification items, one list per item, so elements can be filtered by classification in a single call. (since 1.8.0)
  classificationItemIds: ClassificationItemIds
  → elementsOfClassificationItems: [ClassificationItemElements | ErrorItem]

### SetClassificationsOfElements
# Sets the classifications of elements. In order to set the classification of an element to unclassified, omit the classificationItemId field. It works for subelements of hierarchal elements also. With dryRun true nothing is changed and no undo step is created: the response has dryRun set to true, and each item that passes the checks made before writing gets wouldChange, with the element's classification in the system now (oldValue) and the one a real run would set (newValue). (since 1.0.7)
  elementClassifications: ElementClassifications, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: ChangeExecutionResults

### GetClassificationsOfAttributes
# Returns the classifications of the given attributes (building materials, composites, surfaces, etc.) in every classification system they are classified in. (since 1.8.0)
  attributeIds: AttributeIds
  → attributeClassifications: [AttributeClassifications | ErrorItem]

### SetClassificationsOfAttributes
# Sets the classifications of attributes (building materials, composites, surfaces, etc.). The given item replaces the attribute's current item in the same classification system. In order to set the classification of an attribute to unclassified in a system, omit the classificationItemId field. (since 1.8.0)
  attributeClassifications: [AttributeClassification]
  → executionResults: ExecutionResults

### GetClassificationOfAttributesInSystem
# Returns the classification of the given attributes (for example Building Materials) in the given classification system. classificationItemId is omitted for an unclassified attribute. (since 1.8.0)
  attributeIds: AttributeIds, classificationSystemId: ClassificationSystemId
  → attributeClassifications: ClassificationIdsOrErrors

### GetClassificationsOfElementDefaults
# Returns the classification of the tool defaults (the settings new elements get) of the given element types in the given classification systems. (since 1.7.3)
  elementTypes: [ElementType], classificationSystemIds: ClassificationSystemIds
  → elementDefaultClassifications: ElementClassificationsOrErrors

### SetClassificationsOfElementDefaults
# Sets the classifications of the tool defaults (the settings new elements get) of the given element types. In order to set a default to unclassified, omit the classificationItemId field. (since 1.7.3)
  elementDefaultClassifications: [ElementDefaultClassification]
  → executionResults: ExecutionResults

### GetClassificationsOfToolDefaults
# Returns every classification of the tool defaults (the settings new elements get) of the given element types, in all classification systems at once. Unlike GetClassificationsOfElementDefaults it needs no list of classification systems; systems in which a default is unclassified are left out. (since 1.8.0)
  elementTypes: [ElementType]
  → classificationsOfToolDefaults: [ToolDefaultClassifications | ErrorItem]

### GetAllClassificationSystems
# Returns the classification systems of the project with their guid, name, description, source, version and date. Same output as the official GetAllClassificationSystems command, so scripts can rely on Tapir commands only. (since 1.8.0)
  → classificationSystems: [ClassificationSystemSummary]

### CreateClassificationSystems
# Creates Classification Systems including Classification Items based on the given parameters. (since 1.5.0)
  classificationSystemsWithItems: ClassificationSystemsWithItems
  → executionResults: ExecutionResults, classificationSystemIds: ClassificationSystemIdsOrErrors

### CreateClassificationItems
# Creates Classification Items in the given Classification Systems based on the given parameters. (since 1.5.0)
  newClassificationItems: NewClassificationItems
  → executionResults: ExecutionResults, classificationItemIds: ClassificationItemIdsOrErrors

### DeleteClassificationSystems
# Deletes the given Classification Systems. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each classification system that exists gets wouldDelete. (since 1.5.2)
  classificationSystemIds: ClassificationSystemIds, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### DeleteClassificationItems
# Deletes the given Classification Items. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and each classification item that exists gets wouldDelete. (since 1.5.2)
  classificationItemIds: ClassificationItemIds, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### UpdateClassificationSystems
# Updates the name, description, source, version and/or date of existing Classification Systems, keeping their guid. (since 1.6.0)
  classificationSystems: [ClassificationSystemUpdate]
  → executionResults: ExecutionResults

### UpdateClassificationItems
# Updates the id (code), name and/or description of existing Classification Items, keeping their guid and so the elements classified with them. Items cannot be moved to another parent. (since 1.6.0)
  classificationItems: [ClassificationItemUpdate]
  → executionResults: ExecutionResults

### GetClassificationItemParents
# Returns the parent item and the classification system of the given Classification Items; a top level item has no parent. The output is aligned with the input array of items. (since 1.8.0)
  classificationItemIds: ClassificationItemIds
  → classificationItemParents: [ClassificationItemParent | ErrorItem]

### ImportClassificationsXml
# Imports a Classification Manager XML export, with the given policies for systems and items that already exist. Returns the systems and items it created and removed. (since 1.6.0)
  xml: string, systemConflictPolicy: ClassificationSystemConflictPolicy, itemConflictPolicy: ClassificationItemConflictPolicy
  → executionResult: ExecutionResult, created: [GuidId], removed: [GuidId]

### GetClassificationItemVisibility
# Tells whether the given classification items are visible (offered) for the given elements, element tool defaults and attributes, such as building materials. Non-existing targets and classification items are reported as errors. Visibility does not tell whether the target is classified with the item, and an item can be visible even if its parent item is not. (since 1.8.0)
  targets: [{elementId: ElementId} | {elementType: ElementType} | {attributeId: AttributeId}], classificationItemIds: ClassificationItemIds
  → classificationItemVisibilities: [ClassificationItemVisibilities | ErrorItem]

## Attribute Commands

### GetAttributesByType
# Returns the details of every attribute of the given type, including the path of the attribute folder holding it (Archicad 26 and newer). From Archicad 30 an attribute that Archicad keeps a creation record of also carries creationInfo: how (method), from where (source), by whom and when it was created. (since 1.1.3)
  attributeType: AttributeType
  → AttributeHeadersOrError

### GetAttributeIndexes
# Reports for each given attribute type how many attributes there are, the first valid and the highest index in use, and the free indexes between them (for example those of deleted attributes). Available from Archicad 27. (since 2.0.0)
  attributeTypes: [AttributeType]
  → {attributeIndexes: [{attributeType: AttributeType, count: int, ?firstIndex: int, ?lastIndex: int, freeIndexes: [int]} | ErrorItem]} | ErrorItem

### GetAttributesFromProject
# Reads the attributes of the given types from another project or template file without opening it, for example to compare them with the attributes of the open project. Nothing is imported into the open project. The names are the legacy 8-bit names, so non-ASCII characters may not come through. Archicad does not read Layer, Surface, BuildingMaterial and MEPSystem attributes from a file that is not open: these types get an error item instead of an empty list. Available from Archicad 27. (since 1.7.3)
  projectFilePath: string, attributeTypes: [AttributeType]
  → ProjectAttributes | ErrorItem

### DeleteAttributes
# Deletes the given attributes. Returns an execution result for each input item. With dryRun true nothing is deleted: the response has dryRun set to true, and each attribute that passes the checks made before deleting (valid attribute type, attribute exists) gets wouldDelete. (since 1.5.4)
  ?dryRun: DryRun
  attributesToDelete[]: attributeType: AttributeType, attributeId: AttributeIdArrayItem
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### ImportAttributesFromProject
# Imports Line, Fill, ZoneCategory, PenTable, OperationProfile, Composite, Profile and LayerCombination attributes from another project or template file into the open project, with their complete definition (symbol and percent fills included), like Append or Overwrite by name in Archicad's Attribute Manager. The lines and fills a composite or profile uses are matched by name; its building materials and surfaces, and the layers of a layer combination, keep their index only with referencesByIndex, since Archicad does not read these types from a closed file. An attribute with a reference that cannot be mapped is not imported. A new attribute gets a new guid: Archicad does not hand out the guids stored in the source file. An attribute whose name already exists is skipped, or overwritten in place with overwriteExisting. dryRun reports what would happen without changing anything. The names are the legacy 8-bit names of the source file. Available from Archicad 27. (since 2.0.0)
  projectFilePath: string, attributeTypes: [AttributeType], ?attributeNames: [string], ?overwriteExisting: bool, ?dryRun: bool, ?referencesByIndex: bool
  → {attributesByType: [{attributeType: AttributeType, attributes: [{name: string, sourceIndex: int, result: "created"|"overwritten"|"skipped"|"failed", ?attributeId: AttributeId, ?references: [{attributeType: "Line"|"Fill"|"BuildingMaterial"|"Surface"|"Layer", sourceIndex: int, ?sourceName: string, mappedBy: "name"|"index"|"none", ?attributeId: AttributeId}], ?error: Error}]} | ErrorItem]} | ErrorItem

### GetUsedAttributes
# Gets how many attributes of each type are in use (layers, lines, fills, composites, surfaces, ...), as Archicad reports them for the usedAttributes JSON query: the counts in usedAttributes, the report as text in raw. Available from Archicad 27. (since 1.8.0)
  → ?usedAttributes: object, raw: string

### ConsolidateLines
# Runs the Line Consolidation menu command of Archicad on the current window, as the menu does, and reports whether it ran together with what Archicad answered. Available from Archicad 27. (since 1.8.0)
  → executionResult: ExecutionResult, ?result: string

### ConsolidateFills
# Runs the Fill Consolidation menu command of Archicad on the current window, as the menu does, and reports whether it ran together with what Archicad answered. Available from Archicad 27. (since 1.8.0)
  → executionResult: ExecutionResult, ?result: string

### CreateAttributeFolders
# Creates attribute folders, each given by attribute type and path (the folder names from the root folder down). Missing parent folders are created too; a folder that already exists is kept and reported as success. Available from Archicad 26. (since 1.7.3)
  attributeFolders: AttributeFolders
  → executionResults: ExecutionResults

### DeleteAttributeFolders
# Deletes attribute folders, each given by attribute type and path, together with all the subfolders and deletable attributes they contain (a folder holding an attribute that cannot be deleted is kept). The root folder cannot be deleted. With dryRun true nothing is deleted: the response has dryRun set to true, and each folder that exists and is not the root folder gets wouldDelete. Available from Archicad 26. (since 1.7.3)
  attributeFolders: AttributeFolders, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### RenameAttributeFolders
# Renames attribute folders, each given by attribute type and path, to the given new names. The root folder cannot be renamed. Available from Archicad 26. (since 1.7.3)
  attributeFolders: [AttributeFolderRename]
  → executionResults: ExecutionResults

### MoveAttributesAndFolders
# Moves attributes and attribute folders (with their contents) into the target folder, which must be of the same attribute type; an empty target path is the root folder. Returns one execution result per attribute and per folder; an attribute or folder that is already directly in the target folder counts as moved. Available from Archicad 26. (since 1.7.3)
  ?attributeIds: AttributeIds, ?attributeFolders: AttributeFolders, targetFolder: AttributeFolder
  → attributeExecutionResults: ExecutionResults, folderExecutionResults: ExecutionResults

### ReindexLayers
# Moves layers to new indices. Archicad cannot renumber an attribute, so each layer is recreated at its new index (free indices below it are filled with temporary layers, which are deleted again), gets the old layer's state in every layer combination, and then every element of the old layer is moved to it, in the floor plan and in every view and layout database, with the tool defaults on that layer. Only when the old layer is empty everywhere is it deleted, and the new layer gets its name, flags and folder. If an element cannot be moved (it is locked, not reserved in Teamwork, or comes from a hotlinked module), that layer is left as it was. The new layer has a new attribute id; Favorites that use the layer are not updated. Archicad keeps the shown, locked and wireframe state of a layer per open window: the new layer gets the old one's state in the current window and in every layer combination, and starts shown and unlocked in the other open windows. The model elements that sections, elevations, interior elevations and 3D documents show of the layer come back on the new layer when those views are rebuilt (listed as viewsToRebuild). dryRun lists the elements and tool defaults on each layer without changing anything. The whole call is one undo step. Available from Archicad 27. (since 2.0.0)
  ?dryRun: bool, ?maxPlaceholders: int
  layers[]: attributeId: AttributeId, newIndex: int
  → layers: [{attributeId: AttributeId, oldIndex: int, newIndex: int, elements: Elements, ?blockedElements: Elements, toolDefaults: [ElementType], placeholders: int, ?warnings: [string], viewsToRebuild: Databases} | ErrorItem]

### ReindexAttributes
# Moves fills, line types, surfaces, building materials and zone categories to new indices, the way ReindexLayers moves layers. Archicad cannot renumber an attribute, so the attribute is recreated at its new index (free indices below it are filled with temporary attributes, which are deleted again) and every reference to the old index is rewritten to the new one: the fields of the elements in the floor plan and in every view and layout, the parameters of library part based elements, the memo data of roofs, slabs, meshes, morphs, curtain walls, beams, columns, stairs and interior elevations, the tool defaults, the Favorites (with their sub-elements: a curtain wall's frame and panel classes, a stair's structures), the other attributes that refer to it (composites, building materials, surfaces, profiles, MEP systems) and the graphic override rules. Only then is the old attribute deleted. The new attribute has a new attribute id (Archicad does not keep a given id); its name, definition and attribute folder are the old ones. Elements on a hidden or locked layer cannot be changed, so their layers are shown and unlocked for the move and put back afterwards (in the current window, as Archicad keeps these flags per window). If an element still cannot be changed (it is locked itself, or not reserved in Teamwork), everything is put back and that attribute is not moved. Elements from hotlinked modules cannot be changed and are listed; their module file has to be reindexed on its own. Indices typed into GDL scripts are not found, and the frame and panel classes of curtain wall Favorites and of the Curtain Wall tool default keep the old index (Archicad does not take them from ACAPI_Favorite_Change, so such Favorites are left as they are and named in the warnings). dryRun lists every reference without changing anything. The whole call is one undo step. Pens, layers (see ReindexLayers) and the other attribute types are not supported. Available from Archicad 27. (since 2.0.0)
  attributeType: "Fill"|"Line"|"Surface"|"BuildingMaterial"|"ZoneCategory", attributes: [{attributeId: AttributeId, newIndex: int}], ?dryRun: bool, ?maxPlaceholders: int
  → attributes: [{attributeId: AttributeId, oldIndex: int, newIndex: int, placeholders: int, elements: Elements, hotlinkElements: Elements, toolDefaults: [ElementType], favorites: [string], attributes: [{attributeType: string, attributeId: AttributeId, name: string}], overrideRules: [string], ?layersShown: [AttributeIdArrayItem], ?warnings: [string]} | ErrorItem]

### DeleteAndReplaceAttributes
# Deletes fills, line types, surfaces or building materials and replaces each by another attribute of the same type wherever it was used, like Delete and Replace in the Attribute Manager. Every reference is rewritten to the replacement, the way ReindexAttributes rewrites them: the fields of the elements in the floor plan and in every view and layout, the parameters of library part based elements, their memo data, the tool defaults, the Favorites, the other attributes that refer to it (composites, building materials, surfaces, profiles, MEP systems) and the graphic override rules. Elements on a hidden or locked layer are changed too: their layers are shown and unlocked for the change and put back afterwards (in the current window). If an element cannot be changed (it is locked itself, or not reserved in Teamwork), everything is put back and that attribute is not deleted. Elements from hotlinked modules cannot be changed and are listed. Indices typed into GDL scripts are not found, and the frame and panel classes of curtain wall Favorites and of the Curtain Wall tool default keep the deleted attribute (named in the warnings). If a tool default, Favorite, attribute or rule cannot be rewritten to the replacement, it keeps a copy of the deleted attribute with its name and a new attribute id, named in the warnings. The whole call is one undo step. With dryRun true nothing is changed and no undo step is created: the response has dryRun set to true, and each attribute that passes the checks gets wouldDelete and lists every reference a real run would rewrite (elements, tool defaults, Favorites, other attributes, graphic override rules, elements from hotlinked modules). Available from Archicad 27. (since 2.0.0)
  attributeType: "Fill"|"Line"|"Surface"|"BuildingMaterial", ?dryRun: DryRun
  attributes[]: attributeId: AttributeId, replacementAttributeId: AttributeId
  → ?dryRun: DryRunFlag, attributes: [{attributeId: AttributeId, replacementAttributeId: AttributeId, ?wouldDelete: true, elements: Elements, hotlinkElements: Elements, toolDefaults: [ElementType], favorites: [string], attributes: [{attributeType: string, attributeId: AttributeId, name: string}], overrideRules: [string], ?layersShown: [AttributeIdArrayItem], ?warnings: [string]} | ErrorItem]

### GetUnusedAttributes
# Lists the unused layers, fills, surfaces, building materials, composites, profiles, line types, pen tables and zone categories (index, id and name), for the given types or all of them. The Archicad API has no function that tells which attributes are unused (only how many per type), so every reference is collected: the elements of the floor plan and of every view and layout (hotlinked ones too), with their library part parameters and memo data, the tool defaults, the Favorites, the other attributes (composites, building materials, surfaces, profiles, MEP systems) and the graphic override rules, the way ReindexAttributes finds them; for layers the layer of each element, tool default and Favorite; for composites and profiles the walls, slabs, roofs, shells, column and beam segments whose structure type uses them; for pen tables the current pen table and the drawings set to a pen table of their own. An attribute that only an unused attribute refers to counts as used. Indices typed into GDL scripts and the pen tables saved with views are not found. Each type also reports Archicad's own count of the attributes in use (archicadUsedCount, see GetUsedAttributes), so a difference shows. Read only. Available from Archicad 27. (since 2.0.0)
  ?types: ["layer"|"fill"|"surface"|"buildingMaterial"|"composite"|"profile"|"lineType"|"penTable"|"zoneCategory"]
  → attributeTypes: [{type: "layer"|"fill"|"surface"|"buildingMaterial"|"composite"|"profile"|"lineType"|"penTable"|"zoneCategory", unusedAttributes: [{attributeId: AttributeId, index: int, name: string}], attributeCount: int, usedCount: int, ?archicadUsedCount: int}], ?archicadReport: string, ?warnings: [string]

### GetMissingAttributes
# Lists the references of placed elements to layers, fills, surfaces, building materials, composites, profiles, line types, pen tables and zone categories that do not exist in the project, for the given types or all of them, and of the tool defaults, Favorites, graphic override rules, Model View Options combinations and attributes: the structured counterpart of the missing attributes report of Archicad's GDL palette. Every element of the floor plan and of every view and layout (hotlinked ones too) is checked, and so is every tool default and Favorite (with its sub-elements): its layer, its attribute fields and memo data as ReindexAttributes finds them, its composite or profile when its structure type uses one, a drawing's own pen table, and its library part parameters of attribute types; of every graphic override rule the line type, fill and surface it overrides with; of every Model View Options combination the surfaces and line types of the stair and railing schemes and the library part settings' GDL parameters of attribute types; of every composite the building materials of its skins and the line types of its separators, of every building material its cut fill and cut surface, of every surface the fill of its vectorial hatching, of every MEP system its fill, center line type and surfaces, and of every profile the building material, surface or fill of each skin and its contour, cut end and edge line types. The sources input limits the check to elements, tool defaults, Favorites, graphic override rules, Model View Options or attributes. Each item names the source; for an element the element (and the element it is part of, for a curtain wall frame, a column segment, ...) and the story or view it sits on, for a tool default the tool, for a Favorite its name and tool, for a graphic override rule its guid and name, for a Model View Options combination its guid and name (and the library part option set), for an attribute its type, guid and name; then the attribute type, the missing index and the field or GDL parameter that holds it. Index 0 counts as no attribute. Read only. Available from Archicad 27. (since 2.0.0)
  ?attributeTypes: ["layer"|"fill"|"surface"|"buildingMaterial"|"composite"|"profile"|"lineType"|"penTable"|"zoneCategory"], ?sources: ["element"|"toolDefault"|"favorite"|"overrideRule"|"modelViewOption"|"attribute"]
  → missingAttributes: [{source: "element"|"toolDefault"|"favorite"|"overrideRule"|"modelViewOption"|"attribute", ?elementId: ElementId, ?elementType: string, ?overrideRuleId: {guid: Guid}, ?overrideRuleName: string, ?modelViewOptionId: {guid: Guid}, ?modelViewOptionName: string, ?gdlOptionsName: string, ?ownerAttributeType: "composite"|"buildingMaterial"|"surface"|"mepSystem"|"profile", ?ownerAttributeId: AttributeId, ?ownerAttributeName: string, ?favoriteName: string, ?subElementType: string, ?parentElementId: ElementId, ?parentElementType: string, ?databaseId: DatabaseId, ?databaseType: string, ?storyIndex: int, ?storyName: string, ?databaseName: string, ?databaseReference: string, ?inHotlinkedModule: bool, attributeType: "layer"|"fill"|"surface"|"buildingMaterial"|"composite"|"profile"|"lineType"|"penTable"|"zoneCategory", index: int, ?field: string, ?gdlParameter: string}], checkedElementCount: int, ?checkedToolDefaultCount: int, ?checkedFavoriteCount: int, ?checkedOverrideRuleCount: int, ?checkedModelViewOptionCount: int, ?checkedAttributeCount: int, ?warnings: [string]

### CreateLayers
# Creates or overwrites Layer attributes based on the given parameters. (since 1.0.7)
  ?overwriteExisting: bool
  layerDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?isHidden: bool, ?isLocked: bool, ?isWireframe: bool, ?intersectionGroupNr: int
  → attributeIds: AttributeIdsOrErrors

### CreateLayerCombinations
# Creates or overwrites Layer Combination attributes based on the given parameters. (since 1.2.4)
  ?overwriteExisting: bool
  layerCombinationDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?layers: LayersOfLayerCombination
  → attributeIds: AttributeIdsOrErrors

### CreateLines
# Creates or overwrites Line attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  lineDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?scaleWithPlan: bool, ?defineScale: float, ?lineType: string, ?period: float, ?height: float, ?dashItems: [LineDashItem], ?lineItems: [LineSymbolItemData]
  → attributeIds: AttributeIdsOrErrors

### CreateFills
# Creates or overwrites Fill attributes based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  fillDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?subType: string, ?scaleWithPlan: bool, ?useForWalls: bool, ?useForDraft: bool, ?useForCover: bool, ?horizontalSpacing: float, ?verticalSpacing: float, ?angle: float, ?bitPattern: string, ?gradientStart: Coordinate2D, ?gradientEnd: Coordinate2D, ?symbolOffset1: Coordinate2D, ?symbolOffset2: Coordinate2D, ?percent: float, ?texture: Texture, ?lineItems: [FillLineItem], ?symbolLines: [FillSymbolLine], ?symbolArcs: [FillSymbolArc], ?symbolHotspots: [Coordinate2D], ?symbolSolidFills: [FillSymbolSolidFill]
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

### ModifyPens
# Changes the color, width and description of single pens of the Pen Table in effect for the model views (the default) or the layouts, keeping every other pen as it is. Only the given fields of a listed pen are changed. In a Teamwork project the PenTables lockable object set must be reserved first (see ReserveLockableObjectSet). (since 1.8.0)
  pens: [PenData], ?target: "model"|"layout"
  → executionResults: ExecutionResults

### CreateProfiles
# Creates or overwrites Profile attributes as a copy of an existing Profile's geometry, based on the given parameters. (since 1.5.4)
  ?overwriteExisting: bool
  profileDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?sourceAttributeId: AttributeIdArrayItem, ?wallType: bool, ?beamType: bool, ?coluType: bool, ?handrailType: bool, ?otherGDLObjectType: bool, ?skinOverrides: [{skinId: string, ?buildingMaterialId: AttributeIdArrayItem, ?surfaceId: AttributeIdArrayItem, ?fillId: AttributeIdArrayItem, ?contourPen: int, ?contourLineTypeId: AttributeIdArrayItem, ?isCore: bool, ?isFinish: bool, ?visibleCutEndLines: bool, ?cutEndLinePen: int, ?cutEndLineTypeId: AttributeIdArrayItem, ?edgeOverrides: [ProfileEdgeOverride]}], ?moveVertices: [{?region: {?xMin: float, ?xMax: float, ?yMin: float, ?yMax: float}, vector: Coordinate2D, ?skinIds: [string]}], ?newSkins: [ProfileSkinData], ?replaceSkins: bool
  → attributeIds: AttributeIdsOrErrors

### CreateBuildingMaterials
# Creates or overwrites Building Material attributes based on the given parameters. (since 1.0.7)
  ?overwriteExisting: bool
  buildingMaterialDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?id: string, ?manufacturer: string, ?description: string, ?connPriority: int, ?cutFillIndex: int, ?cutFillPen: int, ?cutFillBackgroundPen: int, ?cutSurfaceIndex: int, ?thermalConductivity: float, ?density: float, ?heatCapacity: float, ?embodiedEnergy: float, ?embodiedCarbon: float, ?showUncutLines: bool, ?collisionDetection: bool, ?cutFillOrientation: string
  → attributeIds: AttributeIdsOrErrors

### CreateComposites
# Creates or overwrites Composite attributes based on the given parameters. (since 1.0.7)
  ?overwriteExisting: bool
  compositeDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?useWith: [string], ?skins: [{type: string, buildingMaterialId: AttributeIdArrayItem, framePen: int, thickness: float}], ?separators: [{lineTypeId: AttributeIdArrayItem, linePen: int}]
  → attributeIds: AttributeIdsOrErrors

### CreateSurfaces
# Creates or overwrites Surface attributes based on the given parameters. (since 1.2.2)
  ?overwriteExisting: bool
  surfaceDataArray[]: ?attributeId: AttributeId, ?index: string, name: string, ?materialType: SurfaceType, ?ambientReflection: float, ?diffuseReflection: float, ?specularReflection: float, ?transparency: float, ?shine: float, ?transparencyAttenuation: float, ?emissionAttenuation: float, ?surfaceColor: ColorRGB, ?specularColor: ColorRGB, ?emissionColor: ColorRGB, ?fillId: AttributeIdArrayItem, ?texture: Texture
  → attributeIds: AttributeIdsOrErrors

### GetBuildingMaterialPhysicalProperties
# Retrieves the physical properties of the given Building Materials. (since 1.0.7)
  attributeIds: AttributeIds
  → properties: BuildingMaterialPhysicalPropertiesList

### GetLayerCombinations
# Returns the details of layer combination attributes. (since 1.2.4)
  attributes: AttributeIds
  → layerCombinations: [LayerCombinationAttributeOrError]

### GetCurrentLayerCombination
# Returns the layer combination in effect in the current window. No layer combination is returned when the current state of the layers matches none. (since 1.7.3)
  → ?layerCombinationId: AttributeId, ?name: string

### ActivateLayerCombination
# Activates the given layer combination in the current window, like choosing it in the Quick Layers palette. Saved views are not changed. (since 2.0.0)
  attributeId: AttributeId
  → ExecutionResult

### GetLayerOfElementDefaults
# Returns the layer of the tool defaults of the given element types: the layer new elements of that type are placed on. (since 2.0.0)
  elementTypes: [ElementType]
  → layersOfElementDefaults: [{elementType: ElementType, layerId: AttributeId, layerName: string} | ErrorItem]

### SetLayerOfElementDefaults
# Sets the layer of the tool defaults of the given element types, so new elements of that type are placed on it. Only the layer of the defaults is changed. (since 2.0.0)
  layersOfElementDefaults[]: elementType: ElementType, layerId: AttributeId
  → executionResults: ExecutionResults

### RenameAttributes
# Renames attributes of any type (layers, layer combinations, composites, surfaces, ...). Each attribute keeps its index, its id and its settings. A new name that another attribute of the same type already has is refused, and so is renaming the attributes Archicad does not allow to change (the built-in Archicad Layer, the Solid and Empty fills). (since 2.0.0)
  attributes[]: attributeId: AttributeId, newName: string
  → executionResults: ExecutionResults

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

### GetCurrentPenTable
# Returns the current Pen Table (its index, attribute identifier and name) and its number of pens. Pass the returned attributeId to GetPenTables to read the pens. (since 1.7.3)
  → index: int, isPenTableAttribute: bool, ?attributeId: AttributeId, ?name: string, ?penCount: int

### GetPens
# Returns the given pens, or all of them, in effect in the current window: index, color, width and description. It also works when the pens in effect are not a Pen Table attribute. Available from Archicad 27. (since 1.8.0)
  ?indices: [int]
  → pens: [PenTablePen | ErrorItem]

### SetPens
# Changes the color, width and description of the given pens in effect in the current window, the pens GetPens returns, in one undo step. Only the given fields of a listed pen are changed; each pen gets its own execution result. In a Teamwork project the PenTables lockable object set must be reserved first (see ReserveLockableObjectSet). Available from Archicad 27. (since 2.0.0)
  pens: [PenData]
  → executionResults: ExecutionResults

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

### GetFontsByName
# Finds loaded fonts by name through Archicad's font search and returns their index (as Text and Label fields reference fonts in fontIndex) and name, or an error for a name no loaded font has. (since 1.7.3)
  fontNames: [string]
  → fonts: [FontDetails | ErrorItem]

### GetGraphicOverrideRules
# Gets all graphic override rules of the project, with their rule group, criterion and style. With includeCriterion the criterion also comes as structured conditions, which CreateGraphicOverrideRules and ModifyGraphicOverrideRules take back. Available from Archicad 27. (since 1.7.2)
  ?includeCriterion: bool
  → graphicOverrideRules: [GraphicOverrideRule]

### GetGraphicOverrideRulesByName
# Gets graphic override rules by name, with their rule group, criterion and style. The rule group narrows the search; without it the rule is searched in every rule group. With includeCriterion the criterion also comes as structured conditions. Available from Archicad 27. (since 1.7.3)
  graphicOverrideRules: [GraphicOverrideRuleReference], ?includeCriterion: bool
  → graphicOverrideRules: [GraphicOverrideRuleOrError]

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

### ModifyGraphicOverrideCombinations
# Modifies the name and/or the rules of graphic override combinations. Omitted fields are kept. Available from Archicad 27. (since 1.8.0)
  graphicOverrideCombinations[]: graphicOverrideCombinationId: GraphicOverrideCombinationId, ?name: string, ?graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]
  → executionResults: ExecutionResults

### DeleteGraphicOverrideCombinations
# Deletes graphic override combinations. Their rules are kept. Available from Archicad 27. (since 1.7.2)
  graphicOverrideCombinationIds: [GraphicOverrideCombinationIdArrayItem]
  → executionResults: ExecutionResults

### CreateGraphicOverrideRuleGroups
# Creates empty graphic override rule groups. Available from Archicad 27. (since 1.8.0)
  ruleGroupNames: [string]
  → executionResults: ExecutionResults

### GetGraphicOverrideRuleGroups
# Gets all graphic override rule groups of the project with the rules they contain, empty groups included. Available from Archicad 27. (since 1.7.2)
  → graphicOverrideRuleGroups: [{name: string, graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]}]

### SetGraphicOverrideRuleOrder
# Sets the order of the rules in graphic override rule groups, found by name. The listed rules come first, in the given order; the other rules of the group keep their order after them. Available from Archicad 27. (since 1.8.0)
  graphicOverrideRuleGroups[]: name: string, graphicOverrideRuleIds: [GraphicOverrideRuleIdArrayItem]
  → executionResults: ExecutionResults

### RenameGraphicOverrideRuleGroups
# Renames graphic override rule groups, found by name. Their rules are kept. Available from Archicad 27. (since 1.7.3)
  ruleGroups: [GraphicOverrideRuleGroupRename]
  → executionResults: ExecutionResults

### DeleteGraphicOverrideRuleGroups
# Deletes graphic override rule groups, found by name. A group that still contains rules is kept unless its rules are moved to another group or deleted with it. Available from Archicad 27. (since 1.7.2)
  ruleGroupNames: [string], ?moveRulesToGroup: string, ?deleteRules: bool
  → executionResults: ExecutionResults

### SetGraphicOverrideRuleGroupOrder
# Sets the order of the graphic override rule groups, found by name. The groups not listed keep their order and follow the listed ones. Available from Archicad 27. (since 1.8.0)
  ruleGroupNames: [string]
  → ExecutionResult

### MoveGraphicOverrideRules
# Moves graphic override rules to another rule group, or to another place in their own group. Available from Archicad 27. (since 1.7.3)
  graphicOverrideRules: [GraphicOverrideRuleMove]
  → executionResults: ExecutionResults

### GetUserDataOfAttributes
# Reads the key-value pairs stored on attributes by SetUserDataOfAttributes. An attribute without user data returns no pairs; one holding user data in another layout returns an error. (since 1.8.0)
  attributeIds: AttributeIds
  → userDataOfAttributes: [AttributeUserData | ErrorItem]

### SetUserDataOfAttributes
# Stores string values under keys in the user data of attributes, for scripts to keep their own state on an attribute. The given pairs are merged into what each attribute already holds: a key that exists gets the new value, other keys are left as they are, and the keys listed in keysToDelete are removed. Prefix the keys with the script's name so that scripts do not overwrite each other's data. User data in another layout is left unchanged and reported as an error. Archicad does not record this change as an undo step, so Undo does not revert it. (since 1.8.0)
  attributeIds: AttributeIds, ?pairs: UserDataPairs, ?keysToDelete: UserDataKeysToDelete
  → executionResults: ExecutionResults

### DeleteUserDataOfAttributes
# Removes the user data of attributes, every key at once. Archicad does not record this change as an undo step, so Undo does not revert it. With dryRun true nothing is removed: the response has dryRun set to true, and each attribute that exists gets wouldDelete. (since 1.8.0)
  attributeIds: AttributeIds, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

## IFC Commands

### IFCFileOperation
# Executes an IFC file operation: opens or merges an IFC file, or saves the project as an IFC file. A save can name the export translator to use, a merge the story the IFC file's first storey is placed on. With overwrite false a save refuses to replace an existing file. (since 1.2.6)
  method: "save"|"merge"|"open", ifcFilePath: string, ?overwrite: bool, ?fileType: "ifc"|"ifcxml"|"ifczip"|"ifcxmlzip", ?translatorName: string, ?elementsToExport: IFCElementsToExport, ?storyIndex: int
  → ExecutionResult

### GetIFCExportTranslators
# Lists the IFC export translators of the project in the order of Archicad's translator list. preview marks the first one, which the Archicad API documents as the preview translator; no API identifies the preview translator otherwise, and in some projects the IFC Translators dialog shows another one as preview. Pass one of the names to IFCFileOperation as translatorName. (since 1.6.0)
  → translators: [IFCExportTranslator]

### GetElementsByIFCIds
# Retrieves the elements by the given IFC identifiers. Accepts IFC GlobalIds in every Archicad version. (since 1.5.1)
  ifcIds: [string]
  → elementsByIFCIds: ElementsByIFCIds

### GetIFCIdsOfElements
# Retrieves the IFC identifiers of the given elements. Before Archicad 28 it also returns their IFC GlobalIds. (since 1.5.1)
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

### GetIFCAttributesOfElements
# Retrieves the IFC attributes (Name, Description, ObjectType, Tag, PredefinedType, LongName, ...) of the given elements, subelements included: the name, the IFC value type and the value of each attribute. On Archicad 25, 26 and 27 storedOnly returns only the attributes stored on the elements. (since 1.7.3)
  elements: Elements, ?storedOnly: bool
  → elementIFCAttributes: ElementIFCAttributesOrErrors

### SetIFCAttributesOfElements
# Sets the values of IFC attributes (Name, Description, ObjectType, Tag, ...) of elements. The attribute must be one GetIFCAttributesOfElements returns for the element; its IFC value type is kept. Available only in Archicad 25, 26 and 27 for now. (since 1.7.3)
  elementIFCAttributeValues: [ElementIFCAttributeValue]
  → executionResults: ExecutionResults

### SetIFCPropertiesOfElements
# Sets local IFC properties on elements by creating or modifying single value (IfcPropertySingleValue) properties in the given property sets. Available only in Archicad 25, 26 and 27 for now. (since 1.7.0)
  elementIFCPropertyValues: [ElementIFCPropertyValue]
  → executionResults: ExecutionResults

### GetIFCClassificationReferencesOfElements
# Retrieves the IFC classification references of the given elements, subelements included: identification, name, location, description and sort (from Archicad 29), the name of the IfcRelAssociatesClassification (from Archicad 28), the referenced classification (name, source, edition, edition date, description and location) and whether the reference comes from the preview translator or is stored locally. On Archicad 25, 26 and 27 the source is not given and storedOnly returns only the references stored on the elements. (since 1.8.0)
  elements: Elements, ?storedOnly: bool
  → elementIFCClassificationReferences: ElementIFCClassificationReferencesOrErrors

### SetIFCClassificationReferencesOfElements
# Stores IFC classification references (identification, name, location and the referenced classification with its name, edition, edition date, description and location) on elements. Available only in Archicad 25, 26 and 27 for now. (since 1.8.0)
  elementIFCClassificationReferences: [ElementIFCClassificationReferenceUpdate]
  → executionResults: ExecutionResults

### RemoveIFCClassificationReferencesOfElements
# Removes IFC classification references stored on elements, given by the name of their classification and optionally their identification; without identification every stored reference of that classification is removed. Available only in Archicad 25, 26 and 27 for now. With dryRun true nothing is removed and no undo step is created: the response has dryRun set to true, and each element that has a matching stored reference gets wouldDelete. (since 1.8.0)
  elementIFCClassificationReferences: [ElementIFCClassificationReferenceRemoval], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### RemoveIFCPropertiesOfElements
# Removes local IFC properties, given by property set and property name, from elements. Available only in Archicad 25, 26 and 27 for now. With dryRun true nothing is removed and no undo step is created: the response has dryRun set to true, and each element that has the local IFC property gets wouldDelete. (since 1.7.3)
  elementIFCProperties: [ElementIFCPropertyRemoval], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### GetIFCSpatialStructure
# Returns the IfcProject, IfcSite and IfcBuilding objects of the project's IFC model (hash value, IFC type and GlobalId), and for the given elements the index of the story they are assigned to in the IFC model. Available from Archicad 28. (since 2.0.0)
  ?elements: Elements
  → ?project: IFCObject, ?site: IFCObject, ?building: IFCObject, ?elements: [IFCSpatialStructureOfElement | ErrorItem]

### GetIFCAssignments
# Returns the IFC assignments of the project: the root IFC groups, and for each object the objects assigned to it (children) and the objects it is assigned to (parents). Each object is given by its hash value, its element where it belongs to one, its IFC type and its GlobalId. Available from Archicad 28. (since 2.0.0)
  → rootGroups: [IFCObject], childObjects: [IFCObjectWithChildren], parentObjects: [IFCObjectWithParents]

## Library Commands

### GetLibraries
# Gets the list of loaded libraries. From Archicad 28 a library package also gets its package information (ID, versions, minimum Archicad version and dependencies). (since 1.0.7)
  → libraries: [Library]

### ReloadLibraries
# Executes the reload libraries command. (since 1.0.7)
  → ExecutionResult

### AddFilesToEmbeddedLibrary
# Adds the given files into the embedded library. With the overwriteExisting flag an embedded library item already existing on an outputPath is replaced (Archicad 27 or newer). (since 1.2.2)
  files: LibraryFileAdditions, ?overwriteExisting: bool
  → executionResults: ExecutionResults

### DeleteEmbeddedLibraryItems
# Deletes the given items from the embedded library. The path of an item is the same relative path that AddFilesToEmbeddedLibrary takes as outputPath. Available from Archicad 27. (since 1.6.0)
  embeddedLibraryItems: [EmbeddedLibraryItem]
  → executionResults: ExecutionResults

### CreateLibraryParts
# Creates GDL library parts in the embedded library from their scripts (master, 2D, 3D, parameter, interface, properties) and parameter definitions, under the given parent subtype. The new parts are placeable right away, e.g. with CreateObjects. With the overwriteExisting flag an embedded library item already existing on the path of a new part is replaced (Archicad 27 or newer). (since 1.8.0)
  libraryParts: [LibraryPartData], ?overwriteExisting: bool
  → libraryParts: [LibraryPartCreationDetails | ErrorItem]

### CreateFolderInEmbeddedLibrary
# Creates a folder, with any missing parent folders, inside the embedded library. The folderPath is relative to the embedded library, like the outputPath of AddFilesToEmbeddedLibrary. (since 1.7.3)
  folderPath: string
  → ExecutionResult

### CopyFilesIntoEmbeddedLibrary
# Copies the given files, keeping their names, into a folder of the embedded library with one library operation. The target folder is created when it is missing. With overwriteIfExists an item of the same name in that folder is replaced. (since 1.7.3)
  files: [EmbeddedLibraryFile], ?targetFolder: string, ?overwriteIfExists: bool
  → ExecutionResult

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
  → libraryParts: [AvailableLibraryPart], skippedCount: int, ?skippedSample: [SkippedLibraryPart]

### GetLibraryPartSections
# Lists the sections of library parts given by index: their four-character type code, sub-identifier, size and whether they are text (scripts, comments) or binary (previews). (since 2.0.0)
  libraryParts: [LibraryPartIndexAndPassword]
  → libraryParts: [LibraryPartSections | ErrorItem]

### GetLibraryPartSection
# Reads the text of a text section (a script or the comment) of a library part given by index, without opening it in the GDL editor. Takes the password of a protected library part. (since 2.0.0)
  index: int, sectionType: string, ?subIdent: int, ?password: string
  → content: string

### GetLibrariesOfLibParts
# Gets the library of each given library part (by file name or guid): display name, location, embedded/built-in/package/local/missing flags and the Library Manager tree path. Available from Archicad 29. (since 2.0.0)
  libraryParts: [LibraryPartNameOrGuid]
  → libraries: [LibraryOfLibraryPart]

### GetLibraryPartTypeDetails
# Returns the type details of the given library parts (ACAPI_LibraryPart_GetDetails): full unique ID and its direct parent's, type, the detail flags of objects, lamps, labels and zones, the frame and orientation settings of doors and windows, and the element type and variation of the tool that places the library part. For their path, library, GUID, license and scripts see GetLibraryPartDetails. (since 2.0.0)
  libraryParts: [LibraryPartIdentifier]
  → libraryParts: [{index: int, name: string, fileName: string, unId: string, parentUnId: string, typeId: LibraryPartType, isPlaceable: bool, isTemplate: bool, ?objectDetails: LibraryPartObjectDetails, ?doorWindowDetails: LibraryPartDoorWindowDetails, ?creatorElementType: ElementType, ?creatorVariation: string} | ErrorItem]

### IsLibraryPartSubtypeOf
# Checks for each of the given library parts whether the given ancestor is anywhere up its subtype hierarchy (e.g. whether a part is a kind of furniture), independent of its name. A library part is not a subtype of itself. With matchAncestorByMainId any revision of the ancestor matches. (since 2.0.0)
  libraryParts: [LibraryPartIdentifier], ancestor: LibraryPartIdentifier, ?matchAncestorByMainId: bool
  → ancestorUnId: string, results: [{unId: string, isSubtypeOf: bool} | ErrorItem]

### GetGDLParametersOfLibraryParts
# Gets the default GDL parameters (name, display name, type, array dimensions, value, flags) of the given library parts by name, read from the library part without placing it or changing any defaults. The output is in the format of GetGDLParametersOfElements, without isLocked and possibleValues, which need a placed element. To read a part by its file name, as SetLibraryPartParameters writes it, use GetLibraryPartParameterValues. (since 2.0.0)
  libraryParts[]: libraryPartName: string
  → gdlParametersOfLibraryParts: [{?libPart: LibPartDetails, parameters: [{name: string, displayName: string, index: int, type: string, ?dimension1: int, ?dimension2: int, ?value: any, ?valueDescription: string, ?itemDescriptions: [string], flags: ["Hidden"|"HiddenFromScript"|"Disabled"|"Child"|"Unique"|"Fixed"|"BoldName"|"Open"]}]} | ErrorItem]

### GetMissingLibPartNames
# Gets the library part name of the given placed Object, Lamp, Window or Door elements, even if the library containing the part is not loaded. Use it to find the parts of elements that are shown as dots because their library part is missing. (since 2.0.0)
  elements: Elements
  → libPartNames: [MissingLibraryPartName | ErrorItem]

### GetUnusedLibraryParts
# Lists the loaded library parts that no element of the project is placed from. Read only. The Archicad API does not tell which library parts are used, so every element of the floor plan and of every view and layout is checked: objects, lamps, doors, windows, skylights, zone stamps, symbol labels, drawing titles, curtain wall parts, and the markers of doors, windows, skylights, sections, elevations, details and worksheets. A library part used only in another way (called as a macro, linked as a property object, as an interior elevation marker, in stairs and railings, in the tool defaults or in Favorites) is listed as unused. Library parts that cannot be placed (e.g. macros) are only listed with includeNotPlaceable. (since 2.0.0)
  ?filterByTypeId: LibraryPartType, ?includeNotPlaceable: bool
  → unusedLibraryParts: [UnusedLibraryPart], usedLibraryPartCount: int, scannedElementCount: int, complete: bool, warnings: [string]

### FindLibraryParts
# Finds loaded library parts with the Library Manager: all of them, GDL objects, images or text files, optionally only those whose name contains a text. Returns the name, path and index of each. Available from Archicad 28. (since 2.0.0)
  ?kind: LibraryPartKind, ?nameContains: string, ?firstOnly: bool
  → libraryParts: [FoundLibraryPart]

### GetLibraryPartDetails
# Gets the details of loaded library parts, by name or index: path, library tree path, containing library, and for GDL objects the GUID, subtype, license, UI default flag, which scripts and pictures they have, and optionally the interface and migration scripts. Can also tell whether each one is in the subtype of another library part. Available from Archicad 28. (since 2.0.0)
  libraryParts: [LibraryPartNameOrIndex], ?subTypeOf: string, ?includeScripts: bool
  → libraryParts: [LibraryPartDetails | ErrorItem]

### ModifyLibraryList
# Adds libraries by path and removes loaded libraries by name or path, in one change of the library list. Returns the result of each addition and removal. Available from Archicad 28. (since 2.0.0)
  ?add: [LibraryLocation], ?remove: [LibraryToRemove]
  → addResults: ExecutionResults, removeResults: ExecutionResults

### GetLibraryPartMetadata
# Returns the description, keywords, author and placeable, password protected and hierarchical pages flags of loaded library parts, given by file name. Use it to search library parts by description or keywords and to tell placeable parts from macros. Available from Archicad 28. (since 2.0.0)
  libraryParts: [LibraryPartName]
  → libraryParts: [LibraryPartMetadataDetails | ErrorItem]

### GetLibraryPartOriginalLocations
# Gets the original location of the given library parts, the file they came from, e.g. before they were embedded into the project. The library parts are given by the index GetAvailableLibraryParts returns. Available from Archicad 27. (since 1.8.0)
  libraryParts: [LibraryPartByIndex]
  → locations: [LibraryPartOriginalLocation | ErrorItem]

### IsUsableGDLString
# Checks whether each of the given strings is usable in GDL, e.g. before writing it into a GDL parameter or script. Returns one boolean for each string. (since 1.8.0)
  strings: [string]
  → results: [bool]

### GetGDLDate
# Gets the date GDL scripts see: year, month, day, hour, minute and second. (since 2.0.0)
  → date: {year: int, month: int, day: int, hour: int, minute: int, second: int}

### SetGDLDate
# Sets the date GDL scripts see: year, month, day, hour, minute and second, as GetGDLDate returns them. Useful to test date-dependent library parts; set the value read with GetGDLDate back to restore it. (since 2.0.0)
  date: {year: int, month: int, day: int, hour: int, minute: int, second: int}
  → ExecutionResult

### CheckLibraries
# Checks the loaded libraries with the Archicad API's library check. Returns the error the API reports, if any. (since 1.8.0)
  → ExecutionResult

### ResetLibraries
# Resets the loaded libraries with the Archicad API's library reset. (since 1.8.0)
  → ExecutionResult

### SetLibraryPartScripts
# Sets and deletes the master, parameter, 2D, 3D, properties, interface and forward and backward migration scripts of loaded library parts. Only the given scripts are changed; an empty script makes the section empty, deleteScripts removes it. A library part that is not editable (e.g. a part of a library package or a read-only library) is refused and left unchanged. Available from Archicad 28. (since 1.7.3)
  libraryParts: [LibraryPartScriptsUpdate]
  → executionResults: ExecutionResults

### SetLibraryPartMetadata
# Sets the author, keywords, license, license version, password and the placeable, UI default, subtype and hierarchical pages flags of loaded library parts. Only the given fields are changed. A library part that is not editable (e.g. a part of a library package or a read-only library) is refused and left unchanged. Available from Archicad 28. (since 1.8.0)
  libraryParts: [LibraryPartMetadataUpdate]
  → executionResults: ExecutionResults

### GetLibraryPartPictures
# Gets the preview picture and the GDL pictures of a loaded library part as base64 encoded PNGs, and from Archicad 29 also their dark user interface variants. Available from Archicad 28. (since 1.8.0)
  name: string
  → ?previewPicture: string, ?darkPreviewPicture: string, gdlPictures: [string], ?darkGdlPictures: [string]

### SetLibraryPartPictures
# Deletes the preview picture, the GDL pictures (and from Archicad 29 their dark variants) or the 2D symbol of a loaded library part, or copies the 2D symbol from another library part. A library part that is not editable is refused and left unchanged. Available from Archicad 28. (since 1.8.0)
  name: string, ?deletePreviewPicture: bool, ?deleteDarkPreviewPicture: bool, ?deleteGdlPictures: bool, ?deleteDarkGdlPictures: bool, ?copy2DSymbolFrom: string, ?delete2DSymbol: bool
  → ExecutionResult

### GetLibraryPartCustomSection
# Gets a custom section of a loaded library part by its section identifier and index: whether it exists, its data version and its content as base64. Available from Archicad 28. (since 1.8.0)
  name: string, sectionId: int, ?index: int
  → exists: bool, ?dataVersion: int, ?data: string

### SetLibraryPartCustomSection
# Creates, replaces or deletes a custom section of a loaded library part. The content is given as base64. A library part that is not editable is refused and left unchanged. Available from Archicad 28. (since 1.8.0)
  name: string, sectionId: int, ?index: int, ?dataVersion: int, ?data: string, ?delete: bool
  → ExecutionResult

### CreateLibraryPart
# Creates a new library part file (.gsm) of the given loaded subtype, inheriting its parameters, and reports whether it is loaded with its index and names. Available from Archicad 28. (since 1.8.0)
  path: string, ancestorSubtype: string
  → isLoaded: bool, ?libraryPart: {guid: string, index: int, documentName: string, fileName: string}

### GetLibraryPartParameterValues
# Returns the parameters of loaded library parts, given by their file name as GetAvailableLibraryParts returns it, with their default values and descriptions, in the format of GetGDLParametersOfElements: the read counterpart of SetLibraryPartParameters. Unlike GetGDLParametersOfLibraryParts, which finds a part by its name and also returns the index, flags and value descriptions of each parameter, it reads through the Library Manager. Available from Archicad 28. (since 2.0.0)
  libraryParts[]: name: string
  → libraryParts: [LibraryPartParameterValues | ErrorItem]

### UpdateLibraryPartSections
# Replaces the text of existing sections (scripts, comment, keywords, copyright) of a loaded library part, found by its name. Each section is read back after the update, and the output has one execution result per section. (since 2.0.0)
  name: string
  sections[]: type: "MasterScript"|"2DScript"|"3DScript"|"ParameterScript"|"UIScript"|"Comment"|"Keywords"|"Copyright", ?subIdent: int, text: string
  → executionResults: ExecutionResults

### GetLibraryPart2DPrimitives
# Gets the lines, arcs and polygons (with their holes, and whether they are fills) of the 2D symbol of a loaded library part, drawn with its default parameters or with the parameters of a placed instance. (since 2.0.0)
  name: string, ?elementId: ElementId, ?gdlContext: int
  → primitives: [{type: "Line"|"Arc"|"Polygon", ?begCoordinate: Coordinate2D, ?endCoordinate: Coordinate2D, ?origin: Coordinate2D, ?radius: float, ?begAngle: float, ?endAngle: float, ?isWhole: bool, ?isFill: bool, ?coordinates: [Coordinate2D], ?holes: [{coordinates: [Coordinate2D]}]}]

### SetLibraryPartPictureImages
# Sets the preview picture and the GDL pictures of a loaded library part from base64 encoded PNGs, and from Archicad 29 also their dark user interface variants. All pictures are set in one step; an invalid picture changes nothing. A library part that is not editable is refused and left unchanged. Available from Archicad 28. (since 2.0.0)
  name: string, ?previewPicture: string, ?gdlPictures: [string], ?darkPreviewPicture: string, ?darkGdlPictures: [string]
  → ExecutionResult

### SetLibraryPartParameters
# Sets the parameter values, and optionally the parameter descriptions, of loaded library parts, in the format of SetGDLParametersOfElements. Only the given parameters are changed; with merge, the changed list is merged into the parameters of the part instead of replacing them. A library part that is not editable, or with an invalid value given, is left unchanged. Available from Archicad 28. (since 2.0.0)
  libraryParts[]: name: string, parameters: [{name: string, ?index1: int, ?index2: int, value: any}], ?descriptions: [string], ?merge: bool
  → executionResults: ExecutionResults

### GetLibraryPartScripts
# Gets the master, parameter, 2D, 3D and properties scripts of loaded library parts, given by name or by an element placed from them, with the unique ID of each part. A script section the part does not have is reported as not present. Password protected parts need their password. Available from Archicad 28. (since 2.0.0)
  libraryParts: [{libraryPartName: string} | {elementId: ElementId}], ?scripts: [LibraryPartReadableScriptType], ?password: string
  → libraryParts: [LibraryPartScriptsDetails | ErrorItem]

### GetLibraryPartFileInfo
# Reads library part files (.gsm) without loading them into the libraries of the project: the unique ID of the part, the unique ID of its subtype and its master, parameter, 2D, 3D and properties scripts. Password protected parts need their password. Available from Archicad 28. (since 2.0.0)
  files: [string], ?scripts: [LibraryPartReadableScriptType], ?password: string
  → files: [LibraryPartFileInfo | ErrorItem]

### CopyLibraryParts
# Copies loaded library parts, given by name or by an element placed from them, under a new file name into a folder, by default the embedded library. The copy gets a new unique ID unless the main GUID is kept. An existing file is never overwritten. The libraries are reloaded once afterwards, so the copies can be found by name. Available from Archicad 28. (since 2.0.0)
  libraryParts: [LibraryPartCopyData]
  → libraryParts: [CopiedLibraryPart | ErrorItem], librariesReloaded: bool

### GetLibraryPartIdentities
# Gets the unique ID (main and revision GUID), the reference GUID and the Teamwork lock status of library parts given by index or file path, and whether they are in a server library. (since 2.0.0)
  libraryParts: [LibraryPartIndexOrPath]
  → identities: [LibraryPartIdentity | ErrorItem]

### CompareLibraryPartUnIds
# Compares two library part unique IDs with Archicad's own comparison and tells whether their main and revision GUIDs are the same. (since 2.0.0)
  unId1: string, unId2: string
  → apiErrorCode: int, sameMainGuid: bool, sameRevisionGuid: bool

### GetLastValidEmbeddedLibraryPartName
# Gets the name and file path of the last valid library part of the embedded library. (since 2.0.0)
  → name: string, path: string

### SearchLibraryParts
# Finds the loaded library parts derived from an ancestor library part (by its unique ID) whose name matches a pattern with * wildcards. Archicad returns at most 50 of them. (since 2.0.0)
  ancestorUnId: string, pattern: string
  → libraryParts: [LibraryPartSearchResult]

### OpenLibraryPartInEditor
# Opens a loaded library part, given by its fileName or documentName as returned by GetAvailableLibraryParts, in Archicad's library part editor. Available from Archicad 27. (since 1.8.0)
  name: string
  → ExecutionResult

### CreateLibraryPartFromElements
# Creates a library part in the embedded library (or in a given local library folder, which is added to the loaded libraries when needed) whose 2D symbol is a copy of the given 2D drawing elements (lines, polylines, arcs, circles, splines, fills, texts and hotspots), under the given parent subtype, with optional master, 2D, 3D and parameter scripts, comment and keywords. A and B are taken from the extent of the symbol. The elements themselves are not changed. (since 2.0.0)
  name: string, elements: [ElementIdArrayItem], ?parentId: string, ?parentName: string, ?folder: string, ?libraryFolder: string, ?overwrite: bool, ?placeable: bool, ?scripts: {?master: string, ?2D: string, ?3D: string, ?parameter: string}, ?comment: string, ?keywords: string
  → name: string, ?fileName: string, unId: string, guid: string, index: int, ?a: float, ?b: float

### InterpretGDLScript3D
# Runs a GDL 3D script, given as text or as the master and 3D scripts of a loaded library part with its default parameters, with the settings of the GDL editor, and returns whether it ran without a GDL error, how many 3D model elements it generated and their bounding box. The API returns no GDL error message or line number. (since 2.0.0)
  ?script: string, ?libraryPartName: string
  → success: bool, ?error: Error, ?elementCount: int, ?boundingBox3D: BoundingBox3D

### GetGDLUserGlobals
# Returns the current GDL global variables the GDL interpreter gets, with their names, types and values. Available from Archicad 28. (since 2.0.0)
  → globals: [{name: string, type: "Integer"|"Length"|"Angle"|"RealNumber"|"LightSwitch"|"RGBColor"|"Intensity"|"LineType"|"Material"|"FillPattern"|"PenColor"|"String"|"Boolean"|"BuildingMaterial"|"Profile", ?dimension1: int, ?dimension2: int, value: any}]

## Teamwork Commands

### TeamworkSend
# Performs a send operation on the currently opened Teamwork project. (since 1.0.7)
  → ExecutionResult

### TeamworkReceive
# Performs a receive operation on the currently opened Teamwork project. (since 1.0.7)
  → ExecutionResult

### GetTeamworkProjectInfo
# Tells whether the opened project is a Teamwork project and whether it is online, and returns its BIMcloud server, project name and the current user (id and name). (since 1.8.0)
  → isTeamwork: bool, isOnline: bool, ?userId: float, ?userName: string, ?serverUrl: string, ?projectName: string

### ReserveElements
# Reserves elements in Teamwork mode. GUIDs that are not elements (navigator items, layouts, databases) cannot be reserved with it: they are returned in notElements and the execution result fails. (since 1.1.4)
  elements: Elements
  → executionResult: ExecutionResult, ?notElements: [ElementIdArrayItem], ?conflicts: [{elementId: ElementId, user: User}]

### ReleaseElements
# Releases elements in Teamwork mode. Fails, naming them, when any of the given GUIDs is not an element; the other elements are released. (since 1.1.4)
  elements: Elements
  → ExecutionResult

### GetReservationStatusOfElements
# Returns the Teamwork reservation status of elements without reserving them: whether each element is free, reserved by the current user or reserved by another user, with the reserving user. New elements stay reserved by the user who created them until they are released. (since 1.7.3)
  elements: Elements
  → reservationStatuses: [ElementReservationStatus | ErrorItem]

### GrantElements
# Hands over the reservation of elements to another Teamwork user, given by user id, without a dialog. Available from Archicad 27. (since 1.7.3)
  elements: Elements, userId: float
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

### GetTeamworkStatus
# Returns whether the opened project is a Teamwork project and is online, the members of the shared project and who has reserved the Hotlink and XRef management. Works in a solo project too, then isShared and isOnline are false. (since 1.7.3)
  → isShared: bool, isOnline: bool, ?users: [TeamworkUser], ?hotlinkCacheManagementOwner: User

### GetTeamworkOwnersOfDatabases
# Returns the Teamwork owner (user id and name) of each given database, e.g. of a layout or a view database. The user id is 0 when nobody owns the database. (since 1.8.0)
  databases: Databases
  → owners: [User | ErrorItem]

### UploadLibrariesToBIMcloud
# Uploads local library folders or container files (.lcf) to a folder of a BIMcloud or Teamwork server, as BIMcloud libraries. Returns a result per library. Available from Archicad 29. (since 1.8.0)
  libraryPaths: [string], serverUrl: string, parentPath: string
  → executionResults: ExecutionResults

### RemoveLibrariesFromBIMcloud
# Removes libraries, given by name, from a folder of a BIMcloud or Teamwork server. Returns a result per library. Available from Archicad 29. (since 1.8.0)
  libraryNames: [string], serverUrl: string, parentPath: string
  → executionResults: ExecutionResults

### GetTeamworkRightsOfObjects
# Returns for each given object, for example an element, whether the current Teamwork user has the right to create objects of its kind and to delete or modify it. (since 2.0.0)
  objectIds: [GuidId]
  → rights: [{canCreate: bool, canDeleteModify: bool} | ErrorItem]

### GetTeamworkAccessRights
# Returns whether the role of the current user has the given Teamwork access rights (API_TWAccessRights names without the API prefix, e.g. LayersCreate), all of them when no names are given. (since 2.0.0)
  ?accessRights: [string]
  → accessRights: [{name: string, hasRight: bool}]

## Navigator Commands

### PublishPublisherSet
# Performs a publish operation on the currently opened project. Only the given publisher set will be published. (since 1.0.7)
  publisherSetName: string, ?outputPath: string, ?selectedNavigatorItemIds: NavigatorItemIds

### GetPublisherSets
# Returns the publisher sets of the project with their saved output: the local or LAN path, the Teamwork file server path, or the Internet host and directory name. (since 2.0.0)
  → publisherSets: [{name: string, rootNavigatorItemId: NavigatorItemId, ?path: string, ?twFileServerPath: string, ?host: string, ?dirName: string}]

### UpdateDrawings
# Performs a drawing update on the given elements. (since 1.1.4)
  elements: Elements
  → ExecutionResult

### GetDrawingContentBoxes
# Returns the full content box of the given Drawing elements, independent of their frames, as ACAPI_Drawing_GetFullDrawingContentBox reports it. Available from Archicad 27. (since 1.7.3)
  elements: Elements
  → contentBoxes: [DrawingContentBox | ErrorItem]

### GetDatabaseIdFromNavigatorItemId
# Gets the ID of the database associated with the supplied navigator item id (since 1.1.4)
  navigatorItemIds: NavigatorItemIds
  → databases: Databases

### GetDatabases
# Lists every database of the given types (sections, elevations, interior elevations, details, worksheets, 3D documents, layouts, master layouts) with its database ID, name and reference ID, without walking the navigator trees. (since 1.7.3)
  ?types: [DatabaseType]
  → databases: [DatabaseDetails]

### CreateDetails
# Creates independent Detail databases. Returns the databaseId and the Project Map navigatorItemId of each new detail. (since 1.4.0)
  detailsData[]: name: string, referenceId: string
  → databases: [CreatedDatabase | ErrorItem]

### CreateWorksheets
# Creates independent Worksheet databases. Returns the databaseId and the Project Map navigatorItemId of each new worksheet. (since 1.4.0)
  worksheetsData[]: name: string, referenceId: string
  → databases: [CreatedDatabase | ErrorItem]

### CreateDetailMarkers
# Places Detail markers with their clip polygon in the current floor plan, section or elevation, each with a new Detail viewpoint, like the Detail tool. GetDetailsOfElements reads them back. (since 2.0.0)
  detailMarkersData[]: clipPolygon: [Coordinate2D], ?polygonArcs: [PolyArc], ?markerCoordinate: Coordinate2D, ?angle: float, ?name: string, ?id: string, ?floorIndex: int
  → elements: ElementIdsOrErrors

### CreateWorksheetMarkers
# Places Worksheet markers with their clip polygon in the current floor plan, section or elevation, each with a new Worksheet viewpoint, like the Worksheet tool. GetDetailsOfElements reads them back. (since 2.0.0)
  worksheetMarkersData[]: clipPolygon: [Coordinate2D], ?polygonArcs: [PolyArc], ?markerCoordinate: Coordinate2D, ?angle: float, ?name: string, ?id: string, ?floorIndex: int
  → elements: ElementIdsOrErrors

### ModifyDetailMarkers
# Changes the name, the reference ID, the clip polygon, the boundary's pen and line type, the marker symbol's angle, always-horizontal setting and pen of Detail and Worksheet markers. Not written: the base point (Archicad places it at the center of the clip polygon's bounding box when the marker is created), the viewpoint the marker refers to, and the marker symbol's other settings, which are parameters of the library part placed as the marker (markerId in GetDetailsOfElements). A value Archicad did not apply gets a failed execution result. (since 2.0.0)
  detailMarkersWithDetails[]: elementId: ElementId, ?name: string, ?id: string, ?clipPolygon: [Coordinate2D], ?polygonArcs: [PolyArc], ?penIndex: int, ?lineTypeIndex: int, ?angle: float, ?isHorizontalMarker: bool, ?markerPenIndex: int
  → executionResults: ExecutionResults

### CreateLayout
# Creates Layouts and their backing master layouts. Archicad inserts a new layout at the first place of its subset, renumbering the sheets after it; previousNavigatorItemId or position 'last' places it after an existing sheet or at the end instead. A custom layout number does not leave the layout out of the numbering; layoutParameters.doNotIncludeInNumbering does. A layout that was created but could not be placed is returned with both its databaseId and the error. (since 1.5.4)
  layoutsData[]: ?masterLayoutName: string, ?masterNavigatorItemId: NavigatorItemId, layoutName: string, ?parentNavigatorItemId: NavigatorItemId, ?previousNavigatorItemId: NavigatorItemId, ?position: LayoutInsertionPosition, ?paperWidth: float, ?paperHeight: float, ?layoutParameters: {?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?displayMasterLayoutBelow: bool}
  → databases: [DatabaseIdArrayItem | ErrorItem | {databaseId: DatabaseId, error: Error}]

### CreateLayoutSubset
# Creates Layout Book subsets. (since 1.5.4)
  subsetsData[]: name: string, ?parentNavigatorItemId: NavigatorItemId, ?ownPrefix: string, ?customNumber: string, ?numberingStyle: "Undefined"|"abc"|"ABC"|"1"|"01"|"001"|"0001"|"noID", ?startAt: int, ?continueNumbering: bool, ?useUpperPrefix: bool, ?includeToIDSequence: bool, ?customNumbering: bool, ?addOwnPrefix: bool
  → navigatorItems: [NavigatorItemIdOrError]

### GetLayoutSubsetSettings
# Gets the settings of existing Layout Book subsets: the same fields CreateLayoutSubset accepts (name, ID prefix, numbering style, ...). (since 1.7.3)
  navigatorItemIds: NavigatorItemIds
  → subsetSettings: [LayoutSubsetSettings | ErrorItem]

### CreateDrawings
# Creates Drawing elements on the specified or active layout from navigator items. (since 1.4.0)
  drawingsData[]: navigatorItemId: NavigatorItemId, ?layoutDatabaseId: DatabaseId, ?name: string, ?nameType: DrawingNameType, position: Coordinate2D, ?scale: float, ?angle: float, ?drawingScale: float, ?modelOffset: Coordinate2D, ?clipPolygon: [Coordinate2D]
  → elements: ElementIdsOrErrors

### ChangeDrawingLink
# Relinks a Drawing to a different source navigator item. Archicad has no in-place relink API, so this recreates the Drawing against the new source and deletes the original - the returned elementId is a NEW guid, not the input one. The Drawing Title marker's own position is not preserved (undocumented Archicad limitation). The new source view is made current before the Drawing is created (Archicad 27 or later), and the window and story that were active when the command started are restored afterwards; the view settings (zoom, layers, scale) shown in that window are not restored. (since 1.5.7) [AC27+]
  drawingsWithNewLinks[]: elementId: ElementId, navigatorItemId: NavigatorItemId, layoutDatabaseId: DatabaseId
  → elements: [ElementIdOrError]

### GetLayoutSettings
# Gets settings of layouts, including their master layout and Layout Info Panel custom data fields. (since 1.5.4)
  layoutDatabaseIds[]: ?databaseId: DatabaseId, ?navigatorItemId: NavigatorItemId
  → layoutSettings: [{?layoutName: string, ?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?displayMasterLayoutBelow: bool, ?masterLayoutDatabaseId: DatabaseId, ?masterNavigatorItemId: NavigatorItemId, ?masterLayoutName: string, ?customData: [LayoutCustomData]}]

### SetLayoutSettings
# Sets settings of layouts, including their master layout and Layout Info Panel custom data fields. In Teamwork the layout settings must be reserved first in Archicad (Layout Book > Reserve Layout Settings); the Archicad API cannot reserve them, and ReserveElements does not. GetTeamworkOwnersOfDatabases shows who holds a layout. (since 1.5.4)
  layoutsData[]: ?layoutDatabaseId: DatabaseId, ?layoutNavigatorItemId: NavigatorItemId, ?layoutName: string, ?horizontalSize: float, ?verticalSize: float, ?leftMargin: float, ?topMargin: float, ?rightMargin: float, ?bottomMargin: float, ?customLayoutNumber: string, ?customLayoutNumbering: bool, ?doNotIncludeInNumbering: bool, ?showMasterBelow: bool, ?masterNavigatorItemId: NavigatorItemId, ?masterLayoutDatabaseId: DatabaseId, ?masterLayoutName: string, ?customData: [LayoutCustomDataToSet]
  → executionResults: ExecutionResults

### GetLayoutCustomScheme
# Gets the Layout Info Panel custom field definitions (name and key) from Book Settings. (since 1.5.4)
  → customScheme: [{customSchemeKey: string, customSchemeName: string}]

### GetDrawingNumberingGridLines
# Gets the lines of the grid of the grid-based drawing numbering of the current layout (start and end point, pen index, line type index), for example to find which grid cell a drawing on the layout sits in. The current window must be a layout (see ChangeWindow), and only a layout that uses grid-based drawing numbering has such a grid. (since 1.8.0)
  → lines: [DrawingNumberingGridLine]

### GetModelViewOptions
# Gets all model view options (since 1.1.4)
  → modelViewOptions: [{name: string}]

### FindModelViewOption
# Finds a model view option combination by id or by name and returns its index, id, name and flags. The index is the one SetViewOptions takes to switch the model view options of a window to the combination. Available from Archicad 27. (since 1.8.0)
  ?modelViewOptionId: ModelViewOptionId, ?name: string
  → index: int, modelViewOptionId: ModelViewOptionId, name: string, flags: int

### GetModelViewOptionDetails
# Gets the settings stored in model view option combinations (Document > Model View > Model View Options), all of them or the ones given by id or by name: the model view options in the fields of GetViewOptions, and the options library parts add to the combination (gdlOptions) with their GDL parameter values. Read-only: the Archicad API has no function to change, rename or create a stored combination; SetViewOptions changes the options of the current window. Available from Archicad 27. (since 2.0.0)
  ?modelViewOptions[]: ?modelViewOptionId: {guid: Guid}, ?name: string
  → modelViewOptionDetails: [{index: int, modelViewOptionId: ModelViewOptionId, name: string, modelViewOptions: object, gdlOptions: [{name: string, guid: {guid: Guid}, ?supersetGuid: {guid: Guid}, parameters: [StoredGDLParameter]}]} | ErrorItem]

### GetViewOptions
# Gets the model view options and on-screen view options of the current plan window, and the index and name of the model view option combination it applies. (since 1.8.0)
  → modelViewOptionIndex: int, modelViewOptionName: string, viewOptions: ViewOptions

### SetViewOptions
# Switches the current plan window to a model view option combination by index, and/or changes the given model view options and on-screen view options. With an index, the model view options stored in the combination apply. (since 1.8.0)
  ?modelViewOptionIndex: int, ?viewOptions: ViewOptionsUpdate

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

### GetRenovationFilters
# Gets the renovation filters of the project, and the one the current window uses (Document > Renovation > Renovation Filter). A renovationFilterId has the same shape as the renovationFilterGuid of GetViewSettings and SetViewSettings, so a filter listed here can be set on saved views too. (since 1.8.0)
  → renovationFilters: [RenovationFilterDetails], ?activeRenovationFilterId: GuidId

### SetActiveRenovationFilter
# Sets the renovation filter of the current window (Document > Renovation > Renovation Filter), given by its renovationFilterId from GetRenovationFilters or by its name. Saved views keep their own filter: change that with SetViewSettings. (since 1.8.0)
  ?renovationFilterId: GuidId, ?name: string
  → ExecutionResult

### GetGhostStorySettings
# Gets the Trace & Reference ghost story settings of the floor plan: whether it is on, whether one story, the story above or the one below is shown, which story, its color and the element types shown in it. (since 1.8.0)
  → on: bool, showOne: bool, showAbove: bool, showBelow: bool, storyIndex: int, ghostColor: ColorRGB, filter: [ElementType]

### SetGhostStorySettings
# Sets the Trace & Reference ghost story settings of the floor plan through its ghost record, which is created when the floor plan has none. Every field is optional; the ones left out keep their value, and without a story choice the current reference is kept. (since 1.8.0)
  ?on: bool, ?showOne: bool, ?showAbove: bool, ?showBelow: bool, ?storyIndex: int, ?ghostColor: ColorRGB, ?filter: [ElementType]
  → ExecutionResult

### GetStructureDisplay
# Gets the Partial Structure Display (EntireStructure, CoreOnly, WithoutFinishes or StructureOnly) of the current window, and whether it is the 3D window. This is the setting of the window itself, not the one stored in a saved view (see GetViewSettings). Available from Archicad 27. (since 1.7.3)
  → structureDisplay: PartialStructureDisplay, is3D: bool

### SetStructureDisplay
# Sets the Partial Structure Display (EntireStructure, CoreOnly, WithoutFinishes or StructureOnly) of the current window, e.g. the floor plan, a section or the 3D window. The change cannot be undone. The saved view is not changed (see SetViewSettings for that). Available from Archicad 27. (since 1.7.3)
  structureDisplay: PartialStructureDisplay
  → ExecutionResult

### GetView2DTransformations
# Get zoom and rotation of 2D views (since 1.1.7)
  ?navigatorItemIds: NavigatorItemIds, ?databases: Databases
  → transformations: [ViewTransformationsOrError]

### SetViewRotation
# Set the rotation angle of 2D views via their floor plan database. (since 1.5.4)
  navigatorItemIdsWithRotation[]: navigatorItemId: NavigatorItemId, rotation: float
  → executionResults: ExecutionResults

### CloneProjectMapItemToViewMap
# Clones Project Map viewpoints into a specified View Map folder. (since 1.5.4)
  viewsData[]: navigatorItemId: NavigatorItemId, parentNavigatorItemId: NavigatorItemId
  → navigatorItems: [NavigatorItemIdOrError]

### CreateViewsInViewMap
# Creates independent (non-clone) navigator views in a specified View Map folder, by copying database and settings from source items. (since 1.5.4)
  viewsData[]: navigatorItemId: NavigatorItemId, parentNavigatorItemId: NavigatorItemId, ?name: string
  → navigatorItems: [NavigatorItemIdOrError]

### CreateViewMapFolder
# Creates a new folder in the View Map. (since 1.5.4)
  folderName: string, ?parentNavigatorItemId: NavigatorItemId
  → navigatorItemId: NavigatorItemId

### Set3DCutPlanes
# Sets the 3D cut planes. An empty cutPlanes array switches the 3D cut off. (since 1.3.1)
  ?cutPlanes: [CutPlane]
  → ExecutionResult

### Get3DCutPlanes
# Gets whether the 3D cut planes are on and the cut planes (pa, pb, pc, pd) of the 3D window, in the form accepted by Set3DCutPlanes. (since 1.7.3)
  → isCutPlanes: bool, useCustom: bool, cutPlanes: [CutPlane]

### Get3DStyleDetails
# Gets the settings of 3D styles by name (an empty name or no names means the current 3D style): rendering engine, model type, monochrome and background colors, contours, shadows and hatching. Available from Archicad 27. (since 1.7.3)
  ?names: [string]
  → styles: [Style3DDetails | ErrorItem]

### Create3DStyles
# Creates 3D styles. Each new style starts from the current 3D style and differs from it only in the given fields. Available from Archicad 27. (since 1.7.3)
  styles: [Style3DDetails]
  → executionResults: ExecutionResults

### Change3DStyles
# Changes the given fields of existing 3D styles, identified by name. Available from Archicad 27. (since 1.7.3)
  styles: [Style3DDetails]
  → executionResults: ExecutionResults

### Get3DProjectionSettings
# Gets the 3D projection settings of the 3D window: whether it is perspective or axonometric, the camera and target position, view cone, roll angle, distance and azimuth of a perspective, or the projection type, azimuth and transformation matrix of an axonometry, and the sun position of either (date and time or azimuth and altitude). (since 1.7.2)
  → isPersp: bool, ?cameraElementId: ElementId, ?activeCameraSetElementId: ElementId, ?perspective: PerspectiveProjectionParameters, ?axonometric: {projectionType: AxonometryProjectionType, azimuth: float, transformationMatrix: [float], sun: ProjectionSunSettings}

### Set3DProjectionSettings
# Sets a perspective or an axonometric projection for the 3D window. Every perspective parameter but sun is required: read a known good set with Get3DProjectionSettings and pass it back, with the values to change replaced. An axonometry changes only the values given: the projection type, the azimuth, the transformation matrix and the sun. The sun of either changes only the values given in it and is kept when sun is missing. The 3D window shows the change after a rebuild (RebuildView), e.g. before SaveCurrentWindowAsImage. (since 1.7.2)
  ?perspective: PerspectiveProjectionParameters, ?axonometry: {?projectionType: AxonometryProjectionType, ?azimuth: float, ?transformationMatrix: [float], ?sun: ProjectionSunSettings}
  → ExecutionResult

### GetCameras
# Gets the Camera Sets (camera paths) of the project with their name, whether the set is the active one, its current camera, and its cameras in path order. Each camera has its element id, whether it is active in the path, and its perspective: camera and target position, distance, azimuth, view cone, roll angle, two-point perspective and sun, in the shape Set3DProjectionSettings accepts, so passing a camera's perspective there shows its view in the 3D window. Archicad cameras are always perspective; they have no name of their own. (since 2.0.0)
  → cameraSets: [{cameraSetElementId: ElementId, name: string, isActive: bool, ?activeCameraElementId: ElementId, cameras: [{cameraElementId: ElementId, isActiveInPath: bool, perspective: PerspectiveProjectionParameters}]}]

### Get3DStyles
# Gets the names of the 3D styles of the project and the name of the current one, which the 3D window uses. (since 2.0.0)
  → styleNames: [string], currentStyleName: string

### SetCurrent3DStyle
# Meant to make the given 3D style, one of the names Get3DStyles returns, the current one. Not available yet: it checks the name, then refuses, because Archicad's API function for it crashes Archicad. (since 2.0.0)
  styleName: string
  → ExecutionResult

### StoreViewSettings
# Stores the current view settings (action Store) and puts them back later (action Restore), for example before and after a script that changes the view. The two must be called in pairs and cannot be stacked. Restoring may rebuild the view. (since 2.0.0)
  action: "Store"|"Restore"
  → ExecutionResult

### ShowElementsIn3D
# Opens the 3D window on the given elements, as Show Selection in 3D does: they become the selection and only they are shown. Without elements it shows every element, as Show All in 3D does. (since 2.0.0)
  ?elements: Elements
  → ExecutionResult

### GetDocumentFrom3DDefaults
# Gets the defaults a newly created 3D Document starts with: name, reference ID, vectorial hatching and sun shadows, transparency, connection to the model, surfaces, boundary contours and the uniform cut, uncut, shadow and hidden edge attributes. (since 1.8.0)
  → name: string, refId: string, vect3DHatching: bool, vectSunShadow: bool, mustBeTransparent: bool, ?intPlanConn: Document3DPlanConnection, materialFrom3D: bool, contureOff: bool, cMater: int, ?boundaryDisplay: Document3DBoundaryDisplay, boundaryPen: int, boundaryLineType: int, attributeOptions: Document3DAttributeOptions

### SetDocumentFrom3DDefaults
# Sets the defaults a newly created 3D Document starts with. Only the given fields are changed; existing 3D Documents are not affected. The fields are the ones returned by GetDocumentFrom3DDefaults. (since 1.8.0)
  ?name: string, ?refId: string, ?vect3DHatching: bool, ?vectSunShadow: bool, ?mustBeTransparent: bool, ?intPlanConn: Document3DPlanConnection, ?materialFrom3D: bool, ?contureOff: bool, ?cMater: int, ?boundaryDisplay: Document3DBoundaryDisplay, ?boundaryPen: int, ?boundaryLineType: int, ?attributeOptions: Document3DAttributeOptions
  → ExecutionResult

### Get3DWindowSettings
# Gets the 3D window settings: the pixel size of the 3D window and the zoom (scale and displacement) of its projection. (since 1.7.3)
  → hSize: int, vSize: int, zoomScaleX: float, zoomScaleY: float, zoomDispX: float, zoomDispY: float

### Set3DWindowSettings
# Changes the pixel size of the 3D window and/or the zoom (scale and displacement) of its projection; the values not given are kept. Returns the settings read back after the change. Archicad may need a rebuild of the 3D window (RebuildView) before it shows the change, e.g. before SaveCurrentWindowAsImage. (since 1.7.3)
  ?hSize: int, ?vSize: int, ?zoomScaleX: float, ?zoomScaleY: float, ?zoomDispX: float, ?zoomDispY: float
  → hSize: int, vSize: int, zoomScaleX: float, zoomScaleY: float, zoomDispX: float, zoomDispY: float

### Get3DDocumentSettings
# Gets the settings of a 3D Document, given by its navigator item: the element and story filter, the 3D cut, the projection, the window and zoom, the uniform cut and uncut surface attributes, the source and the boundary contours, with the field names of API_DocumentFrom3DType. (since 2.0.0)
  navigatorItemId: NavigatorItemId
  → settings: {?filterAndCutSettings: {?firstStory3D: int, ?lastStory3D: int, ?allStories: bool, ?trimToStoryRange: bool, ?filterMode: "FilterByRules"|"FilterBySelection"|"FilterByMarqueeAndRules", ?elemTypeFilter: [{elementType: ElementType, show: bool}]}, ?cutSetting: {?isCutPlanes: bool, ?useCustom: bool, ?customPen: int, ?customMater: AttributeIdArrayItem}, ?cutaway3D: bool, ?projectionSetting: {?isPersp: bool, ?camGuid: ElementIdArrayItem, ?actCamSet: ElementIdArrayItem, ?persp: {?pos: Coordinate2D, ?target: Coordinate2D, ?isTwoPointPersp: bool, ?cameraZ: float, ?targetZ: float, ?distance: float, ?azimuth: float, ?viewCone: float, ?rollAngle: float}, ?axono: {?tranmat: [float]}}, ?floorPlanRotationOrigo: Coordinate2D, ?window3DInfo: {?setWindowSize: bool, ?hSize: int, ?vSize: int, ?setZoom: bool, ?zoomScaleX: float, ?zoomScaleY: float, ?zoomDispX: float, ?zoomDispY: float}, ?hiddenLineType: AttributeIdArrayItem, ?hiddenLineLen: int, ?effects3D: int, ?drawRect: {?left: float, ?top: float, ?right: float, ?bottom: float}, ?attributeOptions: {?shouldUseUniformCutAttributes: bool, ?uniformLineType: int, ?uniformFillPen: int, ?uniformFillBkgPen: int, ?shouldUseUncutSurfaceFill: bool, ?fillCutSurfacesWith: int, ?uncutSurfaceFillType: int, ?uncutSurfaceBkgPen: int, ?shouldUseElemPen: bool, ?elemPen: int, ?shadFillPen: int, ?shadFill: AttributeIdArrayItem, ?shadFillBkgPen: int, ?shadContPen: int, ?hiddenEdgeVisibility: int, ?hiddenEdgeLineType: AttributeIdArrayItem, ?hiddenEdgeLinePen: int, ?onCutPlaneVisibility: int}, ?currPlanConn: "Online"|"Offline"|"Drawing", ?intPlanConn: "Online"|"Offline"|"Drawing", ?materialFrom3D: bool, ?docSrc: "DDD"|"FloorPlan", ?skeletonOptions: {?viewSrc: int, ?floorIdx: int, ?cutHeight: float, ?floorOffset: int, ?cutOffset: float}, ?boundaryDisplay: "UncutContours"|"NoContours"|"OverrideContours", ?boundaryPen: int, ?boundaryLineType: AttributeIdArrayItem, ?transparency: bool}

### Set3DDocumentSettings
# Changes the given settings of a 3D Document, given by its navigator item, in the form Get3DDocumentSettings returns; the settings not given are kept. Returns the settings read back after the change. (since 2.0.0)
  navigatorItemId: NavigatorItemId, settings: {?filterAndCutSettings: {?firstStory3D: int, ?lastStory3D: int, ?allStories: bool, ?trimToStoryRange: bool, ?filterMode: "FilterByRules"|"FilterBySelection"|"FilterByMarqueeAndRules", ?elemTypeFilter: [{elementType: ElementType, show: bool}]}, ?cutSetting: {?isCutPlanes: bool, ?useCustom: bool, ?customPen: int, ?customMater: AttributeIdArrayItem}, ?cutaway3D: bool, ?projectionSetting: {?isPersp: bool, ?camGuid: ElementIdArrayItem, ?actCamSet: ElementIdArrayItem, ?persp: {?pos: Coordinate2D, ?target: Coordinate2D, ?isTwoPointPersp: bool, ?cameraZ: float, ?targetZ: float, ?distance: float, ?azimuth: float, ?viewCone: float, ?rollAngle: float}, ?axono: {?tranmat: [float]}}, ?floorPlanRotationOrigo: Coordinate2D, ?window3DInfo: {?setWindowSize: bool, ?hSize: int, ?vSize: int, ?setZoom: bool, ?zoomScaleX: float, ?zoomScaleY: float, ?zoomDispX: float, ?zoomDispY: float}, ?hiddenLineType: AttributeIdArrayItem, ?hiddenLineLen: int, ?effects3D: int, ?drawRect: {?left: float, ?top: float, ?right: float, ?bottom: float}, ?attributeOptions: {?shouldUseUniformCutAttributes: bool, ?uniformLineType: int, ?uniformFillPen: int, ?uniformFillBkgPen: int, ?shouldUseUncutSurfaceFill: bool, ?fillCutSurfacesWith: int, ?uncutSurfaceFillType: int, ?uncutSurfaceBkgPen: int, ?shouldUseElemPen: bool, ?elemPen: int, ?shadFillPen: int, ?shadFill: AttributeIdArrayItem, ?shadFillBkgPen: int, ?shadContPen: int, ?hiddenEdgeVisibility: int, ?hiddenEdgeLineType: AttributeIdArrayItem, ?hiddenEdgeLinePen: int, ?onCutPlaneVisibility: int}, ?currPlanConn: "Online"|"Offline"|"Drawing", ?intPlanConn: "Online"|"Offline"|"Drawing", ?materialFrom3D: bool, ?docSrc: "DDD"|"FloorPlan", ?skeletonOptions: {?viewSrc: int, ?floorIdx: int, ?cutHeight: float, ?floorOffset: int, ?cutOffset: float}, ?boundaryDisplay: "UncutContours"|"NoContours"|"OverrideContours", ?boundaryPen: int, ?boundaryLineType: AttributeIdArrayItem, ?transparency: bool}
  → settings: {?filterAndCutSettings: {?firstStory3D: int, ?lastStory3D: int, ?allStories: bool, ?trimToStoryRange: bool, ?filterMode: "FilterByRules"|"FilterBySelection"|"FilterByMarqueeAndRules", ?elemTypeFilter: [{elementType: ElementType, show: bool}]}, ?cutSetting: {?isCutPlanes: bool, ?useCustom: bool, ?customPen: int, ?customMater: AttributeIdArrayItem}, ?cutaway3D: bool, ?projectionSetting: {?isPersp: bool, ?camGuid: ElementIdArrayItem, ?actCamSet: ElementIdArrayItem, ?persp: {?pos: Coordinate2D, ?target: Coordinate2D, ?isTwoPointPersp: bool, ?cameraZ: float, ?targetZ: float, ?distance: float, ?azimuth: float, ?viewCone: float, ?rollAngle: float}, ?axono: {?tranmat: [float]}}, ?floorPlanRotationOrigo: Coordinate2D, ?window3DInfo: {?setWindowSize: bool, ?hSize: int, ?vSize: int, ?setZoom: bool, ?zoomScaleX: float, ?zoomScaleY: float, ?zoomDispX: float, ?zoomDispY: float}, ?hiddenLineType: AttributeIdArrayItem, ?hiddenLineLen: int, ?effects3D: int, ?drawRect: {?left: float, ?top: float, ?right: float, ?bottom: float}, ?attributeOptions: {?shouldUseUniformCutAttributes: bool, ?uniformLineType: int, ?uniformFillPen: int, ?uniformFillBkgPen: int, ?shouldUseUncutSurfaceFill: bool, ?fillCutSurfacesWith: int, ?uncutSurfaceFillType: int, ?uncutSurfaceBkgPen: int, ?shouldUseElemPen: bool, ?elemPen: int, ?shadFillPen: int, ?shadFill: AttributeIdArrayItem, ?shadFillBkgPen: int, ?shadContPen: int, ?hiddenEdgeVisibility: int, ?hiddenEdgeLineType: AttributeIdArrayItem, ?hiddenEdgeLinePen: int, ?onCutPlaneVisibility: int}, ?currPlanConn: "Online"|"Offline"|"Drawing", ?intPlanConn: "Online"|"Offline"|"Drawing", ?materialFrom3D: bool, ?docSrc: "DDD"|"FloorPlan", ?skeletonOptions: {?viewSrc: int, ?floorIdx: int, ?cutHeight: float, ?floorOffset: int, ?cutOffset: float}, ?boundaryDisplay: "UncutContours"|"NoContours"|"OverrideContours", ?boundaryPen: int, ?boundaryLineType: AttributeIdArrayItem, ?transparency: bool}

### Get3DFilterAndCutSettings
# Gets the 'Filter and Cut Elements in 3D' settings of the 3D window: the stories shown, the filter mode and which element types are shown. Available from Archicad 27. (since 1.8.0)

### Set3DFilterAndCutSettings
# Changes the 'Filter and Cut Elements in 3D' settings of the 3D window; only the given fields and the listed element types change. Returns the settings read back after the change. Available from Archicad 27. (since 1.8.0)
  settings: {?firstStory3D: int, ?lastStory3D: int, ?allStories: bool, ?trimToStoryRange: bool, ?filterMode: "FilterByRules"|"FilterBySelection"|"FilterByMarqueeAndRules", ?elemTypeFilter: [{elementType: ElementType, show: bool}]}, ?rebuild: bool

### GetGridSettings
# Gets the grid and snap grid settings of the database of the current window, and which database that is. Each database has its own grid settings. Available from Archicad 27. (since 1.8.0)

### SetGridSettings
# Changes the grid and snap grid settings of the database of the current window; only the given fields change. Returns the settings read back after the change. Available from Archicad 27. (since 1.8.0)
  settings: {?spaceMainX: float, ?spaceMainY: float, ?nLineMainX: int, ?nLineMainY: int, ?gridSwitch: bool, ?spaceAuxX: float, ?spaceAuxY: float, ?nLineAuxX: int, ?nLineAuxY: int, ?gridMode: int, ?snapOffsX: float, ?snapOffsY: float, ?snapStepX: float, ?snapStepY: float, ?status: int, ?gridAngle: float, ?gridOffsX: float, ?gridOffsY: float, ?gridOffsZ: float, ?backColor: {?red: float, ?green: float, ?blue: float, ?alpha: float}, ?gridColor: {?red: float, ?green: float, ?blue: float, ?alpha: float}}

### FitInWindow
# Zooms to the given elements or fits everything in the window. (since 1.3.1)
  ?elements: Elements
  → ExecutionResult

### ZoomToElements
# Zooms the current window, 2D or 3D, to the given elements: selects them, zooms to the selection and restores the previous selection unless keepSelection is false. Fails when none of the elements could be selected, e.g. all of them are on another story or on a hidden layer. (since 1.8.0)
  elements: Elements, ?keepSelection: bool
  → ExecutionResult

### SetZoom
# Zooms the current 2D window to the given box in model coordinates. (since 1.7.3)
  zoomBox: Zoom
  → ExecutionResult

### ResetZoom
# Steps back in the zoom history of the current window, like Archicad's Zoom Back. (since 1.7.3)
  ?numberOfStepsBack: int
  → ExecutionResult

### CreateSections
# Creates Section elements on the floor plan. A section looks to the left of its start to end direction, with its depth line that far on that side. GetDetailsOfElements reads the geometry of existing sections back. The floor plan must be the active window: creation fails while a Section or Elevation window is active. (since 1.5.0)
  sectionsData[]: startCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?depth: float, ?name: string, ?id: string, ?favoriteName: string, ?floorIndex: int, ?details: SectionElevationSettableDetails
  → elements: ElementIdsOrErrors

### ModifySections
# Changes the name and the reference ID of Section and Elevation elements, which the Project Map and the markers show. GetDetailsOfElements reads those of a Section back as name and idStr. (since 2.0.0)
  sectionsWithDetails[]: elementId: ElementId, ?name: string, ?id: string
  → executionResults: ExecutionResults

### CreateInteriorElevations
# Creates Interior Elevation elements on the floor plan. Every consecutive pair of the given points becomes one segment, each with its own viewpoint - feed it the corner points of a room to get an interior elevation of that room. (since 1.5.8)
  interiorElevationsData: [InteriorElevationData]
  → elements: ElementIdsOrErrors

### CreateElevations
# Creates Elevation elements on the floor plan. The floor plan must be the active window: creation fails while a Section or Elevation window is active. (since 2.0.0)
  elevationsData[]: startCoordinate: Coordinate2D, endCoordinate: Coordinate2D, ?depth: float, ?name: string, ?id: string, ?floorIndex: int, ?details: SectionElevationSettableDetails
  → elements: ElementIdsOrErrors

### GetSectionsAndElevationsDetails
# Gets every configurable setting of the given Section and Elevation elements, with their name and reference ID. (since 2.0.0)
  elements: Elements
  → detailsOfElements: [SectionElevationDetailsOrError]

### SetSectionsAndElevationsDetails
# Sets settings of the given Section and Elevation elements: pens, line types, horizontal and vertical range, model effects, story handles and markers. The name and the reference ID are changed with ModifySections. (since 2.0.0)
  elementsWithDetails[]: elementId: ElementId, details: SectionElevationSettableDetails
  → executionResults: ExecutionResults

### MoveNavigatorItem
# Moves a navigator item to a new parent in the navigator tree, or to a new position within its current parent. Fails when Archicad does not put the item where it was asked to. (since 1.5.4)
  navigatorItemIdToMove: NavigatorItemId, parentNavigatorItemId: NavigatorItemId, ?previousNavigatorItemId: NavigatorItemId
  → ExecutionResult

### RenameNavigatorItem
# Renames a navigator item or changes its ID. Renaming the Layout Book item of a placed Drawing also sets the custom name of the Drawing. newId sets the custom layout number of a layout and the custom ID of any other item. For a Project Map section, elevation, detail or worksheet the name and ID of the element behind the viewpoint are changed, for an interior elevation those of the segment the item stands for; the change is undone when the item does not show the new name. The name and ID of other Project Map items (stories, schedules, ...) cannot be changed. Fails when Archicad refuses the change or does not apply the new name or ID. With customName false the item drops its custom name and follows its Project Map source again. (since 1.5.4)
  navigatorItemId: NavigatorItemId, ?newName: string, ?newId: string, ?customName: bool
  → ExecutionResult

### DeleteNavigatorItems
# Deletes navigator items from the navigator tree: views and folders of the View Map, layouts and master layouts of the Layout Book, and independent worksheets and details of the Project Map. Layout subsets, View Map folders that are not empty, the other Project Map items and marker-linked worksheets and details cannot be deleted; the failed execution result says which case applies. An item that Archicad refuses to delete (in a Teamwork project: it is not reserved or the user has no right to delete it) is reported as a failed execution result. dryRun reports the result of the checks made before deleting (item not found, layout subset, View Map folder that is not empty) without deleting anything. (since 1.5.4)
  navigatorItemIds: NavigatorItemIds, ?dryRun: bool
  → executionResults: ExecutionResults

### GetNavigatorItemTree
# Returns the full navigator item tree for the specified map. With includeChildCount true every item also reports the number of its direct children. (since 1.5.4)
  navigatorMapId: "PublicViewMap"|"ProjectMap"|"LayoutBook"|"PublisherSets", ?publisherSetName: string, ?includeChildCount: bool
  → navigatorItemTree: NavigatorItem

### GetSchedules
# Returns the Interactive Schedules of the Project Map: navigator item id, name, ID and the folders they are in. Archicad's API does not give the rows of a schedule nor export it; to export one, put it in a publisher set with a spreadsheet format in Archicad and run PublishPublisherSet. (since 2.0.0)
  → schedules: [{navigatorItemId: NavigatorItemId, name: string, uiId: string, folderPath: [string]}]

### GetNavigatorParentItems
# Returns the parent of each given navigator item: the folder, subset or layout book item it is in. The root of a map has no parent and gets an error. (since 1.7.3)
  navigatorItemIds: NavigatorItemIds
  → parentItems: [NavigatorParentItem | ErrorItem]

### SetMasterLayoutContext
# Sets which layout's context the master layout of the current window is drawn in: its autotexts then show the values of the given layout. The current window must be a master layout, otherwise an error is returned. It does not assign a master layout to a layout. Available from Archicad 27. (since 1.8.0)
  layoutDatabaseId: DatabaseId
  → ExecutionResult

### GetAddOnViewpointRoots
# Returns the roots of the add-on viewpoints: the Project Map items created through the Archicad API by an add-on, as Archicad lists them to Tapir. Available from Archicad 27. (since 1.8.0)
  → viewpointIds: [{viewpointId: {guid: Guid}}]

### GetAddOnViewpointChildren
# Returns the direct children of an add-on viewpoint root or group. Available from Archicad 27. (since 1.8.0)
  viewpointId: {guid: Guid}
  → viewpointIds: [{viewpointId: {guid: Guid}}]

### GetAddOnViewpoints
# Returns the details of the given add-on viewpoint items: their parent, type (Root, Group or Leaf), ID, name, view settings flags and attached data (base64 encoded). The output is aligned with the input array; an item that cannot be read gets an error. Available from Archicad 27. (since 1.8.0)
  viewpointIds[]: viewpointId: {guid: Guid}
  → viewpoints: [AddOnViewpointDetails | ErrorItem]

### CreateAddOnViewpoints
# Creates add-on viewpoint roots, groups and leaf nodes in the Project Map, with their ID, name, view settings flags (leaf nodes only) and attached data (base64 encoded). A group or a leaf node is created in the given parent root or group. Returns the identifier of each new item, or an error for an item that could not be created. Roots and groups can't be created in a Teamwork project. Available from Archicad 27. (since 1.8.0)
  viewpoints[]: itemType: AddOnViewpointType, ?parentViewpointId: {guid: Guid}, ?displayId: string, ?displayName: string, ?viewSettingsFlags: int, ?data: string
  → viewpoints: [{viewpointId: {guid: Guid}} | ErrorItem]

### ChangeAddOnViewpoints
# Changes the ID, name, view settings flags or attached data (base64 encoded) of the given add-on viewpoint items; only the given fields are changed. Roots and groups can't be changed in a Teamwork project. Available from Archicad 27. (since 1.8.0)
  viewpoints: [AddOnViewpointModificationData]
  → executionResults: ExecutionResults

### ReorderNavigatorItems
# Reorders the children of a navigator item to match the given order. Works around MoveNavigatorItem being unable to reposition an item within its current parent, by bouncing it through a sibling. (since 2.0.0)
  parentNavigatorItemId: NavigatorItemId, orderedNavigatorItemIds: [NavigatorItemIdArrayItem]
  → executionResults: ExecutionResults

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

### GetGraphicalOverrideStyleOfElements
# Returns the graphic override style each element is drawn with in the current window: for every overridable member (line type, pens, fill types, surfaces, ...) whether the active graphic override combination replaces it, and with what. Needs Archicad 27 or later. (since 1.8.0) [AC27+]
  elements: Elements
  → styles: [{?lineType: OverriddenValue, ?lineMarkerTextPen: OverriddenValue, ?overrideLinePenThickness: bool, ?cutFillType: OverriddenValue, ?cutFillForegroundPen: OverriddenValue, ?cutFillBackgroundPen: OverriddenValue, ?overrideCutFillForegroundThickness: bool, ?coverFillType: OverriddenValue, ?coverFillForegroundPen: OverriddenValue, ?coverFillBackgroundPen: OverriddenValue, ?overrideCoverFillForegroundThickness: bool, ?draftFillType: OverriddenValue, ?draftFillForegroundPen: OverriddenValue, ?draftFillBackgroundPen: OverriddenValue, ?overrideDraftFillForegroundThickness: bool, ?cutSurface: OverriddenValue, ?uncutSurface: OverriddenValue, ?showSkinSeparators: bool, ?hideCutContours: bool, ?hideUncutContours: bool} | ErrorItem]

## Issue Management Commands

### CreateIssue
# Creates a new issue. (since 1.0.7)
  name: string, ?parentIssueId: IssueId, ?tagText: string
  → issueId: IssueId

### DeleteIssue
# Deletes the specified issue. With dryRun true nothing is deleted and no undo step is created: the response has dryRun set to true, and wouldDelete when the issue exists. (since 1.0.7)
  issueId: IssueId, ?acceptAllElements: bool, ?dryRun: DryRun
  → ?dryRun: DryRunFlag, success: bool, ?error: Error, ?wouldDelete: true

### GetIssues
# Retrieves information about existing issues. (since 1.0.7)
  → issues: [{issueId: IssueId, name: string, parentIssueId: IssueId, creaTime: int, modiTime: int, tagText: string, tagTextElementId: ElementId, isTagTextElemVisible: bool}]

### AddCommentToIssue
# Adds a new comment to the specified issue. (since 1.0.7)
  issueId: IssueId, ?author: string, ?status: IssueCommentStatus, text: string
  → ExecutionResult

### GetCommentsFromIssue
# Retrieves comments information from the specified issue. (since 1.0.7)
  issueId: IssueId
  → comments: [{guid: Guid, author: string, text: string, status: IssueCommentStatus, creaTime: int}]

### AttachElementsToIssue
# Attaches elements to the specified issue. (since 1.0.7)
  issueId: IssueId, elements: Elements, type: IssueElementType
  → ExecutionResult

### DetachElementsFromIssue
# Detaches elements from the specified issue. (since 1.0.7)
  issueId: IssueId, elements: Elements
  → ExecutionResult

### GetElementsAttachedToIssue
# Retrieves attached elements of the specified issue, filtered by attachment type. (since 1.0.7)
  issueId: IssueId, type: IssueElementType
  → elements: Elements

### ExportIssuesToBCF
# Exports specified issues to a BCF file. With overwrite false it refuses to replace an existing file. (since 1.0.7)
  ?issues: Issues, exportPath: string, ?overwrite: bool, useExternalId: bool, alignBySurveyPoint: bool
  → ExecutionResult

### ImportIssuesFromBCF
# Imports issues from the specified BCF file. (since 1.0.7)
  importPath: string, alignBySurveyPoint: bool
  → ExecutionResult

### ImportMarkupsFromPDF
# Imports the markups of the specified PDF file as issues, like Issue Manager > Import PDF markups, without any dialog and without opening the Issue Manager palette, and reports the issues it created. Available from Archicad 29. (since 1.7.3)
  pdfFilePath: string
  → executionResult: ExecutionResult, issues: Issues

## Revision Management Commands

### GetRevisionIssues
# Retrieves all issues. (since 1.2.0)
  → revisionIssues: [RevisionIssue], ?customScheme: [{customSchemeKey: Guid, customSchemeName: string}]

### ModifyRevisionIssues
# Modifies the ID, the short description and the custom scheme data of the given revision issues. Only the given fields are changed. Issued revision issues may refuse the change. (since 1.8.0)
  revisionIssues[]: revisionIssueId: RevisionIssueId, ?id: string, ?description: string, ?customSchemeData: [{?customSchemeKey: Guid, ?customSchemeName: string, customSchemeValue: string}]
  → executionResults: ExecutionResults

### GetRevisionChanges
# Retrieves all changes. (since 1.2.0)
  → revisionChanges: [RevisionChange]

### GetRevisionChangeCustomScheme
# Retrieves the custom fields of changes (the change custom scheme): the key and the name of each field. The keys are the customSchemeKey values in the customSchemeData of changes. (since 1.7.3)
  → customScheme: [RevisionChangeCustomSchemeItem]

### GetDocumentRevisions
# Retrieves all document revisions. (since 1.2.0)
  → documentRevisions: [DocumentRevision]

### GetCurrentRevisionChangesOfLayouts
# Retrieves all changes belong to the last revision of the given layouts. (since 1.2.0)
  layoutDatabaseIds: Databases
  → currentRevisionChangesOfLayouts: RevisionChangesOfEntities

### GetRevisionChangesOfElements
# Retrieves the changes belong to the given elements. (since 1.2.0)
  elements: Elements
  → revisionChangesOfElements: RevisionChangesOfEntities

## Design Options Commands

### GetDesignOptions
# Retrieves information about existing design options. Available from Archicad 29. (since 1.2.9)
  → designOptions: [DesignOptionDetails]

### GetDesignOptionSets
# Retrieves information about existing design option sets, and in Teamwork projects the Teamwork identifier of the design options. Available from Archicad 29. (since 1.2.9)
  → designOptionSets: [{designOptionSetId: GuidId, name: string, ?isEditable: bool, ?notEditableError: Error, designOptions: [DesignOptionIdArrayItem]}], ?teamworkId: GuidId

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

### ActivateDesignOptionsInCombinations
# Activates one design option in each of the given combinations, without listing all active design options of the combination. Available from Archicad 29. (since 1.8.0)
  designOptionsToActivate[]: designOptionCombinationId: DesignOptionCombinationId, designOptionId: DesignOptionId
  → executionResults: ExecutionResults

### DeactivateDesignOptionsInCombinations
# Turns off the given design options in the given combinations, leaving their other options as they are. Available from Archicad 29. (since 1.7.3)
  deactivatedDesignOptionsInCombinations: [DesignOptionDeactivation]
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
# Changes the name and/or the string id of the given design options. Available from Archicad 29. (since 1.7.2)
  designOptions[]: designOptionId: DesignOptionId, ?name: string, ?id: string
  → executionResults: ExecutionResults

### RenameDesignOptionSets
# Changes the name of the given design option sets. Available from Archicad 29. (since 1.7.2)
  designOptionSets[]: designOptionSetId: DesignOptionSetId, name: string
  → executionResults: ExecutionResults

### RenameDesignOptionCombinations
# Changes the name of the given design option combinations. Available from Archicad 29. (since 1.7.2)
  designOptionCombinations[]: designOptionCombinationId: DesignOptionCombinationId, name: string
  → executionResults: ExecutionResults

### DeleteDesignOptions
# Deletes the given design options. Available from Archicad 29. (since 1.7.2)
  designOptions: [DesignOptionIdArrayItem]
  → executionResults: ExecutionResults

### DeleteDesignOptionSets
# Deletes the given design option sets. Available from Archicad 29. (since 1.7.2)
  designOptionSets: [DesignOptionSetIdArrayItem]
  → executionResults: ExecutionResults

### DeleteDesignOptionCombinations
# Deletes the given design option combinations. Available from Archicad 29. (since 1.7.2)
  designOptionCombinations: [DesignOptionCombinationIdArrayItem]
  → executionResults: ExecutionResults

### GetHotlinkDesignOptionTables
# Retrieves the design option table of the given hotlink nodes and placed hotlink instances: the filter mode (main model only, by options or by combination), the design option sets, options and combinations of the hotlinked module and which of them are active. Available from Archicad 29. (since 2.0.0)
  hotlinks: [{hotlinkNodeId: HotlinkNodeId} | {elementId: ElementId}]
  → hotlinkDesignOptionTables: [{hotlinkNodeId: HotlinkNodeId, filterMode: "MainModelOnly"|"FilterByOptions"|"FilterByCombination"|"Unknown", designOptionCombinations: [string], ?activeDesignOptionCombination: string, designOptionSets: [{name: string, designOptions: [string], ?activeDesignOption: string}]} | ErrorItem]

### SetHotlinkDesignOptionTables
# Sets the filter mode, the active combination and the active option of sets in the design option table of the given placed hotlink instances. Available from Archicad 29. (since 2.0.0)
  hotlinkInstances[]: elementId: ElementId, ?filterMode: "MainModelOnly"|"FilterByOptions"|"FilterByCombination", ?activeDesignOptionCombination: string, ?activeDesignOptions: [{setName: string, designOptionName: string}]
  → executionResults: ExecutionResults

### SetDefaultDesignOption
# Sets the given design option as the default, or the Main Model when no design option is given. Available from Archicad 29. (since 1.8.0)
  ?designOptionId: DesignOptionId
  → ExecutionResult

### ReorderDesignOptionSets
# Moves the given design option sets before another set or to the end of the list. Available from Archicad 29. (since 1.8.0)
  designOptionSets[]: designOptionSetId: DesignOptionSetId, ?beforeDesignOptionSetId: DesignOptionSetId
  → executionResults: ExecutionResults

### ReorderDesignOptionsInSet
# Moves the given design options before another design option of the same set or to the end of their set. Available from Archicad 29. (since 1.8.0)
  designOptions[]: designOptionId: DesignOptionId, ?beforeDesignOptionId: DesignOptionId
  → executionResults: ExecutionResults

### CanMoveElementsToDesignOptions
# Checks whether the given elements can be moved to another design option or to the main model, with the reason when they cannot. Available from Archicad 29. (since 1.8.0)
  elements: Elements
  → canMoveElements: [{elementId: ElementId, canMove: bool, ?error: Error}]

### DuplicateDesignOptionCombinations
# Duplicates the given design option combinations and returns the identifiers of the new combinations. Available from Archicad 29. (since 1.7.3)
  designOptionCombinations: [DesignOptionCombinationIdArrayItem]
  → designOptionCombinationIdsOrErrors: DesignOptionCombinationIdsOrErrors

### GetDesignOptionCombinationOfViews
# Retrieves which design option combination the given views show: only the main model, a combination, a custom set of design options or a deleted combination. Available from Archicad 27. (since 2.0.0)
  navigatorItemIds: NavigatorItemIds
  → designOptionCombinationOfViews: [{navigatorItemId: NavigatorItemId, status: "MainModelOnly"|"Standard"|"Custom"|"Missing", name: string, ?designOptionCombinationId: DesignOptionCombinationId} | ErrorItem]

### SetDesignOptionCombinationOfViews
# Sets the design option combination the given views show, or makes them show only the main model. Available from Archicad 27. (since 2.0.0)
  navigatorItemIdsWithCombination[]: navigatorItemId: NavigatorItemId, ?designOptionCombinationId: DesignOptionCombinationId, ?mainModelOnly: bool
  → executionResults: ExecutionResults

### GetHotlinkDesignOptionTableDetails
# Reads the design option table of hotlink nodes: the design option sets, options and combinations of the hotlinked source file, and which of them the node shows. Available from Archicad 29. (since 1.8.0)
  hotlinkNodes[]: hotlinkNodeId: HotlinkNodeId
  → hotlinkDesignOptionTables: [{nodeGuid: GuidId, filterMode: "MainModelOnly"|"FilterByOptions"|"FilterByCombination", sets: [{name: string, options: [string], ?activeOption: string}], combinations: [string], ?activeCombination: string} | ErrorItem]

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

## Project Data Commands

### GetProjectDataKeys
# Lists the project data stored by Tapir in the project: the names, the identifiers of the add-on objects that store them, whether they are kept on this client only and the Teamwork user who has reserved them. Project data is text (for example JSON) saved in the project file by scripts and Grasshopper definitions, such as their settings or the mapping of elements to an external system. (since 1.7.3)
  → keys: [ProjectDataKey]

### GetProjectData
# Gets the content of the project data with the given names. (since 1.7.3)
  names: [ProjectDataName]
  → values: [ProjectDataValue | ErrorItem]

### SetProjectData
# Creates or overwrites project data: text (for example JSON) saved in the project under a name. New project data can be kept on this client only, or created as unique so that in Teamwork only one can exist with its name. Prefix the names with the name of your tool (for example 'my-tool/settings') so scripts do not overwrite each other's data. (since 1.7.3)
  values: [ProjectDataValueData]
  → executionResults: ExecutionResults

### DeleteProjectData
# Deletes the project data with the given names. (since 1.7.3)
  names: [ProjectDataName]
  → executionResults: ExecutionResults

### ReserveProjectData
# Reserves the project data with the given names in Teamwork, so that other users cannot change it. Returns the users who have already reserved some of it. (since 1.7.3)
  names: [ProjectDataName]
  → executionResult: ExecutionResult, ?conflicts: [ProjectDataReservationConflict]

### ReleaseProjectData
# Releases the project data with the given names in Teamwork. (since 1.7.3)
  names: [ProjectDataName]
  → ExecutionResult

### RequestProjectData
# Requests the project data with the given names in Teamwork from the users who have reserved it, with an optional message. (since 1.7.3)
  names: [ProjectDataName], ?mailText: string
  → ExecutionResult

### GrantProjectData
# Grants the project data with the given names, reserved by the current user, to another Teamwork user. (since 1.7.3)
  names: [ProjectDataName], toUserId: int
  → ExecutionResult

### GetModulData
# Gets the module data Tapir stored in the project with StoreModulData: the given names, or all of them, with their data version and, unless includeContent is false, their content. Module data are the custom data sections of Archicad's ModulData Manager: text saved in the project file under a name, kept apart from project data (SetProjectData). (since 2.0.0)
  ?names: [string], ?includeContent: bool
  → modulData: [{name: string, dataVersion: int, ?content: string} | ErrorItem]

### StoreModulData
# Creates or overwrites module data: text (for example JSON) saved in the project under a name, with an optional data version. Prefix the names with the name of your tool (for example 'my-tool/settings') so scripts do not overwrite each other's data. Storing module data is not an undoable step. (since 2.0.0)
  modulData[]: name: string, content: string, ?dataVersion: int
  → executionResults: ExecutionResults

### DeleteModulData
# Deletes the module data with the given names. Deleting module data is not an undoable step. (since 2.0.0)
  names: [string]
  → executionResults: ExecutionResults

## MEP Commands

### GetMEPElements
# Retrieves the MEP (Mechanical, Electrical, Plumbing) elements of the project (every element the MEP API lists, and from Archicad 30 the electrical panels and devices), optionally filtered by type and domain. MEP elements are ordinary elements, so the generic element commands work on them as well (for example they can be deleted with the DeleteElements command). Available from Archicad 28. (since 1.5.6)
  ?elementTypes: [MEPElementType], ?domains: [MEPDomain]
  → elements: [MEPElement]

### GetMEPRoutingElements
# Retrieves the details of the given MEP routing elements: domain, MEP system, offset from the home story, branch preference table, the ports logically connected at the route's beginning and end, the floor plan display settings (cut plane position, floor plan display option, show projection and on-story visibility, from Archicad 29), route polyline, segments with cross section data (shape, size, preference table and reference id), begin and end nodes, anchor, reference line offsets, wall thickness, flange size, connection style, insulation thickness and rigid segments, and nodes with their incoming and outgoing segments, preferred transition placement, elbows and transitions. Available from Archicad 28. (since 1.5.6)
  elements: Elements
  → routingElements: MEPRoutingElementDetailsOrErrors

### GetMEPPorts
# Retrieves the ports of the given MEP elements including position, shape, size, connection status (Archicad 27: whether the port is connected, from Archicad 28: whether it is physically connected) and connection style (from Archicad 30), the flow direction of piping and ventilation ports (from Archicad 28), the nominal size of piping ports (from Archicad 30), and the outer diameter, wall thickness and flange size (Archicad 30) of piping and ventilation ports. Available from Archicad 27. (since 1.5.6)
  elements: Elements
  → elementPorts: MEPElementPortsOrErrors

### GetMEPDistributionSystems
# Retrieves the MEP distribution systems of the project with their domain, MEP system attribute, member elements, physical systems (from Archicad 29) and optionally their tree: the elements from the root element on, each with its previous and next elements and the connecting ports. Available from Archicad 28. (since 1.5.6)
  ?includeTree: bool
  → distributionSystems: [MEPDistributionSystem], ?ports: [Guid]

### CreateMEPRoutingElements
# Creates MEP routing elements (duct, pipe or cable carrier routes) along the given polylines with optional cross section data (shape, size, preference table and reference id), MEP system and layer (also set on the segments, elbows and transitions), and optional elbow and transition defaults (preference tables and elbow radius factor, from Archicad 29) that apply only to what is placed. Available from Archicad 28. (since 1.5.6)
  routingElementsData: [MEPRoutingElementData]
  → elements: ElementIdsOrErrors

### CreateMEPElements
# Creates MEP elements (Terminal, Accessory, Equipment or Fitting) at the given positions, optionally with another library part, size (from Archicad 30), MEP system, port sizes and shapes and a changed insulation, which apply only to what is placed. Available from Archicad 28. (since 1.5.6)
  elementsData: [MEPElementData]
  → elements: ElementIdsOrErrors

### ModifyMEPRoutingElements
# Modifies the given MEP routing elements: MEP system, branch preference table, floor plan display settings (cut plane position, floor plan display option, show projection and on-story visibility, from Archicad 29), cross section data (shape, size, preference table and reference id), anchor, reference line offsets, wall thickness, flange size and connection style of all segments, preferred transition placement of all nodes, insulation thickness of the whole route (segments, elbows and transitions), and node positions. Available from Archicad 28. (since 1.5.6)
  routingElementsData: [MEPRoutingElementModificationData]
  → executionResults: ExecutionResults

### ModifyMEPPorts
# Modifies the given MEP ports (as returned by GetMEPPorts): shape, connection style (from Archicad 30), the flow direction of piping and ventilation ports, and the outer diameter and nominal size (from Archicad 30) of piping ports. Only the given fields are changed. Available from Archicad 28. (since 1.8.0)
  portsData: [MEPPortModificationData]
  → executionResults: ExecutionResults

### ConnectMEPElements
# Connects MEP routing elements to other MEP elements or routes. Merges routes, splits routes or creates branch elements as needed. The first or last node of the 'connectToId' route must lie exactly on the 'routingElementId' route, so for a tee pass the main route as 'routingElementId' and the branch as 'connectToId'. A failed connection says which condition is not met. Archicad 27 does not report the merged, split or created elements. Available from Archicad 27. (since 1.5.6)
  connectionsData: [MEPConnectionData]
  → connectionResults: MEPConnectionResultsOrErrors

### CheckMEPPortConnectability
# Checks whether MEP ports can be connected to other ports, for the given pairs of ports. Archicad 28 and later check the physical connection. Available from Archicad 27. (since 1.8.0) [AC28+]
  portPairs: [MEPPortPair]
  → results: [MEPPortConnectability | ErrorItem]

### GetMEPPreferenceTables
# Gets the circular cross section preference tables (referenceId, diameter, wall thickness, description) and the reference set of the Piping or Ventilation domain, optionally with the elbow, branch and transition preference tables, plus the rectangular duct tables of the Ventilation domain or the segment tables of the CableCarrier domain. Each table has its name and whether it is editable; the segment tables also have their segmentation lengths from Archicad 29. The rows of the circular, elbow, branch and transition tables say whether they are valid, and the reference set and the angle set say which of their reference ids and angles are defined. The angle set and the transition tables are available from Archicad 29. Every row has its index in the table, as ModifyMEPPreferenceTables expects it. Available from Archicad 28. (since 1.5.7)
  domain: MEPPreferenceTableDomain, ?includeFittingTables: bool
  → tables: [MEPPreferenceTable], ?rectangularTables: [MEPValuePreferenceTable], ?cableCarrierTables: [MEPValuePreferenceTable], ?referenceSet: MEPReferenceSet, ?angleSet: MEPAngleSet, ?elbowTables: [MEPElbowPreferenceTable], ?branchTables: [MEPBranchPreferenceTable], ?transitionTables: [MEPTransitionPreferenceTable]

### ModifyMEPPreferenceTables
# Modifies the MEP preference tables of a domain, in the shape GetMEPPreferenceTables returns them: adds tables, changes their names, segmentation lengths (from Archicad 29) and row values and descriptions, deletes or empties rows, adds rows to the rectangular duct and cable carrier tables, deletes tables, deletes reference ids from the reference set, and adds and deletes angles of the angle set (from Archicad 29). Each table is changed in one undoable step. Available from Archicad 28. (since 1.8.0)
  domain: MEPPreferenceTableDomain, ?tablesToAdd: [MEPPreferenceTableAddition], ?tables: [MEPPreferenceTableChange], ?tablesToDelete: [string], ?referenceIdsToDelete: [int], ?anglesToAdd: [float], ?anglesToDelete: [float]
  → addedTables: [{guid: string} | FailedExecutionResult], tables: ExecutionResults, deletedTables: ExecutionResults, ?referenceSet: ExecutionResult, ?addedAngles: ExecutionResult, ?angleSet: ExecutionResult

### GetMEPSystemGroups
# Gets the MEP system groups of the project with their physical systems: name, editable flag, root element and MEP system. Available from Archicad 29. (since 1.7.2)
  → systemGroups: [MEPSystemGroupDetailsOrError]

### CreateMEPSystemGroups
# Creates MEP system groups. Available from Archicad 29. (since 1.7.2)
  systemGroupsData: [MEPSystemGroupData]
  → systemGroups: [MEPSystemGroupIdOrError]

### CreateMEPPhysicalSystems
# Creates physical systems in MEP system groups, optionally with a root element and an MEP system as their category. Available from Archicad 29. (since 1.7.2)
  physicalSystemsData: [MEPPhysicalSystemData]
  → physicalSystems: [MEPPhysicalSystemIdOrError]

### ModifyMEPSystemGroups
# Renames MEP system groups. Available from Archicad 29. (since 1.7.3)
  systemGroupsData: [MEPSystemGroupModificationData]
  → executionResults: ExecutionResults

### ModifyMEPPhysicalSystems
# Modifies MEP physical systems: name, root element and the MEP system used as their category. Only the given fields are changed. Available from Archicad 29. (since 1.7.3)
  physicalSystemsData: [MEPPhysicalSystemModificationData]
  → executionResults: ExecutionResults

### DeleteMEPPhysicalSystems
# Removes MEP physical systems from their system groups. Their member elements are not deleted. Available from Archicad 29. (since 1.7.3)
  physicalSystems: [MEPPhysicalSystemIdArrayItem]
  → executionResults: ExecutionResults

### GetMEPToolDefaults
# Retrieves the current settings of the MEP tools per domain, without changing them: the routing tool (MEP system, branch preference table, floor plan display settings from Archicad 29, and its segment, node, elbow (Archicad 27 and from Archicad 29) and transition defaults), its rigid segment and branch defaults, the flexible segment tool, the library part, insulation and port settings of the terminal, accessory, fitting and equipment tools, and from Archicad 30 the electrical panel tool with its number of circuit defaults. Archicad 27 gives fewer settings, and only the shape of the ports. Available from Archicad 27. (since 2.0.0)
  ?domains: [MEPDomain]
  → toolDefaults: [MEPDomainToolDefaults], ?equipment: MEPElementDefaultDetails, ?electricalPanel: ElectricalPanelToolDefaults

### TransferMEPSettings
# Picks up the settings of an MEP element and injects them into other MEP elements of the same type and domain, like Archicad's pick up and inject parameters. Works for routing elements, terminals, accessories, equipment, fittings, flexible segments, branches, take-offs and (from Archicad 30) electrical panels and devices. Each target is changed in its own undoable step. Available from Archicad 28. (since 2.0.0)
  sourceElementId: ElementId, targetElements: Elements
  → executionResults: ExecutionResults

### GetMEPPhysicalSystemsOfElements
# Returns the physical systems each of the given MEP elements is part of. Available from Archicad 29. (since 2.0.0)
  elements: Elements
  → physicalSystemsOfElements: [MEPPhysicalSystemsOfElement]

### CreateMEPFlexibleSegments
# Creates MEP flexible segments through the given control points, or along a polyline of alternating line and spline parts (Piping), with the current settings of the Flexible Segment tool of their domain, optionally with the orientation (control points) or direction (polyline) at both ends. Available from Archicad 28. (since 2.0.0)
  flexibleSegmentsData: [MEPFlexibleSegmentCreationData]
  → elements: ElementIdsOrErrors

### CreateMEPTakeOffs
# Creates MEP take-offs on the given routing segments, at a distance from the beginning of the segment (not more than its length) and optionally rotated around its axis by a multiple of 90 degrees, with the current settings of the Take-Off tool of their domain (by default the domain of the segment's routing element), optionally with their length and without insulation, which apply only to what is created. Archicad only has Ventilation take-offs. Available from Archicad 28. (since 2.0.0)
  takeOffsData: [MEPTakeOffCreationData]
  → elements: ElementIdsOrErrors

### ModifyMEPElements
# Modifies placed MEP elements: the anchor point, orientation and library part of terminals, accessories, equipment, fittings and flexible segments, the control points, polyline (Piping, from Archicad 28), and width and height of flexible segments. Only the given fields are changed, in one undo step with one execution result per element; an item with a field that does not fit its element changes nothing. Archicad reports a 'libraryPartId' it does not find only after the item's other changes were made, so that item's error says which changes stayed. Available from Archicad 27. (since 2.0.0)
  elements: [MEPElementModificationData]
  → executionResults: ExecutionResults

### GetMEPRoutingParameters
# Gets the routing parameters of placed MEP elements: of a routing element its routing node parameters (preferred transition placement, elbow from Archicad 29, transition) and routing segment parameters (cross section, preference table, anchor, reference line offsets, wall thickness, flange size, connection style); of a routing node its elbow (from Archicad 29) and transition parameters; of a routing segment its rigid segment parameters (Archicad 28 only). Available from Archicad 28. (since 1.8.0)
  elements: Elements
  → routingParameters: [MEPRoutingParameters | ErrorItem]

### SetMEPRoutingParameters
# Sets the routing parameters of placed MEP elements: the routing segment parameters (cross section and preference table) and, from Archicad 29, the routing node parameters (elbow radius factor and preference table, transition preference table) of routing elements, and the elbow and transition parameters of routing nodes (from Archicad 29). Only the given keys are changed, with one execution result per element. A changed preference table is also set on each of the route's segments and nodes and injected into them, because Archicad 29 can otherwise keep the old one; the item fails if they still report the old table. Available from Archicad 28. (since 1.8.0)
  elements: [ElementMEPRoutingParameters]
  → executionResults: ExecutionResults

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
  → voltage: float, wiringTypes: [ElectricalWiringType], loadClassifications: [ElectricalLoadClassification]

### CreateElectricalPanels
# Places electrical panels with the default settings of the Electrical Panel tool, optionally with the given library part, size, rotation, mirroring, panel name and circuit naming. Available from Archicad 30. (since 1.7.2)
  electricalPanelsData: [ElectricalPanelData]
  → elements: ElementIdsOrErrors

### CreateElectricalDevices
# Places electrical devices with the default settings of the Electrical Device tool, optionally with the given library part, size, rotation, mirroring, apparent power and load classification, and connects them to a circuit. Available from Archicad 30. (since 1.7.2)
  electricalDevicesData: [ElectricalDeviceData]
  → elements: ElementIdsOrErrors

### ModifyElectricalPanels
# Modifies the name, circuit naming and placement (anchor point, orientation, rotation, mirroring, library part, size) of electrical panels. Available from Archicad 30. (since 1.7.2)
  electricalPanelsData: [ElectricalPanelModificationData]
  → executionResults: ExecutionResults

### CreateElectricalCircuits
# Adds new circuits to electrical panels, optionally with the given description, voltage, wiring type and used phases. Available from Archicad 30. (since 1.7.2)
  electricalCircuitsData: [ElectricalCircuitData]
  → elements: ElementIdsOrErrors

### DeleteElectricalCircuits
# Removes electrical circuits from their panels. Available from Archicad 30. (since 1.7.2)
  electricalCircuits: Elements
  → executionResults: ExecutionResults

### ModifyElectricalCircuits
# Modifies the description, voltage, wiring type and used phases of electrical circuits. Available from Archicad 30. (since 1.7.2)
  electricalCircuitsData: [ElectricalCircuitModificationData]
  → executionResults: ExecutionResults

### ModifyElectricalDevices
# Modifies the apparent power, load classification and placement (anchor point, orientation, rotation, mirroring, library part, size) of electrical devices. Available from Archicad 30. (since 1.7.2)
  electricalDevicesData: [ElectricalDeviceModificationData]
  → executionResults: ExecutionResults

### ConnectToElectricalCircuits
# Connects electrical devices, or panels as sub-panels, to electrical circuits. Available from Archicad 30. (since 1.7.2)
  connectionsData: [ElectricalCircuitConnectionData]
  → executionResults: ExecutionResults

### ModifyElectricalProjectSettings
# Modifies the electrical project settings: sets the default voltage and clears, adds or removes wiring types and load classifications. Available from Archicad 30. (since 1.7.2)
  ?voltage: float, ?clearWiringTypes: bool, ?clearLoadClassifications: bool, ?wiringTypesToAdd: [{name: string, crossSectionalArea: float}], ?wiringTypesToRemove: [string], ?loadClassificationsToAdd: [{name: string, demandFactor: float}], ?loadClassificationsToRemove: [string]
  → ExecutionResult

### GetMEPElementDetails
# Retrieves the type-specific details of the given MEP elements: insulation thickness and routing segment of rigid segments, control points and polyline of flexible segments, radius factor, insulation thickness, preference table and routing node of elbows (from Archicad 29), angle, length and insulation thickness of branches, and offsets, wider and narrower ports, insulation thickness, routing node and (from Archicad 29) preference table of transitions. Available from Archicad 28. (since 1.8.0)
  elements: Elements
  → elementDetails: [MEPElementDetails | ErrorItem]

## MEP Commands (extended)

### GetMEPPreferenceTableRows
# Gets rows of a segment, branch, elbow or (from Archicad 29) transition preference table by their key (the reference ids and, for branch and elbow rows from Archicad 29, the angle): whether the row is valid and its values (diameters, wall thickness, radius, length, angle, branch offset, connection length, description), and whether the table exists. Rectangular duct and cable carrier segment tables only give whether they exist, as their rows have no key. On Archicad 27, which has one kind of preference table, a row is found by its shape and index and has a value and a description; the table's name and number of rows per shape are returned too. Available from Archicad 27. (since 1.8.0)
  tableId: MEPPreferenceTableId, keys: [MEPPreferenceRowKey]
  → exists: bool, ?name: string, ?sizes: {?Circular: int, ?Rectangular: int}, rows: [MEPPreferenceRowDetails | ErrorItem]

### SetMEPPreferenceTableRows
# Sets the given values of rows of a segment, branch, elbow or (from Archicad 29) transition preference table, found by their key (the reference ids and, for branch and elbow rows from Archicad 29, the angle). Only the given values are changed, in one undo step. On Archicad 27 a row is found by its shape and index, its value and description are set, and its index after the call is returned; the keys give the indices before the call. Available from Archicad 27. (since 1.8.0)
  tableId: MEPPreferenceTableId, rows: [MEPPreferenceRowUpdate]
  → executionResults: [MEPPreferenceRowUpdateResult | FailedExecutionResult]

### AddMEPPreferenceTableRows
# Adds rows with the given keys and optionally values to a branch, elbow or transition preference table and returns their index, in one undo step. Branch tables from Archicad 28, elbow and transition tables from Archicad 29; segment tables have a row for each reference id. On Archicad 27 a row is added to the list of the given shape of any preference table, and the index of each new row after the call is returned. Available from Archicad 27. (since 1.8.0)
  tableId: MEPPreferenceTableId, rows: [MEPPreferenceRowAddition]
  → executionResults: [MEPPreferenceRowAdditionResult | FailedExecutionResult]

### DeleteMEPPreferenceTableRows
# Deletes rows of a segment, branch, elbow or (from Archicad 29) transition preference table by their key (the reference ids and, for branch and elbow rows from Archicad 29, the angle), in one undo step. The rows of segment tables, and of the elbow tables of Archicad 28, are emptied instead. On Archicad 27 a row is found by its shape and index. Available from Archicad 27. (since 1.8.0)
  tableId: MEPPreferenceTableId, keys: [MEPPreferenceRowKey]
  → executionResults: ExecutionResults

### GetMEPPreferenceTableContainers
# Lists the preference tables of the Piping, Ventilation and Cable Carrier preference table containers of Archicad 27: their id, name, whether they exist and their number of rows per shape, and whether the container exists. Only for Archicad 27; from Archicad 28 use GetMEPPreferenceTables. (since 1.8.0)
  ?domains: [MEPPreferenceTableDomain]
  → containers: [MEPPreferenceTableContainer | ErrorItem]

### CreateMEPPreferenceTables
# Adds empty preference tables with the given names to the preference table container of a domain of Archicad 27 and returns their id, in one undo step. Only for Archicad 27. (since 1.8.0)
  domain: MEPPreferenceTableDomain
  tables[]: name: string
  → executionResults: [MEPPreferenceTableCreationResult | FailedExecutionResult]

## Analytical Commands

### GetCurrentAnalyticalModel
# Retrieves the Structural Analytical Model created for the current view. Available from Archicad 27. (since 1.7.3)
  → analyticalModelId: GuidId

### UpdateAnalyticalModel
# Triggers an update of the given Structural Analytical Model, or of the model of the current view when no model is given. Available from Archicad 27. (since 1.7.3)
  ?analyticalModelId: GuidId
  → ExecutionResult

### SetAnalyticalGenerationSettingsToNoRule
# Sets the generation settings of the current Structural Analytical Model to no rules. Available from Archicad 27. (since 1.7.3)
  → ExecutionResult

### GetAnalyticalModelCheckTypeId
# Retrieves the type identifier of the Structural Analytical Model check. Available from Archicad 29. (since 1.7.3)
  → modelCheckTypeId: GuidId

### GetAnalyticalModelVariation
# Retrieves the variation of the given Structural Analytical Model, or of the model of the current view when no model is given (the model is required before Archicad 27). The fields of the variation depend on the Archicad version. (since 1.8.0)
  ?analyticalModelId: GuidId
  → variation: AnalyticalModelVariation

### GetAnalyticalModel
# Retrieves the Structural Analytical Model of the given variation, as returned by GetAnalyticalModelVariation. (since 1.8.0)
  variation: AnalyticalModelVariation
  → analyticalModelId: GuidId

### GetAnalyticalVisibilitySettings
# Retrieves the visibility settings of the Structural Analytical Model. Available from Archicad 26. (since 1.8.0)
  → visibilitySettings: AnalyticalVisibilitySettings

### SetAnalyticalVisibilitySettings
# Changes the given fields of the Structural Analytical Model visibility settings; the others keep their value. Available from Archicad 26. (since 1.8.0)
  visibilitySettings: AnalyticalVisibilitySettings
  → ExecutionResult

### GetAnalyticalMemberTypesOfElements
# Retrieves the analytical member type (Beam, Column, Roof, Slab, Wall or Unknown) of the given elements. (since 1.8.0)
  elements: Elements
  → memberTypesOfElements: [{memberType: AnalyticalMemberType} | ErrorItem]

### GetAnalyticalLoadGroups
# Retrieves the structural analysis load groups of the project with all their fields. (since 1.8.0)
  → loadGroups: [AnalyticalLoadGroup | ErrorItem]

### GetAnalyticalLoadCases
# Retrieves the structural analysis load cases of the given load group, or of the project when no load group is given, with all their fields. (since 1.8.0)
  ?loadGroupId: GuidId
  → loadCases: [AnalyticalLoadCase | ErrorItem]

### GetAnalyticalLoadCombinations
# Retrieves the structural analysis load combinations of the project with all their fields and load factors. (since 1.8.0)
  → loadCombinations: [AnalyticalLoadCombination | ErrorItem]

### CreateAnalyticalLoadGroups
# Creates structural analysis load groups in one undo step and returns their identifiers. (since 1.8.0)
  loadGroups: [AnalyticalLoadGroupData]
  → loadGroupIds: [AnalyticalLoadGroupIdArrayItem | ErrorItem]

### CreateAnalyticalLoadCases
# Creates structural analysis load cases in the given load groups in one undo step and returns their identifiers. (since 1.8.0)
  loadCases: [AnalyticalLoadCaseData]
  → loadCaseIds: [AnalyticalLoadCaseIdArrayItem | ErrorItem]

### CreateAnalyticalLoadCombinations
# Creates structural analysis load combinations, optionally with their load factors, in one undo step and returns their identifiers. The combination type is available from Archicad 27. (since 1.8.0)
  loadCombinations: [AnalyticalLoadCombinationData]
  → loadCombinationIds: [AnalyticalLoadCombinationIdArrayItem | ErrorItem]

### DeleteAnalyticalLoadGroups
# Deletes the given structural analysis load groups in one undo step. (since 1.8.0)
  loadGroupIds: [AnalyticalLoadGroupIdArrayItem]
  → executionResults: ExecutionResults

### DeleteAnalyticalLoadCases
# Deletes the given structural analysis load cases in one undo step. (since 1.8.0)
  loadCaseIds: [AnalyticalLoadCaseIdArrayItem]
  → executionResults: ExecutionResults

### DeleteAnalyticalLoadCombinations
# Deletes the given structural analysis load combinations in one undo step. (since 1.8.0)
  loadCombinationIds: [AnalyticalLoadCombinationIdArrayItem]
  → executionResults: ExecutionResults

### AddLoadCasesToLoadCombination
# Adds load cases with their factors to the given structural analysis load combination in one undo step. (since 1.8.0)
  loadCombinationId: GuidId, loadFactors: [AnalyticalLoadFactor]
  → executionResults: ExecutionResults

### GetAnalyticalMembers
# Lists the elements of the curve and surface members of the given Structural Analytical Model, or of the model of the current view when no model is given (the model is required before Archicad 27). (since 1.8.0)
  ?analyticalModelId: GuidId
  → curveMembers: Elements, surfaceMembers: Elements

### GetAnalyticalMemberDetails
# Retrieves the curve, surface or segmented surface member of the given elements in a Structural Analytical Model, with their connections. Cross sections, curves, nodes and surfaces are returned with every field the Archicad version has. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements, ?segmentationCentralAngle: float
  → analyticalMembers: [AnalyticalCurveMemberDetails | AnalyticalSurfaceMemberDetails | AnalyticalSegmentedSurfaceMemberDetails | ErrorItem]

### GetAnalyticalReleases
# Retrieves the releases of the given analytical members. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements
  → releases: [{release: AnalyticalRelease} | ErrorItem]

### SetAnalyticalReleases
# Replaces the releases of the given analytical members, in one undo step. Available from Archicad 26. (since 1.8.0)
  releases: [ElementAnalyticalRelease]
  → executionResults: ExecutionResults

### GetCustomCurveMemberStretch
# Retrieves the lengths added to the start and end of the given curve members. Available from Archicad 29. (since 1.8.0)
  elements: Elements
  → stretches: [AnalyticalCurveMemberStretch | ErrorItem]

### SetCustomCurveMemberStretch
# Sets the lengths added to the start and end of the given curve members, in one undo step. Available from Archicad 29. (since 1.8.0)
  stretches: [AnalyticalCurveMemberStretchUpdate]
  → executionResults: ExecutionResults

### GetLCSOfAnalyticalMembers
# Retrieves the local coordinate system of the given analytical member parts, optionally in their intersection with another member part. Available from Archicad 26. (since 1.8.0)
  memberParts: [AnalyticalMemberCoordinateSystemRequest]
  → localCoordinateSystems: [{localCoordinateSystem: AnalyticalCoordinateSystem} | ErrorItem]

### GetAnalyticalMemberPartGeometries
# Retrieves the node of the given analytical member vertices and the curve of the given member edges. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, memberPartRefs: [AnalyticalMemberPartRef]
  → geometries: [{node: AnalyticalNode} | {curve: AnalyticalCurve} | ErrorItem]

### GetAnalyticalSupports
# Retrieves the settings, the supported member part and the geometry of the given analytical supports. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements
  → supports: [AnalyticalSupportDetails | ErrorItem]

### GetAnalyticalLinks
# Retrieves the settings, the connected member parts and the geometry of the given analytical links. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements
  → links: [AnalyticalLinkDetails | ErrorItem]

### CreateAnalyticalSupports
# Creates analytical supports from their settings and supported member part, as GetAnalyticalSupports returns them, in one undo step. Available from Archicad 26. (since 1.8.0)
  supports: [AnalyticalSupport]
  → elements: ElementIdsOrErrors

### CreateAnalyticalLinks
# Creates analytical links from their settings and connected member parts, as GetAnalyticalLinks returns them, in one undo step. Available from Archicad 26. (since 1.8.0)
  links: [AnalyticalLink]
  → elements: ElementIdsOrErrors

### ConvertAnalyticalLinksToNonShortest
# Converts the given shortest analytical links (associative to a curve member or a surface member edge) to links connected to a fixed coordinate, in one undo step, and returns the converted links. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements
  → links: [{link: AnalyticalLink} | ErrorItem]

### GetAnalyticalLoads
# Retrieves the settings, the loaded member part, the custom data (the curve of an edge load, the contour of a surface load) and the geometry of the given analytical point, edge and surface loads. Available from Archicad 26. (since 1.8.0)
  ?analyticalModelId: GuidId, elements: Elements
  → loads: [AnalyticalPointLoadDetails | AnalyticalEdgeLoadDetails | AnalyticalSurfaceLoadDetails | ErrorItem]

### CreateAnalyticalLoads
# Creates analytical point, edge and surface loads from their settings, loaded member part and custom data, as GetAnalyticalLoads returns them, in one undo step. Available from Archicad 26. (since 1.8.0)
  loads: [{pointLoad: AnalyticalPointLoad} | {edgeLoad: AnalyticalEdgeLoad, customData: AnalyticalEdgeLoadCustomData} | {surfaceLoad: AnalyticalSurfaceLoad, customData: AnalyticalSurfaceLoadCustomData}]
  → elements: ElementIdsOrErrors

### CreateElementsFromAnalyticalMembers
# Creates elements (beams, columns, walls, slabs, roofs) from the given curve, surface or segmented surface members, in the form GetAnalyticalMemberDetails returns them, optionally with the settings of a favorite, in one undo step. Returns the new elements and, from Archicad 26, the mapping of their edges and vertices to member parts. (since 2.0.0)
  members: [ElementFromAnalyticalMemberData]
  → elements: [ElementFromAnalyticalMember | ErrorItem]

## Solid Element Operation Commands

### CreateSolidElementLinks
# Creates solid element operation links between target and operator elements. (since 1.5.4)
  solidLinks: [SolidLinkData]
  → executionResults: ExecutionResults

### RemoveSolidElementLinks
# Removes solid element operation links between target and operator elements. With dryRun true nothing is removed and no undo step is created: the response has dryRun set to true, and each link that exists gets wouldDelete. (since 1.5.4)
  solidLinks: [SolidLinkReference], ?dryRun: DryRun
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### GetSolidElementLinks
# Returns solid element operation links for each queried element, grouped by role (target or operator). (since 1.5.4)
  elements: Elements
  → solidLinks: [SolidLinksOfElement]

### CreateSolidOperations
# Runs a solid operation (subtraction, intersection, addition) on two morphs and returns the resulting morphs, one item per operation. Unlike CreateSolidElementLinks this is not a link: the target and the operator morph are replaced by the result. Morphs only; the operations run in one undo step. (since 1.8.0)
  operations[]: targetId: ElementId, operatorId: ElementId, operation: SolidOperationType
  → results: [{elements: Elements} | ErrorItem]

### TrimElements
# Trims construction elements with a roof or shell: the roofs and shells in the list, or one given trimming element with a trim type. With several roofs or shells in the list Archicad decides which of them trims which element (they may also trim each other), so not every element is necessarily trimmed by each; to trim each element with each roof or shell, call it once per roof or shell with trimmingElement, and check the result with GetElementTrims. (since 1.5.9)
  elements: Elements, ?trimmingElement: ElementId, ?trimType: TrimType
  → ExecutionResult

### RemoveElementTrims
# Removes the trim between an element and the roof or shell trimming it. The Archicad API removes the trimming connection between the two elements, so when they trim each other (two roofs or shells) both directions are removed; trim the other direction again with TrimElements to keep it. With dryRun true nothing is removed and no undo step is created: the response has dryRun set to true, and each pair whose element is trimmed by its trimming element gets wouldDelete. (since 1.5.9)
  ?dryRun: DryRun
  elementPairs[]: elementId: ElementId, trimmingElementId: ElementId
  → ?dryRun: DryRunFlag, executionResults: DeletionExecutionResults

### GetElementTrims
# Which roofs and shells trim each queried element, with the trim type, and which elements it trims. (since 1.5.9)
  elements: Elements
  → elementTrims: [ElementTrimsOrError]

### MergeElements
# Merges the given construction elements (the Merge command of Archicad, which cleans up the junctions of slabs, beams, walls and similar elements). Undoable. The element types are not filtered: Archicad reports the ones it cannot merge. The merge is read back: when Archicad records no merge between the given elements (it decides which elements and type combinations it merges), the result is a failure, not a success. (since 1.8.0)
  elements: Elements
  → ExecutionResult

### UnmergeElements
# Removes the merge between the two elements of each given pair. Undoable; one execution result per pair. (since 1.8.0)
  elementPairs[]: elementId1: ElementId, elementId2: ElementId
  → executionResults: ExecutionResults

### GetMergedElements
# Gets the elements each queried element is merged with, one item per queried element; an unknown element is an error item. (since 1.8.0)
  elements: Elements
  → elementMerges: [MergedElementsOrError]

## Script UI Commands

### ShowScriptUI
# Shows the given HTML content in a native Archicad palette (a tkinter alternative for Python scripts) and returns the uiId of its window. Each script can have its own window, picked by uiId or scriptId; without them the first window is used. (since 1.5.5)
  htmlContent: string, ?width: int, ?height: int, ?title: string, ?resizable: bool, ?zoomEnabled: bool, ?zoomLevel: float, ?scrollBarsVisible: bool, ?contextMenuEnabled: bool, ?navigationDisabled: bool, ?allowSelfSignedCertificates: bool, ?clearCookies: bool, ?autoHeight: bool, ?uiId: int, ?scriptId: string
  → {success: true, uiId: int} | FailedExecutionResult

### GetScriptUIResult
# Retrieves and clears the result last submitted from a Script UI window's page (via window.ACAPI.SubmitResult), if any, and reports whether the window is still open, so a waiting script can stop when the user closes it. The window is picked by uiId or scriptId; without them the first window is used. (since 1.5.5)
  ?uiId: int, ?scriptId: string
  → ?uiId: int, hasResult: bool, ?result: string, isOpen: bool

### OpenSettingsDialog
# Opens Archicad's settings dialog of the selected elements or the current tool (Archicad 28 and later), or the default settings dialog of the given element type, waits for the user and reports whether the dialog was closed with OK or Cancel. (since 2.0.0) [AC28+]
  ?elementType: ElementType
  → cancelled: bool

### PickLibraryPart
# Opens Archicad's Object, Lamp, Window or Door Settings dialog, optionally limited to a library part subtype, lets the user pick a library part and set its parameters, and returns the chosen library part with its GDL parameters, or that the user cancelled. Places nothing. (since 2.0.0)
  ?elementType: "Object"|"Lamp"|"Window"|"Door", ?subtypeUnID: string
  → cancelled: bool, ?libPart: LibPartDetails, ?subtypeUnID: string, ?parameters: [StoredGDLParameter]

### PickLibraryPartFile
# Opens Archicad's Open Library Part dialog, waits for the user and returns the location of the chosen library part, or reports that the user cancelled. (since 2.0.0)
  ?generalGDLObjectsOnly: bool
  → cancelled: bool, ?path: string, ?openedInExternalEditor: bool

### PickPictureFile
# Opens Archicad's Open Picture dialog (the one of the texture settings), waits for the user and returns the location of the chosen picture, or reports that the user cancelled. Archicad adds the chosen picture to the embedded library when it is not in it yet. (since 2.0.0)
  → cancelled: bool, ?path: string

### PickZoneStampOrLabelFile
# Opens Archicad's dialog for opening a zone stamp or label library part, waits for the user and returns the location of the chosen file, or reports that the user cancelled. (since 2.0.0)
  ?objectType: "Label"|"ZoneStamp"
  → cancelled: bool, ?path: string

### PickLibraryPartSaveLocation
# Opens Archicad's Save Library Part dialog (object, door or window), waits for the user and returns the location chosen to save the library part to, or reports that the user cancelled. Nothing is saved. (since 2.0.0)
  ?defaultPath: string, ?libraryPartType: "Object"|"Door"|"Window", ?browseForFolder: bool, ?title: string
  → cancelled: bool, ?path: string

### PickLibraryFolder
# Opens Archicad's dialog for choosing or creating a library folder, waits for the user and returns the location of the folder, or reports that the user cancelled. The folder is not added to the libraries of the project. (since 2.0.0)
  ?defaultName: string
  → cancelled: bool, ?path: string

### ShowIFCExportSettings
# Opens Archicad's IFC export settings dialog, where the user picks a view and an IFC export translator, waits for the user and returns the chosen view and translator, or cancelled. Available from Archicad 28. (since 2.0.0)
  ?navigatorItemId: NavigatorItemId, ?translatorName: string
  → cancelled: bool, ?navigatorItemId: NavigatorItemId, ?viewName: string, ?translatorName: string

### PickAttribute
# Opens a small dialog with Archicad's attribute picker for the given attribute type (layer, building material, composite, profile or surface; fill and line from Archicad 27), waits for the user and returns the chosen attribute, or cancelled. Available from Archicad 26. (since 2.0.0)
  attributeType: "Layer"|"BuildingMaterial"|"Composite"|"Profile"|"Surface"|"Fill"|"Line", ?attributeId: AttributeId, ?title: string
  → cancelled: bool, ?attributeType: AttributeType, ?attributeId: AttributeId

### PickAttributeFolder
# Opens a small dialog with Archicad's attribute folder picker for the given attribute type, waits for the user and returns the chosen folder as its path from the root folder, or cancelled. Available from Archicad 26. (since 2.0.0)
  attributeType: "Layer"|"BuildingMaterial"|"Composite"|"Profile"|"Surface"|"Fill"|"Line", ?title: string
  → cancelled: bool, ?attributeFolder: AttributeFolder

## Developer Commands

### GenerateDocumentation
# Generates files for the documentation. Used by Tapir developers only. (since 1.0.7)
  destinationFolder: string
  → ExecutionResult
