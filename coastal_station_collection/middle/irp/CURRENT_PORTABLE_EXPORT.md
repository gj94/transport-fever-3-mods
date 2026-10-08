# Current portable export for IRP

Open the packed [IRP_coastal_station_v01.blend](IRP_coastal_station_v01.blend) for the authoritative native scene and full procedural materials. The [actual-model gallery](GALLERY.md) retains its source-bound image bytes.

For a portable model, download and extract [IRP_coastal_station_colour_v02.glb.zip](../portable_colour_revision_02/IRP/IRP_coastal_station_colour_v02.glb.zip); then open the complete GLB. ZIP compression is lossless. Missing untextured RGB factors now use the exact native palette; geometry buffers, nodes, transforms, embedded images, existing colour factors and alpha are unchanged. Noise, bump and paving patterns remain native Blender features.

The [independent colour addendum](../../qa/reports/MIDDLE_PORTABLE_COLOUR_COHORT_01_ACCEPTED.json) and `PORTABLE_EXPORT_SELECTION.json` bind the old/new archive hashes to the native acceptance record. The original frozen manifest, export QA, checksum file and any original README describe the immutable pre-colour checkpoint. Previously published export bytes remain untouched.

Source scripts are provenance snapshots, not a tested standalone rebuild. The packed scene is the primary editable deliverable. Nominal platform-body width is not a guarantee of unobstructed walking width. Hidden interiors, unsurveyed dimensions and unsupported details are reconstructions; there is no as-built, safety or accessibility certification.

## Station limitations

- Visual reconstruction, not a surveyed current operating inventory or engineering/safety certification.
- Hidden interiors, dimensions, source-era facade appearance and service assignments are disclosed reconstructions.
- Procedural Blender surface effects use base-colour portable fallbacks.
- Targeted checks are not exhaustive pairwise collision certification.

## Retained-image lineage

All accepted selected views name the current native scene hash in `RENDER_PROVENANCE.json`.
