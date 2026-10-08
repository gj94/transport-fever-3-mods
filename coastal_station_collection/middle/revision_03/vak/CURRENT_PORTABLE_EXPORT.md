# Current portable export for VAK

Open the packed [VAK_coastal_station_v01.blend](VAK_coastal_station_v01.blend) for the authoritative native scene and full procedural materials. The [actual-model gallery](GALLERY.md) retains its source-bound image bytes.

For a portable model, download and extract [VAK_coastal_station_colour_v02.glb.zip](../../portable_colour_revision_02/VAK/VAK_coastal_station_colour_v02.glb.zip); then open the complete GLB. ZIP compression is lossless. Missing untextured RGB factors now use the exact native palette; geometry buffers, nodes, transforms, embedded images, existing colour factors and alpha are unchanged. Noise, bump and paving patterns remain native Blender features.

The [independent colour addendum](../../../qa/reports/MIDDLE_PORTABLE_COLOUR_COHORT_01_ACCEPTED.json) and `PORTABLE_EXPORT_SELECTION.json` bind the old/new archive hashes to the native acceptance record. The original frozen manifest, export QA, checksum file and any original README describe the immutable pre-colour checkpoint. The superseded white-fallback archive is omitted from this first-main package and is available only through its separate historical manifest.

Source scripts are provenance snapshots, not a tested standalone rebuild. The packed scene is the primary editable deliverable. Nominal platform-body width is not a guarantee of unobstructed walking width. Hidden interiors, unsurveyed dimensions and unsupported details are reconstructions; there is no as-built, safety or accessibility certification.

## Station limitations

- Visual reconstruction, not a surveyed current operating inventory or engineering certification.
- The mapped building envelope overlaps259.68m² of the reconstructed raised side body; its nominal6m width is not unobstructed walking width. The narrow rear passage is explicitly approximate and is not an accessibility-compliance claim.
- Hidden interiors, dimensions and source-era station details are reconstructed.
- Targeted checks are not exhaustive pairwise collision certification.
- Some procedural Blender surface effects use base-colour portable fallbacks.

## Retained-image lineage

These accepted views are retained from earlier source scenes because their depicted subjects were unchanged; they are not rerenders of the current scene. Exact image and source hashes remain in `RENDER_PROVENANCE.json`.

- `renders/03_platform_track_details.png`: source `9bdbda1968e9105290c4520a693c5d2d737571064dd76de6628552098e501d56`. Camera03 looks away from the corrected building area, from x−30 toward x−110; outdoor subjects in this view are unchanged.
