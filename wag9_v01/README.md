# WAG-9 · original modelling handoff v01

Conventional green/yellow CLW WAG-9, representative **31034**. This is a modelling source package, not a native Transport Fever 3 mod or a dimensionally surveyed replica of one individual locomotive. Made from original geometry. No external train mesh, photographic texture, reference photo, trademark artwork file or downloaded cab asset is embedded.

## Open first

- `WAG9_master.blend`: live independent pantograph controls, metre-scale editable source and complete furnished cabs
- `WAG9_baked_motion.blend`: same model with pantograph motion sampled every frame
- `WAG9_lowered.fbx` / `WAG9_raised.fbx`: portable static exports
- `WAG9_motion.fbx.zip`: lossless ZIP containing portable rigid hierarchy and pantograph animation; unzip before opening the FBX
- `renders/`: exterior, front detail, side, both cabs and pantograph review images
- `qa/`: measured geometry, linkage sweeps, fresh import and sightline checks; start with `qa/README_QA.md`
- `dimensions.json`: machine-readable dimensional and integration manifest
- `build_wag9.py`: self-contained Blender 4.3+ generator; no network or nonstandard Python packages
- `validate_fbx.py`: fresh-scene import validation for all three FBX files; automatically materializes the ZIP member in a temporary folder if the raw motion FBX is absent
- `export_fbx.py`: regenerate all FBXs from the masters and create/verify the motion ZIP

Rebuild with `blender -b -t 4 --python build_wag9.py`. Set `WAG9_SKIP_RENDER=1` to rebuild just assets and export checks. CPU Cycles renders do not require GPU or OpenImageDenoise. Rendering is intentionally independent from native conversion.

## Dimensions and datums

| Item | Model / basis |
|---|---|
| Scale and axes | 1 Blender unit = 1 metre; +X = cab A forward; +Y lateral; +Z up |
| Rail datum | Tread bottom Z=0; wheel flange projects below rail top |
| Nominal length over buffers | 20.562 m, CLW manual |
| Nominal maximum width | 3.152 m, CLW manual; grab rails set to ±1.576 m |
| Headstock span | 19.280 m reference; structural deck authored to this span |
| Bogie centres | X=+6.000 and −6.000 m; 12.000 m centre distance |
| Axles per bogie | Local X=−1.850, 0, +1.850 m; Co-Co arrangement |
| Wheel diameter | 1.092 m new tyre; axle centre Z=0.546 m |
| Track gauge | 1.676 m reference; presentation inner rail faces ±0.838 m (70 mm heads centred ±0.873 m) |
| Coupling markers | (+10.281,0,1.105) and (−10.281,0,1.105) m |
| Coupling marker span | 20.562 m, measured marker to marker |
| Pantograph strip top | 4.255 m lowered; 5.917 m raised |

Coupling anchors are explicit visual mating/spacing planes, **not the visible mesh envelope**. CBC height 1.105 m follows this repository’s existing visual convention; it is not independently certified prototype survey data. The small CBC locking knuckle projects about 40 mm beyond each marker. Buffer faces terminate at the nominal spacing plane. The `mesh_rig_validation.json` and fresh-import report record exact visible bounds; do not substitute those bounds for vehicle spacing.

## Hierarchy and import contract

Exactly one parentless asset EMPTY: `WAG9_ROOT`, identity transform. All vehicle geometry and markers descend from it. `PRESENTATION_ONLY` is excluded from export and contains floor, rails, sleepers, lights and review cameras.

- `BODY`: static vehicle exterior and cab parents
- `CAB_A`, `CAB_B`: stable cab frames. B is rotated 180° around Z
- `BOGIE_A_YAW_Z` / `BOGIE_B_YAW_Z`: bogie pivots
- `AXLE_A_1_ROLL_Y` … `AXLE_B_3_ROLL_Y`: six true axle pivots; wheelsets are children
- `COUPLING_FRONT`, `COUPLING_REAR`: root-parented mating markers; local +X points outwards
- `PANTO_FRONT_CTRL`, `PANTO_REAR_CTRL`: independent extension controls
- `…LOWER_PIVOT / …ELBOW_PIVOT / …HEAD_LEVEL_PIVOT`: portable rigid linkage nodes
- `DRIVER_001` / `DRIVER_002`: provisional seated character roots, local +X forward
- `CAB_EYE_CAMERA_REFERENCE_1/2`: view markers only, not runtime game camera definitions
- `LIGHT_HEAD_…`, `LIGHT_WHITE_…`, `LIGHT_TAIL_…`: light anchors beside separate lenses

