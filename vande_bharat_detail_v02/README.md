# Vande Bharat 2.0 full-size detailed source v0.2

> Immediate source-preservation checkpoint: editable generator code, references and documentation are backed up. The seven compiled car .blend files and their complete linked assemblies are still being uploaded. Rebuild with the scripts below until that upload is complete. Final gallery pending.

Editable, reference-informed **192 m eight-car and 384 m sixteen-car** white/blue chair-car rakes, using the nominal 24.000 m over-coupler car dimension. These are high-detail Blender authoring sources. The earlier compact v01 sources and the existing TF3 runtime pack remain separate and unchanged.

> Source checkpoint: the full-size source rebuild has been validated and is being backed up after an execution-environment interruption. The final rendered gallery is pending regeneration; this branch is not the finished main-page release.

## Open first

- [Eight-car linked assembly](assemblies/VB_8_car.blend)
- [Sixteen-car linked assembly](assemblies/VB_16_car.blend)
- [Driving trailer and detailed cab](cars/VB_DTC.blend)
- [Executive trailer with pantograph](cars/VB_TC_EC.blend)
- [Motor chair car](cars/VB_MC.blend)

Keep this folder tree together. Each assembly links the seven reusable `cars/` files through relative paths. Geometry and materials are editable; the model sources have no external image dependencies. Procedural fabric/paint shaders require baking or adaptation for a game export. No native TF3 conversion, optimization or runtime test is included here.

## Prototype dimensions and physical seats

The exact drawing callouts used are:

- Nominal car coupling pitch: **24.000 m**
- Intermediate body length: **23.100 m**
- Bogie-center spacing: **14.900 m**
- Bogie wheelbase: **2.700 m**
- Body width: **3.240 m**, gauge **1.676 m**, new wheel tread diameter **0.952 m**
- Floor above rail: **1.320 m**
- Normal saloon panes: **1.500 × 0.880 m**; emergency assemblies **1.580 × 0.900 m**, with a 765 mm saloon sill above floor
- DTC nominal front CBC datum: **1.105 m** above rail; internal semi-permanent mating datum: **0.940 m**
- General manual car-height reference: **4.140 m**; pantograph and roof-electrical envelopes are reported separately. Folded pantograph target: **4.260 m**

DTC nose-to-rear body length is called out as 23.328 m. The sculpted closed fairing follows a drawing-read tip near +11.78 m, behind the +12.00 m nominal front coupling plane. The actual final visible envelopes are **191.560 m and 383.560 m**, measured independently in [eight-car report](assemblies/VB_8_formation.json) and [sixteen-car report](assemblies/VB_16_formation.json), rather than equated to the nominal coupling spans. Straight-pose dimensions do not certify curve clearance or trainset-to-trainset coupling.

This revision restores physical passenger counts: **44 in each DTC, 78 in each ordinary CC car, and 52 in each EC car**. The DTC has its asymmetric row exceptions, a companion seat and wheelchair bay. The ordinary CC arrangement also includes end-row exceptions. Every passenger seat is an actual unscaled detailed mesh instance attached to its own marker; QA counts the chair meshes separately from markers.

The selected eight-car inventory totals **530 seats**; the sixteen-car formation totals **1,128 seats**. These are physical source-model counts, not changes to the existing game's normalized capacity settings.

### Formation evidence

The 16-car order follows the official 2022 system layout:

`DTC – MC – TC_CC – MC2 – MC – TC_CC – MC2 – NDTC_EC – NDTC_EC2 – MC2 – TC_CC – MC – MC2 – TC_CC – MC – DTC`

Pantographs are on cars 3, 6, 11 and 14; the EC pair is at 8 and 9.

The eight-car inventory supports two DTC, four motor cars, one CC trailer and one EC trailer. The supplied `DTC – MC – TC_EC – MC2 – MC2 – TC_CC – MC – DTC` order and handedness are a **disclosed selected arrangement**, not a factory-verified numbered 8-car rake. TC_EC combines the supported eight-car EC role with the 52-seat EC interior layout.

## Detailed model coverage

- Drawing-led nose profile, continuous paint/mask surfaces, separate closed laminated glazing, twin sealed LED capsule, teardrop marker pods, linked wiper arms, cab entry and rescue-fairing joints
- Drawing-informed full-length sidewall, passenger door and glazing stations; continuous rounded-aperture door leaves without overlapping corner faces
- End-positioned HVAC units with fans, guards, louvres, access panels and drains; DTC also has its separate cab AC
- Bolsterless running gear with two secondary bellows per bogie, double concentric primary springs, dropped-center frame, fixed axleboxes/control arms, yaw dampers, brakes, motors, cabling and piping
- Role-specific converter, transformer, battery, compressor, reservoir and water-tank equipment, with separate manufactured/service finishes
- Schunk WBL22.03-informed contact head: 1.800 m overall width, two 35 mm carbon strips at 390 mm centers, rocker boxes, formed flat leaf springs, carrier clamps, pneumatic strip-monitoring lines, flexible copper bearing shunts, horns and bolted open base frame
- Schneider 22CB-inspired stacked porcelain switchgear, separately routed live terminals, open earth contacts and under-roof mechanism case
- Curved end-cap closures above unobstructed gangway openings
- CC/EC shaped upholstery and distinct original woven/jacquard shaders, stitching, molded backs, trays, net pockets, grab handles, armrests, footrests, charging points and floor mounts
- Full-length luggage racks, translucent etched shelves, passenger-service units, ceiling access/perforation panels, information displays and continuous lighting
- Standard service rooms, pantry/electrical end zones, plus the DTC's **one** curved accessible-WC representation, clear rear entry and separate wheelchair/turning areas
- OEM-informed driver desk with readable original mesh graphics, gauges, controllers, microphones, communications hardware, seats, pedals, demister shelf, blind, rear-wall equipment and ceiling fittings

