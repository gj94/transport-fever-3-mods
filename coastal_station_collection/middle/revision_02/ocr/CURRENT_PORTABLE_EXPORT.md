# Current portable export for OCR

Open the packed [OCR_coastal_station_v01.blend](OCR_coastal_station_v01.blend) for the authoritative native scene and full procedural materials. The [actual-model gallery](GALLERY.md) retains its source-bound image bytes.

For a portable model, download and extract [OCR_coastal_station_colour_v02.glb.zip](../../portable_colour_revision_02/OCR/OCR_coastal_station_colour_v02.glb.zip); then open the complete GLB. ZIP compression is lossless. Missing untextured RGB factors now use the exact native palette; geometry buffers, nodes, transforms, embedded images, existing colour factors and alpha are unchanged. Noise, bump and paving patterns remain native Blender features.

The [independent colour addendum](../../../qa/reports/MIDDLE_PORTABLE_COLOUR_COHORT_01_ACCEPTED.json) and `PORTABLE_EXPORT_SELECTION.json` bind the old/new archive hashes to the native acceptance record. The original frozen manifest, export QA, checksum file and any original README describe the immutable pre-colour checkpoint. Previously published export bytes remain untouched.

Source scripts are provenance snapshots, not a tested standalone rebuild. The packed scene is the primary editable deliverable. Nominal platform-body width is not a guarantee of unobstructed walking width. Hidden interiors, unsurveyed dimensions and unsupported details are reconstructions; there is no as-built, safety or accessibility certification.

## Station limitations

- Visual reconstruction, not a surveyed current operational inventory or engineering certification.
- Mapped centerline irregularities have documented local regularization; raw observed source coordinates remain available.
- Unseen interiors, approximate dimensions and ancillary wing extent are reconstructed.
- Targeted checks are not exhaustive pairwise collision certification.
- Some procedural Blender materials use base-colour portable fallbacks.

## Retained-image lineage

These accepted views are retained from earlier source scenes because their depicted subjects were unchanged; they are not rerenders of the current scene. Exact image and source hashes remain in `RENDER_PROVENANCE.json`.

- `renders/01_full_mapped_layout.png`: source `4650621b0a296ec30fc488b63ba13ae8cefae1df7edf6f2bef0fd6d248aaa3f8`. One internal ticket-room noticeboard moved; exterior subject/camera/illumination unchanged and noticeboard not visible in these exterior views.
- `renders/02_station_and_platforms.png`: source `4650621b0a296ec30fc488b63ba13ae8cefae1df7edf6f2bef0fd6d248aaa3f8`. One internal ticket-room noticeboard moved; exterior subject/camera/illumination unchanged and noticeboard not visible in these exterior views.
- `renders/03_platform_track_details.png`: source `4650621b0a296ec30fc488b63ba13ae8cefae1df7edf6f2bef0fd6d248aaa3f8`. One internal ticket-room noticeboard moved; exterior subject/camera/illumination unchanged and noticeboard not visible in these exterior views.
- `renders/04_facade_and_approach.png`: source `4650621b0a296ec30fc488b63ba13ae8cefae1df7edf6f2bef0fd6d248aaa3f8`. One internal ticket-room noticeboard moved; exterior subject/camera/illumination unchanged and noticeboard not visible in these exterior views.