FBX export uses forward X, up Z, `apply_unit_scale=True`, no global object rescale, EMPTY/MESH only. All lettering is converted to original mesh outlines. Bevels and normals are applied in the builder. Materials are named, compact palette materials with matching diffuse and Principled colours; glazing has Transmission Weight 0.96. Blender’s FBX interchange drops Principled transmission; the exporter therefore supplies a verified 0.25 alpha fallback for cab glass in FBX only. The .blend masters retain Transmission Weight 0.96 and Alpha 1. Native conversion should use the .blend material definition, or explicitly remap FBX glazing. No UV atlas or authored LOD chain is claimed. The repository’s converter can merge geometry by nearest retained EMPTY and generate LODs later.

## Pantograph operation

In the live master select either `PANTO_*_CTRL` and edit custom property `extension` in [0,1]. Each pantograph is independent. Both have lower length 1.38 m, upper length 1.15 m, base pivot height 4.105 m and contact-strip top offset 0.044 m.

`height(e) = 4.149 + 2.53 × sin(a0 + e × (a1 − a0))`, where `a0 = asin((4.255 − 4.149)/2.53)` and `a1 = asin((5.917 − 4.149)/2.53)`.

Lower joint Y rotation is −a, elbow local Y rotation +2a, head local Y rotation −a. The head stays horizontal and both arm lengths stay fixed. Opposite pantograph orientation is applied at the control parent. This is a geometric, poseable approximation of a conventional single-arm panto; no manufacturer linkage drawing is claimed. 5.917 m is the repository’s standard-wire visual target, not a native wire binding. No high-reach variant is bundled.

The baked timeline runs at 25 fps: frame 1 both down; 41 front up; 81 both up; 121 rear up/front down; 161 both down. Curves are sampled each frame with linear interpolation. FBX drivers are not portable, hence separate baked files. Fresh-import motion QA sets `anim_offset=0` to avoid Blender’s importer default one-frame offset.

## Cabs and character placement

Both cab shells contain genuine windshield and side-window openings, thin closed glass, stone guards, wipers, sloping control desk, analog gauges with mesh needles/ticks, diagnostic screen, switch and controller banks, seats with pedestals/armrests, pedals, rear access door, extinguisher, fans, sun visors and lighting. Side door pivots are supplied but no door animation is asserted.

Seat cushion top is 2.302 m. Each proposed driver character root is placed at Z=1.819 m using the existing `driving_upright` posed-hip assumption of 0.483 m. Root positions are provisional until actual character/converter/game fit is checked. Rear cab local forward is rotated with the cab; the current generic converter defaults `forward=true`, so rear-cab mapping must be reviewed. Do not claim in-game character seating or camera correctness from this package alone.

## Fidelity and known limits

Principal dimensions and arrangement are grounded in CLW/Indian Railways material. Exterior shapes and green/yellow livery are visually informed by the photographed conventional fleet; 31034 is representative numbering. Small roof apparatus, CBC castings, bogie mechanisms, horns, cab instruments and colour values are authored approximations. Cab layout is an illustrative legacy WAG-9 arrangement, not a control-by-control simulator reproduction or operational instruction. No air-conditioned/IGBT-specific late cab, WAG-9H ballast variant, WAG-9HC or WAG-9HH certification is claimed.

Scale, coupling, six axles, independent pantograph sweeps, sealed glass and FBX import are tested. The package still requires native format conversion, final draw-call/LOD tuning, native lighting/camera/driver binding and testing in the target game. No upstream native resources, conversion tools or distribution packages are modified.

## Provenance

Checked against `gj94/transport-fever-3-mods` main `7de48a11bd95a69e03acb16043629b40a89f35ec`, 30 September 2026. See `references.md` for public reference links and what each source supports. This package is an original user-requested model; cited photographs are only research references and are not redistributed.
