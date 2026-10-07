# Full-size authoring component API

`prototype_dimensions.layout_for(kind)` combines exact car datums with `interior_layout.layout_for(kind)`. The prototype scaffold creates the actual wall openings, root/control hierarchy, role-specific underframe volumes and exact-count PAX markers. Geometry components expose `apply(ctx)` and return JSON reports.

`ctx` includes kind, root, body, asset collection, material roles, output directory and `layout`. The layout provides pitch, body limits, floor, bogie centers, cab/windshield datums, door/window records, saloon/service zones and individual seat poses.

Component order is exterior, end-cap closure, running gear, roof equipment, 22CB switchgear, pantograph microhardware, passenger interiors and cab. Names use VB02_EXT, VB02_END, VB02_GEAR, VB02_ROOF, VB02_VCB, VB02_PM, VB02_INT and VB02_CAB prefixes. Components replace only their owned visual geometry. Original logical names remain recognizable; prototype transforms deliberately differ from compactv01.

All dimensions are metres, +X forward, Y lateral, +Z up, railZ0. Common mesh functions use world coordinates unless local=True is specified. Axle-local wheel/brake geometry remains distinct from bogie-local fixed suspension. Actual detailed passenger chairs are linked meshes parented to individual PAX controls, with unit scale.

Source geometry/materials are editable and image-free. Procedural shaders need explicit baking/adaptation for another renderer or game. The seven car files are the export boundary; linked assemblies and transient render scenery are review assets. Runtime conversion, LODs, independent per-car controls and character-fit checks are separate work.
