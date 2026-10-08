# Current corrected editable scene checkpoint

The corrected 8 October 2026 scene is distributed in `ERS_full_station_v02.blend.parts/` because the GitHub API cannot accept the whole binary at this size. Run that folder's `reassemble.py` in a fresh downloaded folder to reconstruct and SHA256-verify the scene. Individual parts cannot be opened in Blender.

Current checkpoint SHA256: `976d691c3d986de4c54678f69170e88a9eb9608b5801a48aa2afc1ad9a92724e` (43,250,391 bytes).

The direct `ERS_full_station_v02.blend` file in this WIP backup branch is an earlier checkpoint, retained for recovery, and is superseded by these corrected parts. Move the earlier file aside before reassembly; the script intentionally refuses to overwrite a different existing file.

This checkpoint contains reviewed corrected rail/ballast geometry plus a fixture-only full-flight clearance correction. `scene_lineage.json` records the exact parent and changes; earlier accepted parent-bound views remain explicitly attributed. Final comprehensive gallery/export validation remains in progress. No rolling stock is included.
