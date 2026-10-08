# Ernakulam Junction · full station v02

A substantially expanded, editable no-trains station scene. The recognizable white/cobalt2017 west facade is retained; the compact v01 display has been replaced by full mapped platform/yard spans, two furnished entrances, deep interior equipment, long canopies, covered bridges, connected rail routes and detailed railway infrastructure.

## Open
Open `ERS_full_station_v02.blend` in Blender 4.3+. Units are metres. All 11 sign images are packed. Collections separate architecture, interiors, platforms, tracks, pointwork, canopy, bridges, east entry, OHE, services, context and close-range detail. Meshes use descriptive names; repeated track components are batched into editable per-route meshes.

## Evidence and scope
This is explicitly a 2017 photo-derived architectural baseline combined with current-map-derived mixed-date yard geometry, plus evidence-informed reconstructed interiors and hardware. It is not a surveyed 2017 as-built, engineering/interlocking model or2026 redevelopment asset. See `SOURCES.md`, `COVERAGE.md`, `DIMENSIONS.csv`, `track_network.json` and validation reports.

Mapped platform spans: PF1~647m, PF2/3~640m, PF4/5~615m, PF6~434m. Track clipping envelope 1.36 km, retaining both station throats. Exact modeled rail gauge 1.676 m. Six platform faces on four bodies,43 retained map paths, 50 shared-node branch hardware assemblies. The separate ERSD coaching/marshalling depot is not silently relocated into this station.

## Reproduce
From this folder:

    blender -b -t 4 --python build_ers_full.py
    blender -b -t 4 --python render_review.py
    blender -b -t 4 --python export_asset.py
    blender -b -t 4 --python validate_asset.py
    python make_coverage_plan.py

The builder reads `add_details.py`, sign textures and filtered OSM JSON locally. It needs no online fetch or external blend. `make_signs.py` regenerates typeset identity textures when Pillow/RAQM and Noto fonts are available; supplied textures are already usable. Render path uses CPU Cycles, maximum 4 threads, no OIDN; final review uses 64 exterior / 128 interior samples.

## Review
`renders/01` architecture;02 ticket hall;03 waiting;04 operational platform;05 mapped pointwork;06 aerial;07 full yard top-down;08 east hall;09 sanitary interiors;10 bridge;11 reconstructed store/office;12 labelled vector coverage diagram. Review images contain no trains. The editable model contains additional rooms/components beyond what each camera can see.

## Rights
No new open-source licence is granted to generated scripts/scene/artwork/renders. Photography and OSM reference/data attribution and applicable licences are documented separately in SOURCES.md. No official endorsement or survey accuracy is claimed.

### Recreate the global rail-solid preprocessing
The supplied `geometry/rail_solids.json` is sufficient for every Blender rebuild. To regenerate it, use Python with Shapely2.2.0 and Pillow, then run `python prepare_rail_solids.py` and `python verify_rail_geometry.py`. The source computes a global union of all 43 mapped route-head footprints, subtracts every 45 mm route flange channel, partitions non-overlapping tapered blades, and triangulates actual polygon holes. Blender removes the obsolete local rail/casting objects before loading these global solids. `geometry/rail_geometry_validation.json` tests the actual generated mesh footprint and plain-track gauge sections; it explicitly skips multi-route sections that are unsuitable for a plain-track gauge measurement.

### Export appearance
The packed `.blend` is the editable appearance master. The GLB carries geometry, original sign textures and supported PBR values; Blender-specific procedural weathering/noise may appear as simpler base materials in other viewers.

The camera/file name 11_Service_workshop is a legacy asset label. Its content is a reconstructed storage/office interior with shelves and workstations; no verified mechanical workshop machinery layout is claimed.

For the saved architectural view, use camera 01_West_architecture (Numpad 0 in Blender). The other named cameras cover interiors, platforms and pointwork. Hide the presentation collection when framing only editable geometry.

Mapped platform spans are polygon extents, including tapered ends. They are not surveyed usable boarding lengths or coach-capacity certificates.

A lossless transport copy, `exports/ERS_full_station_v02.glb.gz`, reduces the GLB download size. Decompress it with gzip,7-Zip or an equivalent archive tool to recover the exact GLB; `exports/export_manifest.json` records both hashes. The packed Blender scene remains the editable master.
