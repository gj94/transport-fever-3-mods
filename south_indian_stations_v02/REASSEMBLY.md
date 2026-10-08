# Reassemble exact whole-file downloads

The GitHub API cannot accept some large binaries in one call. Files above the transport threshold are stored as `filename.parts/part001.bin`, etc. No scene detail has been removed. Each folder has `manifest.json`, part checksums, the original complete-file SHA256, and `reassemble.py`.

1. Download the complete repository folder tree, not one isolated part.
2. Run `python3 path/to/filename.parts/reassemble.py` (Python 3, standard library only).
3. The script verifies every part and writes the whole original file beside the `.parts` folder. It refuses to overwrite different bytes; move an older local checkpoint aside first.
4. Open a reconstructed `.blend` in Blender 4.3.2 or a compatible newer version. Unzip a reconstructed `.zip`, or decompress a `.glb.gz`, before importing the portable exchange files.

The station manifests/checksums name the reconstructed original files. They intentionally do not list transport-part filenames; each parts folder has its own transport manifest. Source scripts reference original paths after reconstruction.

TVC exchange is supplied by `tvc/packages/TVC_v02_exchange_glb.zip.parts/`. Reassemble and unzip it; its `TVC_v02/exchange/` folder holds all24modules. NCJ exchange is `ncj/exports/NCJ_full_station_v02_GLTF.zip.parts/`; ERS exchange is `ers/exports/ERS_full_station_v02.glb.gz.parts/`. The raw logical export files listed in station checksums are recovered from these archives rather than duplicated in this repository.

For TVC, the portable exchange is modular: preserve all included GLB modules and their manifest; original world coordinates allow them to assemble together. NCJ/ERS use their documented whole-scene exchange files. glTF is an interchange deliverable, not the fully editable procedural Blender source.

The final main selection excludes older superseded whole-binary checkpoints from the WIP backup branch. Backup history remains available for recovery. Whole Blender models are saved in Library; direct chat attachment exceeded its upload limit. The parts route above preserves all model detail and exact bytes.
