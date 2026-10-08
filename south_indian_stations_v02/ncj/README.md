# Nagercoil Junction: detailed full-size station v02

Editable Blender environment with no trains or rolling stock. One unit is one metre. Rail inner-face gauge is 1.676 m. Full mapped platform spans are approximately 841.6 m, including the side/bay extension, and 563.8 m for the island. The source-centreline network totals approximately 19.6 km inside a roughly 2.4 km-long site envelope; the yard is not compressed for presentation.

## Evidence boundary
This is a mixed-date, pre-final-remodelling visual reconstruction, not an as-built survey. The heritage entrance derives from inspected 2010 photographs; mapped platform outlines date from 2021/2023 and some approach edits extend through 2025. Interiors, most equipment locations, pit assignments and missing connections are reconstructed. The proposed 2026 final yard is not presented as commissioned.

The platform arrangement is side platform 1, terminal/bay 1A, and island faces 2/3. Two physical mapped platform bodies support these labels. Source polygons retain their full bounds, with building insets to prevent the platform slab from intruding into the reconstructed toilet/annex rooms.

## Included detail
- Photo-informed portico, shaped Tamil/Hindi/English signs, veranda, annex, weathered surfaces and forecourt
- Booking hall with six grilled ticket counters, pass shelves, clerk desks/computers/chairs, queue rails, timetable, clock, fans, lights and bins
- Furnished waiting room, station-manager and parcel offices, electrical room, upper staff rooms and an internal stairwell
- Six toilet cubicles with open doors, WCs/cisterns, four basins, taps, mirrors and plumbing
- Full platform bodies, individual paving/joints, edge coping, corrugated shelters, trusses, gutters, downpipes, lighting, benches, signs, water taps, kiosks, trolleys and fire equipment
- True-pitch sleepers, fasteners, three-part rails, full curved routes, buffers, source-fitted pointwork and explicit compound crossings
- Five excavated path-following maintenance-pit representations, watering hoses, a furnished workshop, goods shed/apron and water towers
- Connected OHE supports, contact/messenger wires, signal equipment, buried utility crossings, open drains, fences, roads and vegetation

## Main files
- `NCJ_full_station_v02.blend`: primary editable asset, packed fonts and separated collections
- `exports/NCJ_full_station_v02_GLTF.zip`: portable GLB; unzip before use. Procedural material textures simplify to base materials in this export
- `renders/`: reviewed Blender views; consult `RENDER_PROVENANCE.json` for exact source hashes and retained older views
- `references/NCJ_TRACK_COVERAGE_PLAN.svg`: zoomable source/coverage diagram, with a PNG preview
- `SOURCES_AND_UNCERTAINTIES.md`, `DIMENSIONS.csv`, `QA_FINAL_SUMMARY.json`: evidence, scale and verification

## Rebuild and render
Tested with Blender 4.3.2. Geometry finishing uses Shapely 2.2.0 installed for the Python used by Blender. Set `NCJ_SHAPELY_PATH` to a compatible installation, or place it in `.build_deps/shapely`. That dependency is needed only to rebuild, not to open the saved model.

Run from this directory:

    bash scripts/finish_ncj.sh

This performs the clean base build and all physical finishing passes, validates the scene and renders the three pointwork proof views. It uses the frozen JSON source geometry supplied here; optional extraction scripts require the original OSM download.

Render the final gallery:

    blender -b -t 4 --python-exit-code 1 --python scripts/render_ncj_full.py -- 01 02 03 04 05 06 08 10 17 18 19

Export the current scene:

    blender -b -t 4 --python-exit-code 1 --python scripts/export_ncj_full.py

Rendering uses four CPU threads and no denoising. The toilet view is a labelled cutaway with overhead material hidden only for review. Yard labels are a separate non-physical collection, disabled by default and excluded from the GLB. Named cameras and Blender walk navigation make the scene easy to inspect.

## Verification and limits
The final scene contains 7,947 objects and approximately 3.14 million vertices; see the final report for exact counts. Tests found no non-finite mesh coordinates or rolling stock. Six principal circulation rays and 18 sloping stair-body rays passed. Both footbridge flights have real canopy openings. Reconstructed ground-floor blocks have supporting plinths and entrance steps.

All 34 mapped junctions receive explicit treatment: 20 source-fitted simple turnout reconstructions and 14 simplified fixed/compound crossing treatments. These preserve mapped route relationships and clear flange channels, but are not NCJ fabrication drawings, movable-point mechanisms or a signalling/interlocking simulation.

OHE footing centreline clearance is at least 3.406 m. Five inferred pit assignments contain clear inspection sections of approximately 414 / 300 / 408 / 279 / 312 m. Utility crossings are buried rather than left as raised obstructions across tracks. No measured interior plan, certified current yard drawing or verified signal-number inventory was obtained.

Original reference photographs are not textures and are not redistributed. OSM attribution and font notices are retained. No new licence is granted for generated assets; existing repository status is unchanged.
