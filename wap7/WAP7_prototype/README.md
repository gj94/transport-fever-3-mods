# Indian Railways WAP-7 • detailed visual prototype

Original, procedural Blender model for review and further asset development. This is **not a finished or game-tested Transport Fever 3 mod**.

## Deliverables
- `WAP7_prototype.blend`: editable master with named parts, materials and presentation scene
- `WAP7_prototype.fbx`: geometry interchange export, asset only (no track, lights or studio)
- `WAP7_preview.png` and `WAP7_cab_detail.png`: rendered review views
- `build_wap7.py`: reproducible creation script for Blender 4.3.2
- `geometry_report.json`: source geometry counts and animation pivot names

## Basis and dimensions
Meters. Longitudinal X, lateral Y, vertical Z. Rail contact height Z=0. Two three-axle bogies. Wheels roll around local Y; bogies pivot around local Z. Nominal references: length over couplers 20.562 m, maximum width 3.152 m, locked-down pantograph height 4.255 m, gauge 1.676 m, new wheel tread diameter 1.092 m, bogie wheelbase 3.700 m, total wheelbase 15.700 m. Bogie center spacing is derived as 15.700 − 3.700 = 12.000 m. Equal 1.850 m axle spacing is an initial visual-model assumption pending factory drawings.

Primary dimensional source: North Western Railway Working Time Table 2025, Technical Data of Electric Locomotives, PDF page 166 (zero-based page 165):
https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf

Shell finish reference (RAL9003 white with red border):
https://clw.indianrailways.gov.in/uploads/FINAL%20DRAFT%20CLW-MS-3-152%20ALT-13.pdf

## Photographic reference
Both images were inspected visually before model creation. Photos are references only; neither is projected onto the mesh or included in the delivered geometry. Original geometry and procedural materials are used.
- Historical Trains, WAP-7 Locomotive outside Mumbai Central Passenger station, 20 May 2023, CC0: https://commons.wikimedia.org/wiki/File:WAP-7_Locomotive_outside_Mumbai_Central_Passenger_station.jpg
- GMO WAP 7 30544: https://commons.wikimedia.org/wiki/File:GMO_WAP_7_30544.jpg (consult the linked file page for authorship and license)

## Interpretation and limitations
Generic clean white/red WAP-7. No actual locomotive number, shed or specific production revision is claimed. Cab rake, roof shape, grille locations, doors, safety guards, buffer/CBC forms, brake hoses, suspension, transformer enclosure and electrical equipment are visual approximations from perspective photographs, not engineering-certified parts. The front and rear are mirrored; side ventilation is deliberately regularized. English class and railway labeling is a placeholder for a future selected livery. The preview shows the pantographs folded. Geometry is physically separated but no complete animation rig or keyframed animation is supplied.

This detail-rich master is deliberately not a performance-ready game asset. It has many individually named objects. Next production steps are variant approval, close-up dimensional/reference refinement, UV atlas and baking, consolidated meshes, normal and roughness maps, LODs, collision geometry, texture compression, game-specific materials/configuration, animation integration, and actual TF3 importer/runtime verification when a supported pipeline is available. No claim is made about TF3 compatibility, official SDK support or final polygon budgets.

Presentation rail and sleepers belong to `PRESENTATION_ONLY`, which is excluded from FBX. The Blender master includes non-applied bevel modifiers; FBX evaluates modifiers. Keep this master for editing. No downloaded executable or add-on is required.

## Verification results
Blender 4.3.2 opened and saved the master; the FBX was imported into a fresh Blender scene. All six axle pivots and both bogie pivots survived. The FBX contains 2,117 objects (2,107 meshes including converted labels); no presentation floor, track, lights or camera is included. Master evaluated geometry has 117,220 triangles. Small detail parts remain separate for easy editing, so object count is intentionally high and must be consolidated for runtime use.

Measured evaluated envelope: length 20.562 m; width 3.183 m; highest point 4.265 m above rail contact. Small accessories currently protrude 31 mm beyond the nominal width and 10 mm above nominal height. Wheel flanges extend 24 mm below the rail contact plane, intentionally. These are documented visual-prototype tolerances, not engineering accuracy claims. Axle centers are X = ±4.15, ±6.00 and ±7.85 m, Z = 0.546 m, and bogie center X = ±6.00 m. The master uses meters; FBX export declares X forward / Z up, and any downstream importer’s axis and scale interpretation must still be checked.

Both preview images were visually inspected. Final presentation uses 64-sample CPU Cycles rendering, without denoising. Rebuild with `blender -b -t 2 --python build_wap7.py`; optionally run `blender -b -t 2 --python qa_wap7.py` to regenerate the expanded geometry report and FBX re-import check.
