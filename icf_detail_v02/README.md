# ICF detail v02 — work in progress

Separate, original authoring-source revision for seven conventional self-generating ICF classes: 1A, 2A, 3A, 2S, CC, SL and GS. The existing authoring families, locomotive coupling variants and native Transport Fever resources are unchanged.

## Current checkpoint

The six shared-class masters are r10; 1A is an isolated r11-1A revision closing all private cabin/coupe bulkheads and corridor tops to the arched ceiling. All seven pass source geometry, aperture, interior-support, seated-root and relocated-FBX texture/hierarchy/bounds checks. The current sources have actual Blender overview/interior review images. 1A privacy closure also passes focused geometric checks and revised pixel review. Final 512-sample gallery production remains pending; low-sample review images are not final previews. The earlier r10 first-class images remain clearly named history and do not show the r11 privacy correction.

Selected stock uses conventional screw couplings and side buffers. It is intentionally not a CBC clone of the existing native fleet. Coupling to the WAP7, linked rake articulation, character fit and all native game behavior are **unvalidated**. No TF3 conversion is included.

## Prototype scope

Dimensions selected from NWR conventional-stock tables, with the 3.245 m body width from SCR/ICF rather than NWR’s rounded 3.250 m: 21.337 m body/headstock length, 22.297 m over buffers, 3.245 m maximum bodyside width, 14.783 m bogie pivot spacing, 2.896 m wheelbase, 0.915 m new wheel diameter. Nominal roof crown is 4.025 m; ventilators protrude above the crown. SCR Knowledge Bank rounds the first two dimensions differently (21.336 / 22.296 m). Production-class drawings remain authoritative; this is a visual interpretation, not manufacturing or clearance CAD.

Capacities: 1A 18; 2A 46; 3A 64; 2S 108; CC 73; SL 72; GS selected 108-seat subtype. Private first-class cabins/coupes, two-tier curtains, three-tier/folded-middle sleepers, chair car, individual second-sitting seats and general benches are separate physical arrangements. Commercial game capacity is not changed here.

## Rebuild

Use Blender 4.3 or compatible: `blender -b -t 2 --python icf_detail_v02/scripts/build.py -- all`. A class code builds only that variant. After a base rebuild, run `blender -b -t 4 --python icf_detail_v02/scripts/build_1a_r11.py` for the current first-class privacy revision; this wrapper leaves the other six source versions unchanged. The bundled original text-only marking PNGs are packed into each master; Blender builds need no downloads or additional Python libraries. Optional `scripts/make_marking_textures.py` regeneration uses Pillow with Raqm and Noto Sans Devanagari. Preview renderer: `blender -b icf_detail_v02/SL/ICF_SL_master.blend -t 2 --python icf_detail_v02/scripts/render_detail.py -- exterior cutaway aisle bogie entrance`.

Renders are actual Blender geometry, not image-generated illustrations. Cutaway hides the roof and one bodyside for inspection only. Studio lights and camera are excluded from FBX. Passenger and berth markers are authoring references, not claims of runtime validation.

## Remaining work

- Complete seven-class generation, material/mesh/hierarchy checks and full visual review
- Inspect eye-level interior, window/door, bogie and coupling details against appropriate references
- Improve source fidelity where references support a correction; record remaining assumptions
- Export/reimport and class count checks, final source manifests/checksums, final actual-model previews
- No claim of absolute perfection or exact numbered-coach reconstruction

Primary references and existing capacity/layout rationale are in the unchanged `../icf_family_v01/references.md`. New running-gear references are embedded in `scripts/icf_running_gear.py`. Illustrative markings do not identify an exact photographed coach.
