# Current portable export for QLN

Open the packed [QLN_coastal_station_v01.blend reassembly instructions](QLN_coastal_station_v01.blend.parts/README.md) for the authoritative native scene and full procedural materials. The [actual-model gallery](GALLERY.md) retains its source-bound image bytes.

For a portable model, follow the [QLN_coastal_station_colour_v02.glb.zip exact-byte reassembly instructions](../../portable_colour_revision_02/QLN/QLN_coastal_station_colour_v02.glb.zip.parts/README.md). Download every part, `manifest.json` and `reassemble.py` into one folder, run the delivered Python script, and extract the reconstructed ZIP before opening the complete GLB. The native scene is also stored in exact-byte transport parts; follow its linked instructions before opening it. All non-final parts are exactly 16 MiB, and actual script reassembly verified the original whole-file hash. ZIP compression is lossless. Missing untextured RGB factors now use the exact native palette; geometry buffers, nodes, transforms, embedded images, existing colour factors and alpha are unchanged. Noise, bump and paving patterns remain native Blender features.

The [independent colour addendum](../../../qa/reports/MIDDLE_PORTABLE_COLOUR_COHORT_01_ACCEPTED.json) and `PORTABLE_EXPORT_SELECTION.json` bind the old/new archive hashes to the native acceptance record. The original frozen manifest, export QA, checksum file and any original README describe the immutable pre-colour checkpoint. Previously published export bytes remain untouched.

Source scripts are provenance snapshots, not a tested standalone rebuild. The packed scene is the primary editable deliverable. Nominal platform-body width is not a guarantee of unobstructed walking width. Hidden interiors, unsurveyed dimensions and unsupported details are reconstructions; there is no as-built, safety or accessibility certification.

## Station limitations

- Historical2017–2020 terminal facade is reconstructed; current redevelopment completion is not claimed.
- Dimensions, unseen offices/interiors and service assignments remain disclosed reconstructions.
- Visual reconstruction, not a surveyed operating inventory or engineering certification.
- Targeted checks are not exhaustive pairwise collision certification.
- Procedural Blender materials use base-colour portable fallbacks.

## Retained-image lineage

These accepted views are retained from earlier source scenes because their depicted subjects were unchanged; they are not rerenders of the current scene. Exact image and source hashes remain in `RENDER_PROVENANCE.json`.

- `renders/03_platform_track_details.png`: source `032e138121ab63188fb703ceb3238d9d33d13232bb1caa9fce7af81d5aa327d1`. Entrance-side external cladding is outside this platform/interior camera; subject, camera and illumination unchanged.
- `renders/05_ticket_interior.png`: source `032e138121ab63188fb703ceb3238d9d33d13232bb1caa9fce7af81d5aa327d1`. Entrance-side external cladding is outside this platform/interior camera; subject, camera and illumination unchanged.
