# Nagercoil Junction: full-size detailed reconstruction v02

Editable Blender railway environment, no trains or rolling stock. One Blender unit is one metre; broad-gauge rail inner faces are 1.676 m apart. This replaces the former short platform/track demonstration with an approximately 2.4 km-long site envelope and approximately 19.6 km of mapped/reconstructed rail-route geometry.

## Scope and evidence boundary
This is a **mixed-date, pre-final-remodelling visual reconstruction**, not an as-built survey or signalling plan. The retained heritage entrance derives from inspected January/October 2010 photographs. Platform outlines were mapped in 2021/2023; rail approaches include OSM edits through 2025. Furnished interior room arrangements, most equipment locations, connections missing from the map, pit-road assignments and point numbers are reconstructed. The proposed 2026 final yard is not silently presented as commissioned.

The platform arrangement is **side platform 1, terminal/bay 1A, and island faces 2/3**, not four separate through platforms. Two physical mapped platform polygons extend approximately 841 m and 564 m, including the bay-side extension. Source footprints and centreline geometry retain their metric extent; the yard has not been compressed for a hero view.

## What's modelled
- Heritage portico, shaped Tamil/Hindi/English roof lettering, side veranda, annex and forecourt
- Navigable booking hall, six ticket windows and clerk desks/computers, queue railings, waiting room seating/luggage racks, station manager and parcel offices
- Six toilet cubicles with opening doors, WCs/cisterns, four basins/taps/mirrors/waste pipes; electrical room and upper staff rooms with an actual stairwell
- Full platform bodies, clipped individual paving tiles, edge coping/safety stripes, corrugated steel shelters, trusses/purlins/gutters/downpipes, fans/lighting, benches, bins, water taps, kiosks, trolleys and signs
- Full mapped main, loop, siding, bay and depot track alignments with ballast, true-pitch sleepers, pads/clips, three-part rail sections, physical crossing gaps, reconstructed check rails/switch blades/motors/buffers
- Five long inspection-pit facilities with split supports and side walkways, watering hoses, goods shed/loading apron, furnished maintenance workshop, water towers
- Contact/messenger wires, droppers, lattice portals, insulators, colour-light signal equipment, cable troughs, open drains, fences, site roads and vegetation
- Fourteen review cameras covering architecture, interiors, bay, full yard, pointwork, pits and small details

## Files and reproducibility
- `NCJ_full_station_v02.blend`: editable, packed fonts; source scope in scene/collection metadata
- `exports/NCJ_full_station_v02.glb`: portable mesh export (rendered procedural textures simplify to base materials)
- `scripts/build_ncj_full.py`: deterministic build; uses `scripts/facade_heritage.py`, `assets/`, and `references/local_geometry.json`
- `scripts/render_ncj_full.py`: actual Blender render cameras
- `scripts/export_ncj_full.py`: GLB export
- `QA_BUILD.json`, `SOURCES_AND_UNCERTAINTIES.md`: actual inventory and evidence ledger

Run:
    blender -b -t 4 --python scripts/build_ncj_full.py
    blender -b -t 4 --python scripts/render_ncj_full.py
    blender -b -t 4 --python scripts/export_ncj_full.py

Camera navigation: use the named review cameras, or Blender walk navigation (Shift+backtick). Collections separate interiors, platform detail, trackwork, pits and electrical equipment. Roof slabs can be hidden for editing, but normal review views preserve roofs. Rendering is limited to four CPU threads; denoising is disabled because this Blender build lacks OIDN.

## Limits
No measured NCJ interior plan, authenticated contemporary yard drawing, exact signal numbering or verified current utility equipment positions were available. OSM is an open community map, not railway engineering authority. Supplemental pointwork is visual geometry, not simulation-ready interlocking or certified turnout design. Source photographs are not textures and are not redistributed in the publication package. No new licence is granted for generated assets; existing repository status is retained. OSM geometry retains ODbL attribution; see the source ledger.
