# ICF detail v02 — work in progress

Separate, original authoring-source revision for seven conventional self-generating ICF classes: 1A, 2A, 3A, 2S, CC, SL and GS. The existing authoring families, locomotive coupling variants and native Transport Fever resources are unchanged.

## Current checkpoint

All seven r03 class masters and FBX files have now been generated. Actual Blender exterior/cutaway and eye-level 1A and 3A proofs have been inspected. Subsequent source refinements (micron cleanup, selected open-surface normals, contoured chairs and first-class fittings/materials) are staged in the generator and are not yet in these r03 files. Each manifest records the generator hashes used for its model. This is an active recovery checkpoint, not a final release.

Selected stock uses conventional screw couplings and side buffers. It is intentionally not a CBC clone of the existing native fleet. Coupling to the WAP7, linked rake articulation, character fit and all native game behavior are **unvalidated**. No TF3 conversion is included.

## Prototype scope

Dimensions selected from NWR conventional-stock tables, with the 3.245 m body width from SCR/ICF rather than NWR’s rounded 3.250 m: 21.337 m body/headstock length, 22.297 m over buffers, 3.245 m maximum bodyside width, 14.783 m bogie pivot spacing, 2.896 m wheelbase, 0.915 m new wheel diameter. Nominal roof crown is 4.025 m; ventilators protrude above the crown. SCR Knowledge Bank rounds the first two dimensions differently (21.336 / 22.296 m). Production-class drawings remain authoritative; this is a visual interpretation, not manufacturing or clearance CAD.

Capacities: 1A 18; 2A 46; 3A 64; 2S 108; CC 73; SL 72; GS selected 108-seat subtype. Private first-class cabins/coupes, two-tier curtains, three-tier/folded-middle sleepers, chair car, individual second-sitting seats and general benches are separate physical arrangements. Commercial game capacity is not changed here.

## Rebuild

Use Blender 4.3 or compatible: `blender -b -t 2 --python icf_detail_v02/scripts/build.py -- all`. A class code builds only that variant. No external assets or Python dependencies are required. Preview renderer: `blender -b icf_detail_v02/SL/ICF_SL_master.blend -t 2 --python icf_detail_v02/scripts/render_detail.py -- exterior cutaway aisle bogie entrance`.

Renders are actual Blender geometry, not image-generated illustrations. Cutaway hides the roof and one bodyside for inspection only. Studio lights and camera are excluded from FBX. Passenger and berth markers are authoring references, not claims of runtime validation.

## Remaining work

- Complete seven-class generation, material/mesh/hierarchy checks and full visual review
- Inspect eye-level interior, window/door, bogie and coupling details against appropriate references
- Improve source fidelity where references support a correction; record remaining assumptions
- Export/reimport and class count checks, final source manifests/checksums, final actual-model previews
- No claim of absolute perfection or exact numbered-coach reconstruction

Primary references and existing capacity/layout rationale are in the unchanged `../icf_family_v01/references.md`. New running-gear references are embedded in `scripts/icf_running_gear.py`. Illustrative markings do not identify an exact photographed coach.
