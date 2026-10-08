# TVC v02 review gallery

Start with the heritage and amenities views for detail; use the whole-yard plan and top-down view to inspect full-scale coverage. No geometry was shrunk to fit the frame.

## Exterior and platform detail
- `renders/02_Heritage_forecourt.png` — photo-derived heritage identity, expanded wings, ramps/steps and forecourt.
- `renders/17_Platform_amenities_service_side.png` — actual open kiosk with stock, tea urn/cups/menu, water cooler, taps, bins and canopy hardware.
- `renders/13_Footbridge_detail.png` — bridge/stairs, shelter openings and platform links.
- `renders/11_Maintenance_yard.png` — distinctive service fan and reconstructed maintenance facilities.

## Furnished interiors
- `renders/04_Booking_hall.png` — counters, grilles, queue guides, signage and working-side equipment. Cycles component preview; visible grain remains.
- `renders/05_Waiting_lounge_local_eevee.png` — sofas, chrome feet, cove lighting, wall finishes and television informed by a 2017 Southern Railway interior photograph; floorplan reconstructed.
- `renders/07_Station_office_local_eevee.png` — desks, monitors, individual keyboard keys, mouse, forms, filing and duty information.
- `renders/06_Washroom_local_eevee.png` — actual toilet/cistern within an open cubicle.
- `renders/18_Washbasin_detail_local_eevee.png` — shaped basin, tap, mirror and supporting vanity.
- `renders/16_Furnished_building_roof_off.png` — deliberate roof-off view of the furnished room arrangement.

## Full railway coverage and pointwork
- `renders/00_Labelled_yard_coverage.png` and `TVC_track_coverage_plan.pdf` — R01–R46 review keys mapped to OSM ways. R labels are not operational road numbers.
- `renders/12_Full_yard_top.png` — complete scene, true model proportions.
- `renders/01_Overall_full_station.png` — whole 1.64 km campus envelope. The distant viewpoint intentionally shows extent, not close detail.
- `renders/15_Frog_closeup.png` — pointed crossing, 45 mm flange channels, checkrails, clips, timber bearers and filtered ballast.
- `renders/rail_geometry_diagnostic.png` — generated rail-head plan geometry, separate from the beauty renders.

## How to read provenance
Each Blender render has a matching JSON file with its actual source blend SHA256 and renderer. Accepted component previews can come from earlier checkpoints; hashes are retained honestly rather than rewritten to match the latest model. Unrelated later changes do not imply those pictures are exact whole-scene renders of the final file.

Camera-local Eevee interior previews temporarily hide the distant yard/urban collections listed in their JSON sidecars. Walls, room fixtures and nearby station geometry remain; the saved blend itself retains the complete station. The roof-off image explicitly hides only the named lift-off roof/ceiling collection. Exterior/full-yard views render the complete scene. There are no image-generated or photographic stand-in renders.

All room plans and hidden structural detail remain reconstructions. Read `MODELLING_PLAN.md`, `README.md` and `FINAL_QA.md` for evidence limits.
