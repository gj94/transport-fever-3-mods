# Current portable export for MQO

Open the packed [MQO_coastal_station_v01.blend](MQO_coastal_station_v01.blend) for the authoritative native scene and full procedural materials. The [actual-model gallery](GALLERY.md) retains its source-bound image bytes.

For a portable model, download and extract [MQO_coastal_station_colour_v02.glb.zip](../../portable_colour_revision_02/MQO/MQO_coastal_station_colour_v02.glb.zip); then open the complete GLB. ZIP compression is lossless. Missing untextured RGB factors now use the exact native palette; geometry buffers, nodes, transforms, embedded images, existing colour factors and alpha are unchanged. Noise, bump and paving patterns remain native Blender features.

The [independent colour addendum](../../../qa/reports/MIDDLE_PORTABLE_COLOUR_COHORT_01_ACCEPTED.json) and `PORTABLE_EXPORT_SELECTION.json` bind the old/new archive hashes to the native acceptance record. The original frozen manifest, export QA, checksum file and any original README describe the immutable pre-colour checkpoint. Previously published export bytes remain untouched.

Source scripts are provenance snapshots, not a tested standalone rebuild. The packed scene is the primary editable deliverable. Nominal platform-body width is not a guarantee of unobstructed walking width. Hidden interiors, unsurveyed dimensions and unsupported details are reconstructions; there is no as-built, safety or accessibility certification.

## Station limitations

- Visual reconstruction, not surveyed current yard inventory or engineering/safety certification.
- Main building facade is not visible in retrieved source image; modest hut footprint/appearance and hidden interior are reconstructed.
- No direct central straight-through public path; verified public circulation uses left doorway around compact ticket counter.
- Exact original builder-code revision was not captured for this first candidate; packed Blend is authoritative and this is disclosed in its source document.
- Targeted sampling does not constitute exhaustive pairwise collision certification.

## Retained-image lineage

These accepted views are retained from earlier source scenes because their depicted subjects were unchanged; they are not rerenders of the current scene. Exact image and source hashes remain in `RENDER_PROVENANCE.json`.

- `renders/04_facade_and_approach.png`: source `950cf176f29fc8cb21420a3887f5d782801d77a390be513d24840c4cf4edb4b1`. Bridge geometry is outside this facade/interior view; camera, subject geometry, materials and illumination unchanged.
- `renders/05_ticket_interior.png`: source `950cf176f29fc8cb21420a3887f5d782801d77a390be513d24840c4cf4edb4b1`. Bridge geometry is outside this facade/interior view; camera, subject geometry, materials and illumination unchanged.
