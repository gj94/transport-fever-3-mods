# LHB detailed coach family v0.2 — source assets and review gallery

This isolated revision contains source assets and a completed 21-view versioned-source render gallery (20 accepted pre-repair views and the corrected latest-source lavatory view), developed from the seven class-specific v0.1 masters. It does not replace earlier sources or the native TF3 pack. All seven class sources and FBX exports have been rebuilt from matching current modules. Geometry, hierarchy, capacity and furnishing-placement checks pass for all seven classes, with separately reported editable-font tessellation warnings. Visual proofs are being reviewed and refined. The first published checkpoint remains explicitly WIP. Do not treat this checkpoint as a final release or runtime-ready asset.

## Prototype and coordinate contract

Selected conventional LHB types: 1A 24 berths, 2A 52 berths, 3A 72 berths, 2S 102 seats, CC 78 seats, SL 80 berths and legacy centre-entry GS 100 seats. The physical capacities are separate from gameplay payload.

Metres; X longitudinal, Y lateral, Z up; railhead Z=0. Body 23.540 m ×3.240 m, crown 4.039 m, floor 1.303 m, bogie centres 14.900 m, wheelbase 2.560 m, new wheel diameter .915 m. CBC mating anchors at X ±12.000 m and Z1.105 m. Authoring geometry, furniture dimensions and equipment placement remain reference-informed interpretations, not manufacturer CAD.

`PAX_*` EMPTY objects are seated character roots, parented to the body, with explicit yaw. `BERTH_*` EMPTY objects are sleeping references only. No seated passenger roots are on upper/middle beds. Native TF3 conversion and runtime validation are outside this source revision.

## Initial changes

- Original rounded through-window wall apertures and separately closed glazing
- Smooth curved roof with recessed HVAC-end wells and raised end structure, rain gutters, HVAC fan blades/grilles, door seals/hinges/steps
- FIAT running gear rebuilt around two 640 mm brake discs per axle, nested coils, profiled frame, calipers, control arms and pipework
- Detailed equipment enclosures, reservoirs, CBC castings and service hoses
- Upholstery piping, stitched panels, folded upper-berth linen, pleated curtains, berth hinges, reading lights, sockets and hollow wire bottle holders
- Detailed end-service fittings, washbasins, lavatory fixtures and electrical control cubicles

## Rebuild

With Blender 4.3.2, run `blender -b -t 2 --python build_lhb_detail.py -- 3A` from this directory. Omit the class argument to rebuild all classes. The builder writes its own models; preserve hand edits before rerunning. `render_lhb_detail.py` creates actual CPU Cycles views. No generated-image previews or vehicle photographs are used. Outdoor review lighting and terrain use the already credited Poly Haven CC0 sky and Dirt material under `../wap7_photoreal_v02/environment`; these are render-only dependencies, not exported vehicle assets.

## Sources and current limits

