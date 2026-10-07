# ICF detail v02 — work in progress

Separate, original authoring-source revision for seven conventional self-generating ICF classes: 1A, 2A, 3A, 2S, CC, SL and GS. The existing authoring families, locomotive coupling variants and native Transport Fever resources are unchanged.

## Current checkpoint

All seven masters are now r12-stencil: four capacity labels per class were corrected to BERTHS or SEATS, with no fabricated tare mass. An exact non-stencil mesh/transform/hierarchy/material-assignment fingerprint confirms that the reviewed six-class r10 geometry and isolated first-class r11 privacy closure are otherwise unchanged. All source geometry, aperture, support, seated-root and relocated-FBX texture/hierarchy/bounds checks pass on r12. Final 512-sample image production remains pending. Earlier low-sample review images are retained as named history; source hashes in adjacent JSON files distinguish them from current final images.

Selected stock uses conventional screw couplings and side buffers. It is intentionally not a CBC clone of the existing native fleet. Coupling to the WAP7, linked rake articulation, character fit and all native game behavior are **unvalidated**. No TF3 conversion is included.

## Prototype scope

Dimensions selected from NWR conventional-stock tables, with the 3.245 m body width from SCR/ICF rather than NWR’s rounded 3.250 m: 21.337 m body/headstock length, 22.297 m over buffers, 3.245 m maximum bodyside width, 14.783 m bogie pivot spacing, 2.896 m wheelbase, 0.915 m new wheel diameter. Nominal roof crown is 4.025 m; ventilators protrude above the crown. SCR Knowledge Bank rounds the first two dimensions differently (21.336 / 22.296 m). Production-class drawings remain authoritative; this is a visual interpretation, not manufacturing or clearance CAD.

Capacities: 1A 18; 2A 46; 3A 64; 2S 108; CC 73; SL 72; GS selected 108-seat subtype. Private first-class cabins/coupes, two-tier curtains, three-tier/folded-middle sleepers, chair car, individual second-sitting seats and general benches are separate physical arrangements. Commercial game capacity is not changed here.

## Rebuild

Use Blender 4.3 or compatible: `blender -b -t 2 --python icf_detail_v02/scripts/build.py -- all`. A class code builds only that variant. After a base rebuild, run `blender -b -t 4 --python icf_detail_v02/scripts/build_1a_r11.py` for the current first-class privacy revision; this wrapper leaves the other six source versions unchanged. Finish with `blender -b -t 4 --python icf_detail_v02/scripts/patch_capacity_stencils_r12.py` to record the current capacity-stencil pass and non-text fingerprint. The bundled original text-only marking PNGs are packed into each master; Blender builds need no downloads or additional Python libraries. Optional `scripts/make_marking_textures.py` regeneration uses Pillow with Raqm and Noto Sans Devanagari. Preview renderer: `blender -b icf_detail_v02/SL/ICF_SL_master.blend -t 2 --python icf_detail_v02/scripts/render_detail.py -- exterior cutaway aisle bogie entrance`.

Renders are actual Blender geometry, not image-generated illustrations. Cutaway hides the roof and one bodyside for inspection only. Studio lights and camera are excluded from FBX. Passenger and berth markers are authoring references, not claims of runtime validation.

## Verified source state and remaining work

All seven classes have completed source generation, geometry, support/contact, aperture, seated-root and relocated FBX texture/hierarchy/bounds checks. The current r12 sources and exports are frozen in `qa/final_geometry_lock.json`; recovery revalidation confirms unchanged hashes. These checks do not establish native game compatibility, animated character fit or dynamic mechanical clearances.

Remaining work is the complete 24-view high-sample actual-model gallery, final pixel review and finished-gallery provenance audit. The truthful completion count is in GALLERY.md. Do not interpret prior review images as completed high-sample finals.

## Portable render dependencies

Source Blender meshes and packed class-label textures are self-contained for inspection. The outdoor gallery renderer additionally expects these repository-root siblings: `vande_bharat_detail_v02/components/environment_depot.py`, `vande_bharat_detail_v02/components/common.py`, and four textures in `wap7_photoreal_v02/environment/`: `kloofendal_48d_partly_cloudy_puresky_2k.hdr`, `dirt_diff_2k.jpg`, `dirt_rough_2k.jpg`, `dirt_disp_2k.exr`. Keep this folder structure when relocating or packaging render sources. Each outdoor sidecar records exact dependency SHA-256 values; resumed outdoor EXR batches bind those same hashes in their checkpoint fingerprint. These generic depot/ground presentation assets are excluded from vehicle FBX.

Current stock is conventional screw-coupled ICF with side buffers. The earlier family reference ledger also discusses a CBC adaptation; that historical coupling note does not apply to this v02 selection.

Primary references and existing capacity/layout rationale are in the unchanged `../icf_family_v01/references.md`. New running-gear references are embedded in `scripts/icf_running_gear.py`. Illustrative markings do not identify an exact photographed coach.
