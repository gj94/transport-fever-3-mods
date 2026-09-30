# LHB AC 3-tier interior v02

Editable ordinary 72-berth red/grey LHB 3A visual prototype, refined from the v01 source in `gj94/transport-fever-3-mods` commit `7b6b23da96b839751c31faae5160f5a49e0424c1`. This is a Transport Fever 3 asset-development source, **not a tested game-ready mod**.

## Deliverables
- `LHB_3A_interior_v02.blend`: assembled coach with editable interior, original exterior and hierarchy, presentation cameras
- `LHB_3A_interior_v02.fbx`: asset-only export including reference passenger empties
- `LHB_v02_exterior.png`: complete assembled exterior regression view
- `LHB_v02_passenger.png`: real perspective down the offset side aisle
- `LHB_v02_bay.png`: real perspective into a daytime seating bay
- `LHB_v02_cutaway.png`: overall layout, with roof and selected near-side parts hidden for inspection only
- `refine_lhb.py`, `validate_lhb.py`, `validation.json`: reproducible modeling and actual structural/round-trip checks

The saved Blend and FBX are fully assembled. The cutaway does not change exported geometry. It is an inspection view, not the exterior asset appearance.

## Layout and configuration
Nine bays, each with six transverse berths and two longitudinal side berths, retain the 72-berth ordinary 3A scheme. The longitudinal aisle is offset toward +Y, between the transverse bay ends and side berths; it is not a central aisle separating symmetric berth banks.

This version depicts **daytime seating**: 18 middle berths are folded upright into padded backrests. The model contains 18 lower, 18 middle, 18 upper transverse berths plus nine lower and nine upper side berths. There is no middle-berth deployment animation. The narrowest modeled straight aisle between ladder envelope and side guard/support envelope is approximately 0.51 m, not a certified clearance.

72 named `PAX_B##_...` empty objects provide seat/pelvis reference points: six seated references on lower transverse benches and two on the lower side berth in each bay. They face along local +X, with object rotation indicating facing direction. They are **not runtime passenger integration**, and should not be treated as 72 sleeping-pose anchors. A torso/head-prism test found no furniture intersection; limbs, full character meshes, walking, and animation were not tested.

## Added visible detail
Blue padded vinyl, seams and folded backrests; satin-metal berth pans and supports; complete bay partitions; ladders and upper guards; under-seat barred luggage shelves; laminate window tables; genuine open glazing apertures with interior reveals and narrow gathered curtains; blue-grey nonslip flooring; FRP wall and ceiling lining, panel joints, ceiling light housings and AC grilles; generic reading lights and outlet faceplates; offset saloon bulkheads and stowed sliding doors; visible vestibule finishes and closed toilet compartment doors. Hidden toilet rooms and invisible machinery are not modeled. Roof lamps used to light previews belong to the presentation collection and are excluded from export.

Entry door leaf, recess and inner liner have real through-openings at the glazed panes. Entry door panes, seals, handles and new inner liners now follow their existing door pivots while preserving closed-state world transforms. Door animation has not been engine-tested. Original nominal body dimensions, bogie placement, all four axle pivots, underframe and couplers are retained. Glazing was changed to transmissive glass so the genuine interior is visible through existing apertures.

## References and limits
- RDSO Revised LHB Maintenance Manual Vol II, Chapter I, June 2022 draft: https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_II_Chapter_I_Introduction_Draft.pdf#page=10 . Text identifies EOG AC 3-tier LWACCN, layout LE90009, 72 berths. Page 11 is the SG version. Official PDF pixels and download routes failed during this pass; dimensional blueprint validation is therefore **not claimed**.
- Actual 3AC aisle photograph, pixels reviewed: https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/9/2/7/1499927/5/dsc21051868909.jpg . Source context: https://m.indiarailinfo.com/blog/post/1499927 . Used for blue upholstery, metal guards, partition and aisle appearance.
- Actual LHB Gujarat Mail berth photograph, pixels reviewed: https://st.indiarailinfo.com/kjfdsuiemjvcya22/0/7/8/8/3191788/0/picsart031009800443.jpg . Source context: https://indiarailinfo.com/train/tips/gujarat-mail-12901/570/298/60 . Used for side berth, lower seat and guardrail construction cues.

No third-party photographs are embedded, redistributed or used as textures. Procedural solid materials are original. Photos establish appearance, not a single proven production revision. Reading-light/outlet distribution, curtain arrangement, panel joints, ceiling details and exact furniture dimensions are generic/batch-dependent approximations. Existing v01 window rhythm and body envelope are preserved rather than claiming manufacturer-exact interior pitch. This is ordinary 3A, not the later 83-berth economy design.

## Validation and production caveats
`validation.json` records 72 berth modules, 72 seated locators, two bogies, four axle pivots, zero tested torso/head proxy intersections, and asset-only FBX re-import. Export has 252,441 triangles versus 210,340 in v01, about 20% growth. The many separate editable objects are intentionally not merged for final rendering performance. Bounds remain X ±12.000 m, Y approximately ±1.683 m, Z −0.0245 to 4.267 m.

Still required: exact production-revision dimensional verification, appropriate human-mesh fitting, retopology and draw-call consolidation, UV/PBR bake, LODs, final glazing, collision, engine seat/coupling metadata, animation and in-game tests. No TF3 specification compliance or performance budget is claimed.

## Rebuild
Use Blender 4.3.2. Place this folder at `interiors_v02/lhb` beside the original repository's `lhb` folder. Run `blender -b --threads 2 --python interiors_v02/lhb/refine_lhb.py`, then the validation script. Alternatively set the `LHB_SOURCE` environment variable to the original Blend path. The original is read-only input; all outputs are written beside the scripts. Previews use Cycles and two CPU threads, with denoising disabled. The exterior, bay and aisle use 64 samples; the final key cutaway uses 256 samples.
