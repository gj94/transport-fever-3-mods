# Opening and inspecting the TVC scene

Everything is in metres and in one shared local coordinate frame. Positive X points approximately WNW; positive Y points into the yard/SSW. The geometry is not compressed to fit a preview. Railway approaches are cropped at X = ±820 m; the route sum is about 16.56 km because many tracks run in parallel.

## Useful collections
- 01–02: photo-derived heritage pavilion/gallery geometry retained and refined from v01.
- 03–06: entrance/back arcade, waiting lounge, office/toilets/pantry and separate reconstructed booking hall.
- 09: editable mapped centreline guides, intentionally hidden from renders.
- 10 and 10B: rail-side components and unioned running rails/ballast. The railhead, web, foot and moving-tongue regions are distinct editable meshes.
- 11 and 11B: turnout mechanisms, single-grid bearers, buffers, checkrails and crossing fastenings.
- 12–14: mapped full-size platforms, furnished shelters and footbridges/stairs.
- 15–16B: OHE/signals, drains and rail-clear service/cable routes.
- 17–23: surroundings, operational furnishings, trilingual signs, platform paving and service-side kiosk details.
- 80: lift-off room ceilings and wing roofs. Hide only for a deliberate cutaway inspection; restore for exterior and normal interior views.
- 90: review cameras and lighting.

## Camera route
01 overall campus;02 heritage/forecourt;03 entrance hall;04 booking hall;05 waiting lounge;06 washroom;07 office;08 longitudinal platform context;09 island;10 turnout overview;11 service fan;12 full-yard top;13 footbridge;14 back-of-counter equipment;15 frog close-up;16 roof-off furnished building;17 service-facing amenities cluster.

The booking-room preview is retained from an earlier saved checkpoint with its exact blend SHA256 in the image sidecar. Later changes to distant pointwork/ballast do not invalidate that component preview. Each newly rendered image records its actual source hash and any deliberate presentation exclusions. A camera-local Eevee test, if delivered, is explicitly distinguished from the complete-scene Cycles views.

## Editing
`source/mapped_geometry.json` is the explicit editable map input. The hidden09 guide curves make the mapped route geometry inspectable in Blender. To propagate route edits into the unioned rails, edit the map data, regenerate`running_rails_mesh.json` with the documented preprocessing script, and rebuild. Direct mesh editing remains possible in the blend.

All GLB exchange parts use the same world origin and metre units. Import together at identity transforms. glTF uses Y-up; the exporter handles Blender's Z-up conversion. Procedural grain/bump materials may simplify to base colour/roughness in another application. The authoritative blend retains the richer node materials, editable sources and packed signage/font resources.

## Important boundaries
The model is a detailed visual reconstruction. It is not a 2022 measured as-built, approved point design, train-clearance study or navigable safety simulation. Exact hidden room plans and many fixtures are reconstructed. R01–R46 labels are review keys tied to OSM way IDs, not verified operating road numbers. No rolling stock is present.
