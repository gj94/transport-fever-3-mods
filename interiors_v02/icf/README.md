# Conventional ICF 72-berth sleeper — interior v02

Detailed visual prototype for further railway-game asset work. **Not a tested Transport Fever 3 asset.** No game metadata, runtime passenger binding, LODs, collision mesh, animation, or texture baking is provided.

## Files

- `icf_sleeper_interior_v02.blend`: complete coach with editable mesh objects, preserved bogie/axle hierarchy, authoring locators, and studio cameras
- `icf_sleeper_interior_v02.fbx`: coach and locators; studio excluded
- `refine_icf.py`: reproducible Blender 4.3.2 build, export, QA and render script
- `source/icf_sleeper_prototype.blend`: untouched original input for exact rebuilds
- `qa.json`: actual geometry counts and automated regression results
- `passenger_aisle.png`, `passenger_bay.png`: full-shell passenger views, no cutaway geometry hiding
- `cutaway_overview.png`: explicitly staged roof/near-wall removal for spatial inspection only
- `exterior_regression.png`: full exterior after the interior pass

Run from this folder with Blender 4.3.2:

    blender -b -t 2 --python refine_icf.py

An optional input file can be supplied after `--`. The default input is relative to this script. CPU renders use two threads, 64 samples, no denoising. Render lights are authoring aids and excluded from FBX.

## Layout and configuration

Nine bays each retain six transverse berth references and two longitudinal side berths: 72 total. This is the **daytime configuration**: 18 middle cushions are folded upright to form lower-seat backrests. They are present, named and numbered; they are not 18 additional horizontal sleeping surfaces in the displayed state. There is no folding animation or night-state rig.

The main side aisle is between the transverse berth ends and longitudinal side berths. Nominal clear width between hardware is about 0.53 m. The source's 1.71 m bay pitch and window positions are preserved; fitted transverse cushions are 1.77 m long and side cushions 1.57 m long. These dimensions are **prototype compromises**, not claimed as surveyed standard ICF furniture dimensions. A dimensionally exact furniture replacement would require revising the original bay/window grid, outside this preservation pass.

The pass adds padded blue vinyl cushions, upright backrests and hinge hardware, steel berth pans and supports, shared bay partitions, ladders, under-seat luggage racks, curved interior ceiling, caged fans, fluorescent fixtures, finished floor, wall lining aligned with existing barred/shutter apertures, window guides and handles, vestibule/entry rails and surfaces, and simplified sealed toilet compartments.

`BERTH_01` through `BERTH_72` empties record berth references. `PASSENGER_SEATED_01` through `PASSENGER_SEATED_72` empties are proposed daytime seating reference positions, three on each transverse lower bench and two on each side lower bench. They are **authoring locators only**, not tested runtime seats; occupant clearance and game-specific facing/animation bindings remain to be implemented. All are children of BODY.

## Evidence and original modeling

Sources were viewed as image pixels, not solely search snippets. Public reference photographs were used for observation only, not copied into textures or redistributed with this model.

- [Seat 61, India guide](https://www.seat61.com/India.htm), Sleeper Class section; [interior photo](https://www.seat61.com/images/India-sleeper-class.jpg). Observed upright blue-grey backrests, upper berth undersides, open lower bay floor, pale wall panels and metal end ladders
- [V. K. Saxena, Types of Passenger Coaches for Different Services](https://www.aitd.net.in/pdf/7/9.%20Types%20of%20Passenger%20Coaches%20for%20Different%20Services-%20VK%20Saxena.pdf), slide 22. Inspected illustrated II Class Sleeper plan: 72 persons, six transverse berths per bay, foldable middle berth, no compartment doors, two shorter longitudinal berths across aisle, toilets at ends
- [Sleeper bay photograph by Lee Charlton](https://media.assettype.com/deccanherald%2F2025-11-01%2Fiq2g7mbe%2FiStock-1748638290.jpg), viewed for the two-panel side lower cushion, folded backrest proportions, metal ladders, sill and hardware; copyrighted reference, not included in this package
- Original source model: [transport-fever-3-mods](https://github.com/gj94/transport-fever-3-mods/tree/7b6b23da96b839751c31faae5160f5a49e0424c1/icf/icf_sleeper), exact commit `7b6b23da96b839751c31faae5160f5a49e0424c1`

Specific fixture counts, colors, trim dimensions, fan implementation and furniture hardware are interpretive approximations. No unseen mechanisms, wiring or inaccessible toilet fixtures are modeled. Vinyl and floor grain use original procedural noise, not image textures.

## Preservation and checks

The original floor, external shell, roof, windows/shutters, exterior lettering, underframe, bogies and axles are retained. Only simplified interior berths/partitions/ladders/lamps and the original unbroken saloon end bulkheads are replaced. The end bulkheads now have an aisle portal rather than blocking access.

The build checks all cushion AABBs for overlap above a 2 mm tolerance; intended hardware contacts are outside this test. It hashes protected original mesh coordinates, topology, world transforms and parent identity, and asserts zero changes. Empty transforms are also compared. This is a geometry preservation check, not comprehensive game or structural validation.

The final saved Blend has all complete asset geometry visible. Cutaway render visibility changes are restored before saving. All views use the same furniture geometry; the passenger views do not hide flaws by removing walls or berths.

FBX round-trip is checked by `verify_fbx.py`; procedural micro-grain is Blender-specific and standard FBX materials carry base appearance only.

### Measured result

- 266,335 final asset triangles; baseline 217,230; growth 49,105 (22.6%)
- 1,215 protected original objects: zero geometry/transform/parent changes
- 72 cushion components, 72 berth reference empties, 72 daytime seated reference empties
- Zero cushion-AABB overlaps exceeding 2 mm
- FBX reimport: 3,065 objects, 2,913 meshes; no studio cameras/lights exported
- Bogie pivots remain parented to root; each axle remains parented to its original bogie
- Unobstructed 15.6 m eye-height aisle ray; interior floor has upward faces and ceiling has downward faces

These checks do not cover every possible hardware intersection, articulated state, passenger body shape, or game-specific import requirement. Render noise is visible because denoising was explicitly disabled under a 64-sample CPU budget.
