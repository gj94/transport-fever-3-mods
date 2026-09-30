# LHB AC Three Tier · first detailed Blender prototype

A generic Indian Railways red/grey, 72-berth LHB AC 3-tier coach. No real coach number or train identity is claimed. This is an editable visual prototype for review, **not a finished Transport Fever 3 asset**.

## Files
- `LHB_3A_prototype.blend`: editable source, metric scale, materials, component hierarchy, presentation cameras and lighting
- `LHB_3A_prototype.fbx`: asset-only interchange export (no studio or track)
- `LHB_3A_preview.png`: three-quarter rendered review
- `LHB_3A_side.png`: side rendered review
- `LHB_3A_detail.png`: bogie, entry and vestibule detail review
- `verification.json` and `fbx_validation.json`: actual structural and FBX re-import checks
- `build_lhb.py`: reproducible Blender 4.3.2 creation script

## Coordinates and assembly
X is coach length, Y is lateral, Z is up. Railhead Z = 0. Dimensions are metres. Bogie pivots are at X ±7.450 m and wheel-centre Z .4575 m. Four independent axle objects rotate about local Y. Door leaves have separate pivots. Door windows, handles and seals are not yet consolidated into the animated door assemblies. The hierarchy is preparatory rather than an engine animation rig.

## Dimensions used
Body length 23.540 m; coupler envelope 24.000 m; nominal body width 3.240 m; bogie centres 14.900 m; bogie wheelbase 2.560 m; nominal new wheel tread diameter .915 m; Indian broad gauge 1.676 m; floor reference 1.303 m; roof crown 4.250 m.

Height decision: source summaries quote both 4.039 m for general LHB families and 4.250 m for AC three-tier. This 3A prototype uses 4.250 m. The exact EOG/SG production drawing revision still needs final verification.

## Visible modeled features
Rounded arched/fluted metal roof, low-profile end AC packages and louvres; nine main sealed windows per side and narrow door panes; separate red door leaves and handrails; stainless three-level steps; grey end/toilet sections and obscure panes; vestibule bellows and threshold; centre-buffer couplers and brake hoses; detailed generic FIAT bogie silhouette, primary/secondary spring geometry, axle boxes, yaw dampers, brake discs and calipers; underframe cabinets/louvres/reservoirs/toilet tanks/pipes; 72 simplified blue berths across nine interior bays and berth ladders. Procedural solid materials are editable; there are no licensed photographic textures embedded.

## Sources and reference limitations
- RDSO, Revised LHB Maintenance Manual Vol II, Chapter I, Introduction (2022–23): https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_II_Chapter_I_Introduction_Draft.pdf . Text accessible at research time; intended 3A drawings pages 10–11. The PDF image and download routes repeatedly returned 502/timeout. **Drawing pixels were not available and blueprint-accurate validation has not been performed.**
- Official SECR LHB manual mirror: https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf . Download also failed.
- Actual 3A coach photograph visually inspected before modeling: https://st2.indiarailinfo.com/kjfdsuiemjvcya1/0/9/4/9/3691949/0/img20180807wa0027140677.jpg . Found at https://d.indiarailinfo.com/train/gallery/18696/673/41/2 . Used for red/grey paint boundaries, nine-window rhythm, door/step and FIAT silhouette reference. Real coach number and route were deliberately not copied.
- Supporting public railway compilation explicitly distinguishing 4.250 m 3A versus 4.039 m other LHB classes: https://st2.indiarailinfo.com/kjfdsuiemjvcya2/0/0/5/6/6366056/0/bspff243362243.pdf . Secondary cross-check, not an authoritative GA drawing substitute.

Window centres, vestibule apertures, roof equipment dimensions, interior clearances and underframe equipment positions are photographic/engineering approximations. The prototype is generic and may mix details that vary by batch. Do not use for manufacture, dimensional clearance checks or safety engineering.

## Remaining production work
Verify exact chosen drawing revision and side-to-side window details; refine production-specific equipment; retopologize/merge assemblies, UV unwrap and bake PBR atlases; prepare LODs; rig doors/wheels; author collision and coupling metadata; supply engine materials and configuration; verify official TF3 mod specification and test in game. No in-game integration, performance budget or TF3 compatibility was tested.

## Rebuild
Run Blender 4.3.2 in background mode with `--threads 2 --python build_lhb.py`. Script outputs alongside itself. Final three-quarter preview uses Cycles 64 samples; side review uses 64 samples and detail review uses 32 samples. No denoising; 1280px overall review renders. Source scenes retain modifiers. Studio track is illustrative only and excluded from FBX.

## Checked export bounds and complexity
Blender FBX re-import passed with 900 objects, 888 meshes and 210,340 evaluated triangles. No display track, lights, cameras or studio objects were exported. Bounds are X ±12.000 m, Y approximately ±1.683 m including protruding steps/handrails, and Z −0.0245 to 4.267 m including wheel flanges and roof fluting. The sheet-metal roof crown is 4.250 m; ribs add approximately 17 mm. These are modeled prototype bounds, not verified official clearance envelopes. Structural checks confirm two bogies at ±7.450 m, four axle pivots at ±1.280 m within each bogie, and 54 main plus 18 side berths.

Visual QA examined the actual three-quarter, side and detail render pixels. Corrected door parent transforms, overlapping end-panel surfaces, the AC roof transition, and initially over-wide entry steps. Entry treads now sit mostly beneath the bodyside and the detailed mesh envelope is listed separately from nominal body width. Main windows are currently dark-tinted; the simplified interior can be inspected in Blender, but requires final glazing/material tuning for strong exterior interior visibility.
