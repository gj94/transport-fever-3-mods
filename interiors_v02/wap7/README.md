# WAP-7 detailed cab interior pass v02

Editable visual prototype with **two complete cabs**, preserving the original white/red exterior, two bogies and six axle pivots. This is not a finished or game-tested Transport Fever 3 mod.

## Files
- `WAP7_interiors_v02.blend`: editable complete locomotive with preview cameras
- `WAP7_interiors_v02.fbx`: complete asset interchange, excludes preview cameras/lights/studio
- `textures/`: original procedural instrument images, referenced relatively and embedded in FBX
- `source/WAP7_prototype.blend`: unchanged baseline master, used for reproducible build
- `build_interiors.py`, `make_instrument_atlas.py`, `verify_export.py`: rebuild and verification
- `render_remaining.py`: quick cutaway/exterior/second-cab QA renders from the saved master
- `render_cutaway.py`: final clean furniture/floor cutaway, hiding shell and wall/ceiling fixtures for presentation
- `validation.json`, `fbx_validation.json`: evaluated geometry and fresh-import checks
- `WAP7_onboard_A.png`, `WAP7_onboard_B.png`: previews from both cabs
- `WAP7_cab_review.png`, `WAP7_cab_cutaway.png`: desk overview and separate presentation cutaway
- `WAP7_exterior_regression.png`: complete exterior review

## What changed
Both ends have formed grey desk housings, dark slanted control plates, analogue-style meter details, generic textured pressure gauges and diagnostic display, switches and colored controls, lever boots/handles, assistant desk, three pedals, adjustable blue vinyl crew seats, rubber flooring, rear bulkhead and internal access door, roller blinds, ceiling lining/duct/lighting and small equipment cover. These are static visual parts, not a simulated working cockpit.

The original closed body had opaque window plates. Actual boolean cab cavities and window openings now allow a cabin view. Existing slab-like rubber surrounds were replaced with hollow edge trims; clear transmission glazing replaces opaque blue-metal glazing. Exterior silhouette, livery, underframe, roof machinery and running gear are retained. The original dimensional tolerances continue to apply (see baseline documentation in repository).

## Reference and interpretation
Actual reference pixels inspected: WAP7 without seats in factory, published by India Rail Info:
https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/5/9/4/1593594/16557400/wap7seatless134598.jpg

Observed: continuous grey desk; asymmetrical dark instrument plates; left rectangular analogue meters and clustered colored controls; small green central display/keypad; assistant-side panel; three pedals on an inclined footboard; central lower service cabinet; heavy windshield trim; rolled blinds; ceiling equipment. The original photograph is a reference only, is not used as a texture and is not distributed in this package.

Supplementary primary equipment list: Indian Railways procurement document, WAP7 cab equipment and assembly items:
https://indianrailways.gov.in/railwayboard/rb/corrigendum/1731932781388_Corrig%20No-4_Bid%20Doc%20Ver-1_%20Revised%20Spec_Anned-13_Annex-14.pdf

No specific locomotive number, production batch, exact operational layout or engineering certification is claimed. Seats, rear bulkhead/door, concealed desk support, ceiling light/duct dimensions and pressure instrument arrangement are provisional visual interpretations. The reference has no seats, so seat upholstery, suspension geometry and placement are approximate. Instrument faces are original generic visual art with no invented legible safety labels, exact calibration or functional state claims. The two cabs share the same artistic arrangement. A locomotive-specific survey would be needed to establish every control, gauge and dimension exactly.

## TF3 scope
`CAB_A_ONBOARD_PREVIEW` and `CAB_B_ONBOARD_PREVIEW` are Blender CAMERA objects for framing only. They are excluded from FBX. TF3 camera configuration, camera switching, passengers, cab behavior, animations, importer/material conversion and runtime integration are **not implemented or tested**. No playable/functional cab claim is made.

## Rebuild
From this directory, run:

    python make_instrument_atlas.py
    blender -b -t 2 --python build_interiors.py
    blender -b -t 2 --python verify_export.py

Blender 4.3.2; CPU Cycles; denoising OFF; two threads. Source path can alternatively be supplied after `--`. Small instrument details use original textures; this remains an editable high-detail master. Mesh consolidation, normal-map baking, texture atlasing, LODs and game-specific validation are future production steps.

## Geometry accounting
Evaluated mesh triangles: 165,124 (baseline 117,220), net increase 47,904. The interior collection contributes 40,320 triangles; hollow trims and actual cut shell account for the remaining change. The FBX also converts the original exterior text objects to geometry, so its triangle count is higher than the mesh-only master count. Final fresh-import totals are in `fbx_validation.json`.

The reference geometry remains deliberately editable (478 interior collection objects, including the two cab roots). This is not a final runtime draw-call or polygon budget.

## Verification and review notes
- Fresh Blender FBX import preserves both bogie roots, all six axle roots and both new cab roots
- Both original instrument textures are embedded in FBX and packed in the Blender master; fresh import resolves 1024×1024 gauge and 512×256 display images
- No non-finite mesh vertices, preview cameras or presentation lights were found in FBX
- Exterior measured extrema remain X ±10.281 m, Y ±1.59169 m, Z −0.024 to 4.265 m; axle heights remain 0.546 m
- The instrument housings, flat gauge/display faces and relative texture portability were corrected after first-render inspection
- CPU Cycles renders intentionally retain some sample grain because denoising is disabled
- Original source-master SHA-256: `8431ae0c654a5fd3f5486fd5ebf503a69e25ef3c4d582b97504973c44939d548`

Final review images use 64 samples for the main cab views, 32 for cutaway/exterior and 16 at 70% resolution for mirrored cab B. The full build script renders all views at 64 samples; `render_remaining.py` reproduces the faster QA variants.

The final cutaway intentionally hides the body shell, cab wall/ceiling fixtures and exterior/studio rail detail. Those parts remain present and visible in the saved full master. To reproduce that exact presentation image, run `blender -b -t 2 --python render_cutaway.py`.
