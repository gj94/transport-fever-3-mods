# WAP7 pantograph v04 — independently articulated

## Current TF3 integration — pack v1.0

Native conversion is included in **pack v1.0 (TF3 revision 14)** alongside fourteen ICF/LHB coaches. The installed revision 13 has identical vehicle content; v1.0 installation follows the running play test. Existing locomotive/trainset geometry, gameplay, rigs and the approved private horn are retained. All vehicle store/construction PNGs use straight side views. The modelling and QA below document these original authoring files. See [current installation, integration and remaining checks](../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

Start with **WAP7_pantograph_v04.blend**. It opens with both pantographs folded and live, independently editable drivers. The source is the accepted coupling-v03 WAP7, verified byte-for-byte against GitHub main at `f398592b3908ef205843d1e9b2211cb0189973f4`. SHA-256: `41f6584e85797ec5785177a3f44916aeb1344bcc51e5eaf2e0a3c872384ca577`.

## Controls and heights

Select `PANTO_FRONT_CTRL` for the +X vehicle end (roof base around X=+5 m), or `PANTO_REAR_CTRL` for the −X end (base around X=−5 m). Object Properties → Custom Properties → `extension` independently controls each assembly. 0 is folded; 1 is an illustrative raised pose; intermediate values are continuous. Both have the source model’s same longitudinal fold direction.

| extension | lower-arm angle | Contact-strip top above rail | Head pivot above rail |
|---|---:|---:|---:|
| 0 / lowered | 1° | 4.254758 m | 4.222758 m |
| 0.25 | 9.75° | 4.626906 m | 4.594906 m |
| 0.5 | 18.5° | 4.989397 m | 4.957397 m |
| 0.75 | 27.25° | 5.333791 m | 5.301791 m |
| 1 / raised example | 36° | 5.652074 m | 5.620074 m |

Rail top is Z=0, inherited from the source wheel-tread convention, **not flange bottom**. Heights measure the actual flat contact-strip top vertices; they are not the pivot origin. Each strip is level, so its minimum and maximum top heights agree within float precision. These are model measurements, not a required TF3 catenary height.

For desired contact-top height H in the provided range, use:
`extension = (asin((H − 4.212) / 2.45) in degrees − 1) / 35`.
Do not move or scale the locomotive root to fit overhead wire. TF3 animation triggers, wire-following logic and final operating-height choices remain yours. No TF3 runtime scripts, game events, or fixed wire-height binding are included. Test in TF3 after binding.

## Rig and mechanics

Each control has `LOWER_PIVOT → ELBOW_PIVOT → HEAD_LEVEL_PIVOT`. Meshes are separate for lower arms, upper arms, crossbars, base/elbow/head hinge shafts, head supports, two contact strips and end horns. Every name begins `PANTO_FRONT_` or `PANTO_REAR_`.

Constant joint distances: lower arm 1.400 m; upper arm 1.050 m. The lower pivot rotates about local Y by −θ, elbow local Y by 2θ, head local Y by −θ. Thus the upper global angle is +θ and the head sums to zero. Both hinge endpoints coincide throughout travel; rigid parts never stretch. The head moves slightly longitudinally as it rises. The root’s parent inverse cancels the inherited BODY width scaling for this new rig, without touching BODY or any existing object.

The useful supported range is extension 0–1, clamped by the drivers. The 36° raised endpoint is a sample configuration chosen for the existing arm lengths, not a certified physical maximum. To change the mechanical envelope, edit A0/AR in the portable builder and re-run QA; do not assume a high-rise replacement pantograph’s dimensions apply to this conventional approximation. `lower_angle_deg` and `raised_angle_deg` custom properties are informational; the live control is `extension`.

## FBX and animation

Blender drivers do not survive FBX. Three exports are supplied:
- `WAP7_pantograph_v04_lowered.fbx`: complete asset, static lowered pose
- `WAP7_pantograph_v04_raised_sample.fbx`: complete asset, both raised sample poses
- `WAP7_pantograph_v04_motion_samples.zip`: unzip here to obtain `WAP7_pantograph_v04_motion_samples.fbx`, the complete asset with baked rigid transform tracks and independent front/rear movement. Compression is lossless and preserves the verified FBX bytes. The raw file exceeds the GitHub API blob-input limit; the ZIP makes delivery practical.

`WAP7_pantograph_v04_baked_samples.blend` is the editable baked-action equivalent. Use the main `.blend` for live scalar controls; use this separate file or the animated FBX for action extraction.

Motion sample timeline:
- Frames 1–41: front raises, rear stays folded
- Frames 41–81: rear raises, front stays raised
- Frames 81–121: front lowers, rear stays raised
- Frames 121–161: rear lowers, front stays folded

Each of the six pivot objects has a named `…_INDEPENDENT_MOTION_SAMPLES` action in the baked Blender file. FBX exports one combined take with clearly named transform channels. Extract the desired end’s three channels and interval for your game pipeline; the two assemblies share no driver target or moving parent. Frame rate is **24 fps** (fps_base=1), retained from the original scene. Each 40-frame raise/lower interval spans 1.6667 seconds; frame 1 is time zero. Blender’s FBX importer defaults to adding a **one-frame animation offset**; import with `anim_offset=0` to reproduce the listed sample frame numbers, or account for that offset in your importer. This does not change the sample durations or poses.

## Scope and preservation

Only the old static moving pantograph rods, hinges, shoes and horns were replaced. Both roof bases, pneumatic cylinders and ceramic insulators remain untouched. Exact original object names, parent links, matrices, mesh-coordinate/topology hashes and materials were checked for all 2,661 protected objects. This includes both interiors, bogies/axles, units, origin and coupling anchors. Coupling anchors remain (+10.2, 0, 1.105) and (−10.2, 0, 1.105) m.

This is a simplified game-oriented paired-arm/single-fold approximation retaining the accepted asset’s silhouette, not a manufacturer-exact AM92/IR03H reproduction. The differential geometry, spring/air actuator internals and flexible electrical shunts are not mechanically simulated. Contact heads are kept rail-parallel over the full range rather than dynamically tracking track cant or wire irregularities.

## References and reproduction

- [Indian Railways RDSO SMI292, AM92/IR03H pantographs](https://rdso.indianrailways.gov.in/works/uploads/File/SMI%20292%283%29.pdf): maintenance specification, including head horizontality
- [North Western Railway working timetable technical data](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf): WAP7 locked-down reference height 4,255 mm, matching the inherited model convention closely
- [South Central Railway technical question bank](https://scr.indianrailways.gov.in/uploads/files/1629190703446-JE%20TRS%20PRQ%20%20Syllabus%20%20QB.pdf): WAP7 pantograph type context; exact subtype of the accepted model remains unverified
- [Photographic single-fold mechanism comparison](https://indiarailinfo.com/blog/post/4502812?tp=22): inspected the detailed roof photo to check hinges, folded arm topology, level head and downturned horns; this example is not claimed to identify the asset’s exact make

Build: `blender -b -t 2 --python build_pantographs.py -- /path/to/WAP7_coupling_v03.blend /path/to/output`.
Verify and render: first extract the motion-sample ZIP into this package, then run `blender -b -t 2 --python verify_and_render.py`. Blender 4.3.2 used. Build creates direct mesh data (no object-operator mesh loop); renders use CPU, two threads, 32 samples, denoising disabled. Source path is an explicit argument and no external textures are required.

See `rig_validation.json`, `protected_source_manifest.json`, and `fbx_validation.json` for measured checks. Screenshots show the lowered detail, raised detail and one-up/one-down locomotive. Checksums cover the delivered files.

## Final sweep and independent review

A 101-point sweep per pantograph detected no unintended triangle-surface intersection with preserved nearby roof/equipment. Moving geometry's minimum Z was 4.159003 m (0.286503 m above the roof panel); fixed bearing blocks intentionally seat into the retained pantograph bases. Head tilt stayed below 0.000006°. Independent QA additionally checked 23 control combinations and all three fresh FBX files. See `sweep_validation.json` and `independent_review.json`. This checks visual rig closure and interference, not manufacturer tolerances or physical actuator simulation.
