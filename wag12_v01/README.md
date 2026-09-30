# WAG12B twin-section modelling handoff v01

Original editable Indian Railways WAG12B visual source assets. Modelling only: the existing TF3 conversion agent must register these sources, map animations and metadata, build game materials/LODs and test in the game. No existing railway source, conversion tool, native game resource or release archive is changed by this handoff.

Reviewed against repository main `7de48a11bd95a69e03acb16043629b40a89f35ec` (30 September 2026). Generated and checked with Blender 4.3.2.

## Open first

- `sections/WAG12B_A.blend` and `WAG12B_B.blend`: independently authored, identity-root reusable section masters, live pantograph controls
- `assemblies/WAG12B_pair.blend`: complete 38.4 m coupling-span twin-section review snapshot; both driving cabs face outward
- `renders/pair.png`, `exterior.png`, `nose.png`, `cab.png`, `driver.png`, `bogie.png`, `coupling.png`, `pantograph.png`, `independent.png` and `side.png`
- `assemblies/WAG12B_pair_manifest.json`: exact placement, internal matching planes and measured visible bounds
- `qa/fbx_roundtrip.json`: all eight FBXs imported into fresh empty Blender scenes
- `qa/rig_and_aperture_checks.json`: both 101-pose panto sweeps and front/side window aperture checks

Each section has one outward cab, two crew seats/markers, two 2-axle powered bogies, one pantograph and an inward gangway/drawbar. The pair therefore has four bogies/eight axles, two driving cabs and two independently controlled pantographs. The two section masters share construction but have distinct root names and A/B labels. Exact revision-specific handed machine-room equipment differences are not claimed. The assembly contains local copies of both independently authored sections. It is a review snapshot, not a single rigid asset to import as a locomotive; edits to a master require rebuilding it.

## Dimensions and assumptions

Geometry uses metres; X longitudinal, +X towards the section's driving cab, Y lateral, +Z up. Rail top is Z=0. The 1.250 m rolling tread is tangent to that plane; 27 mm flange projections below it are intentional.

| Quantity | Model / basis |
|---|---:|
| Complete outer coupling-plane span | 38.400 m, primary East Central Railway and NWR data |
| Section coupling-plane pitch | 19.200 m, equal-half modelling interpretation |
| Body shell width | 3.058 m, selected provisional body-width figure; distinct from overall envelope |
| Complete maximum width | 3.215 m including fixed handrail hardware, matching NWR overall reference |
| Locked-down contact-strip top | 4.245 m above rail, NWR reference |
| Bogie pivot centre separation, each section | 10.200 m, training-data figure; NWR lists 2×10.200 under total wheelbase |
| Bogie wheelbase | 2.600 m, official railway figure |
| New wheel tread diameter | 1.250 m, official railway figure |
| Track gauge basis | 1.676 m; studio rail head inner faces are ±0.838 m |
| Authoring CBC/drawbar centre height | 1.105 m, project visual-alignment convention |
| Coupling anchors in each source | (+9.600, 0, 1.105) and (−9.600, 0, 1.105) m |
| Complete measured visible length | 38.580 m; CBC knuckles project 90 mm beyond each outer mating plane |
| Folded visible top | 4.245 m; full mesh bottom −0.027 m |
| Pantograph shoe centres in folded pair | Approximately 9.000 m, derivative of the documented model rig |

The main nose shell, cab, roof, bogie hardware, coupler knuckle and equipment positions are photo-informed approximations, not traced manufacturing geometry. Body-width and electrical-package reports differ across WAG12A/WAG12B revisions; this model uses the production B-type overall envelope and deliberately documents its selected body width. This is a visual source, not manufacturing, clearance or operating advice.

## Appearance and interiors

The livery follows inspected operational/manufacturer photographs: blue body, cyan rear chevrons and lower stripe, black windscreen surround, pale roof equipment and white lettering. Yellow is used on small safety hardware. No broad yellow livery is invented. `60027` is an illustrative livery number; this is not a certified replica of that specific locomotive.

The mesh includes front protective screen bars/wipers, separate lamps, cab doors and side/front glazing, body grilles, HVAC/fans, roof insulators/VCB/bus, reservoirs and cabinets, springs, dampers, axleboxes, brake cylinders, gearcases, motors, sand pipes, buffers/CBC heads and the internal gangway/drawbar halves. The rear cyan motifs are original geometry rather than copied images.

Both cabs contain desks, original geometric screens/gauges/toggles/levers, two furnished seats, pedals, interior panels, fans, sunblind rollers, ceiling ventilation/light and a fire extinguisher. Front and side window openings are actual holes through the segmented wall, with separate closed thin glazing. Ray probes confirm there is no opaque shell backing behind the main front and side windows. Thin wildlife-guard bars are intentionally visible through the forward sightline. The desk is static decorative geometry; no interactive controls are claimed.

