# Full-size source contract for a future converter

This revision does not update native TF3 resources. Do not silently substitute it for the compact source or reuse compact placement constants.

## Coordinate changes

- Root identity, metres, +X forward, Y lateral, +Z up; railZ0
- Car pitch24.000m; COUPLING_FRONT/REAR X±12.000m
- Internal mating anchors Z0.940m; DTC outer rescue-CBC nominal datum Z1.105m
- Bogie yaw pivots X±7.450m,Z0.710m
- Axles remain bogie-local X±1.350m, wheel center worldZ0.476m
- Floor topZ1.320m; cushion topZ1.750m; PAX/DRIVER rootZ1.267m is still an assumed posed-character-root convention, not a confirmed animation fit
- DTC driver centers X9.350m,Y±0.730m; authoring eye reference X9.390m,Y−0.730m,Z2.490m
- Door and PAX positions come from the full-size layout records, including asymmetric DTC/CC row exceptions

The coupling heights come from the primary drawings. The front DTC datum does not assert that the closed-fairing visual source can couple complete trainsets nose-to-nose.

## Geometry and hierarchy

The reusable seven-car files each have one root. New detail is grouped by physical component/material while remaining editable. Each actual passenger chair mesh follows its own PAX empty; export pipelines that previously discarded PAX empties must intentionally handle the chair transforms. Do not duplicate or drop these seat meshes when generating passenger-character transforms.

Wheel/brake-disc geometry rotates under axle empties; axleboxes/calipers/suspension remain under bogie empties. Passenger-door interior hardware follows the existing sliding pivots. Cab controls, seats, trays and WC doors are static visual geometry unless a later pipeline adds explicit animation.

The linked review rakes reuse type collections and share type-level pantograph controls. Runtime cars need independent controls.

## Pantograph

The power-end mounting placement and folded4.260m envelope are full-size-source updates. The raised5.917m contact target is an authored display target. The1.5/1.2m rigid linkage is still representative. Blender drivers are not portable game animation; bake or implement them deliberately, then repeat roof/wire/curve-clearance checks.

## Materials and performance

This is high-detail source geometry, with original node-based cloth/paint/metal/glass shaders and no photographic vehicle textures. A game pipeline needs material baking/adaptation, mesh optimization, LOD generation, culling bounds and fresh runtime tests. FBX alone will not preserve the shader graphs. The source's physical530/1128 seat counts do not authorize changing existing gameplay capacity, cost, speed or introduction-year settings.
