# ERS quality and reproducibility report

## Verified computationally
- Blender 4.3.2 source generated and saved, then reopened with `validate_ers.py`.
- Metric scene, one unit per metre.
- 2,047 scene objects; 2,009 base mesh objects; 25,236 base vertices. Evaluated bevels/curves add export geometry.
- 12 original sign textures packed in the `.blend`; no external file-image dependencies.
- GLB 2.0 export contains 2,041 mesh entries and 12 embedded images; no external buffer/image URIs; header length matches file size.
- No empty meshes, nonfinite vertices or inward-facing closed box geometry found.
- Two rail pairs checked at inner rail-head faces: 1.675002 m and 1.675000 m, within 0.01 mm numeric tolerance of nominal 1.675 m. This is a model-scale check, not an engineering measurement of ERS.
- Source scripts pass Python syntax compilation. Full build runs without needing the photographs or fonts because generated sign textures are distributed.

## Visual inspection / corrections
Actual 2017 source pixels were inspected before modelling: Shady59's frontage plus KannanVM's two November platform/bridge photographs. The incorrectly tempting interpretation of `Railway station.jpg` as a frontage photograph was rejected after visual inspection: it shows the footbridge and trackside.

First render review led to these corrections:
- Widened hero camera to include the entire facade.
- Flattened the cobalt entrance arch into a proper architectural fascia, replacing its initially pipe-like section.
- Opened canopy roof/purlins around the covered stair flight.
- Aligned the stairs to the bridge edge and opened the corresponding bridge guardrail/truss bay.
- Lowered platform camera under the canopy so platform furniture and catering stall can be seen.
- Changed front elevation to a wide 1600 × 400 frame.
- Slightly brightened daylight exposure.
- Corrected the right gallery to four small near-entry arched recesses and two broad curved-header bays after magnifying the 2017 photograph.
- Rotated the kiosk shopfront to face along the platform, and brought the platform camera closer.
- Lowered the architectural hero camera after parent review.

All four final camera renders have now been inspected at actual pixels. The hero/elevation show the accepted arched facade rhythm; the entrance detail shows legible multilingual identity and clock; the platform view includes the entire catering-stall frontage, stair flight, canopy structure and platform edge. Deep covered areas retain visible Monte Carlo noise at 64 samples; this is disclosed rather than described as denoised output. Root reviewed and accepted the revised architectural hero.

## Rendering
Four actual Blender Cycles camera views, 64 samples, four CPU threads. No AI-generated previews. The installed Blender build has no OpenImageDenoise support; denoising is disabled, so some noise remains in deep covered areas. Main frames are 1600 × 1000; elevation is 1600 × 400. No claim of denoised or photographic output.

## Known limits
This is a visual modular asset, not a surveyed full yard. Most dimensions and placements are photo-inferred or deliberately game-adjusted; see `DIMENSIONS.csv`. Back walls/roof depths, furniture and forecourt positions are artistic completion. Generic unbranded kiosk goods and simple palm meshes provide scale/dressing. There are no copied passengers, vehicles, trains, actual advertisements or proprietary photo textures.

Only one shortened platform body and two sample track lines are supplied. Platform count/length, turnout topology, operational signalling, electrical clearances, collision/LOD, navigation mesh, simulator compatibility, watertight single-body construction and real-world build safety are **not** certified. Curves and separate components are intentionally editable; glTF simplifies procedural shader noise into base materials. These limits are documented rather than filled with a fictional exact ERS layout.