## Geometry and accessibility checks

The authored CC/EC armrest-clear aisles measure **0.530 / 0.541 m**. The DTC mesh audit checks a 1.500 m turning footprint, the 1.130 m doorway between WC jambs and the corridor past the curved WC. Detailed measurements and obstacle margins are in `qa/DTC_accessibility_mesh_clearance.json`.

These are checks of the supplied visual geometry, **not accessibility, railway or production-installation certification**. Door operating clearance, real wheelchair motion and actual game-character animation are not simulated. The closed WC leaf must be opened/removed in a presentation copy when inspecting the doorway.

## Authoring and converter contract

Metres, identity root, +X forward, Y lateral and rail Z=0 remain consistent. Logical root, BODY, coupling, bogie, axle, door, PAX, DRIVER and pantograph names remain recognizable, but **their longitudinal placements intentionally differ from compact v01**. Couplers now sit at X±12.000 m; bogies at X±7.450 m. Full mappings, heights and validation scope are in [conversion handoff](docs/CONVERSION_HANDOFF.md).

Wheels and brake discs follow axle controls; fixed suspension/calipers follow bogie yaw. Each chair follows its own PAX marker. The provisional seated-character root offset remains documented and needs a real character-fit check during conversion.

Preview lighting uses illuminated white front optics and unlit red lenses. Runtime direction-dependent train lighting is not implemented in these sources.

Linked assemblies share per-type authored controls. A converter must instantiate independent controls for each car. The pantograph preserves the original rigid linkage concept while moving it to the prototype power-end roof zone and adjusting the resting angle to the 4.260 m folded target. The 5.917 m fully raised contact target and the 1.5/1.2 m arm lengths remain an explicitly authored visual mechanism, not a certified Schunk kinematic reconstruction.

## Rebuild and render

Blender 4.3.2 is tested. From the repository root:

```sh
blender -b -t 4 --python vande_bharat_detail_v02/scripts/build_master.py
blender -b -t 4 --python vande_bharat_detail_v02/scripts/validate_sources.py
blender -b -t 4 --python vande_bharat_detail_v02/scripts/validate_pantograph_clearance.py
blender -b -t 4 --python vande_bharat_detail_v02/scripts/validate_roof_ends.py
blender -b -t 4 --python vande_bharat_detail_v02/scripts/validate_accessible_space.py
blender -b -t 4 --python vande_bharat_detail_v02/scripts/build_assemblies.py
blender -b -t 6 --python vande_bharat_detail_v02/scripts/render_rakes.py -- rake8 256 1800
```

The builder recreates the v02 outputs; preserve manual edits first. Shared full-size dimensions and layouts live in `prototype_dimensions.py` and `interior_layout.py`. The original v01 script supplies reusable primitive-construction helpers without modifying its files. See [component API](docs/COMPONENT_API.md).

All previews are real CPU Cycles renders of the supplied sources. Render scripts create temporary scenery/cameras and verify their inputs remain unchanged. They never save those presentation changes into the cars. The full-rake scenery extends the WAP7 v02's original railway geometry and separately credited CC0 sky/soil files from `../wap7_photoreal_v02/environment/`. It depicts a generic depot, not a named real location. No vehicle photo, generated train picture or projected reference image is used. This Blender build lacks OpenImageDenoise; real sample grain remains.

See [validation scope and recovery checkpoint](docs/VALIDATION.md) for exact saved-source checks and runtime exclusions.

## Reference precision and remaining limits

[References](REFERENCES.md) separates exact primary drawing callouts from approximate drawing-coordinate placements. The cab partition, door/window stations, nose profile and equipment centers are drawing-read estimates, generally about ±50–100 mm for body-layout placements and ±100–200 mm for roof equipment; they are not manufacturing-coordinate claims.

Fine hardware, underfloor routing, instrument UI/labels, original fabric patterns, service-room fittings and some subtype distinctions remain representative. The 8-car ordering/handing and TC_EC interior derivative are stated interpretations. Photographs and diagrams were consulted but are not redistributed as model textures. No new open-source license is asserted; follow the repository's existing arrangement.
