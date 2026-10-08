# Current corrected editable scene checkpoint

The corrected 8 October 2026 scene is distributed in `ERS_full_station_v02.blend.parts/` because the GitHub API cannot accept the whole binary at this size. Run that folder's `reassemble.py` in a fresh downloaded folder to reconstruct and SHA256-verify the scene. Individual parts cannot be opened in Blender.

Current checkpoint SHA256: `89667fb2d588576cfc6963456dd7a579d0311b7641acba81bae73fc2e514b54e` (43,308,429 bytes).

The direct `ERS_full_station_v02.blend` file in this WIP backup branch is an earlier checkpoint, retained for recovery, and is superseded by these corrected parts. Move the earlier file aside before reassembly; the script intentionally refuses to overwrite a different existing file.

This checkpoint contains reviewed corrected rail/ballast geometry. Final comprehensive gallery/export validation remains in progress. No rolling stock is included.
