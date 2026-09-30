# Vande Bharat 2.0 compact chair-car modelling handoff

## Current TF3 integration — pack v1.0

Native conversion is included in **pack v1.0 (TF3 revision 14)** alongside fourteen ICF/LHB coaches. The installed revision 13 has identical vehicle content; v1.0 installation follows the running play test. Existing locomotive/trainset geometry, gameplay, rigs and the approved private horn are retained. All vehicle store/construction PNGs use straight side views. The modelling and QA below document these original authoring files. See [current installation, integration and remaining checks](../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

Original editable white/blue visual models for the team's Transport Fever 3 conversion workflow. **Modelling only.** No game resources, runtime scripts, compatibility claims, or changes to the existing conversion tools are included.

## Open first

- `cars/VB_DTC.blend`: outward-facing +X driving trailer, cab and 40-seat saloon
- `cars/VB_TC_EC.blend`: 40-seat executive trailer with live pantograph
- `assemblies/VB_8_car.blend` and `VB_16_car.blend`: complete linked-car review assemblies
- `renders/nose.png`, `interior.png`, `cab.png`, `formation_length_proof.png`
- `assemblies/VB_8_formation.json`, `VB_16_formation.json`: exact placement and measured extents
- `qa/fbx_roundtrip.json`: fresh Blender import checks for every supplied FBX

The assembly scenes link `../cars/` through relative paths. Keep the folder tree together. They are layout/review scenes, not a single train asset to convert. Editing a linked type changes all instances of that type; the converter should instantiate each source car and its controls independently.

## Deliberate compact dimensions

The reference train is approximately 192 m / 384 m for 8 / 16 cars using the official general 24.000 m over-coupler car figure. These models are **not 1:1-length replicas**. Each has a 19.375 m spacing span, approximately 80.729% of that general reference length. Saloon bays and bogie placement have been redesigned rather than uniformly scaling the entire train.

| Dimension | Reference / basis | Model |
|---|---:|---:|
| Nominal car coupling pitch | 24.000 m general manual figure | 19.375 m |
| Main body width | 3.240 m | 3.240 m |
| Height above rail | 4.140 m general figure | Roof HVAC body 4.140 m; grille tips 4.149 m |
| Gauge | 1.676 m | 1.676 m |
| New tread diameter | 0.952 m | 0.952 m |
| Bogie pivot centres | 14.900 m | 11.700 m, deliberate compaction |
| Bogie wheelbase | 2.700 m secondary corroboration only | 2.700 m, provisional |
| Full width including fixed thresholds | not asserted | 3.460 m |
| Lowest wheel flange | not a rail-contact error | −0.028 m |

Real rolling tread contacts rail Z=0. Wheel flange tips lie below that plane as intended. Gauge refers to track geometry, not the total wheel/axle width.

The actual complete visible lengths, measured from transformed mesh instances, are **155.737530 m** and **310.737530 m**. Outer spacing-datum spans are exactly 155.000 m and 310.000 m. The 16-car visible envelope has **9.262470 m** total margin under 320 m. See the manifests for full precision and final evaluated bounds. These are straight authored-pose dimensions, not curve-clearance certification.

Both DTC outer spacing datums lie inside the closed nose fairing. They represent the stowed rescue-coupler/formation-spacing datum, **not an exposed knuckle face**. Nose tips project approximately 0.368765 m beyond each outer datum. Coupling whole complete trainsets nose-to-nose is not supported by this closed-fairing model.

Internal semi-permanent couplings and gangways use matching spacing planes. Main body end clearance is 0.715 m. Bellows lips retain a 0.025 m expansion gap; floor bridges retain 0.035 m. There are no opaque full-width end plates across the central passenger passage. This handoff has no collision simulation, articulation/compression logic, or runtime passenger path validation.

## Car family and formations

| Source | Compact seats | Role / visible distinction |
|---|---:|---|
| DTC | 40 CC + 2 drivers | Sloping cab nose, desk, cab side/front glazing, one rear gangway, batteries/compressor |
| MC | 60 CC | Powered bogies/motors, traction converter cabinets, side cooling grilles |
| MC2 | 60 CC | MC family with an additional electrical changeover cabinet |
| TC_CC | 60 CC | Pantograph, insulators/VCB/bus, underslung transformer and auxiliary converter |
| TC_EC | 40 EC | Same trailer electrical role with wider 2+2 seating |
| NDTC_EC | 40 EC | Non-driving central EC car, batteries/compressor/reservoir, no pantograph |
| NDTC_EC2 | 40 EC | Handed pantry and battery/compressor placement, no pantograph |

8 cars, 420 compact passenger seats:

`DTC – MC – TC_EC – MC2 – MC2 – TC_CC – MC – DTC`

16 cars, 880 compact passenger seats:

`DTC – MC – TC_CC – MC2 – MC – TC_CC – MC2 – NDTC_EC – NDTC_EC2 – MC2 – TC_CC – MC – MC2 – TC_CC – MC – DTC`

The 16-car ordering is confirmed by the railway operating certificate linked below. Pantographs are on cars 3, 6, 11 and 14; the EC pair is central at 8 and 9. The 8-car official circular confirms two DTC, four MC, one CC TC and one EC TC. The two-end-basic-unit ordering and EC at car 3 are the selected interpretation, not a claim of a factory-confirmed numbered rake. Pantographs are on cars 3 and 6. There are no intermediate driving cabs.

Positive X is the front of each source asset. First-half car instances are rotated 180° about Z; second-half instances are 0°. Both end cabs therefore face outward. Mirrored intermediate handedness is an authoring choice; exact production equipment hand and all revision-specific details have not been certified from factory drawings.

CC uses 3+2 seats, EC 2+2. Layouts are shortened to 12 CC rows / 10 EC rows / 8 DTC rows. These counts deliberately differ from the reference nominal 78/52/44. Seats, armrests, back trays, racks, bulkheads, service/pantry volumes and cabin controls are actual geometry. Window/door/cab panes have a closed 6 mm inward thickness, avoiding single-backface total internal reflection from inside. All glazing is separate and is backed by open wall/door apertures rather than painted opaque window panels. Interior saloon doors are clear glazing in the authored closed pose.

## Conversion contract

Reviewed against repository main commit `45f612e6a236e2d9e0742a82dab13d35b1736b15`.

- Metres, identity root, +X forward, Y lateral, +Z up, rail Z=0
- One parentless `VB_<type>_ROOT` empty per per-car asset; every asset object is below it
- Root-parented `COUPLING_FRONT` and `COUPLING_REAR`; local X ±9.6875, Z 1.02. Rear anchor's outward local X points backward
- `BOGIE_A_YAW_Z`, `BOGIE_B_YAW_Z` at X ±5.85, Z .71
- Four `AXLE_<A/B>_<1/2>_ROLL_Y` children at bogie-local X ±1.35, world Z .476
- Wheels are children of axle empties; axleboxes/dampers/frame are children of bogies
- Four separate `DOOR_<L/R>_<1/2>_SLIDE` pivots, with local suggested open travel in custom properties
- `PAX_001...`: compact seated-character authoring roots, +X local facing. Cushion-top Z1.75; assumed posed hip offset .483 m gives root Z1.267. These are proposed CHARACTER ROOT transforms, not cushion/hip markers. The .483 m value was measured previously for WAP7 driving_upright, not independently established for the sitting animation. Passenger Z is provisional: the converter consumes PAX local transforms directly and must fit the actual sitting character before use
- `DRIVER_001/002` only are proposed seated CHARACTER ROOTS, not cushion/hip points. `CAB_EYE_CAMERA_REFERENCE` is a view-reference marker, not a seat or runtime camera
- Headlamp/marker lenses and light anchors are separate from shell geometry
- Every moving pantograph section is under its own persistent empty pivot

The current converter merges meshes by nearest retained empty and material. This hierarchy is intentional. The original source handoff left native mappings to conversion. The current converter maps VB driver/passenger seats, compartment indices, door tracks and pantograph state; full animated character fit and door triggers await runtime checks. Functional lamp effects remain future work. Palette material names/diffuse colors and Principled BSDF values agree; transparent glass has Transmission Weight .96. There are no photographic textures or external image dependencies. No UV atlas, weathering atlas or authored LODs are claimed.

## Live and baked pantograph controls

Both trailer types have this hierarchy:

`BODY / PANTO_BASE / PANTO_CTRL / PANTO_LOWER_PIVOT / PANTO_ELBOW_PIVOT / PANTO_HEAD_LEVEL_PIVOT`

Select `PANTO_CTRL`, set custom property `extension` from 0 to 1. Each standalone car's control is independent. The review assemblies share linked type data; create independent per-car instances for runtime animation.

- Base joint rail Z=4.000 m
- Lower/upper rigid lengths: 1.500 / 1.200 m
- Angle: 1° folded to asin((5.917−4.000−.032)/2.7), about 44.28° raised
- Joint local Y rotations: −θ, +2θ, −θ. Head stays level
- Contact strip top: 4.079122 m folded, 5.917000 m raised. Static folded-car bounds are not the animated pantograph envelope: conversion must account for the raised 5.917 m head in culling/bounds as appropriate
- Height relation: `h = 4.000 + 2.700*sin(theta) + .032`
- Desired height to extension: `(asin((h−4.032)/2.7)−theta_min)/(theta_max−theta_min)`, clamped to [0,1]

This regular-height articulated mechanism is an original visual approximation. The roof photograph used for detail study shows a high-rise variant; its exact high-rise geometry is not copied. No route-specific high-rise performance or real manufacturer dimensions are claimed.

`VB_TC_<CC/EC>.blend` contains live drivers. Drivers are not FBX-portable. `*_raised.fbx` is a static raised pose; `*_baked.blend` and `*_motion.fbx` contain rigid sampled animation, frames1–41 raise and41–81 lower at24fps. Blender's default FBX import introduces a +1 frame offset; validation checks imported frames2/22/42/62/82. Conversion should use these as motion examples, not blindly reuse Blender-only expressions as game triggers.

## Rebuild and validation

Use Blender4.3.2, run from any directory:

```
blender -b -t 2 --python build_vande_bharat.py
blender -b -t 2 --python validate_fbx.py
blender -b -t 2 --python build_assemblies.py
blender -b -t 2 --python render_views.py -- nose
blender -b -t 2 --python render_views.py -- interior
blender -b -t 2 --python render_views.py -- cab
```

The builder recreates its own outputs; back up edits first. CPU Cycles renders use2threads/24samples and denoising off. Some sampling grain remains. All render props/cameras are presentation-only and excluded from per-car exports.

QA covers finite geometry, root/pivot hierarchy, metric coordinates, seat counts, material/name consistency, exact spacing-plane coincidence, evaluated assembly extents, FBX pivot/coordinate preservation and static/animated pantograph heights. Independent review also sweeps moving pantograph geometry for roof-equipment collisions. Review reports identify their exact source hashes; later edits require retesting.

This remains a reference-informed compact visual prototype: nose fairing, door/window dimensions, equipment position, seat shape, pantry/toilet arrangement, lights, bogie details and pantograph hardware contain approximations. It has not been loaded into TF3 or its Model Editor by this modelling task. The cab review camera uses the proposed driver eye (6.43,−.73,2.48)m and a horizontal +X sightline with20mm lens; it is an authoring view, not a claimed runtime camera. No runtime animation, character-fit, light-trigger, wire-contact or curve test is claimed.

## Reference provenance

Reference images were inspected but are not redistributed. All supplied meshes and materials are original procedural constructions.

1. [CAMTECH Vande Bharat2.0 maintenance manual, September2022](https://rdso.indianrailways.gov.in/uploads/VBE_Trainset(V2)_Maintenance_Manual_Volume_II_Chapter1_Introduction_Draft(3).pdf), general dimensions/seating/electrical roles. Original layout drawing identifiers appear at pp29–34, but PDF image download failed in this environment; no claim of tracing those drawings
2. [South Central Railway operating certificate](https://digitalscr.in/bzadiv/circulars/misc_circulars/uploads/Vandebharat_GMsanction.pdf), authoritative16-car sequence
3. [North Western Railway5July2023 circular, hosted copy](https://st.indiarailinfo.com/kjfdsuiemjvcya24/0/6/9/2/5769692/0/commhq1764176322411285603.pdf), authoritative8-car inventory; hosted third-party mirror
4. [PIB launch photograph,30September2022](https://static.pib.gov.in/WriteReadData/Gallery/PhotoGallery/2022/Sep/H20220930118326.JPG), VB2 white-blue frontal livery and lamps
5. [BFG manufacturer project photographs](https://www.bfginternational.com/about-us/bfg-india), original Train18/VB nose, interior finishes and cab family. Earlier-program photos used only where consistent with VB2 references
6. [Cab photograph, Sameer2905,27December2023](https://commons.wikimedia.org/wiki/File:Cabin_of_Vande_Bharat_Express.jpg), dashboard/seats/glazing
7. [Second-generation EC interior photo](https://commons.wikimedia.org/wiki/File:Vande_Bharat_Executive_Chair_Car_interior_layout.jpg),2+2 layout, racks and headrests
8. [High-rise pantograph roof photograph](https://timesofindia.indiatimes.com/business/india-business/why-vande-bharat-express-train-is-being-modified-for-delhi-jaipur-route/articleshow/98860108.cms), roof detail arrangement only

No open-source license is granted by this handoff. Follow the repository's existing licensing arrangement.