## Hierarchy and conversion contract

Each master has exactly one parentless identity EMPTY: `WAG12B_A_ROOT` or `WAG12B_B_ROOT`. Every asset object descends from it. The asset-only FBXs contain MESH/EMPTY objects and no studio rail, ground, light or render camera.

- `BODY`: fixed vehicle geometry, roof systems and cab shell
- `BOGIE_A_YAW_Z` at (+5.100, 0, .880); `BOGIE_B_YAW_Z` at (−5.100, 0, .880)
- `AXLE_<A/B>_<1/2>_ROLL_Y`: bogie-local X ±1.300; world Z .625. Wheels/shaft are axle children; frame/suspension/axleboxes stay bogie children
- `COUPLING_FRONT` and `COUPLING_REAR` are root children. Local +X is the outward mating-plane normal; the rear rotates π about Z. These anchors are spacing/mating planes, not model-tip bounds
- `DOOR_L_CAB_HINGE_Z` / `DOOR_R_CAB_HINGE_Z`: independent closed-position cab-door groups, suggested hinge angles in custom properties. No portable door motion tracks are supplied
- `CAB_INTERIOR`: fixed cab group, local transform identity
- `DRIVER_001` / `DRIVER_002`: proposed seated CHARACTER ROOTS, local +X facing, at X7.450, Y−.690/+.780, Z1.602 m. Cushion top Z2.085; the assumed posed hip offset is .483 m. This prior-project stock-character offset is provisional for these seats and requires actual TF3 fit testing
- `CAB_EYE_CAMERA_REFERENCE`: (7.490, −.690, 2.940) m, an authoring view marker only. It is not a seat and does not assert a TF3 camera API
- `HEADLIGHT_L/R` and `TAILLIGHT_L/R`: source light-location anchors; lamps still need direction/runtime mapping

The current converter merges meshes by nearest retained EMPTY and material, so decorative details are batched within stable mechanical groups. It recognizes generic `DRIVER_` markers but defaults their `forward` flag to true. The conversion must review the pair's reverse-facing section and driver/cab metadata rather than treating both as forward-facing in the assembled locomotive. The two source files are not yet included in `tools/model_sources.py`.

There are 25 original palette materials. Diffuse colour and Principled Base Color agree. `Clear_glass` uses Transmission Weight .98, above the existing converter's .5 glass threshold. Master glass remains physically transmissive with Alpha 1.0. FBX cannot preserve Principled Transmission, so each FBX uses an export-only Alpha .18 transparency fallback, verified after fresh import. The authoritative Blender source is preferred for the existing converter's transmission-based glass classification; an FBX-only integration should explicitly map `Clear_glass` to transparent game glass. Everything is procedural geometry/materials with no photographic textures or external image dependencies. Text was converted to meshes. There is no UV/weathering atlas or authored LOD set in this handoff; existing conversion LOD generation is separate. Section A has 71,364 source triangles and section B has 71,652; exact counts and hashes are in QA. These are detailed LOD0 sources, not a claim of final game optimization.

## Pantograph: live normal/high-reach authoring rig

Each section has `PANTO_BASE / PANTO_CTRL / PANTO_LOWER_PIVOT / PANTO_ELBOW_PIVOT / PANTO_HEAD_LEVEL_PIVOT`. Set `PANTO_CTRL["extension"]` from 0 to 1; each section's control is independent. Lower and upper arm lengths remain 2.400 and 2.000 m. The local Y rotations are +θ, −2θ and +θ, maintaining a horizontal contact head with continuous rigid articulation.

- Base pivot at section X −4.700, Z 4.136 m
- Carbon contact-strip top H = 4.136 + 4.400×sin(θ) + .032 m
- θ_min = asin((4.245−4.168)/4.4); θ_max = asin((7.520−4.168)/4.4)
- extension = (asin((H−4.168)/4.4)−θ_min)/(θ_max−θ_min), clamped to [0, 1]
- 0 is folded at 4.245 m; 1 is high-reach sample at 7.520 m
- The repository's estimated standard TF3 contact height 5.917 m corresponds to extension≈.461093

The 7.520 m endpoint follows the high-rise conductor maximum shown in the linked Alstom general-outline drawing (third-party-hosted copy); it is an illustrative authoring target. The same drawing's normal-rise maximum 5.800 m differs from the repository's estimated game wire height 5.917 m. The latter is included for conversion convenience, not as a claim about actual Indian overhead installation limits. No rigid arm, insulator, actuator or head is asserted to be manufacturer-exact, and no real high-rise certification is implied. The prototype's detailed actuator/parallelogram/shunt mechanics are simplified.

The carbon strips are the highest point of the head; the head bearings remain below them. Both pantographs passed 101 sampled extension poses each for rigid lengths, head horizontality and unintended mesh intersections with other roof equipment. This excludes the intentional bearing/insulator seating within each panto base. Paired service/review images show one raised and one folded; conversion must create its own electrical/direction logic.

