# LHB source review gallery

**16 of 21 planned source-matched final-resolution frames complete.**

Every linked image is an actual Blender CPU Cycles render of its named source. No image generation or photographic compositing. Uniform checkpointed views average eight independent 64-sample scene-linear EXRs, then apply AgX once. No denoising; some interior grain remains visible.

The sources are editable reference-informed models, not manufacturer CAD or a railway certification. Seated and sleeping markers are authoring references, not validated game passengers. Native Transport Fever 3 conversion, baked game materials, LODs, collision and runtime testing remain outside this package.

## Seven class interiors and exteriors

### 1A

- [Interior](previews/LHB_1A_interior.png) · [source/image/sampling provenance](qa/render_1A_interior.json)
- [Exterior](previews/LHB_1A_exterior.png) · [source/image/sampling provenance](qa/render_1A_exterior.json)

### CC

- [Interior](previews/LHB_CC_interior.png) · [source/image/sampling provenance](qa/render_CC_interior.json)
- [Exterior](previews/LHB_CC_exterior.png) · [source/image/sampling provenance](qa/render_CC_exterior.json)

### 3A

- [Interior](previews/LHB_3A_interior.png) · [source/image/sampling provenance](qa/render_3A_interior.json)
- [Exterior](previews/LHB_3A_exterior.png) · [source/image/sampling provenance](qa/render_3A_exterior.json)

### 2A

- [Interior](previews/LHB_2A_interior.png) · [source/image/sampling provenance](qa/render_2A_interior.json)
- [Exterior](previews/LHB_2A_exterior.png) · [source/image/sampling provenance](qa/render_2A_exterior.json)

### SL

- [Interior](previews/LHB_SL_interior.png) · [source/image/sampling provenance](qa/render_SL_interior.json)
- [Exterior](previews/LHB_SL_exterior.png) · [source/image/sampling provenance](qa/render_SL_exterior.json)

### 2S

- [Interior](previews/LHB_2S_interior.png) · [source/image/sampling provenance](qa/render_2S_interior.json)
- [Exterior](previews/LHB_2S_exterior.png) · [source/image/sampling provenance](qa/render_2S_exterior.json)

### GS

- [Interior](previews/LHB_GS_interior.png) · [source/image/sampling provenance](qa/render_GS_interior.json)
- [Exterior](previews/LHB_GS_exterior.png) · [source/image/sampling provenance](qa/render_GS_exterior.json)

Sleeper corridor frames primarily show layout. The 3A bay view below provides clearer berth-face evidence. 1A is a cabin-facing interior; CC and 2S show their seating arrangement.

## Detail views

- [3A bay](previews/LHB_3A_bay.png) · [provenance](qa/render_3A_bay.json)
- [CC chair detail](previews/LHB_CC_chair_detail.png) · [provenance](qa/render_CC_chair_detail.json)
- 1A cabin entry: pending
- 3A hvac: pending
- 3A bogie: pending
- 3A door: pending
- 3A toilet: pending

## Files and reproducibility

- Editable Blender masters, FBX exchange files and matching marker/manifests: [models](models/)
- Measured source/FBX results: [QA summary](qa/source_geometry/SUMMARY.md)
- Review history: [iteration log](docs/iteration_log.md)
- Machine-readable frame status: [delivery status](DELIVERY_STATUS.json)
- Render-only CC0 environment dependencies use the repository-sibling folder `../wap7_photoreal_v02/environment`; a standalone archive must include these actual files or document the sibling checkout requirement. Absolute scratch symlinks are not portable delivery dependencies.
- Evidence JSON preserves historical absolute execution paths byte-for-byte to retain valid fingerprints. Those paths describe provenance; they are not required installation destinations.

Earlier low-sample or stale images may exist in the working tree. Only the source-matched links above are this gallery.