Reference basis: the railway-authored CAMTECH Maintenance Manual of LHB Coaches, chapter 1 class drawing plates and photographs, and the FIAT bogie maintenance chapter. The official source is [SECR's manual](https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf); when its download failed, the identical titled railway document was read from its [public distribution mirror](https://d2wuvg8krwnvon.cloudfront.net/media/user_space/cf19354d093c/ebook/ebook_1639504169_9471.pdf). Only links are redistributed. Drawing pixels were inspected, including distinct 1A cabin/corridor window rhythms and paired narrow SL windows.

Selected dimensions and capacities also follow the official [NWR 2025 technical data](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf) and [RDSO revised introduction](https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_II_Chapter_I_Introduction_Draft.pdf), with the same explicitly selected 1.303 m floor datum as v0.1. See the preserved earlier [reference ledger](../lhb_family_v01/references.md) for source conflicts and prototype-selection boundaries.

The current geometry passes independent source and FBX round-trip QA in `qa/source_geometry/aggregate.json`; complete visual review and final renders remain pending. Old nested QA directories retain historical checks and are not the current verdict. Previews are current only when the recorded source SHA-256 matches the corresponding current .blend; low-sample proofs and stale images are not final beauty renders. Fine furnishing and equipment fittings are representative approximations. Couplers are static visual models; no claim is made for operational articulation, certification, or compatibility with unrelated new locomotive couplers. Materials use editable procedural shaders; a game exporter must bake or adapt them.

## Review provenance

Each new source stores SHA-256 values for its eight build modules. Every rendered view records the source/image SHA-256, camera, samples, resolution and any temporarily hidden review geometry. The renderer refuses to mark provenance complete if the source changes during rendering. Formation-position boards (H1/A1/B1/D1/C1/S1/GS) and NR regional lettering are representative editable livery details, not a claim to reproduce a real numbered coach or verified train formation.

The CC variant now uses the manual’s 450 mm cushion height above the floor (world Z 1.753 m); its seated-root datum is 1.270 m with the retained 483 mm pose hip offset. This is an authoring pose datum, not a claim that a complete game character has passed runtime floor/foot clearance. Other class cushions retain the separately selected datum.

## Reference-informed furnishing milestone, 7 October 2026

- RMPU units use offset twin condenser fans, actual recessed wells, four mesh intake panels, six maintenance covers and paired electrical/conduit fittings; the underlying roof platform is flat to 1.27 m halfwidth and physically clear of the wells
- 1A uses rounded burgundy upholstery, gathered tied curtains, ivory returns, cabin reading/ceiling lamps, magazine nets, mirrors, switches and supported upper-berth access steps. Ladder stiles, coat-hook bases and magazine-frame mounting now meet the surfaces they attach to
- CC uses 450 mm cushion height, 17° upright backrest geometry, roller blinds, aluminium/glass shelves, individual reading lights, footrests, magazine nets and bracket-mounted bottle cages
- GS banks mirror across the centre doorway, with twenty transverse overhead racks. SL and GS each have thirty class-positioned ceiling fans
- Source module hashes, material conversion and PAX/BERTH contracts are measured independently. Fault-injection tests verify that wrong roots, dimensions, fixtures, fan/rack orientation and disconnected 1A attachments are detected

Fine hardware remains representative original modelling; neither reference fidelity nor source geometry QA constitutes railway certification, production CAD or in-game validation.

## Geometry lock and final gallery

The corrected CC antimacassar is a closed 1.2 mm draped textile with a sewn hem, replacing the earlier thick pad proxy. Its 25-ring chair-shoulder refinement preserves maximum dimensions and passenger datums. The corrected 64-sample close and interior proofs were visually reviewed before geometry lock. Fifteen isolated CC furnishing and topology checks pass. The full-family rebuild and independent source/FBX checks are repeated against this locked revision before final rendering.

`scripts/render_final_gallery.py` provides a full-gallery render route using the restart-safe workflow below. Final frames use eight independently seeded 64-sample passes, 512 uniform samples per pixel, four CPU threads, adaptive sampling disabled and no denoising. Gallery completion is separate from geometry, FBX portability and native-game validation. After a source repair, do not reuse old-source caches for a full rerender: preserve them and start fresh caches. The curated delivered gallery follows the explicit versioned-source policy below.


## Post-lock 1A typography correction

The first high-sample interior review revealed a reversed LIGHT / SOCKET legend beneath the cabin mirrors. `scripts/fix_1a_legend_orientation.py` changes only the eight relevant editable FONT rotations toward the interior (+Y). Run this script after rebuilding 1A. The eight original build modules remain unchanged; the patch script hash is stored separately in the 1A root and manifest. The patch records identical non-text evaluated-geometry fingerprints before and after, and verifies all six other class source files retain their hashes. Fresh source/FBX QA and final source-matched renders are required after this correction. See `qa/1A_legend_orientation_patch.json`.

## Restart-safe final rendering

After repeated execution interruptions, the remaining final queue uses eight independently seeded 64-sample CPU Cycles passes. Each pass is saved as a 32-bit scene-linear RGBA EXR and hash-verified before reuse. The equal-weight scene-linear average receives the AgX display transform exactly once when the final PNG is saved. Adaptive sampling and denoising are disabled for this workflow; the result contains 512 uniform samples per pixel. Earlier completed adaptive renders remain valid and are explicitly distinguished by their per-view provenance. This changes rendering persistence only; source geometry, cameras and lighting are unchanged.

The portable implementation is `scripts/checkpoint_render.py`, invoked through `scripts/run_checkpoint_renderer.py`. Each final render JSON includes `sampling_workflow` when this method is used. Intermediate EXRs remain local recovery data and are not presented as finished gallery frames.

## Delivery navigation

See [GALLERY.md](GALLERY.md) for the current source-matched 21-view gallery and [DELIVERY_STATUS.json](DELIVERY_STATUS.json) for measured completion. These indexes are regenerated from actual source/image hashes before checkpointing; they do not treat stale or low-sample images as final. The approved set is fourteen class interiors/exteriors plus seven detail views, including the added 3A bay camera.

Native editable sources are the seven `.blend` masters in `models/`; paired `.fbx` files are portable exchange exports. This folder structure is not a native Transport Fever 3 mod and does not assert runtime readiness. See the explicit limitations above. Historical renderer helper bytes needed to explain earlier fingerprints are preserved under `scripts/render_provenance/`.

## Visible fidelity caveats

The models are detailed reference-informed authoring assets, not a claim of photorealistic perfection. At close range, some CC tray and armrest bevels reveal polygon faceting. The lavatory is a representative modular layout; the rejected segmented seat and floating paper fixture were corrected in the documented WC repair revision. Interior frames retain visible path-tracing grain because denoising is disabled. Sleeper corridor views mostly document layout; the 3A bay detail shows berth faces more clearly. Fine fixtures, coupler castings and equipment placement are representative interpretations, and editable-font tessellation warnings remain disclosed in QA. These limits do not change the measured source/FBX checks or imply native game readiness.

## Provenance scope

Final image and source SHA-256 values, render/helper dependency identities, eight 64-sample EXR batches and single final display transform are independently checked by `scripts/audit_final_gallery.py`. Local EXR caches are recovery/audit material and excluded from the portable source/gallery archive. Per-view `camera_xyz` and lens metadata describe the configured camera and are checked against the unchanged renderer. The nested checkpoint `spec.camera_matrix` was captured before dependency-graph evaluation and can retain the saved scene camera transform; it must not be described as the actual evaluated view matrix. For example, the 1A cabin-entry record correctly reports `camera_xyz` approximately (-7.15, -1.30, 2.59), while the nested pre-evaluation matrix retains translation (20, -29, 13). Existing records and fingerprints are preserved byte-for-byte rather than retroactively relabeled. Final checks do not assert native-game compatibility.

## WC repair revision and exact rebuild order

The final WC review found disconnected six-sided seat-ring rods and a paper-holder/tissue pair floating away from its mounting wall. Two deterministic post-build repairs replace only the rings with continuous manifold smooth meshes (same envelope, material and parent) and move only the paper fixtures onto the actual corridor-wall face. The tissue roll is offset just enough to avoid penetrating the wall. Every other evaluated object, hierarchy, anchor, custom property and material node value/link is fingerprinted unchanged at each step. Patch metadata added to the vehicle root and sidecars is explicit.

To reproduce the latest masters from the unchanged original modules, run in this order:

1. `blender -b -t 2 --python build_lhb_detail.py`
2. `blender -b -t 2 --python scripts/fix_1a_legend_orientation.py`
3. `blender -b -t 2 --python scripts/fix_wc_seat_rings.py`
4. `blender -b -t 2 --python scripts/fix_wc_paper_mounts.py`
5. `blender -b -t 2 --python scripts/verify_lhb_detail.py -- --fbx`

The ring repair intentionally expects original 24-piece rings and stops if applied twice. The patch scripts export fresh FBX with the same documented alpha fallback. Their hashes are embedded in root/sidecar patch metadata and exact before/after source hashes are in `qa/wc_seat_ring_patch.json` and `qa/wc_paper_mount_patch.json`. Blender binary serialization may differ across runs; this recipe reproduces scoped geometry, not a promise of identical `.blend` bytes across Blender versions.

The twenty previously accepted gallery frames remain linked to exact masters in `revisions/pre_wc_repair_20261008/models/`. They predate these concealed WC fixture changes and are not relabeled as newly rendered latest-source images. The corrected toilet view is rerendered from the latest master. Historical rejected toilet evidence is retained only in the revision directory. `GALLERY.md` and `DELIVERY_STATUS.json` explicitly label every source revision. The cutaway renderer hides each removed WC door's matched attachments using evaluated bounds; it never saves those visibility changes into masters.
