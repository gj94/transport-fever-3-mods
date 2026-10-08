# LHB source review gallery

**21 of 21 planned versioned-source final-resolution frames complete.**

Every linked image is an actual Blender CPU Cycles render of its named source. No image generation or photographic compositing. Uniform checkpointed views average eight independent 64-sample scene-linear EXRs, then apply AgX once. No denoising; some interior grain remains visible.

The sources are editable reference-informed models, not manufacturer CAD or a railway certification. Seated and sleeping markers are authoring references, not validated game passengers. Native Transport Fever 3 conversion, baked game materials, LODs, collision and runtime testing remain outside this package.

The first twenty accepted views retain their exact pre-repair source hashes and are linked to the preserved prior revision. Only the corrected toilet view depicts the latest masters. Later changes are limited to concealed WC seat-ring geometry and paper-holder/tissue mounting; no claim is made that older pixels were rerendered. See [repair evidence](qa/wc_seat_ring_patch.json) and [fixture placement evidence](qa/wc_paper_mount_patch.json).

## Seven class interiors and exteriors

### 1A

- [Interior](previews/LHB_1A_interior.png) · [source/image/sampling provenance](qa/render_1A_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_1A.blend)
- [Exterior](previews/LHB_1A_exterior.png) · [source/image/sampling provenance](qa/render_1A_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_1A.blend)

### CC

- [Interior](previews/LHB_CC_interior.png) · [source/image/sampling provenance](qa/render_CC_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_CC.blend)
- [Exterior](previews/LHB_CC_exterior.png) · [source/image/sampling provenance](qa/render_CC_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_CC.blend)

### 3A

- [Interior](previews/LHB_3A_interior.png) · [source/image/sampling provenance](qa/render_3A_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)
- [Exterior](previews/LHB_3A_exterior.png) · [source/image/sampling provenance](qa/render_3A_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)

### 2A

- [Interior](previews/LHB_2A_interior.png) · [source/image/sampling provenance](qa/render_2A_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_2A.blend)
- [Exterior](previews/LHB_2A_exterior.png) · [source/image/sampling provenance](qa/render_2A_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_2A.blend)

### SL

- [Interior](previews/LHB_SL_interior.png) · [source/image/sampling provenance](qa/render_SL_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_SL.blend)
- [Exterior](previews/LHB_SL_exterior.png) · [source/image/sampling provenance](qa/render_SL_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_SL.blend)

### 2S

- [Interior](previews/LHB_2S_interior.png) · [source/image/sampling provenance](qa/render_2S_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_2S.blend)
- [Exterior](previews/LHB_2S_exterior.png) · [source/image/sampling provenance](qa/render_2S_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_2S.blend)

### GS

- [Interior](previews/LHB_GS_interior.png) · [source/image/sampling provenance](qa/render_GS_interior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_GS.blend)
- [Exterior](previews/LHB_GS_exterior.png) · [source/image/sampling provenance](qa/render_GS_exterior.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_GS.blend)

Sleeper corridor frames primarily show layout. The 3A bay view below provides clearer berth-face evidence. 1A is a cabin-facing interior; CC and 2S show their seating arrangement.

## Detail views

- [3A bay](previews/LHB_3A_bay.png) · [provenance](qa/render_3A_bay.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)
- [CC chair detail](previews/LHB_CC_chair_detail.png) · [provenance](qa/render_CC_chair_detail.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_CC.blend)
- [1A cabin entry](previews/LHB_1A_cabin_entry.png) · [provenance](qa/render_1A_cabin_entry.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_1A.blend)
- [3A hvac](previews/LHB_3A_hvac.png) · [provenance](qa/render_3A_hvac.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)
- [3A bogie](previews/LHB_3A_bogie.png) · [provenance](qa/render_3A_bogie.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)
- [3A door](previews/LHB_3A_door.png) · [provenance](qa/render_3A_door.json) · [accepted_pre_repair_source](revisions/pre_wc_repair_20261008/models/LHB_3A.blend)
- [3A toilet](previews/LHB_3A_toilet.png) · [provenance](qa/render_3A_toilet.json) · [current_corrected_source](models/LHB_3A.blend)

## Files and reproducibility

- Editable Blender masters, FBX exchange files and matching marker/manifests: [models](models/)
- Measured source/FBX results: [QA summary](qa/source_geometry/SUMMARY.md)
- Review history: [iteration log](docs/iteration_log.md)
- Machine-readable frame status: [delivery status](DELIVERY_STATUS.json)
- Render-only CC0 environment dependencies use the repository-sibling folder `../wap7_photoreal_v02/environment`; a standalone archive must include these actual files or document the sibling checkout requirement. Absolute scratch symlinks are not portable delivery dependencies.
- Evidence JSON preserves historical absolute execution paths byte-for-byte to retain valid fingerprints. Those paths describe provenance; they are not required installation destinations.

Earlier low-sample or stale images may exist in the working tree. Only the versioned-source links above are this gallery.