## FBX and motion

Per section, four FBXs:

- `*_lowered.fbx`: complete static folded asset
- `*_standard_raised.fbx`: complete static asset with contact top 5.917 m
- `*_highreach.fbx`: complete static asset with contact top 7.520 m
- `*_motion.fbx`: complete asset with baked rigid panto transform tracks

The live `.blend` master has Blender drivers; drivers are not FBX-portable. `*_baked_motion.blend` contains sampled rotation tracks on the three pivots. Frames 1–41 raise 0→1, frames 41–81 lower 1→0, at 24 fps. Each interval is 1.6667 seconds. Fresh FBX QA imports with `anim_offset=0`; Blender's default importer otherwise adds one frame. Static/motion samples are motion examples for conversion, not native triggers or automatic wire following.

## Rebuild and verification

From any directory, with Blender 4.3.2:

```
blender -b -t 2 --python build_wag12.py
blender -b -t 2 --python validate_wag12.py
blender -b -t 2 --python build_assembly_and_render.py
blender -b -t 2 --python validate_assembly.py
blender -b -t 2 --python build_assembly_and_render.py -- pair
blender -b -t 2 --python build_assembly_and_render.py -- cab
```

Other render arguments: exterior, nose, side, bogie, coupling, pantograph, independent, driver. Build scripts recreate only this handoff's outputs; back up edits first. Render files are CPU Cycles previews with denoising disabled; slight sampling grain remains.

Validation covers finite geometry, root identity, exact mechanical hierarchy/coordinates, mating-plane normals, crew markers, all eight fresh FBX imports, static endpoint heights, baked-motion endpoints and 202 live rig poses. The assembly manifest separately records measured internal-plane coincidence and outer span. `qa/assembly_and_glazing.json` checks opposed internal normals, a 1.060 m body-face gap, 96 mm bellows gap, 20 mm bridge gap and touching half-drawbar endpoints. All glass meshes have zero boundary/nonmanifold edges; the actual proposed driver-eye horizontal ray also meets no opaque geometry. Source bounds include flanges and all projecting hardware. Raised bounds must be reflected in game culling as needed.

Not yet tested: TF3/Model Editor import, actual game material appearance/LOD performance, driver-character anatomy or cockpit clipping, curve/slope behaviour, dynamic coupler yaw/compression, door triggers, lights, sound and wire contact/reversal. No native game resources, capacity, weight, power, physics, sound scripts, manifests or runtime behaviour are supplied by this modelling task.

## Reference provenance

References were inspected for original modelling and are linked, not redistributed. All supplied meshes/materials/display graphics are original procedural constructions.

1. [North Western Railway Working Time Table 2025, technical locomotive data, PDF page 166](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf): authoritative overall dimensions, wheel/bogie data and Twin Bo-Bo arrangement
2. [East Central Railway data updated 31 May 2024](https://ecr.indianrailways.gov.in/uploads/files/1718881249178-Updation%2031052024.pdf): confirms 38,400 mm over coupler pulling faces and paired locomotive context
3. [Alstom 100th locomotive delivery, 30 April 2021](https://www.alstom.com/press-releases-news/2021/4/alstom-delivers-100th-electric-locomotive-12000-hp-indian-railways): primary manufacturer photos/production type, cab-front livery, screens, lights and buffers
4. [Alstom first locomotive enters operation, 19 May 2020](https://www.alstom.com/press-releases-news/2020/5/alstoms-first-prima-electric-locomotive-delivered-indian-railways-begins-operation): primary manufacturer freight-locomotive context
5. [SRE WAG12B 60222 photograph](https://commons.wikimedia.org/wiki/File:SRE_WAG12B.jpg): operational nose, rooftop/panto and cab geometry; photograph inspected, not bundled
6. [Rail enthusiast's WAG12B 60207 side photograph](https://indiarailinfo.com/loco/SRE-WAG-12B-60207/27966): twin sections, chevrons, single outer cabs, grille and panto location. Page technical/operating claims are not used
7. [Cab photograph by Ananth Rupanagudi](https://twitter.com/Ananth_IRAS/status/1581220037884801024): first-hand cab desk/gauge/screen/blind/guard-bar visual reference
8. [Alstom WAG12B general-outline drawings, third-party-hosted copy](https://sundarmukherjee.blogspot.com/p/blog-page_60.html): visually inspected sheet NRDD0000572418, C, 3/3 for high-rise/normal-rise ranges and equipment arrangement; not redistributed or claimed as a current controlled engineering drawing

The sources distinguish the production WAG12B from the shorter initial WAG12A. This model intentionally uses the 38.4 m B-type. No open-source licence is granted; follow the repository's licensing arrangement.
